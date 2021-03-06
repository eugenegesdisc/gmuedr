# coding: utf-8

from datetime import date, datetime

from typing import List, Dict, Type

from openapi_server.models.base_model_ import Model
from openapi_server.models.data_query import DataQuery
from openapi_server import util


class Link(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, href: str=None, rel: str=None, type: str=None, hreflang: str=None, title: str=None, length: int=None, templated: bool=None, variables: DataQuery=None):
        """Link - a model defined in OpenAPI

        :param href: The href of this Link.
        :param rel: The rel of this Link.
        :param type: The type of this Link.
        :param hreflang: The hreflang of this Link.
        :param title: The title of this Link.
        :param length: The length of this Link.
        :param templated: The templated of this Link.
        :param variables: The variables of this Link.
        """
        self.openapi_types = {
            'href': str,
            'rel': str,
            'type': str,
            'hreflang': str,
            'title': str,
            'length': int,
            'templated': bool,
            'variables': DataQuery
        }

        self.attribute_map = {
            'href': 'href',
            'rel': 'rel',
            'type': 'type',
            'hreflang': 'hreflang',
            'title': 'title',
            'length': 'length',
            'templated': 'templated',
            'variables': 'variables'
        }

        self._href = href
        self._rel = rel
        self._type = type
        self._hreflang = hreflang
        self._title = title
        self._length = length
        self._templated = templated
        self._variables = variables

    @classmethod
    def from_dict(cls, dikt: dict) -> 'Link':
        """Returns the dict as a model

        :param dikt: A dict.
        :return: The link of this Link.
        """
        return util.deserialize_model(dikt, cls)

    @property
    def href(self):
        """Gets the href of this Link.


        :return: The href of this Link.
        :rtype: str
        """
        return self._href

    @href.setter
    def href(self, href):
        """Sets the href of this Link.


        :param href: The href of this Link.
        :type href: str
        """
        if href is None:
            raise ValueError("Invalid value for `href`, must not be `None`")

        self._href = href

    @property
    def rel(self):
        """Gets the rel of this Link.


        :return: The rel of this Link.
        :rtype: str
        """
        return self._rel

    @rel.setter
    def rel(self, rel):
        """Sets the rel of this Link.


        :param rel: The rel of this Link.
        :type rel: str
        """
        if rel is None:
            raise ValueError("Invalid value for `rel`, must not be `None`")

        self._rel = rel

    @property
    def type(self):
        """Gets the type of this Link.


        :return: The type of this Link.
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, type):
        """Sets the type of this Link.


        :param type: The type of this Link.
        :type type: str
        """

        self._type = type

    @property
    def hreflang(self):
        """Gets the hreflang of this Link.


        :return: The hreflang of this Link.
        :rtype: str
        """
        return self._hreflang

    @hreflang.setter
    def hreflang(self, hreflang):
        """Sets the hreflang of this Link.


        :param hreflang: The hreflang of this Link.
        :type hreflang: str
        """

        self._hreflang = hreflang

    @property
    def title(self):
        """Gets the title of this Link.


        :return: The title of this Link.
        :rtype: str
        """
        return self._title

    @title.setter
    def title(self, title):
        """Sets the title of this Link.


        :param title: The title of this Link.
        :type title: str
        """

        self._title = title

    @property
    def length(self):
        """Gets the length of this Link.


        :return: The length of this Link.
        :rtype: int
        """
        return self._length

    @length.setter
    def length(self, length):
        """Sets the length of this Link.


        :param length: The length of this Link.
        :type length: int
        """

        self._length = length

    @property
    def templated(self):
        """Gets the templated of this Link.

        defines if the link href value is a template with values requiring replacement

        :return: The templated of this Link.
        :rtype: bool
        """
        return self._templated

    @templated.setter
    def templated(self, templated):
        """Sets the templated of this Link.

        defines if the link href value is a template with values requiring replacement

        :param templated: The templated of this Link.
        :type templated: bool
        """

        self._templated = templated

    @property
    def variables(self):
        """Gets the variables of this Link.


        :return: The variables of this Link.
        :rtype: DataQuery
        """
        return self._variables

    @variables.setter
    def variables(self, variables):
        """Sets the variables of this Link.


        :param variables: The variables of this Link.
        :type variables: DataQuery
        """

        self._variables = variables
