"""Numerical-correctness tests for ButterworthFilter and ResampleFilter.

Hand-coded ground-truth tests complementing the regression suite in
``tests/test_regression.py``. Asserts mathematical properties that
hold for any correct implementation: stopband attenuation, passband
flatness, zero-phase (filtfilt), frequency preservation across
downsample, and anti-aliasing.
"""

import numpy as np

from ptsa.data.timeseries import TimeSeries
from ptsa.data.filters import ButterworthFilter, ResampleFilter


SEED = 20260526


def _multitone(freqs, samplerate=500.0, duration=4.0, amplitudes=None):
    """Single-channel sum of pure sinusoids at the given frequencies.
    Returns a (1, n_samples) TimeSeries."""
    if amplitudes is None:
        amplitudes = [1.0] * len(freqs)
    n = int(duration * samplerate)
    t = np.arange(n) / samplerate
    sig = sum(a * np.sin(2 * np.pi * f * t) for f, a in zip(freqs, amplitudes))
    return TimeSeries.create(
        sig[None, :],
        samplerate,
        dims=("channels", "time"),
        coords={"channels": np.array([0]), "time": t},
    )


def _freq_amplitude(signal, samplerate, target_freq):
    """Amplitude of the FFT bin closest to ``target_freq``."""
    fft = np.fft.rfft(signal)
    freqs = np.fft.rfftfreq(len(signal), 1.0 / samplerate)
    bin_idx = int(np.argmin(np.abs(freqs - target_freq)))
    # rfft normalization for a pure sine: amplitude = 2 * |X[k]| / N
    return 2.0 * np.abs(fft[bin_idx]) / len(signal)


def test_butterworth_stopband_attenuates_target_frequency():
    """Notching 55-65 Hz on a 5+30+60 Hz multitone should kill 60 Hz
    by > 40 dB while passing 5 and 30 Hz within 0.5 dB."""
    sr = 500.0
    ts = _multitone([5.0, 30.0, 60.0], samplerate=sr, duration=4.0)

    notched = ButterworthFilter(
        freq_range=[55.0, 65.0], filt_type="stop", order=4
    ).filter(ts)

    # Strip edge effects so the FFT amplitudes are clean.
    edge = int(sr * 0.5)
    sig_in = np.asarray(ts.isel(channels=0).values)[edge:-edge]
    sig_out = np.asarray(notched.isel(channels=0).values)[edge:-edge]

    for f in [5.0, 30.0]:
        a_in = _freq_amplitude(sig_in, sr, f)
        a_out = _freq_amplitude(sig_out, sr, f)
        db = 20 * np.log10(a_out / max(a_in, 1e-12))
        assert abs(db) < 0.5, (
            "{} Hz passband attenuation was {:+.2f} dB, expected within 0.5 dB"
            .format(f, db)
        )

    a_in = _freq_amplitude(sig_in, sr, 60.0)
    a_out = _freq_amplitude(sig_out, sr, 60.0)
    db = 20 * np.log10(a_out / max(a_in, 1e-12))
    assert db < -40.0, (
        "60 Hz stopband attenuation was only {:+.2f} dB, expected < -40 dB"
        .format(db)
    )


def test_butterworth_bandpass_isolates_inband_signal():
    """A [8, 12] bandpass on a 5+10+30 Hz multitone should pass 10 Hz
    cleanly while attenuating 5 and 30 Hz by at least 15 dB."""
    sr = 500.0
    ts = _multitone([5.0, 10.0, 30.0], samplerate=sr, duration=4.0)

    bp = ButterworthFilter(
        freq_range=[8.0, 12.0], filt_type="pass", order=4
    ).filter(ts)

    edge = int(sr * 0.5)
    sig_in = np.asarray(ts.isel(channels=0).values)[edge:-edge]
    sig_out = np.asarray(bp.isel(channels=0).values)[edge:-edge]

    a_in = _freq_amplitude(sig_in, sr, 10.0)
    a_out = _freq_amplitude(sig_out, sr, 10.0)
    db_10 = 20 * np.log10(a_out / max(a_in, 1e-12))
    assert abs(db_10) < 1.0, (
        "10 Hz passband should be ~0 dB, got {:+.2f} dB".format(db_10)
    )

    for f in [5.0, 30.0]:
        a_in = _freq_amplitude(sig_in, sr, f)
        a_out = _freq_amplitude(sig_out, sr, f)
        db = 20 * np.log10(a_out / max(a_in, 1e-12))
        assert db < -15.0, (
            "{} Hz out-of-band attenuation was only {:+.2f} dB, expected < -15"
            .format(f, db)
        )


def test_butterworth_is_zero_phase():
    """Butterworth uses scipy.filtfilt under the hood, which applies the
    filter forward then backward. The output should be in-phase with the
    input (cross-correlation peak at lag 0)."""
    sr = 500.0
    ts = _multitone([5.0, 30.0, 60.0], samplerate=sr, duration=4.0)

    notched = ButterworthFilter(
        freq_range=[55.0, 65.0], filt_type="stop", order=4
    ).filter(ts)

    edge = int(sr * 0.5)
    sig_in = np.asarray(ts.isel(channels=0).values)[edge:-edge]
    sig_out = np.asarray(notched.isel(channels=0).values)[edge:-edge]

    sig_in = sig_in - sig_in.mean()
    sig_out = sig_out - sig_out.mean()
    xcorr = np.correlate(sig_in, sig_out, mode="full")
    lag = int(xcorr.argmax()) - (len(sig_in) - 1)

    assert lag == 0, (
        "Cross-correlation peak landed at lag {} samples; "
        "Butterworth (filtfilt) should be zero-phase".format(lag)
    )


def test_butterworth_treats_channels_independently():
    """Filtering N independent channels stacked vs one-at-a-time should
    produce the same per-channel output. Catches axis-handling bugs in
    the multi-dim path."""
    sr = 500.0
    rng = np.random.default_rng(SEED + 10)
    n = int(sr * 2.0)
    t = np.arange(n) / sr

    # 4 independent channels: each is the sum of a different tone +
    # 60 Hz line noise.
    ch_freqs = [4.0, 9.0, 14.0, 22.0]
    data = np.stack([
        np.sin(2 * np.pi * f * t) + np.sin(2 * np.pi * 60 * t)
        + 0.05 * rng.standard_normal(n)
        for f in ch_freqs
    ])

    ts = TimeSeries.create(
        data, sr, dims=("channels", "time"),
        coords={"channels": np.arange(4), "time": t},
    )

    bf = ButterworthFilter(freq_range=[55.0, 65.0], filt_type="stop", order=4)
    multi_out = np.asarray(bf.filter(ts).values)

    for i, f in enumerate(ch_freqs):
        single_ts = TimeSeries.create(
            data[i : i + 1], sr, dims=("channels", "time"),
            coords={"channels": np.array([i]), "time": t},
        )
        single_out = np.asarray(bf.filter(single_ts).values)[0]
        np.testing.assert_allclose(
            multi_out[i], single_out,
            rtol=1e-12, atol=1e-15,
            err_msg="Channel {} (tone={} Hz) differs between stacked "
                    "and standalone filtering".format(i, f),
        )


def test_resample_preserves_low_frequency_content():
    """A 5 Hz pure sine sampled at 1000 Hz, downsampled to 100 Hz
    (Nyquist=50, comfortable margin), should still have its dominant
    FFT bin at 5 Hz."""
    sr_in = 1000.0
    sr_out = 100.0
    n = int(sr_in * 4.0)
    t = np.arange(n) / sr_in
    sig = np.sin(2 * np.pi * 5.0 * t)
    ts = TimeSeries.create(
        sig[None, :], sr_in, dims=("channels", "time"),
        coords={"channels": np.array([0]), "time": t},
    )

    out = ResampleFilter(resamplerate=sr_out).filter(ts)

    assert float(out["samplerate"]) == sr_out
    assert out.shape[-1] == int(sr_out * 4.0)

    sig_out = np.asarray(out.isel(channels=0).values)
    freqs_out = np.fft.rfftfreq(len(sig_out), 1.0 / sr_out)
    peak_freq = freqs_out[np.abs(np.fft.rfft(sig_out)).argmax()]
    assert abs(peak_freq - 5.0) < 0.5, (
        "Resample lost the 5 Hz tone; peak landed at {:.3f} Hz".format(peak_freq)
    )

    # Amplitude should still be ~1.0
    amp_out = _freq_amplitude(sig_out, sr_out, 5.0)
    assert abs(amp_out - 1.0) < 0.05, (
        "5 Hz amplitude after resample was {:.3f}, expected ~1.0".format(amp_out)
    )


def test_resample_suppresses_aliasing_of_above_nyquist_content():
    """A 200 Hz pure sine at 1000 Hz sampled down to 100 Hz (Nyquist=50)
    must not produce a spurious low-frequency peak. scipy's FFT-based
    resample uses an ideal brick-wall low-pass, so the 200 Hz content
    is filtered out rather than aliased to (200 - 100) = 100 → 100 - 50 = 50 Hz."""
    sr_in = 1000.0
    sr_out = 100.0
    n = int(sr_in * 4.0)
    t = np.arange(n) / sr_in
    sig = np.sin(2 * np.pi * 200.0 * t)
    ts = TimeSeries.create(
        sig[None, :], sr_in, dims=("channels", "time"),
        coords={"channels": np.array([0]), "time": t},
    )

    out = ResampleFilter(resamplerate=sr_out).filter(ts)
    sig_out = np.asarray(out.isel(channels=0).values)

    # Spectrum should be flat-ish noise floor — no peak.
    max_amp = 2.0 * np.max(np.abs(np.fft.rfft(sig_out))) / len(sig_out)
    assert max_amp < 1e-3, (
        "Resample-aliased 200 Hz content into a {:.4f} amplitude peak; "
        "expected anti-aliasing to suppress it below 1e-3".format(max_amp)
    )
