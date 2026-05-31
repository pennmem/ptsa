from __future__ import annotations

import time
from typing import Iterable, Optional, Union

import numpy as np
import numpy.typing as npt
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
    freqs : np.ndarray
        The frequencies to use in the decomposition.
    width : int, optional
        The width of the wavelet (default: 5).
    output : Union[Iterable[str], str], optional
        A string or a list of strings containing ``'power'``, ``'phase'``,
        and/or ``'complex'`` (default: ``('power', 'phase')``).
    verbose : bool, optional
        Print out the wavelet parameters (default: True).
    cpus : int, optional
        Number of threads to use when computing the transform (default: 1).
    output_dim : str, optional
        Name of the output dimension when returning both power and phase
        (default: ``'output'``).
    complete : bool, optional
        Use complete Morlet wavelets with a zero mean, which is required for
        power and phase accuracy with small wavelet widths.  The frequency is
        kept consistent with standard Morlet wavelets (default: True).

    Notes
    -----
    Let :math:`f` be the centre frequency, :math:`w` the ``width``
    (number of cycles of the carrier under the Gaussian envelope),
    :math:`\\sigma_f = f / w` the frequency-domain width of the
    Gaussian, and :math:`\\sigma_t = 1 / (2 \\pi \\sigma_f)` the
    corresponding time-domain width.

    With ``complete=False`` the wavelet is the standard complex Morlet,

    .. math::

       \\psi(t) = \\frac{1}{\\sqrt{\\sigma_t \\sqrt{\\pi}}}\\,
                 e^{-t^{2} / (2 \\sigma_t^{2})}\\,
                 e^{i\\, 2 \\pi f t}.

    With ``complete=True`` (the default since PTSA 2.0.6) PTSA uses
    the "complete" (zero-mean) form: a zero-mean correction
    :math:`e^{-w^{2}/2}` is subtracted from the cosine arm, the
    amplitudes :math:`a_c` (real part) and :math:`a_s` (imaginary
    part) are rescaled analytically so the wavelet keeps unit energy,
    and the time axis is rescaled by

    .. math::

       \\textrm{freq\\_scale} =
         \\frac{2}{\\pi}\\, \\arccos\\!\\left(e^{-w^{2}/2}\\right)

    so the peak frequency stays at :math:`f` despite the offset:

    .. math::

       \\psi_{\\text{complete}}(t) =
         a_c\\, e^{-t^{2}/(2\\sigma_t^{2})}
                  \\left(\\cos(\\text{freq\\_scale} \\cdot 2 \\pi f t)
                        - e^{-w^{2}/2}\\right)
         + i\\, a_s\\, e^{-t^{2}/(2\\sigma_t^{2})} \\sin(2 \\pi f t).

    Larger ``width`` tightens the wavelet's frequency resolution
    (narrower :math:`\\sigma_f`) at the cost of widening its time
    resolution (broader :math:`\\sigma_t`); this is the standard
    Heisenberg/Gabor time-frequency tradeoff.

    See :func:`ptsa.extensions.morlet.get_time_domain_wavelet` for a
    Python reference implementation of the formula, and
    ``tests/test_morlet_formula.py`` for independent validation of
    PTSA's FFT-based kernel against direct time-domain convolution
    with that reference.

    """
    freqs = traits.api.CArray
    width = traits.api.Int
    verbose = traits.api.Bool
    cpus = traits.api.Int
    output = []
    output_dim = traits.api.Str

    def __init__(
        self,
        freqs: npt.ArrayLike,
        width: int = 5,
        output: Union[str, Iterable[str]] = ('power', 'phase'),
        verbose: bool = True,
        cpus: int = 1,
        output_dim: str = 'output',
        complete: bool = True,
    ) -> None:
        self.freqs = freqs
        self.width = width
        self.complete = complete

        output_opts = ('power', 'phase', 'complex')

        if isinstance(output, str):
            output = [output]
        else:
            output = list(output)

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

    def filter(self, timeseries: "TimeSeries") -> Optional["TimeSeries"]:
        """Apply the constructed filter.

        Returns either a :class:`TimeSeries` carrying the requested output
        (power, phase, complex coefficients, or stacked power+phase) or
        ``None`` if no output was requested. In practice ``filter`` always
        returns a :class:`TimeSeries` for any valid configuration constructed
        via :meth:`__init__`; the ``Optional`` reflects the defensive
        ``return phases_ts`` path below where the local ``phases_ts`` may
        not have been assigned in pathological subclasses.
        """
        nontime_dims = self.get_nontime_dims(timeseries)
        nontime_sizes = self.get_nontime_sizes(timeseries)

        # ``self.freqs`` is a traits CArray descriptor on the class; on a
        # bound instance access returns the underlying ``np.ndarray``.
        freqs_arr: np.ndarray = np.asarray(self.freqs)
        wavelet_dims = nontime_sizes + (freqs_arr.shape[0],)

        powers_reshaped = np.array([[]], dtype=float)
        phases_reshaped = np.array([[]], dtype=float)
        wavelets_complex_reshaped = np.array([[]], dtype=complex)

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
                dtype=complex)

        cpus = int(self.trait_get('cpus')['cpus'])
        mt = morlet.MorletWaveletTransformMP(cpus)

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
        # `self.width` is a traits.Int descriptor; pyright sees `type[Int]`
        # even though instance access returns int.
        mt.initialize_wavelet_props(self.width, freqs_arr, self.complete)  # pyright: ignore[reportArgumentType]
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
        coords['frequency'] = freqs_arr

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
                # `self.output_dim` is a traits.Str descriptor.
                return powers_ts.append(phases_ts, dim=self.output_dim).assign_coords(  # pyright: ignore[reportArgumentType]
                    output=['power', 'phase'])
