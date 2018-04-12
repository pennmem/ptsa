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

    @abstractmethod
    def filter(self):
        pass
