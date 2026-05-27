from __future__ import annotations

from typing import TYPE_CHECKING, Hashable, Tuple

import traits.api

if TYPE_CHECKING:
    from ptsa.data.timeseries import TimeSeries

__all__ = ['BaseFilter']


class BaseFilter(traits.api.HasTraits):
    """Base class for constructing filters."""
    nontime_dims = traits.api.Tuple
    nontime_sizes = traits.api.Tuple

    def __init__(self) -> None:
        super(BaseFilter, self).__init__()

    def get_nontime_dims(self, timeseries: "TimeSeries") -> Tuple[Hashable, ...]:
        """Return a tuple of all dimensions that are not time.

        Returns
        -------
        Tuple[Hashable, ...]
            ``xarray.DataArray.dims`` is typed as ``Tuple[Hashable, ...]``;
            in practice PTSA always uses string dim names.

        """
        return tuple([d for d in timeseries.dims if d != 'time'])

    def get_nontime_sizes(self, timeseries: "TimeSeries") -> Tuple[int, ...]:
        """Return a tuple of all dimension sizes for dimensions other than
        time.

        Returns
        -------
        Tuple[int]

        """
        dims = self.get_nontime_dims(timeseries)
        return tuple([len(timeseries[dim]) for dim in dims])

    def filter(self, timeseries: "TimeSeries") -> "TimeSeries":
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
