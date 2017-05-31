import os
import os.path as osp
import numpy as np
import pytest

from ptsa.data.readers import BaseEventReader
from ptsa.data.readers import PTSAEventReader


def get_rhino_root():
    """Return where the root directory structure is for data. Works by checking
    some common places and looking for ``/etc/hostname``.

    """
    data_roots = [
        '/',  # rhino
        '/Volumes/rhino',  # where some people mount rhino
        osp.expanduser('~/mnt/rhino'),  # where mvd mounts rhino
    ]

    for root in data_roots:
        hostname_file = osp.join(root, 'etc', 'hostname')
        if osp.exists(osp.join(root, 'etc', 'hostname')):
            try:
                with open(hostname_file, 'r') as f:
                    if f.read().startswith("rhino"):
                        return root
            except:
                continue
    raise OSError("Rhino root not found!")


# Decorator to skip tests that require data on rhino
skip_without_rhino = pytest.mark.skipif("NO_RHINO" in os.environ,
                                        reason="No access to rhino")


class EventReadersTestBase(object):
    """Common base class for event reader tests.

    FIXME: define attributes here

    """
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
