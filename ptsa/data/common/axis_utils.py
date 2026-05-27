__author__ = 'm'

from typing import Any

import numpy as np


def get_axis_index(data_array: Any, axis_name: str) -> int:

    axis_index_array = np.where(np.array(data_array.dims) == axis_name)
    if len(axis_index_array[0]) > 0:
        # picking first index that corresponds to the dimension
        return int(axis_index_array[0][0])
    else:
        raise RuntimeError("Could not locate '%s' axis in your time series."
                           " Make sure to either label appropriate axis of your time series 'time' or specify"
                           "time axis explicitely as a non-negative integer '" % (axis_name))
