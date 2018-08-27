import codecs
import json

import h5py
import numpy as np
import pandas as pd

vlen = np.vectorize(len)
vencode = np.vectorize(codecs.encode)
vdecode = np.vectorize(codecs.decode)


def save_records(hfile, where, data):
    """Save record array-like data to HDF5.

    Parameters
    ----------
    hfile: h5py.File
        Opened HDF5 file object.
    where: str
        Dataset name.
    data: Union[pd.DataFrame, np.array]
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

    dtype = []
    encoded = set()

    for name in data.dtype.names:
        this_dtype = data[name].dtype
        if this_dtype == object or this_dtype.char == "U":
            maxlen = np.amax(vlen(data[name]))
            dtype.append((name, "|S{}".format(maxlen)))
            encoded.add(name)
        else:
            dtype.append((name, this_dtype))

    sanitized = np.recarray(data.shape, dtype=dtype)

    for name, _ in dtype:
        if name in encoded:
            sanitized[name] = vencode(data[name])
        else:
            sanitized[name] = data[name]

    hfile[where] = sanitized
    hfile[where].attrs["utf8_encoded_fields"] = json.dumps(list(encoded))
    hfile[where].attrs["original_type"] = original_type


def load_records(hfile, where):
    """Load data stored with :func:`save`.

    Parameters
    ----------
    hfile: h5py.File
        Open HDF5 file object.
    where: str
        Key to load data from.

    Returns
    -------
    A numpy record array or pandas DataFrame, depending on the originally saved
    type.

    Notes
    -----
    String types will be coerced to dtype "O".

    """
    data = pd.DataFrame(hfile[where][:])
    encoded = json.loads(hfile[where].attrs["utf8_encoded_fields"])
    columns = {key: value for key, value in data.items()}

    for name in encoded:
        columns[name] = vdecode(columns[name])

    df = pd.DataFrame(columns)

    if "DataFrame" not in hfile[where].attrs["original_type"]:
        return df.to_records(index=False)

    return df
