__author__ = 'm'

import numpy as np
from numpy.testing import *
import unittest
# from unittest import *

from EventReadersTestBase import EventReadersTestBase
from ptsa.data.events import Events
from ptsa.data.readers.EEGReader import EEGReader
from ptsa.data.filters.ButterworthFilter import ButterworthFiler
from ptsa.data.filters.ResampleFilter import ResampleFilter


class TestEEGRead(unittest.TestCase, EventReadersTestBase):
    # class TestEEGRead(unittest.TestCase):
    def setUp(self):
        self.event_range = range(0, 30, 1)
        self.e_path = '/Users/m/data/events/RAM_FR1/R1060M_events.mat'

        # ---------------- ORIG PTSA -------------------

        self.events = self.read_ptsa_events()
        # in case fancy indexing looses Eventness of events we need to create Events object explicitely
        if not isinstance(self.events, Events):
            self.events = Events(self.events)
        self.eegs = self.events.get_data(channels=['002', '003'], start_time=0.0, end_time=1.6,
                                         buffer_time=1.0, eoffset='eegoffset', keep_buffer=True,
                                         eoffset_in_time=False, verbose=True)

        # ---------------- NEW STYLE PTSA -------------------

        self.base_events = self.read_base_events()

        eeg_reader = EEGReader(events=self.base_events, channels=np.array(['002', '003']),
                               start_time=0.0, end_time=1.6, buffer_time=1.0)

        self.base_eegs = eeg_reader.read()

    def test_eeg_read(self):
        base_eegs = self.base_eegs.remove_buffer(duration=1.0)
        eegs = self.eegs.remove_buffer(duration=1.0)

        # orig ptsa returns extra stime point that's why eegs[:,:,:-1]
        assert_array_equal(eegs[:, :, :-1], base_eegs.data)

    def test_eeg_read_keep_buffer(self):
        # orig ptsa returns extra stime point that's why eegs[:,:,:-1]
        eegs = self.eegs
        base_eegs = self.base_eegs

        assert_array_equal(eegs[:, :, :-1], base_eegs.data)

    def test_eeg_read_keep_buffer_butterworth_filtered(self):
        # filtering
        # # orig ptsa returns extra time point that's why eegs[:,:,:-1]
        eegs = self.eegs[:, :, :-1]
        eegs_filtered = eegs.filtered([58, 62], filt_type='stop', order=4)

        # -------------------TimeSeriesX
        base_eegs = self.base_eegs
        base_eegs_filtered_direct = self.base_eegs.filtered([58, 62], filt_type='stop', order=4)

        b_filter = ButterworthFiler(time_series=base_eegs, freq_range=[58, 62], filt_type='stop', order=4)

        base_eegs_filtered = b_filter.filter()

        # ---------------- testing
        # assert_array_almost_equal(eegs_filtered[:,:,:], base_eegs_filtered.data, decimal=2)
        assert_array_equal(eegs_filtered[:, :, :], base_eegs_filtered.data)
        assert_array_equal(eegs_filtered[:, :, :], base_eegs_filtered_direct.data)

    def test_eeg_resample(self):
        # # orig ptsa returns extra stime point that's why eegs[:,:,:-1]
        eegs = self.eegs[:, :, :-1]

        # filtering
        eegs_resampled = eegs.resampled(100.0)

        # -------------------TimeSeriesX
        base_eegs = self.base_eegs

        resample_filter = ResampleFilter(time_series=base_eegs, resamplerate=100.0)

        base_eegs_resampled = resample_filter.filter()

        base_eegs_resampled_direct = base_eegs.resampled(resampled_rate=100.0)

        # -------------- testing
        assert_array_equal(eegs_resampled, base_eegs_resampled.data)
        assert_array_equal(eegs_resampled, base_eegs_resampled_direct.data)


    def test_ts_convenience_fcns(self):
        # # orig ptsa returns extra stime point that's why eegs[:,:,:-1]
        eegs = self.eegs[:, :, :-1]
        base_eegs = self.base_eegs

        mean_eegs = eegs.mean(axis='time')
        mean_base_eegs = base_eegs.mean(dim='time')
        assert_array_equal(mean_eegs, mean_base_eegs)

        min_eegs = eegs.min(axis='time')
        min_base_eegs = base_eegs.min(dim='time')
        assert_array_equal(min_eegs, min_base_eegs)

        max_eegs = eegs.max(axis='time')
        max_base_eegs = base_eegs.max(dim='time')
        assert_array_equal(max_eegs, max_base_eegs)


        cumsum_eegs = eegs.cumsum(axis='time')
        cumsum_base_eegs = np.cumsum(base_eegs,axis=base_eegs.get_axis_num('time'))
        assert_array_equal(cumsum_eegs, cumsum_base_eegs)

        cumprod_eegs = eegs.cumprod(axis='time')
        cumprod_base_eegs = np.cumprod(base_eegs,axis=base_eegs.get_axis_num('time'))
        assert_array_equal(cumprod_eegs, cumprod_base_eegs)

        std_eegs = eegs.std(axis='time')
        std_base_eegs = base_eegs.std(dim='time')
        assert_array_equal(std_eegs, std_base_eegs)

        sum_eegs = eegs.sum(axis='time')
        sum_base_eegs = base_eegs.sum(dim='time')
        assert_array_equal(sum_eegs, sum_base_eegs)

        argmin_eegs = eegs.argmin(axis='time')
        argmin_base_eegs = base_eegs.argmin(dim='time')
        assert_array_equal(argmin_eegs, argmin_base_eegs)

        argmax_eegs = eegs.argmax(axis='time')
        argmax_base_eegs = base_eegs.argmax(dim='time')
        assert_array_equal(argmax_eegs, argmax_base_eegs)

        argsort_eegs = eegs.argsort(axis='time')
        argsort_base_eegs = np.argsort(base_eegs,axis=base_eegs.get_axis_num('time'))
        assert_array_equal(argsort_eegs, argsort_base_eegs)
                
        # could not get compress to work using timeseries.compress method 
        # compress_eegs = eegs.compress(condition=[0,2], axis='time')
        # compress_base_eegs = np.compress(condition=[0,1], a=base_eegs.data, axis=base_eegs.get_axis_num('channels'))
        # assert_array_equal(compress_eegs, compress_base_eegs)

        diagonal_eegs = eegs.diagonal(offset=0, axis1=1, axis2=2)
        diagonal_base_eegs = np.diagonal(base_eegs,offset=0, axis1=1,axis2=2)
        assert_array_equal(diagonal_eegs, diagonal_base_eegs)

        flatten_eegs = eegs.flatten()
        flatten_base_eegs = base_eegs.data.flatten()
        assert_array_equal(flatten_eegs, flatten_base_eegs)

        prod_eegs = eegs.prod(axis='channels')
        prod_base_eegs = base_eegs.prod(dim = 'channels')
        assert_array_equal(prod_eegs, prod_base_eegs)

        ptp_eegs = eegs.ptp(axis='channels')
        ptp_base_eegs = np.ptp(base_eegs.data, axis = base_eegs.get_axis_num('channels'))
        assert_array_equal(ptp_eegs, ptp_base_eegs)

        ravel_eegs = eegs.ravel()
        ravel_base_eegs = np.ravel(base_eegs)
        assert_array_equal(ravel_eegs, ravel_base_eegs)

        repeat_eegs = eegs.repeat(repeats=2, axis='channels')
        repeat_base_eegs = np.repeat(base_eegs.data, repeats=2, axis=base_eegs.get_axis_num('channels'))
        assert_array_equal(repeat_eegs, repeat_base_eegs)

        swapaxes_eegs = eegs.swapaxes(axis1='channels',axis2='events')
        swapaxes_base_eegs = base_eegs.transpose('events','channels','time')
        assert_array_equal(swapaxes_eegs , swapaxes_base_eegs)

        take_eegs = eegs.take(indices=[2,4,6,8],axis='events')
        take_base_eegs = base_eegs.isel(events=[2,4,6,8])
        assert_array_equal(take_eegs , take_base_eegs)
        
        trace_eegs = eegs.trace(offset=0, axis1=0,axis2=2)
        trace_base_eegs = np.trace(base_eegs, offset=0, axis1=base_eegs.get_axis_num('channels'),
                                   axis2=base_eegs.get_axis_num('time'))
        assert_array_equal(trace_eegs , trace_base_eegs)
        
        var_eegs = eegs.var(axis='time')
        var_base_eegs = base_eegs.var(dim='time')
        assert_array_equal(var_eegs, var_base_eegs)
        


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
