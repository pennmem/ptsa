"""Low-level HDF5 helpers.

Used to back ``TimeSeries.to_hdf``/``from_hdf``; current
``TimeSeries.to_hdf`` writes via ``xarray.DataArray.to_netcdf`` (engine
``netcdf4``), so this module is largely unused but kept for any legacy
callers that still touch records on disk in this format.
"""
from __future__ import annotations

import codecs
import json
from typing import Any, Iterable, Union

import numpy as np
import pandas as pd

__all__ = ["maxlen", "save_array", "load_array", "save_records", "load_records"]

# ``hfile`` is an open ``h5py.File`` at runtime; typed ``Any`` to avoid
# pulling h5py into the type-check graph (its dataset/attrs types are
# permissive and would inject Datatype-vs-Dataset noise that is unrelated
# to the actual call shape used here).
H5FileLike = Any

#: A scalar string length or a 1-D arraylike of length-bearing items.
ArrayLike1D = Union[np.ndarray, pd.Series, Iterable]

# ``np.vectorize`` returns a callable wrapper around the supplied ufunc; we
# annotate the call sites rather than the wrappers themselves because the
# wrappers stay schema-less at runtime.
vlen = np.vectorize(len)
vencode = np.vectorize(codecs.encode)
vdecode = np.vectorize(codecs.decode)


def maxlen(a: ArrayLike1D) -> int:
    """Maximum element length, with a floor of 1.

    HDF5 requires all datatypes to be at least 1 element long, so
    ``maxlen`` always returns at least 1.
    """
    _max = int(np.amax(vlen(a)))
    return max(_max, 1)


def save_array(
    hfile: H5FileLike, where: str, data: Union[np.ndarray, pd.DataFrame]
) -> None:
    """Save a generic numpy array or pandas DataFrame to HDF5.

    Parameters
    ----------
    hfile
        Opened HDF5 file object.
    where
        Dataset name.
    data
        The data to write.

    Notes
    -----
    When saving a DataFrame, the index information will be lost.
    """
    if isinstance(data, np.ndarray):
        # ``dtype.names`` is non-None iff the dtype is structured (record),
        # which is the path that needs ``save_records``. Equivalent to the
        # old ``len(data.dtype) > 0`` but avoids tickling the dtype/__len__
        # stub mismatch under pyright.
        if data.dtype.names is not None:
            return save_records(hfile, where, data)
    elif isinstance(data, pd.DataFrame):
        return save_records(hfile, where, data)

    if data.dtype.char == "U":
        strlen = maxlen(data)
        hfile[where] = data.astype("|S{}".format(strlen))
        hfile[where].attrs["string"] = True
    else:
        hfile[where] = data
        hfile[where].attrs["string"] = False

    hfile[where].attrs["tabular"] = False


def load_array(
    hfile: H5FileLike, where: str
) -> Union[np.ndarray, np.recarray, pd.DataFrame]:
    """Load an array from HDF5 that was saved with :func:`save_array`."""
    if hfile[where].attrs["tabular"]:
        return load_records(hfile, where)

    data = hfile[where][()]

    if hfile[where].attrs["string"]:
        return vdecode(data)
    else:
        return data


def save_records(
    hfile: H5FileLike, where: str, data: Union[np.ndarray, pd.DataFrame]
) -> None:
    """Save record array-like data to HDF5.

    Parameters
    ----------
    hfile
        Opened HDF5 file object.
    where
        Dataset name.
    data
        The data to write.

    Notes
    -----
    When saving a DataFrame, the index information will be lost.
    """
    original_type = str(type(data))

    if isinstance(data, pd.DataFrame):
        data = data.to_records(index=False)
    if not isinstance(data, np.recarray):
        data = np.rec.array(data)

    dtype: list[tuple[str, object]] = []
    utf8_encoded: set[str] = set()
    json_encoded: set[str] = set()

    # ``np.recarray.dtype.names`` is typed as ``tuple[str, ...] | None`` even
    # though every recarray actually has named fields. Narrow with an assert
    # so the loop below type-checks without a per-iteration cast.
    field_names = data.dtype.names
    assert field_names is not None, "recarray must have named fields"

    for name in field_names:
        this_dtype = data[name].dtype
        if this_dtype.itemsize == 0:
            this_dtype = np.dtype("|{}1".format(this_dtype.char))

        if this_dtype == object or this_dtype.char == "U":
            dtype.append((name, "|S{}".format(maxlen(data[name]))))
            utf8_encoded.add(name)
        else:
            dtype.append((name, this_dtype))

    sanitized = np.recarray(data.shape, dtype=dtype)

    for i, (name, _) in enumerate(dtype):
        if name in utf8_encoded:
            try:
                sanitized[name] = vencode(data[name])
            except TypeError:  # try dumping with JSON (for list/dict types)
                json_data = [json.dumps(col).encode() for col in data[name]]

                # We have to change the dtype which requires copying the array.
                # Maybe there is a better way to detect if something is JSON-
                # encodable earlier on?
                dtype[i] = (name, "|S{}".format(maxlen(json_data)))
                sanitized = sanitized.astype(dtype)

                sanitized[name] = json_data
                utf8_encoded.remove(name)
                json_encoded.add(name)
        else:
            sanitized[name] = data[name]

    hfile[where] = sanitized
    hfile[where].attrs["tabular"] = True
    hfile[where].attrs["utf8_encoded_fields"] = json.dumps(list(utf8_encoded))
    hfile[where].attrs["json_encoded_fields"] = json.dumps(list(json_encoded))
    hfile[where].attrs["original_type"] = original_type


def load_records(
    hfile: H5FileLike, where: str
) -> Union[pd.DataFrame, np.recarray]:
    """Load data stored with :func:`save_records`.

    Parameters
    ----------
    hfile
        Open HDF5 file object.
    where
        Key to load data from.

    Returns
    -------
    A numpy record array or pandas DataFrame, depending on the originally
    saved type.

    Notes
    -----
    String types will be coerced to dtype "O".
    """
    data = pd.DataFrame(hfile[where][:])
    utf8_encoded = json.loads(hfile[where].attrs["utf8_encoded_fields"])
    json_encoded = json.loads(hfile[where].attrs["json_encoded_fields"])
    # ``data.items()`` yields ``(Hashable, Series)`` pairs (column labels
    # can be ints), so widen the value type to ``Any`` — the ``vdecode``/
    # json decode path overwrites entries with ndarrays and lists too.
    columns: dict[Any, Any] = {key: value for key, value in data.items()}

    for name in utf8_encoded:
        columns[name] = vdecode(columns[name])

    for name in json_encoded:
        columns[name] = [json.loads(col.decode()) for col in columns[name]]

    df = pd.DataFrame(columns)

    if "DataFrame" not in hfile[where].attrs["original_type"]:
        return df.to_records(index=False)

    return df
