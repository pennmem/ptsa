__author__ = 'm'
import traits.api
from .. import TimeSeriesX
from abc import abstractmethod

__all__ = ['BaseFilter']


class BaseFilter(traits.api.HasTraits):
    time_series = traits.api.Instance(TimeSeriesX)

    def __init__(self,time_series):
        super(BaseFilter, self).__init__()
        self.time_series = time_series

    @abstractmethod
    def filter(self):
        pass
