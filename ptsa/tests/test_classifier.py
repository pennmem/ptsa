__author__ = 'm'

import numpy as np
from numpy.testing import *
import unittest
from ptsa.data.readers import BaseEventReader
from ptsa.data.readers.EEGReader import EEGReader
from ptsa.data.filters.ButterworthFilter import ButterworthFilter
from ptsa.data.filters.ResampleFilter import ResampleFilter
from ptsa.data.filters.MorletWaveletFilter import MorletWaveletFilter
from ptsa.data.readers.TalReader import TalReader
from ptsa.data.readers import EEGReader
from ptsa.data.filters import EventDataChopper
from ptsa.data.filters import MonopolarToBipolarMapper
#
# class test_classifier(unittest.TestCase):
#     def setUp(self):
#         self.e_path = '/Users/m/data/events/RAM_FR1/R1060M_math.mat'
#         # ---------------- NEW STYLE PTSA -------------------
#         base_e_reader = BaseEventReader(filename=self.e_path, eliminate_events_with_no_eeg=True)
#
#         self.base_events = base_e_reader.read()
#         print
#
#
#     def test_math_event_read(self):
#
#
#
#
#         # sess_pow_mat_post[ev,i,:] = np.nanmean(pow_ev_stripped, axis=1)
#
#         print

class test_classifier(unittest.TestCase):
    def setUp(self):
        self.e_path = '/Users/m/data/events/RAM_FR1/R1060M_events.mat'
        tal_path = '/Users/m/data/eeg/R1060M/tal/R1060M_talLocs_database_bipol.mat'

        # ---------------- NEW STYLE PTSA -------------------
        base_e_reader = BaseEventReader(filename=self.e_path, eliminate_events_with_no_eeg=True)

        self.base_events = base_e_reader.read()



        tal_reader = TalReader(filename=tal_path)
        self.monopolar_channels = tal_reader.get_monopolar_channels()
        self.bipolar_pairs = tal_reader.get_bipolar_pairs()


        self.base_events = self.base_events[self.base_events.type == 'WORD']

        # retaining first session
        dataroot = self.base_events[0].eegfile
        self.base_events = self.base_events[self.base_events.eegfile == dataroot]

        eeg_reader = EEGReader(events=self.base_events, channels=self.monopolar_channels,
                               start_time=0.0, end_time=1.6, buffer_time=1.0)

        self.base_eegs = eeg_reader.read()

    def test_classifier(self):
        m2b = MonopolarToBipolarMapper(time_series=self.base_eegs, bipolar_pairs=self.bipolar_pairs)
        bp_eegs = m2b.filter()

        wf = MorletWaveletFilter(time_series=bp_eegs,
                                 freqs=np.logspace(np.log10(3), np.log10(180), 8),
                                 output='power',
                                 frequency_dim_pos=0,
                                 verbose=True
                                 )

        pow_wavelet, phase_wavelet = wf.filter()

        pow_wavelet = pow_wavelet.remove_buffer(duration=1.0)
        print(pow_wavelet)
        np.log10(pow_wavelet.data, out=pow_wavelet.data)
        print(pow_wavelet)
        mean_powers = pow_wavelet.mean(dim='time')
        print(mean_powers)




        # sess_pow_mat_post[ev,i,:] = np.nanmean(pow_ev_stripped, axis=1)

        print()


if __name__ == '__main__':
    unittest.main(verbosity=2)
