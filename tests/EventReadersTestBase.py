__author__ = 'm'


from ptsa.data.readers import BaseEventReader
from ptsa.data.readers import PTSAEventReader
from ptsa.data.events import Events

import numpy as np


class EventReadersTestBase(object):

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




