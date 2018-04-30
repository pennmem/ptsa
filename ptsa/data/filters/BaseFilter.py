__author__ = 'm'
import traits.api
from ptsa.data.timeseries import TimeSeries
from abc import abstractmethod

__all__ = ['BaseFilter']


class BaseFilter(traits.api.HasTraits):
    time_series = traits.api.Instance(TimeSeries)

    def __init__(self,time_series):
        super(BaseFilter, self).__init__()
        self.time_series = time_series
        self.nontime_dims = tuple([d for d in self.time_series.dims if d !='time'])
        self.nontime_sizes = tuple([len(self.time_series[d]) for d in self.nontime_dims])

    @abstractmethod
    def filter(self):
        pass
