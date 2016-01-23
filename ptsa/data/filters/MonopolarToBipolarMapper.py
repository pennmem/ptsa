__author__ = 'm'


import numpy as np
import xray
from ptsa.data.common import TypeValTuple, PropertiedObject, get_axis_index
from ptsa.data.TimeSeriesXray import TimeSeriesXray


class MonopolarToBipolarMapper(PropertiedObject):
    _descriptors = [
        TypeValTuple('bipolar_pairs', np.recarray, np.recarray((0,), dtype=[('ch0', '|S3'), ('ch1', '|S3')])),


    ]

    def __init__(self, time_series, **kwds):

        self.time_series = time_series

        self.init_attrs(kwds)

    def filter(self):

        # a = np.arange(20)*2
        #
        # template = [2,4,6,6,8,2,4]
        #
        # sorter = np.argsort(a)
        # idx = sorter[np.searchsorted(a, template, sorter=sorter)]


        # idx = np.where(a == 6)



        #
        # print ch0
        #
        # print ch1
        channel_axis=self.time_series['channels']

        ch0 = self.bipolar_pairs['ch0']
        ch1 = self.bipolar_pairs['ch1']

        sel0 = channel_axis.loc[ch0]
        sel1 = channel_axis.loc[ch1]

        ts0 = self.time_series.loc[dict(channels=sel0)]
        ts1 = self.time_series.loc[dict(channels=sel1)]


        dims_bp = list(self.time_series.dims)
        channels_idx = dims_bp.index('channels')
        dims_bp[channels_idx] = 'bipolar_pairs'

        coords_bp = [self.time_series[dim_name].copy() for dim_name in self.time_series.dims]
        coords_bp[channels_idx] = self.bipolar_pairs

        ts = xray.DataArray(data=ts0.values-ts1.values,
                            dims=dims_bp,
                            coords=coords_bp)

        ts.attrs = self.time_series.attrs.copy()

        return TimeSeriesXray(data=ts)







if __name__=='__main__':
    e_path = '/Users/m/data/events/RAM_FR1/R1060M_events.mat'

    from ptsa.data.readers import BaseEventReader

    base_e_reader = BaseEventReader(event_file=e_path, eliminate_events_with_no_eeg=True, use_ptsa_events_class=False)

    base_e_reader.read()

    base_events = base_e_reader.get_output()

    base_events = base_events[base_events.type == 'WORD']

    # selecting only one session
    base_events = base_events[base_events.eegfile == base_events[0].eegfile]

    from ptsa.data.readers.TalReader import TalReader
    tal_path = '/Users/m/data/eeg/R1060M/tal/R1060M_talLocs_database_bipol.mat'
    tal_reader = TalReader(tal_filename=tal_path)
    monopolar_channels = tal_reader.get_monopolar_channels()
    bipolar_pairs = tal_reader.get_bipolar_pairs()

    print 'bipolar_pairs=', bipolar_pairs

    from ptsa.data.readers.TimeSeriesEEGReader import TimeSeriesEEGReader

    time_series_reader = TimeSeriesEEGReader(events=base_events, start_time=0.0,
                                             end_time=1.6, buffer_time=1.0, keep_buffer=True)

    base_eegs = time_series_reader.read(channels=monopolar_channels)

    m2b = MonopolarToBipolarMapper(time_series=base_eegs,bipolar_pairs=bipolar_pairs)
    m2b.filter()
    pass



