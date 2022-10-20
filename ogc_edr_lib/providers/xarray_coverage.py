import xarray
import logging
from ogc_edr_lib.providers.base import BaseProvider
from ogc_edr_lib.ogc_api_config import OgcApiConfig
from ogc_edr_lib.l10n import LocaleTranslator

Logger = logging.getLogger(__name__)


class XarrayCoverageProvider(BaseProvider):
    """generic Formatter ABC"""
    type = "provider"
    category = "coverage"
    supported_media_types = ["netcdf", "xarray"]

    def __init__(self, provider_def, collection_spec=None):
        """
        Initialize object

        :param provider_def: provider definition

        :returns: pygeoapi.formatter.base.BaseFormatter
        """
        super().__init__(provider_def, collection_spec=collection_spec)

    def query_items(self, bbox=None,
                    datetime=None, limit=None):
        """
        Generate data in specified format

        :param options: CSV formatting options
        :param data: dict representation of GeoJSON object

        :returns: string representation of format
        """
        ret_data = None
        try:
            thedata = self.provider_def["data"]
            if thedata.endswith(".zarr"):
                open_func = xarray.open_zarr
            else:
                open_func = xarray.open_dataset
            thedata = open_func(thedata)
        except Exception as err:
            Logger.warning(err)
            return None

        return ret_data

    def __repr__(self):
        return '<BaseFormatter> {}'.format(self.name)
