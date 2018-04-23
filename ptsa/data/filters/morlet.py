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
