import numpy as np

from ptsa.data.readers.raw import BaseRawReader

try:
    from ptsa.data.readers.edf.edffile import EDFFile
except ImportError:
    EDFFile = None


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
            Channels to read from.
        start_offsets : np.ndarray
            Indices to start reading at (*not* the actual offset times).
        read_size : int
            Number of samples to read at each offset.

        Returns
        -------


        """
        with EDFFile(filename) as edf:
            if not len(channels):
                channels = [n for n in range(edf.num_channels)]
            else:
                channels = [int(n) for n in channels]

            # data = edf.read_samples(channels, read_size, 0)
            data = edf.read_samples(2, 120, 100)

        return data


if __name__ == "__main__":
    import os.path as osp

    filename = osp.expanduser("~/mnt/rhino/data/eeg/eeg/scalp/ltp/ltpFR2/LTP375/session_0/eeg/LTP375_session_0.bdf")

    reader = EDFRawReader(dataroot=filename)
    data = reader.read_file(filename, [])
    print(data)

    import pandas as pd
    ax = pd.Series(data).plot()
    ax.get_figure().savefig('/tmp/out.png')
