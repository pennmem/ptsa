__author__ = 'm'

import time

import numpy as np
import xarray as xr
from scipy.fftpack import fft, ifft

from ptsa.data.TimeSeriesX import TimeSeriesX
from ptsa.data.common import TypeValTuple, PropertiedObject
from ptsa.data.filters import BaseFilter
from ptsa.wavelet import morlet_multi, next_pow2


class MorletWaveletFilter(PropertiedObject,BaseFilter):
    _descriptors = [
        TypeValTuple('freqs', np.ndarray, np.array([], dtype=np.float)),
        TypeValTuple('width', int, 5),
        TypeValTuple('output', str, ''),
        TypeValTuple('frequency_dim_pos', int, 0),
        # NOTE in this implementation the default position of frequency is -2
        TypeValTuple('verbose', bool, True),
    ]

    def __init__(self, time_series, **kwds):

        self.window = None
        self.time_series = time_series
        self.init_attrs(kwds)

        self.compute_power_and_phase_fcn = None

        if self.output == 'power':
            self.compute_power_and_phase_fcn = self.compute_power
        elif self.output == 'phase':
            self.compute_power_and_phase_fcn = self.compute_phase
        else:
            self.compute_power_and_phase_fcn = self.compute_power_and_phase

    def all_but_time_iterator(self, array):
        from itertools import product
        sizes_except_time = np.asarray(array.shape)[:-1]
        ranges = map(lambda size: xrange(size), sizes_except_time)
        for cart_prod_idx_tuple in product(*ranges):
            yield cart_prod_idx_tuple, array[cart_prod_idx_tuple]

    def resample_time_axis(self):
        from ptsa.data.filters.ResampleFilter import ResampleFilter

        rs_time_axis = None  # resampled time axis
        if self.resamplerate > 0:

            rs_time_filter = ResampleFilter(resamplerate=self.resamplerate)
            rs_time_filter.set_input(self.time_series[0, 0, :])
            time_series_resampled = rs_time_filter.filter()
            rs_time_axis = time_series_resampled['time']
        else:
            rs_time_axis = self.time_series['time']

        return rs_time_axis, self.time_series['time']

    def allocate_output_arrays(self, time_axis_size):
        array_type = np.float32
        shape = self.time_series.shape[:-1] + (self.freqs.shape[0], time_axis_size,)

        if self.output == 'power':
            return np.empty(shape=shape, dtype=array_type), None
        elif self.output == 'phase':
            return None, np.empty(shape=shape, dtype=array_type)
        else:
            return np.empty(shape=shape, dtype=array_type), np.empty(shape=shape, dtype=array_type)

    def compute_power(self, wavelet_coef_array):
        # return wavelet_coef_array.real ** 2 + wavelet_coef_array.imag ** 2, None
        return np.abs(wavelet_coef_array) ** 2, None
        # # wavelet_coef_array.real ** 2 + wavelet_coef_array.imag ** 2, None

    def compute_phase(self, wavelet_coef_array):
        return None, np.angle(wavelet_coef_array)

    def compute_power_and_phase(self, wavelet_coef_array):
        return wavelet_coef_array.real ** 2 + wavelet_coef_array.imag ** 2, np.angle(wavelet_coef_array)

    def store(self, idx_tuple, target_array, source_array):
        if source_array is not None:
            target_array[idx_tuple] = source_array

    def get_data_iterator(self):
        return self.all_but_time_iterator(self.time_series)

    def construct_output_array(self, array, dims, coords):
        out_array = xr.DataArray(array, dims=dims, coords=coords)
        # out_array.attrs['samplerate'] = self.time_series.attrs['samplerate']
        out_array['samplerate'] = self.time_series['samplerate']
        return out_array

    def build_output_arrays(self, wavelet_pow_array, wavelet_phase_array, time_axis):
        wavelet_pow_array_xray = None
        wavelet_phase_array_xray = None

        if isinstance(self.time_series, xr.DataArray):

            dims = list(self.time_series.dims[:-1] + ('frequency', 'time',))

            transposed_dims = []

            # NOTE all computaitons up till this point assume that frequency position is -2 whereas
            # the default setting for this filter sets frequency axis index to 0. To avoid unnecessary transpositions
            # we need to adjust position of the frequency axis in the internal computations

            # getting frequency dim position as positive integer
            self.frequency_dim_pos = (len(dims) + self.frequency_dim_pos) % len(dims)
            orig_frequency_idx = dims.index('frequency')

            if self.frequency_dim_pos != orig_frequency_idx:
                transposed_dims = dims[:orig_frequency_idx] + dims[orig_frequency_idx + 1:]
                transposed_dims.insert(self.frequency_dim_pos, 'frequency')

            coords = {dim_name: self.time_series.coords[dim_name] for dim_name in self.time_series.dims[:-1]}
            coords['frequency'] = self.freqs
            coords['time'] = time_axis

            if 'offsets' in list(self.time_series.coords.keys()):
                coords['offsets'] = ('time',  self.time_series['offsets'])

            if wavelet_pow_array is not None:
                wavelet_pow_array_xray = self.construct_output_array(wavelet_pow_array, dims=dims, coords=coords)
            if wavelet_phase_array is not None:
                wavelet_phase_array_xray = self.construct_output_array(wavelet_phase_array, dims=dims, coords=coords)

            if wavelet_pow_array_xray is not None:
                wavelet_pow_array_xray = TimeSeriesX(wavelet_pow_array_xray)
                if len(transposed_dims):
                    wavelet_pow_array_xray = wavelet_pow_array_xray.transpose(*transposed_dims)

                wavelet_pow_array_xray.attrs = self.time_series.attrs.copy()

            if wavelet_phase_array_xray is not None:
                wavelet_phase_array_xray = TimeSeriesX(wavelet_phase_array_xray)
                if len(transposed_dims):
                    wavelet_phase_array_xray = wavelet_phase_array_xray.transpose(*transposed_dims)

                wavelet_phase_array_xray.attrs = self.time_series.attrs.copy()

            return wavelet_pow_array_xray, wavelet_phase_array_xray

    def compute_wavelet_ffts(self):

        # samplerate = self.time_series.attrs['samplerate']
        samplerate = float(self.time_series['samplerate'])

        freqs = np.atleast_1d(self.freqs)

        wavelets = morlet_multi(freqs=freqs, widths=self.width, samplerates=samplerate)
        # ADD WARNING HERE FROM PHASE_MULTI

        num_wavelets = len(wavelets)

        # computing length of the longest wavelet
        s_w = max(map(lambda wavelet: wavelet.shape[0], wavelets))

        time_series_length = self.time_series['time'].shape[0]

        if s_w > self.time_series['time'].shape[0]:
            raise ValueError(
                'Time series length (l_ts=%s) is shorter than maximum wavelet length (l_w=%s). '
                'Please use longer time series or increase lowest wavelet frequency ' %
                (time_series_length, s_w))

        # length of the tie axis of the time series
        s_d = self.time_series['time'].shape[0]

        # determine the size based on the next power of 2
        convolution_size = s_w + s_d - 1
        convolution_size_pow2 = np.power(2, next_pow2(convolution_size))

        # preallocating arrays
        # wavelet_fft_array = np.empty(shape=(num_wavelets, convolution_size_pow2), dtype=np.complex64)
        wavelet_fft_array = np.empty(shape=(num_wavelets, convolution_size_pow2), dtype=np.complex)
        convolution_size_array = np.empty(shape=(num_wavelets), dtype=np.int)

        # computting wavelet ffts
        for i, wavelet in enumerate(wavelets):
            wavelet_fft_array[i] = fft(wavelet, convolution_size_pow2)
            convolution_size_array[i] = wavelet.shape[0] + s_d - 1

        return wavelet_fft_array, convolution_size_array, convolution_size_pow2

    def filter(self):

        data_iterator = self.get_data_iterator()

        time_axis = self.time_series['time']

        time_axis_size = time_axis.shape[0]

        wavelet_pow_array, wavelet_phase_array = self.allocate_output_arrays(time_axis_size=time_axis_size)

        # preallocating array
        wavelet_coef_single_array = np.empty(shape=(time_axis_size), dtype=np.complex64)

        wavelet_fft_array, convolution_size_array, convolution_size_pow2 = self.compute_wavelet_ffts()
        num_wavelets = wavelet_fft_array.shape[0]

        wavelet_start = time.time()

        for idx_tuple, signal in data_iterator:

            signal_fft = fft(signal, convolution_size_pow2)

            for w in xrange(num_wavelets):
                signal_wavelet_conv = ifft(wavelet_fft_array[w] * signal_fft)

                # computting trim indices for the wavelet_coeff array
                start_offset = (convolution_size_array[w] - time_axis_size) / 2
                end_offset = start_offset + time_axis_size

                wavelet_coef_single_array[:] = signal_wavelet_conv[start_offset:end_offset]

                out_idx_tuple = idx_tuple + (w,)

                pow_array_single, phase_array_single = self.compute_power_and_phase_fcn(wavelet_coef_single_array)

                self.store(out_idx_tuple, wavelet_pow_array, pow_array_single)
                self.store(out_idx_tuple, wavelet_phase_array, phase_array_single)

        if self.verbose:
            print('total time wavelet loop: ', time.time() - wavelet_start)

        return self.build_output_arrays(wavelet_pow_array, wavelet_phase_array, time_axis)


def test_1_old():
    import time
    start = time.time()

    e_path = '/Users/m/data/events/RAM_FR1/R1060M_events.mat'

    from ptsa.data.readers import BaseEventReader

    base_e_reader = BaseEventReader(event_file=e_path, eliminate_events_with_no_eeg=True, use_ptsa_events_class=False)

    base_e_reader.read()

    base_events = base_e_reader.get_output()

    base_events = base_events[base_events.type == 'WORD']

    # selecting only one session
    base_events = base_events[base_events.eegfile == base_events[0].eegfile]

    from ptsa.data.readers.TalReader import TalReader
    tal_path = '/Users/m/data/eeg/R1060M/tal/R1060M_talLocs_database_bipol.mat'
    tal_reader = TalReader(tal_filename=tal_path)
    monopolar_channels = tal_reader.get_monopolar_channels()
    bipolar_pairs = tal_reader.get_bipolar_pairs()

    print('bipolar_pairs=', bipolar_pairs)

    from ptsa.data.experimental.TimeSeriesSessionEEGReader import TimeSeriesSessionEEGReader

    # time_series_reader = TimeSeriesSessionEEGReader(events=base_events, channels = ['002', '003', '004', '005'])
    time_series_reader = TimeSeriesSessionEEGReader(events=base_events, channels=monopolar_channels)
    ts_dict = time_series_reader.read()

    first_session_data = list(ts_dict.items())[0][1]

    print(first_session_data)

    wavelet_start = time.time()

    wf = MorletWaveletFilter(time_series=first_session_data,
                             freqs=np.logspace(np.log10(3), np.log10(180), 2),
                             # freqs=np.array([3.]),
                             output='power',
                             # resamplerate=50.0
                             )

    pow_wavelet, phase_wavelet = wf.filter()
    print('wavelet total time = ', time.time() - wavelet_start)
    # return pow_wavelet

    from ptsa.data.experimental.EventDataChopper import EventDataChopper
    edcw = EventDataChopper(events=base_events, event_duration=1.6, buffer=1.0,
                            data_dict={base_events[0].eegfile: pow_wavelet})

    chopped_wavelets = edcw.filter()

    chopped_wavelets = list(chopped_wavelets.items())[0][1]  # getting first item of return dictionary

    print('total time = ', time.time() - start)
    #
    # from ptsa.data.filters.ResampleFilter import ResampleFilter
    # rsf = ResampleFilter (resamplerate=50.0)
    # rsf.set_input(chopped_wavelets)
    # chopped_wavelets_resampled = rsf.filter()
    #
    # return chopped_wavelets_resampled
    return chopped_wavelets


def test_2_old():
    import time
    start = time.time()

    e_path = '/Users/m/data/events/RAM_FR1/R1060M_events.mat'

    from ptsa.data.readers import BaseEventReader

    base_e_reader = BaseEventReader(event_file=e_path, eliminate_events_with_no_eeg=True, use_ptsa_events_class=False)

    base_e_reader.read()

    base_events = base_e_reader.get_output()

    base_events = base_events[base_events.type == 'WORD']

    # selecting only one session
    base_events = base_events[base_events.eegfile == base_events[0].eegfile]

    from ptsa.data.readers.TalReader import TalReader
    tal_path = '/Users/m/data/eeg/R1060M/tal/R1060M_talLocs_database_bipol.mat'
    tal_reader = TalReader(tal_filename=tal_path)
    monopolar_channels = tal_reader.get_monopolar_channels()
    bipolar_pairs = tal_reader.get_bipolar_pairs()

    print('bipolar_pairs=', bipolar_pairs)

    from ptsa.data.experimental.TimeSeriesEEGReader import TimeSeriesEEGReader

    time_series_reader = TimeSeriesEEGReader(events=base_events, start_time=0.0,
                                             end_time=1.6, buffer_time=1.0, keep_buffer=True)

    base_eegs = time_series_reader.read(channels=monopolar_channels)

    # base_eegs = base_eegs[:, 0:10, :]
    # bipolar_pairs = bipolar_pairs[0:10]


    wf = MorletWaveletFilter(time_series=base_eegs,
                             freqs=np.logspace(np.log10(3), np.log10(180), 2),
                             # freqs=np.array([3.]),
                             output='power',
                             # resamplerate=50.0
                             )

    pow_wavelet, phase_wavelet = wf.filter()

    print('total time = ', time.time() - start)

    res_start = time.time()

    # from ptsa.data.filters.ResampleFilter import ResampleFilter
    # rsf = ResampleFilter (resamplerate=50.0)
    # rsf.set_input(pow_wavelet)
    # pow_wavelet = rsf.filter()



    print('resample_time=', time.time() - res_start)
    return pow_wavelet


def test_2():
    import time
    start = time.time()

    e_path = '/Users/m/data/events/RAM_FR1/R1060M_events.mat'

    from ptsa.data.readers import BaseEventReader

    base_e_reader = BaseEventReader(filename=e_path)

    base_events = base_e_reader.read()

    base_events = base_events[base_events.type == 'WORD']

    # selecting only one session
    base_events = base_events[base_events.eegfile == base_events[0].eegfile]

    from ptsa.data.readers.TalReader import TalReader
    tal_path = '/Users/m/data/eeg/R1060M/tal/R1060M_talLocs_database_bipol.mat'
    tal_reader = TalReader(filename=tal_path)
    monopolar_channels = tal_reader.get_monopolar_channels()
    bipolar_pairs = tal_reader.get_bipolar_pairs()

    print('bipolar_pairs=', bipolar_pairs)

    from ptsa.data.experimental.TimeSeriesEEGReader import TimeSeriesEEGReader

    time_series_reader = TimeSeriesEEGReader(events=base_events, start_time=0.0,
                                             end_time=1.6, buffer_time=1.0, keep_buffer=True)

    base_eegs = time_series_reader.read(channels=monopolar_channels)

    # base_eegs = base_eegs[:, 0:10, :]
    # bipolar_pairs = bipolar_pairs[0:10]


    wf = MorletWaveletFilter(time_series=base_eegs,
                             freqs=np.logspace(np.log10(3), np.log10(180), 2),
                             # freqs=np.array([3.]),
                             output='power',
                             )

    pow_wavelet, phase_wavelet = wf.filter()

    print('total time = ', time.time() - start)

    res_start = time.time()

    # from ptsa.data.filters.ResampleFilter import ResampleFilter
    # rsf = ResampleFilter (resamplerate=50.0)
    # rsf.set_input(pow_wavelet)
    # pow_wavelet = rsf.filter()



    print('resample_time=', time.time() - res_start)
    return pow_wavelet


def test_1():
    import time
    start = time.time()

    e_path = '/Users/m/data/events/RAM_FR1/R1060M_events.mat'

    from ptsa.data.readers import BaseEventReader

    base_e_reader = BaseEventReader(filename=e_path)

    base_events = base_e_reader.read()

    base_events = base_events[base_events.type == 'WORD']

    # selecting only one session
    base_events = base_events[base_events.eegfile == base_events[0].eegfile]

    from ptsa.data.readers.TalReader import TalReader
    tal_path = '/Users/m/data/eeg/R1060M/tal/R1060M_talLocs_database_bipol.mat'
    tal_reader = TalReader(filename=tal_path)
    monopolar_channels = tal_reader.get_monopolar_channels()
    bipolar_pairs = tal_reader.get_bipolar_pairs()

    dataroot = base_events[0].eegfile
    from ptsa.data.readers import EEGReader
    session_reader = EEGReader(session_dataroot=dataroot, channels=monopolar_channels)
    session_eegs = session_reader.read()

    wavelet_start = time.time()

    wf = MorletWaveletFilter(time_series=session_eegs,
                             freqs=np.logspace(np.log10(3), np.log10(180), 2),
                             # freqs=np.array([3.]),
                             output='power',
                             # resamplerate=50.0
                             )

    pow_wavelet, phase_wavelet = wf.filter()
    print('wavelet total time = ', time.time() - wavelet_start)
    # return pow_wavelet


    from ptsa.data.filters import EventDataChopper
    sedc = EventDataChopper(events=base_events, session_data=pow_wavelet, start_time=0.0, end_time=1.6, buffer_time=1.0)
    chopped_wavelets = sedc.filter()

    print('total time = ', time.time() - start)

    return chopped_wavelets


if __name__ == '__main__':
    edcw_1 = test_1()
    edcw_2 = test_2()

    wavelet_1 = edcw_1[0, 0, 0, 500:1300]
    wavelet_2 = edcw_2[0, 0, 0, 500:1300]

    import matplotlib;

    matplotlib.use('Qt4Agg')

    import matplotlib.pyplot as plt

    plt.get_current_fig_manager().window.raise_()

    plt.plot(np.arange(wavelet_1.shape[0]) - 1, wavelet_1, 'k')
    plt.plot(np.arange(wavelet_2.shape[0]) - 1, wavelet_2, 'r--')

    plt.show()
    #

# if __name__ == '__main__':
#     edcw_1 = test_1()
#     edcw_2 = test_2()
#
#     wavelet_1 = edcw_1[0,0,0,500:1300]
#     wavelet_2 = edcw_2[0,0,0,500:1300]
#
#     import matplotlib;
#     matplotlib.use('Qt4Agg')
#
#
#     import matplotlib.pyplot as plt
#     plt.get_current_fig_manager().window.raise_()
#
#
#     plt.plot(np.arange(wavelet_1.shape[0])-1,wavelet_1,'r--')
#     plt.plot(np.arange(wavelet_2.shape[0]),wavelet_2)
#
#
#     plt.show()


#
#     print

# if __name__=='__main__':
#
#
#
#     edcw = test_1()
#     pow_wavelet = test_2()
#
#     import matplotlib;
#     matplotlib.use('Qt4Agg')
#
#
#     import matplotlib.pyplot as plt
#     plt.get_current_fig_manager().window.raise_()
#
#
#
#     # pow_wavelet_res =  resample(pow_wavelet.data[0,1,3,500:-501],num=180)[50:]
#     # edcw_res =  resample(edcw.data[0,1,3,500:-501],num=180)[50:]
#
#     # pow_wavelet_res =  resample(pow_wavelet.data[0,1,3,:],num=180)[50:-50]
#     # edcw_res =  resample(edcw.data[0,1,3,:],num=180)[50:-50]
#
#     pow_wavelet_res =  pow_wavelet.data[0,1,3,50:-50]
#     edcw_res =  edcw.data[0,1,3,50:-50]
#
#
#
#     print
#
#
#
#
#     plt.plot(np.arange(pow_wavelet_res.shape[0]),pow_wavelet_res)
#     plt.plot(np.arange(edcw_res.shape[0])-0.5,edcw_res)
#
#
#     plt.show()
#
