from tempfile import mkdtemp
import os.path as osp
import shutil
import pytest
import numpy as np
import xarray as xr
import h5py

from ptsa.data.TimeSeriesX import TimeSeriesX


@pytest.fixture
def tempdir():
    path = mkdtemp()
    yield path
    shutil.rmtree(path, ignore_errors=True)


def test_samplerate_accessor():
    ts = TimeSeriesX([1], dict(samplerate=1), ['t'])
    assert ts.sample.rate == 1
    ts.sample.rate = 2
    assert ts.sample.rate == 2


def test_init():
    """Test that everything is initialized properly."""
    data = np.random.random((10, 10, 10))
    rate = 1000

    with pytest.raises(AssertionError):
        TimeSeriesX(data, {})

    ts = TimeSeriesX(data, dict(samplerate=rate))
    assert isinstance(ts, xr.DataArray)
    assert ts.shape == (10, 10, 10)
    assert ts['samplerate'] == rate


def test_hdf(tempdir):
    """Test saving/loading with HDF5."""
    data = np.random.random((10, 10, 10, 10))
    dims = ('time', 'x', 'y', 'z')
    coords = {label: np.linspace(0, 1, 10) for label in dims}
    rate = 1

    ts = TimeSeriesX.create(data, rate, coords=coords, dims=dims)

    filename = osp.join(tempdir, "timeseries.h5")
    ts.to_hdf(filename)

    with h5py.File(filename, 'r') as hfile:
        assert "data" in hfile
        assert "dims" in hfile
        assert "coords" in hfile

    loaded = TimeSeriesX.from_hdf(filename)
    assert (loaded.data == data).all()
    for coord in loaded.coords:
        assert (loaded.coords[coord] == ts.coords[coord]).all()
    for n, dim in enumerate(dims):
        assert loaded.dims[n] == dim


def test_filtered():
    data = np.random.random(1000)
    dims = ['time']

    ts = TimeSeriesX.create(data, 10, dims=dims)

    # TODO: real test (i.e., actually care about the filtering)
    new_ts = ts.filtered([1, 2])
    assert ts['samplerate'] == new_ts['samplerate']
    assert all(ts.data != new_ts.data)
    for key, attr in ts.attrs.items():
        assert attr == new_ts[key]
    assert ts.name == new_ts.name
    assert ts.dims == new_ts.dims


def test_resampled():
    ts = TimeSeriesX.create(np.linspace(0, 100, 100), 10., dims=['time'])

    resampled = ts.resampled(20.)
    assert resampled.data.shape == (200,)
    assert resampled['samplerate'] == 20

    resampled = ts.resampled(5)
    assert resampled.data.shape == (50,)
    assert resampled['samplerate'] == 5


def test_remove_buffer():
    pass


def test_add_mirror_buffer():
    points = 100

    data = np.array([-1] * points + [1] * points)
    samplerate = 10.
    coords = {'time': np.linspace(-1, 1, points*2)}
    dims = ['time']
    ts = TimeSeriesX.create(data, samplerate, coords=coords, dims=dims)

    duration = 10
    buffered = ts.add_mirror_buffer(duration)
    assert len(buffered.data) == len(data) + 2 * duration * samplerate


def test_baseline_corrected():
    t = np.linspace(0, 10, 100)
    values = np.array([1]*50 + [2]*50)
    coords = {"time": t}
    ts = TimeSeriesX.create(values, 10., coords, dims=("time",))
    corrected = ts.baseline_corrected((0, 5))
    assert all(ts['time'] == corrected['time'])
    assert ts['samplerate'] == corrected['samplerate']
    assert all(corrected.data[:50] == 0)
    assert all(corrected.data[50:] == 1)
