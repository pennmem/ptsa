__author__ = 'm'

import time
import numpy as np
import ptsa.data.common.xr as xr
from ptsa.data.TimeSeriesX import TimeSeriesX
from ptsa.data.common import TypeValTuple, PropertiedObject
from ptsa.data.filters import BaseFilter
# from ptsa.extensions import morlet
# from ptsa.extensions.morlet.morlet import MorletWaveletTransform
from ptsa.extensions import MorletWaveletTransform
from ptsa.extensions import morlet


class MorletWaveletFilterCppLegacy(PropertiedObject, BaseFilter):
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

        # if self.output != 'power':
        #     raise ValueError('Current implementation of '+self.__class__.__name__+' supports wavelet powers only')

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
        if source_array is None or target_array is None: return

        num_wavelets = self.freqs.shape[0]
        time_axis_size = self.time_series.shape[-1]
        for w in xrange(num_wavelets):
            out_idx_tuple = idx_tuple + (w,)
            target_array[out_idx_tuple] = source_array[w * time_axis_size:(w + 1) * time_axis_size]

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
                coords['offsets'] = ('time', self.time_series['offsets'])

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
        # powers=np.empty(shape=(time_axis_size*num_wavelets,), dtype=np.float)


        powers = np.array([], dtype=np.float)
        phases = np.array([], dtype=np.float)
        wavelets_complex_reshaped = np.array([[]], dtype=np.complex)

        if self.output == 'power':
            powers = np.empty(shape=(time_axis_size * num_wavelets,), dtype=np.float)
        if self.output == 'phase':
            phases = np.empty(shape=(time_axis_size * num_wavelets,), dtype=np.float)
        if self.output == 'both':
            powers = np.empty(shape=(time_axis_size * num_wavelets,), dtype=np.float)
            phases = np.empty(shape=(time_axis_size * num_wavelets,), dtype=np.float)

        morlet_transform = MorletWaveletTransform()
        morlet_transform.init_flex(self.width, self.freqs, samplerate, time_axis_size)

        wavelet_start = time.time()

        if self.output in ('phase', 'both'):
            for idx_tuple, signal in data_iterator:
                morlet_transform.multiphasevec(signal, powers, phases)
                self.store(idx_tuple, wavelet_pow_array, powers)
                self.store(idx_tuple, wavelet_phase_array, phases)
        elif self.output == 'power':
            for idx_tuple, signal in data_iterator:
                morlet_transform.multiphasevec(signal, powers)
                self.store(idx_tuple, wavelet_pow_array, powers)

        if self.verbose:
            print('total time wavelet loop: ', time.time() - wavelet_start)

        return self.build_output_arrays(wavelet_pow_array, wavelet_phase_array, time_axis)


