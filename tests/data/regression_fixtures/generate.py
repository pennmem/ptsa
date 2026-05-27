"""Regenerate regression fixtures by running PTSA's load-bearing
operations against deterministic seeded inputs.

Run this with the *current release-candidate* ptsa we want to lock
in as the regression baseline. As of 3.0.6 this is the local conda
build in `build/conda/linux-64/ptsa-3.0.6-py311_0.conda`. Use the
pixi env that installs it::

    cd test_pixi/oneshot-rhino2b
    pixi run python \\
        /home1/rdehaan/dependencies/ptsa/tests/data/regression_fixtures/generate.py

(Why not the *published* `ptsa==3.0.4` on pennmem? Because that
binary's `output='complex'` morlet path was bit-rotted by NumPy 1.24+
removing `np.complex`. 3.0.5 fixed that and 3.0.6 fixes the wider
numpy 2 / traits 7 / pandas 3 surface. 3.0.6 is the first release
where every documented codepath actually runs.)

The script is self-contained — it imports only `numpy` and `ptsa`
and writes one `.npz` per scenario alongside itself. Each `.npz`
stores the input, parameters, the expected output, and a metadata
blob (versions, seed, timestamp) so failures point at *which*
fixture was generated against *which* binary.

If you intend to deliberately change kernel behavior, re-run this
script with the new ptsa installed and commit the resulting
fixtures alongside the source change.
"""

from __future__ import print_function

import datetime
import os.path as osp
import sys

import numpy as np
import scipy
import xarray

import ptsa
from ptsa.data.timeseries import TimeSeries
from ptsa.data.filters import (
    ButterworthFilter,
    MonopolarToBipolarMapper,
    MorletWaveletFilter,
    ResampleFilter,
)


FIXTURE_DIR = osp.dirname(osp.abspath(__file__))
SEED = 20260526  # arbitrary; pinned for reproducibility


def _metadata():
    """Per-fixture provenance blob, stored alongside the arrays."""
    return {
        "ptsa_version": ptsa.__version__,
        "numpy_version": np.__version__,
        "scipy_version": scipy.__version__,
        "xarray_version": xarray.__version__,
        "python_version": sys.version.split()[0],
        "seed": SEED,
        "generated_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }


def _save(name, **arrays_and_scalars):
    """Save a fixture as a compressed .npz. Metadata is JSON-encoded
    so np.load round-trips it as a 0-d unicode array."""
    import json

    arrays_and_scalars["metadata_json"] = json.dumps(_metadata())
    path = osp.join(FIXTURE_DIR, name + ".npz")
    np.savez_compressed(path, **arrays_and_scalars)
    print(
        "wrote",
        osp.relpath(path, FIXTURE_DIR),
        "({:.1f} KB)".format(osp.getsize(path) / 1024.0),
    )


def _eeg_like(rng, n_channels, n_events, n_samples, samplerate, tone_hz=None):
    """Synthetic EEG-shaped float64 data: low-frequency Gaussian
    noise + (optional) sinusoidal tone shared across events."""
    t = np.arange(n_samples) / samplerate
    noise = rng.standard_normal((n_channels, n_events, n_samples)) * 0.5
    if tone_hz is not None:
        tone = np.sin(2.0 * np.pi * tone_hz * t)
        noise += tone[None, None, :]
    return noise.astype(np.float64)


def make_morlet_power_fixture():
    """Morlet power output for small 3-D EEG-shaped input."""
    rng = np.random.default_rng(SEED)
    samplerate = 250.0
    n_channels, n_events, n_samples = 3, 4, 256
    data = _eeg_like(rng, n_channels, n_events, n_samples, samplerate, tone_hz=10.0)

    times = np.arange(n_samples) / samplerate
    ts = TimeSeries.create(
        data,
        samplerate,
        dims=("channels", "events", "time"),
        coords={
            "channels": np.arange(n_channels),
            "events": np.arange(n_events),
            "time": times,
        },
    )

    freqs = np.array([5.0, 10.0, 20.0, 40.0], dtype=np.float64)
    out = MorletWaveletFilter(
        freqs=freqs, width=5, output="power", verbose=False, cpus=1
    ).filter(ts)

    _save(
        "morlet_power_3ch_4ev_256t",
        input_data=data,
        samplerate=samplerate,
        freqs=freqs,
        width=np.int64(5),
        complete=np.bool_(True),
        expected_output=np.asarray(out.data),
        expected_dims=np.array(out.dims, dtype="U16"),
    )


def make_morlet_phase_fixture():
    """Morlet phase output (separate fixture — phase is wrapped to
    [-pi, pi] and exercises a different output path)."""
    rng = np.random.default_rng(SEED + 1)
    samplerate = 200.0
    n_channels, n_events, n_samples = 2, 3, 256
    data = _eeg_like(rng, n_channels, n_events, n_samples, samplerate, tone_hz=15.0)

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

    freqs = np.array([8.0, 15.0, 30.0], dtype=np.float64)
    out = MorletWaveletFilter(
        freqs=freqs, width=5, output="phase", verbose=False, cpus=1
    ).filter(ts)

    _save(
        "morlet_phase_2ch_3ev_256t",
        input_data=data,
        samplerate=samplerate,
        freqs=freqs,
        width=np.int64(5),
        complete=np.bool_(True),
        expected_output=np.asarray(out.data),
        expected_dims=np.array(out.dims, dtype="U16"),
    )


def make_morlet_complex_fixture():
    """Morlet complex coefficient output — power.real ** 2 + power.imag ** 2
    should reproduce the power fixture's behavior."""
    rng = np.random.default_rng(SEED + 2)
    samplerate = 200.0
    n_channels, n_events, n_samples = 2, 2, 128
    data = _eeg_like(rng, n_channels, n_events, n_samples, samplerate, tone_hz=12.0)

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

    freqs = np.array([6.0, 12.0, 24.0], dtype=np.float64)
    out = MorletWaveletFilter(
        freqs=freqs, width=5, output="complex", verbose=False, cpus=1
    ).filter(ts)

    _save(
        "morlet_complex_2ch_2ev_128t",
        input_data=data,
        samplerate=samplerate,
        freqs=freqs,
        width=np.int64(5),
        complete=np.bool_(True),
        expected_output=np.asarray(out.data),
        expected_dims=np.array(out.dims, dtype="U16"),
    )


def make_butterworth_fixture():
    """ButterworthFilter band-stop (60 Hz line-noise notch)."""
    rng = np.random.default_rng(SEED + 3)
    samplerate = 500.0
    n_channels, n_samples = 4, 1024
    # noise + 10 Hz signal + 60 Hz line noise
    t = np.arange(n_samples) / samplerate
    data = (
        rng.standard_normal((n_channels, n_samples)) * 0.2
        + np.sin(2 * np.pi * 10.0 * t)[None, :]
        + np.sin(2 * np.pi * 60.0 * t)[None, :]
    ).astype(np.float64)

    ts = TimeSeries.create(
        data,
        samplerate,
        dims=("channels", "time"),
        coords={"channels": np.arange(n_channels), "time": t},
    )

    freq_range = [58.0, 62.0]
    order = 4
    out = ButterworthFilter(
        freq_range=freq_range, filt_type="stop", order=order
    ).filter(ts)

    _save(
        "butterworth_stop_4ch_1024t",
        input_data=data,
        samplerate=samplerate,
        freq_range=np.array(freq_range, dtype=np.float64),
        order=np.int64(order),
        filt_type=np.array("stop", dtype="U8"),
        expected_output=np.asarray(out.data),
        expected_dims=np.array(out.dims, dtype="U16"),
    )


def make_resample_fixture():
    """ResampleFilter downsample 500 Hz -> 125 Hz."""
    rng = np.random.default_rng(SEED + 4)
    samplerate = 500.0
    n_channels, n_samples = 4, 1024
    t = np.arange(n_samples) / samplerate
    data = (
        rng.standard_normal((n_channels, n_samples)) * 0.2
        + np.sin(2 * np.pi * 10.0 * t)[None, :]
    ).astype(np.float64)

    ts = TimeSeries.create(
        data,
        samplerate,
        dims=("channels", "time"),
        coords={"channels": np.arange(n_channels), "time": t},
    )

    new_rate = 125.0
    out = ResampleFilter(resamplerate=new_rate).filter(ts)

    _save(
        "resample_4ch_1024t_500to125",
        input_data=data,
        samplerate=samplerate,
        new_samplerate=new_rate,
        expected_output=np.asarray(out.data),
        expected_dims=np.array(out.dims, dtype="U16"),
        expected_time=np.asarray(out.coords["time"].data),
    )


def make_monopolar_to_bipolar_fixture():
    """MonopolarToBipolarMapper across 6 channels with 5 sequential pairs."""
    rng = np.random.default_rng(SEED + 5)
    samplerate = 250.0
    n_channels, n_events, n_samples = 6, 4, 256
    data = _eeg_like(rng, n_channels, n_events, n_samples, samplerate, tone_hz=20.0)

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

    pairs = np.array([np.arange(5), np.arange(1, 6)])
    out = MonopolarToBipolarMapper(bipolar_pairs=pairs).filter(ts)

    _save(
        "m2b_6ch_5pairs_4ev_256t",
        input_data=data,
        samplerate=samplerate,
        bipolar_pairs=pairs.astype(np.int64),
        expected_output=np.asarray(out.data),
        expected_dims=np.array(out.dims, dtype="U16"),
    )


def main():
    print("ptsa", ptsa.__version__)
    print("numpy", np.__version__)
    print("scipy", scipy.__version__)
    print("xarray", xarray.__version__)
    print("seed", SEED)
    print("writing fixtures to", FIXTURE_DIR)
    make_morlet_power_fixture()
    make_morlet_phase_fixture()
    make_morlet_complex_fixture()
    make_butterworth_fixture()
    make_resample_fixture()
    make_monopolar_to_bipolar_fixture()
    print("done.")


if __name__ == "__main__":
    main()
