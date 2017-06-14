import os.path as osp
import numpy as np
from ptsa.data.TimeSeriesX import TimeSeriesX
from ptsa.data.readers import BaseEventReader
from ptsa.data.readers import EEGReader

filename = osp.expanduser('~/mnt/rhino/data/events/dBoy25/FR423_events_sess0.mat')
events = BaseEventReader(filename=filename, use_reref_eeg = False,
                         eliminate_events_with_no_eeg=True).read()

coords = osp.expanduser('~/mnt/rhino/data/eeg/FR423/tal/MNIcoords.txt')
with open(coords, 'r') as f:
    txtIN = f.read()

monopolar_channels = np.array([elec.split(' ')[0].zfill(3) for elec in txtIN.split('\n') if elec != ''])
eeg = EEGReader(events=events[:10], channels=monopolar_channels, start_time=0.0, end_time=1.0, buffer_time=1.0).read()
eeg.to_hdf('/tmp/EEG_test_FR423.h5')

loaded = TimeSeriesX.from_hdf('/tmp/EEG_test_FR423.h5')

print(eeg)
print(loaded)
print(eeg == loaded)
