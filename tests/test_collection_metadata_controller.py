# coding: utf-8

import pytest
import json
from aiohttp import web

from openapi_server.models.collection import Collection
from openapi_server.models.edr_feature_collection_geo_json import EdrFeatureCollectionGeoJSON
from openapi_server.models.exception import Exception
from openapi_server.models.instances import Instances
from openapi_server.models.one_ofobjectobject import OneOfobjectobject


async def test_get_collection_instances(client):
    """Test case for get_collection_instances

    List data instances of {collectionId}
    """
    params = [('f', 'f_example')]
    headers = { 
        'Accept': 'application/json',
    }
    response = await client.request(
        method='GET',
        path='/edr/collections/{collection_id}/instances'.format(collection_id='collection_id_example'),
        headers=headers,
        params=params,
        )
    assert response.status == 200, 'Response body is : ' + (await response.read()).decode('utf-8')


async def test_get_queries(client):
    """Test case for get_queries

    List query types supported by the collection
    """
    params = [('f', 'f_example')]
    headers = { 
        'Accept': 'application/json',
    }
    response = await client.request(
        method='GET',
        path='/edr/collections/{collection_id}'.format(collection_id='collection_id_example'),
        headers=headers,
        params=params,
        )
    assert response.status == 200, 'Response body is : ' + (await response.read()).decode('utf-8')


async def test_list_collection_data_locations(client):
    """Test case for list_collection_data_locations

    List available location identifers for the collection
    """
    params = [('bbox', openapi_server.OneOfobjectobject()),
                    ('datetime', 'datetime_example'),
                    ('limit', 10)]
    headers = { 
        'Accept': 'application/json',
    }
    response = await client.request(
        method='GET',
        path='/edr/collections/{collection_id}/locations'.format(collection_id='collection_id_example'),
        headers=headers,
        params=params,
        )
    assert response.status == 200, 'Response body is : ' + (await response.read()).decode('utf-8')


async def test_list_data_items(client):
    """Test case for list_data_items

    List available items
    """
    params = [('bbox', openapi_server.OneOfobjectobject()),
                    ('datetime', 'datetime_example'),
                    ('limit', 10)]
    headers = { 
        'Accept': 'application/json',
    }
    response = await client.request(
        method='GET',
        path='/edr/collections/{collection_id}/items'.format(collection_id='collection_id_example'),
        headers=headers,
        params=params,
        )
    assert response.status == 200, 'Response body is : ' + (await response.read()).decode('utf-8')

