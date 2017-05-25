__author__ = 'm'

import numpy as np
import xarray as xr
from scipy.signal import resample

from ptsa.data.TimeSeriesX import TimeSeriesX
from ptsa.data.common import TypeValTuple, PropertiedObject
from ptsa.data.filters import BaseFilter


class ResampleFilter(PropertiedObject, BaseFilter):
    """Resample Filter"""

    _descriptors = [
        TypeValTuple('time_series', TimeSeriesX, TimeSeriesX([0.0], dict(samplerate=1), dims=['time'])),
        TypeValTuple('resamplerate', float, -1.0),
        TypeValTuple('time_axis_index', int, -1),
        TypeValTuple('round_to_original_timepoints', bool, False),

    ]

    def ___syntax_helper(self):
        self.time_series = None
        self.resamplerate = None
        self.time_axis_index = None
        self.round_to_original_timepoints = None

    def __init__(self,**kwds):
        """

        :param kwds: allowed values are:
        -------------------------------------
        :param resamplerate - new sampling frequency
        :param time_series - TimeSeriesX object
        :param time_axis_index - index of the time axis
        :param round_to_original_timepoints  -  boolean flag indicating if timepoints from original time axis
        should be reused after proper rounding. Default setting is False
        -------------------------------------
        :return:

        """
        self.window = None
        # self.time_series = None
        self.init_attrs(kwds)

    def filter(self):
        """resamples time series

        :return:resampled time series with sampling frequency set to resamplerate

        """
        samplerate = float(self.time_series['samplerate'])

        time_axis_length = np.squeeze(self.time_series.coords['time'].shape)
        new_length = int(np.round(time_axis_length*self.resamplerate/samplerate))

        print(new_length)

        if self.time_axis_index<0:
            self.time_axis_index = self.time_series.get_axis_num('time')

        time_axis = self.time_series.coords[ self.time_series.dims[self.time_axis_index] ]

        try:
            time_axis_data = time_axis.data['time'] # time axis can be recarray with one of the arrays being time
        except (KeyError ,IndexError) as excp:
            # if we get here then most likely time axis is ndarray of floats
            time_axis_data = time_axis.data

        time_idx_array = np.arange(len(time_axis))


        if self.round_to_original_timepoints:
            filtered_array, new_time_idx_array = resample(self.time_series.data,
                                             new_length, t=time_idx_array,
                                             axis=self.time_axis_index, window=self.window)

            # print new_time_axis

            new_time_idx_array = np.rint(new_time_idx_array).astype(np.int)

            new_time_axis = time_axis[new_time_idx_array]

        else:
            filtered_array, new_time_axis = resample(self.time_series.data,
                                             new_length, t=time_axis_data,
                                             axis=self.time_axis_index, window=self.window)

        coords = []
        for i, dim_name in enumerate(self.time_series.dims):
            if i != self.time_axis_index:
                coords.append(self.time_series.coords[dim_name].copy())
            else:
                coords.append((dim_name,new_time_axis))

        filtered_time_series = xr.DataArray(filtered_array, coords=coords)
        filtered_time_series['samplerate'] = self.resamplerate
        return TimeSeriesX(filtered_time_series)
