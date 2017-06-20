import os
import unittest
import os.path as osp
import pytest

import numpy as np
from numpy.testing import assert_array_equal, assert_array_almost_equal
from ptsa.data import TimeSeriesX
from ptsa.data.readers import BaseEventReader
from ptsa.data.filters.MorletWaveletFilter import MorletWaveletFilter
from ptsa.data.readers.TalReader import TalReader
from ptsa.data.readers import EEGReader
from ptsa.data.filters import DataChopper
from ptsa.data.filters import MonopolarToBipolarMapper
from ptsa.data.filters import ButterworthFilter
from ptsa.data.filters import ResampleFilter
from ptsa.test.utils import get_rhino_root, skip_without_rhino


@skip_without_rhino
class TestFilters(unittest.TestCase):
    def setUp(self):
        self.start_time = -0.5
        self.end_time = 1.6
        self.buffer_time = 0.5

        self.event_range = range(0, 30, 1)

        # here = osp.abspath(osp.dirname(__file__))
        here = get_rhino_root()
        self.e_path = osp.join(here, 'data', 'events', 'RAM_FR1', 'R1060M_events.mat')
        tal_path = osp.join(here, 'data', 'eeg', 'R1060M', 'tal', 'R1060M_talLocs_database_bipol.mat')

        tal_reader = TalReader(filename=tal_path)
        self.monopolar_channels = tal_reader.get_monopolar_channels()
        self.bipolar_pairs = tal_reader.get_bipolar_pairs()

        base_e_reader = BaseEventReader(filename=self.e_path, eliminate_events_with_no_eeg=True)
        base_events = base_e_reader.read()
        base_events = base_events[base_events.type == 'WORD']
        base_ev_order = np.argsort(base_events, order=('session', 'list', 'mstime'))
        self.base_events = base_events[base_ev_order]

        # retaining first session
        dataroot = self.base_events[0].eegfile
        self.base_events = self.base_events[self.base_events.eegfile == dataroot]
        self.base_events = self.base_events[self.event_range]

        eeg_reader = EEGReader(events=self.base_events, channels=self.monopolar_channels,
                               start_time=self.start_time, end_time=self.end_time, buffer_time=self.buffer_time)

        self.base_eegs = eeg_reader.read()

        session_reader = EEGReader(session_dataroot=dataroot, channels=self.monopolar_channels)
        self.session_eegs = session_reader.read()

    @pytest.mark.slow
    def test_event_data_chopper(self):
        dataroot = self.base_events[0].eegfile
        session_reader = EEGReader(session_dataroot=dataroot, channels=self.monopolar_channels)
        session_eegs = session_reader.read()

        sedc = DataChopper(events=self.base_events, session_data=session_eegs,
                           start_time=self.start_time, end_time=self.end_time, buffer_time=self.buffer_time)
        chopped_session = sedc.filter()
        assert_array_equal(chopped_session, self.base_eegs)

        sedc = DataChopper(start_offsets=self.base_events.eegoffset, session_data=session_eegs,
                           start_time=self.start_time, end_time=self.end_time, buffer_time=self.buffer_time)
        chopped_session = sedc.filter()
        assert_array_equal(chopped_session, self.base_eegs)

    @pytest.mark.skip
    def test_monopolar_to_bipolar_filter(self):
        m2b = MonopolarToBipolarMapper(time_series=self.base_eegs, bipolar_pairs=self.bipolar_pairs)
        bp_base_eegs = m2b.filter()

        bipolar_pairs = bp_base_eegs['bipolar_pairs'].data
        for i, bp in enumerate(bipolar_pairs):
            e0 = self.base_eegs.sel(channels=bp[0])
            e1 = self.base_eegs.sel(channels=bp[1])
            # res = e0.__sub__(e1)
            assert_array_equal(e0 - e1, bp_base_eegs[i])

    @pytest.mark.skip
    def test_monopolar_to_bipolar_filter_and_data_chopper(self):
        dataroot = self.base_events[0].eegfile

        session_reader = EEGReader(session_dataroot=dataroot, channels=self.monopolar_channels)
        session_eegs = session_reader.read()

        m2b = MonopolarToBipolarMapper(time_series=session_eegs, bipolar_pairs=self.bipolar_pairs)
        bp_session_eegs = m2b.filter()

        sedc = DataChopper(events=self.base_events, session_data=bp_session_eegs, start_time=self.start_time,
                           end_time=self.end_time, buffer_time=self.buffer_time)

        bp_session_eegs_chopped = sedc.filter()

        m2b = MonopolarToBipolarMapper(time_series=self.base_eegs, bipolar_pairs=self.bipolar_pairs)
        bp_base_eegs = m2b.filter()

        assert_array_equal(bp_session_eegs_chopped, bp_base_eegs)

    @pytest.mark.skip
    def test_wavelets_with_event_data_chopper(self):
        wf_session = MorletWaveletFilter(
            time_series=self.session_eegs[:, :, :self.session_eegs.shape[2] / 4],
            freqs=np.logspace(np.log10(3), np.log10(180), 8),
            output='power',
            frequency_dim_pos=0,
            verbose=True
        )

        pow_wavelet_session, phase_wavelet_session = wf_session.filter()

        sedc = DataChopper(events=self.base_events, session_data=pow_wavelet_session, start_time=self.start_time,
                           end_time=self.end_time, buffer_time=self.buffer_time)
        chopped_session_pow_wavelet = sedc.filter()

        # removing buffer
        chopped_session_pow_wavelet = chopped_session_pow_wavelet[:, :, :, 500:-500]

        wf = MorletWaveletFilter(time_series=self.base_eegs,
                                 freqs=np.logspace(np.log10(3), np.log10(180), 8),
                                 output='power',
                                 frequency_dim_pos=0,
                                 verbose=True
                                 )

        pow_wavelet, phase_wavelet = wf.filter()

        pow_wavelet = pow_wavelet[:, :, :, 500:-500]

        assert_array_almost_equal(
            (chopped_session_pow_wavelet.data - pow_wavelet.data) / pow_wavelet.data,
            np.zeros_like(pow_wavelet),
            decimal=5
        )

    def test_ButterwothFilter(self):

        from xarray.testing import assert_equal

        b_filter = ButterworthFilter(time_series=self.base_eegs, freq_range=[58., 62.], filt_type='stop', order=4)
        base_eegs_filtered_1 = b_filter.filter()

        base_eegs_filtered_2 = self.base_eegs.filtered(freq_range=[58., 62.], filt_type='stop', order=4)


        assert_equal(base_eegs_filtered_1, base_eegs_filtered_2)

        with self.assertRaises(AssertionError):
            assert_equal(base_eegs_filtered_1, self.base_eegs)


class TestFiltersExecute(unittest.TestCase):
    def setUp(self):
        times = np.linspace(0,1,1000)
        ts = np.sin(8*times) + np.sin(16*times) + np.sin(32*times)
        self.time_series = TimeSeriesX.TimeSeriesX(data=ts,dims=('time'),coords = {'time':times,'samplerate':1000})


    def test_ButterworthFilter(self):
        bfilter = ButterworthFilter(time_series = self.time_series,freq_range = [10.,20.],filt_type='stop',order=2)
        bfilter.filter()
        return True

    def test_MorletWaveletFilter(self):
        mwf = MorletWaveletFilter(time_series=self.time_series,freqs=np.array([10.,20.,40.]),width=4)
        power,phase= mwf.filter()
        assert power.shape == (3,1000)
        assert phase.shape == (3,1000)


    def test_ResampleFilter(self):
        rf = ResampleFilter(time_series = self.time_series,resamplerate=50.)
        new_ts = rf.filter()
        assert len(new_ts) == 50
        assert new_ts.samplerate == 50.




