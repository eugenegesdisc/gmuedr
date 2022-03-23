# coding: utf-8

from datetime import date, datetime

from typing import List, Dict, Type

from openapi_server.models.base_model_ import Model
from openapi_server.models.collection_data_queries import CollectionDataQueries
from openapi_server.models.extent import Extent
from openapi_server.models.link import Link
from openapi_server import util


class Collection(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, links: List[Link]=None, id: str=None, title: str=None, description: str=None, keywords: List[str]=None, extent: Extent=None, data_queries: CollectionDataQueries=None, crs: List[str]=None, output_formats: List[str]=None, parameter_names: Dict[str, object]=None):
        """Collection - a model defined in OpenAPI

        :param links: The links of this Collection.
        :param id: The id of this Collection.
        :param title: The title of this Collection.
        :param description: The description of this Collection.
        :param keywords: The keywords of this Collection.
        :param extent: The extent of this Collection.
        :param data_queries: The data_queries of this Collection.
        :param crs: The crs of this Collection.
        :param output_formats: The output_formats of this Collection.
        :param parameter_names: The parameter_names of this Collection.
        """
        self.openapi_types = {
            'links': List[Link],
            'id': str,
            'title': str,
            'description': str,
            'keywords': List[str],
            'extent': Extent,
            'data_queries': CollectionDataQueries,
            'crs': List[str],
            'output_formats': List[str],
            'parameter_names': Dict[str, object]
        }

        self.attribute_map = {
            'links': 'links',
            'id': 'id',
            'title': 'title',
            'description': 'description',
            'keywords': 'keywords',
            'extent': 'extent',
            'data_queries': 'data_queries',
            'crs': 'crs',
            'output_formats': 'output_formats',
            'parameter_names': 'parameter_names'
        }

        self._links = links
        self._id = id
        self._title = title
        self._description = description
        self._keywords = keywords
        self._extent = extent
        self._data_queries = data_queries
        self._crs = crs
        self._output_formats = output_formats
        self._parameter_names = parameter_names

    @classmethod
    def from_dict(cls, dikt: dict) -> 'Collection':
        """Returns the dict as a model

        :param dikt: A dict.
        :return: The collection of this Collection.
        """
        return util.deserialize_model(dikt, cls)

    @property
    def links(self):
        """Gets the links of this Collection.


        :return: The links of this Collection.
        :rtype: List[Link]
        """
        return self._links

    @links.setter
    def links(self, links):
        """Sets the links of this Collection.


        :param links: The links of this Collection.
        :type links: List[Link]
        """
        if links is None:
            raise ValueError("Invalid value for `links`, must not be `None`")

        self._links = links

    @property
    def id(self):
        """Gets the id of this Collection.

        id of the collection

        :return: The id of this Collection.
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this Collection.

        id of the collection

        :param id: The id of this Collection.
        :type id: str
        """
        if id is None:
            raise ValueError("Invalid value for `id`, must not be `None`")

        self._id = id

    @property
    def title(self):
        """Gets the title of this Collection.

        title of the collection

        :return: The title of this Collection.
        :rtype: str
        """
        return self._title

    @title.setter
    def title(self, title):
        """Sets the title of this Collection.

        title of the collection

        :param title: The title of this Collection.
        :type title: str
        """

        self._title = title

    @property
    def description(self):
        """Gets the description of this Collection.

        description of the collection

        :return: The description of this Collection.
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """Sets the description of this Collection.

        description of the collection

        :param description: The description of this Collection.
        :type description: str
        """

        self._description = description

    @property
    def keywords(self):
        """Gets the keywords of this Collection.

        List of keywords which help to describe the collection

        :return: The keywords of this Collection.
        :rtype: List[str]
        """
        return self._keywords

    @keywords.setter
    def keywords(self, keywords):
        """Sets the keywords of this Collection.

        List of keywords which help to describe the collection

        :param keywords: The keywords of this Collection.
        :type keywords: List[str]
        """

        self._keywords = keywords

    @property
    def extent(self):
        """Gets the extent of this Collection.


        :return: The extent of this Collection.
        :rtype: Extent
        """
        return self._extent

    @extent.setter
    def extent(self, extent):
        """Sets the extent of this Collection.


        :param extent: The extent of this Collection.
        :type extent: Extent
        """
        if extent is None:
            raise ValueError("Invalid value for `extent`, must not be `None`")

        self._extent = extent

    @property
    def data_queries(self):
        """Gets the data_queries of this Collection.


        :return: The data_queries of this Collection.
        :rtype: CollectionDataQueries
        """
        return self._data_queries

    @data_queries.setter
    def data_queries(self, data_queries):
        """Sets the data_queries of this Collection.


        :param data_queries: The data_queries of this Collection.
        :type data_queries: CollectionDataQueries
        """

        self._data_queries = data_queries

    @property
    def crs(self):
        """Gets the crs of this Collection.

        list of the coordinate reference systems the collection results can support

        :return: The crs of this Collection.
        :rtype: List[str]
        """
        return self._crs

    @crs.setter
    def crs(self, crs):
        """Sets the crs of this Collection.

        list of the coordinate reference systems the collection results can support

        :param crs: The crs of this Collection.
        :type crs: List[str]
        """

        self._crs = crs

    @property
    def output_formats(self):
        """Gets the output_formats of this Collection.

        list of formats the results can be presented in

        :return: The output_formats of this Collection.
        :rtype: List[str]
        """
        return self._output_formats

    @output_formats.setter
    def output_formats(self, output_formats):
        """Sets the output_formats of this Collection.

        list of formats the results can be presented in

        :param output_formats: The output_formats of this Collection.
        :type output_formats: List[str]
        """

        self._output_formats = output_formats

    @property
    def parameter_names(self):
        """Gets the parameter_names of this Collection.

        list of the data parameters available in the collection

        :return: The parameter_names of this Collection.
        :rtype: Dict[str, object]
        """
        return self._parameter_names

    @parameter_names.setter
    def parameter_names(self, parameter_names):
        """Sets the parameter_names of this Collection.

        list of the data parameters available in the collection

        :param parameter_names: The parameter_names of this Collection.
        :type parameter_names: Dict[str, object]
        """

        self._parameter_names = parameter_names
