"""Pure-Python time-domain Morlet wavelet generator.

This module is a line-by-line port of the wavelet-construction loop in
``MorletWaveFFT::init`` (``ptsa/extensions/morlet/morlet.cpp`` lines 30-77).
It exists as an independent reference implementation that PTSA's
FFT-based C++ kernel can be validated against, and as the backend for
``ptsa.extensions.morlet.get_time_domain_wavelet`` so users can inspect
the actual wavelet that PTSA convolves their signal with.

The port deliberately mirrors the C++ control flow (variable names,
ordering, conditionals) rather than refactoring to "pythonic" form, so
that any divergence between the two implementations is easy to spot in
a side-by-side diff.

References
----------
Tallon-Baudry, C., & Bertrand, O. (1996). Oscillatory gamma activity
in humans and its role in object representation. *Trends in Cognitive
Sciences*, 3(4), 151-162.
"""

from __future__ import annotations

import math

import numpy as np
import numpy.typing as npt

__all__ = ["python_morlet_wavelet"]


def python_morlet_wavelet(
    freq: float,
    width: int,
    samplerate: float,
    complete: bool = True,
) -> npt.NDArray[np.complex128]:
    """Generate a complex Morlet wavelet in the time domain.

    Direct port of the ``cur_wave`` construction loop in
    ``MorletWaveFFT::init`` (morlet.cpp lines 30-77), stopping just
    before the C++ code takes its FFT.

    Parameters
    ----------
    freq : float
        Centre frequency of the wavelet, in Hz.
    width : int
        Number of cycles of the carrier under the Gaussian envelope.
        This is the Tallon-Baudry parameterisation; do not confuse it
        with scipy.signal.morlet's ``w`` (a scale factor) or with MNE's
        ``n_cycles`` (which is the same thing as PTSA's ``width``).
    samplerate : float
        Sampling rate, in Hz.
    complete : bool, default True
        If True, use the Tallon-Baudry "complete" Morlet: subtract a
        ``exp(-w^2/2)`` zero-mean offset on the real (cosine) arm,
        rescale the ``a_c`` / ``a_s`` amplitudes analytically, and
        rescale the time axis by ``(2/pi) * arccos(exp(-w^2/2))`` so
        the peak frequency stays at ``freq`` despite the offset.
        If False, use the standard (textbook) complex Morlet.

    Returns
    -------
    np.ndarray, complex128, shape ``(nt,)``
        The complex wavelet, sampled on the same support and with the
        same length as PTSA's internal ``cur_wave`` buffer (before
        zero-padding to a power of two).
    """
    width = int(width)
    freq = float(freq)
    samplerate = float(samplerate)

    dt = 1.0 / samplerate
    sf = freq / width                  # sigma_f; Gaussian width in freq domain
    st = 1.0 / (2.0 * math.pi * sf)    # sigma_t; Gaussian width in time domain
    a_c = 1.0 / math.sqrt(st * math.sqrt(math.pi))
    a_s = a_c
    omega = 2.0 * math.pi * freq

    sample_factor = 10.0
    nt = int(sample_factor * st / dt) + 1

    t = -(sample_factor / 2.0) * st
    scale = 2.0 * st * st
    complete_offset = 0.0
    freq_scale = 1.0

    if complete:
        complete_offset = math.exp(-(width * width) / 2.0)
        freq_scale = (2.0 / math.pi) * math.acos(math.exp(-0.5 * width * width))
        nt = int((nt - 1) / freq_scale + 1.5)
        t = t / freq_scale
        scale /= freq_scale * freq_scale
        inv_sq_a_c = (1.0 / freq_scale) * (
            width / (4.0 * freq * math.sqrt(math.pi))
            + 3.0 * width * math.exp(-(width * width)) / (4.0 * freq * math.sqrt(math.pi))
            - width * math.exp(-3 * (width * width) / 4.0) / (freq * math.sqrt(math.pi))
        )
        acos_term = math.acos(math.exp(-(width * width) / 2.0))
        inv_sq_a_s = (
            width * math.sqrt(math.pi) / (8.0 * freq * acos_term)
        ) * (
            1.0 - math.exp(-(width * width) * math.pi * math.pi / (4.0 * acos_term * acos_term))
        )
        a_c = 1.0 / math.sqrt(inv_sq_a_c)
        a_s = 1.0 / math.sqrt(inv_sq_a_s)

    cur_wave = np.empty(nt, dtype=np.complex128)
    for i in range(nt):
        coef_common = math.exp(-t * t / scale)
        coef_c = a_c * coef_common
        coef_s = a_s * coef_common
        omega_t = omega * t
        re = coef_c * (math.cos(freq_scale * omega_t) - complete_offset)
        im = coef_s * math.sin(omega_t)
        cur_wave[i] = complex(re, im)
        t += dt

    return cur_wave
