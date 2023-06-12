from copy import copy
from tempfile import mkdtemp
from functools import partial
import os.path as osp
from tempfile import mkdtemp
import shutil
import sys
import warnings

import h5py
import numpy as np
from numpy.testing import assert_equal, assert_allclose
import pytest
import xarray as xr
import pandas as pd

from ptsa import __version__
from ptsa.data.filters import ResampleFilter
from ptsa.data.timeseries import TimeSeries, ConcatenationError
from tests.utils import assert_timeseries_equal, skip_without_rhino
from ptsa.data.concat import concat


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


@pytest.mark.parametrize("dtype", [int, None, np.float32, np.float64])
def test_coerce_to(dtype):
    shape = (1, 10, 100)

    ts = TimeSeries.create(
        np.random.random(shape),
        samplerate=1,
        dims=("a", "b", "c"),
        coords={
            "a": np.linspace(0, 1, shape[0]),
            "b": np.linspace(0, 1, shape[1]),
            "c": np.linspace(0, 1, shape[2])
        }
    )

    orig_dtype = copy(ts.data.dtype)
    ts.coerce_to(dtype)
    assert ts.data.dtype == dtype
    if orig_dtype != dtype:
        assert ts.data.dtype != orig_dtype


def test_hdf(tempdir):
    """Test saving/loading with HDF5."""
    data = np.random.random((10, 10, 10, 10))
    data = data.astype(float)
    dims = ('time', 'x', 'y', 'z')
    coords = {label: np.linspace(0, 1, 10) for label in dims}
    rate = 1

    ts = TimeSeries.create(data, rate, coords=coords, dims=dims, name="test")

    filename = osp.join(tempdir, "timeseries.h5")
    ts.to_hdf(filename)

    # with h5py.File(filename, 'r') as hfile:
        # assert "data" in hfile
        # assert "dims" in hfile
        # assert "coords" in hfile
        # assert "name" in list(hfile['/'].attrs.keys())
        # assert "ptsa_version" in hfile.attrs
        # assert hfile.attrs["ptsa_version"] == __version__
        # assert "created" in hfile.attrs

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
        assert np.all(ts_with_attrs.attrs[key] == loaded.attrs[key])
    assert np.all(loaded.data == data)

    for coord in loaded.coords:
        assert (loaded.coords[coord] == ts_with_attrs.coords[coord]).all()

    for n, dim in enumerate(dims):
        assert loaded.dims[n] == dim

    assert loaded.name == "test"


#@pytest.mark.skipif(sys.version_info[0] < 3,
#                    reason="cmlreaders doesn't support legacy Python")
@pytest.skip(allow_module_level=True)
class TestCMLReaders:
    @property
    def reader(self):
        from cmlreaders import CMLReader
        from tests.utils import get_rhino_root

        try:
            rootdir = get_rhino_root()
        except OSError:
            rootdir = None

        return CMLReader("R1111M", "FR1", 0, rootdir=rootdir)

    def make_eeg(self, events, rel_start, rel_stop):
        """Fake EEG data for testing without rhino."""
        from cmlreaders.eeg_container import EEGContainer

        channels = ["CH{}".format(n) for n in range(1, 10)]
        data = np.random.random((len(events), len(channels), rel_stop - rel_start))

        container = EEGContainer(data, 1000, events=events, channels=channels)

        return container

    @skip_without_rhino
    def test_hdf_rhino(self, tmpdir):
        from cmlreaders.warnings import MultiplePathsFoundWarning

        filename = str(tmpdir.join("test.h5"))

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", MultiplePathsFoundWarning)

            events = self.reader.load("events")
            ev = events[events.eegoffset > 0].sample(n=5)
            eeg = self.reader.load_eeg(events=ev, rel_start=0, rel_stop=10)

        ts = eeg.to_ptsa()
        ts.to_hdf(filename)

        ts2 = TimeSeries.from_hdf(filename)
        assert_timeseries_equal(ts, ts2)

    def test_hdf(self, tmpdir):
        from cmlreaders.readers.readers import EventReader
        from unittest.mock import patch

        efile = osp.join(osp.dirname(__file__), "data", "R1111M_FR1_0_events.json")
        filename = str(tmpdir.join("test.h5"))
        ev = EventReader.fromfile(efile, subject="R1111M", experiment="FR1")
        ev = ev[ev.eegoffset > 0].sample(n=5)
        ev = ev.drop(columns=['stim_params', 'test'])

        rel_start, rel_stop = 0, 10
        get_eeg = partial(self.make_eeg, ev, rel_start, rel_stop)

        reader = self.reader
        
        with patch.object(reader, "load_eeg", return_value=get_eeg()):
            eeg = reader.load_eeg(events=ev, rel_start=0, rel_stop=10)

        ts = eeg.to_ptsa()
        print(ts)
        print(ts.event)
        print(type(ts.event))
        print(ts.indexes)
        print(ts.indexes['eegoffset'])
        #ts = ts.assign_coords({'event':pd.MultiIndex.from_frame(ev)})

        import pdb;
        pdb.set_trace()

        ts.to_hdf(filename)

        ts2 = TimeSeries.from_hdf(filename)
        assert_timeseries_equal(ts, ts2)


@pytest.mark.skipif(sys.version_info[0] < 3,
                    reason="not loadable in legacy Python")
def test_load_hdf_base64():
    """Test that we can still load the base64-encoded HDF5 format."""
    filename = osp.join(osp.dirname(__file__), "data", "R1111M_base64.h5")
    ts = TimeSeries.from_hdf(filename)

    assert "event" in ts.coords
    assert len(ts.coords["event"]) == 10


class TestFilterWith:
    @pytest.mark.parametrize("cls,kwargs", [
        (ResampleFilter, {"resamplerate": 1.}),
    ])
    def test_single_filter(self, cls, kwargs):
        ts = TimeSeries.create(
            np.random.random((2, 100)),
            samplerate=10,
            dims=("x", "time"),
            coords={
                "x": range(2),
                "time": range(100),
            }
        )

        filt = cls(**kwargs)
        tsf = ts.filter_with(filt)
        assert isinstance(tsf, TimeSeries)
        assert tsf.data.shape != ts.data.shape

    def test_multi_filter(self):
        from ptsa.data.filters.base import BaseFilter

        class NegationFilter(BaseFilter):
            def filter(self, timeseries: TimeSeries) -> TimeSeries:
                return timeseries * -1

        class DoubleFilter(BaseFilter):
            def filter(self, timeseries: TimeSeries) -> TimeSeries:
                return timeseries * 2

        filters = [
            NegationFilter(),
            DoubleFilter()
        ]

        init_data = np.random.random((10, 10, 10))

        ts = TimeSeries.create(
            init_data, 1,
            coords={
                "events": np.linspace(0, init_data.shape[0], init_data.shape[0]),
                "channels": np.linspace(0, init_data.shape[1], init_data.shape[1]),
                "time": np.linspace(0, init_data.shape[2], init_data.shape[2]),
            },
            dims=["events", "channels", "time"]
        )

        new_ts = ts.filter_with(filters)
        assert_equal((-ts * 2).data, new_ts.data)
        assert_equal(ts["time"].data, new_ts["time"].data)
        assert_equal(ts.coords.keys(), new_ts.coords.keys())
        assert_equal(ts.dims, new_ts.dims)


def test_remove_line_noise():
    ts = None


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
    assert (x_mean == np.arange(45,55,1, dtype=float)).all()
    # checking axes
    assert(ts_1.y == x_mean.y).all()

    y_mean = ts_1.mean(dim='y')
    assert (y_mean == np.arange(4.5,95,10, dtype=float)).all()
    # checking axes
    assert (y_mean.x == ts_1.x).all()

    # test mean NaN
    data_2 = np.arange(100, dtype=float).reshape(10,10)
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

    """
    p1 = np.array([('John', 180), ('Stacy', 150), ('Dick',200)],
                  dtype=[('name', '|S256'), ('height', int)])
    p2 = np.array([('Bernie', 170), ('Donald', 250), ('Hillary',150)],
                  dtype=[('name', '|S256'), ('height', int)])

    data = np.arange(50, 80, 1, dtype=int)
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

    combined = concat((ts1, ts2), dim='participant')

    assert isinstance(combined, TimeSeries)
    assert (combined.participant.data['height'] ==
            np.array([180, 150, 200, 170, 250, 150])).all()
    assert (combined.participant.data['name'].astype(str) ==
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

    data = np.arange(50, 80, 1, dtype=float)
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
