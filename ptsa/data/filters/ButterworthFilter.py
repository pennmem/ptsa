__author__ = 'm'

import numpy as np
import xray
from ptsa.data.common import TypeValTuple, PropertiedObject
from ptsa.data.TimeSeriesXray import TimeSeriesXray

class ButterworthFiler(PropertiedObject):
    _descriptors = [
        TypeValTuple('samplerate', float, -1.0),
        TypeValTuple('order', int, 4),
        TypeValTuple('freq_range', list, [58,62]),
        TypeValTuple('filt_type', str, 'stop'),
    ]


    def __init__(self,**kwds):

        self.time_series = None
        self.time_axis = -1

        for option_name, val in kwds.items():

            try:
                attr = getattr(self,option_name)
                setattr(self,option_name,val)
            except AttributeError:
                print 'Option: '+ option_name+' is not allowed'

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


        filtered_time_series = xray.DataArray(
            filtered_array,
            coords = [xray.DataArray(coord.copy()) for coord_name, coord in self.time_series.coords.items() ]
        )

        filtered_time_series.attrs['samplerate'] = self.time_series.attrs['samplerate']

        filtered_time_series = TimeSeriesXray(filtered_time_series)

        return filtered_time_series



