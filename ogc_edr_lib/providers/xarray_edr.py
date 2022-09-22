import shapely
import geopandas
import pyproj
from astropy import units as ast_units
import tempfile
import xarray as xr
import logging
import numpy as np
import cftime
import json
import os
import re
from ogc_edr_lib.util import ogrutil
from ogc_edr_lib.util import geopandas_util as gutil
from astropy.utils.misc import JsonCustomEncoder
from ogc_edr_lib.providers.base import BaseProvider
from ogc_edr_lib.ogc_api_config import OgcApiConfig
from ogc_edr_lib.l10n import LocaleTranslator
from openapi_server.models.edr_feature_collection_geo_json import (
    EdrFeatureCollectionGeoJSON
)
from openapi_server.models.feature_geo_json import (
    FeatureGeoJSON
)
from openapi_server.models.point_geo_json import (
    PointGeoJSON
)
from openapi_server.models.polygon_geo_json import (
    PolygonGeoJSON
)
from openapi_server.models.multipolygon_geo_json import (
    MultipolygonGeoJSON
)
from openapi_server.models.edr_properties import (
    EdrProperties
)
from openapi_server.models.link import (
    Link as edrLink
)
from openapi_server.models.coverage_json import (
    CoverageJSON
)
from openapi_server.models.domain_description import (
    DomainDescription
)
from openapi_server.models.parameter import (
    Parameter
)
from openapi_server.models.units import(
    Units
)
from openapi_server.models.observed_property import(
    ObservedProperty
)
Logger = logging.getLogger(__name__)


class XarrayEDRProvider(BaseProvider):
    """generic Formatter ABC"""
    type = "provider"
    category = "edr"
    supported_media_types = ["netcdf", "xarray"]

    def __init__(self, provider_def):
        """
        Initialize object

        :param provider_def: provider definition

        :returns: pygeoapi.formatter.base.BaseFormatter
        """
        super().__init__(provider_def)

    def get_data_for_location(
            self, collection_id, location_id,
            datetime=None, crs=None, f=None):
        """Query end point for queries of collection {collectionId}
         defined by a location id

        Return data the for the location defined by locationId

        :param collection_id: Identifier (id) of a specific collection
        :type collection_id: str
        :param location_id: Retreive data for the location defined by
         locationId (i.e. London_Heathrow, EGLL, 03772 etc)
        :type location_id: str
        :param datetime: Either a date-time or an interval, open or closed.
         Date and time expressions adhere to RFC 3339. Open intervals are
         expressed using double-dots. Examples:
          * A date-time: \&quot;2018-02-12T23:20:50Z\&quot;
          * A closed interval:
           \&quot;2018-02-12T00:00:00Z/2018-03-18T12:31:12Z\&quot;
          * Open intervals: \&quot;2018-02-12T00:00:00Z/..\&quot; or
           \&quot;../2018-03-18T12:31:12Z\&quot;
            Only features that have a temporal property that intersects the
            value of &#x60;datetime&#x60; are selected. If a feature has
            multiple temporal properties, it is the decision of the server
            whether only a single temporal property is used to determine the
            extent or all relevant temporal properties.
        :type datetime: str
        :param crs: identifier (id) of the coordinate system to return data
         in list of valid crs identifiers for the chosen collection are defined
         in the metadata responses.  If not supplied the coordinate reference
         system will default to WGS84.
        :type crs: str
        :param f: format to return the data response in
        :type f: str

        """
        ret_data = None
        try:
            thedata = self.provider_def["data"]
            if thedata.endswith(".zarr"):
                open_func = xr.open_zarr
            else:
                open_func = xr.open_dataset
            thedata = open_func(thedata)
            theproperties = self._get_coverage_properties2(thedata)
            # the_id_array = self._form_the_id(thedata)
            # thedata["id_user_"] = the_id_array
            theparams = self._parse_parameter_name(
                None, theproperties)
            # thedata = thedata.get(theparams)
            # thepolygon = ogrutil.get_polygon_from_wkt(coords)
            # may need to convert the crs...
            # print("thepolygon=", thepolygon)
            # native_crs = self._get_coverage_native_crs(thedata)
            the_coords = self._get_data_location_coords(location_id)
            the_xarray_data = gutil.rxr_clip(thedata, theparams, the_coords)

            # handling native format such as netcdf
            if f == "application/x-netcdf":
                with tempfile.TemporaryFile() as fp:
                    Logger.debug('Returning data in native NetCDF format')
                    fp.write(the_xarray_data.to_netcdf())
                    fp.seek(0)
                    return fp.read()

            theretdata = self._get_coverage_json_for_area(
                collection_id, the_xarray_data, theproperties,
                theparams)
            # ret_data = json.dumps(theretdata.to_dict(), cls=JsonCustomEncoder)
            ret_data = theretdata
        except Exception as err:
            Logger.warning(err)
            return None

        return ret_data

    def _get_data_location_coords(
            self, location_id):
        try:
            the_shape_file = self._get_location_shapefile()
            gdf = geopandas.read_file(the_shape_file)
            the_loc_id_field = self.provider_def.get("locid_field", None)
            if the_loc_id_field is None:
                the_loc_id_field = self._find_first_unique_column(gdf)
            the_loc = gdf[gdf[the_loc_id_field] == location_id]
            return the_loc["geometry"].values[0].wkt
        except Exception as ee:
            return None

    def list_collection_data_locations(
            self, collection_id, bbox=None,
            datetime=None, limit=None, offset=None, f=None):
        """List available location identifers for the collection

        List the locations available for the collection

        :param collection_id: Identifier (id) of a specific collection
        :type collection_id: str
        :param bbox: Only features that have a geometry that intersects the
         bounding box are selected. The bounding box is provided as four or six
         numbers, depending on whether the coordinate reference system includes
         a vertical axis (height or depth):
         * Lower left corner, coordinate axis 1
         * Lower left corner, coordinate axis 2
         * Minimum value, coordinate axis 3 (optional)
         * Upper right corner, coordinate axis 1
         * Upper right corner, coordinate axis 2
         * Maximum value, coordinate axis 3 (optional)
         The coordinate reference system of the values is specified by
         the &#x60;crs&#x60; query parameter. If the &#x60;crs&#x60;
         query parameter is not defined the coordinate reference system is
         defined by the default &#x60;crs&#x60;
         for the query type. If a default &#x60;crs&#x60;
         has not been defined the values will be assumed to be in the WGS 84
         longitude/latitude (http://www.opengis.net/def/crs/OGC/1.3/CRS84)
         coordinate reference system. For WGS 84 longitude/latitude the values
         are in most cases the sequence of minimum longitude, minimum latitude,
         maximum longitude and maximum latitude. However, in cases where the
         box spans the antimeridian the first value (west-most box edge) is
         larger than the third value (east-most box edge). If the vertical
         axis is included, the third and the sixth number are the bottom and
         the top of the 3-dimensional bounding box. If a feature has multiple
         spatial geometry properties, it is the decision of the server whether
         only a single spatial geometry property is used to determine the
         extent or all relevant geometries.
        :type bbox: dict | bytes
        :param datetime: Either a date-time or an interval, open or closed.
         Date and time expressions adhere to RFC 3339. Open intervals are
         expressed using double-dots. Examples:
         * A date-time: \&quot;2018-02-12T23:20:50Z\&quot;
         * A closed interval:
          \&quot;2018-02-12T00:00:00Z/2018-03-18T12:31:12Z\&quot;
         * Open intervals: \&quot;2018-02-12T00:00:00Z/..\&quot;
          or \&quot;../2018-03-18T12:31:12Z\&quot;
          Only features that have a temporal property that intersects the
          value of &#x60;datetime&#x60; are selected. If a feature has multiple
          temporal properties, it is the decision of the server whether only
          a single temporal property is used to determine the extent or all
          relevant temporal properties.
        :type datetime: str
        :param limit: The optional limit parameter limits the number of results
         that are presented in the response document. Minimum &#x3D; 1.
         Maximum &#x3D; 10000. Default &#x3D; 10.
        :type limit: int

        """
        ret_data = None
        try:
            thedata = self.provider_def["data"]
            if thedata.endswith(".zarr"):
                open_func = xr.open_zarr
            else:
                open_func = xr.open_dataset
            thedata = open_func(thedata)
            theproperties = self._get_coverage_properties2(thedata)
            # the_id_array = self._form_the_id(thedata)
            # thedata["id_user_"] = the_id_array
            # theparams = self._parse_parameter_name(
            #     parameter_name, theproperties)
            the_number_matched, the_number_returned, the_return_data = \
                self._get_collection_locations(
                    collection_id, bbox, offset, limit)
            theparams = self._parse_parameter_name(
                None, theproperties)
            # thedata = thedata.get(theparams)
            #  the_crs=self._parse_crs(crs)
            # handling native format such as netcdf
            the_ret_gjsona = self._gen_geojson_list_collection_data_locations(
                collection_id, theproperties,
                the_number_matched, the_number_returned, the_return_data)
            the_j_str = json.dumps(
                the_ret_gjsona.to_dict(), cls=JsonCustomEncoder)
            ret_data = the_j_str
        except Exception as err:
            Logger.warning(err)
            return None

        return ret_data

    # ----------------metadata--collections-locations----------------
    def _gen_geojson_list_collection_data_locations(
            self,  collection_id, theproperties,
            the_number_matched, the_number_returned,
            the_return_data):
        thefeatures = self._gen_geojson_features_list_collection_data_locations(
            collection_id, theproperties,
            the_number_matched, the_number_returned,
            the_return_data)
        # time_stamp =
        #    time_stamp=time_stamp,
        #    links=thelinks,
        #    parameters=theparameters,
        thegeojsoncollecion = EdrFeatureCollectionGeoJSON(
            type="FeatureCollection",
            features=thefeatures,
            number_matched=the_number_matched,
            number_returned=the_number_returned
        )
        return thegeojsoncollecion

    def _gen_geojson_features_list_collection_data_locations(
            self,  collection_id, theproperties,
            the_number_matched, the_number_returned, the_return_data):
        thefeatures = []
        if the_number_returned < 1:
            return thefeatures
        the_loc_id_field = self.provider_def.get("locid_field", None)
        if the_loc_id_field is None:
            the_loc_id_field = self._find_first_unique_column(the_return_data)
        the_title_field = self.provider_def.get(
            "title_field", the_loc_id_field)
        for index, row in the_return_data.iterrows():
            # id
            the_id = row[the_loc_id_field]
            # geometry
            the_s_geom = row["geometry"]
            thegeometry = self._gen_feature_geometry(the_s_geom)
            # properties
            fp_datetime = theproperties["time_range"]
            fp_label = None
            if the_title_field is not None:
                fp_label = row[the_title_field]
            fp_edrqendpoint = "/collections/{}/locations/{}".format(
                collection_id,
                the_id
            )
            fp_parameter_name = theproperties["fields"]
            thefproperties = EdrProperties(
                datetime=fp_datetime,
                label=fp_label,
                edrqueryendpoint=fp_edrqendpoint,
                parameter_name=fp_parameter_name
            )
            # links
            thelinks = []
            thehref = "/collections/{}/locations/{}?f=coveragejson".format(
                collection_id,
                the_id)
            thelink = edrLink(
                rel="data",
                href=thehref,
                type="application/prs.coverage+json",
                title=fp_label + " (coveragejson)"
            )
            thelinks.append(thelink)
            thehref = "/collections/{}/locations/{}?f=netcdf".format(
                collection_id,
                the_id)
            thelink = edrLink(
                rel="data",
                href=thehref,
                type="application/x-netcdf",
                title=fp_label + " (netcdf)"
            )
            thelinks.append(thelink)
            thefeature = FeatureGeoJSON(
                type="Feature",
                geometry=thegeometry,
                properties=thefproperties,
                id=the_id,
                links=thelinks
            )
            thefeatures.append(thefeature)
        return thefeatures

    def _find_first_unique_column(self, the_return_data):
        tn = len(the_return_data.columns)
        for r in range(tn):
            if np.unique(the_return_data[the_return_data.columns[r]]).size == len(
                    the_return_data[the_return_data.columns[r]]):
                return the_return_data.columns[r]
        return None

    def _gen_feature_geometry(self, the_s_geom):
        thegeometry = None
        the_coords = shapely.geometry.mapping(
            the_s_geom
        )["coordinates"]
        if isinstance(the_s_geom, shapely.geometry.multipolygon.MultiPolygon):
            thegeometry = MultipolygonGeoJSON(
                type="MultiPolygon",
                coordinates=the_coords
            )
        elif isinstance(the_s_geom, shapely.geometry.polygon.Polygon):
            thegeometry = PolygonGeoJSON(
                type="MultiPolygon",
                coordinates=the_coords
            )
        elif isinstance(the_s_geom, shapely.geometry.point.Point):
            thegeometry = PointGeoJSON(
                type="Point",
                coordinates=the_coords
            )
        return thegeometry

    def _get_collection_locations(
            self, collection_id, bbox, offset, limit):
        the_shape_file = self._get_location_shapefile()
        gdf = geopandas.read_file(
            the_shape_file,
            bbox=bbox,
        )
        the_number_matched = len(gdf)
        the_limit = self.provider_def.get("limitdefault", 10)
        the_max_limit = self.provider_def.get("limitmax", 1000)
        if limit is not None:
            if (limit > the_max_limit):
                the_limit = the_max_limit
            else:
                the_limit = limit
        the_offset = 0
        if offset is not None:
            if offset > 0:
                the_offset = offset
        the_number_returned = the_number_matched - the_offset
        if the_number_returned > 0:
            if the_number_returned > limit:
                the_number_returned = limit
            the_return_data = gdf[offset:]
        else:
            the_number_returned = 0
            the_return_data = None
        return the_number_matched, the_number_returned, the_return_data

    def _get_location_shapefile(self):
        the_ret_path = None
        try:
            the_ret_path = self.provider_def['loc_shapefile']
        except:
            the_ret_path = '{}{}..{}data{}country{}country.shp'.format(os.path.dirname(
                os.path.realpath(__file__)), os.sep, os.sep, os.sep, os.sep)
        return the_ret_path
    # ================metadata==collections-locations================

    def get_data_for_corridor(
            self, collection_id, coords, corridor_width,
            width_units, corridor_height, height_units, z=None, datetime=None,
            parameter_name=None, resolution_x=None, resolution_z=None,
            crs=None, f=None):
        """Query end point for Corridor queries  of collection
         {collectionId} defined by a polygon

        Return the data values for the Corridor defined by the query parameters

        :param collection_id: Identifier (id) of a specific collection
        :type collection_id: str
        :param coords: Only data that has a geometry that intersects the area
         defined by the linestring are selected.  The trajectory is defined
         using a Well Known Text string following
           A 2D trajectory, on the surface of earth with no time or height
            dimensions:
            coords&#x3D;LINESTRING(-2.87 51.14 , -2.98 51.36,-3.15 51.03 ,
            -3.48 50.74 ,-3.36 50.9 )
           A 2D trajectory, on the surface of earth with all for the same time
            and no height dimension, time value defined in ISO8601 format by
            the &#x60;datetime&#x60; query parameter :
            coords&#x3D;LINESTRING(-2.87 51.14 , -2.98 51.36 ,-3.15 51.03 ,
            -3.48 50.74 ,-3.36 50.9 )&amp;time&#x3D;2018-02-12T23:00:00Z
           A 2D trajectory, on the surface of earth with no time value but at
            a fixed height level, height defined in the collection height units
            by the &#x60;z&#x60; query parameter :
            coords&#x3D;LINESTRING(-2.87 51.14 , -2.98 51.36 ,-3.15 51.03 ,
            -3.48 50.74 ,-3.36 50.9 )&amp;z&#x3D;850
           A 2D trajectory, on the surface of earth with all for the same time
            and at a fixed height level, time value defined in ISO8601 format
            by the &#x60;datetime&#x60; query parameter and height defined in
            the collection height units by the &#x60;z&#x60; query parameter :
            coords&#x3D;LINESTRING(-2.87 51.14 , -2.98 51.36 ,-3.15 51.03 ,
            -3.48 50.74 ,-3.36 50.9 )
            &amp;time&#x3D;2018-02-12T23:00:00Z&amp;z&#x3D;850
           A 3D trajectory, on the surface of the earth but over a time range
            with no height values:
            coords&#x3D;LINESTRINGM(-2.87 51.14  1560507000,
            -2.98 51.36  1560507600,-3.15 51.03  1560508200,
            -3.48 50.74  1560508500,-3.36 50.9  1560510240)
           A 3D trajectory, on the surface of the earth but over a time range
            with a fixed height value, height defined in the collection height
            units by the &#x60;z&#x60; query parameter :
            coords&#x3D;LINESTRINGM(-2.87 51.14  1560507000,
            -2.98 51.36  1560507600,-3.15 51.03  1560508200,
            -3.48 50.74  1560508500,-3.36 50.9  1560510240)&amp;z&#x3D;200
           A 3D trajectory, through a 3D volume with height or depth, but no
            defined time: coords&#x3D;LINESTRINGZ(-2.87 51.14  0.1,
            -2.98 51.36  0.2,-3.15 51.03  0.3,-3.48 50.74  0.4,-3.36 50.9  0.5)
           A 3D trajectory, through a 3D volume with height or depth, but a
            fixed time time value defined in ISO8601 format by the
            &#x60;datetime&#x60; query parameter:
            coords&#x3D;LINESTRINGZ(-2.87 51.14  0.1,-2.98 51.36  0.2,
            -3.15 51.03  0.3,-3.48 50.74  0.4,
            -3.36 50.9  0.5)&amp;time&#x3D;2018-02-12T23:00:00Z
           A 4D trajectory, through a 3D volume but over a time range:
            oords&#x3D;LINESTRINGZM(-2.87 51.14 0.1 1560507000,
            -2.98 51.36 0.2 1560507600,
            -3.15 51.03 0.3 1560508200, -3.48 50.74 0.4 1560508500,
            -3.36 50.9 0.5 1560510240)
            (using either the &#x60;time&#x60; or &#x60;z&#x60;
            parameters with a 4D trajectory wil generate an error response)
            where Z in &#x60;LINESTRINGZ&#x60; and &#x60;LINESTRINGZM&#x60;
            refers to the height value. &#x60;If the specified CRS does not
            define the height units, the heights units will default to metres
            above mean sea level&#x60;  and the M in &#x60;LINESTRINGM&#x60;
            and &#x60;LINESTRINGZM&#x60; refers to the number of seconds that
            have elapsed since the Unix epoch, that is the time 00:00:00 UTC
            on 1 January 1970. See https://en.wikipedia.org/wiki/Unix_time
        :type coords: str
        :param corridor_width: width of the corridor  The width value
         represents the whole width of the corridor where the trajectory
         supplied in the &#x60;coords&#x60; query parameter is the centre
         point of the corridor  &#x60;corridor-width&#x3D;{width}&#x60;
         e.g.  corridor-width&#x3D;100  Would be a request for a corridor 100
         units wide with the coords parameter values being the centre point of
         the requested corridor, the request would be for data values 50 units
         either side of the trajectory coordinates defined in the coords
         parameter.  The width units supported by the collection will be
         provided in the API metadata responses
        :type corridor_width: str
        :param width_units: Distance units for the corridor-width parameter
        :type width_units: str
        :param corridor_height: height of the corridor  The height value
         represents the whole height of the corridor where the trajectory
         supplied in the &#x60;coords&#x60; query parameter is the centre
         point of the corridor  &#x60;corridor-height&#x3D;{height}&#x60;
         e.g.  corridor-height&#x3D;100  Would be a request for a corridor 100
         units high with the coords parameter values being the centre point of
         the requested corridor, the request would be for data values 50 units
         either side of the trajectory coordinates defined in the coords
         parameter.  The height units supported by the collection will be
         provided in the API metadata responses
        :type corridor_height: str
        :param height_units: Distance units for the corridor-height parameter
        :type height_units: str
        :param z: Define the vertical level to return data from i.e.
         z&#x3D;level  for instance if the 850hPa pressure level is being
         queried  z&#x3D;850  or a range to return data for all levels between
         and including 2 defined levels i.e. z&#x3D;minimum value/maximum value
         for instance if all values between and including 10m and 100m
         z&#x3D;10/100  finally a list of height values can be specified
         i.e. z&#x3D;value1,value2,value3  for instance if values at 2m, 10m
         and 80m are required  z&#x3D;2,10,80  An Arithmetic sequence using
         Recurring height intervals, the difference is the number of
         recurrences is defined at the start and the amount to increment the
         height by is defined at the end  i.e. z&#x3D;Rn/min height/height
         interval  so if the request was for 20 height levels 50m apart
         starting at 100m:  z&#x3D;R20/100/50  When not specified data from all
         available heights SHOULD be returned
        :type z: str
        :param datetime: Either a date-time or an interval, open or closed.
        Date and time expressions adhere to RFC 3339. Open intervals are
        expressed using double-dots. Examples:
         * A date-time: \&quot;2018-02-12T23:20:50Z\&quot;
         * A closed interval:
          \&quot;2018-02-12T00:00:00Z/2018-03-18T12:31:12Z\&quot;
         * Open intervals: \&quot;2018-02-12T00:00:00Z/..\&quot; or
          \&quot;../2018-03-18T12:31:12Z\&quot; Only features that have a
          temporal property that intersects the value of &#x60;datetime&#x60;
          are selected. If a feature has multiple temporal properties, it is
          the decision of the server whether only a single temporal property
          is used to determine the extent or all relevant temporal properties.
        :type datetime: str
        :param parameter_name: comma delimited list of parameters to retrieve
         data for.  Valid parameters are listed in the collections metadata
        :type parameter_name: str
        :param resolution_x: Defined it the user requires data at a different
         resolution from the native resolution of the data along the x-axis
         If this is a single value it denotes the number of intervals to
         retrieve data for along the x-axis    i.e. resolution-x&#x3D;10
         would retrieve 10 values along the x-axis from the minimum x
         coordinate to maximum x coordinate (i.e. a value at both the minimum x
         and maximum x coordinates and 8 values between).
        :type resolution_x: dict | bytes
        :param resolution_z: Defined it the user requires data at a different
         resolution from the native resolution of the data along the z-axis
         If this is a single value it denotes the number of intervals to
         retrieve data for along the z-axis    i.e. resolution-z&#x3D;10
         would retrieve 10 values along the z-axis from the minimum z
         coordinate to maximum z  coordinate (i.e. a value at both the minimum
         z and maximum z coordinates and 8 values between).
        :type resolution_z: dict | bytes
        :param crs: identifier (id) of the coordinate system to return data in
         list of valid crs identifiers for the chosen collection are defined in
         the metadata responses.  If not supplied the coordinate reference
         system will default to WGS84.
        :type crs: str
        :param f: format to return the data response in
        :type f: str

        """
        ret_data = None
        try:
            thedata = self.provider_def["data"]
            if thedata.endswith(".zarr"):
                open_func = xr.open_zarr
            else:
                open_func = xr.open_dataset
            thedata = open_func(thedata)
            theproperties = self._get_coverage_properties(thedata)
            # the_id_array = self._form_the_id(thedata)
            # thedata["id_user_"] = the_id_array
            theparams = self._parse_parameter_name(
                parameter_name, theproperties)
            thedata = thedata.get(theparams)
            the_crs = self._parse_crs(crs)
            the_c_width, the_cw_units = self._parse_within(
                corridor_width, width_units)
            the_grd_res = None
            thecorridor = gutil.create_corridor_lines_wkt(
                coords, the_crs, the_c_width, the_cw_units,
                the_grd_res)
            theretdata = self._get_xarray_dataset_for_corridor(
                collection_id, thecorridor, thedata, theproperties, theparams)
            # handling native format such as netcdf
            if f == "application/x-netcdf":
                return self._export_corridor_xarrays_to_netcdf(theretdata)
            the_ret_cov_json = self._get_coverage_json_for_corridor_from_xarrays(
                theretdata, theproperties, theparams)
            ret_data = the_ret_cov_json
        except Exception as err:
            Logger.warning(err)
            return None

        return ret_data

    def _export_corridor_xarrays_to_netcdf(
            self, xarrays):
        the_xarray = None  # to create the trajectory representation in xarray
        with tempfile.TemporaryFile() as fp:
            Logger.debug('Returning data in native NetCDF format')
            fp.write(the_xarray.to_netcdf())
            fp.seek(0)
            return fp.read()

    # ----------------coverage-json-corridor----------------

    def _get_coverage_json_for_corridor_from_xarrays(
            self, the_xarrays, theproperties, theparams):
        # handling native format such as netcdf
        the_ret_cov_json = self._gen_coverage_json_for_corridor_from_xarrays(
            the_xarrays,  theproperties, theparams
        )
        ret_data = json.dumps(
            the_ret_cov_json.to_dict(), cls=JsonCustomEncoder)
        return ret_data

    def _gen_coverage_json_for_corridor_from_xarrays(
            self, the_xarrays, theproperties, theparams):
        referencing = [
                        {
                            "coordinates": ["t"],
                            "system": {
                                "type": "TemporalRS",
                                "calendar": "Gregorian"
                            }
                        }, {
                            "coordinates": ["y", "x"],
                            "system": {
                                "type": "GeographicCRS",
                                "id": "http://www.opengis.net/def/crs/OGC/1.3/CRS84"
                            }
                        }
                    ]

        the_param_descriptions = self._get_parameter_descriptions(
            the_xarrays[0], theparams, theproperties)
        # the_ranges = self._get_coverage_json_ranges_from_trajectory(
        #    thedata, theparams, theproperties)
        the_coverages = self._get_coverage_json_corridor_coverages(
            the_xarrays, theparams, theproperties)
        thecovjson = CoverageJSON(
            type="CoverageCollection",
            domain_type="Trajectory",
            domain=None,
            parameters=the_param_descriptions,
            referencing=referencing,
            ranges=None,
            coverages=the_coverages)
        return thecovjson

    def _get_xarray_dataset_for_corridor(
            self, collection_id, thecorridor, data, properties, params):
        the_xarrays = []
        for k, g in enumerate(thecorridor.geometry):
            the_point_array = np.asarray(g.coords)
            target_lon = xr.DataArray(the_point_array[:, 0], dims="trajectory")
            target_lat = xr.DataArray(the_point_array[:, 1], dims="trajectory")
            the_s_data = data.sel(
                lon=target_lon, lat=target_lat, method="nearest")
            the_s_data.attrs["featureType"] = "trajectory"
            the_xarrays.append(the_s_data)
        return the_xarrays

    def _get_coverage_json_corridor_coverages(
            self, the_xarrays, theparams, theproperties):
        the_coverages = []
        for k, v in enumerate(the_xarrays):
            the_coverage = self._gen_coverage_json_corridor_trajectory(
                v, theparams, theproperties)
            the_coverages.append(the_coverage)
        return the_coverages

    def _gen_coverage_json_corridor_trajectory(
            self, thedata, theparams, theproperties):
        theaxes = {
            "composite": {
                "dataType": "tuple",
                "coordinates": ["t", "x", "y"],
                "values": self._get_composite_axes_from_trajectory(
                    thedata, theproperties
                )
            }
        }
        thedomaindesc = DomainDescription(
            type="Domain",
            domain_type=None,
            axes=theaxes
        )
        the_ranges = self._get_coverage_json_ranges_from_trajectory(
            thedata, theparams, theproperties)
        thecovjson = CoverageJSON(
            type="Coverage",
            domain=thedomaindesc,
            parameters=None,
            ranges=the_ranges)
        return thecovjson

    # ================coverage-json-corridor================

    def get_data_for_trajectory(
            self, collection_id, coords, z=None,
            datetime=None, parameter_name=None, crs=None, f=None):
        """Query end point for trajectory queries  of
         collection {collectionId} defined by a wkt linestring and a iso8601
         time period

        Return the data values for the data Polygon defined by the query
         parameters

        :param collection_id: Identifier (id) of a specific collection
        :type collection_id: str
        :param coords: Only data that has a geometry that intersects the area
         defined by the linestring are selected.  The trajectory is defined
         using a Well Known Text string following
           A 2D trajectory, on the surface of earth with no time or height
            dimensions:
            coords&#x3D;LINESTRING(-2.87 51.14 , -2.98 51.36,-3.15 51.03 ,
            -3.48 50.74 ,-3.36 50.9 )
           A 2D trajectory, on the surface of earth with all for the same time
            and no height dimension, time value defined in ISO8601 format by
            the &#x60;datetime&#x60; query parameter :
            coords&#x3D;LINESTRING(-2.87 51.14 , -2.98 51.36 ,-3.15 51.03 ,
            -3.48 50.74 ,-3.36 50.9 )&amp;time&#x3D;2018-02-12T23:00:00Z
           A 2D trajectory, on the surface of earth with no time value but at
            a fixed height level, height defined in the collection height units
            by the &#x60;z&#x60; query parameter :
            coords&#x3D;LINESTRING(-2.87 51.14 , -2.98 51.36 ,-3.15 51.03 ,
            -3.48 50.74 ,-3.36 50.9 )&amp;z&#x3D;850
           A 2D trajectory, on the surface of earth with all for the same time
            and at a fixed height level, time value defined in ISO8601 format
            by the &#x60;datetime&#x60; query parameter and height defined in
            the collection height units by the &#x60;z&#x60; query parameter :
            coords&#x3D;LINESTRING(-2.87 51.14 , -2.98 51.36 ,-3.15 51.03 ,
            -3.48 50.74 ,-3.36 50.9 )
            &amp;time&#x3D;2018-02-12T23:00:00Z&amp;z&#x3D;850
           A 3D trajectory, on the surface of the earth but over a time range
            with no height values:
            coords&#x3D;LINESTRINGM(-2.87 51.14  1560507000,
            -2.98 51.36  1560507600,-3.15 51.03  1560508200,
            -3.48 50.74  1560508500,-3.36 50.9  1560510240)
           A 3D trajectory, on the surface of the earth but over a time range
            with a fixed height value, height defined in the collection height
            units by the &#x60;z&#x60; query parameter :
            coords&#x3D;LINESTRINGM(-2.87 51.14  1560507000,
            -2.98 51.36  1560507600,-3.15 51.03  1560508200,
            -3.48 50.74  1560508500,-3.36 50.9  1560510240)&amp;z&#x3D;200
           A 3D trajectory, through a 3D volume with height or depth, but no
            defined time: coords&#x3D;LINESTRINGZ(-2.87 51.14  0.1,
            -2.98 51.36  0.2,-3.15 51.03  0.3,-3.48 50.74  0.4,-3.36 50.9  0.5)
           A 3D trajectory, through a 3D volume with height or depth, but a
            fixed time time value defined in ISO8601 format by the
            &#x60;datetime&#x60; query parameter:
            coords&#x3D;LINESTRINGZ(-2.87 51.14  0.1,-2.98 51.36  0.2,
            -3.15 51.03  0.3,-3.48 50.74  0.4,
            -3.36 50.9  0.5)&amp;time&#x3D;2018-02-12T23:00:00Z
           A 4D trajectory, through a 3D volume but over a time range:
            oords&#x3D;LINESTRINGZM(-2.87 51.14 0.1 1560507000,
            -2.98 51.36 0.2 1560507600,
            -3.15 51.03 0.3 1560508200, -3.48 50.74 0.4 1560508500,
            -3.36 50.9 0.5 1560510240)
            (using either the &#x60;time&#x60; or &#x60;z&#x60;
            parameters with a 4D trajectory wil generate an error response)
            where Z in &#x60;LINESTRINGZ&#x60; and &#x60;LINESTRINGZM&#x60;
            refers to the height value. &#x60;If the specified CRS does not
            define the height units, the heights units will default to metres
            above mean sea level&#x60;  and the M in &#x60;LINESTRINGM&#x60;
            and &#x60;LINESTRINGZM&#x60; refers to the number of seconds that
            have elapsed since the Unix epoch, that is the time 00:00:00 UTC
            on 1 January 1970. See https://en.wikipedia.org/wiki/Unix_time
        :type coords: str
        :param z: Define the vertical level to return data from i.e.
         z&#x3D;level  for instance if the 850hPa pressure level is being
         queried  z&#x3D;850  or a range to return data for all levels between
         and including 2 defined levels i.e. z&#x3D;minimum value/maximum value
         for instance if all values between and including 10m and 100m
         z&#x3D;10/100  finally a list of height values can be specified
         i.e. z&#x3D;value1,value2,value3  for instance if values at 2m, 10m
         and 80m are required  z&#x3D;2,10,80  An Arithmetic sequence using
         Recurring height intervals, the difference is the number of
         recurrences is defined at the start and the amount to increment the
         height by is defined at the end  i.e. z&#x3D;Rn/min height/height
         interval  so if the request was for 20 height levels 50m apart
         starting at 100m:  z&#x3D;R20/100/50  When not specified data from all
         available heights SHOULD be returned
        :type z: str
        :param datetime: Either a date-time or an interval, open or closed.
        Date and time expressions adhere to RFC 3339. Open intervals are
        expressed using double-dots. Examples:
         * A date-time: \&quot;2018-02-12T23:20:50Z\&quot;
         * A closed interval:
          \&quot;2018-02-12T00:00:00Z/2018-03-18T12:31:12Z\&quot;
         * Open intervals: \&quot;2018-02-12T00:00:00Z/..\&quot; or
          \&quot;../2018-03-18T12:31:12Z\&quot; Only features that have a
          temporal property that intersects the value of &#x60;datetime&#x60;
          are selected. If a feature has multiple temporal properties, it is
          the decision of the server whether only a single temporal property
          is used to determine the extent or all relevant temporal properties.
        :type datetime: str
        :param parameter_name: comma delimited list of parameters to retrieve
        data for.  Valid parameters are listed in the collections metadata
        :type parameter_name: str
        :param crs: identifier (id) of the coordinate system to return data in
         list of valid crs identifiers for the chosen collection are defined in
         the metadata responses.  If not supplied the coordinate reference
         system will default to WGS84.
        :type crs: str
        :param f: format to return the data response in
        :type f: str

        """
        ret_data = None
        try:
            thedata = self.provider_def["data"]
            if thedata.endswith(".zarr"):
                open_func = xr.open_zarr
            else:
                open_func = xr.open_dataset
            thedata = open_func(thedata)
            theproperties = self._get_coverage_properties(thedata)
            # the_id_array = self._form_the_id(thedata)
            # thedata["id_user_"] = the_id_array
            theparams = self._parse_parameter_name(
                parameter_name, theproperties)
            thedata = thedata.get(theparams)
            thepoints = ogrutil.get_coords_from_wkt_reformatting_zm(coords)
            # may need to convert the crs...
            theretdata = self._get_xarray_dataset_for_trajectory(
                collection_id, thepoints, thedata, theproperties, theparams)
            # handling native format such as netcdf
            if f == "application/x-netcdf":
                with tempfile.TemporaryFile() as fp:
                    Logger.debug('Returning data in native NetCDF format')
                    fp.write(theretdata.to_netcdf())
                    fp.seek(0)
                    return fp.read()
            the_ret_cov_json = self._get_coverage_json_for_trajectory(
                theretdata, theproperties, theparams)
            ret_data = the_ret_cov_json
        except Exception as err:
            Logger.warning(err)
            return None

        return ret_data

    def _get_xarray_dataset_for_trajectory(
            self, collection_id, points, data, properties, params):
        the_point_array = np.asarray(points)
        target_lon = xr.DataArray(the_point_array[:, 0], dims="trajectory")
        target_lat = xr.DataArray(the_point_array[:, 1], dims="trajectory")
        the_ret_data = data.sel(
            lon=target_lon, lat=target_lat, method="nearest")
        the_ret_data.attrs["featureType"] = "trajectory"
        return the_ret_data

    def _get_coverage_json_for_trajectory(
            self, thedata, properties, params):
        # handling native format such as netcdf
        the_ret_cov_json = self._gen_coverage_json_trajectory(
            thedata, params, properties,
        )
        ret_data = json.dumps(
            the_ret_cov_json.to_dict(), cls=JsonCustomEncoder)
        return ret_data

        # ----------------coverage-json-trajectory----------------
    def _gen_coverage_json_trajectory(
            self, thedata, theparams, theproperties):
        referencing = [
                        {
                            "coordinates": ["t"],
                            "system": {
                                "type": "TemporalRS",
                                "calendar": "Gregorian"
                            }
                        }, {
                            "coordinates": ["y", "x"],
                            "system": {
                                "type": "GeographicCRS",
                                "id": "http://www.opengis.net/def/crs/OGC/1.3/CRS84"
                            }
                        }
                    ]
        theaxes = {
            "composite": {
                "dataType": "tuple",
                "coordinates": ["t", "x", "y"],
                "values": self._get_composite_axes_from_trajectory(
                    thedata, theproperties
                )
            }
        }
        thedomaindesc = DomainDescription(
            type="Domain",
            domain_type="Trajectory",
            axes=theaxes,
            referencing=referencing
        )

        the_param_descriptions = self._get_parameter_descriptions(
            thedata, theparams, theproperties)
        the_ranges = self._get_coverage_json_ranges_from_trajectory(
            thedata, theparams, theproperties)
        # the_coverages = self._get_coverage_json_points_coverages(
        #    thedata, theparams, theproperties)
        thecovjson = CoverageJSON(
            type="Coverage",
            domain_type="Trajectory",
            domain=thedomaindesc,
            parameters=the_param_descriptions,
            referencing=None,
            ranges=the_ranges,
            coverages=None)
        return thecovjson

    def _get_composite_axes_from_trajectory(
            self, the_traj_data, theproperties):
        the_coords = []
        for p in the_traj_data["trajectory"]:
            the_p = the_traj_data.sel(trajectory=p)
            p_crds = self._get_composite_axes_from_trajectory_coords_at_1point(
                the_p, theproperties)
            the_coords = [*the_coords, *p_crds]
        return the_coords

    def _get_composite_axes_from_trajectory_coords_at_1point(
            self, the_p, theproperties):
        the_coords = []
        for t in the_p.coords[theproperties["time_axis_label"]]:
            the_coord = [
                self._to_datetime_string(t.values.tolist()),
                the_p.coords[theproperties["x_axis_label"]].values.tolist(),
                the_p.coords[theproperties["y_axis_label"]].values.tolist()
            ]
            the_coords.append(the_coord)
        return the_coords

    def _get_coverage_json_ranges_from_trajectory(
            self, the_traj_data, theparams, theproperties):
        the_ranges = self._init_coverage_json_ranges_for_trajectory(
            the_traj_data, theparams)
        for p in the_traj_data["trajectory"]:
            the_p = the_traj_data.sel(trajectory=p)
            the_ranges = self._update_coverage_json_ranges_from_trajectory_1point(
                the_ranges, the_p, theparams, theproperties)
        return the_ranges

    def _init_coverage_json_ranges_for_trajectory(
            self, the_traj_data, theparams):
        the_ranges = {}
        for p in theparams:
            the_range = {
              "type": "NdArray",
              "dataType": self._get_coveragejson_accepted_data_type(
                the_traj_data[p].dtype.name),
              "axisNames": ["composite"],
              "shape": [0],
              "values": []
            }
            the_ranges[p] = the_range
        return the_ranges

    def _update_coverage_json_ranges_from_trajectory_1point(
            self, the_ranges, the_p_d, theparams, theproperties):
        for p in theparams:
            the_ranges = self._update_coverage_json_ranges_from_trajectory_1point_1p(
                the_ranges, p, the_p_d, theproperties)
        return the_ranges

    def _update_coverage_json_ranges_from_trajectory_1point_1p(
            self, the_ranges, the_param_name, the_ds, theproperties):
        the_var = the_ds[the_param_name]
        the_range = the_ranges[the_param_name]
        the_shape_n = the_range["shape"][0]
        the_v_array = the_var.values.flatten()
        the_v_len = len(the_v_array)
        the_shape_n = the_shape_n + the_v_len
        the_range["shape"][0] = the_shape_n
        the_vs = the_v_array.tolist()
        if isinstance(the_vs, list):
            the_old_vs = the_range["values"]
            the_range["values"] = [*the_old_vs, *the_vs]
        elif the_v_len > 0:
            the_old_vs = the_range["values"]
            the_range["values"] = the_old_vs.append(the_vs)
        the_ranges[the_param_name] = the_range
        return the_ranges

    # ================coverage-json-trajectory================

    def get_data_for_radius(
            self, collection_id, coords, within,
            within_units, z=None, datetime=None, parameter_name=None, crs=None,
            f=None):
        """Query end point for radius queries  of collection {collectionId}

        Query end point for to return values within a defined radius of a
        point queries

        :param collection_id: Identifier (id) of a specific collection
        :type collection_id: str
        :param coords: location(s) to return data for, the coordinates are
        defined by a Well Known Text (wkt) string. to retrieve a single
        location :  POINT(x y) i.e. POINT(0 51.48) for Greenwich, London
        see http://portal.opengeospatial.org/files/?artifact_id&#x3D;25355
        and
        https://en.wikipedia.org/wiki/Well-known_text_representation_of_geometry
        the coordinate values will depend on the CRS parameter, if this is not
        defined the values will be assumed to WGS84 values
        (i.e x&#x3D;longitude and y&#x3D;latitude)
        :type coords: str
        :param within: Defines radius of area around defined coordinates to
        include in the data selection
        :type within:
        :param within_units: Distance units for the within parameter
        :type within_units: str
        :param z: Define the vertical level to return data from i.e.
        z&#x3D;level  for instance if the 850hPa pressure level is being
        queried  z&#x3D;850  or a range to return data for all levels between
        and including 2 defined levels i.e. z&#x3D;minimum value/maximum value
        for instance if all values between and including 10m and 100m
        z&#x3D;10/100  finally a list of height values can be specified i.e.
        z&#x3D;value1,value2,value3  for instance if values at 2m, 10m and 80m
        are required  z&#x3D;2,10,80  An Arithmetic sequence using Recurring
        height intervals, the difference is the number of recurrences is defined
        at the start and the amount to increment the height by is defined at
        the end  i.e. z&#x3D;Rn/min height/height interval  so if the request
        was for 20 height levels 50m apart starting at 100m:  z&#x3D;R20/100/50
        When not specified data from all available heights SHOULD be returned
        :type z: str
        :param datetime: Either a date-time or an interval, open or closed.
        Date and time expressions adhere to RFC 3339. Open intervals are
        expressed using double-dots. Examples:
        * A date-time: \&quot;2018-02-12T23:20:50Z\&quot;
        * A closed interval:
         \&quot;2018-02-12T00:00:00Z/2018-03-18T12:31:12Z\&quot;
        * Open intervals: \&quot;2018-02-12T00:00:00Z/..\&quot; or
         \&quot;../2018-03-18T12:31:12Z\&quot; Only features that have a
         temporal property that intersects the value of &#x60;datetime&#x60;
         are selected. If a feature has multiple temporal properties, it is the
         decision of the server whether only a single temporal property is used
         to determine the extent or all relevant temporal properties.
        :type datetime: str
        :param parameter_name: comma delimited list of parameters to retrieve
        data for.  Valid parameters are listed in the collections metadata
        :type parameter_name: str
        :param crs: identifier (id) of the coordinate system to return data in
        list of valid crs identifiers for the chosen collection are defined in
        the metadata responses.  If not supplied the coordinate reference
        system will default to WGS84.
        :type crs: str
        :param f: format to return the data response in
        :type f: str

        """
        ret_data = None
        try:
            thedata = self.provider_def["data"]
            if thedata.endswith(".zarr"):
                open_func = xr.open_zarr
            else:
                open_func = xr.open_dataset
            thedata = open_func(thedata)
            theproperties = self._get_coverage_properties2(thedata)
            the_id_array = self._form_the_id(thedata)
            thedata["id_user_"] = the_id_array
            theparams = self._parse_parameter_name(
                parameter_name, theproperties)
            thedata = thedata.get(theparams)
            # thepolygon = ogrutil.get_polygon_from_wkt(coords)
            # may need to convert the crs...
            # print("thepolygon=", thepolygon)
            the_crs = self._parse_crs(crs)
            the_within, the_within_units = self._parse_within(
                within, within_units)
            thecircle = gutil.create_circle_wkt(
                coords, the_crs, the_within, the_within_units)
            the_xarray_data = gutil.rxr_clip(thedata, theparams, thecircle)

            # handling native format such as netcdf
            if f == "application/x-netcdf":
                with tempfile.TemporaryFile() as fp:
                    Logger.debug('Returning data in native NetCDF format')
                    fp.write(the_xarray_data.to_netcdf())
                    fp.seek(0)
                    return fp.read()

            theretdata = self._get_coverage_json_for_area(
                collection_id, the_xarray_data, theproperties,
                theparams)
            # ret_data = json.dumps(theretdata.to_dict(), cls=JsonCustomEncoder)
            ret_data = theretdata
        except Exception as err:
            Logger.warning(err)
            return None

        return ret_data

    def _parse_crs(self, thecrs):
        try:
            pyproj.crs.CRS.from_user_input(thecrs)
            return thecrs
        except Exception as ee:
            Logger.warning(ee)
            return "urn:ogc:def:crs:OGC:1.3:CRS84"

    def _parse_within(self, within, within_units):
        try:
            the_within = float(within)
            the_within_units = ast_units.Unit(within_units.lower())
            return the_within, within_units
        except Exception as ee:
            Logger.warning(ee)
            raise Exception("Invalid inputs - {}".format(ee))

    def get_data_for_cube(
            self, collection_id, bbox=None, z=None,
            datetime=None, parameter_name=None, crs=None, f=None):
        """Query end point for Cube queries  of collection {collectionId}
         defined by a cube

        Return the data values for the data Cube defined by the query parameters

        :param collection_id: Identifier (id) of a specific collection
        :type collection_id: str
        :param bbox: Only features that have a geometry that intersects the
         bounding box are selected. The bounding box is provided as four or six
         numbers, depending on whether the coordinate reference system includes
         a vertical axis (height or depth):
          * Lower left corner, coordinate axis 1
          * Lower left corner, coordinate axis 2
          * Minimum value, coordinate axis 3 (optional)
          * Upper right corner, coordinate axis 1
          * Upper right corner, coordinate axis 2
          * Maximum value, coordinate axis 3 (optional)
         The coordinate reference system of the values is specified by the
         &#x60;crs&#x60; query parameter. If the &#x60;crs&#x60; query
         parameter is not defined the coordinate reference system is defined by
         the default &#x60;crs&#x60; for the query type. If a default
         &#x60;crs&#x60; has not been defined the values will be assumed to be
         in the WGS 84 longitude/latitude
         (http://www.opengis.net/def/crs/OGC/1.3/CRS84) coordinate reference
         system. For WGS 84 longitude/latitude the values are in most cases the
         sequence of minimum longitude, minimum latitude, maximum longitude
         and maximum latitude. However, in cases where the box spans the
         antimeridian the first value (west-most box edge) is larger than the
         third value (east-most box edge). If the vertical axis is included,
         the third and the sixth number are the bottom and the top of the
         3-dimensional bounding box. If a feature has multiple spatial geometry
         properties, it is the decision of the server whether only a single
         spatial geometry property is used to determine the extent or all
         relevant geometries.
        :type bbox: dict | bytes
        :param z: Define the vertical levels to return data from
        A range to return data for all levels between and including 2 defined
        levels  i.e. z&#x3D;minimum value/maximum value  for instance if all
        values between and including 10m and 100m  z&#x3D;10/100 A list of
        height values can be specified i.e. z&#x3D;value1,value2,value3
        for instance if values at 2m, 10m and 80m are required  z&#x3D;2,10,80
        An Arithmetic sequence using Recurring height intervals, the difference
        is the number of recurrences is defined at the start and the amount to
        increment the height by is defined at the end
        i.e. z&#x3D;Rn/min height/height interval
        so if the request was for 20 height levels 50m apart starting at 100m:
        z&#x3D;R20/100/50  When not specified data from all available heights
        SHOULD be returned
        :type z: str
        :param datetime: Either a date-time or an interval, open or closed. Date
        and time expressions adhere to RFC 3339. Open intervals are expressed
        using double-dots. Examples:
        * A date-time: \&quot;2018-02-12T23:20:50Z\&quot;
        * A closed interval:
         \&quot;2018-02-12T00:00:00Z/2018-03-18T12:31:12Z\&quot;
        * Open intervals: \&quot;2018-02-12T00:00:00Z/..\&quot;
        or \&quot;../2018-03-18T12:31:12Z\&quot;
        Only features that have a temporal property that intersects the value
        of &#x60;datetime&#x60; are selected. If
        a feature has multiple temporal properties, it is the decision of the
        server whether only a single temporal property is used to determine the
        extent or all relevant temporal properties.
        :type datetime: str
        :param parameter_name: comma delimited list of parameters to retrieve
        data for.  Valid parameters are listed in the collections metadata
        :type parameter_name: str
        :param crs: identifier (id) of the coordinate system to return data in
        list of valid crs identifiers for the chosen collection are defined in
        the metadata responses.  If not supplied the coordinate reference
        system will default to WGS84.
        :type crs: str
        :param f: format to return the data response in
        :type f: str

        """
        ret_data = None
        try:
            thedata = self.provider_def["data"]
            if thedata.endswith(".zarr"):
                open_func = xr.open_zarr
            else:
                open_func = xr.open_dataset
            thedata = open_func(thedata)
            theproperties = self._get_coverage_properties2(thedata)
            the_id_array = self._form_the_id(thedata)
            thedata["id_user_"] = the_id_array
            theparams = self._parse_parameter_name(
                parameter_name, theproperties)
            thedata = thedata.get(theparams)
            # thepolygon = ogrutil.get_polygon_from_wkt(coords)
            # may need to convert the crs...
            # print("thepolygon=", thepolygon)
            the_crs = self._parse_crs(crs)

            minX = bbox[0]
            minY = bbox[1]
            maxX = bbox[2]
            maxY = bbox[3]
            the_rect_bbox = "Polygon(({} {},{} {},{} {},{} {},{} {}))".format(
                minX, minY,
                maxX, minY,
                maxX, maxY,
                minX, maxY,
                minX, minY)
            the_xarray_data = gutil.rxr_clip(thedata, theparams, the_rect_bbox)

            # handling native format such as netcdf
            if f == "application/x-netcdf":
                with tempfile.TemporaryFile() as fp:
                    Logger.debug('Returning data in native NetCDF format')
                    fp.write(the_xarray_data.to_netcdf())
                    fp.seek(0)
                    return fp.read()

            theretdata = self._get_coverage_json_for_area(
                collection_id, the_xarray_data, theproperties,
                theparams)
            # ret_data = json.dumps(theretdata.to_dict(), cls=JsonCustomEncoder)
            ret_data = theretdata
        except Exception as err:
            Logger.warning(err)
            return None

        return ret_data

    def get_data_for_area(
            self, collection_id, coords, z=None,
            datetime=None, parameter_name=None, crs=None,
            resolution_x=None, resolution_y=None, f=None):
        """Query end point for area queries  of collection {collectionId}
        defined by a polygon

        Return the data values for the data area defined by the query parameters

        :param collection_id: Identifier (id) of a specific collection
        :type collection_id: str
        :param coords: Only data that has a geometry that intersects the area
         defined by the polygon are selected.  The polygon is defined using a Well
         Known Text string following
          coords&#x3D;POLYGON((x y,x1 y1,x2 y2,...,xn yn x y))
         which are values in the coordinate system defined by the crs query
         parameter (if crs is not defined the values will be assumed to be WGS84
         longitude/latitude coordinates).  For instance a polygon that roughly
         describes an area that contains South West England in WGS84 would look
         like:
          coords&#x3D;POLYGON((-6.1 50.3,-4.35 51.4,-2.6 51.6,-2.8 50.6,-5.3
           49.9,-6.1,50.3))
         see http://portal.opengeospatial.org/files/?artifact_id&#x3D;25355 and
         https://en.wikipedia.org/wiki/Well-known_text_representation_of_geometry
         The coords parameter will only support 2D POLYGON definitions
        :type coords: str
        :param z: Define the vertical level to return data from i.e. z&#x3D;level
         for instance if the 850hPa pressure level is being queried  z&#x3D;850
         or a range to return data for all levels between and including 2 defined
         levels i.e. z&#x3D;minimum value/maximum value  for instance if all values
         between and including 10m and 100m  z&#x3D;10/100  finally a list of
         height values can be specified i.e. z&#x3D;value1,value2,value3  for
         instance if values at 2m, 10m and 80m are required  z&#x3D;2,10,80
         An Arithmetic sequence using Recurring height intervals, the difference
         is the number of recurrences is defined at the start and the amount to
         increment the height by is defined at the end  i.e.
         z&#x3D;Rn/min height/height interval  so if the request was for 20 height
         levels 50m apart starting at 100m:
          z&#x3D;R20/100/50  When not specified data from all available heights
         SHOULD be returned
        :type z: str
        :param datetime: Either a date-time or an interval, open or closed. Date
         and time expressions adhere to RFC 3339. Open intervals are expressed
         using double-dots. Examples:
         * A date-time: \&quot;2018-02-12T23:20:50Z\&quot;
         * A closed interval:
          \&quot;2018-02-12T00:00:00Z/2018-03-18T12:31:12Z\&quot;
         * Open intervals: \&quot;2018-02-12T00:00:00Z/..\&quot;
          or \&quot;../2018-03-18T12:31:12Z\&quot; Only features that have a
          temporal property that intersects the value of &#x60;datetime&#x60;
          are selected.
         If a feature has multiple temporal properties, it is the decision of the
         server whether only a single temporal property is used to determine the
         extent or all relevant temporal properties.
        :type datetime: str
        :param parameter_name: comma delimited list of parameters to retrieve data
         for.  Valid parameters are listed in the collections metadata
        :type parameter_name: str
        :param crs: identifier (id) of the coordinate system to return data in list
         of valid crs identifiers for the chosen collection are defined in the
         metadata responses.  If not supplied the coordinate reference system will
         default to WGS84.
        :type crs: str
        #x3D;10  would retrieve 10 values along the x-axis from the minimum x
         coordinate to maximum x coordinate (i.e. a value at both the minimum x and
         maximum x coordinates and 8 values between).
        :param resolution_x: Defined it the user requires data at a different
         resolution from the native resolution of the data along the x-axis
         If this is a single value it denotes the number of intervals to retrieve
         data for along the x-axis    i.e. resolution-x&
        :type resolution_x: dict | bytes
        #x3D;10  would retrieve 10 values along the y-axis from the minimum y
         coordinate to maximum y coordinate (i.e. a value at both the minimum y
         and maximum y coordinates and 8 values between).
        :param resolution_y: Defined it the user requires data at a different
         resolution from the native resolution of the data along the y-axis  If
         this is a single value it denotes the number of intervals to retrieve data
         for along the y-axis    i.e. resolution-y&
        :type resolution_y: dict | bytes
        :param f: format to return the data response in
        :type f: str

        """
        ret_data = None
        try:
            thedata = self.provider_def["data"]
            if thedata.endswith(".zarr"):
                open_func = xr.open_zarr
            else:
                open_func = xr.open_dataset
            thedata = open_func(thedata)
            theproperties = self._get_coverage_properties2(thedata)
            the_id_array = self._form_the_id(thedata)
            thedata["id_user_"] = the_id_array
            theparams = self._parse_parameter_name(
                parameter_name, theproperties)
            thedata = thedata.get(theparams)
            # thepolygon = ogrutil.get_polygon_from_wkt(coords)
            # may need to convert the crs...
            # print("thepolygon=", thepolygon)
            # native_crs = self._get_coverage_native_crs(thedata)
            the_xarray_data = gutil.rxr_clip(thedata, theparams, coords)

            # handling native format such as netcdf
            if f == "application/x-netcdf":
                with tempfile.TemporaryFile() as fp:
                    Logger.debug('Returning data in native NetCDF format')
                    fp.write(the_xarray_data.to_netcdf())
                    fp.seek(0)
                    return fp.read()

            theretdata = self._get_coverage_json_for_area(
                collection_id, the_xarray_data, theproperties,
                theparams)
            # ret_data = json.dumps(theretdata.to_dict(), cls=JsonCustomEncoder)
            ret_data = theretdata
        except Exception as err:
            Logger.warning(err)
            return None

        return ret_data

    def _get_coverage_json_grid_ranges(
            self, theds, theparams, theproperties):
        the_ranges = {}
        for p in theparams:
            the_range = self._get_coverage_json_grid_range(
                p, theds, theproperties)
            the_ranges[p] = the_range
        return the_ranges

    def _get_coverage_json_grid_range(
            self, the_param_name, the_ds, theproperties):
        the_var = the_ds[the_param_name]
        the_range = {}
        the_range["type"] = "NdArray"
        the_range["dataType"] = self._get_coveragejson_accepted_data_type(
            the_var.dtype.name)
        the_range["axisNames"] = self._form_variable_range_axes(
            the_var, theproperties)
        the_range["shape"] = list(the_var.shape)
        the_t_var = the_var.fillna(None)
        the_range["values"] = the_t_var.values.flatten().tolist()
        return the_range

    def _form_variable_range_axes(
            self, the_var, theproperties):
        try:
            theaxes = list(the_var.dims)
            the_ret_axes = []
            for k, v in enumerate(theaxes):
                if v == theproperties["time_axis_label"]:
                    the_ret_axes.append("t")
                elif v == theproperties["x_axis_label"]:
                    the_ret_axes.append("x")
                elif v == theproperties["y_axis_label"]:
                    the_ret_axes.append("y")
                else:
                    the_ret_axes.append(v)
            return the_ret_axes
        except Exception as ee:
            logging.getLogger(
                "ogc_edr_lib.providers.XarrayEDRProvider"
                ).warning("Error: {}".format(ee))
            return None

    def _get_parameter_descriptions(
            self, theds, theparams, theproperties):
        the_param_descriptions = {}
        for p in theparams:
            the_param = self._get_parameter_description(
                p, theds)
            the_param_descriptions[p] = the_param
        return the_param_descriptions

    def _get_parameter_description(
            self, the_param_name, the_ds):
        the_param = self._get_parameter_description_from_config(
            the_param_name)
        if the_param is None:
            the_param = self._get_parameter_description_from_variable(
                the_param_name, the_ds)
        return the_param

    def _get_parameter_description_from_variable(
            self, the_param_name, the_ds):
        try:
            the_var = the_ds[the_param_name]
            the_attrs = the_var.attrs
            the_desc = the_attrs.get("long_name", None)
            if the_desc is None:
                the_desc_o = None
            else:
                the_desc_o = {"en": the_desc}
            the_label = the_attrs.get("standard_name", None)
            if the_label is None:
                the_label = the_desc
            if the_label is None:
                the_label_o = None
            else:
                the_label_o = {"en": the_label}
            the_unit_label = the_attrs.get("units", None)
            if the_unit_label is None:
                the_unit_label_o = None
            else:
                the_unit_label_o = {"en": the_unit_label}
            the_symbol = the_attrs.get("units", None)
            if the_symbol is None:
                the_symbol_o = None
            else:
                the_type_o = "http://ogc/"+the_symbol
                the_symbol_o = {"type": the_type_o, "value": the_symbol}
            the_dtype = the_var.dtype.name
            the_units = Units(
                label=the_unit_label_o,
                symbol=the_symbol_o)
            the_ob_property = ObservedProperty(
                id=the_param_name,
                label=the_label_o,
                description=None,
                categories=None
            )
            the_param = Parameter(
                type="Parameter",
                description=the_desc_o,
                label=the_label_o,
                unit=the_units,
                id=the_param_name,
                data_type=the_dtype,
                observed_property=the_ob_property,
                category_encoding=None,
                extent=None,
                measurement_type=None
            )
            return the_param
        except Exception as ee:
            logging.getLogger(
                "ogc_edr_lib.providers.xarray_edr.XarrayEDRProvider"
            ).warning(
                "_get_parameter_description_from_variable - {}".format(ee)
                )
            return None

    def _get_parameter_description_from_config(
            self, the_param_name):
        logging.getLogger(
            "ogc_edr_lib.providers.xarray_edr.XarrayEDRProvider"
            ).error(
            "_get_parameter_description_from_config: Not implemented."
            )
        return None

    def _gen_coverage_json_grid(self, theds, theparams, theproperties):
        if theds.coords[
                theproperties["x_axis_label"]].ndim == 0:
            x_values = [theds.coords[
                theproperties["x_axis_label"]].values.tolist()]
        else:
            x_values = theds.coords[
                theproperties["x_axis_label"]].values.tolist()
        if theds.coords[
                theproperties["y_axis_label"]].ndim == 0:
            y_values = [theds.coords[
                theproperties["y_axis_label"]].values.tolist()]
        else:
            y_values = theds.coords[
                theproperties["y_axis_label"]].values.tolist()
        if theds.coords[
                theproperties["time_axis_label"]].ndim == 0:
            t_values = [theds.coords[
                theproperties["time_axis_label"]].values.tolist()]
        else:
            t_values = theds.coords[
                theproperties["time_axis_label"]].values.tolist()
        theaxes = {
            "x": {"values": x_values},
            "y": {"values": y_values},
            "t": {"values": self._convert_time_array_to_strings(
                t_values)}
        }
        thereferencing = [
                {
                    "coordinates": self._replace_variable_coordinates(
                        theproperties),
                    "system": {
                        "type": "GeographicCRS",
                        "id": "http://www.opengis.net/def/crs/OGC/1.3/CRS84"
                    }
                }, {
                    "coordinates": ["t"],
                    "system": {
                        "type": "TemporalRS",
                        "calendar": "Gregorian"
                    }
                }
            ]
        thedomaindesc = DomainDescription(
            type="Domain",
            domain_type="Grid",
            axes=theaxes,
            referencing=thereferencing
        )
        the_param_descriptions = self._get_parameter_descriptions(
            theds, theparams, theproperties)
        the_ranges = self._get_coverage_json_grid_ranges(
            theds, theparams, theproperties)
        thecovjson = CoverageJSON(
            type="Coverage",
            domain=thedomaindesc,
            parameters=the_param_descriptions,
            ranges=the_ranges)
        return thecovjson

    def _convert_time_array_to_strings(self, thetimes):
        the_ret_time = []
        for k, v in enumerate(thetimes):
            the_ret_time.append(self._to_datetime_string(v))
        return the_ret_time

    def _replace_variable_coordinates(self, theproperties):
        try:
            theaxes = theproperties["axes"]
            the_ret_axes = []
            for k, v in enumerate(theaxes):
                if v == theproperties["time_axis_label"]:
                    continue
                elif v == theproperties["x_axis_label"]:
                    the_ret_axes.append("x")
                elif v == theproperties["y_axis_label"]:
                    the_ret_axes.append("y")
                else:
                    the_ret_axes.append(v)
            return the_ret_axes
        except Exception as ee:
            logging.getLogger(
                "ogc_edr_lib.providers.XarrayEDRProvider"
                ).warning("Error: {}".format(ee))
            return None

    def _get_coverage_json_for_area(
            self, collection_id, thedata,
            theproperties, theparams):
        the_ret_covjson = self._gen_coverage_json_grid(
            thedata, theparams, theproperties)
        the_ret_covjson_str = json.dumps(
            the_ret_covjson.to_dict(), cls=JsonCustomEncoder)
        return the_ret_covjson_str

    def get_data_for_point(
            self, collection_id, coords, z=None,
            datetime=None, parameter_name=None, crs=None, f=None):
        """Query end point for position queries  of collection {collectionId}

        Query end point for position queries

        :param collection_id: Identifier (id) of a specific collection
        :type collection_id: str
        :param coords: location(s) to return data for, the coordinates are
         defined by a Well Known Text (wkt) string. to retrieve a single
         location :  POINT(x y) i.e. POINT(0 51.48) for Greenwich, London
         And for a list of locations  MULTIPOINT((x y),(x1 y1),(x2 y2),(x3 y3))
         i.e.
   MULTIPOINT((38.9 -77),(48.85 2.35),(39.92 116.38),(-35.29 149.1),(51.5 -0.1))
         see http://portal.opengeospatial.org/files/?artifact_id&#x3D;25355 and
         https://en.wikipedia.org/wiki/Well-known_text_representation_of_geometry
         the coordinate values will depend on the CRS parameter, if this is not
         defined the values will be assumed to WGS84 values
         (i.e x&#x3D;longitude and y&#x3D;latitude)
        :type coords: str
        :param z: Define the vertical level to return data from
         i.e. z&#x3D;level  for instance if the 850hPa pressure level is being
         queried  z&#x3D;850  or a range to return data for all levels between
         and including 2 defined levels i.e. z&#x3D;minimum value/maximum value
         for instance if all values between and including 10m and
         100m  z&#x3D;10/100  finally a list of height values can be specified
         i.e. z&#x3D;value1,value2,value3  for instance if values at 2m, 10m
         and 80m are required  z&#x3D;2,10,80  An Arithmetic sequence using
         Recurring height intervals, the difference is the number of recurrences
         is defined at the start and the amount to increment the height by is
         defined at the end  i.e. z&#x3D;Rn/min height/height interval  so if
         the request was for 20 height levels 50m apart starting at
         100m:  z&#x3D;R20/100/50  When not specified data from all available
         heights SHOULD be returned
        :type z: str
        :param datetime: Either a date-time or an interval, open or closed.
         Date and time expressions adhere to RFC 3339. Open intervals are
         expressed using double-dots. Examples:
         * A date-time: \&quot;2018-02-12T23:20:50Z\&quot;
         * A closed interval:
          \&quot;2018-02-12T00:00:00Z/2018-03-18T12:31:12Z\&quot;
         * Open intervals: \&quot;2018-02-12T00:00:00Z/..\&quot;
          or \&quot;../2018-03-18T12:31:12Z\&quot; Only features that have
          a temporal property that intersects the value of &#x60;datetime&#x60;
          are selected. If a feature has multiple temporal properties, it is
          the decision of the server whether only a single temporal property is
          used to determine the extent or all relevant temporal properties.
        :type datetime: str
        :param parameter_name: comma delimited list of parameters to retrieve
         data for.  Valid parameters are listed in the collections metadata
        :type parameter_name: str
        :param crs: identifier (id) of the coordinate system to return data in
         list of valid crs identifiers for the chosen collection are defined in
         the metadata responses.  If not supplied the coordinate reference
         system will default to WGS84.
        :type crs: str
        :param f: format to return the data response in
        :type f: str

        """
        ret_data = None
        try:
            thedata = self.provider_def["data"]
            if thedata.endswith(".zarr"):
                open_func = xr.open_zarr
            else:
                open_func = xr.open_dataset
            thedata = open_func(thedata)
            theproperties = self._get_coverage_properties(thedata)
            # the_id_array = self._form_the_id(thedata)
            # thedata["id_user_"] = the_id_array
            theparams = self._parse_parameter_name(
                parameter_name, theproperties)
            thedata = thedata.get(theparams)
            thepoints = ogrutil.get_coords_from_wkt(coords)
            # may need to convert the crs...
            theretdata = self._get_xarray_dataset_for_points(
                collection_id, thepoints, thedata, theproperties, theparams)
            # handling native format such as netcdf
            if f == "application/x-netcdf":
                with tempfile.TemporaryFile() as fp:
                    Logger.debug('Returning data in native NetCDF format')
                    fp.write(theretdata.to_netcdf())
                    fp.seek(0)
                    return fp.read()
            the_ret_cov_json = self._get_coverage_json_for_points(
                theretdata, theproperties, theparams)
            ret_data = the_ret_cov_json
        except Exception as err:
            Logger.warning(err)
            return None

        return ret_data

    def _get_xarray_dataset_for_points(
            self, collection_id, points, data, properties, params):
        the_point_array = np.asarray(points)
        target_lon = xr.DataArray(the_point_array[:, 0], dims="points")
        target_lat = xr.DataArray(the_point_array[:, 1], dims="points")
        the_ret_data = data.sel(
            lon=target_lon, lat=target_lat, method="nearest")
        return the_ret_data

    def _get_coverage_json_for_points(
            self, thedata, properties, params):
        # handling native format such as netcdf
        the_ret_cov_json = self._gen_coverage_json_points(
            thedata, params, properties,
        )
        ret_data = json.dumps(
            the_ret_cov_json.to_dict(), cls=JsonCustomEncoder)
        return ret_data

        # ----------------coverage-json-point----------------
    def _gen_coverage_json_points(
            self, thedata, theparams, theproperties):
        thedomaindesc = DomainDescription(
            type="Domain",
            domain_type="Point",
            axes=None
        )
        referencing = [
                        {
                            "coordinates": self._replace_variable_coordinates(
                                theproperties),
                            "system": {
                                "type": "GeographicCRS",
                                "id": "http://www.opengis.net/def/crs/OGC/1.3/CRS84"
                            }
                        }, {
                            "coordinates": ["t"],
                            "system": {
                                "type": "TemporalRS",
                                "calendar": "Gregorian"
                            }
                        }
                    ]

        the_param_descriptions = self._get_parameter_descriptions(
            thedata, theparams, theproperties)
        # the_ranges = self._get_coverage_json_grid_ranges(
        #    theds, theparams, theproperties)
        the_coverages = self._get_coverage_json_points_coverages(
            thedata, theparams, theproperties)
        thecovjson = CoverageJSON(
            type="CoverageCollection",
            domain_type="Point",
            domain=None,
            parameters=the_param_descriptions,
            referencing=referencing,
            ranges=None,
            coverages=the_coverages)
        return thecovjson

    def _get_coverage_json_points_coverages(
            self, theds, theparams, theproperties):
        the_coverages = []
        for p in theds["points"]:
            the_coverage = self._gen_coverage_json_point(
                theds.sel(points=p), theparams, theproperties)
            the_coverages.append(the_coverage)
        return the_coverages

    def _gen_coverage_json_point(self, theds, theparams, theproperties):
        theaxes = {
            "x": {"values": [theds.coords[
                theproperties["x_axis_label"]].values.tolist()]},
            "y": {"values": [theds.coords[
                theproperties["y_axis_label"]].values.tolist()]},
            "t": {"values": self._convert_time_array_to_strings(
                theds.coords[
                    theproperties["time_axis_label"]].values.tolist())}
        }
        thedomaindesc = DomainDescription(
            type="Domain",
            domain_type=None,
            axes=theaxes
        )
        the_ranges = self._get_coverage_json_point_ranges(
            theds, theparams, theproperties)
        thecovjson = CoverageJSON(
            type="Coverage",
            domain=thedomaindesc,
            parameters=None,
            ranges=the_ranges)
        return thecovjson

    def _get_coverage_json_point_ranges(
            self, theds, theparams, theproperties):
        the_ranges = {}
        for p in theparams:
            the_range = self._get_coverage_json_point_range(
                p, theds, theproperties)
            the_ranges[p] = the_range
        return the_ranges

    def _get_coverage_json_point_range(
            self, the_param_name, the_ds, theproperties):
        the_var = the_ds[the_param_name]
        the_range = {}
        the_range["type"] = "NdArray"
        the_range["dataType"] = self._get_coveragejson_accepted_data_type(
            the_var.dtype.name)
        the_t_var = the_var.fillna(None)
        the_range["values"] = the_t_var.values.flatten().tolist()
        return the_range
    # ================coverage-json-point================

    def _get_coveragejson_accepted_data_type(self, the_dtype_name):
        if self._str_startswith_ignorecase("int", the_dtype_name):
            return "integer"
        elif self._str_startswith_ignorecase("float", the_dtype_name):
            return "float"
        elif self._str_startswith_ignorecase("str", the_dtype_name):
            return "string"
        else:
            return "string"

    def _str_startswith_ignorecase(self, pattern, the_str):
        return bool(re.match(pattern, the_str, re.I))

    def _str_endswith_ignorecase(self, pattern, the_str):
        return bool(re.match(".*"+pattern+"$", the_str, re.I))

    def _get_feature_collection_for_points2(
            self, collection_id, points, data, properties, params):
        xcoord = data.coords[properties["x_axis_label"]]
        ycoord = data.coords[properties["y_axis_label"]]
        thefeatures = []
        for pnt in points:
            idxx = self._locate_closest_point(
                xcoord, pnt[0])
            idxy = self._locate_closest_point(
                ycoord, pnt[1])
            thesfeatures = self._get_feature_collection_for_points_feature(
                collection_id, idxx, idxy, data, properties, params
            )
            thefeatures = [*thefeatures, *thesfeatures]
        n_matched = len(thefeatures)
        n_returned = len(thefeatures)
        # time_stamp =
        #    time_stamp=time_stamp,
        #    links=thelinks,
        #    parameters=theparameters,
        thegeojsoncollecion = EdrFeatureCollectionGeoJSON(
            type="FeatureCollection",
            features=thefeatures,
            number_matched=n_matched,
            number_returned=n_returned
        )
        return thegeojsoncollecion

    def _get_feature_collection_for_points_feature(
            self, collection_id, idxx, idxy, data, properties, params
            ):
        yv = data.coords[self.y_field].values[idxy]
        xv = data.coords[self.x_field].values[idxx]
        therfeatures = []
        for ti, tv in enumerate(data.coords[self.time_field].values):
            # for this order (lat, lon) when in degrees
            coords = [yv, xv]
            thepointfeature = PointGeoJSON(
                type="Point",
                coordinates=coords
            )
            sdatetime = self._to_datetime_string(tv)
            slabel = data["id_user_"].values[ti][idxy][idxx]
            edrqendpoint = "/collections/{}/items/{}".format(
                collection_id,
                slabel
            )
            pname = properties["fields"]
            fproperties = EdrProperties(
                datetime=sdatetime,
                label=slabel,
                edrqueryendpoint=edrqendpoint,
                parameter_name=pname
            )
            thelinks = []
            thehref = "/collections/{}/items/{}".format(
                collection_id,
                slabel)
            thelink = edrLink(
                rel="data",
                href=thehref,
                type="application/geo+json",
                title=slabel
            )
            thefproperties = fproperties.to_dict()
            # add additional properties
            for f in params:
                thefproperties[f] = data[f].values[ti, idxy, idxx]
            thelinks.append(thelink)
            thefeature = FeatureGeoJSON(
                type="Feature",
                geometry=thepointfeature,
                properties=thefproperties,
                id=slabel,
                links=thelinks
            )
            therfeatures.append(thefeature)
        return therfeatures

    def _locate_closest_point(self, coordaxis, coord):
        if (coordaxis is None or len(coordaxis) < 1):
            return -1
        v0 = coordaxis[0]
        k0 = 0
        for k, v in enumerate(coordaxis.values):
            if (v > v0):
                if (coord >= v0
                        and coord <= v):
                    if ((coord-v0) < (v-coord)):
                        return k0
                    else:
                        return k
            else:
                if (coord >= v
                        and coord <= v0):
                    if ((coord-v) < (v0-coord)):
                        return k
                    else:
                        return k0
            k0 = k
            v0 = v
        if coord < coordaxis[0]:
            ext = coordaxis[0] - (coordaxis[1] - coordaxis[0])
            if (coord >= ext
                    and coord <= coordaxis[0]):
                return 0
        else:
            ext = coordaxis[-1] + (coordaxis[-1] - coordaxis[-2])
            if (coord >= coordaxis[-1]
                    and coord <= ext):
                return len(coordaxis)-1
        return -1

    def _parse_parameter_name(self, parameter_name, theproperties):
        theparameters = theproperties["fields"]
        if parameter_name is not None:
            params = parameter_name.split(",")
            theparams = []
            for p in params:
                thep = p.strip()
                if thep:
                    theparams.append(thep)
            if len(theparams) > 0:
                theparameters = theparams
        return theparameters

    def get_data_for_item(self, collection_id, item_id):
        """Return item {itemId} from collection {collectionId}

        Query end point to retrieve data from collection {collectionId} using a unique identifier

        :param collection_id: Identifier (id) of a specific collection
        :type collection_id: str
        :param item_id: Retrieve data from the collection using a unique identifier.
        :type item_id: str

        """
        ret_data = None
        try:
            thedata = self.provider_def["data"]
            if thedata.endswith(".zarr"):
                open_func = xr.open_zarr
            else:
                open_func = xr.open_dataset
            thedata = open_func(thedata)
            strs = item_id.split('_')
            theretdata = {}
            theproperties = self._get_coverage_properties(thedata)
            ti = int(strs[0])
            yi = int(strs[1])
            xi = int(strs[2])
            for f in theproperties["fields"]:
                theretdata[f] = thedata[f].values[ti, yi, xi]
            ret_data = json.dumps(theretdata, cls=JsonCustomEncoder)
        except Exception as err:
            Logger.warning(err)
            return None

        return ret_data

    def query_items(self, collection_id, bbox=None,
                    datetime=None, limit=None, offset=None, f=None):
        """
        Extract metadata from a collection

        :param bbox: bounding box [minx,miny,maxx,maxy]
        :param datetime: temporal (datestamp or extent)
        :param limit: maximum number of feaures
        :param f: data format of output

        :returns: string representation of format
        """
        ret_data = None
        try:
            thedata = self.provider_def["data"]
            if thedata.endswith(".zarr"):
                open_func = xr.open_zarr
            else:
                open_func = xr.open_dataset
            thedata = open_func(thedata)
            theproperties = self._get_coverage_properties(thedata)
            query_params = {}
            if bbox:
                query_params[theproperties['x_axis_label']] = \
                    slice(bbox[0], bbox[2])
                query_params[theproperties['y_axis_label']] = \
                    slice(bbox[1], bbox[3])
            if datetime is not None:
                if '/' in datetime:
                    begin, end = datetime.split('/')
                    if begin < end:
                        query_params[self.time_field] = slice(begin, end)
                    else:
                        Logger.warning(
                            'Range may be inr reverse order for time:'
                            '{}'.format(datetime)
                        )
                        query_params[self.time_field] = slice(end, begin)
                else:
                    query_params[self.time_field] = datetime
            the_id_array = self._form_the_id(thedata)
            thedata["id_user_"] = the_id_array
            thqeretdata = thedata.sel(query_params)
            theretdata = self._gen_geojson_with_limit(
                collection_id, thqeretdata, theproperties, limit=limit,
                offset=offset)
            ret_data = theretdata.to_str()
        except Exception as err:
            Logger.warning(err)
            return None

        return ret_data

    def _form_the_id(self, thedata):
        dims = [self.time_field, self.y_field, self.x_field]
        coords = [thedata[self.time_field],
                  thedata[self.y_field], thedata[self.x_field]]
        the_id_array = []
        for ti, tv in enumerate(thedata.coords[self.time_field].values):
            the_id_t = []
            for yi, yv in enumerate(thedata.coords[self.y_field].values):
                the_id_y = []
                for xi, xv in enumerate(thedata.coords[self.x_field].values):
                    theid = str(ti)+"_"+str(yi)+"_"+str(xi)
                    the_id_y.append(theid)
                the_id_t.append(the_id_y)
            the_id_array.append(the_id_t)
            the_data_array = xr.DataArray(
                the_id_array, coords=coords, dims=dims)
        return the_data_array

    def _gen_geojson_with_limit(
            self,  collection_id, thedata, theproperties, limit=None,
            offset=None):
        theoffset = 0
        if offset is not None:
            theoffset = offset
        thelimit = 10000
        if (
                limit is not None
                and limit < 10000
                and limit > 0
                ):
            thelimit = limit
        n_matched, n_returned, thefeatures = self._gen_geojson_features(
            collection_id, thedata, theproperties, thelimit, theoffset)
        # time_stamp =
        #    time_stamp=time_stamp,
        #    links=thelinks,
        #    parameters=theparameters,
        thegeojsoncollecion = EdrFeatureCollectionGeoJSON(
            type="FeatureCollection",
            features=thefeatures,
            number_matched=n_matched,
            number_returned=n_returned
        )
        return thegeojsoncollecion

    def _gen_geojson_features(
            self,  collection_id, thedata, theproperties, thelimit, theoffset):
        totalcount = 0
        acount = 0
        thefeatures = []
        print("theoffset=", theoffset)
        print("thelimit=", thelimit)
        for ti, tv in enumerate(thedata.coords[self.time_field].values):
            for yi, yv in enumerate(thedata.coords[self.y_field].values):
                for xi, xv in enumerate(thedata.coords[self.x_field].values):
                    totalcount = totalcount + 1
                    if totalcount < theoffset:
                        continue
                    if totalcount > thelimit:
                        break
                    acount += 1
                    # for this order (lat, lon) when in degrees
                    coords = [yv, xv]
                    thepointfeature = PointGeoJSON(
                        type="Point",
                        coordinates=coords
                    )
                    sdatetime = self._to_datetime_string(tv)
                    slabel = thedata["id_user_"].values[ti][yi][xi]
                    edrqendpoint = "/collections/{}/items/{}".format(
                        collection_id,
                        slabel
                    )
                    pname = theproperties["fields"]
                    fproperties = EdrProperties(
                        datetime=sdatetime,
                        label=slabel,
                        edrqueryendpoint=edrqendpoint,
                        parameter_name=pname
                    )
                    thelinks = []
                    thehref = "/collections/{}/items/{}".format(
                        collection_id,
                        slabel)
                    thelink = edrLink(
                        rel="data",
                        href=thehref,
                        type="application/geo+json",
                        title=slabel
                    )
                    thefproperties = fproperties.to_dict()
                    # add additional properties
                    for f in theproperties["fields"]:
                        thefproperties[f] = thedata[f].values[ti, yi, xi]
                    thelinks.append(thelink)
                    thefeature = FeatureGeoJSON(
                        type="Feature",
                        geometry=thepointfeature,
                        properties=thefproperties,
                        id=slabel,
                        links=thelinks
                    )
                    thefeatures.append(thefeature)
        print("totalcount=", totalcount)
        print("acount=", acount)
        return totalcount, acount, thefeatures

    def __repr__(self):
        return '<BaseFormatter> {}'.format(self.name)

    def _get_coverage_properties2(self, thedata):
        self.x_field = self.provider_def.get('x_field', None)
        self.y_field = self.provider_def.get('y_field', None)
        self.time_field = self.provider_def.get('time_field', None)
        time_var, y_var, x_var = [None, None, None]
        for coord in thedata.coords:
            if coord.lower() == 'time':
                time_var = coord
                continue
            if thedata.coords[coord].attrs['units'] == 'degrees_north':
                y_var = coord
                continue
            if thedata.coords[coord].attrs['units'] == 'degrees_east':
                x_var = coord
                continue

        if self.x_field is None:
            self.x_field = x_var
        if self.y_field is None:
            self.y_field = y_var
        if self.time_field is None:
            self.time_field = time_var
        # It would be preferable to use CF attributes to get width
        # resolution etc but for now a generic approach is used to asess
        # all of the attributes based on lat lon vars

        properties = {
            'bbox': [
                thedata.coords[self.x_field].values[0],
                thedata.coords[self.y_field].values[0],
                thedata.coords[self.x_field].values[-1],
                thedata.coords[self.y_field].values[-1],
            ],
            'time_range': [
                self._to_datetime_string(
                    thedata.coords[self.time_field].values[0]
                ),
                self._to_datetime_string(
                    thedata.coords[self.time_field].values[-1]
                )
            ],
            'bbox_crs': 'http://www.opengis.net/def/crs/OGC/1.3/CRS84',
            'crs_type': 'GeographicCRS',
            'x_axis_label': self.x_field,
            'y_axis_label': self.y_field,
            'time_axis_label': self.time_field,
            'width': thedata.dims[self.x_field],
            'height': thedata.dims[self.y_field],
            'time': thedata.dims[self.time_field],
            'time_duration': self.get_time_coverage_duration(thedata),
            'bbox_units': 'degrees',
            'resx': np.abs(thedata.coords[self.x_field].values[1]
                           - thedata.coords[self.x_field].values[0]),
            'resy': np.abs(thedata.coords[self.y_field].values[1]
                           - thedata.coords[self.y_field].values[0]),
            'restime': self.get_time_resolution(thedata)
        }

        if 'crs' in thedata.variables.keys():
            properties['bbox_crs'] = '{}/{}'.format(
                'http://www.opengis.net/def/crs/OGC/1.3/',
                thedata.crs.epsg_code)

            properties['inverse_flattening'] = thedata.crs.\
                inverse_flattening

            properties['crs_type'] = 'ProjectedCRS'

        # properties['axes'] = [
        #    properties['x_axis_label'],
        #    properties['y_axis_label'],
        #    properties['time_axis_label']
        # ]

        properties['fields'] = [name for name in thedata.variables
                                if len(thedata.variables[name].shape) >= 3]
        if len(properties["fields"]) > 0:
            properties['axes'] = list(thedata[properties['fields'][0]].dims)

        return properties

    def _get_coverage_properties(self, thedata):
        self.x_field = self.provider_def.get('x_field', None)
        self.y_field = self.provider_def.get('y_field', None)
        self.time_field = self.provider_def.get('time_field', None)
        print("time_field0=", self.time_field)
        time_var, y_var, x_var = [None, None, None]
        print("thecoods=", thedata.coords)
        for coord in thedata.coords:
            if coord.lower() == 'time':
                time_var = coord
                continue
            if thedata.coords[coord].attrs['units'] == 'degrees_north':
                y_var = coord
                continue
            if thedata.coords[coord].attrs['units'] == 'degrees_east':
                x_var = coord
                continue

        if self.x_field is None:
            self.x_field = x_var
        if self.y_field is None:
            self.y_field = y_var
        if self.time_field is None:
            self.time_field = time_var
        print("time_field=", self.time_field)
        print("x_field=", self.x_field)
        print("y_field=", self.y_field)
        # It would be preferable to use CF attributes to get width
        # resolution etc but for now a generic approach is used to asess
        # all of the attributes based on lat lon vars

        properties = {
            'bbox': [
                thedata.coords[self.x_field].values[0],
                thedata.coords[self.y_field].values[0],
                thedata.coords[self.x_field].values[-1],
                thedata.coords[self.y_field].values[-1],
            ],
            'time_range': [
                self._to_datetime_string(
                    thedata.coords[self.time_field].values[0]
                ),
                self._to_datetime_string(
                    thedata.coords[self.time_field].values[-1]
                )
            ],
            'bbox_crs': 'http://www.opengis.net/def/crs/OGC/1.3/CRS84',
            'crs_type': 'GeographicCRS',
            'x_axis_label': self.x_field,
            'y_axis_label': self.y_field,
            'time_axis_label': self.time_field,
            'width': thedata.dims[self.x_field],
            'height': thedata.dims[self.y_field],
            'time': thedata.dims[self.time_field],
            'time_duration': self.get_time_coverage_duration(thedata),
            'bbox_units': 'degrees',
            'resx': np.abs(thedata.coords[self.x_field].values[1]
                           - thedata.coords[self.x_field].values[0]),
            'resy': np.abs(thedata.coords[self.y_field].values[1]
                           - thedata.coords[self.y_field].values[0]),
            'restime': self.get_time_resolution(thedata)
        }

        if 'crs' in thedata.variables.keys():
            properties['bbox_crs'] = '{}/{}'.format(
                'http://www.opengis.net/def/crs/OGC/1.3/',
                thedata.crs.epsg_code)

            properties['inverse_flattening'] = thedata.crs.\
                inverse_flattening

            properties['crs_type'] = 'ProjectedCRS'

        properties['axes'] = [
            properties['x_axis_label'],
            properties['y_axis_label'],
            properties['time_axis_label']
        ]

        properties['fields'] = [name for name in thedata.variables
                                if len(thedata.variables[name].shape) >= 3]

        return properties

    @staticmethod
    def _to_datetime_string(datetime_obj):
        """
        Convenience function to formulate string from various datetime objects

        :param datetime_obj: datetime object (native datetime, cftime)

        :returns: str representation of datetime
        """

        try:
            value = np.datetime_as_string(datetime_obj)
        except Exception as err:
            Logger.warning(err)
            if isinstance(datetime_obj, cftime.DatetimeJulian):
                value = datetime_obj.strftime('%Y-%m-%d')
            else:
                value = datetime_obj.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        return value

    def get_time_resolution(self, thedata):
        """
        Helper function to derive time resolution
        :returns: time resolution string
        """

        if thedata[self.time_field].size > 1:
            time_diff = (thedata[self.time_field][1]
                         - thedata[self.time_field][0])

            dt = np.array([time_diff.values.astype('timedelta64[{}]'.format(x))
                           for x in ['Y', 'M', 'D', 'h', 'm', 's', 'ms']])

            return str(dt[np.array([x.astype(np.int) for x in dt]) > 0][0])
        else:
            return None

    def get_time_coverage_duration(self, thedata):
        """
        Helper function to derive time coverage duration
        :returns: time coverage duration string
        """

        dur = thedata[self.time_field][-1] - thedata[self.time_field][0]
        ms_difference = dur.values.astype('timedelta64[ms]').astype(np.double)

        time_dict = {
            'days': int(ms_difference / 1000 / 60 / 60 / 24),
            'hours': int((ms_difference / 1000 / 60 / 60) % 24),
            'minutes': int((ms_difference / 1000 / 60) % 60),
            'seconds': int(ms_difference / 1000) % 60
        }

        times = ['{} {}'.format(val, key) for key, val
                 in time_dict.items() if val > 0]

        return ', '.join(times)

    def get_edr_property_datetime_duration(self, coord_time, thedata):
        """
        Helper function to derive time edr property datetime
        :returns: time coverage duration string
        """

        dur = thedata[coord_time][-1] - thedata[coord_time][0]
        if dur == 0:
            return self._to_datetime_string(thedata[coord_time][0])
        starttime = self._to_datetime_string(thedata[coord_time][0])
        endtime = self._to_datetime_string(thedata[coord_time][-1])
        return "{}/{}".format(starttime, endtime)
