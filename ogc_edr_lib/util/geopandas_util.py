import geopandas as gpd
import rioxarray
import xarray as xr
from shapely.geometry import mapping
import logging


def rxr_clip(thedata, theparams, thepolygonwkt):
    """
    Clip xarray object using a polygon geometry in wkt

    :param thexarray: The data as a xarray.
    :param theparams: The list of parameter name or variable name.
    :param thepolygonwkt: The polygon in wkt string.

    retrun clipped result as a xarray
    """
    theretdata = {}
    thecoords = {}
    try:
        print("thepolygonwkt=", thepolygonwkt)
        thegeom = gpd.GeoSeries.from_wkt([thepolygonwkt])
        print("thegeom=", thegeom)
        for v in theparams:
            p = thedata[v]
            p.rio.set_spatial_dims(x_dim="lon", y_dim="lat", inplace=True)
            p.rio.write_crs("epsg:4326", inplace=True)
            clipped = p.rio.clip(thegeom.apply(mapping), p.rio.crs, drop=True)
            theretdata[v] = clipped
            thecoords = clipped.coords
        theretds = xr.Dataset(theretdata, thecoords, thedata.attrs)
        return theretds
    except Exception as ee:
        logging.getLogger("ogc_edr_lib.util.geopandas").warning(
            ee
        )
        return None
