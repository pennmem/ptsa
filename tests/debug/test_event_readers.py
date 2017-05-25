import numpy as np
from numpy.testing import *
from os.path import *
import unittest
from ptsa.data.readers import BaseEventReader
from ptsa.data.readers import CMLEventReader

import traceback

from ptsa.data.readers.TalReader import TalReader
from ptsa.data.readers import EEGReader


class TestPyFR(unittest.TestCase):
    def setUp(self):
        self.start_time = -0.5
        self.end_time = 1.6
        self.buffer_time = 0.5

        self.event_range = range(0, 30, 1)
        # self.prefix = '/Volumes/rhino_root'
        self.prefix = '/Users/m'

        # self.task = 'pyFR'
        # self.subject_list = ['BW001', 'FR025', 'BW013', 'FR029', 'BW014', 'FR060', 'FR070', 'FR080', 'BW025', 'FR090',
        #                      'CH003', 'FR091', 'CH005', 'FR100', 'CH008b', 'FR110', 'CH012', 'FR120', 'CH013', 'FR130',
        #                      'CH018', 'FR140', 'CH040', 'CH042', 'CH046', 'FR170', 'CH048', 'CH058', 'CH061', 'CH063',
        #                      'CH065', 'CH066', 'CH067', 'CH068', 'FR032', 'FR037', 'FR038', 'FR050', 'FR270', 'FR280',
        #                      'TJ075', 'UP044_1', 'UP044', 'UP045', 'UP046']

        # self.task = 'FR1'
        # self.ram_subject_list = ['R1111M', 'R1065J']

    def read_events_BaseEventReader(self, e_path, **kwds):

        base_e_reader = BaseEventReader(filename=e_path, eliminate_events_with_no_eeg=True, **kwds)

        base_events = base_e_reader.read()
        return base_events

    def read_ram_events_BaseEventReader_Matlab(self, task, subject, **kwds):
        e_path = join(self.prefix, 'data/events/%s/%s_events.mat' % ('RAM_' + task, subject))
        return self.read_events_BaseEventReader(e_path, **kwds)

    def read_scalp_events_BaseEventReader_Matlab(self, task, subject, **kwds):
        e_path = join(self.prefix, 'data/scalp_events/%s/%s_events.mat' % (task, subject))
        return self.read_events_BaseEventReader(e_path, **kwds)

    def read_ram_events_BaseEventReader_JSON(self, task, subject, **kwds):
        e_path = join(self.prefix, 'protocols/r1/subjects/%s/experiments/%s/sessions/0/behavioral/current_processed'
                                   '/task_events.json' % (subject, task))

        return self.read_events_BaseEventReader(e_path, **kwds)

    def read_events_CMLEventReader(self, e_path, **kwds):

        base_e_reader = CMLEventReader(filename=e_path, eliminate_events_with_no_eeg=True, **kwds)

        base_events = base_e_reader.read()
        return base_events

    def read_ram_events_CMLEventReader_Matlab(self, task, subject, **kwds):
        e_path = join(self.prefix, 'data/events/%s/%s_events.mat' % ('RAM_' + task, subject))
        return self.read_events_CMLEventReader(e_path, **kwds)

    def read_scalp_events_CMLEventReader_Matlab(self, task, subject, **kwds):
        e_path = join(self.prefix, 'data/scalp_events/%s/%s_events.mat' % (task, subject))
        return self.read_events_CMLEventReader(e_path, **kwds)

    def read_ram_events_CMLEventReader_JSON(self, task, subject, **kwds):
        e_path = join(self.prefix, 'protocols/r1/subjects/%s/experiments/%s/sessions/0/behavioral/current_processed'
                                   '/task_events.json' % (subject, task))

        return self.read_events_CMLEventReader(e_path, **kwds)

    def test_ram_event_readers(self):

        subjects_failed = []

        cml_readers = [self.read_ram_events_CMLEventReader_Matlab, self.read_ram_events_CMLEventReader_JSON]
        base_readers = [self.read_ram_events_BaseEventReader_Matlab, self.read_ram_events_BaseEventReader_JSON]

        # cml_readers = [self.read_events_CMLEventReader_Matlab]
        # base_readers = [self.read_events_BaseEventReader_Matlab]

        # cml_readers = [self.read_events_CMLEventReader_JSON]
        # base_readers = [self.read_events_BaseEventReader_JSON]

        print('Testing "unmodified" events')
        task = 'FR1'
        subject_list = ['R1111M', 'R1065J']

        for subject in subject_list:
            print ('processing subject ', subject)

            for cml_reader, base_reader in zip(cml_readers, base_readers):
                cml_evs = cml_reader(task, subject, normalize_eeg_path=True)
                try:
                    evs = base_reader(task, subject,
                                      use_reref_eeg=True)
                except NotImplementedError as e:
                    if str(e).strip() == 'Reref from JSON not implemented':
                        continue

                num_path_diffs = np.sum(cml_evs.eegfile != evs.eegfile)
                try:
                    assert_equal(num_path_diffs, 0, 'paths in the eegfile field are different between events'
                                                    'read with CMLEventReader and BaseEventReader')
                except AssertionError:

                    subjects_failed.append(subject)

        print ('Testing noreref substitution in the events')

        for subject in subject_list:
            print 'processing subject ', subject

            for cml_reader, base_reader in zip(cml_readers, base_readers):

                cml_evs = cml_reader(
                    task, subject,
                    eeg_fname_search_pattern='eeg.reref',
                    eeg_fname_replace_pattern='eeg.noreref',
                    normalize_eeg_path=True
                )

                evs = base_reader(task, subject,
                                  use_reref_eeg=False)

                num_path_diffs = np.sum(cml_evs.eegfile != evs.eegfile)

                try:
                    assert_equal(num_path_diffs, 0, 'paths in the eegfile field are different between events'
                                                    'read with CMLEventReader and BaseEventReader')
                except AssertionError:

                    subjects_failed.append(subject)

        for subject in subject_list:
            print ('processing subject ', subject)
            for cml_reader, base_reader in zip(cml_readers, base_readers):

                cml_evs = cml_reader(
                    task, subject,
                    eeg_fname_search_pattern='eeg.reref',
                    eeg_fname_replace_pattern='eeg.noreref',
                    normalize_eeg_path=False)

                evs = base_reader(task, subject,
                                  use_reref_eeg=False, normalize_eeg_path=False)

                num_path_diffs = np.sum(cml_evs.eegfile != evs.eegfile)

                try:
                    assert_equal(num_path_diffs, 0, 'paths in the eegfile field are different between events'
                                                    'read with CMLEventReader and BaseEventReader')
                except AssertionError:
                    subjects_failed.append(subject)

        assert_equal(len(subjects_failed), 0,
                     'The following subjects had event read errors %s' % ', '.join(subjects_failed))

    def test_scalp_event_readers(self):

        subjects_failed = []

        cml_readers = [self.read_scalp_events_CMLEventReader_Matlab]
        base_readers = [self.read_scalp_events_BaseEventReader_Matlab]

        subject_list = ['LTP001', 'LTP002', 'LTP040']
        task = 'catFR'

        print ('Testing events with normalized eeg paths')
        for subject in subject_list:
            print ('processing subject ', subject)

            for cml_reader, base_reader in zip(cml_readers, base_readers):
                cml_evs = cml_reader(task, subject, common_root='data/scalp_events', normalize_eeg_path=True)

                evs = base_reader(task, subject,
                                  use_reref_eeg=True, common_root='data/scalp_events')

                num_path_diffs = np.sum(cml_evs.eegfile != evs.eegfile)
                try:
                    assert_equal(num_path_diffs, 0, 'paths in the eegfile field are different between events'
                                                    'read with CMLEventReader and BaseEventReader')
                except AssertionError:

                    subjects_failed.append(subject)

        print ('testing event read with no path_manipulation')
        for subject in subject_list:
            print ('processing subject ', subject)

            for cml_reader, base_reader in zip(cml_readers, base_readers):
                cml_evs = cml_reader(task, subject)

                evs = base_reader(task, subject,
                                  use_reref_eeg=True,
                                  normalize_eeg_path=False)

                num_path_diffs = np.sum(cml_evs.eegfile != evs.eegfile)
                try:
                    assert_equal(num_path_diffs, 0, 'paths in the eegfile field are different between events'
                                                    'read with CMLEventReader and BaseEventReader')
                except AssertionError:

                    subjects_failed.append(subject)

        assert_equal(len(subjects_failed), 0,
                     'The following subjects had event read errors %s' % ', '.join(subjects_failed))

    def test_scalp_eeg_readers(self):

        subjects_failed = []

        cml_readers = [self.read_scalp_events_CMLEventReader_Matlab]
        base_readers = [self.read_scalp_events_BaseEventReader_Matlab]

        print ('Testing "unmodified" events')

        subject_list = ['LTP001', 'LTP002', 'LTP040']
        task = 'catFR'

        monopolar_channels = np.array(map(lambda x: str(x).zfill(3), range(1,129)))

        for subject in subject_list:
            print ('processing subject ', subject)

            for cml_reader, base_reader in zip(cml_readers, base_readers):
                cml_evs = cml_reader(task, subject,
                                     common_root='data/scalp_events',
                                     normalize_eeg_path=True
                                     )

                evs = base_reader(task, subject,
                                  use_reref_eeg=True,
                                  common_root='data/scalp_events')

                num_path_diffs = np.sum(cml_evs.eegfile != evs.eegfile)
                try:
                    assert_equal(num_path_diffs, 0, 'paths in the eegfile field are different between events'
                                                    'read with CMLEventReader and BaseEventReader')
                except AssertionError:

                    subjects_failed.append(subject)

                try:
                    eeg_reader = EEGReader(events=cml_evs[:30], channels = monopolar_channels,
                               start_time=self.start_time, end_time=self.end_time, buffer_time=self.buffer_time)

                    eegs = eeg_reader.read()
                except StandardError:
                    subjects_failed.append(subject)
                    print ('traceback:',traceback.print_exc())

        assert_equal(len(subjects_failed), 0,
                     'The following subjects had event read errors %s' % ', '.join(subjects_failed))
