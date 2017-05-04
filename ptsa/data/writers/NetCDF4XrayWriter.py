__author__ = 'm'

import xarray as xr
import numpy as np
from ptsa.data.writers import BaseWriter


class NetCDF4XrayWriter(BaseWriter):
    def __init__(self, array):
        self.array = array
        self._writer_version = 1

    def write(self, filename):

        dim_names_appended = map(lambda x: x, self.array.dims)

        values_dict = {'array': (tuple(dim_names_appended), self.array.values)}

        # axes
        coords_dict = {}
        coords_dict = {'axis_names': list(self.array.dims), '__version__': self._writer_version, '__writerclass__':self.__class__.__name__}

        for dim_name in self.array.dims:
            if self.array[dim_name].dtype.fields is None:  # indicates simple type, not a recarray
                coords_dict['__axis__' + dim_name] = self.array[dim_name].values
            else:
                for field, dtype_tuple in list(self.array[dim_name].dtype.fields.items()):
                    if self.array[dim_name].values[field].dtype.char == 'O':
                        print('WE ARE NOT STORING VARIABLES OF TYPE=OBJECT IN THIS WRITER ')
                        continue
                    dtype = dtype_tuple[0]
                    coords_dict['__axis__' + dim_name + '__' + field] = self.array[dim_name].values[field]

        ds = xr.Dataset(values_dict, coords=coords_dict)

        ds.to_netcdf(filename)
