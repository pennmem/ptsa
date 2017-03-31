import sys
from ptsa.data.readers import BaseEventReader
from ptsa.data.readers.TalReader import TalReader
from ptsa.data.readers import EEGReader

ev_path = '/Volumes/rhino_root/data/events/pyFR/TJ011_events.mat'
base_e_reader = BaseEventReader(filename=ev_path, eliminate_events_with_no_eeg=True)
base_events = base_e_reader.read()

base_events = base_events[base_events.type == 'WORD']