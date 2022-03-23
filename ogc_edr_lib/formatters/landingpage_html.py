from ogc_edr_lib.formatters.base import BaseFormatter
from ogc_edr_lib.ogc_api_config import OgcApiConfig
from ogc_edr_lib.l10n import LocaleTranslator


class LandingPageHtmlFormatter(BaseFormatter):
    """generic Formatter ABC"""
    type = "formatter"
    category = "landingpage"
    supported_media_types = ["text/html"]

    def __init__(self, formatter_def):
        """
        Initialize object

        :param formatter_def: formatter definition

        :returns: pygeoapi.formatter.base.BaseFormatter
        """
        super().__init__(formatter_def)
        # self.type = 'formatter'

        # self.mediatypes = formatter_def['mediatype']

        # self.name = formatter_def['name']

    def write(self, options={}, data=None):
        """
        Generate data in specified format

        :param options: CSV formatting options
        :param data: dict representation of GeoJSON object

        :returns: string representation of format
        """
        config = OgcApiConfig()
        template_path = config.get_template_path()
        print("TEMPLATE_path=", template_path)
        thelocale = None
        if "locale" in options:
            thelocale = options["locale"]
        print("thelocale=", thelocale)
        jj2template = config.get_jinja2_template(
            rtemplate="jj2_landing_page.html",
            locale=thelocale)
        thetranslator = LocaleTranslator()
        tconfig = thetranslator.translate_struct(
            options["config"], thelocale, is_config=True)
        ret_html = jj2template.render(config=tconfig, data=data)

        return ret_html

    def __repr__(self):
        return '<LandingPageHtmlFormatter> {}'.format(self.name)
