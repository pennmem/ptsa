import numpy as np
import traits.api

from ptsa.data.timeseries import TimeSeries

__all__ = ['BaseFilter']


class BaseFilter(traits.api.HasTraits):
    """Base class for constructing filters.

    Parameters
    ----------
    timeseries : TimeSeries
        The :class:`TimeSeries` to filter.
    dtype : str or np.dtype or None
        When given, coerce the input to a valid numpy dtype. When ``None``,
        leave as the original dtype. Default: coerce to ``np.float64``.

    """
    timeseries = traits.api.Instance(TimeSeries)

    def __init__(self, timeseries, dtype=np.float64):
        super(BaseFilter, self).__init__()

        self.timeseries = timeseries

        if dtype is not None:
            self.timeseries.data = timeseries.data.astype(dtype)

        self.nontime_dims = tuple([d for d in self.timeseries.dims if d != 'time'])
        self.nontime_sizes = tuple([len(self.timeseries[d]) for d in self.nontime_dims])

    def filter(self):
        raise NotImplementedError
