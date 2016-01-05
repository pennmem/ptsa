__author__ = 'm'


from os.path import *
import numpy as np
import re
# from scipy.io import loadmat

from ptsa.data.events import Events





class BaseEventReader(object):
    def __init__(self, event_file, **kwds):
        self.__event_file = event_file
        self.__events = None
        self.eliminate_events_with_no_eeg = True
        self.data_dir_prefix = None
        self.raw_data_root = None
        self.subject_path = None

        self.use_ptsa_events_class = True

        self.use_reref_eeg = False

        possible_argument_list = ['eliminate_events_with_no_eeg', 'data_dir_prefix', 'use_ptsa_events_class','use_reref_eeg']

        for argument in possible_argument_list:

            try:
                setattr(self, argument, kwds[argument])
            except LookupError:
                print 'did not find the argument: ', argument
                pass


    def correct_eegfile_field(self, events):
        events = events[events.eegfile != '[]']  # remove events with no recording
        data_dir_bad = r'/data.*/' + events[0].subject + r'/eeg'
        data_dir_good = r'/data/eeg/' + events[0].subject + r'/eeg'
        for ev in events:
            ev.eegfile = ev.eegfile.replace('eeg.reref', 'eeg.noreref')
            ev.eegfile = re.sub(data_dir_bad, data_dir_good, ev.eegfile)
        return events


    def read(self):
        from MatlabIO import read_single_matlab_matrix_as_numpy_structured_array

        # extract matlab matrix (called 'events') as numpy structured array
        struct_array = read_single_matlab_matrix_as_numpy_structured_array(self.__event_file, 'events')

        evs = Events(struct_array)
        if self.use_ptsa_events_class:
            evs = Events(struct_array)
        else:
            evs = struct_array

        if self.eliminate_events_with_no_eeg:

            # eliminating events that have no eeg file
            indicator = np.empty(len(evs), dtype=bool)
            indicator[:] = False
            for i, ev in enumerate(evs):
                indicator[i] = (type(evs[i].eegfile).__name__.startswith('unicode')) & (len(str(evs[i].eegfile)) > 3)


            evs = evs[indicator]

        if not self.use_reref_eeg:
            evs = self.correct_eegfile_field(evs)


        self.__events = evs



        return self.__events

    def get_subject_path(self):
        return self.subject_path

    def get_raw_data_root(self):
        return self.raw_data_root

    def get_output(self):
        return self.__events

    def set_output(self,evs):
        self.__events = evs



if __name__=='__main__':

        from BaseEventReader import BaseEventReader
        e_path = join('/Volumes/rhino_root', 'data/events/RAM_FR1/R1060M_math.mat')
        # e_path = '/Users/m/data/events/RAM_FR1/R1056M_events.mat'
        e_reader = BaseEventReader(event_file=e_path, eliminate_events_with_no_eeg=True, data_dir_prefix='/Volumes/rhino_root')

        events = e_reader.read()

        events = e_reader.get_output()

