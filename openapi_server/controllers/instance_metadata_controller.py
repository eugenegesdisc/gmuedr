from typing import List, Dict
from aiohttp import web

from openapi_server.models.edr_feature_collection_geo_json import EdrFeatureCollectionGeoJSON
from openapi_server.models.exception import Exception
from openapi_server.models.one_ofobjectobject import OneOfobjectobject
from openapi_server import util


async def list_data_instance_locations(request: web.Request, collection_id, instance_id, bbox=None, datetime=None, limit=None) -> web.Response:
    """List available location identifers for the instance

    List the locations available for the instance of the collection

    :param collection_id: Identifier (id) of a specific collection
    :type collection_id: str
    :param instance_id: Identifier (id) of a specific instance of a collection
    :type instance_id: str
    :param bbox: Only features that have a geometry that intersects the bounding box are selected. The bounding box is provided as four or six numbers, depending on whether the coordinate reference system includes a vertical axis (height or depth): * Lower left corner, coordinate axis 1 * Lower left corner, coordinate axis 2 * Minimum value, coordinate axis 3 (optional) * Upper right corner, coordinate axis 1 * Upper right corner, coordinate axis 2 * Maximum value, coordinate axis 3 (optional) The coordinate reference system of the values is specified by the &#x60;crs&#x60; query parameter. If the &#x60;crs&#x60; query parameter is not defined the coordinate reference system is defined by the default &#x60;crs&#x60; for the query type. If a default &#x60;crs&#x60; has not been defined the values will be assumed to be in the WGS 84 longitude/latitude (http://www.opengis.net/def/crs/OGC/1.3/CRS84) coordinate reference system. For WGS 84 longitude/latitude the values are in most cases the sequence of minimum longitude, minimum latitude, maximum longitude and maximum latitude. However, in cases where the box spans the antimeridian the first value (west-most box edge) is larger than the third value (east-most box edge). If the vertical axis is included, the third and the sixth number are the bottom and the top of the 3-dimensional bounding box. If a feature has multiple spatial geometry properties, it is the decision of the server whether only a single spatial geometry property is used to determine the extent or all relevant geometries.
    :type bbox: dict | bytes
    :param datetime: Either a date-time or an interval, open or closed. Date and time expressions adhere to RFC 3339. Open intervals are expressed using double-dots. Examples: * A date-time: \&quot;2018-02-12T23:20:50Z\&quot; * A closed interval: \&quot;2018-02-12T00:00:00Z/2018-03-18T12:31:12Z\&quot; * Open intervals: \&quot;2018-02-12T00:00:00Z/..\&quot; or \&quot;../2018-03-18T12:31:12Z\&quot; Only features that have a temporal property that intersects the value of &#x60;datetime&#x60; are selected. If a feature has multiple temporal properties, it is the decision of the server whether only a single temporal property is used to determine the extent or all relevant temporal properties.
    :type datetime: str
    :param limit: The optional limit parameter limits the number of results that are presented in the response document. Minimum &#x3D; 1. Maximum &#x3D; 10000. Default &#x3D; 10.
    :type limit: int

    """
#    bbox = .from_dict(bbox)
    return web.Response(status=200)
