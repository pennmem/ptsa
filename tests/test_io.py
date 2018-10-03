import h5py
import numpy as np
import pandas as pd
import pytest

from ptsa.io import hdf5

@pytest.fixture
def hfilename(tmpdir):
    return str(tmpdir.join("test.h5"))


class TestHDF5IO:
    def test_maxlen(self):
        array = ["a", "bb", "ccc", "dddd"]
        assert hdf5.maxlen(array) == 4

        array = ["", "", ""]
        assert hdf5.maxlen(array) == 1

    @pytest.mark.parametrize("data", [
        np.linspace(0, 100, 100, dtype=int),
        np.array(["R1111M", "R1", "whatever", "another string"]),
        pd.DataFrame({
            "a": [1, 2, 3],
            "b": [3, 2, 1],
        }),
        np.array(["","",""], dtype='S'),
    ])
    def test_save_load_array(self, data, hfilename):
        with h5py.File(hfilename, "w") as hfile:
            hdf5.save_array(hfile, "data", data)

        with h5py.File(hfilename, "r") as hfile:
            data_out = hdf5.load_array(hfile, "data")
            assert all(data == data_out)

    @pytest.mark.parametrize("data_in", [
        pd.DataFrame({
            "string": ["a", "string"],
            "integer": [1, 2],
            "float": [1., 2.],
            "dict": [{"a": 1}, {"b": 2}],
            "zero_len_string": ["", ""],
        }),
        np.rec.array(
            [("a", 1, {"a": 1}, ""), ("longer string", 2, {"b": 2}, "")],
            dtype=[("description", "<U32"), ("number", int), ("dict", object), ("empty_string", "S")]
        ),
    ])
    def test_save_load_records(self, data_in, tmpdir):
        filename = str(tmpdir.join("test.h5"))

        with h5py.File(filename, "w") as hfile:
            hdf5.save_records(hfile, "data", data_in)

        with h5py.File(filename, "r") as hfile:
            data_out = hdf5.load_records(hfile, "data")
            assert str(type(data_in)) == str(type(data_out))

            if isinstance(data_in, pd.DataFrame):
                assert (data_out == data_in).all().all()
            else:
                assert set(data_in.dtype.names) == set(data_out.dtype.names)
                for name in data_in.dtype.names:
                    assert all(data_in[name] == data_out[name])
