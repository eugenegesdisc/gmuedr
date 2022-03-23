import os
import sys
import yaml
from ogc_edr_lib.ogc_api_edr_plugin_manager import OGCEDRPluginManager
import mimeparse
from jinja2 import Environment, FileSystemLoader, select_autoescape
import gettext
from typing import Tuple, Union
from babel.support import Translations
import logging
# configfile = "C:\\wksp\\py\\ogc\\api\\edr\\edr\\aiohttp\\edr-config.yaml"

Logger = logging.getLogger(__name__)


class OgcApiConfig(object):

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(OgcApiConfig, cls).__new__(cls)
            configfile = (
                '{}{}..{}edr-config.yaml'
            ).format(
                os.path.dirname(os.path.realpath(__file__)),
                os.sep, os.sep
            )
            cls.config = cls.instance.load_config_file(configfile)
            cls.pluginmanager = OGCEDRPluginManager()
            cls.openapi = cls.instance.load_openapi_file()
            cls.instance.setup_logger()
        return cls.instance

    def load_config_file(self, configfile):
        config = {}
        with open(configfile, mode="r", encoding="utf8") as cf:
            config = yaml.safe_load(cf)
        return config

    def get_config(self):
        return self.config

    def get_template_path(self):
        if not hasattr(self, 'template_path'):
            try:
                self.template_path = self.config['server']['templates']['path']
            except:
                self.template_path = '{}{}templates'.format(os.path.dirname(
                    os.path.realpath(__file__)), os.sep)
        return self.template_path

    def get_jinja2_template(self, rtemplate, locale=None):
        template_path = self.get_template_path()
        jj2env = Environment(
            loader=FileSystemLoader(template_path),
            extensions=[
                'jinja2.ext.i18n',
                'jinja2.ext.autoescape'
            ],
            autoescape=select_autoescape(['html', 'xml'])
        )
        if locale:
            translation = Translations.load(
                'locale', [locale])
        else:
            translation = gettext.NullTranslations()
        jj2env.install_gettext_translations(translation)
        return jj2env.get_template(rtemplate)

    def load_openapi_file(self):
        openapifile = self.get_openapi_yaml_path()
        openapi = {}
        with open(openapifile, mode="r", encoding="utf8") as cf:
            openapi = yaml.safe_load(cf)
        return openapi

    def get_openapi_yaml_path(self):
        if not hasattr(self, 'openapi_yaml_path'):
            try:
                self.openapi_yaml_path = self.config['server']['penapi']['yaml']
            except:
                self.openapi_yaml_path = (
                    '{}{}..{}openapi_server{}openapi{}openapi.yaml'
                ).format(
                    os.path.dirname(os.path.realpath(__file__)),
                    os.sep, os.sep, os.sep, os.sep
                )
        return self.openapi_yaml_path

    def get_response_formats(self, thepath):
        ret_formats = []
        try:
            ret_formats = self.openapi['paths'][thepath][
                "get"]["responses"]["200"]["content"].keys()
        except:
            ret_formats = []
        return ret_formats

    def get_mimetype_best_match(
            self, supported_mtypes: list, header_accept: str):
        best_match = mimeparse.best_match(
            supported_mtypes, header_accept)
        return best_match

    def setup_logger(self):
        """
        Setup configuration

        :returns: void (creates logging instance)
        """

        log_format = self._get_log_format()
        date_format = self._get_log_dateformat()
        loglevel = self._get_log_loglevel()
        logfile = self._get_log_file()
        if logfile is not None:
            logging.basicConfig(
                level=loglevel, datefmt=date_format,
                format=log_format,
                filename=logfile)
        else:
            logging.basicConfig(
                level=loglevel, datefmt=date_format,
                format=log_format, stream=sys.stdout)

    def _get_log_format(self):
        try:
            log_format = self.config["logging"]["logformat"]
        except BaseException as error:
            Logger.debug("error - {}".format(error))
            log_format = (
                '[%(asctime)s] {%(pathname)s:%(lineno)d} '
                '%(levelname)s - %(message)s'
                )
        return log_format

    def _get_log_dateformat(self):
        try:
            date_format = self.config["logging"]["dateformat"]
        except BaseException as error:
            Logger.debug("error - {}".format(error))
            date_format = (
                '%Y-%m-%dT%H:%M:%SZ'
                )
        return date_format

    def _get_log_loglevel(self):
        loglevels = {
            'CRITICAL': logging.CRITICAL,
            'ERROR': logging.ERROR,
            'WARNING': logging.WARNING,
            'INFO': logging.INFO,
            'DEBUG': logging.DEBUG,
            'NOTSET': logging.NOTSET
            }
        try:
            loglevel = loglevels[self.config["logging"]["level"]]
        except BaseException as error:
            Logger.debug("error - {}".format(error))
            loglevel = logging.ERROR
        return loglevel

    def _get_log_file(self):
        try:
            logfile = self.config["logging"]["logfile"]
            return logfile
        except BaseException as error:
            Logger.debug("error - {}".format(error))
            return None
