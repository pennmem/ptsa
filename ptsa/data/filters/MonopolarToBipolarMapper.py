__author__ = 'm'

import numpy as np
from ptsa.data.timeseries import TimeSeries
# from memory_profiler import profile
import time

from ptsa.data.filters import BaseFilter
import traits.api


class MonopolarToBipolarMapper(BaseFilter):
    """
    Object that takes as an input time series for monopolar electrodes and an array of bipolar pairs and outputs
    Time series where 'channels' axis is replaced by 'bipolar_pairs' axis and the time series data is a difference
    between time series corresponding to different electrodes as specified by bipolar pairs
    """

    bipolar_pairs = traits.api.Array(dtype=[('ch0', '|S3'), ('ch1', '|S3')])

    def __init__(self, time_series,bipolar_pairs):
        """
        Constructor:

        :param kwds:allowed values are:
        -------------------------------------
        :param time_series  -  TimeSeries object with eeg session data and 'channels as one of the axes'
        :param bipolar_pairs {np.recarray} - an array of bipolar electrode pairs

        :return: None
        """
        super(MonopolarToBipolarMapper, self).__init__(time_series)
        self.bipolar_pairs = bipolar_pairs


    def filter(self):
        """
        Turns time series for monopolar electrodes into time series where where 'channels' axis is replaced by
        'bipolar_pairs' axis and the time series data is a difference
        between time series corresponding to different electrodes as specified by bipolar pairs

        :return: TimeSeries object
        """

        channel_axis = self.time_series['channels']

        ch0 = self.bipolar_pairs['ch0']
        ch1 = self.bipolar_pairs['ch1']

        sel0 = channel_axis.loc[ch0]
        sel1 = channel_axis.loc[ch1]

        ts0 = self.time_series.loc[dict(channels=sel0)]
        ts1 = self.time_series.loc[dict(channels=sel1)]

        dims_bp = list(self.time_series.dims)
        channels_idx = dims_bp.index('channels')
        dims_bp[channels_idx] = 'bipolar_pairs'

        # coords_bp = [self.time_series[dim_name].copy() for dim_name in self.time_series.dims]
        # coords_bp[channels_idx] = self.bipolar_pairs

        coords_bp = {coord_name:coord for coord_name, coord in list(self.time_series.coords.items())}
        del coords_bp['channels']
        coords_bp['bipolar_pairs'] = self.bipolar_pairs


        ts = TimeSeries(data=ts0.values - ts1.values, dims=dims_bp, coords=coords_bp)
        ts['samplerate'] = self.time_series['samplerate']

        ts.attrs = self.time_series.attrs.copy()
        return ts
