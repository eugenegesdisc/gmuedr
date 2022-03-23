# coding: utf-8

from datetime import date, datetime

from typing import List, Dict, Type

from openapi_server.models.base_model_ import Model
from openapi_server import util


class LandingPageProvider(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, name: str=None, url: str=None):
        """LandingPageProvider - a model defined in OpenAPI

        :param name: The name of this LandingPageProvider.
        :param url: The url of this LandingPageProvider.
        """
        self.openapi_types = {
            'name': str,
            'url': str
        }

        self.attribute_map = {
            'name': 'name',
            'url': 'url'
        }

        self._name = name
        self._url = url

    @classmethod
    def from_dict(cls, dikt: dict) -> 'LandingPageProvider':
        """Returns the dict as a model

        :param dikt: A dict.
        :return: The landingPage_provider of this LandingPageProvider.
        """
        return util.deserialize_model(dikt, cls)

    @property
    def name(self):
        """Gets the name of this LandingPageProvider.

        Name of organization providing the service

        :return: The name of this LandingPageProvider.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this LandingPageProvider.

        Name of organization providing the service

        :param name: The name of this LandingPageProvider.
        :type name: str
        """

        self._name = name

    @property
    def url(self):
        """Gets the url of this LandingPageProvider.

        Link to service providers website

        :return: The url of this LandingPageProvider.
        :rtype: str
        """
        return self._url

    @url.setter
    def url(self, url):
        """Sets the url of this LandingPageProvider.

        Link to service providers website

        :param url: The url of this LandingPageProvider.
        :type url: str
        """

        self._url = url