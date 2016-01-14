__author__ = 'm'


import xray
import numpy as np

class NetCDF4XrayReader(object):
    def __init__(self):
        pass

    def read(self,filename):
        ds = xray.open_dataset(filename)

        array = xray.DataArray(ds['array'])
        print array
        print ds

        #reconstructing axes
        for axis_name in ds['axis_names'].values:
            axis_array = self.reconstruct_axis(ds,str(axis_name))

            array[axis_name] = axis_array

        return array


    def reconstruct_axis(self,ds,axis_name):
        # axis_element_names = filter(lambda x : x.startswith('axis__'+axis_name), ds.dims)
        axis_identifier_str = 'axis__'+axis_name
        axis_element_names = filter(lambda dim_name : dim_name.startswith(axis_identifier_str), list(ds.dims))

        axis_size = len(ds[axis_element_names[0]].values)
        recarray_flag = len(axis_element_names)>1
        axis_array = None

        if recarray_flag:
            print axis_element_names
            axis_dtype={'names':[],'formats':[]}

            for full_axis_element_name in axis_element_names:
                axis_element_name = full_axis_element_name.replace(axis_identifier_str+'__','')
                print ds[full_axis_element_name].values
                print ds[full_axis_element_name].dtype
                axis_dtype['names'].append(axis_element_name)
                axis_dtype['formats'].append(str(ds[full_axis_element_name].dtype))

            # creating recarray
            axis_array = np.empty(axis_size, dtype=axis_dtype)

            # populating columns of the recarray
            for full_axis_element_name in axis_element_names:
                axis_element_name = full_axis_element_name.replace(axis_identifier_str+'__','')
                axis_array[axis_element_name] = ds[full_axis_element_name].values

        else:
            axis_array = ds[axis_element_names[0]].values

        print axis_array
        print axis_array.dtype
        return axis_array