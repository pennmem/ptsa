__author__ = 'm'

import sys
sys.path.append('/Users/m/PTSA_NEW_GIT')


import re
from os.path import *
import numpy as np
# from scipy.io import loadmat



from ptsa.data.events import Events
from ptsa.data.rawbinwrapper import RawBinWrapper
from ptsa.data.common import pathlib


from BaseEventReader import BaseEventReader
from ptsa.data.common import TypeValTuple


class PTSAEventReader(BaseEventReader):

    _descriptors = [TypeValTuple('samplerate_10', float, 30)]


    def __init__(self, event_file, **kwds):
        BaseEventReader.__init__(self,event_file, **kwds)

        self.use_reref_eeg = False
        try:
            self.use_reref_eeg = bool(kwds['use_reref_eeg'])
        except LookupError:
            pass

        self.attach_rawbinwrapper = True
        try:
            self.attach_rawbinwrapper = bool(kwds['attach_rawbinwrapper'])
        except LookupError:
            pass

    def read(self):

        # calling base class read fcn
        evs = BaseEventReader.read(self)

        # this replaces references to reref eef with references to noreref eeg in the file path stored in the eegfile field
        # if not self.use_reref_eeg:
        #     evs = self.correct_eegfile_field(evs) ################## RESTORE THIS

        # in case evs is simply recarray
        if not isinstance(evs,Events):
            evs = Events(evs)

        if self.attach_rawbinwrapper:
            evs = evs.add_fields(esrc=np.dtype(RawBinWrapper))


        for ev in evs:
            try:
                eeg_file_path = join(self.data_dir_prefix, str(pathlib.Path(str(ev.eegfile)).parts[1:]))

                if self.attach_rawbinwrapper:
                    ev.esrc = RawBinWrapper(eeg_file_path)
                self.raw_data_root=str(eeg_file_path)

            except TypeError:
                print 'skipping event with eegfile=',ev.eegfile
                pass


        self._events = evs
        return self._events

        # self.set_output(evs)
        # return self.get_output()


if __name__=='__main__':

        from PTSAEventReader import PTSAEventReader
        # e_path = join('/Volumes/rhino_root', 'data/events/RAM_FR1/R1060M_events.mat')
        e_path = '/Users/m/data/events/RAM_FR1/R1060M_events.mat'

        e_reader = PTSAEventReader(event_file=e_path, eliminate_events_with_no_eeg=True, data_dir_prefix='/Users/m/')

        events = e_reader.read()

        events = e_reader.get_output()

        print events