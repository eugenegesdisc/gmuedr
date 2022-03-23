# coding: utf-8

import pytest
import json
from aiohttp import web

from openapi_server.models.edr_feature_collection_geo_json import EdrFeatureCollectionGeoJSON
from openapi_server.models.exception import Exception
from openapi_server.models.one_ofobjectobject import OneOfobjectobject


async def test_list_data_instance_locations(client):
    """Test case for list_data_instance_locations

    List available location identifers for the instance
    """
    params = [('bbox', openapi_server.OneOfobjectobject()),
                    ('datetime', 'datetime_example'),
                    ('limit', 10)]
    headers = { 
        'Accept': 'application/json',
    }
    response = await client.request(
        method='GET',
        path='/edr/collections/{collection_id}/instances/{instance_id}/locations'.format(collection_id='collection_id_example', instance_id='instance_id_example'),
        headers=headers,
        params=params,
        )
    assert response.status == 200, 'Response body is : ' + (await response.read()).decode('utf-8')

