import os.path as osp
import unittest
import numpy as np
import pytest

from ptsa.data.readers import BaseEventReader
from ptsa.data.filters.MorletWaveletFilter import MorletWaveletFilter
from ptsa.data.readers.tal import TalReader
from ptsa.data.readers import EEGReader
from ptsa.data.filters import MonopolarToBipolarMapper
from ptsa.test.utils import get_rhino_root, skip_without_rhino


@skip_without_rhino
class TestClassifier(unittest.TestCase):
    def setUp(self):
        root = get_rhino_root()
        self.e_path = osp.join(root, 'data', 'events', 'RAM_FR1',
                               'R1060M_events.mat')
        tal_path = osp.join(root, 'data', 'eeg', 'R1060M', 'tal',
                            'R1060M_talLocs_database_bipol.mat')

        base_e_reader = BaseEventReader(filename=self.e_path,
                                        eliminate_events_with_no_eeg=True)

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

    @pytest.mark.slow
    def test_classifier(self):
        m2b = MonopolarToBipolarMapper(time_series=self.base_eegs, bipolar_pairs=self.bipolar_pairs)
        bp_eegs = m2b.filter()

        wf = MorletWaveletFilter(timeseries=bp_eegs,
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
