__author__ = 'm'

import sys

sys.path.append('/Users/m/PTSA_NEW_GIT')

import re
from os.path import *
import numpy as np

from ptsa.data.events import Events
from ptsa.data.rawbinwrapper import RawBinWrapper
from ptsa.data.common import pathlib

from BaseEventReader import BaseEventReader
from ptsa.data.common import TypeValTuple
from ptsa.data.common.path_utils import find_dir_prefix


class PTSAEventReader(BaseEventReader):
    def __init__(self, event_file, **kwds):
        BaseEventReader.__init__(self, event_file, **kwds)

        self.attach_rawbinwrapper = True

        try:
            self.attach_rawbinwrapper = bool(kwds['attach_rawbinwrapper'])
        except LookupError:
            pass

    def read(self):

        # calling base class read fcn
        evs = BaseEventReader.read(self)

        # determining data_dir_prefix in case rhino /data filesystem was mounted under different root
        data_dir_prefix = self.find_data_dir_prefix()

        # in case evs is simply recarray
        if not isinstance(evs, Events):
            evs = Events(evs)

        if self.attach_rawbinwrapper:
            evs = evs.add_fields(esrc=np.dtype(RawBinWrapper))

        for ev in evs:
            try:
                # eeg_file_path = join(data_dir_prefix, str(pathlib.Path(str(ev.eegfile)).parts[1:]))

                if self.attach_rawbinwrapper:
                    # ev.esrc = RawBinWrapper(eeg_file_path)
                    ev.esrc = RawBinWrapper(ev.eegfile)

                # self.raw_data_root = str(eeg_file_path)

            except TypeError:
                print 'skipping event with eegfile=', ev.eegfile
                pass

        self._events = evs
        return self._events

        # self.set_output(evs)
        # return self.get_output()

    def find_data_dir_prefix(self):
        # determining dir_prefix
        #
        # data on rhino is mounted as /data
        # copying rhino /data structure to another directory will cause all files in data have new prefix
        # example:
        # self._event_file='/Users/m/data/events/R1060M_events.mat'
        # prefix is '/Users/m'
        # we use find_dir_prefix to determine prefix based on common_root in path with and without prefix
        common_root = 'data/events'
        prefix = find_dir_prefix(path_with_prefix=self._event_file, common_root=common_root)
        if not prefix:
            raise RuntimeError(
                'Could not determine prefix from: %s using common_root: %s' % (self._event_file, common_root))

        return find_dir_prefix(self._event_file, 'data/events')


if __name__ == '__main__':
    from PTSAEventReader import PTSAEventReader
    # e_path = join('/Volumes/rhino_root', 'data/events/RAM_FR1/R1060M_events.mat')
    e_path = '/Users/m/data/events/RAM_FR1/R1060M_events.mat'

    e_reader = PTSAEventReader(event_file=e_path, eliminate_events_with_no_eeg=True)

    events = e_reader.read()

    events = e_reader.get_output()

    print events
