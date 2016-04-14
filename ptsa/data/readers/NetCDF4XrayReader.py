__author__ = 'm'

import xray
import numpy as np
from ptsa.data.readers import BaseReader

class NetCDF4XrayReader(BaseReader):
    def __init__(self):
        pass
        self.writer_class_name = 'NetCDFXRayReader'
        self.writer_version = 1

    def read(self, filename):
        ds = xray.open_dataset(filename)

        if ds['__writerclass__'] != self.writer_class_name or ds['__version__'] != self.writer_version:
            print '\n\n*****WARNING*****: this reader may not be able to properly read dataset written with writer %s version:  %s \n\n' % (
            ds['__writerclass__'].values, ds['__version__'].values)

        array = xray.DataArray(ds['array'])

        # reconstructing axes
        for axis_name in ds['axis_names'].values:
            axis_array = self.reconstruct_axis(ds, str(axis_name))

            array[axis_name] = axis_array

        return array

    def reconstruct_axis(self, ds, axis_name):
        # axis_element_names = filter(lambda x : x.startswith('axis__'+axis_name), ds.dims)
        axis_identifier_str = '__axis__' + axis_name
        axis_element_names = filter(lambda dim_name: dim_name.startswith(axis_identifier_str), list(ds.dims))

        axis_size = len(ds[axis_element_names[0]].values)
        recarray_flag = len(axis_element_names) > 1
        axis_array = None

        if recarray_flag:

            axis_dtype = {'names': [], 'formats': []}

            for full_axis_element_name in axis_element_names:
                axis_element_name = full_axis_element_name.replace(axis_identifier_str + '__', '')
                axis_dtype['names'].append(axis_element_name)
                axis_dtype['formats'].append(str(ds[full_axis_element_name].dtype))

            # creating recarray
            axis_array = np.empty(axis_size, dtype=axis_dtype)

            # populating columns of the recarray
            for full_axis_element_name in axis_element_names:
                axis_element_name = full_axis_element_name.replace(axis_identifier_str + '__', '')
                axis_array[axis_element_name] = ds[full_axis_element_name].values
        else:
            axis_array = ds[axis_element_names[0]].values

        return axis_array
