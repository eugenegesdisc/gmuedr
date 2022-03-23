# coding: utf-8

from datetime import date, datetime

from typing import List, Dict, Type

from openapi_server.models.base_model_ import Model
from openapi_server.models.collection import Collection
from openapi_server.models.link import Link
from openapi_server import util


class Instances(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, links: List[Link]=None, instances: List[Collection]=None):
        """Instances - a model defined in OpenAPI

        :param links: The links of this Instances.
        :param instances: The instances of this Instances.
        """
        self.openapi_types = {
            'links': List[Link],
            'instances': List[Collection]
        }

        self.attribute_map = {
            'links': 'links',
            'instances': 'instances'
        }

        self._links = links
        self._instances = instances

    @classmethod
    def from_dict(cls, dikt: dict) -> 'Instances':
        """Returns the dict as a model

        :param dikt: A dict.
        :return: The instances of this Instances.
        """
        return util.deserialize_model(dikt, cls)

    @property
    def links(self):
        """Gets the links of this Instances.


        :return: The links of this Instances.
        :rtype: List[Link]
        """
        return self._links

    @links.setter
    def links(self, links):
        """Sets the links of this Instances.


        :param links: The links of this Instances.
        :type links: List[Link]
        """
        if links is None:
            raise ValueError("Invalid value for `links`, must not be `None`")

        self._links = links

    @property
    def instances(self):
        """Gets the instances of this Instances.


        :return: The instances of this Instances.
        :rtype: List[Collection]
        """
        return self._instances

    @instances.setter
    def instances(self, instances):
        """Sets the instances of this Instances.


        :param instances: The instances of this Instances.
        :type instances: List[Collection]
        """
        if instances is None:
            raise ValueError("Invalid value for `instances`, must not be `None`")

        self._instances = instances