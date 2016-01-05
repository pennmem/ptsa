__author__ = 'm'

import numpy as np

def get_axis_index(data_array, axis_name):

    axis_index_array = np.where(np.array(data_array.dims) == axis_name)
    if len(axis_index_array[0])>0:
        return  axis_index_array[0][0] # picking first index that corresponds to the dimension
    else:
        raise RuntimeError("Could not locate '%s' axis in your time series."
                           " Make sure to either label appropriate axis of your time series 'time' or specify"
                           "time axis explicitely as a non-negative integer '" %(axis_name) )
