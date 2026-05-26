"""Numerical-correctness tests for the Morlet wavelet kernel.

These are *hand-coded ground-truth* tests, not regression tests
against a frozen baseline. They assert mathematical properties the
wavelet output must satisfy regardless of the underlying numpy /
scipy / FFTW version: a pure sinusoid at frequency ``f0`` should
produce maximum power at the bin closest to ``f0``, the phase
output should square back to power with the right magnitudes, and
parallelized output should match the serial result exactly.

The matching regression suite in ``tests/test_regression.py``
locks in the *exact* numerical output against a known-good 3.0.6
build. The two sets of tests are complementary: regression catches
bit-level drift, correctness catches "we silently switched the
formula" bugs.
"""

import numpy as np
import pytest

from ptsa.data.timeseries import TimeSeries
from ptsa.data.filters import MorletWaveletFilter


# Per-test seeded RNG. Replace any np.random.* with these so failures
# can be reproduced bit-identically from a printed seed.
SEED = 20260526


def _sinusoid_timeseries(f0, samplerate=250.0, duration=4.0):
    """Single-channel float64 sinusoid at frequency f0, sampled at
    samplerate for ``duration`` seconds. No noise — used to assert
    the wavelet picks out f0 in isolation."""
    n = int(duration * samplerate)
    t = np.arange(n) / samplerate
    sig = np.sin(2 * np.pi * f0 * t)
    return TimeSeries.create(
        sig[None, :],
        samplerate,
        dims=("channels", "time"),
        coords={"channels": np.array([0]), "time": t},
    )


@pytest.mark.parametrize("f0", [10.0, 20.0, 40.0])
@pytest.mark.parametrize("width", [4, 5, 7])
def test_morlet_power_peaks_at_input_frequency(f0, width):
    """The time-averaged Morlet power spectrum of a pure ``f0`` Hz
    sinusoid should peak at the wavelet-grid bin closest (in log
    distance) to ``f0``, and that peak should be at least 5x the
    median power across the grid.

    Parametrized over ``f0`` in {10, 20, 40} Hz and ``width`` in
    {4, 5, 7} to make sure the picking is robust across the
    frequency range and the time/frequency-resolution tradeoff.
    """
    samplerate = 250.0
    ts = _sinusoid_timeseries(f0, samplerate=samplerate, duration=4.0)

    # Mirror-buffer to suppress edge effects from the wavelet's
    # finite-support kernel. 1 s is comfortably longer than 1/f0
    # for all f0 we test (>= 10 Hz).
    ts_buf = ts.add_mirror_buffer(1.0)

    # Log-spaced frequency grid that brackets every f0 we test.
    freqs = np.logspace(np.log10(2.0), np.log10(80.0), 12)

    out = MorletWaveletFilter(
        freqs=freqs, width=width, output="power", verbose=False, cpus=1
    ).filter(ts_buf)

    # Strip the 1 s mirror buffer.
    buf_samples = int(samplerate * 1.0)
    out_unbuf = out.isel(time=slice(buf_samples, -buf_samples))

    # Time-averaged power per frequency on the single channel.
    mean_pow = np.asarray(out_unbuf.mean(dim="time").isel(channels=0).values)

    # Bin we expect to win = closest in log distance to f0.
    expected_bin = int(np.argmin(np.abs(np.log(freqs) - np.log(f0))))
    argmax_bin = int(mean_pow.argmax())

    assert argmax_bin == expected_bin, (
        "Morlet power peak at f0={} Hz with width={} landed at "
        "freqs[{}]={:.3f} Hz, expected freqs[{}]={:.3f} Hz".format(
            f0, width, argmax_bin, freqs[argmax_bin],
            expected_bin, freqs[expected_bin],
        )
    )

    peak_to_median = mean_pow.max() / np.median(mean_pow)
    assert peak_to_median > 5.0, (
        "Morlet power peak is only {:.2f}x the median, expected > 5x; "
        "the wavelet is not clearly resolving f0={} Hz".format(
            peak_to_median, f0
        )
    )


def test_morlet_complex_magnitude_equals_power():
    """For the same input, the squared magnitude of the complex output
    should equal the power output, since power = |z|^2 by definition.

    Catches the regression where one output type is computed by a
    different formula than the other."""
    rng = np.random.default_rng(SEED)
    samplerate = 200.0
    n_channels, n_events, n_samples = 2, 3, 512
    # Mix of tone + noise so we exercise non-trivial complex values.
    t = np.arange(n_samples) / samplerate
    data = (
        rng.standard_normal((n_channels, n_events, n_samples)) * 0.5
        + np.sin(2 * np.pi * 12.0 * t)[None, None, :]
    ).astype(np.float64)

    ts = TimeSeries.create(
        data,
        samplerate,
        dims=("channels", "events", "time"),
        coords={
            "channels": np.arange(n_channels),
            "events": np.arange(n_events),
            "time": t,
        },
    )

    freqs = np.array([6.0, 12.0, 24.0], dtype=np.float64)

    pow_ts = MorletWaveletFilter(
        freqs=freqs, width=5, output="power", verbose=False, cpus=1
    ).filter(ts)

    cplx_ts = MorletWaveletFilter(
        freqs=freqs, width=5, output="complex", verbose=False, cpus=1
    ).filter(ts)

    pow_from_cplx = np.abs(np.asarray(cplx_ts.data)) ** 2

    np.testing.assert_allclose(
        pow_from_cplx, np.asarray(pow_ts.data),
        rtol=1e-10, atol=1e-15,
        err_msg="|complex|^2 disagrees with the 'power' output",
    )


def test_morlet_parallel_matches_serial():
    """Running the Morlet filter with cpus=1 vs cpus=4 should produce
    bit-identical output. Catches threadpool / data-race bugs in
    MorletWaveletTransformMP."""
    rng = np.random.default_rng(SEED + 1)
    samplerate = 250.0
    n_channels, n_events, n_samples = 4, 8, 512  # 32 work items, > 4 cpus
    data = rng.standard_normal((n_channels, n_events, n_samples)).astype(np.float64)

    ts = TimeSeries.create(
        data,
        samplerate,
        dims=("channels", "events", "time"),
        coords={
            "channels": np.arange(n_channels),
            "events": np.arange(n_events),
            "time": np.arange(n_samples) / samplerate,
        },
    )

    freqs = np.logspace(np.log10(4.0), np.log10(60.0), 6)

    serial = MorletWaveletFilter(
        freqs=freqs, width=5, output="power", verbose=False, cpus=1
    ).filter(ts)

    parallel = MorletWaveletFilter(
        freqs=freqs, width=5, output="power", verbose=False, cpus=4
    ).filter(ts)

    # Bit-identical: the C++ kernel does the same arithmetic per
    # signal regardless of which worker thread runs it.
    np.testing.assert_array_equal(
        np.asarray(parallel.data),
        np.asarray(serial.data),
        err_msg="cpus=1 vs cpus=4 produced different Morlet output",
    )


def test_morlet_phase_is_linear_in_time_at_input_freq():
    """The unwrapped phase of a Morlet wavelet response to a pure
    ``f0`` Hz sinusoid is approximately linear in time with slope
    ``2*pi*f0``. Catches phase-sign / unwrap bugs."""
    f0 = 15.0
    samplerate = 250.0
    ts = _sinusoid_timeseries(f0, samplerate=samplerate, duration=4.0)
    ts_buf = ts.add_mirror_buffer(1.0)

    # Only request the exact target freq so we don't pick a slightly
    # off-grid bin and bias the slope.
    out = MorletWaveletFilter(
        freqs=np.array([f0]),
        width=5,
        output="phase",
        verbose=False,
        cpus=1,
    ).filter(ts_buf)

    # Strip the mirror buffer and pick the single channel/freq.
    buf_samples = int(samplerate * 1.0)
    phase = np.asarray(
        out.isel(time=slice(buf_samples, -buf_samples))
        .isel(channels=0, frequency=0).values
    )
    # Unwrap so the phase climbs monotonically instead of wrapping.
    unwrapped = np.unwrap(phase)

    # Fit a line: slope should be 2*pi*f0 rad/sec.
    n = len(unwrapped)
    t = np.arange(n) / samplerate
    slope, intercept = np.polyfit(t, unwrapped, 1)

    expected_slope = 2 * np.pi * f0
    rel_err = abs(slope - expected_slope) / abs(expected_slope)
    assert rel_err < 5e-3, (
        "Phase slope for f0={} Hz was {:.4f} rad/sec, expected "
        "{:.4f} rad/sec (rel err {:.2%})".format(
            f0, slope, expected_slope, rel_err
        )
    )
