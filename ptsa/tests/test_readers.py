__author__ = 'm'

from ptsa.data.readers import BaseEventReader
from ptsa.data.readers import PTSAEventReader
from ptsa.data.readers import EEGReader
from ptsa.data.readers import BaseRawReader
from ptsa.data.events import Events
import numpy as np
import unittest
import numpy.testing as npt


class TestReaders(unittest.TestCase):
    def setUp(self):
        self.event_range = range(0, 30, 1)
        self.e_path = '/Users/m/data/events/RAM_FR1/R1060M_events.mat'

        # self.set_verbose(2)
        self.start_time = 0.0
        self.end_time = 1.6
        self.buffer_time = 1.0

    def test_event_read(self):

        ptsa_reader = PTSAEventReader(filename=self.e_path)

        events = ptsa_reader.read()

        base_event_reader = BaseEventReader(filename=self.e_path)

        base_events = base_event_reader.read()

        for base_event, event in zip(base_events, events):
            self.assertEqual(base_event['item'], event['item'])

        for base_event, event in zip(base_events, events):
            self.assertEqual(base_event.eegoffset, event.eegoffset)

    def test_base_raw_reader(self):
        e_path = '/Users/m/data/events/RAM_FR1/R1060M_events.mat'
        base_e_reader = BaseEventReader(filename=e_path, eliminate_events_with_no_eeg=True)
        base_events = base_e_reader.read()
        base_events = base_events[base_events.type == 'WORD']

        dataroot = base_events[0].eegfile

        brr_session = BaseRawReader(dataroot=dataroot, channels=np.array(['002', '003']))
        array_session, read_ok_mask = brr_session.read()

        eeg_reader = EEGReader(events=base_events, channels=np.array(['002', '003']),
                               start_time=self.start_time, end_time=self.end_time, buffer_time=0.0)
        base_eegs = eeg_reader.read()

        for i in xrange(100):
            offset = base_events[i].eegoffset
            npt.assert_array_equal(array_session[:, 0, offset:offset + 100], base_eegs[:, i, :100])

    def test_eeg_read_incomplete_data(self):
        e_path_incomplete = '/Volumes/rhino_root/data/events/RAM_PS/R1104D_events.mat'

        base_event_reader = BaseEventReader(filename=e_path_incomplete)

        base_events = base_event_reader.read()

        sess_1 = base_events[base_events.session == 1]
        sess_3 = base_events[base_events.session == 3]
        sess_5 = base_events[base_events.session == 5]
        sess_7 = base_events[base_events.session == 7]

        sess_1[440].eegoffset = 2000000000000
        sess_1[444].eegoffset = 2000000000000
        sess_1[434].eegoffset = 2000000000000

        shuffled_sess_events = np.hstack((sess_3, sess_7, sess_1, sess_5)).view(np.recarray)

        eeg_reader = EEGReader(events=shuffled_sess_events, channels=np.array(['002', '003']),
                               start_time=self.start_time, end_time=self.end_time, buffer_time=self.buffer_time)
        base_eegs = eeg_reader.read()

        if eeg_reader.removed_bad_data():
            print 'REMOVED BAD DATA !!!!!!!!!!!!!'

        events = base_eegs['events'].data.view(np.recarray)

        if not isinstance(events, Events):
            events = Events(events)

        from ptsa.data.rawbinwrapper import RawBinWrapper
        events = events.add_fields(esrc=np.dtype(RawBinWrapper))

        # ------------- using PTSAevent reader functions to prepare events for reading old-ptsa-style

        ptsa_event_reader = PTSAEventReader()

        ptsa_event_reader.attach_rawbinwrapper_groupped(events)

        eegs = events.get_data(channels=['002', '003'], start_time=self.start_time, end_time=self.end_time,
                               buffer_time=self.buffer_time, eoffset='eegoffset', keep_buffer=True,
                               eoffset_in_time=False, verbose=True)

        npt.assert_array_equal(eegs[:, :, :-1], base_eegs.data)

    def test_R1070T_read(self):
        e_path = '/Volumes/rhino_root/data/events/RAM_FR1/R1070T_events.mat'
        base_event_reader = BaseEventReader(filename=e_path)

        start_time = 0.0
        end_time = 1.366
        buffer_time = 1.365

        base_events = base_event_reader.read()
        eeg_reader = EEGReader(events=base_events, channels=np.array(['042', '043']),
                               start_time=start_time, end_time=end_time, buffer_time=buffer_time)
        base_eegs = eeg_reader.read()

    def test_eeg_read(self):

        ptsa_reader = PTSAEventReader(filename=self.e_path)

        events = ptsa_reader.read()

        # in case fancy indexing looses Eventness of events we need to create Events object explicitely
        if not isinstance(events, Events):
            events = Events(events)

        eegs = events.get_data(channels=['002', '003'], start_time=self.start_time, end_time=self.end_time,
                               buffer_time=self.buffer_time, eoffset='eegoffset', keep_buffer=True,
                               eoffset_in_time=False, verbose=True)

        base_event_reader = BaseEventReader(filename=self.e_path)

        base_events = base_event_reader.read()

        eeg_reader = EEGReader(events=base_events, channels=np.array(['002', '003']),
                               start_time=self.start_time, end_time=self.end_time, buffer_time=self.buffer_time)

        base_eegs = eeg_reader.read()

        npt.assert_array_equal(eegs[:, :, :-1], base_eegs.data)

    @unittest.expectedFailure
    def test_eventness(self):

        events = self.read_ptsa_events()
        ptsa_reader = PTSAEventReader(filename=self.e_path)

        events = ptsa_reader.read()

        self.assertIsInstance(events, Events, "WARNING:Warning Fancy Indexing Causes Events to be recarray")


if __name__ == '__main__':
    # unittest.main(verbosity=2)

    suite = unittest.TestSuite()
    suite.addTest(TestReaders('test_event_read'))
    suite.addTest(TestReaders('test_eventness'))
    suite.addTest(TestReaders('test_eeg_read'))
    unittest.TextTestRunner(verbosity=2).run(suite)
