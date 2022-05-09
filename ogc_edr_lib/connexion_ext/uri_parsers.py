"""
This module defines view function decorators to split query and path parameters.
"""

import abc
import functools
import json
import logging
import re
from connexion.decorators.uri_parsing import AbstractURIParser
from connexion import utils
from connexion.decorators.decorator import BaseDecorator

QUERY_STRING_DELIMITERS = {
    'spaceDelimited': ' ',
    'pipeDelimited': '|',
    'simple': ',',
    'form': ','
}


class MyOpenAPIURIParser(AbstractURIParser):
    style_defaults = {"path": "simple", "header": "simple",
                      "query": "form", "cookie": "form",
                      "form": "form"}

    @property
    def param_defns(self):
        return self._param_defns

    @property
    def form_defns(self):
        return {k: v for k, v in self._body_schema.get('properties', {}).items()}

    @property
    def param_schemas(self):
        return {k: v.get('schema', {}) for k, v in self.param_defns.items()}

    def resolve_form(self, form_data):
        if self._body_schema is None or self._body_schema.get('type') != 'object':
            return form_data
        for k in form_data:
            encoding = self._body_encoding.get(k, {"style": "form"})
            defn = self.form_defns.get(k, {})
            # TODO support more form encoding styles
            form_data[k] = \
                self._resolve_param_duplicates(form_data[k], encoding, 'form')
            if defn and defn["type"] == "array":
                form_data[k] = self._split(form_data[k], encoding, 'form')
            elif 'contentType' in encoding and utils.all_json([encoding.get('contentType')]):
                form_data[k] = json.loads(form_data[k])
        return form_data

    def _make_deep_object(self, k, v):
        """ consumes keys, value pairs like (a[foo][bar], "baz")
            returns (a, {"foo": {"bar": "baz"}}}, is_deep_object)
        """
        root_key = None
        if k in self.param_schemas.keys():
            return k, v, False
        else:
            for keys in self.param_schemas.keys():
                if k.startswith(keys):
                    rest = keys.replace(k, '')
                    root_key = rest

        if not root_key:
            root_key = k.split("[", 1)[0]
            if k == root_key:
                return k, v, False

        key_path = re.findall(r'\[([^\[\]]*)\]', k)
        root = prev = node = {}
        for k in key_path:
            node[k] = {}
            prev = node
            node = node[k]
        prev[k] = v[0]
        return root_key, [root], True

    def _preprocess_deep_objects(self, query_data):
        """ deep objects provide a way of rendering nested objects using query
            parameters.
        """
        deep = [self._make_deep_object(k, v) for k, v in query_data.items()]
        root_keys = [k for k, v, is_deep_object in deep]
        ret = dict.fromkeys(root_keys, [{}])
        for k, v, is_deep_object in deep:
            if is_deep_object:
                ret[k] = [utils.deep_merge(v[0], ret[k][0])]
            else:
                v = self._attempt_to_convert_value(k, v)
                ret[k] = v
        return ret

    def _attempt_to_process_object_value(self, k, v):
        defn = self.form_defns.get(k, {})

    def _attempt_to_convert_value(self, k, v):
        """
        Speciall handling wrapper for object.
        If the received value is not a object (dict in python), the process attempts to wrap it
        as a dict and put the scalarvalue into property 'scalaravalue'. If string is entered,
        it needs to be wrap in quote when passing throgh as a request parameter. Otherwise, an error
        would be thrown.
        :returns: wrapped as {scalavalue: invalue} if invalue is not a dict.
        """
        try:
            param_type = self.param_schemas.get(k, None)
            if param_type is None:
                return v
            if (param_type.get("type") == "object"
                and len(v) == 1
                    and v[0] is not dict):
                a_v = v
                av0 = json.loads(v[0])
                av0 = self._attempt_to_wrap_scalar_value_for_object_param(av0)
                a_v[0] = av0
                return a_v
            elif (param_type.get("type") == "array"
                  and len(v) == 1
                  and v[0] is str
                  and ("," in str)):
                a_v = v.split(",")
                return a_v
            return v
        except Exception as ee:
            logging.warning("error in parsing - {}".format(ee))
            return v

    def _get_param_type_with_oneof(self, param_type):
        the_type = param_type.get("type")
        if the_type is not None:
            return the_type
        the_one_of = param_type.get("oneOf", None)
        if the_one_of is None:
            return the_type
        the_ret_type = the_one_of[0].get("type")
        for i in the_one_of:
            if the_ret_type != i.get("type"):
                return None
        return the_ret_type

    def resolve_params(self, params, _in):
        """
        Override the function in base.
        takes a dict of parameters, and resolves the values into
        the correct array type handling duplicate values, and splitting
        based on the collectionFormat defined in the spec.
        """
        resolved_param = {}
        for k, values in params.items():
            param_defn = self.param_defns.get(k)
            param_schema = self.param_schemas.get(k)

            if not (param_defn or param_schema):
                # rely on validation
                resolved_param[k] = values
                continue

            if _in == 'path':
                # multiple values in a path is impossible
                values = [values]

            # if param_schema and param_schema['type'] == 'array':
            if param_schema and self._get_param_type_with_oneof(param_schema) == 'array':
                # resolve variable re-assignment, handle explode
                values = self._resolve_param_duplicates(
                    values, param_defn, _in)
                # handle array styles
                resolved_param[k] = self._split(values, param_defn, _in)
            else:
                resolved_param[k] = values[-1]

        return resolved_param

    def _attempt_to_wrap_scalar_value_for_object_param(self, val):
        retval = val
        if type(val) is not dict:
            retval = dict()
            retval["scalarvalue"] = val
        return retval

    def resolve_query(self, query_data):
        query_data = self._preprocess_deep_objects(query_data)
        return self.resolve_params(query_data, 'query')

    def resolve_path(self, path_data):
        return self.resolve_params(path_data, 'path')

    @staticmethod
    def _resolve_param_duplicates(values, param_defn, _in):
        """ Resolve cases where query parameters are provided multiple times.
            The default behavior is to use the first-defined value.
            For example, if the query string is '?a=1,2,3&a=4,5,6' the value of
            `a` would be "4,5,6".
            However, if 'explode' is 'True' then the duplicate values
            are concatenated together and `a` would be "1,2,3,4,5,6".
        """
        default_style = MyOpenAPIURIParser.style_defaults[_in]
        style = param_defn.get('style', default_style)
        delimiter = QUERY_STRING_DELIMITERS.get(style, ',')
        is_form = (style == 'form')
        explode = param_defn.get('explode', is_form)
        if explode:
            return delimiter.join(values)

        # default to last defined value
        return values[-1]

    @staticmethod
    def _split(value, param_defn, _in):
        default_style = MyOpenAPIURIParser.style_defaults[_in]
        style = param_defn.get('style', default_style)
        delimiter = QUERY_STRING_DELIMITERS.get(style, ',')
        return value.split(delimiter)
