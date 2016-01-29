__author__ = 'm'

from os.path import *
import numpy as np
import re

from ptsa.data.events import Events

from ptsa.data.common import TypeValTuple, PropertiedObject
from ptsa.data.common.path_utils import find_dir_prefix
from ptsa.data.common import pathlib

class BaseEventReader(PropertiedObject):
    '''
    Reader class that reads event file and returns them as np.recarray
    '''
    _descriptors = [
        TypeValTuple('event_file', str, ''),
        TypeValTuple('eliminate_events_with_no_eeg', bool, True),
        TypeValTuple('use_ptsa_events_class', bool, False),
        TypeValTuple('use_reref_eeg', bool, False),
    ]
    def __init__(self,**kwds):
        '''
        Constructor:

        :param kwds:allowed values are:
        -------------------------------------
        :param event_file {str} -  path to event file
        :param eliminate_events_with_no_eeg {bool} - flag to automatically remov events woth no eegfile (default True)
        :param use_reref_eeg {bool} -  flag that changes eegfiles to point reref eegs. Default is False and eegs read
        are nonreref ones
        :return: None
        '''
        self.init_attrs(kwds)


    # def __init__(self, event_file, **kwds):
    #     self._event_file = event_file
    #     self._events = None
    #
    #     possible_argument_list = ['eliminate_events_with_no_eeg', 'use_ptsa_events_class',
    #                               'use_reref_eeg']
    #
    #     for argument in possible_argument_list:
    #         try:
    #             accessor = getattr(self, argument)
    #             accessor = argument
    #         except AttributeError:
    #             sys.exit()
    #             pass
    #         # try:
    #         #     setattr(self, argument, kwds[argument])
    #         # except LookupError:
    #         #     print 'did not find the argument: ', argument
    #         #     pass
    #
    def correct_eegfile_field(self, events):
        data_dir_bad = r'/data.*/' + events[0].subject + r'/eeg'
        data_dir_good = r'/data/eeg/' + events[0].subject + r'/eeg'
        for ev in events:
            ev.eegfile = ev.eegfile.replace('eeg.reref', 'eeg.noreref')
            ev.eegfile = re.sub(data_dir_bad, data_dir_good, ev.eegfile)
        return events


    def read(self):
        from ptsa.data.MatlabIO import read_single_matlab_matrix_as_numpy_structured_array

        # extract matlab matrix (called 'events') as numpy structured array
        struct_array = read_single_matlab_matrix_as_numpy_structured_array(self._event_file, 'events')

        evs = struct_array

        if self.eliminate_events_with_no_eeg:

            # eliminating events that have no eeg file
            indicator = np.empty(len(evs), dtype=bool)
            indicator[:] = False

            for i, ev in enumerate(evs):
                # MAKE THIS CHECK STRONGER
                indicator[i] = (len(str(evs[i].eegfile)) > 3)
                # indicator[i] = (type(evs[i].eegfile).__name__.startswith('unicode')) & (len(str(evs[i].eegfile)) > 3)

            evs = evs[indicator]

        # determining data_dir_prefix in case rhino /data filesystem was mounted under different root
        data_dir_prefix = self.find_data_dir_prefix()
        for i, ev in enumerate(evs):
            ev.eegfile=join(data_dir_prefix, str(pathlib.Path(str(ev.eegfile)).parts[1:]))


        # NEW CODE
        if self.use_ptsa_events_class:
            evs = Events(evs)

        if not self.use_reref_eeg:
            evs = self.correct_eegfile_field(evs)

        return evs


    def find_data_dir_prefix(self):
        '''
        determining dir_prefix

        data on rhino database is mounted as /data
        copying rhino /data structure to another directory will cause all files in data have new prefix
        example:
        self._event_file='/Users/m/data/events/R1060M_events.mat'
        prefix is '/Users/m'
        we use find_dir_prefix to determine prefix based on common_root in path with and without prefix

        :return: data directory prefix
        '''

        common_root = 'data/events'
        prefix = find_dir_prefix(path_with_prefix=self._event_file, common_root=common_root)
        if not prefix:
            raise RuntimeError(
                'Could not determine prefix from: %s using common_root: %s' % (self._event_file, common_root))

        return find_dir_prefix(self._event_file, 'data/events')


if __name__ == '__main__':
    from BaseEventReader import BaseEventReader
    # e_path = join('/Volumes/rhino_root', 'data/events/RAM_FR1/R1060M_math.mat')
    e_path = '/Users/m/data/events/RAM_PS/R1108J_1_events.mat'

    # e_path ='/Users/m/data/events/RAM_FR1/R1056M_events.mat'

    e_reader = BaseEventReader(event_file=e_path, eliminate_events_with_no_eeg=True)


    events = e_reader.read()

    events = e_reader.get_output()

    print events
