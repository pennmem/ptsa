import time

import numpy as np
import traits.api

from ptsa.data.timeseries import TimeSeries
from ptsa.data.filters import BaseFilter
from ptsa.extensions import morlet


class MorletWaveletFilter(BaseFilter):
    """Applies a Morlet wavelet transform to a time series, returning the power
    and phase spectra over time.

    .. versionchanged:: 2.0

        Return type is now a :class:`TimeSeries` to conform with other
        filter types.

    Parameters
    ----------
    timeseries: TimeSeries
        The time series to filter

    Keyword Arguments
    -----------------
    freqs: np.ndarray
        The frequencies to use in the decomposition
    width: int
        The width of the wavelet
    output: List[str] or str
        A string or a list of strings containing power, phase, and/or
        complex (default: ``['power', 'phase']``)
    verbose: bool
        Print out the wavelet parameters
    cpus : int
        Number of threads to use when computing the transform (default: 1).

    """
    freqs = traits.api.CArray
    width = traits.api.Int
    output = traits.api.Str
    verbose = traits.api.Bool
    cpus = traits.api.Int

    def __init__(self, timeseries, freqs, width=5,
                 output=['power', 'phase'], verbose=True, cpus=1):
        super(MorletWaveletFilter, self).__init__(timeseries)
        self.freqs = freqs
        self.width = width

        output_opts = ['power', 'phase', 'complex']

        if isinstance(output, str):
            output = [output]

        for el in output:
            if el not in output_opts:
                raise RuntimeError("output must be one of %r" % output_opts)

        self.output = output

        self.verbose = verbose
        self.cpus = cpus
        self.window = None

        self.compute_power_and_phase_fcn = None

    def filter(self):
        """Apply the constructed filter."""
        time_axis = self.timeseries['time']

        wavelet_dims = self.nontime_sizes + (self.freqs.shape[0],)

        powers_reshaped = np.array([[]], dtype=np.float)
        phases_reshaped = np.array([[]], dtype=np.float)
        wavelets_complex_reshaped = np.array([[]], dtype=np.complex)

        if 'power' in self.output:
            powers_reshaped = np.empty(
                shape=(np.prod(wavelet_dims),
                       len(self.timeseries['time'])), dtype=np.float)
        if 'phase' in self.output:
            phases_reshaped = np.empty(
                shape=(np.prod(wavelet_dims),
                       len(self.timeseries['time'])), dtype=np.float)
        if 'complex' in self.output:
            wavelets_complex_reshaped = np.empty(
                shape=(np.prod(wavelet_dims), len(self.timeseries['time'])),
                dtype=np.complex)

        mt = morlet.MorletWaveletTransformMP(self.cpus)

        timeseries_reshaped = np.ascontiguousarray(
            self.timeseries.data.reshape(
                np.prod(self.nontime_sizes, dtype=int),
                len(self.timeseries['time'])), self.timeseries.data.dtype)

        if self.output == ['power']:
            mt.set_output_type(morlet.POWER)
        if self.output == ['phase']:
            mt.set_output_type(morlet.PHASE)
        if 'power' in self.output and 'phase' in self.output:
            mt.set_output_type(morlet.BOTH)

        # FIXME: update to allow outputing complex as well as power/phase
        if self.output == ['complex']:
            mt.set_output_type(morlet.COMPLEX)

        mt.set_signal_array(timeseries_reshaped)
        mt.set_wavelet_pow_array(powers_reshaped)
        mt.set_wavelet_phase_array(phases_reshaped)
        mt.set_wavelet_complex_array(wavelets_complex_reshaped)

        mt.initialize_signal_props(float(self.timeseries['samplerate']))
        mt.initialize_wavelet_props(self.width, self.freqs)
        mt.prepare_run()

        s = time.time()
        mt.compute_wavelets_threads()

        powers_final = None
        phases_final = None
        wavelet_complex_final = None

        if 'power' in self.output:
            powers_final = powers_reshaped.reshape(wavelet_dims + (len(self.timeseries['time']),))
        if 'phase' in self.output:
            phases_final = phases_reshaped.reshape(wavelet_dims + (len(self.timeseries['time']),))
        if 'complex' in self.output:
            wavelet_complex_final = wavelets_complex_reshaped.reshape(wavelet_dims + (len(self.timeseries['time']),))

        coords = {k: v for k, v in list(self.timeseries.coords.items())}
        coords['frequency'] = self.freqs

        powers_ts = None
        phases_ts = None
        wavelet_complex_ts = None

        if powers_final is not None:
            powers_ts = TimeSeries(powers_final,
                                   dims=self.nontime_dims + ('frequency', 'time',),
                                   coords=coords)
            final_dims = (powers_ts.dims[-2],) + powers_ts.dims[:-2] + (powers_ts.dims[-1],)

            powers_ts = powers_ts.transpose(*final_dims)

        if phases_final is not None:
            phases_ts = TimeSeries(phases_final,
                                   dims=self.nontime_dims + ('frequency','time'),
                                   coords=coords)

            final_dims = (phases_ts.dims[-2],) + phases_ts.dims[:-2] + (phases_ts.dims[-1],)

            phases_ts = phases_ts.transpose(*final_dims)

        if wavelet_complex_final is not None:
            wavelet_complex_ts = TimeSeries(wavelet_complex_final,
                                            dims=self.nontime_dims + (
                                             'frequency', 'time',),
                                            coords=coords)

            final_dims = (wavelet_complex_ts.dims[-2],) + wavelet_complex_ts.dims[:-2] + (wavelet_complex_ts.dims[-1],)

            wavelet_complex_ts = wavelet_complex_ts.transpose(*final_dims)

        if self.verbose:
            print('CPP total time wavelet loop: ', time.time() - s)

        # TODO: return a single TimeSeries
        return {
            'power': powers_ts,
            'phase': phases_ts,
            'complex': wavelet_complex_ts
        }
