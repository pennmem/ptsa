__author__ = 'm'


from ptsa.data.readers import BaseEventReader
from ptsa.data.readers import PTSAEventReader
from ptsa.data.events import Events

import numpy as np
# from numpy.testing import *
import unittest
from unittest import *


class TestEventRead(unittest.TestCase):
    def setUp(self):
        self.event_range = range(0,30,1)
        self.e_path = '/Users/m/data/events/RAM_FR1/R1060M_events.mat'


    def read_ptsa_events(self):

        e_reader = PTSAEventReader(event_file=self.e_path, eliminate_events_with_no_eeg=True)
        e_reader.read()

        events = e_reader.get_output()

        events = events[events.type == 'WORD']

        events = events[self.event_range]

        ev_order = np.argsort(events, order=('session','list','mstime'))
        events = events[ev_order]
        return events


    def read_base_events(self):

        base_e_reader = BaseEventReader(event_file=self.e_path, eliminate_events_with_no_eeg=True, use_ptsa_events_class=False)


        base_e_reader.read()

        base_events = base_e_reader.get_output()

        base_events = base_events[base_events.type == 'WORD']

        base_ev_order = np.argsort(base_events, order=('session','list','mstime'))
        base_events = base_events[base_ev_order]

        base_events = base_events[self.event_range]

        return base_events


    def test_event_read(self):
        # self.initialize()

        events = self.read_ptsa_events()
        base_events = self.read_base_events()


        for base_event, event in zip(base_events,events):
            self.assertEqual(base_event['item'],event['item'])

        for base_event, event in zip(base_events,events):
            self.assertEqual(base_event.eegoffset,event.eegoffset)

    @unittest.expectedFailure
    def test_eventness(self):
        # self.initialize()
        events = self.read_ptsa_events()
        self.assertIsInstance(events,Events,"WARNING:Warning Fancy Indexing Causes Events to be recarray")

        # assert_warns(UserWarning('Warning Fancy Indexing Causes Events to be recarray'), isinstance, events, Events)
        # # if not isinstance(events,Events):
        # #     print 'GOT NON EVENTS'
        # # # assert_raises(RuntimeError, isinstance , events, Events)

if __name__ == '__main__':
    unittest.main(verbosity=2)

