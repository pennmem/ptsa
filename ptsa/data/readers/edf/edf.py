from ptsa.data.readers.raw import BaseRawReader
from ptsa.data.readers.edf.edffile import EDFFile


class EDFRawReader(BaseRawReader):
    """Reads EEG data stored in the European Data Format (EDF/BDF, EDF+/BDF+
    formats).

    """


if __name__ == "__main__":
    import os.path as osp

    edf = EDFFile(osp.expanduser("~/mnt/rhino//data/eeg/eeg/scalp/ltp/ltpFR2/LTP375/session_0/eeg/LTP375_session_0.bdf"))
    print("Samples:", edf.get_num_samples())
    print("Annotations:", edf.get_num_annotations())
    data = edf.read_samples(0, 100, 0)
    print(data)