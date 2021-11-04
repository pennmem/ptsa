import time

import numpy as np
import traits.api

from ptsa.data.timeseries import TimeSeries
from ptsa.data.filters import BaseFilter
from ptsa.extensions import morlet


class MorletWaveletFilter(BaseFilter):
    """Applies a Morlet wavelet transform to a time series, returning the power
    and phase spectra over time.

    .. versionchanged:: 2.0.6

        Return type is now a :class:`TimeSeries` to conform with other
        filter types.

    Parameters
    ----------
    freqs: np.ndarray
        The frequencies to use in the decomposition
    
    Keyword Arguments
    -----------------
    width: int
        The width of the wavelet (default: 5)
    output: Union[Iterable[str], str]
        A string or a list of strings containing power, phase, and/or
        complex (default: ``['power', 'phase']``)
    verbose: bool
        Print out the wavelet parameters (default: False)
    cpus : int
        Number of threads to use when computing the transform (default: 1).
    output_dim: str
        Name of the output dimension when returning both power and phase
        (default: ``'output'``)
    complete: bool
        Use complete Morlet wavelets with a zero mean, which is required for
        power and phase accuracy with small wavelet widths.  The frequency is
        kept consistent with standard Morlet wavelets.  (default: True)

    """
    freqs = traits.api.CArray
    width = traits.api.Int
    verbose = traits.api.Bool
    cpus = traits.api.Int
    output = []
    output_dim = traits.api.Str

    def __init__(self, freqs, width=5, output=('power', 'phase'), 
                 verbose=True, cpus=1, output_dim='output', complete=True):
        self.freqs = freqs
        self.width = width
        self.complete = complete

        output_opts = ('power', 'phase', 'complex')

        if isinstance(output, str):
            output = [output]

        for el in output:
            if el not in output_opts:
                raise RuntimeError("invalid output option: {}".format(el))

        # TODO: update extension module to allow for this scenario
        if 'complex' in output and len(output) > 1:
            raise RuntimeError("complex output requires not also requesting power/phase")

        self.output = output

        self.verbose = verbose
        self.cpus = cpus
        self.output_dim = output_dim

    def filter(self, timeseries):
        """Apply the constructed filter."""
        nontime_dims = self.get_nontime_dims(timeseries)
        nontime_sizes = self.get_nontime_sizes(timeseries)

        wavelet_dims = nontime_sizes + (self.freqs.shape[0],)

        powers_reshaped = np.array([[]], dtype=float)
        phases_reshaped = np.array([[]], dtype=float)
        wavelets_complex_reshaped = np.array([[]], dtype=np.complex)

        if 'power' in self.output:
            powers_reshaped = np.empty(
                shape=(np.prod(wavelet_dims),
                       len(timeseries['time'])), dtype=float)
        if 'phase' in self.output:
            phases_reshaped = np.empty(
                shape=(np.prod(wavelet_dims),
                       len(timeseries['time'])), dtype=float)
        if 'complex' in self.output:
            wavelets_complex_reshaped = np.empty(
                shape=(np.prod(wavelet_dims), len(timeseries['time'])),
                dtype=np.complex)

        mt = morlet.MorletWaveletTransformMP(self.cpus)

        timeseries_reshaped = np.ascontiguousarray(
            timeseries.data.reshape(
                np.prod(nontime_sizes, dtype=int),
                len(timeseries['time'])), timeseries.data.dtype).astype(np.float64)

        if self.output == ['power']:
            mt.set_output_type(morlet.POWER)
        if self.output == ['phase']:
            mt.set_output_type(morlet.PHASE)
        if 'power' in self.output and 'phase' in self.output:
            mt.set_output_type(morlet.BOTH)

        # TODO: update to allow outputing complex as well as power/phase
        if self.output == ['complex']:
            mt.set_output_type(morlet.COMPLEX)

        mt.set_signal_array(timeseries_reshaped)
        mt.set_wavelet_pow_array(powers_reshaped)
        mt.set_wavelet_phase_array(phases_reshaped)
        mt.set_wavelet_complex_array(wavelets_complex_reshaped)

        mt.initialize_signal_props(float(timeseries['samplerate']))
        mt.initialize_wavelet_props(self.width, self.freqs, self.complete)
        mt.prepare_run()

        s = time.time()
        mt.compute_wavelets_threads()

        powers_final = None
        phases_final = None
        wavelet_complex_final = None

        if 'power' in self.output:
            powers_final = powers_reshaped.reshape(wavelet_dims + (len(timeseries['time']),))
        if 'phase' in self.output:
            phases_final = phases_reshaped.reshape(wavelet_dims + (len(timeseries['time']),))
        if 'complex' in self.output:
            wavelet_complex_final = wavelets_complex_reshaped.reshape(wavelet_dims + (len(timeseries['time']),))

        coords = {k: v for k, v in list(timeseries.coords.items())}
        coords['frequency'] = self.freqs

        powers_ts = None
        phases_ts = None
        wavelet_complex_ts = None

        if powers_final is not None:
            powers_ts = TimeSeries(powers_final,
                                   dims=nontime_dims + ('frequency', 'time'),
                                   coords=coords)
            final_dims = (powers_ts.dims[-2],) + powers_ts.dims[:-2] + (powers_ts.dims[-1],)

            powers_ts = powers_ts.transpose(*final_dims)

        if phases_final is not None:
            phases_ts = TimeSeries(phases_final,
                                   dims=nontime_dims + ('frequency', 'time'),
                                   coords=coords)

            final_dims = (phases_ts.dims[-2],) + phases_ts.dims[:-2] + (phases_ts.dims[-1],)

            phases_ts = phases_ts.transpose(*final_dims)

        if wavelet_complex_final is not None:
            wavelet_complex_ts = TimeSeries(wavelet_complex_final,
                                            dims=nontime_dims + (
                                             'frequency', 'time',),
                                            coords=coords)

            final_dims = (wavelet_complex_ts.dims[-2],) + wavelet_complex_ts.dims[:-2] + (wavelet_complex_ts.dims[-1],)

            wavelet_complex_ts = wavelet_complex_ts.transpose(*final_dims)

        if self.verbose:
            print('CPP total time wavelet loop: ', time.time() - s)

        if wavelet_complex_ts is not None:
            return wavelet_complex_ts
        else:
            if powers_ts is None:
                return phases_ts
            elif phases_ts is None:
                return powers_ts
            else:
                return powers_ts.append(phases_ts, dim=self.output_dim).assign_coords(
                    output=['power', 'phase'])
