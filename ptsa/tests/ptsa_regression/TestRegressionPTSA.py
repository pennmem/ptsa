__author__ = 'm'

import sys
import numpy as np
from numpy.testing import *
import unittest
# from unittest import *

from EventReadersTestBase import EventReadersTestBase
from ptsa.data.events import Events
from ptsa.data.readers import BaseEventReader
from ptsa.data.readers import PTSAEventReader
from ptsa.data.readers.EEGReader import EEGReader
from ptsa.data.readers.TalReader import TalReader
from ptsa.data.filters.ButterworthFilter import ButterworthFilter
from ptsa.data.filters.ResampleFilter import ResampleFilter
from ptsa.data.filters import EventDataChopper
from ptsa.data.filters.MorletWaveletFilter import MorletWaveletFilter
from ptsa.data.TimeSeriesX import TimeSeriesX
from ptsa.data.timeseries import TimeSeries


# class TestRegressionPTSA(unittest.TestCase, EventReadersTestBase):
class TestRegressionPTSA(unittest.TestCase):
    # class TestRegressionPTSA(unittest.TestCase):
    def setUp(self):
        self.event_range = range(0, 30, 1)
        self.e_path = '/Users/m/data/events/RAM_FR1/R1060M_events.mat'
        self.tal_path = '/Users/m/data/eeg/R1060M/tal/R1060M_talLocs_database_bipol.mat'

        # --------------- TAL STRUCTS READ
        tal_reader = TalReader(filename=self.tal_path)
        self.monopolar_channels = tal_reader.get_monopolar_channels()


        # ---------------- ORIG PTSA -------------------
        e_reader = PTSAEventReader(filename=self.e_path, eliminate_events_with_no_eeg=True)
        events = e_reader.read()

        events = events[events.type == 'WORD']

        events = events[self.event_range]

        ev_order = np.argsort(events, order=('session','list','mstime'))
        self.events = events[ev_order]

        # self.events = self.read_ptsa_events()

        # in case fancy indexing looses Eventness of events we need to create Events object explicitely
        if not isinstance(self.events, Events):
            self.events = Events(self.events)

        start_time = 0.0
        end_time = 1.6
        buffer_time = 1.0

        self.eegs = self.events.get_data(channels=['002', '003'], start_time=start_time, end_time=end_time,
                                         buffer_time=buffer_time, eoffset='eegoffset', keep_buffer=True,
                                         eoffset_in_time=False, verbose=True)

        # ---------------- NEW STYLE PTSA -------------------
        base_e_reader = BaseEventReader(filename=self.e_path, eliminate_events_with_no_eeg=True)

        base_events = base_e_reader.read()

        base_events = base_events[base_events.type == 'WORD']

        base_ev_order = np.argsort(base_events, order=('session','list','mstime'))
        base_events = base_events[base_ev_order]

        self.base_events = base_events[self.event_range]

        # self.base_events = self.read_base_events()

        eeg_reader = EEGReader(events=self.base_events, channels=np.array(['002', '003']),
                               start_time=start_time, end_time=end_time, buffer_time=buffer_time)

        self.base_eegs = eeg_reader.read()

    def test_time_series_mirror(self):
        duration = 1.0
        mirrored_buf_eegs = self.base_eegs.add_mirror_buffer(duration=duration)

        samplerate = float(self.base_eegs['samplerate'])
        nb_ = int(np.ceil(samplerate * duration))

        assert_array_equal(self.base_eegs[...,1:nb_+1], mirrored_buf_eegs[...,:nb_][...,::-1])
        print mirrored_buf_eegs

    def test_missing_data_read(self):
        self.e_path = '/Volumes/rhino_root/data/events/RAM_PS/R1104D_events.mat'
        base_e_reader = BaseEventReader(filename=self.e_path)
        base_events = base_e_reader.read()
        print 'base_events=',base_events


    def test_full_session_read(self):


        # ---------------- ORIG PTSA -------------------
        e_reader = PTSAEventReader(filename=self.e_path, eliminate_events_with_no_eeg=True)
        events = e_reader.read()

        events = events[events.type == 'WORD']

        events = events[self.event_range]

        ev_order = np.argsort(events, order=('session','list','mstime'))
        self.events = events[ev_order]

        # self.events = self.read_ptsa_events()

        # in case fancy indexing looses Eventness of events we need to create Events object explicitely
        if not isinstance(self.events, Events):
            self.events = Events(self.events)

        eegs = self.events.get_data(channels=self.monopolar_channels, start_time=0.0, end_time=1.6,
                                         buffer_time=1.0, eoffset='eegoffset', keep_buffer=True,
                                         eoffset_in_time=False, verbose=True)

        # removing last entry to match dimensions - ptsa adds one extra element at the end of time axis
        eegs = eegs[:,:,:-1]
        eeg_reader = EEGReader(events=self.base_events, channels=self.monopolar_channels,
                               start_time=0.0, end_time=1.6, buffer_time=1.0)


        base_eegs = eeg_reader.read()

        assert_array_equal(x=eegs, y=base_eegs)
        # checking if axes match
        assert_array_equal(np.array(eegs['channels']['name']), base_eegs['channels'].data)
        assert_array_almost_equal(np.array(eegs['time']), base_eegs['time'].data, decimal=3)
        assert_array_equal(np.array(eegs['events']['item']), base_eegs['events'].data['item'])


        print



    def test_ptsa_event_ordering(self):
        # --------------------OROG PTSA - one raw bin wrapper per event
        e_reader = PTSAEventReader(filename=self.e_path, eliminate_events_with_no_eeg=True, use_groupped_rawbinwrapper=False)
        events = e_reader.read()

        events = events[events.type == 'WORD']

        events = events[self.event_range]

        if not isinstance(events, Events):
            events = Events(events)

        eegs = events.get_data(channels=['002', '003'], start_time=0.0, end_time=1.6,
                                         buffer_time=1.0, eoffset='eegoffset', keep_buffer=True,
                                         eoffset_in_time=False, verbose=True)

        eegs = eegs[:,:,:-1]
        words_ptsa = eegs['events']['item']
        print 'words_ptsa=',words_ptsa


        words = self.base_eegs['events'].data['item']


        print words

        assert_array_equal(np.array(words_ptsa),words)

        assert_array_equal(eegs, self.base_eegs)


    def test_eeg_read(self):
        # base_eegs = self.base_eegs.remove_buffer(duration=1.0)
        # eegs = self.eegs.remove_buffer(duration=1.0)

        base_eegs = self.base_eegs
        eegs = self.eegs


        # orig ptsa returns extra stime point that's why eegs[:,:,:-1]
        # assert_array_equal(eegs[:, :, :-1], base_eegs.data)
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

        b_filter = ButterworthFilter(time_series=base_eegs, freq_range=[58, 62], filt_type='stop', order=4)

        base_eegs_filtered = b_filter.filter()

        # ---------------- testing
        # assert_array_almost_equal(eegs_filtered[:,:,:], base_eegs_filtered.data, decimal=2)
        assert_array_equal(eegs_filtered[:, :, :], base_eegs_filtered.data)
        assert_array_equal(eegs_filtered[:, :, :], base_eegs_filtered_direct.data)

        # checking filtering of just single time series
        eegs_0_0 = eegs[0,0]
        eegs_filtered_0_0 = eegs_0_0.filtered([58, 62], filt_type='stop', order=4)

        assert_array_equal(eegs_filtered_0_0, eegs_filtered[0,0])

        base_eegs[0:1,0:1].filtered([58, 62], filt_type='stop', order=4)





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

        base_eegs_resampled_direct_0_0 = base_eegs[0,0].resampled(resampled_rate=100.0)

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
        
    def test_wavelets(self):
        eegs = self.eegs[:, :, :-1]
        base_eegs = self.base_eegs

        wf = MorletWaveletFilter(time_series=base_eegs,
                                 freqs=np.logspace(np.log10(3), np.log10(180), 8),
                                 output='power',
                                 frequency_dim_pos=0,

                                 )

        pow_wavelet, phase_wavelet = wf.filter()
        print 'pow_wavelet=',pow_wavelet

        from ptsa.wavelet import phase_pow_multi
        pow_wavelet_ptsa_orig = phase_pow_multi(freqs=np.logspace(np.log10(3), np.log10(180), 8), dat=eegs,to_return='power')
        print 'pow_wavelets_ptsa_orig=',pow_wavelet_ptsa_orig


        # import matplotlib;
        # matplotlib.use('Qt4Agg')
        #
        #
        # import matplotlib.pyplot as plt
        # plt.get_current_fig_manager().window.raise_()
        #
        wavelet_1 = pow_wavelet[0,0,0,500:-500]
        wavelet_2 = pow_wavelet_ptsa_orig[0,0,0,500:-500]
        #
        # plt.plot(np.arange(wavelet_1.shape[0])-1,wavelet_1,'k')
        # plt.plot(np.arange(wavelet_2.shape[0])-1,wavelet_2,'r--')
        #
        # plt.show()

        assert_array_equal(eegs, base_eegs.data)
        # assert_array_equal(wavelet_1, wavelet_2)

        # assert_array_almost_equal((wavelet_1-wavelet_2)/wavelet_1, np.zeros_like(wavelet_1), decimal=4)
        # assert_array_almost_equal((pow_wavelet_ptsa_orig-pow_wavelet)/pow_wavelet_ptsa_orig, np.zeros_like(pow_wavelet), decimal=4)


        assert_array_almost_equal(
            (pow_wavelet_ptsa_orig-pow_wavelet)/pow_wavelet_ptsa_orig,
            np.zeros_like(pow_wavelet), decimal=6)


        freq_num = 7
        assert_array_equal(
            (pow_wavelet_ptsa_orig[freq_num,:,:,500:-500]-pow_wavelet[freq_num,:,:,500:-500])/pow_wavelet_ptsa_orig[freq_num,:,:,500:-500],
            np.zeros_like(pow_wavelet[freq_num,:,:,500:-500]))

    def test_wavelets_python_cpp(self):
        from ptsa.data.filters import MorletWaveletFilterCpp
        print 'hello'

        wf = MorletWaveletFilter(time_series=self.base_eegs,
                                 freqs=np.logspace(np.log10(3), np.log10(180), 8),
                                 output='power',
                                 )

        pow_wavelet, phase_wavelet = wf.filter()


        wf_cpp = MorletWaveletFilterCpp(time_series=self.base_eegs,
                                 freqs=np.logspace(np.log10(3), np.log10(180), 8),
                                 output='power',
                                 )

        pow_wavelet_cpp, phase_wavelet_cpp = wf_cpp.filter()

        decimal = 2
        freq_num=0

        from scipy.stats import describe

        desc_cpp = describe(pow_wavelet_cpp[freq_num,:,:,500:-500])
        desc_py = describe(pow_wavelet[freq_num,:,:,500:-500])

        try:
            assert_array_almost_equal(
                (pow_wavelet_cpp[freq_num,:,:,500:-500]-pow_wavelet[freq_num,:,:,500:-500])/pow_wavelet_cpp[freq_num,:,:,500:-500],
                np.zeros_like(pow_wavelet_cpp[freq_num,:,:,500:-500]), decimal=decimal)
        except AssertionError:
            print 'WARNING: Cpp and Python wavelets are not within 1%. Will try weaker test '

            mean_min = np.min((desc_cpp.mean-desc_py.mean)/desc_cpp.mean)
            mean_max = np.max((desc_cpp.mean-desc_py.mean)/desc_cpp.mean)
            print 'mean_max=',mean_max
            print 'mean_min=',mean_min


            self.assertTrue(np.abs(mean_max)<0.05)
            self.assertTrue(np.abs(mean_min)<0.05)


    def test_wavelets_cpp(self):


        eegs = self.eegs[:, :, :-1]
        base_eegs = self.base_eegs


        sys.path.append('/Users/m/src/morlet_git_install')
        import morlet
        num_freqs = 8
        f_min = 3.0
        f_max = 180.0
        signal_length = base_eegs.shape[-1]
        morlet_transform = morlet.MorletWaveletTransform()
        samplerate = float(base_eegs['samplerate'])
        morlet_transform.init(5, f_min, f_max, num_freqs, samplerate , signal_length)

        signal = base_eegs[0:1,0:1,:]
        signal_orig_eegs = eegs[0:1,0:1,:]

        pow_wavelets_cpp = np.empty(shape=(base_eegs.shape[-1]*num_freqs,), dtype=np.float)

        # for i in xrange(num_of_iterations):
        #     morlet_transform.multiphasevec(signal,powers)
        morlet_transform.multiphasevec(signal.data.flatten(),pow_wavelets_cpp)

        pow_wavelets_cpp = pow_wavelets_cpp.reshape(8,pow_wavelets_cpp.shape[0]/8)



        wf = MorletWaveletFilter(time_series=signal,
                                 freqs=np.logspace(np.log10(f_min), np.log10(f_max), num_freqs),
                                 output='power',
                                 frequency_dim_pos=0,

                                 )

        pow_wavelet, phase_wavelet = wf.filter()



        from ptsa.wavelet import phase_pow_multi
        pow_wavelet_ptsa_orig = phase_pow_multi(freqs=np.logspace(np.log10(3), np.log10(180), 8), dat=signal_orig_eegs,to_return='power')


        freq_num = 0

        decimal = 1

        assert_array_almost_equal(
            (np.squeeze(pow_wavelet[freq_num,:,:,500:-500])-np.squeeze(pow_wavelet_ptsa_orig[freq_num,:,:,500:-500]))/np.squeeze(pow_wavelet_ptsa_orig[freq_num,:,:,500:-500]),
            np.zeros_like(np.squeeze(pow_wavelet_ptsa_orig[freq_num,:,:,500:-500])), decimal=decimal)


        assert_array_almost_equal(
            (pow_wavelets_cpp[freq_num,500:-500]-np.squeeze(pow_wavelet[freq_num,:,:,500:-500]))/pow_wavelets_cpp[freq_num,500:-500],
            np.zeros_like(pow_wavelets_cpp[freq_num,500:-500]), decimal=decimal)

        #
        assert_array_almost_equal(
            (pow_wavelets_cpp[freq_num,500:-500]-np.squeeze(pow_wavelet_ptsa_orig[freq_num,:,:,500:-500]))/pow_wavelets_cpp[freq_num,500:-500],
            np.zeros_like(np.squeeze(pow_wavelet_ptsa_orig[freq_num,:,:,500:-500])), decimal=decimal)




        from ptsa.wavelet import phase_pow_multi

    def test_event_data_chopper(self):


        dataroot=self.base_events[0].eegfile
        from ptsa.data.readers import EEGReader
        session_reader = EEGReader(session_dataroot=dataroot, channels=self.monopolar_channels)
        session_eegs = session_reader.read()


        from ptsa.data.filters import EventDataChopper
        sedc = EventDataChopper(events=self.base_events, session_data=session_eegs, start_time=0.0, end_time=1.6, buffer_time=1.0)
        chopped_session = sedc.filter()

        from ptsa.data.filters import EventDataChopper
        sedc_so = EventDataChopper(start_offsets=self.base_events.eegoffset, session_data=session_eegs, start_time=0.0, end_time=1.6, buffer_time=1.0)
        chopped_session_so = sedc_so.filter()

        assert_array_equal(chopped_session,chopped_session_so)


    def test_wavelets_synthetic_data(self):
        samplerate = 1000.
        frequency = 180.0
        modulation_frequency = 80.0

        duration = 1.0

        n_points = int(np.round(duration*samplerate))
        x = np.arange(n_points, dtype=np.float)
        y = np.sin(x*(2*np.pi*frequency/n_points))
        y_mod = np.sin(x*(2*np.pi*frequency/n_points))* np.sin(x*(2*np.pi*modulation_frequency/n_points))

        ts = TimeSeriesX(y, dims=['time'], coords=[x])
        ts['samplerate']=samplerate
        ts.attrs['samplerate'] = samplerate

        frequencies = [ 10.0, 30.0, 50.0, 80., 120., 180., 250.0 , 300.0, 500.]
        for frequency  in frequencies:
            wf = MorletWaveletFilter(time_series=ts,
                                     freqs=np.array([frequency]),
                                     output='both',
                                     frequency_dim_pos=0,
                                     verbose=True
                                     )

            pow_wavelet, phase_wavelet = wf.filter()

            from ptsa.wavelet import phase_pow_multi


            pow_wavelet_ptsa_orig = phase_pow_multi(freqs=[frequency],samplerates=samplerate, dat=ts.data,to_return='power')


            assert_array_almost_equal(
                (pow_wavelet_ptsa_orig-pow_wavelet)/pow_wavelet_ptsa_orig,
                np.zeros_like(pow_wavelet), decimal=6)


if __name__ == '__main__':
    unittest.main(verbosity=2)

    # if __name__=='__main__':
    #     test_suite = unittest.TestSuite()
    #     # test_suite.addTest(unittest.makeSuite(TestEventRead))
    #     test_suite.addTest(unittest.makeSuite(TestRegressionPTSA))
    #
    #     # test_suite.addTest(unittest.makeSuite(test_morlet_multi))
    #
    #     runner=unittest.TextTestRunner()
    #     runner.run(test_suite)
