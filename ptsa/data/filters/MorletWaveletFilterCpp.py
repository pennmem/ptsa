__author__ = 'm'

import time
import numpy as np
import ptsa.data.common.xr as xr
from ptsa.data.TimeSeriesX import TimeSeriesX
from ptsa.data.common import TypeValTuple, PropertiedObject
from ptsa.data.filters import BaseFilter
import sys
sys.path.append('/Users/m/src/morlet_git_clion_install')
import morlet



class MorletWaveletFilterCpp(PropertiedObject,BaseFilter):
    _descriptors = [
        TypeValTuple('freqs', np.ndarray, np.array([], dtype=np.float)),
        TypeValTuple('width', int, 5),
        TypeValTuple('output', str, 'power'),
        TypeValTuple('frequency_dim_pos', int, 0),
        # NOTE in this implementation the default position of frequency is -2
        TypeValTuple('verbose', bool, True),
    ]

    def __init__(self, time_series, **kwds):

        self.window = None
        self.time_series = time_series
        self.init_attrs(kwds)

        if self.output != 'power':
            raise ValueError('Current implementation of '+self.__class__.__name__+' supports wavelet powers only')

    def all_but_time_iterator(self, array):
        from itertools import product
        sizes_except_time = np.asarray(array.shape)[:-1]
        ranges = map(lambda size: xrange(size), sizes_except_time)
        for cart_prod_idx_tuple in product(*ranges):
            yield cart_prod_idx_tuple, array[cart_prod_idx_tuple]

    def allocate_output_arrays(self, time_axis_size):
        array_type = np.float32
        shape = self.time_series.shape[:-1] + (self.freqs.shape[0], time_axis_size,)

        if self.output == 'power':
            return np.empty(shape=shape, dtype=array_type), None
        elif self.output == 'phase':
            return None, np.empty(shape=shape, dtype=array_type)
        else:
            return np.empty(shape=shape, dtype=array_type), np.empty(shape=shape, dtype=array_type)

    def store(self, idx_tuple, target_array, source_array):
        if source_array is None: return

        num_wavelets = self.freqs.shape[0]
        time_axis_size = self.time_series.shape[-1]
        for w in xrange(num_wavelets):
            out_idx_tuple = idx_tuple + (w,)
            target_array[out_idx_tuple] = source_array[w*time_axis_size:(w+1)*time_axis_size]

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


    def filter(self):

        data_iterator = self.get_data_iterator()

        time_axis = self.time_series['time']

        time_axis_size = time_axis.shape[0]
        samplerate = float(self.time_series['samplerate'])

        wavelet_pow_array, wavelet_phase_array = self.allocate_output_arrays(time_axis_size=time_axis_size)

        num_wavelets = self.freqs.shape[0]
        powers=np.empty(shape=(time_axis_size*num_wavelets,), dtype=np.float)
        morlet_transform = morlet.MorletWaveletTransform(self.width, self.freqs, samplerate, time_axis_size)


        wavelet_start = time.time()

        for idx_tuple, signal in data_iterator:
            morlet_transform.multiphasevec(signal,powers)
            self.store(idx_tuple, wavelet_pow_array, powers)


        if self.verbose:
            print 'total time wavelet loop: ', time.time() - wavelet_start

        return self.build_output_arrays(wavelet_pow_array, wavelet_phase_array, time_axis)



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

    print 'bipolar_pairs=', bipolar_pairs

    from ptsa.data.readers.EEGReader import EEGReader

    time_series_reader = EEGReader(events=base_events, start_time=0.0,channels=monopolar_channels, end_time=1.6, buffer_time=1.0)

    base_eegs = time_series_reader.read()

    # base_eegs = base_eegs[:, 0:10, :]
    # bipolar_pairs = bipolar_pairs[0:10]


    wf = MorletWaveletFilterCpp(time_series=base_eegs,
                             freqs=np.logspace(np.log10(3), np.log10(180), 8),
                             # freqs=np.array([3.]),
                             output='power',
                             )

    pow_wavelet, phase_wavelet = wf.filter()

    print 'total time = ', time.time() - start

    res_start = time.time()

    # from ptsa.data.filters.ResampleFilter import ResampleFilter
    # rsf = ResampleFilter (resamplerate=50.0)
    # rsf.set_input(pow_wavelet)
    # pow_wavelet = rsf.filter()



    print 'resample_time=', time.time() - res_start
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

    print 'bipolar_pairs=', bipolar_pairs

    from ptsa.data.readers.EEGReader import EEGReader

    time_series_reader = EEGReader(events=base_events, start_time=0.0,channels=monopolar_channels, end_time=1.6, buffer_time=1.0)

    base_eegs = time_series_reader.read()

    # base_eegs = base_eegs[:, 0:10, :]
    # bipolar_pairs = bipolar_pairs[0:10]

    from ptsa.data.filters import MorletWaveletFilter
    wf = MorletWaveletFilter(time_series=base_eegs,
                             freqs=np.logspace(np.log10(3), np.log10(180), 8),
                             # freqs=np.array([3.]),
                             output='power',
                             )

    pow_wavelet, phase_wavelet = wf.filter()

    print 'total time = ', time.time() - start

    res_start = time.time()

    # from ptsa.data.filters.ResampleFilter import ResampleFilter
    # rsf = ResampleFilter (resamplerate=50.0)
    # rsf.set_input(pow_wavelet)
    # pow_wavelet = rsf.filter()



    print 'resample_time=', time.time() - res_start
    return pow_wavelet



if __name__ == '__main__':
    edcw_2 = test_2()
    edcw_1 = test_1()

    #
    wavelet_1 = edcw_1[0, 0, 0, 500:1300]
    wavelet_2 = edcw_2[0, 0, 0, 500:1300]

    import matplotlib;

    matplotlib.use('Qt4Agg')

    import matplotlib.pyplot as plt

    plt.get_current_fig_manager().window.raise_()

    plt.plot(np.arange(wavelet_1.shape[0]) - 1, wavelet_1, 'k')
    plt.plot(np.arange(wavelet_2.shape[0]) - 1, wavelet_2, 'r--')

    plt.show()


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
