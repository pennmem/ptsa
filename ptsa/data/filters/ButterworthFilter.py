__author__ = 'm'

from ptsa.data.common.xr import DataArray
from ptsa.data.common import TypeValTuple, PropertiedObject
from ptsa.data.TimeSeriesX import TimeSeriesX
from ptsa.data.common import get_axis_index


class ButterworthFiler(PropertiedObject):
    '''
    Applies Butterworth filter to a time series
    '''
    _descriptors = [
        TypeValTuple('time_series', TimeSeriesX, TimeSeriesX([0.0], dims=['time'])),
        TypeValTuple('order', int, 4),
        TypeValTuple('freq_range', list, [58, 62]),
        TypeValTuple('filt_type', str, 'stop'),
    ]

    def __init__(self, **kwds):
        '''
        Constructor
        :param kwds:allowed values are:
        -------------------------------------
        :param time_series  -  TimeSeriesX object
        :param order -  Butterworth filter order
        :param freq_range -  array of frequencies [min_freq, max_freq] to filter out
        :return: None
        '''
        self.init_attrs(kwds)

    def filter(self):
        '''
        Applies Butterwoth filter to input time series and returns filtered TimeSeriesX object
        :return: TimeSeriesX object
        '''

        from ptsa.filt import buttfilt

        time_axis_index = get_axis_index(self.time_series, axis_name='time')
        filtered_array = buttfilt(self.time_series,
                                  self.freq_range, self.time_series['samplerate'].data, self.filt_type,
                                  self.order, axis=time_axis_index)

        coords_dict = {coord_name: DataArray(coord.copy()) for coord_name, coord in self.time_series.coords.items()}
        coords_dict['samplerate'] = self.time_series['samplerate']
        dims = [dim_name for dim_name in self.time_series.dims]
        filtered_time_series = TimeSeriesX(
            filtered_array,
            dims=dims,
            coords=coords_dict
        )

        # filtered_time_series.attrs['samplerate'] = self.time_series.attrs['samplerate']
        filtered_time_series.attrs['samplerate'] = self.time_series['samplerate']
        filtered_time_series = TimeSeriesX(filtered_time_series)

        return filtered_time_series
