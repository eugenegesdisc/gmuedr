import logging
from osgeo import ogr


def get_coords_from_wkt(wktstr):
    theretdata = []
    try:
        thegeom = ogr.CreateGeometryFromWkt(wktstr)
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
