import numpy as np
from numpy.testing import *
from os.path import *
import unittest
from ptsa.data.readers import BaseEventReader
import traceback

from ptsa.data.readers.EEGReader import EEGReader
from ptsa.data.filters.ButterworthFilter import ButterworthFilter
from ptsa.data.filters.ResampleFilter import ResampleFilter
from ptsa.data.filters.MorletWaveletFilter import MorletWaveletFilter
from ptsa.data.readers.TalReader import TalReader
from ptsa.data.readers import EEGReader
from ptsa.data.filters import DataChopper
from ptsa.data.filters import MonopolarToBipolarMapper
import sys


class TestPyFR(unittest.TestCase):
    def setUp(self):
        self.start_time = -0.5
        self.end_time = 1.6
        self.buffer_time = 0.5

        self.event_range = range(0, 30, 1)
        self.prefix = '/Volumes/rhino_root'

        self.task = 'pyFR'
        self.subject_list = ['BW001', 'FR025', 'BW013', 'FR029', 'BW014', 'FR060', 'FR070', 'FR080', 'BW025', 'FR090',
                             'CH003', 'FR091', 'CH005', 'FR100', 'CH008b', 'FR110', 'CH012', 'FR120', 'CH013', 'FR130',
                             'CH018', 'FR140', 'CH040', 'CH042', 'CH046', 'FR170', 'CH048', 'CH058', 'CH061', 'CH063',
                             'CH065', 'CH066', 'CH067', 'CH068', 'FR032', 'FR037', 'FR038', 'FR050', 'FR270', 'FR280',
                             'TJ075', 'UP044_1', 'UP044', 'UP045', 'UP046']

        # self.e_path = '/Users/m/data/events/RAM_FR1/R1060M_events.mat'
        # tal_path = '/Users/m/data/eeg/R1060M/tal/R1060M_talLocs_database_bipol.mat'
        #
        # if sys.platform.startswith('win'):
        #     self.e_path = 'D:/data/events/RAM_FR1/R1060M_events.mat'
        #     tal_path = 'D:/data/eeg/R1060M/tal/R1060M_talLocs_database_bipol.mat'
        #
        #
        # tal_reader = TalReader(filename=tal_path)
        # self.monopolar_channels = tal_reader.get_monopolar_channels()
        # self.bipolar_pairs = tal_reader.get_bipolar_pairs()
        #
        # # ---------------- NEW STYLE PTSA -------------------
        # base_e_reader = BaseEventReader(filename=self.e_path, eliminate_events_with_no_eeg=True)
        #
        # base_events = base_e_reader.read()
        #
        # base_events = base_events[base_events.type == 'WORD']
        #
        # base_ev_order = np.argsort(base_events, order=('session', 'list', 'mstime'))
        # self.base_events = base_events[base_ev_order]
        #
        # # retaining first session
        # dataroot = self.base_events[0].eegfile
        # self.base_events = self.base_events[self.base_events.eegfile == dataroot]
        #
        # self.base_events = self.base_events[self.event_range]
        #
        # # self.base_events = base_events[self.event_range]
        #
        # # self.base_events = self.read_base_events()
        #
        # eeg_reader = EEGReader(events=self.base_events, channels=self.monopolar_channels,
        #                        start_time=self.start_time, end_time=self.end_time, buffer_time=self.buffer_time)
        #
        # self.base_eegs = eeg_reader.read()
        #
        # session_reader = EEGReader(session_dataroot=dataroot, channels=self.monopolar_channels)
        # self.session_eegs = session_reader.read()

    def read_events(self, task, subject):
        e_path = join(self.prefix, 'data/events/%s/%s_events.mat' % (task, subject))

        base_e_reader = BaseEventReader(filename=e_path, eliminate_events_with_no_eeg=True)

        base_events = base_e_reader.read()
        return base_events

    def read_electrode_info(self, subject):

        tal_path = join(self.prefix, 'data/eeg/%s/tal/%s_talLocs_database_bipol.mat' % (subject, subject))

        tal_reader = TalReader(filename=tal_path)

        monopolar_channels = tal_reader.get_monopolar_channels()
        bipolar_pairs = tal_reader.get_bipolar_pairs()
        tal_struct = tal_reader.read()

        return tal_struct, monopolar_channels, bipolar_pairs


    def read_eegs(self, events, channels):

        eeg_reader = EEGReader(events=events, channels=channels,
                               start_time=self.start_time, end_time=self.end_time, buffer_time=self.buffer_time)

        self.base_eegs = eeg_reader.read()


    def test_event_reader(self):
        error_count = 0
        subjects_failed = []

        for subject in self.subject_list:
            print 'processing subject ', subject

            try:
                self.read_events(self.task, subject)
            except StandardError as e:
                error_count += 1
                print traceback.print_exc()
                subjects_failed.append(subject)
                print str(e)

        assert_equal(error_count, 0, 'The following subjects failed event read %s' % (','.join(subjects_failed)))

    def test_tal_reader(self):
        error_count = 0
        subjects_failed = []

        for subject in self.subject_list:
            print 'processing subject ', subject

            try:
                tal_struct, monopolar_channels, bipolar_pairs = self.read_electrode_info(subject)

            except StandardError as e:
                error_count += 1
                print traceback.print_exc()
                subjects_failed.append(subject)
                print str(e)
                continue

        assert_equal(error_count, 0,
                     'The following subjects failed electrode info read %s' % (','.join(subjects_failed)))

    def test_eeg_reader(self):
        num_test_failed = 0
        subject_failed_eeg = []
        subjects_failed_events = []
        subjects_failed_electrode_info = []

        for subject in self.subject_list:

            print 'processing subject ', subject


            try:
                events = self.read_events(self.task, subject)
            except StandardError as e:
                events = None
                print traceback.print_exc()
                subjects_failed_events.append(subject)

                print str(e)

            try:
                tal_struct, monopolar_channels, bipolar_pairs = self.read_electrode_info(subject)
            except StandardError as e:
                tal_struct, monopolar_channels, bipolar_pairs = None,None,None
                print traceback.print_exc()
                subjects_failed_electrode_info.append(subject)
                print str(e)

            try:
                if events is not None and monopolar_channels is not None:
                    eegs = self.read_eegs(events=events,channels=monopolar_channels)
            except StandardError as e:
                print 'Error in subject: ', subject
                print traceback.print_exc()

                eegs = None
                subject_failed_eeg.append(subject)

        try:
            assert_equal(len(subjects_failed_electrode_info), 0,
                         'The following subjects failed electrode info read %s' % (
                         ','.join(subjects_failed_electrode_info)))
        except StandardError as e:
            print traceback.print_exc()
            num_test_failed += 1

        try:
            assert_equal(len(subjects_failed_events), 0,
                         'The following subjects failed event read %s' % (','.join(subjects_failed_events)))
        except StandardError as e:
            print traceback.print_exc()
            num_test_failed += 1


        print 'subjects_failed_events=', subjects_failed_events
        print 'subjects_failed_electrode_info=', subjects_failed_electrode_info
        print 'subject_failed_eeg=', subject_failed_eeg


        assert_equal(num_test_failed, 0, 'Certain read operations failed - see output above')

