"""
This module defines view function decorators to validate request and response parameters and bodies.
"""

import collections
import copy
import functools
import logging
from typing import AnyStr, Union

try:
    from importlib.metadata import version
except ImportError:
    from importlib_metadata import version

from jsonschema import Draft4Validator, ValidationError, draft4_format_checker
from jsonschema import exceptions as jsexceptions
from jsonschema.validators import extend
from packaging.version import Version
from werkzeug.datastructures import FileStorage

from connexion.exceptions import (BadRequestProblem, ExtraParameterProblem,
                          UnsupportedMediaTypeProblem)
from connexion.http_facts import FORM_CONTENT_TYPES
from connexion.json_schema import Draft4RequestValidator, Draft4ResponseValidator
from connexion.lifecycle import ConnexionResponse
from connexion.utils import all_json, boolean, is_json_mimetype, is_null, is_nullable

import json
import re
import urllib

_jsonschema_3_or_newer = Version(version("jsonschema")) >= Version("3.0.0")

logger = logging.getLogger('ogc_edr_lib.connexion_ext.validation_ext')

TYPE_MAP = {
    'integer': int,
    'number': float,
    'boolean': boolean,
    'object': dict
}
# paths to be ignored for validation when (1) input has text/html as output
# and (2) ending with the given pattern
paths_ignore_validation_html = [
    "/.*/collections/.*/area$",
    "/.*/collections/.*/position$",
    "/.*/collections/.*/trajectory$",
    "/.*/collections/.*/corridor$",
    "/.*/collections/.*/cube$",
    "/.*/collections/.*/radius$",
    "/.*/collections/.*/locations$"]

class TypeValidationError(Exception):
    def __init__(self, schema_type, parameter_type, parameter_name):
        """
        Exception raise when type validation fails

        :type schema_type: str
        :type parameter_type: str
        :type parameter_name: str
        :return:
        """
        self.schema_type = schema_type
        self.parameter_type = parameter_type
        self.parameter_name = parameter_name

    def __str__(self):
        msg = "Wrong type, expected '{schema_type}' for {parameter_type} parameter '{parameter_name}'"
        return msg.format(**vars(self))


def my_coerce_type(param, value, parameter_type, parameter_name=None):

    def make_type(value, type_literal):
        if type_literal == "object":
            value = resolve_value_object(value)
        type_func = TYPE_MAP.get(type_literal)
        return type_func(value)

    def resolve_value_object(value):
        try:
            a_value = json.loads(value)
            return a_value
        except Exception as ee:
            logger.warning("Error - {}".format(ee))
            return value

    param_schema = param.get("schema", param)
    if is_nullable(param_schema) and is_null(value):
        return None

    param_type = param_schema.get('type')
    parameter_name = parameter_name if parameter_name else param.get('name')
    if param_type == "array":
        converted_params = []
        if parameter_type == "header":
            value = value.split(',')
        for v in value:
            try:
                converted = make_type(v, param_schema["items"]["type"])
            except (ValueError, TypeError):
                converted = v
            converted_params.append(converted)
        return converted_params
    elif param_type == 'object':
        if param_schema.get('properties'):
            def cast_leaves(d, schema):
                if type(d) is not dict:
                    try:
                        return make_type(d, schema['type'])
                    except (ValueError, TypeError):
                        return d
                for k, v in d.items():
                    if k in schema['properties']:
                        d[k] = cast_leaves(v, schema['properties'][k])
                return d

            return cast_leaves(value, param_schema)
        
        if type(value) is not dict:
            try:
                return make_type(value, param_schema['type'])
            except (ValueError, TypeError):
                return value
    else:
        try:
            return make_type(value, param_type)
        except ValueError:
            raise TypeValidationError(param_type, parameter_type, parameter_name)
        except TypeError:
            return value


def validate_parameter_list(request_params, spec_params):
    request_params = set(request_params)
    spec_params = set(spec_params)

    return request_params.difference(spec_params)


class MyRequestBodyValidator:

    def __init__(self, schema, consumes, api, is_null_value_valid=False, validator=None,
                 strict_validation=False):
        """
        :param schema: The schema of the request body
        :param consumes: The list of content types the operation consumes
        :param is_null_value_valid: Flag to indicate if null is accepted as valid value.
        :param validator: Validator class that should be used to validate passed data
                          against API schema. Default is jsonschema.Draft4Validator.
        :type validator: jsonschema.IValidator
        :param strict_validation: Flag indicating if parameters not in spec are allowed
        """
        self.consumes = consumes
        self.schema = schema
        self.has_default = schema.get('default', False)
        self.is_null_value_valid = is_null_value_valid
        validatorClass = validator or Draft4RequestValidator
        self.validator = validatorClass(schema, format_checker=draft4_format_checker)
        self.api = api
        self.strict_validation = strict_validation

    def validate_formdata_parameter_list(self, request):
        request_params = request.form.keys()
        spec_params = self.schema.get('properties', {}).keys()
        return validate_parameter_list(request_params, spec_params)

    def __call__(self, function):
        """
        :type function: types.FunctionType
        :rtype: types.FunctionType
        """

        @functools.wraps(function)
        def wrapper(request):
            if all_json(self.consumes):
                data = request.json

                empty_body = not(request.body or request.form or request.files)
                if data is None and not empty_body and not self.is_null_value_valid:
                    try:
                        ctype_is_json = is_json_mimetype(request.headers.get("Content-Type", ""))
                    except ValueError:
                        ctype_is_json = False

                    if ctype_is_json:
                        # Content-Type is json but actual body was not parsed
                        raise BadRequestProblem(detail="Request body is not valid JSON")
                    else:
                        # the body has contents that were not parsed as JSON
                        raise UnsupportedMediaTypeProblem(
                                       detail="Invalid Content-type ({content_type}), expected JSON data".format(
                                           content_type=request.headers.get("Content-Type", "")
                                       ))

                logger.debug("%s validating schema...", request.url)
                if data is not None or not self.has_default:
                    self.validate_schema(data, request.url)
            elif self.consumes[0] in FORM_CONTENT_TYPES:
                data = dict(request.form.items()) or (request.body if len(request.body) > 0 else {})
                data.update(dict.fromkeys(request.files, ''))  # validator expects string..
                logger.debug('%s validating schema...', request.url)

                if self.strict_validation:
                    formdata_errors = self.validate_formdata_parameter_list(request)
                    if formdata_errors:
                        raise ExtraParameterProblem(formdata_errors, [])

                if data:
                    props = self.schema.get("properties", {})
                    errs = []
                    for k, param_defn in props.items():
                        if k in data:
                            try:
                                data[k] = my_coerce_type(param_defn, data[k], 'requestBody', k)
                            except TypeValidationError as e:
                                errs += [str(e)]
                                print(errs)
                    if errs:
                        raise BadRequestProblem(detail=errs)

                self.validate_schema(data, request.url)

            response = function(request)
            return response

        return wrapper

    @classmethod
    def _error_path_message(cls, exception):
        error_path = '.'.join(str(item) for item in exception.path)
        error_path_msg = f" - '{error_path}'" if error_path else ""
        return error_path_msg

    def validate_schema(self, data, url):
        # type: (dict, AnyStr) -> Union[ConnexionResponse, None]
        if self.is_null_value_valid and is_null(data):
            return None

        try:
            self.validator.validate(data)
        except ValidationError as exception:
            error_path_msg = self._error_path_message(exception=exception)
            logger.error(
                "{url} validation error: {error}{error_path_msg}".format(
                    url=url, error=exception.message,
                    error_path_msg=error_path_msg),
                extra={'validator': 'body'})
            raise BadRequestProblem(detail="{message}{error_path_msg}".format(
                               message=exception.message,
                               error_path_msg=error_path_msg))

        return None


class MyResponseBodyValidator:
    def __init__(self, schema, validator=None):
        """
        :param schema: The schema of the response body
        :param validator: Validator class that should be used to validate passed data
                          against API schema. Default is Draft4ResponseValidator.
        :type validator: jsonschema.IValidator
        """
        ValidatorClass = validator or Draft4ResponseValidator
        self.validator = ValidatorClass(schema, format_checker=draft4_format_checker)

    def validate_schema(self, data, url):
        # type: (dict, AnyStr) -> Union[ConnexionResponse, None]
        try:
            self.validator.validate(data)
        except ValidationError as exception:
            logger.error("{url} validation error: {error}".format(url=url,
                                                                  error=exception),
                         extra={'validator': 'response'})
            raise exception

        return None


class MyParameterValidator:
    def __init__(self, parameters, api, strict_validation=False):
        """
        :param parameters: List of request parameter dictionaries
        :param api: api that the validator is attached to
        :param strict_validation: Flag indicating if parameters not in spec are allowed
        """
        self.parameters = collections.defaultdict(list)
        for p in parameters:
            self.parameters[p['in']].append(p)

        self.api = api
        self.strict_validation = strict_validation

    @staticmethod
    def validate_parameter(parameter_type, value, param, param_name=None):
        if value is not None:
            if is_nullable(param) and is_null(value):
                return

            try:
                converted_value = my_coerce_type(param, value, parameter_type, param_name)
            except TypeValidationError as e:
                return str(e)

            param = copy.deepcopy(param)
            param = param.get('schema', param)
            if 'required' in param:
                del param['required']
            try:
                #MyParameterValidator.test_here(param, converted_value)
                if parameter_type == 'formdata' and param.get('type') == 'file':
                    if _jsonschema_3_or_newer:
                        extend(
                            Draft4Validator,
                            type_checker=Draft4Validator.TYPE_CHECKER.redefine(
                                "file",
                                lambda checker, instance: isinstance(instance, FileStorage)
                            )
                        )(param, format_checker=draft4_format_checker).validate(converted_value)
                    else:
                        Draft4Validator(
                            param,
                            format_checker=draft4_format_checker,
                            types={'file': FileStorage}).validate(converted_value)
                else:
                    pass
                    #the_validator = Draft4Validator(
                    #    param, format_checker=draft4_format_checker)
                    #the_best_match = MyParameterValidator.best_match(the_validator.iter_errors(converted_value))
                    #Draft4Validator(
                    #     the_best_match.schema, format_checker=draft4_format_checker).validate(converted_value)
                    # Draft4Validator(
                    #    param, format_checker=draft4_format_checker).validate(converted_value)
            except ValidationError as exception:
                debug_msg = 'Error while converting value {converted_value} from param ' \
                            '{type_converted_value} of type real type {param_type} to the declared type {param}'
                fmt_params = dict(
                    converted_value=str(converted_value),
                    type_converted_value=type(converted_value),
                    param_type=param.get('type'),
                    param=param
                )
                logger.info(debug_msg.format(**fmt_params))
                return str(exception)

        elif param.get('required'):
            return "Missing {parameter_type} parameter '{param[name]}'".format(**locals())

    @staticmethod
    def test_here(param, converted_value):
        the_validator =  Draft4Validator(
                        param, format_checker=draft4_format_checker)
        the_best = MyParameterValidator.best_match(the_validator.iter_errors(converted_value))
        print("the_best=", the_best)

    @staticmethod
    def best_match(errors):
        errors = list(errors)
        best = jsexceptions.best_match(errors)
        reversed_best = jsexceptions.best_match(reversed(errors))
        # self.astertEqual(
        #    best,
        #    reversed_best,
        #    msg="Didn't return a consistent best match!\n"
        #        "Got: {0}\n\nThen: {1}".format(best, reversed_best),
        #)
        print("reserved_best=", reversed_best)
        return best

    def validate_query_parameter_list(self, request):
        request_params = request.query.keys()
        spec_params = [x['name'] for x in self.parameters.get('query', [])]
        return validate_parameter_list(request_params, spec_params)

    def validate_formdata_parameter_list(self, request):
        request_params = request.form.keys()
        if 'formData' in self.parameters:  # Swagger 2:
            spec_params = [x['name'] for x in self.parameters['formData']]
        else:  # OAS 3
            return set()
        return validate_parameter_list(request_params, spec_params)

    def validate_query_parameter(self, param, request):
        """
        Validate a single query parameter (request.args in Flask)

        :type param: dict
        :rtype: str
        """
        val = request.query.get(param['name'])
        return self.validate_parameter('query', val, param)

    def validate_path_parameter(self, param, request):
        val = request.path_params.get(param['name'].replace('-', '_'))
        return self.validate_parameter('path', val, param)

    def validate_header_parameter(self, param, request):
        val = request.headers.get(param['name'])
        return self.validate_parameter('header', val, param)

    def validate_cookie_parameter(self, param, request):
        val = request.cookies.get(param['name'])
        return self.validate_parameter('cookie', val, param)

    def validate_formdata_parameter(self, param_name, param, request):
        if param.get('type') == 'file' or param.get('format') == 'binary':
            val = request.files.get(param_name)
        else:
            val = request.form.get(param_name)

        return self.validate_parameter('formdata', val, param)

    def __call__(self, function):
        """
        :type function: types.FunctionType
        :rtype: types.FunctionType
        """

        @functools.wraps(function)
        def wrapper(request):
            logger.debug("%s validating parameters...", request.url)

            if self.strict_validation:
                query_errors = self.validate_query_parameter_list(request)
                formdata_errors = self.validate_formdata_parameter_list(request)

                if formdata_errors or query_errors:
                    raise ExtraParameterProblem(formdata_errors, query_errors)

            t1 = self._check_path_ends_with(request)
            t2 = self._check_if_html_is_the_output_format(request)
            if not (t1 and t2):
                for param in self.parameters.get('query', []):
                    error = self.validate_query_parameter(param, request)
                    if error:
                        raise BadRequestProblem(detail=error)

            for param in self.parameters.get('path', []):
                error = self.validate_path_parameter(param, request)
                if error:
                    raise BadRequestProblem(detail=error)

            for param in self.parameters.get('header', []):
                error = self.validate_header_parameter(param, request)
                if error:
                    raise BadRequestProblem(detail=error)

            for param in self.parameters.get('cookie', []):
                error = self.validate_cookie_parameter(param, request)
                if error:
                    raise BadRequestProblem(detail=error)

            for param in self.parameters.get('formData', []):
                error = self.validate_formdata_parameter(param["name"], param, request)
                if error:
                    raise BadRequestProblem(detail=error)

            print("type(function=",type(function))

            return function(request)

        return wrapper

    def _check_path_ends_with(self, request):
        print(request)
        print("dir -----", dir(request.context))
        the_path = request.context.path
        for p in paths_ignore_validation_html:
            if re.fullmatch(p, the_path) is not None:
                return True
        return False

    def _check_if_html_is_the_output_format(self, request):
        qstrs = urllib.parse.parse_qs(request.context.query_string)
        the_formats = qstrs.get('f')
        the_formats = self._get_full_media_type_from_f_params(the_formats)
        if the_formats is not None:
            if "text/html" in the_formats:
                return True
            else:
                return False
        the_a_formats = request.context.headers.getall("accept", None)
        if (the_a_formats is not None):
            the_formats = ",".join(the_a_formats).split(",")
            if "text/html" in the_formats:
                return True        
        return False

    def _get_full_media_type_from_f_params(self, f_formats: list):
        if f_formats is None:
            return None
        the_f_formats = [x.lower() for x in f_formats]
        ret_formats = []
        for f in the_f_formats:
            the_f = self._get_full_media_type_from_f_param(f)
            ret_formats.append(the_f)
        return ret_formats

    def _get_full_media_type_from_f_param(self, f_format):
        ret_format = f_format
        if f_format.lower() == 'json':
            ret_format = 'application/json'
        elif f_format.lower() == 'html':
            ret_format = 'text/html'
        elif f_format.lower() == 'coveragejson':
            ret_format = 'application/prs.coverage+json'
        elif f_format.lower() == 'geojson':
            ret_format = 'application/geo+json'
        elif f_format.lower() == 'netcdf':
            ret_format = 'application/x-netcdf'
        return ret_format
