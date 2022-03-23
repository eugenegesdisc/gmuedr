# coding: utf-8

import pytest

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
