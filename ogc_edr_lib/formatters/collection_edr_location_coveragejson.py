import json
from ogc_edr_lib.formatters.base import BaseFormatter


class CollecionsLocationCoverageJsonFormatter(BaseFormatter):
    """generic Formatter ABC"""
    type = "formatter"
    category = "collection_edr_location"
    supported_media_types = ["application/prs.coverage+json"]

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
        if data is not None:
            if isinstance(data, dict):
                jsonstr = json.dumps(
                    data, default=self._default_json_string_converter)
            else:
                jsonstr = data
        else:
            jsonstr = ""
        return jsonstr

    def __repr__(self):
        return '<CollecionsJsonFormatter> {}'.format(self.name)
