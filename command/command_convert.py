import glob
import os
import pathlib
import xarray as xr
import netCDF4 as nc
from command.command import Command
class CommandConvert(Command):
    def __init__(self, args):
        self.args = args

    def execute(self):
        the_files = glob.glob(self.args.list)
        the_dir = self.args.directory
        the_varstr = self.args.variables
        the_variables = None
        if the_varstr:
            the_variables = the_varstr.split(",")
        for f in the_files:
            the_x = self._open_hdf5file_as_xarray(
                f, "Grid"
            )
            the_path = os.path.join(the_dir, pathlib.Path(f).stem+".nc")
            if the_variables:
                the_x0 = the_x[the_variables]
                the_x0.to_netcdf(path=the_path)
            else:
                the_x.to_netcdf(path=the_path)

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
