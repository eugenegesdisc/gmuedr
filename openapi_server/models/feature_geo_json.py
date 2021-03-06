# coding: utf-8

from datetime import date, datetime

from typing import List, Dict, Type

from openapi_server.models.base_model_ import Model
from openapi_server.models.edr_properties import EdrProperties
from openapi_server.models.geometrycollection_geo_json import GeometrycollectionGeoJSON
from openapi_server.models.linestring_geo_json import LinestringGeoJSON
from openapi_server.models.link import Link
from openapi_server.models.multilinestring_geo_json import MultilinestringGeoJSON
from openapi_server.models.multipoint_geo_json import MultipointGeoJSON
from openapi_server.models.multipolygon_geo_json import MultipolygonGeoJSON
from openapi_server.models.point_geo_json import PointGeoJSON
from openapi_server.models.polygon_geo_json import PolygonGeoJSON
from openapi_server import util

from openapi_server.models.one_ofpoint_geo_jso_nmultipoint_geo_jso_nlinestring_geo_jso_nmultilinestring_geo_jso_npolygon_geo_jso_nmultipolygon_geo_jso_ngeometrycollection_geo_json import OneOfpointGeoJSONmultipointGeoJSONlinestringGeoJSONmultilinestringGeoJSONpolygonGeoJSONmultipolygonGeoJSONgeometrycollectionGeoJSON
from openapi_server.models.one_ofstringinteger import OneOfstringinteger


class FeatureGeoJSON(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, type: str = None, geometry: OneOfpointGeoJSONmultipointGeoJSONlinestringGeoJSONmultilinestringGeoJSONpolygonGeoJSONmultipolygonGeoJSONgeometrycollectionGeoJSON = None, properties: EdrProperties = None, id: OneOfstringinteger = None, links: List[Link] = None):
        """FeatureGeoJSON - a model defined in OpenAPI

        :param type: The type of this FeatureGeoJSON.
        :param geometry: The geometry of this FeatureGeoJSON.
        :param properties: The properties of this FeatureGeoJSON.
        :param id: The id of this FeatureGeoJSON.
        :param links: The links of this FeatureGeoJSON.
        """
        self.openapi_types = {
            'type': str,
            'geometry': OneOfpointGeoJSONmultipointGeoJSONlinestringGeoJSONmultilinestringGeoJSONpolygonGeoJSONmultipolygonGeoJSONgeometrycollectionGeoJSON,
            'properties': EdrProperties,
            'id': OneOfstringinteger,
            'links': List[Link]
        }

        self.attribute_map = {
            'type': 'type',
            'geometry': 'geometry',
            'properties': 'properties',
            'id': 'id',
            'links': 'links'
        }

        self._type = type
        self._geometry = geometry
        self._properties = properties
        self._id = id
        self._links = links

    @classmethod
    def from_dict(cls, dikt: dict) -> 'FeatureGeoJSON':
        """Returns the dict as a model

        :param dikt: A dict.
        :return: The featureGeoJSON of this FeatureGeoJSON.
        """
        return util.deserialize_model(dikt, cls)

    @property
    def type(self):
        """Gets the type of this FeatureGeoJSON.


        :return: The type of this FeatureGeoJSON.
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, type):
        """Sets the type of this FeatureGeoJSON.


        :param type: The type of this FeatureGeoJSON.
        :type type: str
        """
        allowed_values = ["Feature"]  # noqa: E501
        if type not in allowed_values:
            raise ValueError(
                "Invalid value for `type` ({0}), must be one of {1}"
                .format(type, allowed_values)
            )

        self._type = type

    @property
    def geometry(self):
        """Gets the geometry of this FeatureGeoJSON.


        :return: The geometry of this FeatureGeoJSON.
        :rtype: OneOfpointGeoJSONmultipointGeoJSONlinestringGeoJSONmultilinestringGeoJSONpolygonGeoJSONmultipolygonGeoJSONgeometrycollectionGeoJSON
        """
        return self._geometry

    @geometry.setter
    def geometry(self, geometry):
        """Sets the geometry of this FeatureGeoJSON.


        :param geometry: The geometry of this FeatureGeoJSON.
        :type geometry: OneOfpointGeoJSONmultipointGeoJSONlinestringGeoJSONmultilinestringGeoJSONpolygonGeoJSONmultipolygonGeoJSONgeometrycollectionGeoJSON
        """
        if geometry is None:
            raise ValueError(
                "Invalid value for `geometry`, must not be `None`")

        self._geometry = geometry

    @property
    def properties(self):
        """Gets the properties of this FeatureGeoJSON.


        :return: The properties of this FeatureGeoJSON.
        :rtype: EdrProperties
        """
        return self._properties

    @properties.setter
    def properties(self, properties):
        """Sets the properties of this FeatureGeoJSON.


        :param properties: The properties of this FeatureGeoJSON.
        :type properties: EdrProperties
        """
        if properties is None:
            raise ValueError(
                "Invalid value for `properties`, must not be `None`")

        self._properties = properties

    @property
    def id(self):
        """Gets the id of this FeatureGeoJSON.


        :return: The id of this FeatureGeoJSON.
        :rtype: OneOfstringinteger
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this FeatureGeoJSON.


        :param id: The id of this FeatureGeoJSON.
        :type id: OneOfstringinteger
        """

        self._id = id

    @property
    def links(self):
        """Gets the links of this FeatureGeoJSON.


        :return: The links of this FeatureGeoJSON.
        :rtype: List[Link]
        """
        return self._links

    @links.setter
    def links(self, links):
        """Sets the links of this FeatureGeoJSON.


        :param links: The links of this FeatureGeoJSON.
        :type links: List[Link]
        """

        self._links = links
