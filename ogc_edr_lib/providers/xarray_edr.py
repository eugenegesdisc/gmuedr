import tempfile
import xarray as xr
import logging
import numpy as np
import cftime
import json
import netCDF4
import rioxarray
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
        the_range["dataType"] = the_var.dtype.name
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
                the_symbol_o = {"value": the_symbol}
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
                            "ccordinates": ["t"],
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
        the_range["dataType"] = the_var.dtype.name
        the_t_var = the_var.fillna(None)
        the_range["values"] = the_t_var.values.flatten().tolist()
        return the_range
    # ================coverage-json-point================

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
        print("parameter_name=", parameter_name)
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
                x_var = coord
                continue
            if thedata.coords[coord].attrs['units'] == 'degrees_east':
                y_var = coord
                continue

        if self.x_field is None:
            self.x_field = x_var
        if self.y_field is None:
            self.y_field = y_var
        if self.time_field is None:
            self.time_field = time_var
        print("time_field=", self.time_field)
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

        return ', '.join(times)
