# coding: utf-8

from datetime import date, datetime

from typing import List, Dict, Type

from openapi_server.models.base_model_ import Model
from openapi_server import util
from openapi_server.models.any_ofobjectobject import AnyOfobjectobject


class DomainDescription(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, type: object = None, domain_type: object = None, axes: AnyOfobjectobject = None, referencing: AnyOfobjectobject = None):
        """DomainDescription - a model defined in OpenAPI

        :param type: The type of this DomainDescription.
        :param domain_type: The domain_type of this DomainDescription.
        :param axes: The axes of this DomainDescription.
        """
        self.openapi_types = {
            'type': object,
            'domain_type': object,
            'axes': AnyOfobjectobject,
            'referencing': AnyOfobjectobject
        }

        self.attribute_map = {
            'type': 'type',
            'domain_type': 'domainType',
            'axes': 'axes',
            'referencing': "referencing"
        }

        self._type = type
        self._domain_type = domain_type
        self._axes = axes
        self._referencing = referencing

    @classmethod
    def from_dict(cls, dikt: dict) -> 'DomainDescription':
        """Returns the dict as a model

        :param dikt: A dict.
        :return: The Domain_description of this DomainDescription.
        """
        return util.deserialize_model(dikt, cls)

    @property
    def type(self):
        """Gets the type of this DomainDescription.

        Type

        :return: The type of this DomainDescription.
        :rtype: object
        """
        return self._type

    @type.setter
    def type(self, type):
        """Sets the type of this DomainDescription.

        Type

        :param type: The type of this DomainDescription.
        :type type: object
        """
        allowed_values = [Domain]  # noqa: E501
        if type not in allowed_values:
            raise ValueError(
                "Invalid value for `type` ({0}), must be one of {1}"
                .format(type, allowed_values)
            )

        self._type = type

    @property
    def domain_type(self):
        """Gets the domain_type of this DomainDescription.

        Domain type

        :return: The domain_type of this DomainDescription.
        :rtype: object
        """
        return self._domain_type

    @domain_type.setter
    def domain_type(self, domain_type):
        """Sets the domain_type of this DomainDescription.

        Domain type

        :param domain_type: The domain_type of this DomainDescription.
        :type domain_type: object
        """
        allowed_values = [Grid, Point, Trajectory, PointSeries, PolygonSeries, MultiPolygon, MultiPoint, VerticalProfile]  # noqa: E501
        if domain_type not in allowed_values:
            raise ValueError(
                "Invalid value for `domain_type` ({0}), must be one of {1}"
                .format(domain_type, allowed_values)
            )

        self._domain_type = domain_type

    @property
    def axes(self):
        """Gets the axes of this DomainDescription.

        Geotemporal dimension axes of the CoverageJSON domain

        :return: The axes of this DomainDescription.
        :rtype: AnyOfobjectobject
        """
        return self._axes

    @axes.setter
    def axes(self, axes):
        """Sets the axes of this DomainDescription.

        Geotemporal dimension axes of the CoverageJSON domain

        :param axes: The axes of this DomainDescription.
        :type axes: AnyOfobjectobject
        """
        if axes is None:
            raise ValueError("Invalid value for `axes`, must not be `None`")

        self._axes = axes

    @property
    def referencing(self):
        """Gets the referencing of this CoverageJSON.


        :return: The referencing of this CoverageJSON.
        :rtype: Dict[str, OneOfobjectobject]
        """
        return self._referencing

    @referencing.setter
    def referencing(self, referencing):
        """Sets the referencing of this CoverageJSON.


        :param referencing: The referencing of this CoverageJSON.
        :type referencing: Dict[str, OneOfobjectobject]
        """
        if referencing is None:
            raise ValueError(
                "Invalid value for `referencing`, must not be `None`")

        self._referencing = referencing
