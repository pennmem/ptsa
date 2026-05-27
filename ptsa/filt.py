#emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
#ex: set sts=4 ts=4 sw=4 et:
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See the COPYING file distributed along with the PTSA package for the
#   copyright and license terms.
#
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""Tiny SciPy ``buttfilt`` helper, used by ``TimeSeries.filtered`` and
``ButterworthFilter``."""
from __future__ import annotations

from typing import Sequence, cast

import numpy as np
import numpy.typing as npt
from scipy.signal import butter, filtfilt

__all__ = ["buttfilt"]

# `butter(..., output='ba')` returns ``(b, a)`` numerator/denominator
# coefficient vectors. The other output modes (``'zpk'``/``'sos'``) widen the
# return type, so pyright sees the union and flags the 2-tuple unpacking. The
# helper only ever uses ``'ba'``, so a narrow alias keeps the call site clean
# without a ``cast``.
FreqRangeLike = float | Sequence[float] | npt.ArrayLike


def buttfilt(
    dat: npt.ArrayLike,
    freq_range: FreqRangeLike,
    sample_rate: float,
    filt_type: str,
    order: int,
    axis: int = -1,
) -> npt.NDArray[np.floating]:
    """Apply a zero-phase Butterworth filter along ``axis``.

    Parameters
    ----------
    dat
        Input samples.
    freq_range
        Cutoff frequency (or low/high pair) in Hz.
    sample_rate
        Sample rate of ``dat`` in Hz.
    filt_type
        ``"low"``, ``"high"``, ``"bandpass"`` or ``"bandstop"``.
    order
        Filter order.
    axis
        Axis along which to filter (default ``-1`` = last).
    """
    dat_arr = np.asarray(dat)
    freq = np.asarray(freq_range, dtype=float)

    nyq = sample_rate / 2.0

    # `butter` with the default ``output='ba'`` returns a 2-tuple, but its
    # overloads union with zpk/sos return shapes — narrow back via cast so
    # pyright can unpack ``(b, a)`` cleanly. (Locally scoped, single use.)
    ba = cast(
        "tuple[npt.NDArray[np.floating], npt.NDArray[np.floating]]",
        butter(order, freq / nyq, filt_type),
    )
    b, a = ba

    filtered = filtfilt(b, a, dat_arr, axis=axis)
    return cast("npt.NDArray[np.floating]", filtered)
