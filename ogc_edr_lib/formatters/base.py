import datetime


class BaseFormatter:
    """generic Formatter ABC"""
    type = "formatter"
    category = "base"
    supported_media_types = []

    def __init__(self, formatter_def):
        """
        Initialize object

        :param formatter_def: formatter definition

        :returns: ogc_edr_lib.formatter.base.BaseFormatter
        """

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

        raise None

    def _default_json_string_converter(self, o):
        if isinstance(o, datetime.datetime):
            return datetime.datetime.strftime(o, "%Y-%m-%dT%H:%M:%SZ")

    def __repr__(self):
        return '<BaseFormatter> {}'.format(self.name)
