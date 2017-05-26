import numpy as np
from numpy.testing import *
from os.path import *
import unittest
from ptsa.data.readers import BaseEventReader
from ptsa.data.readers import CMLEventReader
from dataset_utils import *

class TestEventReaders(unittest.TestCase):
    def setUp(self):

        self.prefix = '/Users/m'

    def test_ram_event_readers(self):

        task = 'RAM_FR1'
        subject_list = ['R1111M', 'R1065J']

        for subject in subject_list:
            e_path = e_path_matlab(self.prefix, subject, task)
            evs = read_events(e_path=e_path, reader_class=BaseEventReader, use_reref_eeg=True)
            cml_evs = read_events(e_path=e_path, reader_class=CMLEventReader, normalize_eeg_path=True)

            num_path_diffs = np.sum(cml_evs.eegfile != evs.eegfile)

            assert_equal(num_path_diffs, 0, 'paths in the eegfile field are different between events'
                                            'read with CMLEventReader and BaseEventReader')

    def test_ram_event_readers_change_to_noreref(self):

        task = 'RAM_FR1'
        subject_list = ['R1111M', 'R1065J']

        for subject in subject_list:
            e_path = e_path_matlab(self.prefix, subject, task)
            evs = read_events(e_path=e_path, reader_class=BaseEventReader, use_reref_eeg=False)
            cml_evs = read_events(e_path=e_path,
                                  reader_class=CMLEventReader,
                                  normalize_eeg_path=True,
                                  eeg_fname_search_pattern='eeg.reref',
                                  eeg_fname_replace_pattern='eeg.noreref'
                                  )

            num_path_diffs = np.sum(cml_evs.eegfile != evs.eegfile)

            assert_equal(num_path_diffs, 0, 'paths in the eegfile field are different between events'
                                            'read with CMLEventReader and BaseEventReader')

    def test_ram_event_readers_no_path_normalization(self):

        task = 'RAM_FR1'
        subject_list = ['R1111M', 'R1065J']

        for subject in subject_list:
            e_path = e_path_matlab(self.prefix, subject, task)
            evs = read_events(e_path=e_path, reader_class=BaseEventReader, use_reref_eeg=False,
                              normalize_eeg_path=False)
            cml_evs = read_events(e_path=e_path,
                                  reader_class=CMLEventReader,
                                  normalize_eeg_path=False,
                                  eeg_fname_search_pattern='eeg.reref',
                                  eeg_fname_replace_pattern='eeg.noreref'
                                  )

            num_path_diffs = np.sum(cml_evs.eegfile != evs.eegfile)

            assert_equal(num_path_diffs, 0, 'paths in the eegfile field are different between events'
                                            'read with CMLEventReader and BaseEventReader')

    def test_scalp_event_readers_reref(self):

        subject_list = ['LTP001', 'LTP002', 'LTP040']
        task = 'catFR'

        for subject in subject_list:
            e_path = e_path_matlab_scalp(self.prefix, subject, task)

            evs = read_events(e_path=e_path,
                              reader_class=BaseEventReader,
                              common_root='data/scalp_events',
                              use_reref_eeg=True)

            cml_evs = read_events(e_path=e_path,
                                  reader_class=CMLEventReader,
                                  common_root='data/scalp_events',
                                  normalize_eeg_path=True
                                  )

            num_path_diffs = np.sum(cml_evs.eegfile != evs.eegfile)

            assert_equal(num_path_diffs, 0, 'paths in the eegfile field are different between events'
                                            'read with CMLEventReader and BaseEventReader')


    def test_scalp_event_readers_no_path_manipulation(self):

        subject_list = ['LTP001', 'LTP002', 'LTP040']
        task = 'catFR'

        for subject in subject_list:
            e_path = e_path_matlab_scalp(self.prefix, subject, task)

            evs = read_events(e_path=e_path,
                              reader_class=BaseEventReader,
                              common_root='data/scalp_events',
                              use_reref_eeg=True,
                              normalize_eeg_path=False
                              )

            cml_evs = read_events(e_path=e_path,
                                  reader_class=CMLEventReader
                                  )

            num_path_diffs = np.sum(cml_evs.eegfile != evs.eegfile)

            assert_equal(num_path_diffs, 0, 'paths in the eegfile field are different between events'
                                            'read with CMLEventReader and BaseEventReader')


