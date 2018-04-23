import time

import numpy as np
from scipy.fftpack import fft, ifft
import traits.api
import xarray as xr

from ptsa.data.timeseries import TimeSeries
from ptsa.data.filters import BaseFilter
from ptsa.extensions import morlet
from ptsa.wavelet import morlet_multi, next_pow2


class MorletWaveletFilter(BaseFilter):
    """Applies a Morlet wavelet transform to a time series, returning the power
    and phase spectra over time.

    Parameters
    ----------
    time_series: TimeSeries
        The time series to filter

    Keyword Arguments
    -----------------
    freqs: np.ndarray
        The frequencies to use in the decomposition
    width: int
        The width of the wavelet
    output: str
        One of: 'power', 'phase', 'both', 'complex' (default: 'both')
    frequency_dim_pos: int
        The position of the new frequency axis in the output array
    verbose: bool
        Print out the wavelet parameters
    cpus : int
        Number of threads to use when computing the transform (default: 1).

    """
    freqs = traits.api.CArray
    width = traits.api.Int
    output = traits.api.Str
    frequency_dim_pos = traits.api.Int
    verbose = traits.api.Bool
    cpus = traits.api.Int

    def __init__(self, timeseries, freqs, width=5, output='both',
                 frequency_dim_pos=-2, verbose=True, cpus=1):
        super(MorletWaveletFilter, self).__init__(timeseries)
        self.freqs = freqs
        self.width = width
        self.output = output
        self.frequency_dim_pos = frequency_dim_pos
        self.verbose = verbose
        self.cpus = cpus
        self.window = None

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
        ranges = map(lambda size: range(size), sizes_except_time)
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
            if 'samplerate' not in coords:
                coords['samplerate'] = self.time_series.coords['samplerate']

            if 'offsets' in list(self.time_series.coords.keys()):
                coords['offsets'] = ('time',  self.time_series['offsets'])

            if wavelet_pow_array is not None:
                wavelet_pow_array_xray = TimeSeries(wavelet_pow_array, coords=coords, dims=dims)
                if len(transposed_dims):
                    wavelet_pow_array_xray = wavelet_pow_array_xray.transpose(*transposed_dims)

                wavelet_pow_array_xray.attrs = self.time_series.attrs.copy()

            if wavelet_phase_array is not None:
                wavelet_phase_array_xray = TimeSeries(wavelet_phase_array, coords=coords, dims=dims)
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
        """Apply the constructed filter.

        Returns
        -------
        (power,phase): tuple(TimeSeries or None, TimeSeries or None)
            Returns a tuple containing the computed power and phase values.
        """

        time_axis = self.time_series['time']

        time_axis_size = time_axis.shape[0]
        samplerate = float(self.time_series['samplerate'])

        wavelet_dims = self.time_series.shape[:-1] + (self.freqs.shape[0],)

        powers_reshaped = np.array([[]], dtype=np.float)
        phases_reshaped = np.array([[]], dtype=np.float)
        wavelets_complex_reshaped = np.array([[]], dtype=np.complex)

        if self.output == 'power':
            powers_reshaped = np.empty(shape=(np.prod(wavelet_dims), self.time_series.shape[-1]), dtype=np.float)
        if self.output == 'phase':
            phases_reshaped = np.empty(shape=(np.prod(wavelet_dims), self.time_series.shape[-1]), dtype=np.float)
        if self.output == 'both':
            powers_reshaped = np.empty(shape=(np.prod(wavelet_dims), self.time_series.shape[-1]), dtype=np.float)
            phases_reshaped = np.empty(shape=(np.prod(wavelet_dims), self.time_series.shape[-1]), dtype=np.float)
        if self.output == 'complex':
            wavelets_complex_reshaped = np.empty(shape=(np.prod(wavelet_dims), self.time_series.shape[-1]),
                                                 dtype=np.complex)

        mt = morlet.MorletWaveletTransformMP(self.cpus)

        time_series_reshaped = np.ascontiguousarray(self.time_series.data.reshape(np.prod(self.time_series.shape[:-1]),
                                                    self.time_series.shape[-1]),self.time_series.data.dtype)
        if self.output == 'power':
            mt.set_output_type(morlet.POWER)
        if self.output == 'phase':
            mt.set_output_type(morlet.PHASE)
        if self.output == 'both':
            mt.set_output_type(morlet.BOTH)
        if self.output == 'complex':
            mt.set_output_type(morlet.COMPLEX)

        mt.set_signal_array(time_series_reshaped)
        mt.set_wavelet_pow_array(powers_reshaped)
        mt.set_wavelet_phase_array(phases_reshaped)
        mt.set_wavelet_complex_array(wavelets_complex_reshaped)

        # mt.initialize_arrays(time_series_reshaped, wavelets_reshaped)

        mt.initialize_signal_props(float(self.time_series['samplerate']))
        mt.initialize_wavelet_props(self.width, self.freqs)
        mt.prepare_run()

        s = time.time()
        mt.compute_wavelets_threads()

        powers_final = None
        phases_final = None
        wavelet_complex_final = None

        if self.output == 'power':
            powers_final = powers_reshaped.reshape(wavelet_dims + (self.time_series.shape[-1],))
        if self.output == 'phase':
            phases_final = phases_reshaped.reshape(wavelet_dims + (self.time_series.shape[-1],))
        if self.output == 'both':
            powers_final = powers_reshaped.reshape(wavelet_dims + (self.time_series.shape[-1],))
            phases_final = phases_reshaped.reshape(wavelet_dims + (self.time_series.shape[-1],))
        if self.output == 'complex':
            wavelet_complex_final = wavelets_complex_reshaped.reshape(wavelet_dims + (self.time_series.shape[-1],))

        # wavelets_final = powers_reshaped.reshape( wavelet_dims+(self.time_series.shape[-1],) )

        coords = {k: v for k, v in list(self.time_series.coords.items())}
        coords['frequency'] = self.freqs

        powers_ts = None
        phases_ts = None
        wavelet_complex_ts = None

        if powers_final is not None:
            powers_ts = TimeSeries(powers_final,
                                   dims=self.time_series.dims[:-1] + ('frequency', self.time_series.dims[-1],),
                                   coords=coords
                                   )
            final_dims = (powers_ts.dims[-2],) + powers_ts.dims[:-2] + (powers_ts.dims[-1],)

            powers_ts = powers_ts.transpose(*final_dims)

        if phases_final is not None:
            phases_ts = TimeSeries(phases_final,
                                   dims=self.time_series.dims[:-1] + ('frequency', self.time_series.dims[-1],),
                                   coords=coords
                                   )

            final_dims = (phases_ts.dims[-2],) + phases_ts.dims[:-2] + (phases_ts.dims[-1],)

            phases_ts = phases_ts.transpose(*final_dims)

        if wavelet_complex_final is not None:
            wavelet_complex_ts = TimeSeries(wavelet_complex_final,
                                            dims=self.time_series.dims[:-1] + (
                                             'frequency', self.time_series.dims[-1],),
                                            coords=coords
                                            )

            final_dims = (wavelet_complex_ts.dims[-2],) + wavelet_complex_ts.dims[:-2] + (wavelet_complex_ts.dims[-1],)

            wavelet_complex_ts = wavelet_complex_ts.transpose(*final_dims)

        if self.verbose:
            print('CPP total time wavelet loop: ', time.time() - s)

        if wavelet_complex_ts is not None:
            return wavelet_complex_ts, None
        else:
            return powers_ts, phases_ts
