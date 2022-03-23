# coding: utf-8

from datetime import date, datetime

from typing import List, Dict, Type

from openapi_server.models.base_model_ import Model
from openapi_server.models.collection import Collection
from openapi_server.models.link import Link
from openapi_server import util


class Collections(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, links: List[Link]=None, collections: List[Collection]=None):
        """Collections - a model defined in OpenAPI

        :param links: The links of this Collections.
        :param collections: The collections of this Collections.
        """
        self.openapi_types = {
            'links': List[Link],
            'collections': List[Collection]
        }

        self.attribute_map = {
            'links': 'links',
            'collections': 'collections'
        }

        self._links = links
        self._collections = collections

    @classmethod
    def from_dict(cls, dikt: dict) -> 'Collections':
        """Returns the dict as a model

        :param dikt: A dict.
        :return: The collections of this Collections.
        """
        return util.deserialize_model(dikt, cls)

    @property
    def links(self):
        """Gets the links of this Collections.


        :return: The links of this Collections.
        :rtype: List[Link]
        """
        return self._links

    @links.setter
    def links(self, links):
        """Sets the links of this Collections.


        :param links: The links of this Collections.
        :type links: List[Link]
        """
        if links is None:
            raise ValueError("Invalid value for `links`, must not be `None`")

        self._links = links

    @property
    def collections(self):
        """Gets the collections of this Collections.


        :return: The collections of this Collections.
        :rtype: List[Collection]
        """
        return self._collections

    @collections.setter
    def collections(self, collections):
        """Sets the collections of this Collections.


        :param collections: The collections of this Collections.
        :type collections: List[Collection]
        """
        if collections is None:
            raise ValueError("Invalid value for `collections`, must not be `None`")

        self._collections = collections