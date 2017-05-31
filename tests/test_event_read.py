import os.path as osp
import unittest

from ptsa.data.events import Events
from ptsa.test.utils import EventReadersTestBase, skip_without_rhino, get_rhino_root


@skip_without_rhino
class TestEventRead(unittest.TestCase, EventReadersTestBase):
    def setUp(self):
        self.event_range = range(0, 30, 1)
        root = get_rhino_root()
        self.e_path = osp.join(root, 'data', 'events', 'RAM_FR1', 'R1060M_events.mat')

    @unittest.expectedFailure
    def test_event_read(self):
        events = self.read_ptsa_events()
        base_events = self.read_base_events()

        for base_event, event in zip(base_events, events):
            self.assertEqual(base_event['item'], event['item'])

        for base_event, event in zip(base_events, events):
            self.assertEqual(base_event.eegoffset, event.eegoffset)

    @unittest.expectedFailure
    def test_eventness(self):
        events = self.read_ptsa_events()
        self.assertIsInstance(
            events, Events,
            "WARNING:Warning Fancy Indexing Causes Events to be recarray")
