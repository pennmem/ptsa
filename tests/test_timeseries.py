from tempfile import mkdtemp
import os.path as osp
import shutil
import warnings
import pytest
import numpy as np
import xarray as xr
import h5py

from ptsa import __version__
from ptsa.data.filters import ResampleFilter
from ptsa.data.timeseries import TimeSeries, ConcatenationError


@pytest.fixture
def tempdir():
    path = mkdtemp()
    yield path
    shutil.rmtree(path, ignore_errors=True)


def test_init():
    """Test that everything is initialized properly."""
    data = np.random.random((10, 10, 10))
    rate = 1000

    with pytest.raises(AssertionError):
        TimeSeries(data, {})

    with pytest.raises(AssertionError):
        TimeSeries.create(data, None, coords={})

    assert TimeSeries.create(data, None, coords={'samplerate': 1}).samplerate == 1

    ts = TimeSeries(data, dict(samplerate=rate))
    assert isinstance(ts, xr.DataArray)
    assert ts.shape == (10, 10, 10)
    assert ts['samplerate'] == rate


def test_arithmetic_operations():
    data = np.arange(1000).reshape(10, 10, 10)
    rate = 1000

    ts_1 = TimeSeries.create(data, None, coords={'samplerate': 1})
    ts_2 = TimeSeries.create(data, None, coords={'samplerate': 1})

    ts_out = ts_1 + ts_2

    print('ts_out=', ts_out)


def test_hdf(tempdir):
    """Test saving/loading with HDF5."""
    data = np.random.random((10, 10, 10, 10))
    dims = ('time', 'x', 'y', 'z')
    coords = {label: np.linspace(0, 1, 10) for label in dims}
    rate = 1

    ts = TimeSeries.create(data, rate, coords=coords, dims=dims, name="test")

    filename = osp.join(tempdir, "timeseries.h5")
    ts.to_hdf(filename)

    with h5py.File(filename, 'r') as hfile:
        assert "data" in hfile
        assert "dims" in hfile
        assert "coords" in hfile
        assert "name" in list(hfile['/'].attrs.keys())
        assert "ptsa_version" in hfile.attrs
        assert hfile.attrs["ptsa_version"] == __version__
        assert "created" in hfile.attrs

    loaded = TimeSeries.from_hdf(filename)
    assert np.all(loaded.data == data)

    for coord in loaded.coords:
        assert (loaded.coords[coord] == ts.coords[coord]).all()

    for n, dim in enumerate(dims):
        assert loaded.dims[n] == dim
    assert loaded.name == "test"

    ts_with_attrs = TimeSeries.create(data, rate, coords=coords, dims=dims,
                                      name="test", attrs=dict(a=1, b=[1, 2]))
    ts_with_attrs.to_hdf(filename)
    loaded = TimeSeries.from_hdf(filename)

    for key in ts_with_attrs.attrs:
        assert ts_with_attrs.attrs[key] == loaded.attrs[key]
    assert np.all(loaded.data == data)

    for coord in loaded.coords:
        assert (loaded.coords[coord] == ts_with_attrs.coords[coord]).all()

    for n, dim in enumerate(dims):
        assert loaded.dims[n] == dim

    assert loaded.name == "test"


def test_load_hdf_base64():
    """Test that we can still load the base64-encoded HDF5 format."""
    filename = osp.join(osp.dirname(__file__), "data", "R1111M_base64.h5")
    ts = TimeSeries.from_hdf(filename)

    assert "event" in ts.coords
    assert len(ts.coords["event"] == 10)


@pytest.mark.parametrize("cls,kwargs", [
    (None, {}),
    (ResampleFilter, {"resamplerate": 1.}),
])
def test_filter_with(cls, kwargs):
    ts = TimeSeries.create(
        np.random.random((2, 100)),
        samplerate=10,
        dims=("x", "time"),
        coords={
            "x": range(2),
            "time": range(100),
        }
    )

    if cls is None:
        class MyClass(object):
            pass

        with pytest.raises(TypeError):
            ts.filter_with(MyClass)
    else:
        tsf = ts.filter_with(cls, **kwargs)
        assert isinstance(tsf, TimeSeries)
        assert tsf.data.shape != ts.data.shape


def test_filtered():
    data = np.random.random(1000)
    dims = ['time']

    ts = TimeSeries.create(data, 10, dims=dims)

    # TODO: real test (i.e., actually care about the filtering)
    with warnings.catch_warnings(record=True) as w:
        new_ts = ts.filtered([1, 2])
        assert len(w) == 1
        assert ts['samplerate'] == new_ts['samplerate']
        assert all(ts.data != new_ts.data)
        for key, attr in ts.attrs.items():
            assert attr == new_ts[key]
        assert ts.name == new_ts.name
        assert ts.dims == new_ts.dims


def test_resampled():
    ts = TimeSeries.create(np.linspace(0, 100, 100), 10., dims=['time'])

    resampled = ts.resampled(20.)
    assert resampled.data.shape == (200,)
    assert resampled['samplerate'] == 20

    resampled = ts.resampled(5)
    assert resampled.data.shape == (50,)
    assert resampled['samplerate'] == 5


def test_remove_buffer():
    length = 100
    data = np.array([0]*length)
    samplerate = 10.
    coords = {'time': np.linspace(-1, 1, length)}
    dims = ['time']
    ts = TimeSeries.create(data, samplerate, coords=coords, dims=dims)

    with pytest.raises(ValueError):
        # We can't remove this much
        ts.remove_buffer(int(samplerate * length + 1))

    buffer_dur = 0.1
    buffered = ts.add_mirror_buffer(buffer_dur)
    unbuffered = buffered.remove_buffer(buffer_dur)

    assert len(unbuffered.data) == len(ts.data)
    assert (unbuffered.data == ts.data).all()


def test_add_mirror_buffer():
    points = 100

    data = np.array([-1] * points + [1] * points)
    samplerate = 10.
    coords = {'time': np.linspace(-1, 1, points*2)}
    dims = ['time']
    ts = TimeSeries.create(data, samplerate, coords=coords, dims=dims)

    duration = 10
    buffered = ts.add_mirror_buffer(duration)
    assert len(buffered.data) == len(data) + 2 * duration * samplerate

    with pytest.raises(ValueError):
        # 100 s is longer than the length of data
        ts.add_mirror_buffer(100)


def test_baseline_corrected():
    t = np.linspace(0, 10, 100)
    values = np.array([1]*50 + [2]*50)
    coords = {"time": t}
    ts = TimeSeries.create(values, 10., coords, dims=("time",))
    corrected = ts.baseline_corrected((0, 5))
    assert all(ts['time'] == corrected['time'])
    assert ts['samplerate'] == corrected['samplerate']
    assert all(corrected.data[:50] == 0)
    assert all(corrected.data[50:] == 1)


@pytest.mark.parametrize("i,j,k,expected", [
    (0, 0, 0, 0),
    (0, 0, 1, 2),
    (9, 9, 9, 1998),
])
def test_addition(i, j, k, expected):
    data = np.arange(1000).reshape(10,10,10)
    rate = 1000

    ts_1 = TimeSeries.create(data, None, coords={'samplerate': 1})
    ts_2 = TimeSeries.create(data, None, coords={'samplerate': 1})

    ts_out = ts_1 + ts_2
    assert ts_out[i,j,k] == expected


def test_samplerate_prop():
    data = np.arange(1000).reshape(10,10,10)
    rate = 1000

    ts_1 = TimeSeries.create(data, None, coords={'samplerate': 1})
    ts_2 = TimeSeries.create(data, None, coords={'samplerate': 2})

    with pytest.raises(AssertionError):
        ts_out = ts_1 + ts_2


def test_coords_ops():
    data = np.arange(1000).reshape(10,10,10)

    ts_1 = TimeSeries.create(data, None, dims=['x', 'y', 'z'],
                             coords={'x':np.arange(10),
                                     'y':np.arange(10),
                                     'z':np.arange(10)*2,
                                     'samplerate': 1})
    ts_2 = TimeSeries.create(data, None, dims=['x', 'y', 'z'],
                             coords={'x':np.arange(10),
                                     'y':np.arange(10),
                                     'z':np.arange(10),
                                     'samplerate': 1})
    ts_out = ts_1 + ts_2
    assert ts_out.z.shape[0] == 5

    ts_out_1 = ts_1 + ts_2[...,::2]

    assert (ts_out_1 == ts_out).all()

    ts_out_2 = ts_2[...,1::2] + ts_2[...,::2]

    assert ts_out_2.shape[-1] ==0

    ts_out_3 = ts_2[...,[0,2,3,4,8]] + ts_2[...,[3,4,8,9]]

    assert (ts_out_3.z.data == np.array([3,4,8])).all()


def test_mean():
    """tests various ways to compute mean - collapsing different
combination of axes"""
    data = np.arange(100).reshape(10,10)
    ts_1 = TimeSeries.create(data, None, dims=['x', 'y'],
                             coords={'x': np.arange(10) * 2,
                                     'y':np.arange(10),
                                     'samplerate': 1})
    grand_mean = ts_1.mean()

    assert grand_mean == 49.5

    x_mean  = ts_1.mean(dim='x')
    assert (x_mean == np.arange(45,55,1, dtype=np.float)).all()
    # checking axes
    assert(ts_1.y == x_mean.y).all()

    y_mean = ts_1.mean(dim='y')
    assert (y_mean == np.arange(4.5,95,10, dtype=np.float)).all()
    # checking axes
    assert (y_mean.x == ts_1.x).all()

    # test mean NaN
    data_2 = np.arange(100, dtype=np.float).reshape(10,10)
    np.fill_diagonal(data_2,np.NaN)
    # data_2[9,9] = 99


    ts_2 = TimeSeries.create(data_2, None, dims=['x', 'y'],
                             coords={'x': np.arange(10) * 2,
                                     'y':np.arange(10),
                                     'samplerate': 1})

    grand_mean = ts_2.mean(skipna=True)
    assert grand_mean == 49.5


@pytest.mark.skipif(int(xr.__version__.split('.')[1]) > 7,
                    reason="dtype lost on xarray >= 0.8")
def test_concatenate():
    """make sure we can concatenate easily time series x - test it with rec
    array as one of the coords.

    This fails for xarray > 0.7. See
    https://github.com/pydata/xarray/issues/1434 for details.

    """
    p1 = np.array([('John', 180), ('Stacy', 150), ('Dick',200)],
                  dtype=[('name', '|S256'), ('height', int)])
    p2 = np.array([('Bernie', 170), ('Donald', 250), ('Hillary',150)],
                  dtype=[('name', '|S256'), ('height', int)])

    data = np.arange(50, 80, 1, dtype=np.float)
    dims = ['measurement', 'participant']

    ts1 = TimeSeries.create(data.reshape(10, 3), None, dims=dims,
                            coords={
                                 'measurement': np.arange(10),
                                 'participant': p1,
                                 'samplerate': 1
                             })

    ts2 = TimeSeries.create(data.reshape(10, 3) * 2, None, dims=dims,
                            coords={
                                 'measurement': np.arange(10),
                                 'participant': p2,
                                 'samplerate': 1
                             })

    combined = xr.concat((ts1, ts2), dim='participant')

    assert isinstance(combined, TimeSeries)
    assert (combined.participant.data['height'] ==
            np.array([180, 150, 200, 170, 250, 150])).all()
    assert (combined.participant.data['name'] ==
            np.array([
                'John', 'Stacy', 'Dick', 'Bernie', 'Donald', 'Hillary'])).all()


def test_append_simple():
    """Test appending without regard to dimensions."""
    points = 100
    data1 = np.random.random(points)
    data2 = np.random.random(points)
    coords1 = {'time': np.linspace(0, points, points)}
    coords2 = {'time': np.linspace(points, points*2, points)}
    dims = ["time"]
    samplerate = 10.

    # Base case: everything should Just Work
    ts1 = TimeSeries.create(data1, samplerate, coords=coords1, dims=dims)
    ts2 = TimeSeries.create(data2, samplerate, coords=coords2, dims=dims)
    combined = ts1.append(ts2)
    assert combined.samplerate == samplerate
    assert (combined.data == np.concatenate([data1, data2])).all()
    assert combined.dims == ts1.dims
    assert combined.dims == ts2.dims
    assert (combined.coords['time'] == np.concatenate(
        [coords1['time'], coords2['time']])).all()

    # Append along a new dimension
    combined = ts1.append(ts2, dim='notyet')
    assert combined.shape == (2, 100)
    assert hasattr(combined, 'notyet')

    # Incompatible sample rates
    ts1 = TimeSeries.create(data1, samplerate, coords=coords1, dims=dims)
    ts2 = TimeSeries.create(data2, samplerate + 1, coords=coords2, dims=dims)
    with pytest.raises(ConcatenationError):
        ts1.append(ts2)


def test_append_recarray():
    """Test appending along a dimension with a recarray."""
    p1 = np.array([('John', 180), ('Stacy', 150), ('Dick',200)],
                  dtype=[('name', '|S256'), ('height', int)])
    p2 = np.array([('Bernie', 170), ('Donald', 250), ('Hillary',150)],
                  dtype=[('name', '|S256'), ('height', int)])

    data = np.arange(50, 80, 1, dtype=np.float)
    dims = ['measurement', 'participant']

    ts1 = TimeSeries.create(data.reshape(10, 3), None, dims=dims,
                            coords={
                                 'measurement': np.arange(10),
                                 'participant': p1,
                                 'samplerate': 1
                             })

    ts2 = TimeSeries.create(data.reshape(10, 3) * 2, None, dims=dims,
                            coords={
                                 'measurement': np.arange(10),
                                 'participant': p2,
                                 'samplerate': 1
                             })

    ts3 = TimeSeries.create(data.reshape(10, 3) * 2, None, dims=dims,
                            coords={
                                 'measurement': np.arange(10),
                                 'participant': p2,
                                 'samplerate': 2
                             })

    ts4 = TimeSeries.create(data.reshape(10, 3) * 2, None, dims=dims,
                            coords={
                                 'measurement': np.linspace(0, 1, 10),
                                 'participant': p2,
                                 'samplerate': 2
                             })

    combined = ts1.append(ts2, dim='participant')

    assert isinstance(combined, TimeSeries)
    assert (combined.participant.data['height'] == np.array(
        [180, 150, 200, 170, 250, 150])).all()
    names = np.array([b'John', b'Stacy', b'Dick', b'Bernie',
                      b'Donald', b'Hillary'])
    assert (combined.participant.data['name'] == names).all()

    # incompatible sample rates
    with pytest.raises(ConcatenationError):
        ts1.append(ts3)

    # incompatible other dimensions (measurement)
    with pytest.raises(ConcatenationError):
        ts1.append(ts4)
