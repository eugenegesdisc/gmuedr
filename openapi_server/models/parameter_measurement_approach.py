# coding: utf-8

from datetime import date, datetime

from typing import List, Dict, Type

from openapi_server.models.base_model_ import Model
from openapi_server import util


class ParameterMeasurementApproach(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, method: str=None, duration: str=None):
        """ParameterMeasurementApproach - a model defined in OpenAPI

        :param method: The method of this ParameterMeasurementApproach.
        :param duration: The duration of this ParameterMeasurementApproach.
        """
        self.openapi_types = {
            'method': str,
            'duration': str
        }

        self.attribute_map = {
            'method': 'method',
            'duration': 'duration'
        }

        self._method = method
        self._duration = duration

    @classmethod
    def from_dict(cls, dikt: dict) -> 'ParameterMeasurementApproach':
        """Returns the dict as a model

        :param dikt: A dict.
        :return: The Parameter_measurement_approach of this ParameterMeasurementApproach.
        """
        return util.deserialize_model(dikt, cls)

    @property
    def method(self):
        """Gets the method of this ParameterMeasurementApproach.


        :return: The method of this ParameterMeasurementApproach.
        :rtype: str
        """
        return self._method

    @method.setter
    def method(self, method):
        """Sets the method of this ParameterMeasurementApproach.


        :param method: The method of this ParameterMeasurementApproach.
        :type method: str
        """
        if method is None:
            raise ValueError("Invalid value for `method`, must not be `None`")

        self._method = method

    @property
    def duration(self):
        """Gets the duration of this ParameterMeasurementApproach.

        The time duration that the value was calculated for as an RFC3339 duration value.  If the method value is instantaneous this value is not required.

        :return: The duration of this ParameterMeasurementApproach.
        :rtype: str
        """
        return self._duration

    @duration.setter
    def duration(self, duration):
        """Sets the duration of this ParameterMeasurementApproach.

        The time duration that the value was calculated for as an RFC3339 duration value.  If the method value is instantaneous this value is not required.

        :param duration: The duration of this ParameterMeasurementApproach.
        :type duration: str
        """

        self._duration = duration
