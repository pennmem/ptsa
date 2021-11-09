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

    .. versionchanged:: 2.0

        Parameter "time_series" was renamed to "timeseries".

    """
    order = traits.api.Int
    freq_range = traits.api.CList(maxlen=2)
    filt_type = traits.api.Str

    def __init__(self, freq_range, order=4, filt_type="stop"):
        super().__init__()
        self.freq_range = freq_range
        self.order = order
        self.filt_type = filt_type

    def filter(self, timeseries):
        """
        Applies Butterwoth filter to input time series and returns filtered
        :class:`TimeSeries` object.

        Returns
        -------
        filtered: TimeSeries
            The filtered time series

        """
        time_axis_index = get_axis_index(timeseries, axis_name='time')
        filtered_array = buttfilt(timeseries.data,
                                  self.freq_range, float(timeseries['samplerate']), self.filt_type,
                                  self.order, axis=time_axis_index)

        timeseries.data = filtered_array
        return timeseries
