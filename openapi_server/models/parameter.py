# coding: utf-8

from datetime import date, datetime

from typing import List, Dict, Type

from openapi_server.models.base_model_ import Model
from openapi_server.models.extent import Extent
from openapi_server.models.observed_property import ObservedProperty
from openapi_server.models.one_ofintegerarray import OneOfintegerarray
from openapi_server.models.parameter_measurement_approach import ParameterMeasurementApproach
from openapi_server.models.units import Units
from openapi_server import util


class Parameter(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, type: object=None, description: str=None, label: str=None, data_type: object=None, unit: Units=None, observed_property: ObservedProperty=None, category_encoding: Dict[str, OneOfintegerarray]=None, extent: Extent=None, id: str=None, measurement_type: ParameterMeasurementApproach=None):
        """Parameter - a model defined in OpenAPI

        :param type: The type of this Parameter.
        :param description: The description of this Parameter.
        :param label: The label of this Parameter.
        :param data_type: The data_type of this Parameter.
        :param unit: The unit of this Parameter.
        :param observed_property: The observed_property of this Parameter.
        :param category_encoding: The category_encoding of this Parameter.
        :param extent: The extent of this Parameter.
        :param id: The id of this Parameter.
        :param measurement_type: The measurement_type of this Parameter.
        """
        self.openapi_types = {
            'type': object,
            'description': str,
            'label': str,
            'data_type': object,
            'unit': Units,
            'observed_property': ObservedProperty,
            'category_encoding': Dict[str, OneOfintegerarray],
            'extent': Extent,
            'id': str,
            'measurement_type': ParameterMeasurementApproach
        }

        self.attribute_map = {
            'type': 'type',
            'description': 'description',
            'label': 'label',
            'data_type': 'data-type',
            'unit': 'unit',
            'observed_property': 'observedProperty',
            'category_encoding': 'categoryEncoding',
            'extent': 'extent',
            'id': 'id',
            'measurement_type': 'measurementType'
        }

        self._type = type
        self._description = description
        self._label = label
        self._data_type = data_type
        self._unit = unit
        self._observed_property = observed_property
        self._category_encoding = category_encoding
        self._extent = extent
        self._id = id
        self._measurement_type = measurement_type

    @classmethod
    def from_dict(cls, dikt: dict) -> 'Parameter':
        """Returns the dict as a model

        :param dikt: A dict.
        :return: The parameter of this Parameter.
        """
        return util.deserialize_model(dikt, cls)

    @property
    def type(self):
        """Gets the type of this Parameter.

        type

        :return: The type of this Parameter.
        :rtype: object
        """
        return self._type

    @type.setter
    def type(self, type):
        """Sets the type of this Parameter.

        type

        :param type: The type of this Parameter.
        :type type: object
        """
        allowed_values = [Parameter]  # noqa: E501
        if type not in allowed_values:
            raise ValueError(
                "Invalid value for `type` ({0}), must be one of {1}"
                .format(type, allowed_values)
            )

        self._type = type

    @property
    def description(self):
        """Gets the description of this Parameter.


        :return: The description of this Parameter.
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """Sets the description of this Parameter.


        :param description: The description of this Parameter.
        :type description: str
        """

        self._description = description

    @property
    def label(self):
        """Gets the label of this Parameter.


        :return: The label of this Parameter.
        :rtype: str
        """
        return self._label

    @label.setter
    def label(self, label):
        """Sets the label of this Parameter.


        :param label: The label of this Parameter.
        :type label: str
        """

        self._label = label

    @property
    def data_type(self):
        """Gets the data_type of this Parameter.

        Data type of returned parameter

        :return: The data_type of this Parameter.
        :rtype: object
        """
        return self._data_type

    @data_type.setter
    def data_type(self, data_type):
        """Sets the data_type of this Parameter.

        Data type of returned parameter

        :param data_type: The data_type of this Parameter.
        :type data_type: object
        """
        allowed_values = [integer, float, string]  # noqa: E501
        if data_type not in allowed_values:
            raise ValueError(
                "Invalid value for `data_type` ({0}), must be one of {1}"
                .format(data_type, allowed_values)
            )

        self._data_type = data_type

    @property
    def unit(self):
        """Gets the unit of this Parameter.


        :return: The unit of this Parameter.
        :rtype: Units
        """
        return self._unit

    @unit.setter
    def unit(self, unit):
        """Sets the unit of this Parameter.


        :param unit: The unit of this Parameter.
        :type unit: Units
        """

        self._unit = unit

    @property
    def observed_property(self):
        """Gets the observed_property of this Parameter.


        :return: The observed_property of this Parameter.
        :rtype: ObservedProperty
        """
        return self._observed_property

    @observed_property.setter
    def observed_property(self, observed_property):
        """Sets the observed_property of this Parameter.


        :param observed_property: The observed_property of this Parameter.
        :type observed_property: ObservedProperty
        """
        if observed_property is None:
            raise ValueError("Invalid value for `observed_property`, must not be `None`")

        self._observed_property = observed_property

    @property
    def category_encoding(self):
        """Gets the category_encoding of this Parameter.


        :return: The category_encoding of this Parameter.
        :rtype: Dict[str, OneOfintegerarray]
        """
        return self._category_encoding

    @category_encoding.setter
    def category_encoding(self, category_encoding):
        """Sets the category_encoding of this Parameter.


        :param category_encoding: The category_encoding of this Parameter.
        :type category_encoding: Dict[str, OneOfintegerarray]
        """

        self._category_encoding = category_encoding

    @property
    def extent(self):
        """Gets the extent of this Parameter.


        :return: The extent of this Parameter.
        :rtype: Extent
        """
        return self._extent

    @extent.setter
    def extent(self, extent):
        """Sets the extent of this Parameter.


        :param extent: The extent of this Parameter.
        :type extent: Extent
        """

        self._extent = extent

    @property
    def id(self):
        """Gets the id of this Parameter.

        Unique ID of the parameter, this is the value used for querying the data

        :return: The id of this Parameter.
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this Parameter.

        Unique ID of the parameter, this is the value used for querying the data

        :param id: The id of this Parameter.
        :type id: str
        """

        self._id = id

    @property
    def measurement_type(self):
        """Gets the measurement_type of this Parameter.


        :return: The measurement_type of this Parameter.
        :rtype: ParameterMeasurementApproach
        """
        return self._measurement_type

    @measurement_type.setter
    def measurement_type(self, measurement_type):
        """Sets the measurement_type of this Parameter.


        :param measurement_type: The measurement_type of this Parameter.
        :type measurement_type: ParameterMeasurementApproach
        """

        self._measurement_type = measurement_type