# coding: utf-8

import pytest
import json
from aiohttp import web

from openapi_server.models.collections import Collections
from openapi_server.models.conf_classes import ConfClasses
from openapi_server.models.exception import Exception
from openapi_server.models.groups import Groups
from openapi_server.models.landing_page import LandingPage
from openapi_server.models.one_ofobjectobject import OneOfobjectobject


async def test_get_landing_page(client):
    """Test case for get_landing_page

    landing page of this API
    """
    params = [('f', 'f_example')]
    headers = { 
        'Accept': 'application/json',
    }
    response = await client.request(
        method='GET',
        path='/edr/',
        headers=headers,
        params=params,
        )
    assert response.status == 200, 'Response body is : ' + (await response.read()).decode('utf-8')


async def test_get_requirements_classes(client):
    """Test case for get_requirements_classes

    information about standards that this API conforms to
    """
    params = [('f', 'f_example')]
    headers = { 
        'Accept': 'application/json',
    }
    response = await client.request(
        method='GET',
        path='/edr/conformance',
        headers=headers,
        params=params,
        )
    assert response.status == 200, 'Response body is : ' + (await response.read()).decode('utf-8')


async def test_group_infomation(client):
    """Test case for group_infomation

    List of links to information available in the group
    """
    params = [('f', 'f_example')]
    headers = { 
        'Accept': 'application/json',
    }
    response = await client.request(
        method='GET',
        path='/edr/groups/{group_id}'.format(group_id='group_id_example'),
        headers=headers,
        params=params,
        )
    assert response.status == 200, 'Response body is : ' + (await response.read()).decode('utf-8')


async def test_list_collections(client):
    """Test case for list_collections

    List the avialable collections from the service
    """
    params = [('bbox', openapi_server.OneOfobjectobject()),
                    ('datetime', 'datetime_example'),
                    ('f', 'f_example')]
    headers = { 
        'Accept': 'application/json',
    }
    response = await client.request(
        method='GET',
        path='/edr/collections',
        headers=headers,
        params=params,
        )
    assert response.status == 200, 'Response body is : ' + (await response.read()).decode('utf-8')


async def test_list_groups(client):
    """Test case for list_groups

    Provide a list of avialable data groups
    """
    params = [('f', 'f_example')]
    headers = { 
        'Accept': 'application/json',
    }
    response = await client.request(
        method='GET',
        path='/edr/groups',
        headers=headers,
        params=params,
        )
    assert response.status == 200, 'Response body is : ' + (await response.read()).decode('utf-8')

