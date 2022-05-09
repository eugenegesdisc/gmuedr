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


class OgcApiCollectionDataByTrajectory(OgcApi):
    def get_data_for_trajectory(
            self, request: web.Request, collection_id, coords, z=None,
            datetime=None, parameter_name=None, crs=None, f=None):
        """Query end point for trajectory queries  of
         collection {collectionId} defined by a wkt linestring and a iso8601
         time period

        Return the data values for the data Polygon defined by the query
         parameters

        :param collection_id: Identifier (id) of a specific collection
        :type collection_id: str
        :param coords: Only data that has a geometry that intersects the area
         defined by the linestring are selected.  The trajectory is defined
         using a Well Known Text string following
           A 2D trajectory, on the surface of earth with no time or height
            dimensions:
            coords&#x3D;LINESTRING(-2.87 51.14 , -2.98 51.36,-3.15 51.03 ,
            -3.48 50.74 ,-3.36 50.9 )
           A 2D trajectory, on the surface of earth with all for the same time
            and no height dimension, time value defined in ISO8601 format by
            the &#x60;datetime&#x60; query parameter :
            coords&#x3D;LINESTRING(-2.87 51.14 , -2.98 51.36 ,-3.15 51.03 ,
            -3.48 50.74 ,-3.36 50.9 )&amp;time&#x3D;2018-02-12T23:00:00Z
           A 2D trajectory, on the surface of earth with no time value but at
            a fixed height level, height defined in the collection height units
            by the &#x60;z&#x60; query parameter :
            coords&#x3D;LINESTRING(-2.87 51.14 , -2.98 51.36 ,-3.15 51.03 ,
            -3.48 50.74 ,-3.36 50.9 )&amp;z&#x3D;850
           A 2D trajectory, on the surface of earth with all for the same time
            and at a fixed height level, time value defined in ISO8601 format
            by the &#x60;datetime&#x60; query parameter and height defined in
            the collection height units by the &#x60;z&#x60; query parameter :
            coords&#x3D;LINESTRING(-2.87 51.14 , -2.98 51.36 ,-3.15 51.03 ,
            -3.48 50.74 ,-3.36 50.9 )
            &amp;time&#x3D;2018-02-12T23:00:00Z&amp;z&#x3D;850
           A 3D trajectory, on the surface of the earth but over a time range
            with no height values:
            coords&#x3D;LINESTRINGM(-2.87 51.14  1560507000,
            -2.98 51.36  1560507600,-3.15 51.03  1560508200,
            -3.48 50.74  1560508500,-3.36 50.9  1560510240)
           A 3D trajectory, on the surface of the earth but over a time range
            with a fixed height value, height defined in the collection height
            units by the &#x60;z&#x60; query parameter :
            coords&#x3D;LINESTRINGM(-2.87 51.14  1560507000,
            -2.98 51.36  1560507600,-3.15 51.03  1560508200,
            -3.48 50.74  1560508500,-3.36 50.9  1560510240)&amp;z&#x3D;200
           A 3D trajectory, through a 3D volume with height or depth, but no
            defined time: coords&#x3D;LINESTRINGZ(-2.87 51.14  0.1,
            -2.98 51.36  0.2,-3.15 51.03  0.3,-3.48 50.74  0.4,-3.36 50.9  0.5)
           A 3D trajectory, through a 3D volume with height or depth, but a
            fixed time time value defined in ISO8601 format by the
            &#x60;datetime&#x60; query parameter:
            coords&#x3D;LINESTRINGZ(-2.87 51.14  0.1,-2.98 51.36  0.2,
            -3.15 51.03  0.3,-3.48 50.74  0.4,
            -3.36 50.9  0.5)&amp;time&#x3D;2018-02-12T23:00:00Z
           A 4D trajectory, through a 3D volume but over a time range:
            oords&#x3D;LINESTRINGZM(-2.87 51.14 0.1 1560507000,
            -2.98 51.36 0.2 1560507600,
            -3.15 51.03 0.3 1560508200, -3.48 50.74 0.4 1560508500,
            -3.36 50.9 0.5 1560510240)
            (using either the &#x60;time&#x60; or &#x60;z&#x60;
            parameters with a 4D trajectory wil generate an error response)
            where Z in &#x60;LINESTRINGZ&#x60; and &#x60;LINESTRINGZM&#x60;
            refers to the height value. &#x60;If the specified CRS does not
            define the height units, the heights units will default to metres
            above mean sea level&#x60;  and the M in &#x60;LINESTRINGM&#x60;
            and &#x60;LINESTRINGZM&#x60; refers to the number of seconds that
            have elapsed since the Unix epoch, that is the time 00:00:00 UTC
            on 1 January 1970. See https://en.wikipedia.org/wiki/Unix_time
        :type coords: str
        :param z: Define the vertical level to return data from i.e.
         z&#x3D;level  for instance if the 850hPa pressure level is being
         queried  z&#x3D;850  or a range to return data for all levels between
         and including 2 defined levels i.e. z&#x3D;minimum value/maximum value
         for instance if all values between and including 10m and 100m
         z&#x3D;10/100  finally a list of height values can be specified
         i.e. z&#x3D;value1,value2,value3  for instance if values at 2m, 10m
         and 80m are required  z&#x3D;2,10,80  An Arithmetic sequence using
         Recurring height intervals, the difference is the number of
         recurrences is defined at the start and the amount to increment the
         height by is defined at the end  i.e. z&#x3D;Rn/min height/height
         interval  so if the request was for 20 height levels 50m apart
         starting at 100m:  z&#x3D;R20/100/50  When not specified data from all
         available heights SHOULD be returned
        :type z: str
        :param datetime: Either a date-time or an interval, open or closed.
        Date and time expressions adhere to RFC 3339. Open intervals are
        expressed using double-dots. Examples:
         * A date-time: \&quot;2018-02-12T23:20:50Z\&quot;
         * A closed interval:
          \&quot;2018-02-12T00:00:00Z/2018-03-18T12:31:12Z\&quot;
         * Open intervals: \&quot;2018-02-12T00:00:00Z/..\&quot; or
          \&quot;../2018-03-18T12:31:12Z\&quot; Only features that have a
          temporal property that intersects the value of &#x60;datetime&#x60;
          are selected. If a feature has multiple temporal properties, it is
          the decision of the server whether only a single temporal property
          is used to determine the extent or all relevant temporal properties.
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
        # ocdata = OgcApiCollectionDataByTrajectory()
        # headers, status, content = ocdata.get_data_for_trajectory(
        #     request, collection_id, coords, z, datetime, parameter_name, crs, f)
        api_path = "/collections/{collectionId}/trajectory"
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
                    "coords": coords,
                    "z": z,
                    "datetime": datetime,
                    "parameter_name": parameter_name,
                    "crs": crs,
                    "f": f
                }
            the_item_data = {
                "parameters": the_parameters,
                "collection_metadata": thecollection_value
            }
        else:
            the_item_data = self._get_collection_data_by_trajectory(
                thecollection_value, collection_id, coords, z, datetime,
                parameter_name, crs, best_match)

        the_final_ret = self._format_get_data_for_trajectory(
            the_item_data, best_match)

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

    def _get_collection_data_by_trajectory(
            self, collection_spec, collection_id, coords, z=None,
            datetime=None, parameter_name=None, crs=None, f=None):
        try:
            theprovider_def = self.config.pluginmanager.get_provider_by_type(
                collection_spec["providers"], "edr")
            theplugin = self.config.\
                pluginmanager.get_plugin_by_category_media_type(
                    "provider", theprovider_def.get("type"),
                    theprovider_def.get("name"))
            theprovider = theplugin.cls(theprovider_def)
            thedata = theprovider.get_data_for_trajectory(
                collection_id, coords, z,
                datetime, parameter_name, crs, f
            )
            return thedata
        except BaseException as error:
            Logger.error(error)
            return None

    def _format_get_data_for_trajectory(
            self, thedata, mediatype: str, loc="en_US"):
        theplugin = self.config.pluginmanager.get_plugin_by_category_media_type(
            "formatter", "collection_edr_trajectory", mediatype)
        # Assuming thedata is already in the suitable format
        if theplugin is None:
            Logger.warning("No formaater for mediatype={} for {}.".format(
                mediatype, "collection_edr_trajectory"
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
