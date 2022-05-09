from openapi_server.models.edr_feature_collection_geo_json import (
    EdrFeatureCollectionGeoJSON
)
from multidict import CIMultiDict
from typing import Tuple, Union
from aiohttp import web
from urllib.parse import urlparse, parse_qs
from ogc_edr_lib.l10n import LocaleTranslator
from ogc_edr_lib.ogc_api import OgcApi
import json
# from datetime import datetime
from ogc_edr_lib.l10n import LocaleTranslator
import logging

from openapi_server.models.edr_feature_collection_geo_json import (
    EdrFeatureCollectionGeoJSON
)

Logger = logging.getLogger(__name__)


class OgcApiCollectionDataItem(OgcApi):
    def get_full_media_type_from_f_param(self, f_formats: list):
        if f_formats is None:
            return None
        ret_formats = []
        for f in f_formats:
            the_f = self._get_full_media_type_from_f_param(f)
            ret_formats.append(the_f)
        return ret_formats

    def _get_full_media_type_from_f_param(self, f_format):
        ret_format = f_format
        if f_format.lower() == 'json':
            ret_format = 'application/json'
        elif f_format.lower() == 'html':
            ret_format = 'text/html'
        return ret_format

    def _negotiate_content_best_match(self, request: web.Request,
                                      the_formats: Union[list, None]):
        # get the best_match
        response_formats = self.config.get_response_formats("/")
        header_accept = ",".join(request.headers.getall('ACCEPT', '*/*'))
        best_match = None
        Logger.debug("header_accept= {}".format(header_accept))
        Logger.debug("the_formats= {}".format(the_formats))

        if the_formats is not None:
            best_match = self.config.get_mimetype_best_match(
                response_formats, ",".join(the_formats))
        if best_match is None:
            best_match = self.config.get_mimetype_best_match(
                response_formats, header_accept)
        return best_match

    def get_data_for_item(
            self, request: web.Request, collection_id, item_id):
        """Return item {itemId} from collection {collectionId}

        Query end point to retrieve data from collection {collectionId} using a unique identifier

        :param collection_id: Identifier (id) of a specific collection
        :type collection_id: str
        :param item_id: Retrieve data from the collection using a unique identifier.
        :type item_id: str

        """
        qstrs = parse_qs(request.query_string)
        the_locale = qstrs.get('locale')
        the_formats = qstrs.get('f')
        the_formats = self.get_full_media_type_from_f_param(the_formats)
        best_match = self._negotiate_content_best_match(request, the_formats)

        translator = LocaleTranslator()
        thecollection_value = translator.get_config_translated(
            the_locale)["resources"][collection_id]
        the_item_data = self._get_collection_item_data(
            thecollection_value, collection_id, item_id)

        headers = CIMultiDict()
        headers["Content-Type"] = best_match
        return headers, 200, the_item_data

    def _get_collection_item_data(
            self, collection_spec, collection_id, item_id,
            r_media_type="application/json"):
        try:
            theprovider_def = self.config.pluginmanager.get_provider_by_type(
                collection_spec["providers"], "edr")
            theplugin = self.config.\
                pluginmanager.get_plugin_by_category_media_type(
                    "provider", theprovider_def.get("type"),
                    theprovider_def.get("name"))
            theprovider = theplugin.cls(theprovider_def)
            thedata = theprovider.get_data_for_item(
                collection_id, item_id
            )
            return thedata
        except BaseException as error:
            Logger.error(error)
            return None
