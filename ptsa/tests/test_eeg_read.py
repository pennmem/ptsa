__author__ = 'm'

import unittest

from numpy.testing import *
# from unittest import *

from EventReadersTestBase import EventReadersTestBase
from ptsa.data.events import Events


class TestEEGRead(unittest.TestCase, EventReadersTestBase):
    def setUp(self):

        self.event_range = range(0, 30, 1)
        self.e_path = '/Users/m/data/events/RAM_FR1/R1060M_events.mat'

    def test_eeg_read(self):

        events = self.read_ptsa_events()

        # in case fancy indexing looses Eventness of events we need to create Events object explicitely
        if not isinstance(events, Events):
            events = Events(events)

        base_events = self.read_base_events()

        eegs = events.get_data(channels=['002', '003'], start_time=0.0, end_time=1.6,
                               buffer_time=1.0, eoffset='eegoffset', keep_buffer=False,
                               eoffset_in_time=False, verbose=True)

        from ptsa.data.experimental.TimeSeriesEEGReader import TimeSeriesEEGReader

        time_series_reader = TimeSeriesEEGReader(base_events)

        time_series_reader.start_time = 0.0
        time_series_reader.end_time = 1.6
        time_series_reader.buffer_time = 1.0
        time_series_reader.keep_buffer = False

        time_series_reader.read(channels=['002', '003'])

        base_eegs = time_series_reader.get_output()

        assert_array_equal(eegs, base_eegs.data)

    def test_eeg_read_keep_buffer(self):

        # OLD READERS
        events = self.read_ptsa_events()

        # in case fancy indexing looses Eventness of events we need to create Events object explicitely
        if not isinstance(events, Events):
            events = Events(events)

        eegs = events.get_data(channels=['002', '003'], start_time=0.0, end_time=1.6,
                               buffer_time=1.0, eoffset='eegoffset', keep_buffer=True,
                               eoffset_in_time=False, verbose=True)


        # NEW READERS
        base_events = self.read_base_events()

        from ptsa.data.experimental.TimeSeriesEEGReader import TimeSeriesEEGReader

        time_series_reader = TimeSeriesEEGReader(events=base_events, start_time=0.0,
                                                 end_time=1.6, buffer_time=1.0, keep_buffer=True)

        time_series_reader.read(channels=['002', '003'])

        base_eegs = time_series_reader.get_output()

        # testing
        assert_array_equal(eegs, base_eegs.data)

    def test_eeg_read_keep_buffer_butterworth_filtered(self):

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
        eegs_filtered = eegs.filtered([58, 62], filt_type='stop', order=4)


        # New style reading
        from ptsa.data.experimental.TimeSeriesEEGReader import TimeSeriesEEGReader

        time_series_reader = TimeSeriesEEGReader(events=base_events, start_time=0.0,
                                                 end_time=1.6, buffer_time=1.0, keep_buffer=True)

        time_series_reader.read(channels=['002', '003'])

        base_eegs = time_series_reader.get_output()

        from ptsa.data.filters.ButterworthFilter import ButterworthFilter
        b_filter = ButterworthFilter(time_series=base_eegs, samplerate=base_eegs.attrs['samplerate'],
                                     freq_range=[58, 62], filt_type='stop',
                                     order=4)


        base_eegs_filtered = b_filter.filter()



        # testing
        assert_array_equal(eegs_filtered, base_eegs_filtered.data)

        assert_array_equal(eegs, base_eegs.data)

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
        from ptsa.data.experimental.TimeSeriesEEGReader import TimeSeriesEEGReader

        time_series_reader = TimeSeriesEEGReader(events=base_events, start_time=0.0,
                                                 end_time=1.6, buffer_time=1.0, keep_buffer=True)

        time_series_reader.read(channels=['002', '003'])

        base_eegs = time_series_reader.get_output()

        from ptsa.data.filters.ResampleFilter import ResampleFilter
        resample_filter = ResampleFilter(time_series=base_eegs, resamplerate=50.0)

        base_eegs_resampled = resample_filter.filter()


        # testing
        assert_array_equal(eegs_resampled, base_eegs_resampled.data)





if __name__ == '__main__':
    unittest.main(verbosity=2)
