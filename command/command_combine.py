import glob
import os
import pathlib
import xarray as xr
import netCDF4 as nc
from command.command import Command
class CommandCombine(Command):
    def __init__(self, args):
        self.args = args

    def execute(self):
        the_files = glob.glob(self.args.list)
        the_path = self.args.directory
        the_varstr = self.args.variables
        the_variables = None
        if the_varstr:
            the_variables = the_varstr.split(",")
        the_combined = None
        for f in the_files:
            the_x = self._open_hdf5file_as_xarray(
                f, "Grid"
            )
            if the_combined:
                if the_variables:
                    the_x0 = the_x[the_variables]
                    the_combined = xr.combine_by_coords(
                        [the_combined, the_x0])
                else:
                    the_combined = xr.combine_by_coords(
                        [the_combined, the_x])
            else:
                if the_variables:
                    the_x0 = the_x[the_variables]
                    the_combined = the_x0
                else:
                    the_combined = the_x
        if the_combined:
            the_combined.to_netcdf(path=the_path)

    def _open_hdf5file_as_xarray(
            self, sfile, sgroup):
        try:
            if not sgroup:
                thedata = xr.open_dataset(sfile)
                return thedata
            ncf = nc.Dataset(sfile, diskless=True, persist=False)
            nch = ncf.groups.get(sgroup)
            thedata = xr.open_dataset(xr.backends.NetCDF4DataStore(nch))
            return thedata
        except Exception as err:
            Logger.warning("In _open_hdf5file_as_xarray - error")
            Logger.warning(err)
            return None
