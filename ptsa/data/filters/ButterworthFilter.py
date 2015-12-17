__author__ = 'm'

import numpy as np
import xray

class ButterworthFiler(object):
    def __init__(self):
        self._filt_type = 'stop'
        self._order = 4
        self._freq_range = [58, 62]

        self.time_series = None
        self._samplerate = None
        self.time_axis = -1

    @property
    def samplerate(self):
        return self._samplerate

    @samplerate.setter
    def samplerate(self, val):
        self._samplerate = val


    @property
    def freq_range(self):
        return self._freq_range

    @freq_range.setter
    def freq_range(self, val):
        self._freq_range = val

    @property
    def filt_type(self):
        return self._filt_type

    @filt_type.setter
    def filt_type(self, val):
        self._filt_type = val

    @property
    def order(self):
        return self._order

    @order.setter
    def order(self, val):
        self._order = val

    def set_input(self, time_series):
        self.time_series = time_series

    def get_output(self):
        return self.filtered_time_series

    def filter(self):

        from ptsa.filt  import buttfilt

        # find index  of the  axis called 'time'
        if self.time_axis<0:

            time_index_array = np.where(np.array(self.time_series.dims) == 'time')
            if len(time_index_array)>0:
                self.time_axis =time_index_array[0] # picking first index that corresponds to the dimension
            else:
                raise RuntimeError("Could not locate 'time' axis in your time series."
                                   " Make sure to either label appropriate axis of your time series 'time' or specify"
                                   "time axis explicitely as a non-negative integer '")

        filtered_array = buttfilt(self.time_series,
                                       self.freq_range, self.samplerate, self.filt_type,
                                       self.order,axis=self.time_axis)


        self.filtered_time_series = xray.DataArray(
            filtered_array,
            coords = [xray.DataArray(coord.copy()) for coord_name, coord in self.time_series.coords.items() ]
        )


        # l = [xray.DataArray(coord.copy()) for coord_name, coord in self.time_series.coords.items() ]

        return self.filtered_time_series

        # attrs = self._attrs.copy()
        # for k in self._required_attrs.keys():
        #     attrs.pop(k,None)
        # return TimeSeries(filtered_array,self.tdim, self.samplerate,
        #                   dims=self.dims.copy(), **attrs)