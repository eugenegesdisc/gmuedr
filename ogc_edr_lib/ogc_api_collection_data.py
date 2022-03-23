from typing import Tuple, Union
from aiohttp import web
from ogc_edr_lib.ogc_api import OgcApi
import logging

from ogc_edr_lib.ogc_api_collection_data_item import (
    OgcApiCollectionDataItem)
from ogc_edr_lib.ogc_api_collection_data_by_point import (
    OgcApiCollectionDataByPoint
)
from ogc_edr_lib.ogc_api_collection_data_by_area import (
    OgcApiCollectionDataByArea
)
Logger = logging.getLogger(__name__)


class OgcApiCollectionData(OgcApi):

    def get_data_for_area(
            self, request: web.Request, collection_id, coords, z=None,
            datetime=None, parameter_name=None, crs=None, resolution_x=None,
            resolution_y=None, f=None):
        """Query end point for area queries  of collection {collectionId}
        defined by a polygon

        Return the data values for the data area defined by the query parameters

        :param collection_id: Identifier (id) of a specific collection
        :type collection_id: str
        :param coords: Only data that has a geometry that intersects the area
         defined by the polygon are selected.  The polygon is defined using a Well
         Known Text string following
          coords&#x3D;POLYGON((x y,x1 y1,x2 y2,...,xn yn x y))
         which are values in the coordinate system defined by the crs query
         parameter (if crs is not defined the values will be assumed to be WGS84
         longitude/latitude coordinates).  For instance a polygon that roughly
         describes an area that contains South West England in WGS84 would look
         like:
          coords&#x3D;POLYGON((-6.1 50.3,-4.35 51.4,-2.6 51.6,-2.8 50.6,-5.3
           49.9,-6.1,50.3))
         see http://portal.opengeospatial.org/files/?artifact_id&#x3D;25355 and
         https://en.wikipedia.org/wiki/Well-known_text_representation_of_geometry
         The coords parameter will only support 2D POLYGON definitions
        :type coords: str
        :param z: Define the vertical level to return data from i.e. z&#x3D;level
         for instance if the 850hPa pressure level is being queried  z&#x3D;850
         or a range to return data for all levels between and including 2 defined
         levels i.e. z&#x3D;minimum value/maximum value  for instance if all values
         between and including 10m and 100m  z&#x3D;10/100  finally a list of
         height values can be specified i.e. z&#x3D;value1,value2,value3  for
         instance if values at 2m, 10m and 80m are required  z&#x3D;2,10,80
         An Arithmetic sequence using Recurring height intervals, the difference
         is the number of recurrences is defined at the start and the amount to
         increment the height by is defined at the end  i.e.
         z&#x3D;Rn/min height/height interval  so if the request was for 20 height
         levels 50m apart starting at 100m:
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
          or \&quot;../2018-03-18T12:31:12Z\&quot; Only features that have a
          temporal property that intersects the value of &#x60;datetime&#x60;
          are selected.
         If a feature has multiple temporal properties, it is the decision of the
         server whether only a single temporal property is used to determine the
         extent or all relevant temporal properties.
        :type datetime: str
        :param parameter_name: comma delimited list of parameters to retrieve data
         for.  Valid parameters are listed in the collections metadata
        :type parameter_name: str
        :param crs: identifier (id) of the coordinate system to return data in list
         of valid crs identifiers for the chosen collection are defined in the
         metadata responses.  If not supplied the coordinate reference system will
         default to WGS84.
        :type crs: str
        #x3D;10  would retrieve 10 values along the x-axis from the minimum x
         coordinate to maximum x coordinate (i.e. a value at both the minimum x and
         maximum x coordinates and 8 values between).
        :param resolution_x: Defined it the user requires data at a different
         resolution from the native resolution of the data along the x-axis
         If this is a single value it denotes the number of intervals to retrieve
         data for along the x-axis    i.e. resolution-x&
        :type resolution_x: dict | bytes
        #x3D;10  would retrieve 10 values along the y-axis from the minimum y
         coordinate to maximum y coordinate (i.e. a value at both the minimum y
         and maximum y coordinates and 8 values between).
        :param resolution_y: Defined it the user requires data at a different
         resolution from the native resolution of the data along the y-axis  If
         this is a single value it denotes the number of intervals to retrieve data
         for along the y-axis    i.e. resolution-y&
        :type resolution_y: dict | bytes
        :param f: format to return the data response in
        :type f: str

        """
        ocdata = OgcApiCollectionDataByArea()
        headers, status, content = ocdata.get_data_for_area(
            request, collection_id, coords, z, datetime, parameter_name,
            crs, resolution_x, resolution_y, f)
        return headers, status, content

    def get_data_for_item(
            self, request: web.Request, collection_id, item_id):
        """Return item {itemId} from collection {collectionId}

        Query end point to retrieve data from collection {collectionId} using a unique identifier

        :param collection_id: Identifier (id) of a specific collection
        :type collection_id: str
        :param item_id: Retrieve data from the collection using a unique identifier.
        :type item_id: str

        """
        ocdata = OgcApiCollectionDataItem()
        headers, status, content = ocdata.get_data_for_item(
            request, collection_id, item_id)

        return headers, status, content

    def get_data_for_point(
            self, request: web.Request, collection_id, coords, z=None,
            datetime=None, parameter_name=None, crs=None, f=None):
        """Query end point for position queries  of collection {collectionId}

        Query end point for position queries

        :param collection_id: Identifier (id) of a specific collection
        :type collection_id: str
        :param coords: location(s) to return data for, the coordinates are
         defined by a Well Known Text (wkt) string. to retrieve a single
         location :  POINT(x y) i.e. POINT(0 51.48) for Greenwich, London
         And for a list of locations  MULTIPOINT((x y),(x1 y1),(x2 y2),(x3 y3))
         i.e.
   MULTIPOINT((38.9 -77),(48.85 2.35),(39.92 116.38),(-35.29 149.1),(51.5 -0.1))
         see http://portal.opengeospatial.org/files/?artifact_id&#x3D;25355 and
         https://en.wikipedia.org/wiki/Well-known_text_representation_of_geometry
         the coordinate values will depend on the CRS parameter, if this is not
         defined the values will be assumed to WGS84 values
         (i.e x&#x3D;longitude and y&#x3D;latitude)
        :type coords: str
        :param z: Define the vertical level to return data from
         i.e. z&#x3D;level  for instance if the 850hPa pressure level is being
         queried  z&#x3D;850  or a range to return data for all levels between
         and including 2 defined levels i.e. z&#x3D;minimum value/maximum value
         for instance if all values between and including 10m and
         100m  z&#x3D;10/100  finally a list of height values can be specified
         i.e. z&#x3D;value1,value2,value3  for instance if values at 2m, 10m
         and 80m are required  z&#x3D;2,10,80  An Arithmetic sequence using
         Recurring height intervals, the difference is the number of recurrences
         is defined at the start and the amount to increment the height by is
         defined at the end  i.e. z&#x3D;Rn/min height/height interval  so if
         the request was for 20 height levels 50m apart starting at
         100m:  z&#x3D;R20/100/50  When not specified data from all available
         heights SHOULD be returned
        :type z: str
        :param datetime: Either a date-time or an interval, open or closed.
         Date and time expressions adhere to RFC 3339. Open intervals are
         expressed using double-dots. Examples:
         * A date-time: \&quot;2018-02-12T23:20:50Z\&quot;
         * A closed interval:
          \&quot;2018-02-12T00:00:00Z/2018-03-18T12:31:12Z\&quot;
         * Open intervals: \&quot;2018-02-12T00:00:00Z/..\&quot;
          or \&quot;../2018-03-18T12:31:12Z\&quot; Only features that have
          a temporal property that intersects the value of &#x60;datetime&#x60;
          are selected. If a feature has multiple temporal properties, it is
          the decision of the server whether only a single temporal property is
          used to determine the extent or all relevant temporal properties.
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
        ocdata = OgcApiCollectionDataByPoint()
        headers, status, content = ocdata.get_data_for_point(
            request, collection_id, coords, z,
            datetime, parameter_name, crs, f)

        return headers, status, content
