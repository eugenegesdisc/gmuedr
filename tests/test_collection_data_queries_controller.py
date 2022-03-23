# coding: utf-8

import pytest
import json
from aiohttp import web

from openapi_server.models.coverage_json import CoverageJSON
from openapi_server.models.edr_feature_collection_geo_json import EdrFeatureCollectionGeoJSON
from openapi_server.models.exception import Exception
from openapi_server.models.one_ofobjectobject import OneOfobjectobject


async def test_get_collection_data_for_location(client):
    """Test case for get_collection_data_for_location

    Query end point for queries of collection {collectionId} defined by a location id
    """
    params = [('datetime', 'datetime_example'),
                    ('crs', 'native'),
                    ('f', 'f_example')]
    headers = { 
        'Accept': 'application/json',
    }
    response = await client.request(
        method='GET',
        path='/edr/collections/{collection_id}/locations/{location_id}'.format(collection_id='collection_id_example', location_id='location_id_example'),
        headers=headers,
        params=params,
        )
    assert response.status == 200, 'Response body is : ' + (await response.read()).decode('utf-8')


async def test_get_data_for_area(client):
    """Test case for get_data_for_area

    Query end point for area queries  of collection {collectionId} defined by a polygon
    """
    params = [('coords', 'coords_example'),
                    ('z', 'z_example'),
                    ('datetime', 'datetime_example'),
                    ('parameter-name', 'parameter_name_example'),
                    ('crs', 'native'),
                    ('resolution-x', None),
                    ('resolution-y', None),
                    ('f', 'f_example')]
    headers = { 
        'Accept': 'application/json',
    }
    response = await client.request(
        method='GET',
        path='/edr/collections/{collection_id}/area'.format(collection_id='collection_id_example'),
        headers=headers,
        params=params,
        )
    assert response.status == 200, 'Response body is : ' + (await response.read()).decode('utf-8')


async def test_get_data_for_corridor(client):
    """Test case for get_data_for_corridor

    Query end point for Corridor queries  of collection {collectionId} defined by a polygon
    """
    params = [('coords', 'coords_example'),
                    ('z', 'z_example'),
                    ('datetime', 'datetime_example'),
                    ('parameter-name', 'parameter_name_example'),
                    ('corridor-width', 'corridor_width_example'),
                    ('width-units', 'KM'),
                    ('corridor-height', 'corridor_height_example'),
                    ('height-units', 'KM'),
                    ('resolution-x', None),
                    ('resolution-z', None),
                    ('crs', 'native'),
                    ('f', 'f_example')]
    headers = { 
        'Accept': 'application/json',
    }
    response = await client.request(
        method='GET',
        path='/edr/collections/{collection_id}/corridor'.format(collection_id='collection_id_example'),
        headers=headers,
        params=params,
        )
    assert response.status == 200, 'Response body is : ' + (await response.read()).decode('utf-8')


async def test_get_data_for_cube(client):
    """Test case for get_data_for_cube

    Query end point for Cube queries  of collection {collectionId} defined by a cube
    """
    params = [('bbox', openapi_server.OneOfobjectobject()),
                    ('z', 'z_example'),
                    ('datetime', 'datetime_example'),
                    ('parameter-name', 'parameter_name_example'),
                    ('crs', 'native'),
                    ('f', 'f_example')]
    headers = { 
        'Accept': 'application/json',
    }
    response = await client.request(
        method='GET',
        path='/edr/collections/{collection_id}/cube'.format(collection_id='collection_id_example'),
        headers=headers,
        params=params,
        )
    assert response.status == 200, 'Response body is : ' + (await response.read()).decode('utf-8')


async def test_get_data_for_item(client):
    """Test case for get_data_for_item

    Return item {itemId} from collection {collectionId}
    """
    headers = { 
        'Accept': 'application/json',
    }
    response = await client.request(
        method='GET',
        path='/edr/collections/{collection_id}/items/{item_id}'.format(collection_id='collection_id_example', item_id='item_id_example'),
        headers=headers,
        )
    assert response.status == 200, 'Response body is : ' + (await response.read()).decode('utf-8')


async def test_get_data_for_point(client):
    """Test case for get_data_for_point

    Query end point for position queries  of collection {collectionId}
    """
    params = [('coords', 'coords_example'),
                    ('z', 'z_example'),
                    ('datetime', 'datetime_example'),
                    ('parameter-name', 'parameter_name_example'),
                    ('crs', 'native'),
                    ('f', 'f_example')]
    headers = { 
        'Accept': 'application/json',
    }
    response = await client.request(
        method='GET',
        path='/edr/collections/{collection_id}/position'.format(collection_id='collection_id_example'),
        headers=headers,
        params=params,
        )
    assert response.status == 200, 'Response body is : ' + (await response.read()).decode('utf-8')


async def test_get_data_for_radius(client):
    """Test case for get_data_for_radius

    Query end point for radius queries  of collection {collectionId}
    """
    params = [('coords', 'coords_example'),
                    ('within', 10),
                    ('within-units', 'KM'),
                    ('z', 'z_example'),
                    ('datetime', 'datetime_example'),
                    ('parameter-name', 'parameter_name_example'),
                    ('crs', 'native'),
                    ('f', 'f_example')]
    headers = { 
        'Accept': 'application/json',
    }
    response = await client.request(
        method='GET',
        path='/edr/collections/{collection_id}/radius'.format(collection_id='collection_id_example'),
        headers=headers,
        params=params,
        )
    assert response.status == 200, 'Response body is : ' + (await response.read()).decode('utf-8')


async def test_get_data_for_trajectory(client):
    """Test case for get_data_for_trajectory

    Query end point for trajectory queries  of collection {collectionId} defined by a wkt linestring and a iso8601 time period
    """
    params = [('coords', 'coords_example'),
                    ('z', 'z_example'),
                    ('datetime', 'datetime_example'),
                    ('parameter-name', 'parameter_name_example'),
                    ('crs', 'native'),
                    ('f', 'f_example')]
    headers = { 
        'Accept': 'application/json',
    }
    response = await client.request(
        method='GET',
        path='/edr/collections/{collection_id}/trajectory'.format(collection_id='collection_id_example'),
        headers=headers,
        params=params,
        )
    assert response.status == 200, 'Response body is : ' + (await response.read()).decode('utf-8')

