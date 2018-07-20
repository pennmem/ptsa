import unittest
import os.path as osp
import pytest
import xarray as xr

import numpy as np
from numpy.testing import assert_array_equal, assert_array_almost_equal

from ptsa.data import timeseries
from ptsa.data.filters import (
    BaseFilter, ButterworthFilter, DataChopper, MonopolarToBipolarMapper,
    MorletWaveletFilter, ResampleFilter
)
from ptsa.data.readers import BaseEventReader, EEGReader
from ptsa.data.readers.tal import TalReader
from ptsa.test.utils import get_rhino_root, skip_without_rhino


def test_monopolar_to_bipolar_filter_norhino():
    data = np.random.random((20, 10, 5))
    rate = 1000
    dims = ('time', 'channels', 'events')
    coords = {'time': np.linspace(0, 1, 20),
              'channels': range(10),
              'events': ['A', 'B', 'C', 'D', 'E']}
    ts = timeseries.TimeSeries.create(
        data, rate, coords=coords,
        dims=dims, name="test", attrs={'test_attr': 1})

    bipolar_pairs1 = np.array([range(9), range(1,10)])
    m2b1 = MonopolarToBipolarMapper(timeseries=ts,
                                    bipolar_pairs=bipolar_pairs1)
    ts_m2b1 = m2b1.filter()

    bipolar_pairs2 = np.array([(i, j) for i, j in zip(range(9), range(1,10))],
                              dtype=[('ch0', '<i8'), ('ch1', '<i8')])
    m2b2 = MonopolarToBipolarMapper(timeseries=ts,
                                    bipolar_pairs=bipolar_pairs2)
    ts_m2b2 = m2b2.filter()

    assert np.all(ts_m2b1 == ts_m2b2)

    # checking each coord is probably redundant (mismatching coords
    # should cause failure in the above assertion), but won't hurt
    for coord in ts_m2b1.coords:
        assert np.all(ts_m2b1[coord] == ts_m2b2[coord])
        if coord != 'channels':
            assert np.all(ts[coord] == ts_m2b1[coord])

    # sanity check that we haven't lost any coords:
    for coord in ts.coords:
        if coord != 'channels':
            assert np.all(ts[coord] == ts_m2b1[coord])
    for attr in ts.attrs:
        assert np.all(ts_m2b1.attrs[attr] == ts_m2b2.attrs[attr])
        assert np.all(ts.attrs[attr] == ts_m2b1.attrs[attr])

    assert ts.name == ts_m2b1.name
    assert ts.name == ts_m2b2.name
    assert np.all(ts_m2b1['channels'] == bipolar_pairs2)
    assert np.all(ts_m2b1 == (ts.sel(channels=range(9)).values -
                              ts.sel(channels=range(1,10)).values))
    assert np.all(ts_m2b2 == (ts.sel(channels=range(9)).values -
                              ts.sel(channels=range(1,10)).values))

    dims2 = ('time', 'electrodes', 'events')
    coords2 = {'time': np.linspace(0, 1, 20),
              'electrodes': range(10),
              'events': ['A', 'B', 'C', 'D', 'E']}
    ts2 = timeseries.TimeSeries.create(
        data, rate, coords=coords2,
        dims=dims2, name="test", attrs={'test_attr': 1})
    m2b3 = MonopolarToBipolarMapper(timeseries=ts2, channels_dim='electrodes',
                                    bipolar_pairs=bipolar_pairs1)
    ts_m2b3 = m2b3.filter()
    assert np.all(ts_m2b3.values == ts_m2b1.values)
    # checking each coord is probably redundant (mismatching coords
    # should cause failure in the above assertion), but won't hurt
    for coord in ts_m2b3.coords:
        if coord != 'electrodes':
            assert np.all(ts[coord] == ts_m2b3[coord])
    assert np.all(ts_m2b3['electrodes'].values == ts_m2b1['channels'].values)
    # sanity check that we haven't lost any coords:
    for coord in ts.coords:
        if coord != 'channels':
            assert np.all(ts[coord] == ts_m2b3[coord])
    for attr in ts.attrs:
        assert np.all(ts_m2b3.attrs[attr] == ts_m2b1.attrs[attr])
        assert np.all(ts.attrs[attr] == ts_m2b3.attrs[attr])
    assert ts.name == ts_m2b3.name
    assert np.all(ts_m2b3['electrodes'] == bipolar_pairs2)
    assert np.all(ts_m2b3 == (ts.sel(channels=range(9)).values -
                              ts.sel(channels=range(1,10)).values))
    m2b4 = MonopolarToBipolarMapper(timeseries=ts2, channels_dim='electrodes',
                                    bipolar_pairs=bipolar_pairs2)
    ts_m2b4 = m2b4.filter()
    assert np.all(ts_m2b4 == ts_m2b3)
    # checking each coord is probably redundant (mismatching coords
    # should cause failure in the above assertion), but won't hurt
    for coord in ts_m2b4.coords:
        assert np.all(ts_m2b3[coord] == ts_m2b4[coord])
    # sanity check that we haven't lost any coords:
    for coord in ts.coords:
        if coord != 'channels':
            assert np.all(ts[coord] == ts_m2b4[coord])
    for attr in ts.attrs:
        assert np.all(ts_m2b4.attrs[attr] == ts_m2b1.attrs[attr])
        assert np.all(ts.attrs[attr] == ts_m2b4.attrs[attr])
    assert ts.name == ts_m2b4.name
    assert np.all(ts_m2b4['electrodes'] == bipolar_pairs2)
    assert np.all(ts_m2b4 == (ts.sel(channels=range(9)).values -
                              ts.sel(channels=range(1,10)).values))

    bipolar_pairs3 = np.array([(i, j) for i, j in zip(range(9), range(1,10))],
                              dtype=[('channel0', '<i8'), ('channel1', '<i8')])
    m2b5 = MonopolarToBipolarMapper(timeseries=ts2, channels_dim='electrodes',
                                    bipolar_pairs=bipolar_pairs1,
                                    chan_names=['channel0', 'channel1'])
    ts_m2b5 = m2b5.filter()
    assert np.all(ts_m2b5.values == ts_m2b1.values)
    # checking each coord is probably redundant (mismatching coords
    # should cause failure in the above assertion), but won't hurt
    for coord in ts_m2b5.coords:
        if coord != 'electrodes':
            assert np.all(ts[coord] == ts_m2b5[coord])
    for a, b in zip(ts_m2b5['electrodes'], ts_m2b1['channels']):
        assert np.all(
            np.array(a.values.tolist()) == np.array(b.values.tolist()))
    # sanity check that we haven't lost any coords:
    for coord in ts.coords:
        if coord != 'channels':
            assert np.all(ts[coord] == ts_m2b5[coord])
    for attr in ts.attrs:
        assert np.all(ts_m2b5.attrs[attr] == ts_m2b1.attrs[attr])
        assert np.all(ts.attrs[attr] == ts_m2b5.attrs[attr])
    assert ts.name == ts_m2b5.name
    assert np.all(ts_m2b5['electrodes'] == bipolar_pairs3)
    assert np.all(ts_m2b5 == (ts.sel(channels=range(9)).values -
                              ts.sel(channels=range(1,10)).values))
    m2b6 = MonopolarToBipolarMapper(timeseries=ts2, channels_dim='electrodes',
                                    chan_names=['channel0', 'channel1'],
                                    bipolar_pairs=bipolar_pairs3)
    ts_m2b6 = m2b6.filter()
    assert np.all(ts_m2b6 == ts_m2b5)
    # checking each coord is probably redundant (mismatching coords
    # should cause failure in the above assertion), but won't hurt
    for coord in ts_m2b6.coords:
        assert np.all(ts_m2b6[coord] == ts_m2b5[coord])
    # sanity check that we haven't lost any coords:
    for coord in ts.coords:
        if coord != 'channels':
            assert np.all(ts[coord] == ts_m2b6[coord])
    for attr in ts.attrs:
        assert np.all(ts_m2b6.attrs[attr] == ts_m2b1.attrs[attr])
        assert np.all(ts.attrs[attr] == ts_m2b6.attrs[attr])
    assert ts.name == ts_m2b6.name
    assert np.all(ts_m2b6['electrodes'] == bipolar_pairs3)
    assert np.all(ts_m2b6 == (ts.sel(channels=range(9)).values -
                              ts.sel(channels=range(1,10)).values))


@pytest.mark.filters
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

        sedc = DataChopper(events=self.base_events, timeseries=session_eegs,
                           start_time=self.start_time, end_time=self.end_time, buffer_time=self.buffer_time)
        chopped_session = sedc.filter()
        assert_array_equal(chopped_session, self.base_eegs)

        sedc = DataChopper(start_offsets=self.base_events.eegoffset, timeseries=session_eegs,
                           start_time=self.start_time, end_time=self.end_time, buffer_time=self.buffer_time)
        chopped_session = sedc.filter()
        assert_array_equal(chopped_session, self.base_eegs)

    def test_monopolar_to_bipolar_filter(self):
        m2b = MonopolarToBipolarMapper(timeseries=self.base_eegs, bipolar_pairs=self.bipolar_pairs)
        bp_base_eegs = m2b.filter()

        bipolar_pairs = bp_base_eegs['channels'].data
        for i, bp in enumerate(bipolar_pairs):
            e0 = self.base_eegs.sel(channels=bp[0])
            e1 = self.base_eegs.sel(channels=bp[1])
            # res = e0.__sub__(e1)
            assert_array_equal(e0 - e1, bp_base_eegs[i])

    @pytest.mark.slow
    def test_monopolar_to_bipolar_filter_and_data_chopper(self):
        dataroot = self.base_events[0].eegfile

        session_reader = EEGReader(session_dataroot=dataroot, channels=self.monopolar_channels)
        session_eegs = session_reader.read()

        m2b = MonopolarToBipolarMapper(timeseries=session_eegs, bipolar_pairs=self.bipolar_pairs)
        bp_session_eegs = m2b.filter()

        sedc = DataChopper(events=self.base_events, timeseries=bp_session_eegs, start_time=self.start_time,
                           end_time=self.end_time, buffer_time=self.buffer_time)

        bp_session_eegs_chopped = sedc.filter()

        m2b = MonopolarToBipolarMapper(timeseries=self.base_eegs, bipolar_pairs=self.bipolar_pairs)
        bp_base_eegs = m2b.filter()

        assert_array_equal(bp_session_eegs_chopped, bp_base_eegs)

    @pytest.mark.slow
    @pytest.mark.xfail
    def test_wavelets_with_event_data_chopper(self):
        wf_session = MorletWaveletFilter(
            timeseries=self.session_eegs[:, :, :int(self.session_eegs.shape[2] / 4)],
            freqs=np.logspace(np.log10(3), np.log10(180), 8),
            output='power',
            verbose=True
        )

        pow_wavelet_session = wf_session.filter()

        sedc = DataChopper(events=self.base_events, timeseries=pow_wavelet_session, start_time=self.start_time,
                           end_time=self.end_time, buffer_time=self.buffer_time)
        chopped_session_pow_wavelet = sedc.filter()

        # removing buffer
        chopped_session_pow_wavelet = chopped_session_pow_wavelet[:, :, :, 500:-500]

        wf = MorletWaveletFilter(timeseries=self.base_eegs,
                                 freqs=np.logspace(np.log10(3), np.log10(180), 8),
                                 output='power',
                                 verbose=True
                                 )

        pow_wavelet = wf.filter()

        pow_wavelet = pow_wavelet[:, :, :, 500:-500]

        assert_array_almost_equal(
            (chopped_session_pow_wavelet.data - pow_wavelet.data) / pow_wavelet.data,
            np.zeros_like(pow_wavelet),
            decimal=5
        )

    def test_ButterwothFilter(self):

        from xarray.testing import assert_equal

        b_filter = ButterworthFilter(timeseries=self.base_eegs, freq_range=[58., 62.], filt_type='stop', order=4)
        base_eegs_filtered_1 = b_filter.filter()

        base_eegs_filtered_2 = self.base_eegs.filtered(freq_range=[58., 62.], filt_type='stop', order=4)


        assert_equal(base_eegs_filtered_1, base_eegs_filtered_2)

        with self.assertRaises(AssertionError):
            assert_equal(base_eegs_filtered_1, self.base_eegs)


@pytest.fixture
def time_series():
    times = np.linspace(0, 1, 1000)
    ts = np.sin(8*times) + np.sin(16*times) + np.sin(32*times)
    return timeseries.TimeSeries(data=ts, dims=('time'),
                                            coords={
                                                'time': times,
                                                'samplerate': 1000
                                            })


@pytest.mark.filters
class TestFiltersExecute:
    @classmethod
    def setup_class(cls):
        times = np.linspace(0, 1, 1000)
        ts = np.sin(8*times) + np.sin(16*times) + np.sin(32*times)
        cls.timeseries = timeseries.TimeSeries(data=ts, dims=('time'),
                                                coords={
                                                    'time': times,
                                                    'samplerate': 1000
                                                })

    def test_butterworth(self,time_series):
        bfilter = ButterworthFilter(timeseries=time_series,
                                    freq_range=[10., 20.],
                                    filt_type='stop',
                                    order=2)
        bfilter.filter()

    @pytest.mark.morlet
    @pytest.mark.parametrize('output_type', [
        'power',
        'phase',
        ['power', 'phase'],
    ])
    def test_morlet(self, output_type):
        mwf = MorletWaveletFilter(timeseries=self.timeseries,
                                  freqs=np.array([10., 20., 40.]),
                                  width=4, output=output_type)
        result = mwf.filter()

        if len(mwf.output) == 1:
            if 'power' in mwf.output:
                assert result.data.shape == (3, 1000)
            if 'phase' in mwf.output:
                assert result.data.shape == (3, 1000)
        else:
            assert result.data.shape == (2,3,1000)

    def test_resample(self,time_series):
        rf = ResampleFilter(timeseries=time_series, resamplerate=50.)
        new_ts = rf.filter()
        assert len(new_ts) == 50
        assert new_ts.samplerate == 50.


class TestFilterShapes:
    """Filter behavior should not depend on shape of input array."""
    @classmethod
    def setup_class(self):
        self.times = times = np.linspace(0,1,1000)
        self.data = np.sin(8*times) + np.sin(16*times) + np.sin(32*times)
        self.freqs = np.array([10,20],dtype=float)
        self.timeseries = timeseries.TimeSeries(data=self.data[None,:],
                                                coords={
                                                    'offsets': [0],
                                                    'time': self.times,
                                                    'samplerate': 1000
                                                },
                                                dims=('offsets', 'time'))

    def test_MorletWaveletFilterCpp(self):
        results0 = MorletWaveletFilter(self.timeseries, freqs=self.freqs,
                                       width=4, output=['power','phase']).filter()

        results1 = MorletWaveletFilter(self.timeseries.transpose(),
                                       freqs=self.freqs,
                                       width=4, output=['power','phase']).filter()
        print(results0)

        xr.testing.assert_allclose(results0.sel(output='power'),
                                   results1.sel(output='power'))
        xr.testing.assert_allclose(results0.sel(output='phase'),
                                   results1.sel(output='phase'))

    @pytest.mark.slow
    def test_ButterworthFilter(self):
        filtered0 = ButterworthFilter(self.timeseries, self.freqs.tolist()).filter()
        filtered1 = ButterworthFilter(self.timeseries.transpose(), self.freqs.tolist()).filter()

        xr.testing.assert_allclose(filtered0, filtered1.transpose(*filtered0.dims))


class TestBaseFilter:
    @property
    def dummy_ts(self):
        return timeseries.TimeSeries(
            np.linspace(0, 10, 10),
            dims=("x",),
            coords={
                "x": range(10),
                "samplerate": 1
            }
        )

    @pytest.mark.parametrize("dtype,expected_dtype", [
        (None, np.float64),
        (np.float64, np.float64),
        ("double", np.float64),
        ("float32", np.float32),
        ("int", np.int),
    ])
    def test_dtypes(self, dtype, expected_dtype):
        filt = BaseFilter(self.dummy_ts, dtype)
        assert filt.timeseries.data.dtype == expected_dtype

    @pytest.mark.parametrize("dtype", [np.int8, np.uint16, np.float32])
    def test_unchanged_dtype(self, dtype):
        """Special case test where we use a weird input dtype. The previous
        test works with None since by default Numpy uses float64.

        """
        ts = self.dummy_ts.astype(dtype)
        filt = BaseFilter(ts, None)
        assert filt.timeseries.data.dtype == dtype

    def test_filter(self):
        with pytest.raises(NotImplementedError):
            filt = BaseFilter(self.dummy_ts)
            filt.filter()


class TestMorletFilter:
    def test_non_double(self):
        """Test that we can use a TimeSeries that starts out as a dtype other
        than double.

        """
        lim = 10000
        data = np.random.uniform(-lim, lim, (100, 1000)).astype(np.int16)

        ts = timeseries.TimeSeries(
            data=data,
            dims=("x", "time"),
            coords={
                "x": np.linspace(0, data.shape[0], data.shape[0]),
                "time": np.arange(data.shape[1]),
                "samplerate": 1,
            }
        )

        mwf = MorletWaveletFilter(ts, np.array(range(70, 171, 10)), output="power")
        mwf.filter()
