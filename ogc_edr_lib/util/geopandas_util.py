import geopandas as gpd
import rioxarray
import xarray as xr
from shapely.geometry import mapping, Point, LineString
import pyproj
from astropy import units
import logging
import numpy as np
import pandas as pd
import re
import traceback


def create_corridor_lines_wkt(
        line_wkt: str, crs: str, corridor_width: float, cw_units: str,
        grd_res=None):
    """
    Create an array of corridor lines (2D only)

    :param line_wkt: Line in wkt, e.g. LINESTRING(...)
    :param crs: String input of projection. Any supported
        by pyproj.from_user_input
    :param corridor_width: The width for the corridor.
    :param cw_units: Units. e.g. meter, km
    :param grd_res: Grid resolution in meters.

    retrun array of geopanda.GeoSeries geometry in given crs
    """
    the_l_lines = []
    the_r_lines = []
    try:
        # incase there is no space between optional dimensions and geom keyword
        line_wkt = re.sub("(?i) *(ZM|Z|M) *\\(", " \\1 (", line_wkt)
        thegeom = gpd.GeoSeries.from_wkt([line_wkt])
        aeqd = pyproj.crs.CRS.from_user_input("ESRI:54032")
        the_crs = pyproj.crs.CRS.from_user_input(crs)
        thegeom = thegeom.set_crs(the_crs)
        thegeom = thegeom.to_crs(aeqd)
        theunit = units.Unit(cw_units.lower())
        the_cw_in_meter = (corridor_width*theunit).to(units.Unit("m"))
        the_half_cw = the_cw_in_meter.value/2
        the_r_lines.append(thegeom.geometry[0])
        if grd_res is None:
            the_left = thegeom.geometry[0].parallel_offset(
                the_half_cw, "left", join_style=2)
            the_l_lines.append(the_left)
            the_right = thegeom.geometry[0].parallel_offset(
                the_half_cw, "right", join_style=2)
            the_r_lines.append(the_right)
        else:
            nn = round(the_half_cw / grd_res)
            for i in range(nn):
                the_cw = (i+1)*grd_res
                the_left = thegeom.geometry[0].parallel_offset(
                    the_cw, "left", join_style=2)
                the_l_lines.insert(0, the_left)
                the_right = thegeom.geometry[0].parallel_offset(
                    the_cw, "right", join_style=2)
                the_r_lines.append(the_right)
        print("the_l_lines=", the_l_lines)
        print("the_r_lines=", the_r_lines)
        the_geoms = [*the_l_lines, *the_r_lines]
        the_gpd_series = gpd.GeoSeries(the_geoms, crs=aeqd)
        the_ret_geoms = the_gpd_series.to_crs(the_crs)
        return the_ret_geoms
    except Exception as ee:
        logging.getLogger(
            "ogc_edr_lib.util.geopandas_util.create_circle_wkt"
            ).warning(
                "error {}".format(ee)
            )
        return None


def create_circle_wkt(pnt_wkt: str, crs: str, radius: float, theunits: str):
    """
    Create a circle

    :param pnt_wkt: Poing in wkt, e.g. POINT(5 6)
    :param crs: String input of projection. Any supported
        by pyproj.from_user_input
    :param radius: The radius for the circle.
    :param theunits: Units. e.g. meter, km

    retrun circle in wkt
    """
    try:
        thegeom = gpd.GeoSeries.from_wkt([pnt_wkt])
        aeqd = pyproj.crs.CRS.from_user_input("ESRI:54032")
        the_crs = pyproj.crs.CRS.from_user_input(crs)
        thegeom = thegeom.set_crs(the_crs)
        thegeom = thegeom.to_crs(aeqd)
        theunit = units.Unit(theunits.lower())
        the_radius_in_meter = (radius*theunit).to(units.Unit("m"))
        the_circle = thegeom.buffer(the_radius_in_meter.value)
        the_circle = the_circle.to_crs(the_crs)
        return the_circle.to_wkt()[0]
    except Exception as ee:
        logging.getLogger(
            "ogc_edr_lib.util.geopandas_util.create_circle_wkt"
            ).warning(
                "error {}".format(ee)
            )
        return None


def rxr_clip2(
        thedata, theparams, xdim, ydim, thepolygonwkt, crs):
    """
    Clip xarray object using a polygon geometry in wkt

    :param thedata: The data as a xarray.
    :param theparams: The list of parameter name or variable name.
    :param thepolygonwkt: The polygon in wkt string.

    retrun clipped result as a xarray
    """
    theretdata = {}
    thecoords = {}
    try:
        thegeom = gpd.GeoSeries.from_wkt([thepolygonwkt])
        for v in theparams:
            p = thedata[v]
            p.rio.set_spatial_dims(x_dim=xdim, y_dim=ydim, inplace=True)
            # p.rio.write_crs("epsg:4326", inplace=True)
            the_crs = get_coverage_native_crs(p.rio)
            clipped = p.rio.clip(thegeom.apply(mapping), crs, drop=True)
            theretdata[v] = clipped
            thecoords = clipped.coords
        theretds = xr.Dataset(theretdata, thecoords, thedata.attrs)
        return theretds
    except Exception as ee:
        logging.getLogger("ogc_edr_lib.util.geopandas").warning(
            ee
        )
        return None


def get_coverage_native_crs(theriodata):
    if "crs" in theriodata:
        return theriodata.crs
    else:
        the_crs = pyproj.crs.CRS.from_user_input(
            "urn:ogc:def:crs:OGC:1.3:CRS84")
        theriodata.write_crs(the_crs, inplace=True)
        return the_crs


def rxr_clip(thedata, theparams, thepolygonwkt):
    """
    Clip xarray object using a polygon geometry in wkt

    :param thedata: The data as a xarray.
    :param theparams: The list of parameter name or variable name.
    :param thepolygonwkt: The polygon in wkt string.

    retrun clipped result as a xarray
    """
    theretdata = {}
    thecoords = {}
    try:
        # print("thepolygonwkt=", thepolygonwkt)
        thegeom = gpd.GeoSeries.from_wkt([thepolygonwkt])
        # print("thegeom=", thegeom)
        for v in theparams:
            # print("v=", v)
            p = thedata[v]
            if p.dtype == '<m8[ns]':
                p = p.astype('timedelta64[ns]')
            p.rio.set_spatial_dims(x_dim="lon", y_dim="lat", inplace=True)
            p.rio.write_crs("epsg:4326", inplace=True)
            clipped = p.rio.clip(thegeom.apply(mapping), p.rio.crs, drop=True)
            theretdata[v] = clipped
            # print("len(thecoords)=", len(thecoords))
        theretds = xr.Dataset(theretdata, thecoords, thedata.attrs)
        return theretds
    except Exception as ee:
        traceback.print_exc()
        logging.getLogger("ogc_edr_lib.util.geopandas").warning(
            ee
        )
        return None


def densify_geometry(line_geometry: LineString, step, crs=None):
    """
    :param crs: epsg code of a coordinate reference system you want
     your line to be georeferenced with
    :param step: add a vertice every step in whatever unit your coordinate
     reference system use.
    """
    length_m = line_geometry.length  # get the length
    xy = []  # to store new tuples of coordinates
    for distance_along_old_line in np.arange(0, int(length_m), step):
        # interpolate a point every step along the old line
        point = line_geometry.interpolate(distance_along_old_line)
        xp, yp = point.x, point.y  # extract the coordinates

        xy.append((xp, yp))  # and store them in xy list
    # Here, we finally create a new line with densified points.
    new_line = LineString(xy)
    if crs != None:  # If you want to georeference your new geometry, uses crs to do the job.
       new_line_geo = gpd.geoseries.GeoSeries(new_line, crs=crs)
       return new_line_geo
    else:
       return new_line
