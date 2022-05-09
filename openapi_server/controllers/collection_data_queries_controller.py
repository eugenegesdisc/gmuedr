from typing import List, Dict
from aiohttp import web

from openapi_server.models.coverage_json import CoverageJSON
from openapi_server.models.edr_feature_collection_geo_json import EdrFeatureCollectionGeoJSON
from openapi_server.models.exception import Exception
from openapi_server.models.one_ofobjectobject import OneOfobjectobject
from openapi_server import util

from ogc_edr_lib.ogc_api_collection_data import OgcApiCollectionData


async def get_collection_data_for_location(request: web.Request, collection_id, location_id, datetime=None, crs=None, f=None) -> web.Response:
    """Query end point for queries of collection {collectionId} defined by a location id

    Return data the for the location defined by locationId

    :param collection_id: Identifier (id) of a specific collection
    :type collection_id: str
    :param location_id: Retreive data for the location defined by locationId (i.e. London_Heathrow, EGLL, 03772 etc)
    :type location_id: str
    :param datetime: Either a date-time or an interval, open or closed. Date and time expressions adhere to RFC 3339. Open intervals are expressed using double-dots. Examples: * A date-time: \&quot;2018-02-12T23:20:50Z\&quot; * A closed interval: \&quot;2018-02-12T00:00:00Z/2018-03-18T12:31:12Z\&quot; * Open intervals: \&quot;2018-02-12T00:00:00Z/..\&quot; or \&quot;../2018-03-18T12:31:12Z\&quot; Only features that have a temporal property that intersects the value of &#x60;datetime&#x60; are selected. If a feature has multiple temporal properties, it is the decision of the server whether only a single temporal property is used to determine the extent or all relevant temporal properties.
    :type datetime: str
    :param crs: identifier (id) of the coordinate system to return data in list of valid crs identifiers for the chosen collection are defined in the metadata responses.  If not supplied the coordinate reference system will default to WGS84.
    :type crs: str
    :param f: format to return the data response in
    :type f: str

    """
    ocdata = OgcApiCollectionData()
    headers, status, content = ocdata.get_collection_data_for_location(
        request, collection_id, location_id, datetime,
        crs, f)
    return web.Response(body=content, status=status, headers=headers)

# async def get_data_for_area(request: web.Request, collection_id, coords, z=None, datetime=None, parameter_name=None, crs=None, resolution_x=None, resolution_y=None, f=None) -> web.Response:


async def get_data_for_area(request: web.Request, collection_id, coords=None, z=None, datetime=None, parameter_name=None, crs=None, resolution_x=None, resolution_y=None, f=None) -> web.Response:
    """Query end point for area queries  of collection {collectionId} defined by a polygon

    Return the data values for the data area defined by the query parameters

    :param collection_id: Identifier (id) of a specific collection
    :type collection_id: str
    :param coords: Only data that has a geometry that intersects the area defined by the polygon are selected.  The polygon is defined using a Well Known Text string following  coords&#x3D;POLYGON((x y,x1 y1,x2 y2,...,xn yn x y))  which are values in the coordinate system defined by the crs query parameter (if crs is not defined the values will be assumed to be WGS84 longitude/latitude coordinates).  For instance a polygon that roughly describes an area that contains South West England in WGS84 would look like:  coords&#x3D;POLYGON((-6.1 50.3,-4.35 51.4,-2.6 51.6,-2.8 50.6,-5.3 49.9,-6.1,50.3))  see http://portal.opengeospatial.org/files/?artifact_id&#x3D;25355 and https://en.wikipedia.org/wiki/Well-known_text_representation_of_geometry  The coords parameter will only support 2D POLYGON definitions
    :type coords: str
    :param z: Define the vertical level to return data from i.e. z&#x3D;level  for instance if the 850hPa pressure level is being queried  z&#x3D;850  or a range to return data for all levels between and including 2 defined levels i.e. z&#x3D;minimum value/maximum value  for instance if all values between and including 10m and 100m  z&#x3D;10/100  finally a list of height values can be specified i.e. z&#x3D;value1,value2,value3  for instance if values at 2m, 10m and 80m are required  z&#x3D;2,10,80  An Arithmetic sequence using Recurring height intervals, the difference is the number of recurrences is defined at the start and the amount to increment the height by is defined at the end  i.e. z&#x3D;Rn/min height/height interval  so if the request was for 20 height levels 50m apart starting at 100m:  z&#x3D;R20/100/50  When not specified data from all available heights SHOULD be returned
    :type z: str
    :param datetime: Either a date-time or an interval, open or closed. Date and time expressions adhere to RFC 3339. Open intervals are expressed using double-dots. Examples: * A date-time: \&quot;2018-02-12T23:20:50Z\&quot; * A closed interval: \&quot;2018-02-12T00:00:00Z/2018-03-18T12:31:12Z\&quot; * Open intervals: \&quot;2018-02-12T00:00:00Z/..\&quot; or \&quot;../2018-03-18T12:31:12Z\&quot; Only features that have a temporal property that intersects the value of &#x60;datetime&#x60; are selected. If a feature has multiple temporal properties, it is the decision of the server whether only a single temporal property is used to determine the extent or all relevant temporal properties.
    :type datetime: str
    :param parameter_name: comma delimited list of parameters to retrieve data for.  Valid parameters are listed in the collections metadata
    :type parameter_name: str
    :param crs: identifier (id) of the coordinate system to return data in list of valid crs identifiers for the chosen collection are defined in the metadata responses.  If not supplied the coordinate reference system will default to WGS84.
    :type crs: str
    :param resolution_x: Defined it the user requires data at a different resolution from the native resolution of the data along the x-axis  If this is a single value it denotes the number of intervals to retrieve data for along the x-axis    i.e. resolution-x&#x3D;10  would retrieve 10 values along the x-axis from the minimum x coordinate to maximum x coordinate (i.e. a value at both the minimum x and maximum x coordinates and 8 values between).
    :type resolution_x: dict | bytes
    :param resolution_y: Defined it the user requires data at a different resolution from the native resolution of the data along the y-axis  If this is a single value it denotes the number of intervals to retrieve data for along the y-axis    i.e. resolution-y&#x3D;10  would retrieve 10 values along the y-axis from the minimum y coordinate to maximum y coordinate (i.e. a value at both the minimum y and maximum y coordinates and 8 values between).
    :type resolution_y: dict | bytes
    :param f: format to return the data response in
    :type f: str

    """
#    resolution_x = .from_dict(resolution_x)
#    resolution_y = .from_dict(resolution_y)
#    return web.Response(status=200)
    ocdata = OgcApiCollectionData()
    headers, status, content = ocdata.get_data_for_area(
        request, collection_id, coords, z, datetime, parameter_name,
        crs, resolution_x, resolution_y, f)
    return web.Response(body=content, status=status, headers=headers)

# async def get_data_for_corridor(request: web.Request, collection_id, coords, corridor_width, width_units, corridor_height, height_units, z=None, datetime=None, parameter_name=None, resolution_x=None, resolution_z=None, crs=None, f=None) -> web.Response:


async def get_data_for_corridor(request: web.Request, collection_id, coords=None, corridor_width=None, width_units=None, corridor_height=None, height_units=None, z=None, datetime=None, parameter_name=None, resolution_x=None, resolution_z=None, crs=None, f=None) -> web.Response:
    """Query end point for Corridor queries  of collection {collectionId} defined by a polygon

    Return the data values for the Corridor defined by the query parameters

    :param collection_id: Identifier (id) of a specific collection
    :type collection_id: str
    :param coords: Only data that has a geometry that intersects the area defined by the linestring are selected.  The trajectory is defined using a Well Known Text string following  A 2D trajectory, on the surface of earth with no time or height dimensions:     coords&#x3D;LINESTRING(-2.87 51.14 , -2.98 51.36,-3.15 51.03 ,-3.48 50.74 ,-3.36 50.9 )  A 2D trajectory, on the surface of earth with all for the same time and no height dimension, time value defined in ISO8601 format by the &#x60;datetime&#x60; query parameter :     coords&#x3D;LINESTRING(-2.87 51.14 , -2.98 51.36 ,-3.15 51.03 ,-3.48 50.74 ,-3.36 50.9 )&amp;time&#x3D;2018-02-12T23:00:00Z  A 2D trajectory, on the surface of earth with no time value but at a fixed height level, height defined in the collection height units by the &#x60;z&#x60; query parameter :     coords&#x3D;LINESTRING(-2.87 51.14 , -2.98 51.36 ,-3.15 51.03 ,-3.48 50.74 ,-3.36 50.9 )&amp;z&#x3D;850  A 2D trajectory, on the surface of earth with all for the same time and at a fixed height level, time value defined in ISO8601 format by the &#x60;datetime&#x60; query parameter and height defined in the collection height units by the &#x60;z&#x60; query parameter :     coords&#x3D;LINESTRING(-2.87 51.14 , -2.98 51.36 ,-3.15 51.03 ,-3.48 50.74 ,-3.36 50.9 )&amp;time&#x3D;2018-02-12T23:00:00Z&amp;z&#x3D;850  A 3D trajectory, on the surface of the earth but over a time range with no height values: coords&#x3D;LINESTRINGM(-2.87 51.14  1560507000,-2.98 51.36  1560507600,-3.15 51.03  1560508200,-3.48 50.74  1560508500,-3.36 50.9  1560510240)  A 3D trajectory, on the surface of the earth but over a time range with a fixed height value, height defined in the collection height units by the &#x60;z&#x60; query parameter : coords&#x3D;LINESTRINGM(-2.87 51.14  1560507000,-2.98 51.36  1560507600,-3.15 51.03  1560508200,-3.48 50.74  1560508500,-3.36 50.9  1560510240)&amp;z&#x3D;200   A 3D trajectory, through a 3D volume with height or depth, but no defined time: coords&#x3D;LINESTRINGZ(-2.87 51.14  0.1,-2.98 51.36  0.2,-3.15 51.03  0.3,-3.48 50.74  0.4,-3.36 50.9  0.5)  A 3D trajectory, through a 3D volume with height or depth, but a fixed time time value defined in ISO8601 format by the &#x60;datetime&#x60; query parameter: coords&#x3D;LINESTRINGZ(-2.87 51.14  0.1,-2.98 51.36  0.2,-3.15 51.03  0.3,-3.48 50.74  0.4,-3.36 50.9  0.5)&amp;time&#x3D;2018-02-12T23:00:00Z  A 4D trajectory, through a 3D volume but over a time range: coords&#x3D;LINESTRINGZM(-2.87 51.14 0.1 1560507000,-2.98 51.36 0.2 1560507600,-3.15 51.03 0.3 1560508200, -3.48 50.74 0.4 1560508500, -3.36 50.9 0.5 1560510240) (using either the &#x60;time&#x60; or &#x60;z&#x60; parameters with a 4D trajectory wil generate an error response)  where Z in &#x60;LINESTRINGZ&#x60; and &#x60;LINESTRINGZM&#x60; refers to the height value. &#x60;If the specified CRS does not define the height units, the heights units will default to metres above mean sea level&#x60;  and the M in &#x60;LINESTRINGM&#x60; and &#x60;LINESTRINGZM&#x60; refers to the number of seconds that have elapsed since the Unix epoch, that is the time 00:00:00 UTC on 1 January 1970. See https://en.wikipedia.org/wiki/Unix_time
    :type coords: str
    :param corridor_width: width of the corridor  The width value represents the whole width of the corridor where the trajectory supplied in the &#x60;coords&#x60; query parameter is the centre point of the corridor  &#x60;corridor-width&#x3D;{width}&#x60;  e.g.  corridor-width&#x3D;100  Would be a request for a corridor 100 units wide with the coords parameter values being the centre point of the requested corridor, the request would be for data values 50 units either side of the trajectory coordinates defined in the coords parameter.  The width units supported by the collection will be provided in the API metadata responses
    :type corridor_width: str
    :param width_units: Distance units for the corridor-width parameter
    :type width_units: str
    :param corridor_height: height of the corridor  The height value represents the whole height of the corridor where the trajectory supplied in the &#x60;coords&#x60; query parameter is the centre point of the corridor  &#x60;corridor-height&#x3D;{height}&#x60;  e.g.  corridor-height&#x3D;100  Would be a request for a corridor 100 units high with the coords parameter values being the centre point of the requested corridor, the request would be for data values 50 units either side of the trajectory coordinates defined in the coords parameter.  The height units supported by the collection will be provided in the API metadata responses
    :type corridor_height: str
    :param height_units: Distance units for the corridor-height parameter
    :type height_units: str
    :param z: Define the vertical level to return data from i.e. z&#x3D;level  for instance if the 850hPa pressure level is being queried  z&#x3D;850  or a range to return data for all levels between and including 2 defined levels i.e. z&#x3D;minimum value/maximum value  for instance if all values between and including 10m and 100m  z&#x3D;10/100  finally a list of height values can be specified i.e. z&#x3D;value1,value2,value3  for instance if values at 2m, 10m and 80m are required  z&#x3D;2,10,80  An Arithmetic sequence using Recurring height intervals, the difference is the number of recurrences is defined at the start and the amount to increment the height by is defined at the end  i.e. z&#x3D;Rn/min height/height interval  so if the request was for 20 height levels 50m apart starting at 100m:  z&#x3D;R20/100/50  When not specified data from all available heights SHOULD be returned
    :type z: str
    :param datetime: Either a date-time or an interval, open or closed. Date and time expressions adhere to RFC 3339. Open intervals are expressed using double-dots. Examples: * A date-time: \&quot;2018-02-12T23:20:50Z\&quot; * A closed interval: \&quot;2018-02-12T00:00:00Z/2018-03-18T12:31:12Z\&quot; * Open intervals: \&quot;2018-02-12T00:00:00Z/..\&quot; or \&quot;../2018-03-18T12:31:12Z\&quot; Only features that have a temporal property that intersects the value of &#x60;datetime&#x60; are selected. If a feature has multiple temporal properties, it is the decision of the server whether only a single temporal property is used to determine the extent or all relevant temporal properties.
    :type datetime: str
    :param parameter_name: comma delimited list of parameters to retrieve data for.  Valid parameters are listed in the collections metadata
    :type parameter_name: str
    :param resolution_x: Defined it the user requires data at a different resolution from the native resolution of the data along the x-axis  If this is a single value it denotes the number of intervals to retrieve data for along the x-axis    i.e. resolution-x&#x3D;10  would retrieve 10 values along the x-axis from the minimum x coordinate to maximum x coordinate (i.e. a value at both the minimum x and maximum x coordinates and 8 values between).
    :type resolution_x: dict | bytes
    :param resolution_z: Defined it the user requires data at a different resolution from the native resolution of the data along the z-axis  If this is a single value it denotes the number of intervals to retrieve data for along the z-axis    i.e. resolution-z&#x3D;10  would retrieve 10 values along the z-axis from the minimum z coordinate to maximum z  coordinate (i.e. a value at both the minimum z and maximum z coordinates and 8 values between).
    :type resolution_z: dict | bytes
    :param crs: identifier (id) of the coordinate system to return data in list of valid crs identifiers for the chosen collection are defined in the metadata responses.  If not supplied the coordinate reference system will default to WGS84.
    :type crs: str
    :param f: format to return the data response in
    :type f: str

    """
#    resolution_x = .from_dict(resolution_x)
#    resolution_z = .from_dict(resolution_z)
#    return web.Response(status=200)
    print("z=", z)
    print("datetime=", datetime)
    print("resolution_x=", resolution_x)
    print("resolution_z=", resolution_z)
    ocdata = OgcApiCollectionData()
    headers, status, content = ocdata.get_data_for_corridor(
        request, collection_id, coords, corridor_width,
        width_units, corridor_height, height_units, z, datetime,
        parameter_name, resolution_x, resolution_z, crs, f)
    return web.Response(body=content, status=status, headers=headers)


async def get_data_for_cube(request: web.Request, collection_id, bbox=None, z=None, datetime=None, parameter_name=None, crs=None, f=None) -> web.Response:
    """Query end point for Cube queries  of collection {collectionId} defined by a cube

    Return the data values for the data Cube defined by the query parameters

    :param collection_id: Identifier (id) of a specific collection
    :type collection_id: str
    :param bbox: Only features that have a geometry that intersects the bounding box are selected. The bounding box is provided as four or six numbers, depending on whether the coordinate reference system includes a vertical axis (height or depth): * Lower left corner, coordinate axis 1 * Lower left corner, coordinate axis 2 * Minimum value, coordinate axis 3 (optional) * Upper right corner, coordinate axis 1 * Upper right corner, coordinate axis 2 * Maximum value, coordinate axis 3 (optional) The coordinate reference system of the values is specified by the &#x60;crs&#x60; query parameter. If the &#x60;crs&#x60; query parameter is not defined the coordinate reference system is defined by the default &#x60;crs&#x60; for the query type. If a default &#x60;crs&#x60; has not been defined the values will be assumed to be in the WGS 84 longitude/latitude (http://www.opengis.net/def/crs/OGC/1.3/CRS84) coordinate reference system. For WGS 84 longitude/latitude the values are in most cases the sequence of minimum longitude, minimum latitude, maximum longitude and maximum latitude. However, in cases where the box spans the antimeridian the first value (west-most box edge) is larger than the third value (east-most box edge). If the vertical axis is included, the third and the sixth number are the bottom and the top of the 3-dimensional bounding box. If a feature has multiple spatial geometry properties, it is the decision of the server whether only a single spatial geometry property is used to determine the extent or all relevant geometries.
    :type bbox: dict | bytes
    :param z: Define the vertical levels to return data from  A range to return data for all levels between and including 2 defined levels  i.e. z&#x3D;minimum value/maximum value  for instance if all values between and including 10m and 100m  z&#x3D;10/100  A list of height values can be specified i.e. z&#x3D;value1,value2,value3  for instance if values at 2m, 10m and 80m are required  z&#x3D;2,10,80  An Arithmetic sequence using Recurring height intervals, the difference is the number of recurrences is defined at the start and the amount to increment the height by is defined at the end  i.e. z&#x3D;Rn/min height/height interval  so if the request was for 20 height levels 50m apart starting at 100m:  z&#x3D;R20/100/50  When not specified data from all available heights SHOULD be returned
    :type z: str
    :param datetime: Either a date-time or an interval, open or closed. Date and time expressions adhere to RFC 3339. Open intervals are expressed using double-dots. Examples: * A date-time: \&quot;2018-02-12T23:20:50Z\&quot; * A closed interval: \&quot;2018-02-12T00:00:00Z/2018-03-18T12:31:12Z\&quot; * Open intervals: \&quot;2018-02-12T00:00:00Z/..\&quot; or \&quot;../2018-03-18T12:31:12Z\&quot; Only features that have a temporal property that intersects the value of &#x60;datetime&#x60; are selected. If a feature has multiple temporal properties, it is the decision of the server whether only a single temporal property is used to determine the extent or all relevant temporal properties.
    :type datetime: str
    :param parameter_name: comma delimited list of parameters to retrieve data for.  Valid parameters are listed in the collections metadata
    :type parameter_name: str
    :param crs: identifier (id) of the coordinate system to return data in list of valid crs identifiers for the chosen collection are defined in the metadata responses.  If not supplied the coordinate reference system will default to WGS84.
    :type crs: str
    :param f: format to return the data response in
    :type f: str

    """
#    bbox = .from_dict(bbox)
#    return web.Response(status=200)
    ocdata = OgcApiCollectionData()
    headers, status, content = ocdata.get_data_for_cube(
        request, collection_id, bbox, z, datetime, parameter_name, crs, f)
    return web.Response(body=content, status=status, headers=headers)


async def get_data_for_item(request: web.Request, collection_id, item_id) -> web.Response:
    """Return item {itemId} from collection {collectionId}

    Query end point to retrieve data from collection {collectionId} using a unique identifier

    :param collection_id: Identifier (id) of a specific collection
    :type collection_id: str
    :param item_id: Retrieve data from the collection using a unique identifier.
    :type item_id: str

    """
    ocdata = OgcApiCollectionData()
    headers, status, content = ocdata.get_data_for_item(
        request, collection_id, item_id)
    return web.Response(body=content, status=status, headers=headers)

# async def get_data_for_point(request: web.Request, collection_id, coords, z=None, datetime=None, parameter_name=None, crs=None, f=None) -> web.Response:


async def get_data_for_point(request: web.Request, collection_id, coords=None, z=None, datetime=None, parameter_name=None, crs=None, f=None) -> web.Response:
    """Query end point for position queries  of collection {collectionId}

    Query end point for position queries

    :param collection_id: Identifier (id) of a specific collection
    :type collection_id: str
    :param coords: location(s) to return data for, the coordinates are defined by a Well Known Text (wkt) string. to retrieve a single location :  POINT(x y) i.e. POINT(0 51.48) for Greenwich, London  And for a list of locations  MULTIPOINT((x y),(x1 y1),(x2 y2),(x3 y3))  i.e. MULTIPOINT((38.9 -77),(48.85 2.35),(39.92 116.38),(-35.29 149.1),(51.5 -0.1))  see http://portal.opengeospatial.org/files/?artifact_id&#x3D;25355 and https://en.wikipedia.org/wiki/Well-known_text_representation_of_geometry  the coordinate values will depend on the CRS parameter, if this is not defined the values will be assumed to WGS84 values (i.e x&#x3D;longitude and y&#x3D;latitude)
    :type coords: str
    :param z: Define the vertical level to return data from i.e. z&#x3D;level  for instance if the 850hPa pressure level is being queried  z&#x3D;850  or a range to return data for all levels between and including 2 defined levels i.e. z&#x3D;minimum value/maximum value  for instance if all values between and including 10m and 100m  z&#x3D;10/100  finally a list of height values can be specified i.e. z&#x3D;value1,value2,value3  for instance if values at 2m, 10m and 80m are required  z&#x3D;2,10,80  An Arithmetic sequence using Recurring height intervals, the difference is the number of recurrences is defined at the start and the amount to increment the height by is defined at the end  i.e. z&#x3D;Rn/min height/height interval  so if the request was for 20 height levels 50m apart starting at 100m:  z&#x3D;R20/100/50  When not specified data from all available heights SHOULD be returned
    :type z: str
    :param datetime: Either a date-time or an interval, open or closed. Date and time expressions adhere to RFC 3339. Open intervals are expressed using double-dots. Examples: * A date-time: \&quot;2018-02-12T23:20:50Z\&quot; * A closed interval: \&quot;2018-02-12T00:00:00Z/2018-03-18T12:31:12Z\&quot; * Open intervals: \&quot;2018-02-12T00:00:00Z/..\&quot; or \&quot;../2018-03-18T12:31:12Z\&quot; Only features that have a temporal property that intersects the value of &#x60;datetime&#x60; are selected. If a feature has multiple temporal properties, it is the decision of the server whether only a single temporal property is used to determine the extent or all relevant temporal properties.
    :type datetime: str
    :param parameter_name: comma delimited list of parameters to retrieve data for.  Valid parameters are listed in the collections metadata
    :type parameter_name: str
    :param crs: identifier (id) of the coordinate system to return data in list of valid crs identifiers for the chosen collection are defined in the metadata responses.  If not supplied the coordinate reference system will default to WGS84.
    :type crs: str
    :param f: format to return the data response in
    :type f: str

    """
    ocdata = OgcApiCollectionData()
    headers, status, content = ocdata.get_data_for_point(
            request, collection_id, coords, z,
            datetime, parameter_name, crs, f)
    return web.Response(body=content, status=status, headers=headers)

# async def get_data_for_radius(request: web.Request, collection_id, coords, within, within_units, z=None, datetime=None, parameter_name=None, crs=None, f=None) -> web.Response:


async def get_data_for_radius(request: web.Request, collection_id, coords=None, within=None, within_units=None, z=None, datetime=None, parameter_name=None, crs=None, f=None) -> web.Response:
    """Query end point for radius queries  of collection {collectionId}

    Query end point for to return values within a defined radius of a point queries

    :param collection_id: Identifier (id) of a specific collection
    :type collection_id: str
    :param coords: location(s) to return data for, the coordinates are defined by a Well Known Text (wkt) string. to retrieve a single location :  POINT(x y) i.e. POINT(0 51.48) for Greenwich, London  see http://portal.opengeospatial.org/files/?artifact_id&#x3D;25355 and https://en.wikipedia.org/wiki/Well-known_text_representation_of_geometry  the coordinate values will depend on the CRS parameter, if this is not defined the values will be assumed to WGS84 values (i.e x&#x3D;longitude and y&#x3D;latitude)
    :type coords: str
    :param within: Defines radius of area around defined coordinates to include in the data selection
    :type within:
    :param within_units: Distance units for the within parameter
    :type within_units: str
    :param z: Define the vertical level to return data from i.e. z&#x3D;level  for instance if the 850hPa pressure level is being queried  z&#x3D;850  or a range to return data for all levels between and including 2 defined levels i.e. z&#x3D;minimum value/maximum value  for instance if all values between and including 10m and 100m  z&#x3D;10/100  finally a list of height values can be specified i.e. z&#x3D;value1,value2,value3  for instance if values at 2m, 10m and 80m are required  z&#x3D;2,10,80  An Arithmetic sequence using Recurring height intervals, the difference is the number of recurrences is defined at the start and the amount to increment the height by is defined at the end  i.e. z&#x3D;Rn/min height/height interval  so if the request was for 20 height levels 50m apart starting at 100m:  z&#x3D;R20/100/50  When not specified data from all available heights SHOULD be returned
    :type z: str
    :param datetime: Either a date-time or an interval, open or closed. Date and time expressions adhere to RFC 3339. Open intervals are expressed using double-dots. Examples: * A date-time: \&quot;2018-02-12T23:20:50Z\&quot; * A closed interval: \&quot;2018-02-12T00:00:00Z/2018-03-18T12:31:12Z\&quot; * Open intervals: \&quot;2018-02-12T00:00:00Z/..\&quot; or \&quot;../2018-03-18T12:31:12Z\&quot; Only features that have a temporal property that intersects the value of &#x60;datetime&#x60; are selected. If a feature has multiple temporal properties, it is the decision of the server whether only a single temporal property is used to determine the extent or all relevant temporal properties.
    :type datetime: str
    :param parameter_name: comma delimited list of parameters to retrieve data for.  Valid parameters are listed in the collections metadata
    :type parameter_name: str
    :param crs: identifier (id) of the coordinate system to return data in list of valid crs identifiers for the chosen collection are defined in the metadata responses.  If not supplied the coordinate reference system will default to WGS84.
    :type crs: str
    :param f: format to return the data response in
    :type f: str

    """
    ocdata = OgcApiCollectionData()
    headers, status, content = ocdata.get_data_for_radius(
        request, collection_id, coords, within, within_units, z,
        datetime, parameter_name, crs, f)
    return web.Response(body=content, status=status, headers=headers)


async def get_data_for_trajectory(request: web.Request, collection_id, coords, z=None, datetime=None, parameter_name=None, crs=None, f=None) -> web.Response:
    """Query end point for trajectory queries  of collection {collectionId} defined by a wkt linestring and a iso8601 time period

    Return the data values for the data Polygon defined by the query parameters

    :param collection_id: Identifier (id) of a specific collection
    :type collection_id: str
    :param coords: Only data that has a geometry that intersects the area defined by the linestring are selected.  The trajectory is defined using a Well Known Text string following  A 2D trajectory, on the surface of earth with no time or height dimensions:     coords&#x3D;LINESTRING(-2.87 51.14 , -2.98 51.36,-3.15 51.03 ,-3.48 50.74 ,-3.36 50.9 )  A 2D trajectory, on the surface of earth with all for the same time and no height dimension, time value defined in ISO8601 format by the &#x60;datetime&#x60; query parameter :     coords&#x3D;LINESTRING(-2.87 51.14 , -2.98 51.36 ,-3.15 51.03 ,-3.48 50.74 ,-3.36 50.9 )&amp;time&#x3D;2018-02-12T23:00:00Z  A 2D trajectory, on the surface of earth with no time value but at a fixed height level, height defined in the collection height units by the &#x60;z&#x60; query parameter :     coords&#x3D;LINESTRING(-2.87 51.14 , -2.98 51.36 ,-3.15 51.03 ,-3.48 50.74 ,-3.36 50.9 )&amp;z&#x3D;850  A 2D trajectory, on the surface of earth with all for the same time and at a fixed height level, time value defined in ISO8601 format by the &#x60;datetime&#x60; query parameter and height defined in the collection height units by the &#x60;z&#x60; query parameter :     coords&#x3D;LINESTRING(-2.87 51.14 , -2.98 51.36 ,-3.15 51.03 ,-3.48 50.74 ,-3.36 50.9 )&amp;time&#x3D;2018-02-12T23:00:00Z&amp;z&#x3D;850  A 3D trajectory, on the surface of the earth but over a time range with no height values: coords&#x3D;LINESTRINGM(-2.87 51.14  1560507000,-2.98 51.36  1560507600,-3.15 51.03  1560508200,-3.48 50.74  1560508500,-3.36 50.9  1560510240)  A 3D trajectory, on the surface of the earth but over a time range with a fixed height value, height defined in the collection height units by the &#x60;z&#x60; query parameter : coords&#x3D;LINESTRINGM(-2.87 51.14  1560507000,-2.98 51.36  1560507600,-3.15 51.03  1560508200,-3.48 50.74  1560508500,-3.36 50.9  1560510240)&amp;z&#x3D;200   A 3D trajectory, through a 3D volume with height or depth, but no defined time: coords&#x3D;LINESTRINGZ(-2.87 51.14  0.1,-2.98 51.36  0.2,-3.15 51.03  0.3,-3.48 50.74  0.4,-3.36 50.9  0.5)  A 3D trajectory, through a 3D volume with height or depth, but a fixed time time value defined in ISO8601 format by the &#x60;datetime&#x60; query parameter: coords&#x3D;LINESTRINGZ(-2.87 51.14  0.1,-2.98 51.36  0.2,-3.15 51.03  0.3,-3.48 50.74  0.4,-3.36 50.9  0.5)&amp;time&#x3D;2018-02-12T23:00:00Z  A 4D trajectory, through a 3D volume but over a time range: coords&#x3D;LINESTRINGZM(-2.87 51.14 0.1 1560507000,-2.98 51.36 0.2 1560507600,-3.15 51.03 0.3 1560508200, -3.48 50.74 0.4 1560508500, -3.36 50.9 0.5 1560510240) (using either the &#x60;time&#x60; or &#x60;z&#x60; parameters with a 4D trajectory wil generate an error response)  where Z in &#x60;LINESTRINGZ&#x60; and &#x60;LINESTRINGZM&#x60; refers to the height value. &#x60;If the specified CRS does not define the height units, the heights units will default to metres above mean sea level&#x60;  and the M in &#x60;LINESTRINGM&#x60; and &#x60;LINESTRINGZM&#x60; refers to the number of seconds that have elapsed since the Unix epoch, that is the time 00:00:00 UTC on 1 January 1970. See https://en.wikipedia.org/wiki/Unix_time
    :type coords: str
    :param z: Define the vertical level to return data from i.e. z&#x3D;level  for instance if the 850hPa pressure level is being queried  z&#x3D;850  or a range to return data for all levels between and including 2 defined levels i.e. z&#x3D;minimum value/maximum value  for instance if all values between and including 10m and 100m  z&#x3D;10/100  finally a list of height values can be specified i.e. z&#x3D;value1,value2,value3  for instance if values at 2m, 10m and 80m are required  z&#x3D;2,10,80  An Arithmetic sequence using Recurring height intervals, the difference is the number of recurrences is defined at the start and the amount to increment the height by is defined at the end  i.e. z&#x3D;Rn/min height/height interval  so if the request was for 20 height levels 50m apart starting at 100m:  z&#x3D;R20/100/50  When not specified data from all available heights SHOULD be returned
    :type z: str
    :param datetime: Either a date-time or an interval, open or closed. Date and time expressions adhere to RFC 3339. Open intervals are expressed using double-dots. Examples: * A date-time: \&quot;2018-02-12T23:20:50Z\&quot; * A closed interval: \&quot;2018-02-12T00:00:00Z/2018-03-18T12:31:12Z\&quot; * Open intervals: \&quot;2018-02-12T00:00:00Z/..\&quot; or \&quot;../2018-03-18T12:31:12Z\&quot; Only features that have a temporal property that intersects the value of &#x60;datetime&#x60; are selected. If a feature has multiple temporal properties, it is the decision of the server whether only a single temporal property is used to determine the extent or all relevant temporal properties.
    :type datetime: str
    :param parameter_name: comma delimited list of parameters to retrieve data for.  Valid parameters are listed in the collections metadata
    :type parameter_name: str
    :param crs: identifier (id) of the coordinate system to return data in list of valid crs identifiers for the chosen collection are defined in the metadata responses.  If not supplied the coordinate reference system will default to WGS84.
    :type crs: str
    :param f: format to return the data response in
    :type f: str

    """
    ocdata = OgcApiCollectionData()
    headers, status, content = ocdata.get_data_for_trajectory(
        request, collection_id, coords, z, datetime, parameter_name, crs, f)
    return web.Response(body=content, status=status, headers=headers)
