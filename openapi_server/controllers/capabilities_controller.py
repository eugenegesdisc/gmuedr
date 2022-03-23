from typing import List, Dict
from aiohttp import web

from openapi_server.models.collections import Collections
from openapi_server.models.conf_classes import ConfClasses
from openapi_server.models.exception import Exception
from openapi_server.models.groups import Groups
from openapi_server.models.landing_page import LandingPage
from openapi_server.models.one_ofobjectobject import OneOfobjectobject
from openapi_server import util

from ogc_edr_lib.ogc_api_capabilities import OgcApiCapabilities

import logging

Logger = logging.getLogger(__name__)


async def get_landing_page(request: web.Request, f=None) -> web.Response:
    """landing page of this API

    The landing page provides links to the API definition, the Conformance statements and the metadata about the feature data in this dataset.

    :param f: format to return the data response in
    :type f: str

    """
    capab = OgcApiCapabilities()
    headers, status, content = capab.landing_page(request)
#    return web.Response(text="landing page", status=200)
    return web.Response(body=content, status=status, headers=headers)


async def get_requirements_classes(request: web.Request, f=None) -> web.Response:
    """information about standards that this API conforms to

    list all requirements classes specified in a standard that the server conforms to

    :param f: format to return the data response in
    :type f: str

    """
    capab = OgcApiCapabilities()
    headers, status, content = capab.get_requirements_classes(request)
    # return web.Response(status=200)
    return web.Response(body=content, status=status, headers=headers)


async def group_infomation(request: web.Request, group_id, f=None) -> web.Response:
    """List of links to information available in the group



    :param group_id: Identifier (name) of a specific group
    :type group_id: str
    :param f: format to return the data response in
    :type f: str

    """
    return web.Response(status=200)


async def list_collections(request: web.Request, bbox=None, datetime=None, f=None) -> web.Response:
    """List the avialable collections from the service



    :param bbox: Only features that have a geometry that intersects the bounding box are selected. The bounding box is provided as four or six numbers, depending on whether the coordinate reference system includes a vertical axis (height or depth): * Lower left corner, coordinate axis 1 * Lower left corner, coordinate axis 2 * Minimum value, coordinate axis 3 (optional) * Upper right corner, coordinate axis 1 * Upper right corner, coordinate axis 2 * Maximum value, coordinate axis 3 (optional) The coordinate reference system of the values is specified by the &#x60;crs&#x60; query parameter. If the &#x60;crs&#x60; query parameter is not defined the coordinate reference system is defined by the default &#x60;crs&#x60; for the query type. If a default &#x60;crs&#x60; has not been defined the values will be assumed to be in the WGS 84 longitude/latitude (http://www.opengis.net/def/crs/OGC/1.3/CRS84) coordinate reference system. For WGS 84 longitude/latitude the values are in most cases the sequence of minimum longitude, minimum latitude, maximum longitude and maximum latitude. However, in cases where the box spans the antimeridian the first value (west-most box edge) is larger than the third value (east-most box edge). If the vertical axis is included, the third and the sixth number are the bottom and the top of the 3-dimensional bounding box. If a feature has multiple spatial geometry properties, it is the decision of the server whether only a single spatial geometry property is used to determine the extent or all relevant geometries.
    :type bbox: dict | bytes
    :param datetime: Either a date-time or an interval, open or closed. Date and time expressions adhere to RFC 3339. Open intervals are expressed using double-dots. Examples: * A date-time: \&quot;2018-02-12T23:20:50Z\&quot; * A closed interval: \&quot;2018-02-12T00:00:00Z/2018-03-18T12:31:12Z\&quot; * Open intervals: \&quot;2018-02-12T00:00:00Z/..\&quot; or \&quot;../2018-03-18T12:31:12Z\&quot; Only features that have a temporal property that intersects the value of &#x60;datetime&#x60; are selected. If a feature has multiple temporal properties, it is the decision of the server whether only a single temporal property is used to determine the extent or all relevant temporal properties.
    :type datetime: str
    :param f: format to return the data response in
    :type f: str

    """
    # bbox = .from_dict(bbox)
    capab = OgcApiCapabilities()
    headers, status, content = capab.list_collections(
        request, bbox, datetime, f)
    return web.Response(body=content, status=200, headers=headers)


async def list_groups(request: web.Request, f=None) -> web.Response:
    """Provide a list of avialable data groups



    :param f: format to return the data response in
    :type f: str

    """
    return web.Response(status=200)
