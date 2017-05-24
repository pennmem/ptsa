import numpy as np
import ptsa
from numpy.testing import *
import unittest
from ptsa.data.readers import BaseEventReader

from ptsa.data.readers.EEGReader import EEGReader
from ptsa.data.filters.ButterworthFilter import ButterworthFilter
from ptsa.data.filters.ResampleFilter import ResampleFilter
from ptsa.data.filters.MorletWaveletFilter import MorletWaveletFilter
from ptsa.data.readers.TalReader import TalReader
from ptsa.data.readers import EEGReader
from ptsa.data.filters import DataChopper
from ptsa.data.filters import MonopolarToBipolarMapper
import sys


class IndexingDemo(object):
    def __init__(self):
        self.start_time = -0.5
        self.end_time = 1.6
        self.buffer_time = 0.5

        self.event_range = range(0, 30, 1)
        self.e_path = '/Users/m/data/events/RAM_FR1/R1060M_events.mat'
        tal_path = '/Users/m/data/eeg/R1060M/tal/R1060M_talLocs_database_bipol.mat'

        if sys.platform.startswith('win'):
            self.e_path = 'D:/data/events/RAM_FR1/R1060M_events.mat'
            tal_path = 'D:/data/eeg/R1060M/tal/R1060M_talLocs_database_bipol.mat'

        tal_reader = TalReader(filename=tal_path)
        self.monopolar_channels = tal_reader.get_monopolar_channels()
        self.bipolar_pairs = tal_reader.get_bipolar_pairs()

        # ---------------- NEW STYLE PTSA -------------------
        base_e_reader = BaseEventReader(filename=self.e_path, eliminate_events_with_no_eeg=True)

        base_events = base_e_reader.read()

        base_events = base_events[base_events.type == 'WORD']

        base_ev_order = np.argsort(base_events, order=('session', 'list', 'mstime'))
        self.base_events = base_events[base_ev_order]

        # retaining first session
        dataroot = self.base_events[0].eegfile
        self.base_events = self.base_events[self.base_events.eegfile == dataroot]

        self.base_events = self.base_events[self.event_range]

        eeg_reader = EEGReader(events=self.base_events, channels=self.monopolar_channels,
                               start_time=self.start_time, end_time=self.end_time, buffer_time=self.buffer_time)

        self.base_eegs = eeg_reader.read()

        session_reader = EEGReader(session_dataroot=dataroot, channels=self.monopolar_channels)
        self.session_eegs = session_reader.read()


if __name__ == '__main__':
    id_demo = IndexingDemo()

    eegs = id_demo.base_eegs

    print 'Names of the coords: '
    print eegs.dims

    print 'masking array based on one of the coords:'
    print eegs.events.data['recalled'] == True

    print 'Simple positional indexing:'

    print eegs[:, eegs.events.data['recalled'] == True, :]

    print 'explicit selection: '
    print eegs.sel(events=eegs.events.data['recalled'] == True)

    print 'comparing both ways of selection:'

    comp_eeg = eegs[:, eegs.events.data['recalled'] == True, :] - eegs.sel(events=eegs.events.data['recalled'] == True)

    print comp_eeg


    print 'Sum of all entries in comp_eeg = ', np.sum(comp_eeg)

    print 'Using dictionary to index: '

    print eegs[dict(events=eegs.events.data['recalled'] == True)]

    resampled_series = eegs.resampled(100)










    # new_eegs = eegs[:, eegs.events.data['recalled'] == True, :] + eegs[:, eegs.events.data['recalled'] == True, :]

    print
