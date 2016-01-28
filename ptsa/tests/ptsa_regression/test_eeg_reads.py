__author__ = 'm'

import numpy as np
from numpy.testing import *
import unittest
# from unittest import *

from EventReadersTestBase import EventReadersTestBase
from ptsa.data.events import Events

# class OutcomesTest(unittest.TestCase):
#
#     def test_pass(self):
#         self.assertTrue(True)
#
#     def test_fail(self):
#         self.assertTrue(False)
#
#     def test_error(self):
#         raise RuntimeError('Test error!')

class TestEEGRead(unittest.TestCase, EventReadersTestBase):
# class TestEEGRead(unittest.TestCase):
    def setUp(self):

        self.event_range = range(0, 30, 1)
        self.e_path = '/Users/m/data/events/RAM_FR1/R1060M_events.mat'

    # def test_eeg_read(self):
    #
    #     assert_equal(0.1,0.1)

    # def test_eeeg_read(self):
    #
    #     assert_equal(0.2,0.2)


    def test_eeg_read(self):

        events = self.read_ptsa_events()

        # in case fancy indexing looses Eventness of events we need to create Events object explicitely
        if not isinstance(events, Events):
            events = Events(events)



        eegs = events.get_data(channels=['002', '003'], start_time=0.0, end_time=1.6,
                               buffer_time=1.0, eoffset='eegoffset', keep_buffer=False,
                               eoffset_in_time=False, verbose=True)

        base_events = self.read_base_events()

        from ptsa.data.readers.EEGReader import EEGReader
        eeg_reader = EEGReader(events=base_events, channels=['002','003'], start_time=0.0,end_time=1.6, buffer_time=1.0)

        base_eegs = eeg_reader.read()
        base_eegs = base_eegs.remove_buffer(duration=1.0)

        print
        # orig ptsa returns extra stime point that's why eegs[:,:,:-1]
        assert_array_equal(eegs[:,:,:-1], base_eegs.data)

    def test_eeg_read_keep_buffer(self):

        # OLD READERS
        events = self.read_ptsa_events()

        # in case fancy indexing looses Eventness of events we need to create Events object explicitely
        if not isinstance(events, Events):
            events = Events(events)

        eegs = events.get_data(channels=['002', '003'], start_time=0.0, end_time=1.6,
                               buffer_time=1.0, eoffset='eegoffset', keep_buffer=True,
                               eoffset_in_time=False, verbose=True)


        # # NEW READERS
        # base_events = self.read_base_events()
        #
        # from ptsa.data.readers.TimeSeriesEEGReader import TimeSeriesEEGReader
        #
        # time_series_reader = TimeSeriesEEGReader(events=base_events, start_time=0.0,
        #                                          end_time=1.6, buffer_time=1.0, keep_buffer=True)
        #
        # time_series_reader.read(channels=['002', '003'])

        base_events = self.read_base_events()
        from ptsa.data.readers.EEGReader import EEGReader
        eeg_reader = EEGReader(events=base_events, channels=['002','003'], start_time=0.0,end_time=1.6, buffer_time=1.0)
        base_eegs = eeg_reader.read()

        print

        # testing
        # orig ptsa returns extra stime point that's why eegs[:,:,:-1]
        assert_array_equal(eegs[:,:,:-1], base_eegs.data)

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
        # eegs_filtered = eegs.filtered([58, 62], filt_type='stop', order=4)
        # # orig ptsa returns extra stime point that's why eegs[:,:,:-1]
        eegs = eegs[:,:,:-1]
        eegs_filtered = eegs.filtered([58, 62], filt_type='stop', order=4)


        # New style reading
        # from ptsa.data.readers.TimeSeriesEEGReader import TimeSeriesEEGReader
        #
        # time_series_reader = TimeSeriesEEGReader(events=base_events, start_time=0.0,
        #                                          end_time=1.6, buffer_time=1.0, keep_buffer=True)
        #
        # time_series_reader.read(channels=['002', '003'])
        #
        # base_eegs = time_series_reader.get_output()

        base_events = self.read_base_events()
        from ptsa.data.readers.EEGReader import EEGReader
        eeg_reader = EEGReader(events=base_events, channels=['002','003'], start_time=0.0,end_time=1.6, buffer_time=1.0)
        base_eegs = eeg_reader.read()

        base_eegs_filtered_direct = base_eegs.filtered([58, 62], filt_type='stop', order=4)

        from ptsa.data.filters.ButterworthFilter import ButterworthFiler
        b_filter = ButterworthFiler(time_series=base_eegs,freq_range=[58, 62], filt_type='stop',order=4)


        base_eegs_filtered = b_filter.filter()


        print
        # testing

        assert_array_equal(eegs[:,:,:], base_eegs.data)


        # assert_array_almost_equal(eegs_filtered[:,:,:], base_eegs_filtered.data, decimal=2)
        assert_array_equal(eegs_filtered[:,:,:], base_eegs_filtered.data)
        assert_array_equal(eegs_filtered[:,:,:], base_eegs_filtered_direct.data)


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

        # # orig ptsa returns extra stime point that's why eegs[:,:,:-1]
        eegs = eegs[:,:,:-1]

        # filtering
        eegs_resampled = eegs.resampled(100.0)



        base_events = self.read_base_events()
        from ptsa.data.readers.EEGReader import EEGReader
        eeg_reader = EEGReader(events=base_events, channels=['002','003'], start_time=0.0,end_time=1.6, buffer_time=1.0)
        base_eegs = eeg_reader.read()


        # New style reading
        # from ptsa.data.readers.TimeSeriesEEGReader import TimeSeriesEEGReader
        #
        # time_series_reader = TimeSeriesEEGReader(events=base_events, start_time=0.0,
        #                                          end_time=1.6, buffer_time=1.0, keep_buffer=True)
        #
        # time_series_reader.read(channels=['002', '003'])
        #
        # base_eegs = time_series_reader.get_output()

        from ptsa.data.filters.ResampleFilter import ResampleFilter
        resample_filter = ResampleFilter(time_series=base_eegs, resamplerate=100.0)

        base_eegs_resampled = resample_filter.filter()

        base_eegs_resampled_direct = base_eegs.resampled(resampled_rate=100.0)

        # testing
        assert_array_equal(eegs_resampled, base_eegs_resampled.data)
        assert_array_equal(eegs_resampled, base_eegs_resampled_direct.data)




if __name__ == '__main__':
    unittest.main(verbosity=2)

# if __name__=='__main__':
#     test_suite = unittest.TestSuite()
#     # test_suite.addTest(unittest.makeSuite(TestEventRead))
#     test_suite.addTest(unittest.makeSuite(TestEEGRead))
#
#     # test_suite.addTest(unittest.makeSuite(test_morlet_multi))
#
#     runner=unittest.TextTestRunner()
#     runner.run(test_suite)