# coding: utf-8

from datetime import date, datetime

from typing import List, Dict, Type

from openapi_server.models.base_model_ import Model
from openapi_server import util


class MultilinestringGeoJSON(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, type: str=None, coordinates: List[List[List[float]]]=None):
        """MultilinestringGeoJSON - a model defined in OpenAPI

        :param type: The type of this MultilinestringGeoJSON.
        :param coordinates: The coordinates of this MultilinestringGeoJSON.
        """
        self.openapi_types = {
            'type': str,
            'coordinates': List[List[List[float]]]
        }

        self.attribute_map = {
            'type': 'type',
            'coordinates': 'coordinates'
        }

        self._type = type
        self._coordinates = coordinates

    @classmethod
    def from_dict(cls, dikt: dict) -> 'MultilinestringGeoJSON':
        """Returns the dict as a model

        :param dikt: A dict.
        :return: The multilinestringGeoJSON of this MultilinestringGeoJSON.
        """
        return util.deserialize_model(dikt, cls)

    @property
    def type(self):
        """Gets the type of this MultilinestringGeoJSON.


        :return: The type of this MultilinestringGeoJSON.
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, type):
        """Sets the type of this MultilinestringGeoJSON.


        :param type: The type of this MultilinestringGeoJSON.
        :type type: str
        """
        allowed_values = ["MultiLineString"]  # noqa: E501
        if type not in allowed_values:
            raise ValueError(
                "Invalid value for `type` ({0}), must be one of {1}"
                .format(type, allowed_values)
            )

        self._type = type

    @property
    def coordinates(self):
        """Gets the coordinates of this MultilinestringGeoJSON.


        :return: The coordinates of this MultilinestringGeoJSON.
        :rtype: List[List[List[float]]]
        """
        return self._coordinates

    @coordinates.setter
    def coordinates(self, coordinates):
        """Sets the coordinates of this MultilinestringGeoJSON.


        :param coordinates: The coordinates of this MultilinestringGeoJSON.
        :type coordinates: List[List[List[float]]]
        """
        if coordinates is None:
            raise ValueError("Invalid value for `coordinates`, must not be `None`")

        self._coordinates = coordinates
