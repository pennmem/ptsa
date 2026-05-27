"""Morlet wavelet transform extension.

The compiled module is ``_morlet`` (built from ``wrap.cpp`` via pybind11);
its public symbols are re-exported here so that code using the historical
``from ptsa.extensions import morlet; morlet.MorletWaveletTransform`` (or
``from ptsa.extensions.morlet import POWER``) keeps working unchanged.

Also exposes ``get_time_domain_wavelet`` — a pure-Python reference
implementation of the wavelet PTSA convolves with, useful for inspecting
the kernel directly without going through the FFT-based filter.
"""

from __future__ import annotations

import numpy as np
import numpy.typing as npt

from ._morlet import (  # noqa: F401
    BOTH,
    COMPLEX,
    PHASE,
    POWER,
    MorletWaveFFT,
    MorletWaveletTransform,
    MorletWaveletTransformMP,
    OutputType,
)
from ._python_reference import python_morlet_wavelet as _python_morlet_wavelet


def get_time_domain_wavelet(
    freq: float,
    width: int,
    samplerate: float,
    complete: bool = True,
) -> npt.NDArray[np.complex128]:
    """Python reference implementation of the wavelet PTSA convolves with."""
    return _python_morlet_wavelet(freq, width, samplerate, complete=complete)


__all__ = [
    "MorletWaveFFT",
    "MorletWaveletTransform",
    "MorletWaveletTransformMP",
    "OutputType",
    "POWER",
    "PHASE",
    "BOTH",
    "COMPLEX",
    "get_time_domain_wavelet",
]
