from ogc_edr_lib.ogc_api_config import OgcApiConfig


class OgcApi:
    config = {}

    def __init__(self):
        """
        constructor

        :param config: configuration object

        :returns: `ogc_edr_lib.ogc_api.OgcApi` instance
        """
        config = OgcApiConfig()

        self.config = config
