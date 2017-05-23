__author__ = 'm'

import sys
from ptsa.data.readers import BaseEventReader
from ptsa.data.readers import PTSAEventReader
from ptsa.data.events import Events

import numpy as np
# from numpy.testing import *
import unittest
from unittest import *

from EventReadersTestBase import EventReadersTestBase

from ptsa.data.readers import BaseEventReader
from ptsa.data.readers.TalReader import TalReader
from ptsa.data.readers import EEGReader

from os.path import *


class TestEEGRead(unittest.TestCase):
    def setUp(self):
        self.prefix = '/Volumes/rhino_root'

    def test_pyfr_eegs(self):
        sub = 'BW001'
        task = 'pyFR'

        #read electrode info
        tal_path = join(self.prefix, 'data/eeg/' + sub + '/tal/' + sub + '_talLocs_database_bipol.mat')
        tal_reader = TalReader(filename=tal_path)
        monopolar_channels = tal_reader.get_monopolar_channels()
        bipolar_pairs = tal_reader.get_bipolar_pairs()
        sub_elecs = tal_reader.tal_struct_array

        # Get events
        e_path = join(self.prefix, 'data/events/' + task + '/' + sub + '_events.mat')
        base_e_reader = BaseEventReader(filename=e_path, eliminate_events_with_no_eeg=True)
        base_events = base_e_reader.read()
        evs = base_events[base_events.type == 'WORD']


        #Get EEGs
        eeg_reader = EEGReader(events=evs, channels=monopolar_channels,
                              start_time=0.0, end_time=1.6, buffer_time=1.0)
        base_eegs = eeg_reader.read()

        print

if __name__ == '__main__':
    unittest.main(verbosity=2)
