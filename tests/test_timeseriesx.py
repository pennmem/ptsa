import pytest
import numpy as np
import xarray as xr

from ptsa.data.TimeSeriesX import TimeSeriesX


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
    print(ts['samplerate'])
    assert ts['samplerate'] == rate


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
    pass


def test_remove_buffer():
    pass


def test_add_mirror_buffer():
    pass


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
