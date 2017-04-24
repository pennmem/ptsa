import time
import numpy as np
from ptsa.data.TimeSeriesX import TimeSeriesX
from ptsa.data.common import TypeValTuple, PropertiedObject
from ptsa.data.filters import BaseFilter
from ptsa.extensions.morlet.morlet import MorletWaveletTransformMP
from ptsa.extensions import morlet


class MorletWaveletFilterCpp(PropertiedObject, BaseFilter):
    _descriptors = [
        TypeValTuple('freqs', np.ndarray, np.array([], dtype=np.float)),
        TypeValTuple('width', int, 5),
        TypeValTuple('output', str, 'power'),
        TypeValTuple('frequency_dim_pos', int, 0),
        TypeValTuple('cpus', int, 1),
        # NOTE in this implementation the default position of frequency is -2
        TypeValTuple('verbose', bool, True),
    ]

    def __init__(self, time_series, **kwds):

        self.window = None
        self.time_series = time_series
        self.init_attrs(kwds)

    def filter(self):

        time_axis = self.time_series['time']

        time_axis_size = time_axis.shape[0]
        samplerate = float(self.time_series['samplerate'])

        wavelet_dims = self.time_series.shape[:-1] + (self.freqs.shape[0],)
        print(wavelet_dims)

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

        # mt = morlet.MorletWaveletTransformMP(self.cpus)
        # mt = MorletWaveletTransformMP(self.cpus)
        mt = MorletWaveletTransformMP(self.cpus)


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
            powers_ts = TimeSeriesX(powers_final,
                                    dims=self.time_series.dims[:-1] + ('frequency', self.time_series.dims[-1],),
                                    coords=coords
                                    )
            final_dims = (powers_ts.dims[-2],) + powers_ts.dims[:-2] + (powers_ts.dims[-1],)

            powers_ts = powers_ts.transpose(*final_dims)

        if phases_final is not None:
            phases_ts = TimeSeriesX(phases_final,
                                    dims=self.time_series.dims[:-1] + ('frequency', self.time_series.dims[-1],),
                                    coords=coords
                                    )

            final_dims = (phases_ts.dims[-2],) + phases_ts.dims[:-2] + (phases_ts.dims[-1],)

            phases_ts = phases_ts.transpose(*final_dims)

        if wavelet_complex_final is not None:
            wavelet_complex_ts = TimeSeriesX(wavelet_complex_final,
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
