import glob
import os
import pathlib
import xarray as xr
import netCDF4 as nc
from command.command import Command
class CommandCombine2(Command):
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
            the_x = xr.open_dataset(f)
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
