"""Regression tests against the ptsa 3.0.6 baseline.

Each fixture in `tests/data/regression_fixtures/*.npz` was generated
by running a load-bearing PTSA operation (Morlet, Butterworth,
Resample, MonopolarToBipolar) against a deterministic seeded input
in the reference env. This module loads each fixture and asserts the
current PTSA install produces the same output bit-for-bit (within a
very tight numerical tolerance).

The tolerance is intentionally tight (``rtol=1e-12``). FFTW and
scipy's filtfilt are deterministic across rebuilds of the same
library version, so any kernel-level behavior change — a SWIG
typemap regression, a different FFTW planner pick, an internal
scipy edit, a silent numpy-2 ABI shift — should fail loudly here.

If you intentionally changed kernel behavior, regenerate fixtures
via the script in the fixture dir; see its README.
"""

import json
import os.path as osp

import numpy as np
import pytest

from ptsa.data.timeseries import TimeSeries
from ptsa.data.filters import (
    ButterworthFilter,
    MonopolarToBipolarMapper,
    MorletWaveletFilter,
    ResampleFilter,
)


FIXTURE_DIR = osp.join(osp.dirname(__file__), "data", "regression_fixtures")

# Tight tolerances. FFTW + scipy.signal.filtfilt are deterministic
# across rebuilds of the same upstream version, so we usually see
# bit-identical output. Loosen only if a deliberate scipy / numpy
# rebuild changes one of the round-to-even paths.
RTOL = 1e-12
ATOL = 1e-15


def _load(name):
    path = osp.join(FIXTURE_DIR, name + ".npz")
    if not osp.exists(path):
        pytest.skip("regression fixture missing: " + name + ".npz "
                    "(run tests/data/regression_fixtures/generate.py "
                    "in the 3.0.6 reference env to (re)generate)")
    blob = np.load(path, allow_pickle=False)
    meta = json.loads(str(blob["metadata_json"]))
    return blob, meta


def _assert_close(actual, expected, meta, name):
    """Wrap np.testing.assert_allclose so the failure message includes
    the fixture's metadata blob — i.e. which baseline PTSA / numpy /
    scipy version was used to generate the expected output. Saves
    a ton of guesswork when a test fails on a CI matrix cell."""
    actual = np.asarray(actual)
    expected = np.asarray(expected)
    try:
        np.testing.assert_allclose(actual, expected, rtol=RTOL, atol=ATOL)
    except AssertionError as e:
        raise AssertionError(
            "Regression {} failed against baseline:\n  {}\n"
            "If you intentionally changed kernel behavior, regenerate "
            "the fixtures (see tests/data/regression_fixtures/README.md). "
            "Original failure:\n{}".format(
                name,
                "  ".join(["{}={}".format(k, v) for k, v in sorted(meta.items())]),
                e,
            )
        )


def test_morlet_power_regression():
    blob, meta = _load("morlet_power_3ch_4ev_256t")
    n_ch, n_ev, n_t = blob["input_data"].shape
    sr = float(blob["samplerate"])

    ts = TimeSeries.create(
        blob["input_data"],
        sr,
        dims=("channels", "events", "time"),
        coords={
            "channels": np.arange(n_ch),
            "events": np.arange(n_ev),
            "time": np.arange(n_t) / sr,
        },
    )

    out = MorletWaveletFilter(
        freqs=blob["freqs"],
        width=int(blob["width"]),
        output="power",
        verbose=False,
        cpus=1,
        complete=bool(blob["complete"]),
    ).filter(ts)

    assert tuple(out.dims) == tuple(blob["expected_dims"])
    _assert_close(out.data, blob["expected_output"], meta, "morlet_power")


def test_morlet_phase_regression():
    blob, meta = _load("morlet_phase_2ch_3ev_256t")
    n_ch, n_ev, n_t = blob["input_data"].shape
    sr = float(blob["samplerate"])

    ts = TimeSeries.create(
        blob["input_data"],
        sr,
        dims=("channels", "events", "time"),
        coords={
            "channels": np.arange(n_ch),
            "events": np.arange(n_ev),
            "time": np.arange(n_t) / sr,
        },
    )

    out = MorletWaveletFilter(
        freqs=blob["freqs"],
        width=int(blob["width"]),
        output="phase",
        verbose=False,
        cpus=1,
        complete=bool(blob["complete"]),
    ).filter(ts)

    assert tuple(out.dims) == tuple(blob["expected_dims"])
    _assert_close(out.data, blob["expected_output"], meta, "morlet_phase")


def test_morlet_complex_regression():
    blob, meta = _load("morlet_complex_2ch_2ev_128t")
    n_ch, n_ev, n_t = blob["input_data"].shape
    sr = float(blob["samplerate"])

    ts = TimeSeries.create(
        blob["input_data"],
        sr,
        dims=("channels", "events", "time"),
        coords={
            "channels": np.arange(n_ch),
            "events": np.arange(n_ev),
            "time": np.arange(n_t) / sr,
        },
    )

    out = MorletWaveletFilter(
        freqs=blob["freqs"],
        width=int(blob["width"]),
        output="complex",
        verbose=False,
        cpus=1,
        complete=bool(blob["complete"]),
    ).filter(ts)

    assert tuple(out.dims) == tuple(blob["expected_dims"])
    _assert_close(out.data, blob["expected_output"], meta, "morlet_complex")


def test_butterworth_regression():
    blob, meta = _load("butterworth_stop_4ch_1024t")
    n_ch, n_t = blob["input_data"].shape
    sr = float(blob["samplerate"])

    ts = TimeSeries.create(
        blob["input_data"],
        sr,
        dims=("channels", "time"),
        coords={"channels": np.arange(n_ch), "time": np.arange(n_t) / sr},
    )

    out = ButterworthFilter(
        freq_range=list(blob["freq_range"]),
        filt_type=str(blob["filt_type"]),
        order=int(blob["order"]),
    ).filter(ts)

    assert tuple(out.dims) == tuple(blob["expected_dims"])
    _assert_close(out.data, blob["expected_output"], meta, "butterworth")


def test_resample_regression():
    blob, meta = _load("resample_4ch_1024t_500to125")
    n_ch, n_t = blob["input_data"].shape
    sr = float(blob["samplerate"])

    ts = TimeSeries.create(
        blob["input_data"],
        sr,
        dims=("channels", "time"),
        coords={"channels": np.arange(n_ch), "time": np.arange(n_t) / sr},
    )

    out = ResampleFilter(resamplerate=float(blob["new_samplerate"])).filter(ts)

    assert tuple(out.dims) == tuple(blob["expected_dims"])
    _assert_close(out.data, blob["expected_output"], meta, "resample_data")
    _assert_close(
        out.coords["time"].data, blob["expected_time"], meta, "resample_time_axis"
    )


def test_monopolar_to_bipolar_regression():
    blob, meta = _load("m2b_6ch_5pairs_4ev_256t")
    n_ch, n_ev, n_t = blob["input_data"].shape
    sr = float(blob["samplerate"])

    ts = TimeSeries.create(
        blob["input_data"],
        sr,
        dims=("channels", "events", "time"),
        coords={
            "channels": np.arange(n_ch),
            "events": np.arange(n_ev),
            "time": np.arange(n_t) / sr,
        },
    )

    out = MonopolarToBipolarMapper(bipolar_pairs=blob["bipolar_pairs"]).filter(ts)

    assert tuple(out.dims) == tuple(blob["expected_dims"])
    _assert_close(out.data, blob["expected_output"], meta, "m2b")
