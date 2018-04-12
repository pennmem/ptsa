import warnings
from ptsa.data.timeseries import *

with warnings.catch_warnings():
    warnings.simplefilter('always')
    warnings.warn("importing from ptsa.data.TimeSeriesX is deprecated; import from ptsa.data.timeseries instead",
                  DeprecationWarning)
