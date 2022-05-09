import logging
from osgeo import ogr
import re


def get_coords_from_wkt(wktstr):
    theretdata = []
    try:
        thegeom = ogr.CreateGeometryFromWkt(wktstr)
        if thegeom.IsSimple():
            theretdata = thegeom.GetPoints()
        else:
            for k in range(thegeom.GetGeometryCount()):
                theretdata += [*thegeom.GetGeometryRef(k).GetPoints()]
        return theretdata
    except Exception as ee:
        logging.getLogger("ogrutil.get_coords_from_wkt").warning(ee)
        return theretdata


def get_polygon_from_wkt(wktstr):
    theretdata = None
    try:
        thegeom = ogr.CreateGeometryFromWkt(wktstr)
        if thegeom.GetGeometryName() == "POLYGON":
            return thegeom
        logging.getLogger("ogrutil.get_polygon_from_wkt").warning(
            "Incorrect geometry type. 'POLYGON' is expected. However, get - "
            + thegeom.GetGeometryName()
        )
        return None
    except Exception as ee:
        logging.getLogger("ogrutil.get_polygon_from_wkt").warning(ee)
        return theretdata


def get_coords_from_wkt_reformatting_zm(wktstr):
    """
        It parses line feature in wkt (including Z & M optional dimensions).
        Check if the geometry Is3D(), IsMeasured(), and separate M-Value from
        the original geometry to be used in shapely/geopandas which cannot
        handle M-value at all for now.
        :param wktstr: WKT string, e.g. LineStringM(...)

        :returns: (points, IsMeasured, Is3D, M-Values)
    """
    # pre-process the string by adding space between LineString and optional
    # dimension
    wktstr = re.sub("(?i) *(ZM|Z|M) *\\(", " \\1 (", wktstr)
    return get_coords_from_wkt(wktstr)


def get_vertexes_from_linestring_wkt(wktstr):
    """
        It parses line feature in wkt (including Z & M optional dimensions).
        Check if the geometry Is3D(), IsMeasured(), and separate M-Value from
        the original geometry to be used in shapely/geopandas which cannot
        handle M-value at all for now.
        :param wktstr: WKT string, e.g. LineStringM(...)

        :returns: (points, IsMeasured, Is3D, M-Values)
    """
    # pre-process the string by adding space between LineString and optional
    # dimension
    wktstr = re.sub("(?i)(LineString[ ]*)", "LineString ", wktstr)
    the_geom = ogr.CreateGeometryFromWkt(wktstr)
    the_ret_wkt = the_geom.ExportToWkt()
    the_is_3d = True if the_geom.Is3D() != 0 else False
    the_is_measured = True if the_geom.IsMeasured() != 0 else False
