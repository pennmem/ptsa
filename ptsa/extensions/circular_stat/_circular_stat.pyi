"""Type stubs for the pybind11-compiled ``_circular_stat`` extension.

Mirrors the runtime surface exposed by
``ptsa/extensions/circular_stat/wrap.cpp``. All functions are free
functions; numpy buffers are passed in pre-allocated by the caller and
written into in place. Parameter names match the pybind11 ``py::arg``
declarations so pyright errors point at the caller-visible identifier.
"""
from __future__ import annotations

import numpy as np
import numpy.typing as npt

_Float64Array = npt.NDArray[np.float64]
_Complex128Array = npt.NDArray[np.complex128]
_BoolArray = npt.NDArray[np.bool_]


def circ_diff(
    c1: _Complex128Array, c2: _Complex128Array, cdiff: _Complex128Array
) -> None:
    """Elementwise circular difference c1 - c2, written into ``cdiff``."""
    ...


def circ_diff_par(
    c1: _Complex128Array,
    c2: _Complex128Array,
    cdiff: _Complex128Array,
    n_threads: int,
) -> None:
    """Parallel variant of :func:`circ_diff` using ``n_threads`` worker threads."""
    ...


def resultant_vector(c: _Complex128Array) -> complex:
    """Sum of the unit-phase vectors in ``c``."""
    ...


def resultant_vector_length(c: _Complex128Array) -> float:
    """Magnitude of :func:`resultant_vector`."""
    ...


def circ_mean(c: _Complex128Array) -> complex:
    """Circular mean (mean direction) of ``c``."""
    ...


def circ_diff_time_bins(
    c1: _Complex128Array,
    c2: _Complex128Array,
    cdiff: _Complex128Array,
    cdiff_means: _Complex128Array,
) -> None:
    """Per-time-bin circular differences and their bin-wise means."""
    ...


def compute_f_stat(
    phase_diff_mat: _Complex128Array,
    recalls: _BoolArray,
    f_stat_mat: _Float64Array,
) -> None:
    """F-statistic comparing recalled and non-recalled trials, in place."""
    ...


def compute_zscores(mat: _Float64Array, n_perms: int) -> None:
    """Convert ``mat`` to z-scores using ``n_perms`` permutations, in place."""
    ...


def single_trial_ppc_all_features(
    recalls: _BoolArray,
    wavelets: _Complex128Array,
    ppc_output: _Float64Array,
    theta_sum_recalls: _Complex128Array,
    theta_sum_non_recalls: _Complex128Array,
    n_freqs: int,
    n_bps: int,
    n_threads: int,
) -> None:
    """Pairwise-phase-consistency features across all bipolar pairs."""
    ...


def single_trial_outsample_ppc_features(
    wavelets: _Complex128Array,
    theta_avg_recalls: _Complex128Array,
    theta_avg_non_recalls: _Complex128Array,
    outsample_ppc_features: _Float64Array,
    n_freqs: int,
    n_bps: int,
    n_threads: int,
) -> None:
    """Out-of-sample PPC features against precomputed class-mean phases."""
    ...
