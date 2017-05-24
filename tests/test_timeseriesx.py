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
