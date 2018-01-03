from contextlib import closing
import logging
import os.path as osp
import warnings

import numpy as np

from ptsa.data.readers.raw import BaseRawReader

try:
    from ptsa.data.readers.edf.edffile import EDFFile
except ImportError:
    EDFFile = None


logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class EDFRawReader(BaseRawReader):
    """Reads EEG data stored in the European Data Format (EDF/BDF, EDF+/BDF+
    formats).

    Keyword arguments
    -----------------
    dataroot : str
        Full path to EDF/BDF/EDF+/BDF+ file (including extension).
    channels : List[Union[str, int]]
        List of channels to read.


    """
    def __init__(self, **kwargs):
        if EDFFile is None:
            raise RuntimeError(
                "The compiled edffile extension module was not found.\n"
                "This probably means you don't have pybind11 installed.\n"
                "Please pip install pybind11 then reinstall ptsa"
            )

        _, data_ext = osp.splitext(kwargs['dataroot'])
        if not len(data_ext):
            raise RuntimeError('Dataroot missing extension (must be supplied for EDF reader)')

        # FIXME: we don't need this once the base class is more generic
        self.params_dict = {'gain': 1.0}

    def read_file(self, filename, channels, start_offsets=np.array([0]),
                  read_size=-1):
        """Read an EDF/BDF/EDF+/BDF+ file.

        Parameters
        ----------
        filename : str
            Path to file to read.
        channels : list
            Channels to read from. If False-like, use all channels.
        start_offsets : np.ndarray
            Indices to start reading at (*not* the actual offset times).
        read_size : int
            Number of samples to read at each offset.

        Returns
        -------
        Tuple[np.ndarray, np.ndarray]
            A tuple containing the array of EEG data and a boolean index mask
            indicating whether each offset was read successfully.

        """
        with closing(EDFFile(filename)) as edf:
            if not len(channels):
                channels = [n for n in range(edf.num_channels)]
            else:
                channels = [int(n) for n in channels]

            # Read all data
            if read_size < 0:
                if len(start_offsets) > 1:
                    msg = "start_offsets given when read_size implies reading all data"
                    warnings.warn(msg, UserWarning)
                data = edf.read_samples(channels, edf.num_samples)
                return data[:, None, :], np.ones((len(channels), 1), dtype=bool)

            # Read epochs
            else:
                data = np.empty((len(channels), len(start_offsets), read_size),
                                dtype=np.float) * np.nan
                read_ok_mask = np.ones((len(channels), len(start_offsets)),
                                       dtype=bool)

                for i, offset in enumerate(start_offsets):
                    if offset < 0:
                        logger.warning("Cannot read negative offset %d", offset)
                        read_ok_mask[:, i] = False
                        continue

                    samples = edf.read_samples(channels, read_size, offset=offset)
                    if samples.shape[1] == read_size:
                        data[:, i, :] = samples
                    else:
                        logger.warning("Cannot read full chunk of data for offset %d... probably end of file", offset)
                        read_ok_mask[:, i] = False

                return data, read_ok_mask


if __name__ == "__main__":
    logger.addHandler(logging.StreamHandler())
    filename = osp.expanduser("~/mnt/rhino/data/eeg/eeg/scalp/ltp/ltpFR2/LTP375/session_0/eeg/LTP375_session_0.bdf")

    reader = EDFRawReader(dataroot=filename)
    data, mask = reader.read_file(filename, [], read_size=1024, start_offsets=[0, 1024, 2048])
    print(data)
