import numpy as np
import traits.api

from ptsa.data.timeseries import TimeSeries

__all__ = ['BaseFilter']


class BaseFilter(traits.api.HasTraits):
    """Base class for constructing filters.

    Parameters
    ----------
    timeseries : TimeSeries or None
        The :class:`TimeSeries` to filter (None to set later).
    args
        Arguments that get passed on to :meth:`initialize`.

    Keyword arguments
    -----------------
    dtype : str or np.dtype or None
        When given, coerce the input to a valid numpy dtype. When ``None``,
        leave as the original dtype. Default: coerce to ``np.float64``.
    kwargs
        Additional keyword arguments that get passed on to :meth:`initialize`.

    Notes
    -----
    Do not override the :meth:`__init__` method. Instead, perform
    filter-specific initialization in the :meth:`initialize` method.

    """
    _timeseries = traits.api.Instance(TimeSeries)

    def __init__(self, timeseries, *args, **kwargs):
        super(BaseFilter, self).__init__()

        self._dtype = kwargs.pop("dtype", np.float64)
        self.timeseries = timeseries

        self.nontime_dims = tuple([d for d in self.timeseries.dims if d != 'time'])
        self.nontime_sizes = tuple([len(self.timeseries[d]) for d in self.nontime_dims])

        self.initialize(*args, **kwargs)

    def initialize(self, *args, **kwargs):
        """Override this method to include additional filter-specific
        initialization steps.

        """

    @property
    def timeseries(self):
        return self._timeseries

    @timeseries.setter
    def timeseries(self, ts):
        """Set the time series data and coerce types if neccessary."""
        if ts is None:
            self._timeseries = None
            return

        self._timeseries = ts
        if self._dtype is not None:
            self._timeseries.data = ts.data.astype(self._dtype)

    def filter(self):
        raise NotImplementedError
