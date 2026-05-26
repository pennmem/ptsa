"""Independent validation of PTSA's Morlet wavelet against a pure-Python
time-domain reimplementation of the formula in
``ptsa/extensions/morlet/morlet.cpp`` (``MorletWaveFFT::init``).

The strategy is:

1. Construct the wavelet directly in the time domain via the Python
   port (``python_morlet_wavelet``).
2. Convolve a synthetic signal with that wavelet using
   ``np.convolve(mode='same')``.
3. Run the same signal through PTSA's FFT-based pipeline
   (``MorletWaveletFilter``).
4. Compare the two power outputs on the interior of the signal (the
   regions where neither end is contaminated by boundary handling).

If they agree on the interior, the C++ kernel implements the formula
in ``_python_reference.python_morlet_wavelet`` -- and that formula is
the one documented in :class:`MorletWaveletFilter`'s docstring and in
the comment block above ``MorletWaveFFT::init`` in the C++ source.
"""

from __future__ import annotations

import numpy as np
import pytest

from ptsa.data.filters import MorletWaveletFilter
from ptsa.data.timeseries import TimeSeries
from ptsa.extensions.morlet import get_time_domain_wavelet
from ptsa.extensions.morlet._python_reference import python_morlet_wavelet


SAMPLERATE = 250.0
DURATION = 4.0  # seconds


def _make_signal(freq, samplerate=SAMPLERATE, duration=DURATION, seed=0):
    """Sinusoid at ``freq`` plus a little Gaussian noise, seeded."""
    rng = np.random.default_rng(seed)
    n = int(round(duration * samplerate))
    t = np.arange(n) / samplerate
    signal = np.sin(2 * np.pi * freq * t) + 0.1 * rng.standard_normal(n)
    return signal.astype(np.float64), t


def _ptsa_power(signal, freq, width, complete):
    """Run PTSA's MorletWaveletFilter on a 1-D signal at a single freq."""
    ts = TimeSeries(
        signal[np.newaxis, :],
        dims=("channels", "time"),
        coords={
            "channels": np.array(["ch0"]),
            "time": np.arange(len(signal)) / SAMPLERATE,
            "samplerate": SAMPLERATE,
        },
    )
    filt = MorletWaveletFilter(
        freqs=np.array([float(freq)]),
        width=int(width),
        output="power",
        complete=bool(complete),
        verbose=False,
        cpus=1,
    )
    out = filt.filter(ts)
    # out dims: ('frequency', 'channels', 'time'). 1 freq, 1 channel.
    return np.asarray(out.values[0, 0, :], dtype=np.float64)


def _python_power(signal, freq, width, complete):
    """Convolve signal with the python wavelet and return |conv|^2."""
    wavelet = python_morlet_wavelet(freq, width, SAMPLERATE, complete=complete)
    conv = np.convolve(signal, wavelet, mode="same")
    return np.abs(conv) ** 2


@pytest.mark.parametrize("freq", [5.0, 10.0, 20.0, 40.0])
@pytest.mark.parametrize("width", [4, 5, 7])
@pytest.mark.parametrize("complete", [False, True])
def test_python_wavelet_matches_ptsa(freq, width, complete):
    """Python time-domain convolution power == PTSA FFT power on the
    interior of the signal."""
    signal, _ = _make_signal(freq, seed=42)

    py_power = _python_power(signal, freq, width, complete)
    ptsa_p = _ptsa_power(signal, freq, width, complete)

    # Strip wavelet-support boundary samples on each side. The wavelet
    # has effective support of roughly (sample_factor=10) * sigma_t, but
    # the array returned by python_morlet_wavelet is exactly nt samples
    # long, so we trim by half its length on each side.
    wavelet = python_morlet_wavelet(freq, width, SAMPLERATE, complete=complete)
    pad = len(wavelet) // 2

    py_interior = py_power[pad:-pad]
    ptsa_interior = ptsa_p[pad:-pad]

    assert py_interior.shape == ptsa_interior.shape
    assert np.all(np.isfinite(py_interior))
    assert np.all(np.isfinite(ptsa_interior))

    # Direct match: the FFT-based path and the time-domain convolution
    # path implement the same operation, so absolute agreement is
    # expected. atol scales with the peak power so the comparison is
    # meaningful at every frequency.
    np.testing.assert_allclose(
        py_interior, ptsa_interior,
        rtol=1e-3,
        atol=1e-6 * np.max(ptsa_interior),
        err_msg=f"freq={freq} width={width} complete={complete}",
    )


def test_wavelet_autocorrelation_peak():
    """If the input signal IS the wavelet (real part), the PTSA power
    output should peak at the center sample where the wavelet sits."""
    freq, width = 10.0, 5
    wavelet = python_morlet_wavelet(freq, width, SAMPLERATE, complete=True)

    # Embed the wavelet's real part in a zero-padded buffer of length
    # equal to a normal signal. Place it at the center.
    n = int(round(DURATION * SAMPLERATE))
    signal = np.zeros(n, dtype=np.float64)
    nw = len(wavelet)
    start = (n - nw) // 2
    signal[start:start + nw] = wavelet.real

    ptsa_p = _ptsa_power(signal, freq, width, complete=True)
    peak_idx = int(np.argmax(ptsa_p))

    # The peak of the power should be at the center of where we placed
    # the wavelet (i.e. signal length // 2), within a couple of samples
    # for fence-post reasons.
    expected = n // 2
    assert abs(peak_idx - expected) <= 2, (
        f"Power peak at sample {peak_idx}, expected near {expected}"
    )


def test_get_time_domain_wavelet_matches_internal_reference():
    """The public helper must return exactly the same array as the
    internal Python reference -- if they ever diverge it's a bug."""
    for (freq, width, complete) in [
        (5.0, 4, False),
        (10.0, 5, True),
        (40.0, 7, True),
        (20.0, 4, False),
    ]:
        a = get_time_domain_wavelet(freq, width, SAMPLERATE, complete=complete)
        b = python_morlet_wavelet(freq, width, SAMPLERATE, complete=complete)
        np.testing.assert_array_equal(a, b)
