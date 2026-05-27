"""Comprehensive smoke tests — import and minimally invoke every
public PTSA function/class so we catch import-time bugs, constructor
bugs, and gross runtime breakage even for code that has no other
test coverage.

These are not correctness tests — see tests/test_morlet_correctness.py,
tests/test_butterworth_resample_correctness.py, and
tests/test_regression.py for numerical assertions. Smoke tests
intentionally make weak assertions (shape, dtype, basic type) so a
new pandas / numpy / traits release that drops or renames an API
fails *here* (broad signal) before failing in some downstream
analysis script.
"""

import os.path as osp

import h5py
import numpy as np
import pytest


HERE = osp.dirname(osp.abspath(__file__))
DATA = osp.join(HERE, "data")


# ---------------------------------------------------------------------------
# top-level
# ---------------------------------------------------------------------------

def test_smoke_version():
    import ptsa
    assert isinstance(ptsa.__version__, str)
    # Should be PEP-440 ish: x.y.z
    parts = ptsa.__version__.split(".")
    assert len(parts) >= 2 and parts[0].isdigit()


# ---------------------------------------------------------------------------
# ptsa.filt + ptsa.data.timeseries.TimeSeries
# ---------------------------------------------------------------------------

class TestSmokeTimeSeries:
    def _make(self, n_samples=512):
        # n_samples >= 27 so scipy.filtfilt is willing to filter; that
        # threshold is the filter's pad length for default order=4
        # butterworth.
        from ptsa.data.timeseries import TimeSeries
        rng = np.random.default_rng(0)
        return TimeSeries.create(
            rng.standard_normal((3, 4, n_samples)),
            samplerate=100.0,
            dims=("channels", "events", "time"),
            coords={
                "channels": np.arange(3),
                "events": np.arange(4),
                "time": np.arange(n_samples) / 100.0,
            },
        )

    def test_create_and_assert_samplerate_coord(self):
        from ptsa.data.timeseries import TimeSeries
        ts = self._make(n_samples=128)
        assert ts.shape == (3, 4, 128)
        assert float(ts["samplerate"]) == 100.0
        with pytest.raises(AssertionError):
            TimeSeries(np.zeros(3), coords={})  # no samplerate

    def test_coerce_to(self):
        ts = self._make()
        ts.coerce_to(np.float32)
        assert ts.data.dtype == np.float32

    def test_remove_buffer_roundtrip(self):
        ts = self._make()
        buffered = ts.add_mirror_buffer(0.01)  # 1 sample at 100 Hz
        unbuffered = buffered.remove_buffer(0.01)
        assert unbuffered.shape == ts.shape

    def test_baseline_corrected(self):
        ts = self._make()
        out = ts.baseline_corrected((0.0, 0.02))
        assert out.shape == ts.shape

    def test_resampled(self):
        ts = self._make()
        out = ts.resampled(50.0)
        assert float(out["samplerate"]) == 50.0
        assert out.shape[-1] != ts.shape[-1]

    def test_filtered_deprecation(self):
        # The TimeSeries.filtered shortcut still works but emits a
        # DeprecationWarning. Smoke-test both.
        import warnings
        ts = self._make()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            out = ts.filtered([10.0, 20.0])
        assert out.shape == ts.shape

    def test_append_along_existing_dim(self):
        ts1 = self._make()
        ts2 = self._make()
        combined = ts1.append(ts2, dim="time")
        assert combined.shape[-1] == ts1.shape[-1] + ts2.shape[-1]

    def test_filter_with(self):
        from ptsa.data.filters import ButterworthFilter
        ts = self._make()
        out = ts.filter_with(ButterworthFilter(freq_range=[5.0, 10.0]))
        assert out.shape == ts.shape

    def test_to_and_from_hdf(self, tmp_path):
        from ptsa.data.timeseries import TimeSeries
        ts = self._make()
        path = str(tmp_path / "smoke.h5")
        ts.to_hdf(path)
        assert osp.exists(path)
        out = TimeSeries.from_hdf(path)
        np.testing.assert_array_equal(out.data, ts.data)

    def test_concatenation_error_exists(self):
        from ptsa.data.timeseries import ConcatenationError
        assert issubclass(ConcatenationError, Exception)


def test_smoke_filt_buttfilt():
    from ptsa.filt import buttfilt
    sr = 100.0
    sig = np.sin(2 * np.pi * 10 * np.arange(100) / sr)
    out = buttfilt(sig, [5.0, 15.0], sr, "pass", 4)
    assert out.shape == sig.shape


def test_smoke_concat():
    from ptsa.data.timeseries import TimeSeries
    from ptsa.data.concat import concat
    ts1 = TimeSeries.create(
        np.arange(6).reshape(2, 3), samplerate=10.0,
        dims=("ch", "time"),
        coords={"ch": np.arange(2), "time": np.arange(3)},
    )
    ts2 = TimeSeries.create(
        np.arange(6, 12).reshape(2, 3), samplerate=10.0,
        dims=("ch", "time"),
        coords={"ch": np.arange(2, 4), "time": np.arange(3)},
    )
    out = concat((ts1, ts2), dim="ch")
    assert isinstance(out, TimeSeries)
    assert out.shape == (4, 3)


# ---------------------------------------------------------------------------
# ptsa.data.filters
# ---------------------------------------------------------------------------

class TestSmokeFilters:
    @pytest.fixture
    def ts_3d(self):
        from ptsa.data.timeseries import TimeSeries
        rng = np.random.default_rng(0)
        return TimeSeries.create(
            rng.standard_normal((4, 3, 256)),
            samplerate=100.0,
            dims=("channels", "events", "time"),
            coords={
                "channels": np.arange(4),
                "events": np.arange(3),
                "time": np.linspace(0, 2.56, 256),
            },
        )

    def test_base_filter_raises(self):
        from ptsa.data.filters import BaseFilter
        from ptsa.data.timeseries import TimeSeries
        ts = TimeSeries.create(np.zeros(3), samplerate=1.0,
                               dims=("time",), coords={"time": np.arange(3)})
        with pytest.raises(NotImplementedError):
            BaseFilter().filter(ts)

    def test_butterworth(self, ts_3d):
        from ptsa.data.filters import ButterworthFilter
        out = ButterworthFilter(freq_range=[10.0, 20.0]).filter(ts_3d)
        assert out.shape == ts_3d.shape

    def test_resample(self, ts_3d):
        from ptsa.data.filters import ResampleFilter
        out = ResampleFilter(resamplerate=50.0).filter(ts_3d)
        assert out.shape[:-1] == ts_3d.shape[:-1]
        assert out.shape[-1] != ts_3d.shape[-1]
        assert float(out["samplerate"]) == 50.0

    def test_monopolar_to_bipolar(self, ts_3d):
        from ptsa.data.filters import MonopolarToBipolarMapper
        pairs = np.array([np.arange(3), np.arange(1, 4)])
        out = MonopolarToBipolarMapper(bipolar_pairs=pairs).filter(ts_3d)
        assert out.shape[0] == 3  # 3 bipolar pairs

    def test_morlet_power(self, ts_3d):
        from ptsa.data.filters import MorletWaveletFilter
        freqs = np.array([5.0, 10.0])
        out = MorletWaveletFilter(
            freqs=freqs, output="power", verbose=False, cpus=1
        ).filter(ts_3d)
        assert out.shape == (len(freqs),) + ts_3d.shape

    def test_morlet_phase(self, ts_3d):
        from ptsa.data.filters import MorletWaveletFilter
        out = MorletWaveletFilter(
            freqs=np.array([8.0]), output="phase", verbose=False, cpus=1
        ).filter(ts_3d)
        assert out.shape[0] == 1

    def test_morlet_complex(self, ts_3d):
        from ptsa.data.filters import MorletWaveletFilter
        out = MorletWaveletFilter(
            freqs=np.array([8.0]), output="complex", verbose=False, cpus=1
        ).filter(ts_3d)
        assert np.iscomplexobj(out.data)

    def test_morlet_both_power_and_phase(self, ts_3d):
        from ptsa.data.filters import MorletWaveletFilter
        out = MorletWaveletFilter(
            freqs=np.array([8.0]),
            output=("power", "phase"),
            verbose=False, cpus=1,
        ).filter(ts_3d)
        # has an extra 'output' dim of length 2
        assert "output" in out.dims

    def test_data_chopper_with_start_offsets(self):
        from ptsa.data.timeseries import TimeSeries
        from ptsa.data.filters import DataChopper
        sr = 100.0
        n = 1000
        data = np.arange(n, dtype=float)[None, :]
        ts = TimeSeries.create(
            data, sr,
            dims=("channels", "time"),
            coords={
                "channels": np.array([0]),
                "time": np.arange(n) / sr,
                "offsets": ("time", np.arange(n)),
            },
        )
        chopper = DataChopper(
            start_offsets=np.array([100, 300, 500]),
            start_time=0.0, end_time=0.5, buffer_time=0.0,
        )
        out = chopper.filter(ts)
        assert "start_offsets" in out.dims
        assert out.sizes["start_offsets"] == 3


# ---------------------------------------------------------------------------
# ptsa.data.readers
# ---------------------------------------------------------------------------

class TestSmokeReaders:
    """Readers that need only files we have in tests/data/."""

    def test_base_event_reader_matlab(self):
        from ptsa.data.readers import BaseEventReader
        r = BaseEventReader(
            filename=osp.join(DATA, "test_events.mat"),
            normalize_eeg_path=False,
            eliminate_events_with_no_eeg=False,
        )
        events = r.read()
        assert hasattr(events, "dtype")
        # as_dataframe path
        df = r.as_dataframe()
        assert len(df) == len(events)

    def test_cml_event_reader_json(self):
        from ptsa.data.readers import CMLEventReader
        r = CMLEventReader(
            filename=osp.join(DATA, "task_events.json"),
            eliminate_events_with_no_eeg=False,
        )
        evs = r.read()
        assert len(evs) > 0

    def test_tal_reader_json(self):
        from ptsa.data.readers.tal import TalReader
        r = TalReader(
            filename=osp.join(DATA, "pairs.json"),
            struct_type="bi",
            unpack=True,
        )
        arr = r.read()
        assert len(arr) > 0
        assert "channel" in arr.dtype.names
        bp = r.get_bipolar_pairs()
        assert len(bp) == len(arr)

    def test_tal_stim_only_reader_importable(self):
        # TalStimOnlyReader is a subclass; just confirm the import +
        # construction path with a synthetic filename (we don't have a
        # virtualTalStruct fixture, so .read() would error — that's OK).
        from ptsa.data.readers.tal import TalStimOnlyReader
        r = TalStimOnlyReader(filename="nope.mat", struct_type="bi")
        assert r.struct_name == "virtualTalStruct"

    def test_json_index_reader(self):
        from ptsa.data.readers import JsonIndexReader
        r = JsonIndexReader(osp.join(DATA, "r1.json"))
        df = r.as_dataframe()
        assert len(df) > 0

    def test_loc_reader_json(self):
        from ptsa.data.readers import LocReader
        r = LocReader(osp.join(DATA, "localization.json"))
        df = r.read()
        assert len(df) > 0

    def test_edf_raw_reader(self):
        from ptsa.data.readers import EDFRawReader
        r = EDFRawReader(
            dataroot=osp.join(DATA, "eeg.edf"),
            channels=np.array([0, 1, 2]),
            start_offsets=np.array([0]),
            read_size=500,
        )
        data, mask = r.read_file(r.dataroot, r.channels, r.start_offsets, 500)
        assert data.shape[0] == 3
        assert mask.all()

    def test_reader_classes_importable(self):
        # The remaining readers need rhino-style file layouts; just
        # confirm the imports work so a downstream rename catches here.
        from ptsa.data.readers import (
            BaseRawReader,
            BaseReader,
            BinaryRawReader,
            EEGReader,
            H5RawReader,
            NetCDF4XrayReader,
            ParamsReader,
        )
        for cls in (BaseRawReader, BaseReader, BinaryRawReader, EEGReader,
                    H5RawReader, NetCDF4XrayReader, ParamsReader):
            assert isinstance(cls, type)


# ---------------------------------------------------------------------------
# ptsa.extensions.morlet — direct (skip the Python filter wrapper)
# ---------------------------------------------------------------------------

class TestSmokeMorletExtension:
    def test_output_type_enum_values(self):
        from ptsa.extensions import morlet
        assert hasattr(morlet, "POWER")
        assert hasattr(morlet, "PHASE")
        assert hasattr(morlet, "BOTH")
        assert hasattr(morlet, "COMPLEX")

    def test_morlet_wavelet_transform(self):
        from ptsa.extensions import morlet
        sr = 200.0
        n = 512
        sig = np.sin(2 * np.pi * 10 * np.arange(n) / sr).astype(np.float64)
        freqs = np.array([5.0, 10.0, 20.0], dtype=np.float64)
        # SWIG collapses (double *freqs, size_t nf) into one Python
        # arg, so the Python signature is (width, freqs, sample_freq,
        # signal_len[, complete]).
        mwt = morlet.MorletWaveletTransform(5, freqs, sr, len(sig))
        powers = np.empty(len(freqs) * n, dtype=np.float64)
        mwt.multiphasevec(sig, powers)
        powers = powers.reshape(len(freqs), n)
        # 10 Hz bin should have higher mean power than 5 Hz or 20 Hz
        assert powers[1].mean() > powers[0].mean()
        assert powers[1].mean() > powers[2].mean()

    def test_morlet_wavelet_transform_mp(self):
        from ptsa.extensions import morlet
        sr = 200.0
        n = 256
        n_signals = 4
        sigs = np.random.default_rng(0).standard_normal(
            (n_signals, n)).astype(np.float64)
        freqs = np.array([8.0, 16.0], dtype=np.float64)
        mp = morlet.MorletWaveletTransformMP(1)
        mp.initialize_signal_props(sr)
        mp.initialize_wavelet_props(5, freqs, True)
        mp.set_signal_array(sigs)
        out_pow = np.empty((n_signals * len(freqs), n), dtype=np.float64)
        out_phase = np.empty((n_signals * len(freqs), n), dtype=np.float64)
        mp.set_wavelet_pow_array(out_pow)
        mp.set_wavelet_phase_array(out_phase)
        mp.set_output_type(morlet.BOTH)
        mp.prepare_run()
        mp.compute_wavelets_threads()
        assert np.isfinite(out_pow).all()
        assert np.isfinite(out_phase).all()


# ---------------------------------------------------------------------------
# ptsa.extensions.circular_stat — SWIG module
# ---------------------------------------------------------------------------

class TestSmokeCircularStat:
    @staticmethod
    def _cs():
        from ptsa.extensions.circular_stat import circular_stat as cs
        return cs

    def test_circ_diff(self):
        cs = self._cs()
        n = 16
        rng = np.random.default_rng(0)
        c1 = (rng.standard_normal(n) + 1j * rng.standard_normal(n)).astype(np.complex128)
        c2 = (rng.standard_normal(n) + 1j * rng.standard_normal(n)).astype(np.complex128)
        out = np.zeros(n, dtype=np.complex128)
        cs.circ_diff(c1, c2, out)
        # |out| should be approximately 1 (unit phasor diff)
        np.testing.assert_allclose(np.abs(out), np.ones(n), rtol=1e-10)

    def test_circ_diff_par(self):
        cs = self._cs()
        n = 64
        rng = np.random.default_rng(1)
        c1 = (rng.standard_normal(n) + 1j * rng.standard_normal(n)).astype(np.complex128)
        c2 = (rng.standard_normal(n) + 1j * rng.standard_normal(n)).astype(np.complex128)
        out_serial = np.zeros(n, dtype=np.complex128)
        out_par = np.zeros(n, dtype=np.complex128)
        cs.circ_diff(c1, c2, out_serial)
        cs.circ_diff_par(c1, c2, out_par, 4)
        np.testing.assert_array_equal(out_serial, out_par)

    def test_circ_mean(self):
        cs = self._cs()
        # 100 unit phasors all at the same angle -> mean is that angle.
        c = np.exp(1j * np.pi / 4 * np.ones(100, dtype=np.complex128))
        mean = cs.circ_mean(c)
        np.testing.assert_allclose(np.angle(mean), np.pi / 4, rtol=1e-10)
        np.testing.assert_allclose(np.abs(mean), 1.0, rtol=1e-10)

    def test_resultant_vector_and_length(self):
        cs = self._cs()
        c = np.exp(1j * np.pi / 6 * np.ones(50, dtype=np.complex128))
        rv = cs.resultant_vector(c)
        rl = cs.resultant_vector_length(c)
        np.testing.assert_allclose(abs(rv), rl, rtol=1e-10)
        np.testing.assert_allclose(rl, 50.0, rtol=1e-10)

    def test_compute_f_stat(self):
        cs = self._cs()
        n_events = 20
        n_comps = 3
        rng = np.random.default_rng(2)
        phase_diff = (
            rng.standard_normal((n_comps, n_events))
            + 1j * rng.standard_normal((n_comps, n_events))
        ).astype(np.complex128).reshape(-1)
        # Normalize to unit phasors
        phase_diff /= np.abs(phase_diff)
        recalls = np.zeros(n_events, dtype=bool)
        recalls[::2] = True
        f_stat = np.zeros(n_comps, dtype=np.float64)
        cs.compute_f_stat(phase_diff, recalls, f_stat)
        assert np.isfinite(f_stat).all()

    def test_compute_zscores(self):
        cs = self._cs()
        n_stats = 5
        n_perms = 50
        rng = np.random.default_rng(3)
        mat = rng.standard_normal((n_perms, n_stats)).astype(np.float64).reshape(-1)
        cs.compute_zscores(mat, n_perms)
        mat = mat.reshape(n_perms, n_stats)
        # The C++ kernel computes leave-one-out z-scores (mean/std are
        # taken over the OTHER n_perms-1 values), so the per-stat mean
        # isn't exactly zero — but the unit-variance property should
        # still approximately hold.
        assert np.isfinite(mat).all()
        stat_std = mat.std(axis=0)
        np.testing.assert_allclose(stat_std, 1.0, atol=0.2)

    def test_circ_diff_time_bins(self):
        cs = self._cs()
        n = 32
        n_bins = 4
        c1 = np.exp(1j * np.linspace(0, np.pi, n)).astype(np.complex128)
        c2 = np.exp(1j * np.linspace(0, np.pi / 2, n)).astype(np.complex128)
        out_diff = np.zeros(n, dtype=np.complex128)
        out_means = np.zeros(n_bins, dtype=np.complex128)
        cs.circ_diff_time_bins(c1, c2, out_diff, out_means)
        assert np.isfinite(np.abs(out_means)).all()


# ---------------------------------------------------------------------------
# ptsa.extensions.edf
# ---------------------------------------------------------------------------

def test_smoke_edffile():
    from ptsa.extensions.edf import EDFFile
    edf = EDFFile(osp.join(DATA, "eeg.edf"))
    try:
        assert edf.num_channels > 0
        assert edf.num_samples > 0
        info = edf.get_channel_info(0)
        assert isinstance(info.label, str)
    finally:
        edf.close()


# ---------------------------------------------------------------------------
# ptsa.io.hdf5 — legacy helpers
# ---------------------------------------------------------------------------

def test_smoke_io_hdf5_save_load_array(tmp_path):
    from ptsa.io import hdf5
    path = str(tmp_path / "smoke.h5")
    data = np.linspace(0, 1, 16)
    with h5py.File(path, "w") as f:
        hdf5.save_array(f, "data", data)
    with h5py.File(path, "r") as f:
        out = hdf5.load_array(f, "data")
    np.testing.assert_array_equal(out, data)
