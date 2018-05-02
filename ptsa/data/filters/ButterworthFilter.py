from numpy import asarray
from xarray import DataArray
from ptsa.filt import buttfilt
from ptsa.data.timeseries import TimeSeries
from ptsa.data.common import get_axis_index
from ptsa.data.filters import BaseFilter
import traits.api

__all__ = ['ButterworthFilter']

class ButterworthFilter(BaseFilter):
    """Applies Butterworth filter to a time series.

    Keyword Arguments
    -----------------

    timeseries
         TimeSeries object
    order
         Butterworth filter order
    freq_range: list-like
       Array [min_freq, max_freq] describing the filter range

    """
    order=traits.api.Int
    freq_range = traits.api.List(maxlen=2)
    filt_type=traits.api.Str


    def __init__(self, timeseries,freq_range,order=4,filt_type='stop'):
        super(ButterworthFilter, self).__init__(timeseries)

        self.freq_range = freq_range
        self.order = order
        self.filt_type = filt_type

    def filter(self):
        """
        Applies Butterwoth filter to input time series and returns filtered TimeSeriesX object

        Returns
        -------
        filtered: TimeSeries
            The filtered time series

        """
        time_axis_index = get_axis_index(self.timeseries, axis_name='time')
        filtered_array = buttfilt(self.timeseries,
                                  self.freq_range, float(self.timeseries['samplerate']), self.filt_type,
                                  self.order, axis=time_axis_index)

        coords_dict = {coord_name: DataArray(coord.copy()) for coord_name, coord in list(self.timeseries.coords.items())}
        coords_dict['samplerate'] = self.timeseries['samplerate']
        dims = [dim_name for dim_name in self.timeseries.dims]
        filtered_timeseries = TimeSeries(
            filtered_array,
            dims=dims,
            coords=coords_dict
        )

        # filtered_timeseries = TimeSeries(filtered_timeseries)
        filtered_timeseries.attrs = self.timeseries.attrs.copy()
