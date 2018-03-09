import os.path as osp
import unittest
from numpy.testing import assert_array_equal
import pytest

from ptsa.data.filters.ButterworthFilter import ButterworthFilter
from ptsa.data.filters.ResampleFilter import ResampleFilter
from ptsa.data.events import Events
from ptsa.data.experimental.TimeSeriesEEGReader import TimeSeriesEEGReader
from ptsa.test.utils import EventReadersTestBase, skip_without_rhino, get_rhino_root


@skip_without_rhino
class TestEEGRead(unittest.TestCase, EventReadersTestBase):
    def setUp(self):
        root = get_rhino_root()
        self.event_range = range(0, 30, 1)
        self.e_path = osp.join(root, 'data', 'events', 'RAM_FR1', 'R1060M_events.mat')

    @pytest.mark.xfail
    def test_eeg_read(self):

        events = self.read_ptsa_events()

        # in case fancy indexing looses Eventness of events we need to create
        # Events object explicitely
        if not isinstance(events, Events):
            events = Events(events)

        base_events = self.read_base_events()

        eegs = events.get_data(channels=['002', '003'], start_time=0.0, end_time=1.6,
                               buffer_time=1.0, eoffset='eegoffset', keep_buffer=False,
                               eoffset_in_time=False, verbose=True)

        time_series_reader = TimeSeriesEEGReader(base_events)

        time_series_reader.start_time = 0.0
        time_series_reader.end_time = 1.6
        time_series_reader.buffer_time = 1.0
        time_series_reader.keep_buffer = False

        time_series_reader.read(channels=['002', '003'])

        base_eegs = time_series_reader.get_output()

        assert_array_equal(eegs, base_eegs.data)

    @pytest.mark.xfail
    def test_eeg_read_keep_buffer(self):
        # OLD READERS
        events = self.read_ptsa_events()

        # in case fancy indexing looses Eventness of events we need to create
        # Events object explicitely
        if not isinstance(events, Events):
            events = Events(events)

        eegs = events.get_data(channels=['002', '003'], start_time=0.0, end_time=1.6,
                               buffer_time=1.0, eoffset='eegoffset', keep_buffer=True,
                               eoffset_in_time=False, verbose=True)

        # NEW READERS
        base_events = self.read_base_events()
        time_series_reader = TimeSeriesEEGReader(events=base_events, start_time=0.0,
                                                 end_time=1.6, buffer_time=1.0, keep_buffer=True)

        time_series_reader.read(channels=['002', '003'])
        base_eegs = time_series_reader.get_output()

        # testing
        assert_array_equal(eegs, base_eegs.data)

    @pytest.mark.xfail
    def test_eeg_read_keep_buffer_butterworth_filtered(self):
        # old readers
        events = self.read_ptsa_events()

        # in case fancy indexing looses Eventness of events we need to create
        # Events object explicitely
        if not isinstance(events, Events):
            events = Events(events)

        base_events = self.read_base_events()
        eegs = events.get_data(channels=['002', '003'], start_time=0.0, end_time=1.6,
                               buffer_time=1.0, eoffset='eegoffset', keep_buffer=True,
                               eoffset_in_time=False, verbose=True)
        # filtering
        eegs_filtered = eegs.filtered([58, 62], filt_type='stop', order=4)

        # New style reading
        time_series_reader = TimeSeriesEEGReader(events=base_events, start_time=0.0,
                                                 end_time=1.6, buffer_time=1.0, keep_buffer=True)
        time_series_reader.read(channels=['002', '003'])
        base_eegs = time_series_reader.get_output()

        b_filter = ButterworthFilter(time_series=base_eegs, samplerate=base_eegs.attrs['samplerate'],
                                     freq_range=[58, 62], filt_type='stop',
                                     order=4)

        base_eegs_filtered = b_filter.filter()

        # testing
        assert_array_equal(eegs_filtered, base_eegs_filtered.data)
        assert_array_equal(eegs, base_eegs.data)

    @pytest.mark.xfail
    def test_eeg_resample(self):
        # old readers
        events = self.read_ptsa_events()

        # in case fancy indexing looses Eventness of events we need to create Events object explicitely
        if not isinstance(events, Events):
            events = Events(events)

        base_events = self.read_base_events()

        eegs = events.get_data(channels=['002', '003'], start_time=0.0, end_time=1.6,
                               buffer_time=1.0, eoffset='eegoffset', keep_buffer=True,
                               eoffset_in_time=False, verbose=True)
        # filtering
        eegs_resampled = eegs.resampled(50.0)

        # New style reading
        time_series_reader = TimeSeriesEEGReader(events=base_events, start_time=0.0,
                                                 end_time=1.6, buffer_time=1.0, keep_buffer=True)

        time_series_reader.read(channels=['002', '003'])

        base_eegs = time_series_reader.get_output()
        resample_filter = ResampleFilter(time_series=base_eegs, resamplerate=50.0)

        base_eegs_resampled = resample_filter.filter()

        # testing
        assert_array_equal(eegs_resampled, base_eegs_resampled.data)

@skip_without_rhino
def test_eeg_with_tal_data():
    from ptsa.data.readers import JsonIndexReader,TalReader,EEGReader,BaseEventReader
    import os
    subject = 'R1111M'
    experiment='FR1'
    session=0
    jr = JsonIndexReader(os.path.join(get_rhino_root(),'protocols','r1.json'))
    events = BaseEventReader(filename=jr.get_value('task_events',subject=subject,experiment=experiment,session=session)).read()
    tal_struct = TalReader(filename=jr.get_value('contacts',subject=subject),struct_type='mono').read()
    eeg = EEGReader(events=events[:10],channels=tal_struct[:10],start_time=0.0,end_time=0.1).read()
    for col in tal_struct.dtype.names:
        if col != 'atlases': # Because I don't want to deal with NaNs at the moment
            assert (eeg.channels.data[col]==tal_struct[:10][col]).all()