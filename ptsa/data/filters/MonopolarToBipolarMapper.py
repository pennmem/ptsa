__author__ = 'm'

import numpy as np
from ptsa.data.timeseries import TimeSeries
# from memory_profiler import profile
import time

from ptsa.data.filters import BaseFilter
import traits.api


class MonopolarToBipolarMapper(BaseFilter):
    """Object that takes as an input time series for monopolar electrodes
    and an array of bipolar pairs and outputs a TimeSeries object
    where the data is a difference between time series corresponding
    to different electrodes as specified by bipolar pairs.

    Parameters
    ----------
    time_series: TimeSeries
        The time series to filter
    bipolar_pairs: array-like
        An array of bipolar electrode pairs. Must be either a 1-D
        structured array where dtypes has two fields corresponding to
        chan_names or a 2-D container where the first dimension must
        be length 2 corresponding to the two channels in the bipolar
        pair

    Keyword Arguments
    -----------------
    channels_dim: str, optional
        Name of the channels dimension
    chan_names: container, optional
        container with two elements corresponding to the names of the
        two channels in the bipolar pair

    """

    # bipolar_pairs = traits.api.Array(dtype=[('ch0', '|S3'), ('ch1', '|S3')])

    def __init__(self, time_series, bipolar_pairs, channels_dim='channels',
                 chan_names=['ch0', 'ch1']):
        super(MonopolarToBipolarMapper, self).__init__(time_series)
        if (len(np.shape(bipolar_pairs)) == 2):
            if np.shape(biolar_pairs)[0] == 2:
                self.bipolar_pairs = np.core.records.fromarrays(
                    tst, names=chan_names)
            else:
                raise ValueError(
                    'bipolar_pair must be either a 1-D structured array where'
                    'dtypes has two fields corresponding to chan_names or a 2-D'
                    'container where the first dimension must be length 2'
                    'corresponding to the two channels in the bipolar pair.'
                    'Input was 2-D with the following dimensions: '+
                    str(np.shape(bipolar_pairs)))
        else:
            self.bipolar_pairs = bipolar_pairs
        self.channels_dim = channels_dim
        self.chan_names = chan_names

    def filter(self):
        """Apply the constructed filter.

        Returns
        -------
        A TimeSeries object.

        """
        channel_axis = self.time_series[self.channels_dim]

        ch0 = self.bipolar_pairs[self.chan_names[0]]
        ch1 = self.bipolar_pairs[self.chan_names[1]]

        sel0 = channel_axis.loc[ch0]
        sel1 = channel_axis.loc[ch1]

        ts0 = self.time_series.loc[{self.channels_dim: sel0}]
        ts1 = self.time_series.loc[{self.channels_dim: sel1}]

        dims_bp = list(self.time_series.dims)

        coords_bp = {coord_name:coord for coord_name, coord in list(self.time_series.coords.items())}
        coords_bp[self.channels_dim] = self.bipolar_pairs

        ts = TimeSeries(data=ts0.values - ts1.values, dims=dims_bp, coords=coords_bp)
        ts['samplerate'] = self.time_series['samplerate']

        ts.attrs = self.time_series.attrs.copy()
        return ts


# # @profile
# def main_fcn():
#     e_path = '/Users/m/data/events/RAM_FR1/R1060M_events.mat'

#     from ptsa.data.readers import BaseEventReader

#     base_e_reader = BaseEventReader(filename=e_path, eliminate_events_with_no_eeg=True)

#     base_events = base_e_reader.read()



#     base_events = base_events[base_events.type == 'WORD']

#     # selecting only one session
#     base_events = base_events[base_events.eegfile == base_events[0].eegfile]

#     from ptsa.data.readers.tal import TalReader

#     tal_path = '/Users/m/data/eeg/R1060M/tal/R1060M_talLocs_database_bipol.mat'
#     tal_reader = TalReader(filename=tal_path)
#     monopolar_channels = tal_reader.get_monopolar_channels()
#     bipolar_pairs = tal_reader.get_bipolar_pairs()

#     print('bipolar_pairs=', bipolar_pairs)


#     from ptsa.data.readers.EEGReader import EEGReader

#     sessions = np.unique(base_events.session)
#     dataroot = base_events[0].eegfile

#     session_reader = EEGReader(session_dataroot=dataroot, channels=monopolar_channels)
#     session_eegs = session_reader.read()

#     m2b = MonopolarToBipolarMapper(time_series=session_eegs, bipolar_pairs=bipolar_pairs)
#     session_bp_eegs = m2b.filter()





#     time_series_reader = EEGReader(events=base_events, channels=monopolar_channels, start_time=0.0,
#                                              end_time=1.6, buffer_time=1.0)


#     base_eegs = time_series_reader.read()


#     m2b = MonopolarToBipolarMapper(time_series=base_eegs, bipolar_pairs=bipolar_pairs)
#     ts_filtered = m2b.filter()

#     del base_eegs
#     del time_series_reader

#     print()

#     pass

# # @profile
# def new_fcn():

#     time.sleep(20)
#     print(new_fcn)

# if __name__ == '__main__':
#     main_fcn()
#     new_fcn()
