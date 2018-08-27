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
    utf8_encoded = set()
    json_encoded = set()

    for name in data.dtype.names:
        this_dtype = data[name].dtype
        if this_dtype == object or this_dtype.char == "U":
            maxlen = np.amax(vlen(data[name]))
            dtype.append((name, "|S{}".format(maxlen)))
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
                maxlen = np.amax(vlen(json_data))
                dtype[i] = (name, "|S{}".format(maxlen))
                sanitized = sanitized.astype(dtype)

                sanitized[name] = json_data
                utf8_encoded.remove(name)
                json_encoded.add(name)
        else:
            sanitized[name] = data[name]

    hfile[where] = sanitized
    hfile[where].attrs["utf8_encoded_fields"] = json.dumps(list(utf8_encoded))
    hfile[where].attrs["json_encoded_fields"] = json.dumps(list(json_encoded))
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
    utf8_encoded = json.loads(hfile[where].attrs["utf8_encoded_fields"])
    json_encoded = json.loads(hfile[where].attrs["json_encoded_fields"])
    columns = {key: value for key, value in data.items()}

    for name in utf8_encoded:
        columns[name] = vdecode(columns[name])

    for name in json_encoded:
        columns[name] = [json.loads(col) for col in columns[name]]

    df = pd.DataFrame(columns)

    if "DataFrame" not in hfile[where].attrs["original_type"]:
        return df.to_records(index=False)

    return df
