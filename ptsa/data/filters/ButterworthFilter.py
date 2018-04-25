from numpy import asarray
from xarray import DataArray
from ptsa.data.timeseries import TimeSeries
from ptsa.data.common import get_axis_index
from ptsa.filt import buttfilt
from ptsa.data.filters import BaseFilter
import traits.api

__all__ = ['ButterworthFilter']

class ButterworthFilter(BaseFilter):
    """Applies Butterworth filter to a time series.

    Keyword Arguments
    -----------------

    time_series
         TimeSeries object
    order
         Butterworth filter order
    freq_range: list-like
       Array [min_freq, max_freq] describing the filter range

    """
    order=traits.api.Int
    freq_range = traits.api.List(maxlen=2)
    filt_type=traits.api.Str


    def __init__(self, time_series,freq_range,order=4,filt_type='stop'):
        super(ButterworthFilter, self).__init__(time_series)

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
        time_axis_index = get_axis_index(self.time_series, axis_name='time')
        filtered_array = buttfilt(self.time_series,
                                  self.freq_range, float(self.time_series['samplerate']), self.filt_type,
                                  self.order, axis=time_axis_index)

        coords_dict = {coord_name: DataArray(coord.copy()) for coord_name, coord in list(self.time_series.coords.items())}
        coords_dict['samplerate'] = self.time_series['samplerate']
        dims = [dim_name for dim_name in self.time_series.dims]
        filtered_time_series = TimeSeries(
            filtered_array,
            dims=dims,
            coords=coords_dict
        )

        # filtered_time_series = TimeSeries(filtered_time_series)
        filtered_time_series.attrs = self.time_series.attrs.copy()
        return filtered_time_series



from scipy.signal import butter, lfilter


def butter_bandpass(lowcut, highcut, fs, order=4):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    # b, a = butter(order, [low, high], btype='band')
    b, a = butter(order, [low, high], btype='stop')
    return b, a


def butter_bandpass_filter(data, lowcut, highcut, fs, order=4):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = lfilter(b, a, data)
    return y
