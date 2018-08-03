import traits.api

from ptsa.data.timeseries import TimeSeries

__all__ = ['BaseFilter']


class BaseFilter(traits.api.HasTraits):
    """Base class for constructing filters."""
    nontime_dims = traits.api.Tuple
    nontime_sizes = traits.api.Tuple

    def __init__(self):
        super(BaseFilter, self).__init__()

    def get_nontime_dims(self, timeseries):
        """Return a tuple of all dimensions that are not time.

        Returns
        -------
        Tuple[str]

        """
        return tuple([d for d in timeseries.dims if d != 'time'])

    def get_nontime_sizes(self, timeseries):
        """Return a tuple of all dimension sizes for dimensions other than
        time.

        Returns
        -------
        Tuple[int]

        """
        dims = self.get_nontime_dims(timeseries)
        return tuple([len(timeseries[dim]) for dim in dims])

    def filter(self, timeseries):
        """Apply the filter.

        Parameters
        ----------
        timeseries : TimeSeries

        Notes
        -----
        Some filters may require certain numpy datatypes to work. To coerce to
        the proper datatype, use :meth:`TimeSeries.coerce_to` when implementing
        this method.

        """
        raise NotImplementedError

