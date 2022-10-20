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
import logging

from openapi_server.models.edr_feature_collection_geo_json import (
    EdrFeatureCollectionGeoJSON
)

Logger = logging.getLogger(__name__)


class OgcApiCollectionDataByLocation(OgcApi):
    def get_collection_data_for_location(
            self, request: web.Request, collection_id, location_id,
            datetime=None, crs=None, f=None):
        """Query end point for queries of collection {collectionId}
         defined by a location id

        Return data the for the location defined by locationId

        :param collection_id: Identifier (id) of a specific collection
        :type collection_id: str
        :param location_id: Retreive data for the location defined by
         locationId (i.e. London_Heathrow, EGLL, 03772 etc)
        :type location_id: str
        :param datetime: Either a date-time or an interval, open or closed.
         Date and time expressions adhere to RFC 3339. Open intervals are
         expressed using double-dots. Examples:
          * A date-time: \&quot;2018-02-12T23:20:50Z\&quot;
          * A closed interval:
           \&quot;2018-02-12T00:00:00Z/2018-03-18T12:31:12Z\&quot;
          * Open intervals: \&quot;2018-02-12T00:00:00Z/..\&quot; or
           \&quot;../2018-03-18T12:31:12Z\&quot;
            Only features that have a temporal property that intersects the
            value of &#x60;datetime&#x60; are selected. If a feature has
            multiple temporal properties, it is the decision of the server
            whether only a single temporal property is used to determine the
            extent or all relevant temporal properties.
        :type datetime: str
        :param crs: identifier (id) of the coordinate system to return data
         in list of valid crs identifiers for the chosen collection are defined
         in the metadata responses.  If not supplied the coordinate reference
         system will default to WGS84.
        :type crs: str
        :param f: format to return the data response in
        :type f: str

        """
        api_path = "/collections/{collectionId}/locations/{locationId}"
        qstrs = parse_qs(request.query_string)
        the_locale = qstrs.get('locale')
        the_formats = qstrs.get('f')
        the_formats = self.get_full_media_type_from_f_param(the_formats)
        best_match = self._negotiate_content_best_match(
            api_path, request, the_formats)

        translator = LocaleTranslator()
        thecollection_value = translator.get_config_translated(
            the_locale)["resources"][collection_id]
        if best_match == "text/html":
            the_parameters = {
                    "collection_id": collection_id,
                    "location_id": location_id,
                    "datetime": datetime,
                    "crs": crs,
                    "f": f
                }
            the_ret_data = {
                "parameters": the_parameters,
                "collection_metadata": thecollection_value
            }
        else:
            the_ret_data = self._get_collection_data_by_location(
                thecollection_value, collection_id, location_id, datetime,
                crs, best_match)
        the_final_ret = self._format_get_data_for_location(
            the_ret_data, best_match)
        headers = CIMultiDict()
        headers["Content-Type"] = best_match
        return headers, 200, the_final_ret

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
        elif f_format.lower() == 'coveragejson':
            ret_format = 'application/prs.coverage+json'
        elif f_format.lower() == 'geojson':
            ret_format = 'application/geo+json'
        elif f_format.lower() == 'netcdf':
            ret_format = 'application/x-netcdf'
        return ret_format

    def _negotiate_content_best_match(
            self, api_path: str,
            request: web.Request,
            the_formats: Union[list, None]):
        # get the best_match
        response_formats = self.config.get_response_formats(api_path)
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

    def _format_get_data_for_location(
            self, thedata, mediatype: str, loc="en_US"):
        theplugin = self.config.pluginmanager.get_plugin_by_category_media_type(
            "formatter", "collection_edr_location", mediatype)
        # Assuming thedata is already in the suitable format
        if theplugin is None:
            Logger.warning("No formater for mediatype={} for {}.".format(
                mediatype, "collection_edr_location"
            ))
            return thedata
        thewriter = theplugin.cls({})
        return thewriter.write(
            options={
                "config": self.config.get_config(),
                "openapi": self.config.load_openapi_file(),
                "locale": loc
            },
            data=thedata)

    def _get_collection_data_by_location(
            self, collection_spec, collection_id, location_id,
            datetime=None, crs=None, f=None):
        try:
            theprovider_def = self.config.pluginmanager.get_provider_by_type(
                collection_spec["providers"], "edr")
            theplugin = self.config.\
                pluginmanager.get_plugin_by_category_media_type(
                    "provider", theprovider_def.get("type"),
                    theprovider_def.get("name"))
            theprovider = theplugin.cls(theprovider_def)
            thedata = theprovider.get_data_for_location(
                collection_id, location_id, datetime,
                crs, f)
            return thedata
        except BaseException as error:
            Logger.error(error)
            return None
