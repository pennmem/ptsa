"""Type stubs for the pybind11-compiled ``_morlet`` extension.

Mirrors the runtime surface exposed by ``ptsa/extensions/morlet/wrap.cpp``:
an ``OutputType`` enum (with the integer aliases ``POWER``/``PHASE``
/``BOTH``/``COMPLEX`` re-exported at module scope), plus the three
classes ``MorletWaveFFT``, ``MorletWaveletTransform`` and
``MorletWaveletTransformMP`` used by ``ptsa.data.filters.morlet``.

Signatures follow the pybind11 docstrings: numpy array arguments are
typed ``npt.NDArray`` of the corresponding scalar (``float64`` for
real-valued signals / powers / phases, ``complex128`` for wavelet
coefficients, ``bool_`` for recall labels). Scalar pybind11 ints / floats
accept ``SupportsInt`` / ``SupportsFloat`` respectively, but we narrow
to ``int`` / ``float`` here because the wider protocol types add noise
without buying expressiveness for the call sites in this repo.
"""
from __future__ import annotations

from typing import overload

import numpy as np
import numpy.typing as npt

_Float64Array = npt.NDArray[np.float64]
_Complex128Array = npt.NDArray[np.complex128]


class OutputType:
    """Output-mode enum for :class:`MorletWaveletTransform`.

    Each member exposes the standard pybind11 ``name`` (str) and
    ``value`` (int) attributes; the values are also re-exported as
    module-level constants ``POWER``, ``PHASE``, ``BOTH``, ``COMPLEX``.
    """

    POWER: "OutputType"
    PHASE: "OutputType"
    BOTH: "OutputType"
    COMPLEX: "OutputType"

    name: str
    value: int

    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...


# Module-level aliases for the enum members. These bind to the same
# ``OutputType`` instances as ``OutputType.POWER`` etc., not raw ints.
POWER: OutputType
PHASE: OutputType
BOTH: OutputType
COMPLEX: OutputType


class MorletWaveFFT:
    """Precomputed FFT of a single complex Morlet wavelet."""

    len0: int
    len: int
    nt: int

    def __init__(self) -> None: ...
    def init(
        self,
        width: int,
        freq: float,
        win_size: int,
        sample_freq: float,
        complete: bool = ...,
    ) -> int: ...


class MorletWaveletTransform:
    """Single-threaded wavelet engine wrapping the FFTW plans."""

    n_freqs: int
    signal_len_: int

    @overload
    def __init__(self) -> None: ...
    @overload
    def __init__(
        self,
        width: int,
        freqs: npt.ArrayLike,
        sample_freq: float,
        signal_len: int,
        complete: bool = ...,
    ) -> None: ...
    @overload
    def __init__(
        self,
        width: int,
        low_freq: float,
        high_freq: float,
        nf: int,
        sample_freq: float,
        signal_len: int,
        complete: bool = ...,
    ) -> None: ...

    def init(
        self,
        width: int,
        low_freq: float,
        high_freq: float,
        nf: int,
        sample_freq: float,
        signal_len: int,
        complete: bool = ...,
    ) -> None: ...

    def init_flex(
        self,
        width: int,
        freqs: npt.ArrayLike,
        sample_freq: float,
        signal_len: int,
        complete: bool = ...,
    ) -> None: ...

    def multiphasevec(
        self,
        signal: _Float64Array,
        powers: _Float64Array,
        phases: _Float64Array | None = ...,
    ) -> None: ...

    def multiphasevec_complex(
        self, signal: _Float64Array, wavelets: _Complex128Array
    ) -> None: ...

    def multiphasevec_powers(
        self, signal: _Float64Array, powers: _Float64Array
    ) -> None: ...

    def multiphasevec_powers_and_phases(
        self,
        signal: _Float64Array,
        powers: _Float64Array,
        phases: _Float64Array,
    ) -> None: ...

    def wavelet_pow_phase(
        self,
        signal: _Float64Array,
        powers: _Float64Array,
        phases: _Float64Array,
        wavelets: _Complex128Array,
    ) -> None: ...

    def wavelet_pow_phase_py(
        self,
        signal: _Float64Array,
        powers: _Float64Array,
        phases: _Float64Array,
        wavelets: _Complex128Array,
    ) -> None: ...

    def set_output_type(self, output_type: OutputType) -> None: ...


class MorletWaveletTransformMP:
    """Multi-worker pool wrapping ``MorletWaveletTransform`` instances."""

    def __init__(self, cpus: int = ...) -> None: ...

    def set_num_freq(self, num_freq: int) -> None: ...
    def set_signal_array(self, signal_array: _Float64Array) -> None: ...
    def set_wavelet_pow_array(self, wavelet_pow_array: _Float64Array) -> None: ...
    def set_wavelet_phase_array(self, wavelet_phase_array: _Float64Array) -> None: ...
    def set_wavelet_complex_array(
        self, wavelet_complex_array: _Complex128Array
    ) -> None: ...
    def set_output_type(self, output_type: OutputType) -> None: ...

    def initialize_signal_props(self, sample_freq: float) -> None: ...
    def initialize_wavelet_props(
        self,
        width: int,
        freqs: npt.ArrayLike,
        complete: bool = ...,
    ) -> None: ...

    def prepare_run(self) -> None: ...
    def compute_wavelets_threads(self) -> None: ...
    def compute_wavelets_worker_fcn(self, thread_no: int) -> int: ...
    def index(self, i: int, j: int, stride: int) -> int: ...
