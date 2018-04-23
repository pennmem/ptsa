import numpy as np
from numpy.testing import *
from os.path import *
import unittest
from ptsa.data.readers import BaseEventReader
import traceback

from ptsa.data.readers.EEGReader import EEGReader
from ptsa.data.filters.ButterworthFilter import ButterworthFilter
from ptsa.data.filters.ResampleFilter import ResampleFilter
from ptsa.data.filters.morlet import MorletWaveletFilter
from ptsa.data.readers.tal import TalReader
from ptsa.data.readers import EEGReader
from ptsa.data.filters import DataChopper
from ptsa.data.filters import MonopolarToBipolarMapper
import sys


class UnicodeEventDataRead(unittest.TestCase):
    def setUp(self):
        self.start_time = -0.5
        self.end_time = 1.6
        self.buffer_time = 0.5

        self.event_range = range(0, 30, 1)
        self.prefix = '/Volumes/rhino_root'

        self.task = 'dBoy25'


    def read_events_debug(self):

        # event_files = ['/Users/m/data/dboy_ev.mat']
        event_files = ['/Volumes/rhino_root/data/eeg/FR438/behavioral/session_0/events.mat']
        for event_file in event_files:
            e_path = event_file

            base_e_reader =BaseEventReader(filename=e_path, eliminate_events_with_no_eeg=False, normalize_eeg_path=False)

            base_events = base_e_reader.read()
            print base_events['store'][447]


            return base_events



