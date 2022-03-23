# coding: utf-8

from datetime import date, datetime

from typing import List, Dict, Type

from openapi_server.models.base_model_ import Model
from openapi_server import util


class ExtentTemporal(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, interval: List[List[datetime]]=None, trs: str='http://www.opengis.net/def/uom/ISO-8601/0/Gregorian', name: str=None):
        """ExtentTemporal - a model defined in OpenAPI

        :param interval: The interval of this ExtentTemporal.
        :param trs: The trs of this ExtentTemporal.
        :param name: The name of this ExtentTemporal.
        """
        self.openapi_types = {
            'interval': List[List[datetime]],
            'trs': str,
            'name': str
        }

        self.attribute_map = {
            'interval': 'interval',
            'trs': 'trs',
            'name': 'name'
        }

        self._interval = interval
        self._trs = trs
        self._name = name

    @classmethod
    def from_dict(cls, dikt: dict) -> 'ExtentTemporal':
        """Returns the dict as a model

        :param dikt: A dict.
        :return: The extent_temporal of this ExtentTemporal.
        """
        return util.deserialize_model(dikt, cls)

    @property
    def interval(self):
        """Gets the interval of this ExtentTemporal.

        RFC3339 compliant Date and Time, either as a time range specified as start time / end time / interval (e.g. 2017-11-14T09:00Z/2017-11-14T21:00Z/PT3H) or a list of time values (e.g. 2017-11-14T09:00Z,2017-11-14T12:00Z,2017-11-14T15:00Z,2017-11-14T18:00Z,2017-11-14T21:00Z)

        :return: The interval of this ExtentTemporal.
        :rtype: List[List[datetime]]
        """
        return self._interval

    @interval.setter
    def interval(self, interval):
        """Sets the interval of this ExtentTemporal.

        RFC3339 compliant Date and Time, either as a time range specified as start time / end time / interval (e.g. 2017-11-14T09:00Z/2017-11-14T21:00Z/PT3H) or a list of time values (e.g. 2017-11-14T09:00Z,2017-11-14T12:00Z,2017-11-14T15:00Z,2017-11-14T18:00Z,2017-11-14T21:00Z)

        :param interval: The interval of this ExtentTemporal.
        :type interval: List[List[datetime]]
        """
        if interval is None:
            raise ValueError("Invalid value for `interval`, must not be `None`")
        if interval is not None and len(interval) < 1:
            raise ValueError("Invalid value for `interval`, number of items must be greater than or equal to `1`")

        self._interval = interval

    @property
    def trs(self):
        """Gets the trs of this ExtentTemporal.

        Coordinate reference system of the coordinates in the temporal extent (property `interval`). The default reference system is the Gregorian calendar. In the Core this is the only supported temporal coordinate reference system. Extensions may support additional temporal coordinate reference systems and add additional enum values.

        :return: The trs of this ExtentTemporal.
        :rtype: str
        """
        return self._trs

    @trs.setter
    def trs(self, trs):
        """Sets the trs of this ExtentTemporal.

        Coordinate reference system of the coordinates in the temporal extent (property `interval`). The default reference system is the Gregorian calendar. In the Core this is the only supported temporal coordinate reference system. Extensions may support additional temporal coordinate reference systems and add additional enum values.

        :param trs: The trs of this ExtentTemporal.
        :type trs: str
        """
        if trs is None:
            raise ValueError("Invalid value for `trs`, must not be `None`")

        self._trs = trs

    @property
    def name(self):
        """Gets the name of this ExtentTemporal.

        Name of the temporal coordinate reference system

        :return: The name of this ExtentTemporal.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this ExtentTemporal.

        Name of the temporal coordinate reference system

        :param name: The name of this ExtentTemporal.
        :type name: str
        """

        self._name = name
