import numpy as np

import unittest

from ptsa.data.readers import CMLEventReader

import traceback

from ptsa.data.readers.TalReader import TalReader
from ptsa.data.readers import EEGReader

from dataset_utils import *


class TestEEGReaders(unittest.TestCase):
    def setUp(self):
        self.start_time = -0.5
        self.end_time = 1.6
        self.buffer_time = 0.5

        self.event_range = range(0, 30, 1)
        self.prefix = '/Users/m'

    def test_scalp_eeg_readers(self):

        subject_list = ['LTP001', 'LTP002', 'LTP040']
        task = 'catFR'

        monopolar_channels = np.array(map(lambda x: str(x).zfill(3), range(1,129)))

        for subject in subject_list:
            e_path = e_path_matlab_scalp(self.prefix, subject, task)

            cml_evs = read_events(e_path=e_path,
                                  reader_class=CMLEventReader,
                                     common_root='data/scalp_events',
                                     normalize_eeg_path=True
                                  )



            eeg_reader = EEGReader(events=cml_evs[:30], channels = monopolar_channels,
                       start_time=self.start_time, end_time=self.end_time, buffer_time=self.buffer_time)

            eegs = eeg_reader.read()
            print eegs





