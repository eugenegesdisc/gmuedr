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


class OgcApiCollectionDataByCube(OgcApi):
    def get_data_for_cube(
            self, request: web.Request, collection_id, bbox=None, z=None,
            datetime=None, parameter_name=None, crs=None, f=None):
        """Query end point for Cube queries  of collection {collectionId}
         defined by a cube

        Return the data values for the data Cube defined by the query parameters

        :param collection_id: Identifier (id) of a specific collection
        :type collection_id: str
        :param bbox: Only features that have a geometry that intersects the
         bounding box are selected. The bounding box is provided as four or six
         numbers, depending on whether the coordinate reference system includes
         a vertical axis (height or depth):
          * Lower left corner, coordinate axis 1
          * Lower left corner, coordinate axis 2
          * Minimum value, coordinate axis 3 (optional)
          * Upper right corner, coordinate axis 1
          * Upper right corner, coordinate axis 2
          * Maximum value, coordinate axis 3 (optional)
         The coordinate reference system of the values is specified by the
         &#x60;crs&#x60; query parameter. If the &#x60;crs&#x60; query
         parameter is not defined the coordinate reference system is defined by
         the default &#x60;crs&#x60; for the query type. If a default
         &#x60;crs&#x60; has not been defined the values will be assumed to be
         in the WGS 84 longitude/latitude
         (http://www.opengis.net/def/crs/OGC/1.3/CRS84) coordinate reference
         system. For WGS 84 longitude/latitude the values are in most cases the
         sequence of minimum longitude, minimum latitude, maximum longitude
         and maximum latitude. However, in cases where the box spans the
         antimeridian the first value (west-most box edge) is larger than the
         third value (east-most box edge). If the vertical axis is included,
         the third and the sixth number are the bottom and the top of the
         3-dimensional bounding box. If a feature has multiple spatial geometry
         properties, it is the decision of the server whether only a single
         spatial geometry property is used to determine the extent or all
         relevant geometries.
        :type bbox: dict | bytes
        :param z: Define the vertical levels to return data from
        A range to return data for all levels between and including 2 defined
        levels  i.e. z&#x3D;minimum value/maximum value  for instance if all
        values between and including 10m and 100m  z&#x3D;10/100 A list of
        height values can be specified i.e. z&#x3D;value1,value2,value3
        for instance if values at 2m, 10m and 80m are required  z&#x3D;2,10,80
        An Arithmetic sequence using Recurring height intervals, the difference
        is the number of recurrences is defined at the start and the amount to
        increment the height by is defined at the end
        i.e. z&#x3D;Rn/min height/height interval
        so if the request was for 20 height levels 50m apart starting at 100m:
        z&#x3D;R20/100/50  When not specified data from all available heights
        SHOULD be returned
        :type z: str
        :param datetime: Either a date-time or an interval, open or closed. Date
        and time expressions adhere to RFC 3339. Open intervals are expressed
        using double-dots. Examples:
        * A date-time: \&quot;2018-02-12T23:20:50Z\&quot;
        * A closed interval:
         \&quot;2018-02-12T00:00:00Z/2018-03-18T12:31:12Z\&quot;
        * Open intervals: \&quot;2018-02-12T00:00:00Z/..\&quot;
        or \&quot;../2018-03-18T12:31:12Z\&quot;
        Only features that have a temporal property that intersects the value
        of &#x60;datetime&#x60; are selected. If
        a feature has multiple temporal properties, it is the decision of the
        server whether only a single temporal property is used to determine the
        extent or all relevant temporal properties.
        :type datetime: str
        :param parameter_name: comma delimited list of parameters to retrieve
        data for.  Valid parameters are listed in the collections metadata
        :type parameter_name: str
        :param crs: identifier (id) of the coordinate system to return data in
        list of valid crs identifiers for the chosen collection are defined in
        the metadata responses.  If not supplied the coordinate reference
        system will default to WGS84.
        :type crs: str
        :param f: format to return the data response in
        :type f: str

        """
    #    bbox = .from_dict(bbox)
    #    return web.Response(status=200)
        api_path = "/collections/{collectionId}/cube"
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
                    "bbox": bbox,
                    "z": z,
                    "datetime": datetime,
                    "parameter_name": parameter_name,
                    "crs": crs,
                    "f": f
                }
            the_ret_data = {
                "parameters": the_parameters,
                "collection_metadata": thecollection_value
            }
        else:
            the_ret_data = self._get_collection_data_by_cube(
                thecollection_value,
                collection_id, bbox, z, datetime, parameter_name, crs, f)
        the_final_ret = self._format_get_data_for_cube(
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

    def _format_get_data_for_cube(
            self, thedata, mediatype: str, loc="en_US"):
        theplugin = self.config.pluginmanager.get_plugin_by_category_media_type(
            "formatter", "collection_edr_cube", mediatype)
        # Assuming thedata is already in the suitable format
        if theplugin is None:
            Logger.warning("No formaater for mediatype={} for {}.".format(
                mediatype, "collection_edr_cube"
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

    def _get_collection_data_by_cube(
            self, collection_spec, collection_id, bbox=None, z=None,
            datetime=None, parameter_name=None, crs=None, f=None):
        try:
            theprovider_def = self.config.pluginmanager.get_provider_by_type(
                collection_spec["providers"], "edr")
            theplugin = self.config.\
                pluginmanager.get_plugin_by_category_media_type(
                    "provider", theprovider_def.get("type"),
                    theprovider_def.get("name"))
            theprovider = theplugin.cls(theprovider_def)
            thedata = theprovider.get_data_for_cube(
                collection_id, bbox, z, datetime, parameter_name, crs, f)
            return thedata
        except BaseException as error:
            Logger.error(error)
            return None
