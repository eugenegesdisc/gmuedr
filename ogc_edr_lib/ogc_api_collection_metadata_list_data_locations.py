from multidict import CIMultiDict
from typing import Union
from aiohttp import web
from urllib.parse import parse_qs
from ogc_edr_lib.l10n import LocaleTranslator
from ogc_edr_lib.ogc_api import OgcApi
import logging

Logger = logging.getLogger(__name__)


class OgcApiCollectionMetadataListDataLocations(OgcApi):

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

    def list_collection_data_locations(
            self, request: web.Request, collection_id, bbox=None,
            datetime=None, limit=None):
        """List available location identifers for the collection

        List the locations available for the collection

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
         The coordinate reference system of the values is specified by
         the &#x60;crs&#x60; query parameter. If the &#x60;crs&#x60;
         query parameter is not defined the coordinate reference system is
         defined by the default &#x60;crs&#x60;
         for the query type. If a default &#x60;crs&#x60;
         has not been defined the values will be assumed to be in the WGS 84
         longitude/latitude (http://www.opengis.net/def/crs/OGC/1.3/CRS84)
         coordinate reference system. For WGS 84 longitude/latitude the values
         are in most cases the sequence of minimum longitude, minimum latitude,
         maximum longitude and maximum latitude. However, in cases where the
         box spans the antimeridian the first value (west-most box edge) is
         larger than the third value (east-most box edge). If the vertical
         axis is included, the third and the sixth number are the bottom and
         the top of the 3-dimensional bounding box. If a feature has multiple
         spatial geometry properties, it is the decision of the server whether
         only a single spatial geometry property is used to determine the
         extent or all relevant geometries.
        :type bbox: dict | bytes
        :param datetime: Either a date-time or an interval, open or closed.
         Date and time expressions adhere to RFC 3339. Open intervals are
         expressed using double-dots. Examples:
         * A date-time: \&quot;2018-02-12T23:20:50Z\&quot;
         * A closed interval:
          \&quot;2018-02-12T00:00:00Z/2018-03-18T12:31:12Z\&quot;
         * Open intervals: \&quot;2018-02-12T00:00:00Z/..\&quot;
          or \&quot;../2018-03-18T12:31:12Z\&quot;
          Only features that have a temporal property that intersects the
          value of &#x60;datetime&#x60; are selected. If a feature has multiple
          temporal properties, it is the decision of the server whether only
          a single temporal property is used to determine the extent or all
          relevant temporal properties.
        :type datetime: str
        :param limit: The optional limit parameter limits the number of results
         that are presented in the response document. Minimum &#x3D; 1.
         Maximum &#x3D; 10000. Default &#x3D; 10.
        :type limit: int

        """
        api_path = "/collections/{collectionId}/locations"
        qstrs = parse_qs(request.query_string)
        the_locale = qstrs.get('locale')
        the_formats = qstrs.get('f')
        the_formats = self.get_full_media_type_from_f_param(the_formats)
        best_match = self._negotiate_content_best_match(
            api_path, request, the_formats)

        the_offset = qstrs.get("offset")
        translator = LocaleTranslator()
        thecollection_value = translator.get_config_translated(
            the_locale)["resources"][collection_id]
        if best_match == "text/html":
            the_parameters = {
                    "collection_id": collection_id,
                    "bbox": bbox,
                    "datetime": datetime,
                    "limit": limit,
                    "f": best_match
                }
            thecollection_data = {
                "parameters": the_parameters,
                "collection_metadata": thecollection_value
            }
        else:
            thecollection_data = self._get_collection_locations(
                thecollection_value,
                collection_id, bbox, datetime, limit, the_offset,
                best_match)

#        retcontent = self._get_collection_items(
#            collection_id, thecollection_data, best_match)
        the_final_ret = self._format_list_collection_data_locations(
            thecollection_data, best_match)
        headers = CIMultiDict()
        headers["Content-Type"] = best_match
        status = 200
        content = the_final_ret
        return headers, status, content

    def _get_collection_locations(
        self, collection_spec: dict,
        collection_id,
        bbox=None,
        datetime=None, limit=None, offset=None,
        r_media_type="en_US"
    ):
        """
        Form a collection record from key-value pair.

        :param key: A unique id for collection
        :param value: The collection metadata in config file.
        :param r_media_type: return media type

        :returns: FeatureCollection
        """
        try:
            theprovider_def = self.config.pluginmanager.get_provider_by_type(
                collection_spec["providers"], "edr")
            theplugin = self.config.\
                pluginmanager.get_plugin_by_category_media_type(
                    "provider", theprovider_def.get("type"),
                    theprovider_def.get("name"))
            theprovider = theplugin.cls(theprovider_def)
            thedata = theprovider.list_collection_data_locations(
                collection_id, bbox, datetime, limit, offset)
            # type: str=None,
            # features: List[FeatureGeoJSON]=None,
            # parameters: List[Parameter]=None,
            # links: List[Link]=None,
            # time_stamp: datetime=None,
            # number_matched: int=None,
            # number_returned: int=None
            # thedata = EdrFeatureCollectionGeoJSON(
            #     type="FeatureCollection"
            # )
            return thedata
        except BaseException as error:
            Logger.error(error)
            return None

    def _format_list_collection_data_locations(
            self, thedata, mediatype: str, loc="en_US"):
        theplugin = self.config.pluginmanager.get_plugin_by_category_media_type(
            "formatter", "collection_edr_location", mediatype)
        # Assuming thedata is already in the suitable format
        if theplugin is None:
            Logger.warning("No formaater for mediatype={} for {}.".format(
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
