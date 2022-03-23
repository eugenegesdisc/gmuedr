class BaseProvider:
    """generic Formatter ABC"""
    type = 'provider'
    category = 'base'
    supported_media_types = []

    def __init__(self, provider_def):
        """
        Initialize object

        :param provider_def: provider definition

        :returns: ogc_edr_lib.provider.base.BaseProvider
        """
        self.provider_def = provider_def

    def query(self, **kwargs):
        """
        Generate data in specified format

        :param options: CSV formatting options
        :param data: dict representation of GeoJSON object

        :returns: string representation of format
        """

        raise None

    def __repr__(self):
        return '<BaseFormatter> {}'.format(self.name)
