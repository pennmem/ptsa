from __future__ import annotations

from typing import TYPE_CHECKING, Sequence

import traits.api

from ptsa.filt import buttfilt
from ptsa.data.common import get_axis_index
from ptsa.data.filters import BaseFilter

if TYPE_CHECKING:
    from ptsa.data.timeseries import TimeSeries

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

    def __init__(
        self,
        freq_range: Sequence[float],
        order: int = 4,
        filt_type: str = "stop",
    ) -> None:
        super().__init__()
        self.freq_range = freq_range
        self.order = order
        self.filt_type = filt_type

    def filter(self, timeseries: "TimeSeries") -> "TimeSeries":
        """
        Applies Butterwoth filter to input time series and returns filtered
        :class:`TimeSeries` object.

        Returns
        -------
        filtered: TimeSeries
            The filtered time series

        """
        time_axis_index = get_axis_index(timeseries, axis_name='time')
        # `self.filt_type` and `self.order` are traits descriptors;
        # pyright sees the class type rather than the runtime-coerced
        # value (which is always str/int). Narrow ignores keep the
        # type-checker quiet without changing behavior.
        filtered_array = buttfilt(
            timeseries.values,
            self.freq_range,
            float(timeseries['samplerate']),
            self.filt_type,  # pyright: ignore[reportArgumentType]
            self.order,      # pyright: ignore[reportArgumentType]
            axis=time_axis_index,
        )

        filtered_timeseries = timeseries.copy(data=filtered_array)
        return filtered_timeseries
