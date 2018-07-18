import traits.api

from ptsa.data.timeseries import TimeSeries

__all__ = ['BaseFilter']


class BaseFilter(traits.api.HasTraits):
    timeseries = traits.api.Instance(TimeSeries)

    def __init__(self, timeseries):
        super(BaseFilter, self).__init__()
        self.timeseries = timeseries
        self.nontime_dims = tuple([d for d in self.timeseries.dims if d != 'time'])
        self.nontime_sizes = tuple([len(self.timeseries[d]) for d in self.nontime_dims])

    def filter(self):
        raise NotImplementedError
