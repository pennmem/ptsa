__author__ = 'm'

from os.path import *
import numpy as np
import re
from ptsa.data.common import TypeValTuple, PropertiedObject
from ptsa.data.readers import BaseReader
from ptsa.data.common.path_utils import find_dir_prefix
from ptsa.data.common import pathlib

class BaseEventReader(PropertiedObject,BaseReader):
    '''
    Reader class that reads event file and returns them as np.recarray
    '''
    _descriptors = [
        TypeValTuple('filename', str, ''),
        TypeValTuple('eliminate_events_with_no_eeg', bool, True),
        TypeValTuple('eliminate_nans', bool, True),
        TypeValTuple('use_reref_eeg', bool, False),
    ]
    def __init__(self,**kwds):
        '''
        Constructor:

        :param kwds:allowed values are:
        -------------------------------------
        :param filename {str} -  path to event file
        :param eliminate_events_with_no_eeg {bool} - flag to automatically remove events with no eegfile (default True)
        :param eliminate_nans {bool} - flag to automatically replace nans in the event structs with -999 (default True)
        :param use_reref_eeg {bool} -  flag that changes eegfiles to point reref eegs. Default is False and eegs read
        are nonreref ones

        :return: None
        '''
        self.init_attrs(kwds)


    def correct_eegfile_field(self, events):
        '''
        Replaces 'eeg.reref' with 'eeg.noreref' in eegfile path
        :param events: np.recarray representing events. One of hte field of this array should be eegfile
        :return:
        '''
        data_dir_bad = r'/data.*/' + events[0].subject + r'/eeg'
        data_dir_good = r'/data/eeg/' + events[0].subject + r'/eeg'
        for ev in events:
            ev.eegfile = ev.eegfile.replace('eeg.reref', 'eeg.noreref')
            ev.eegfile = re.sub(data_dir_bad, data_dir_good, ev.eegfile)
        return events


    def read(self):
        '''
        Reads Matlab event file and returns corresponging np.recarray. Path to the eegfile is changed
        w.r.t original Matlab code to account for the following:
        1. /data dir of the database might have been mounted under different mount point e.g. /Users/m/data
        2. use_reref_eeg is set to True in which case we replaces 'eeg.reref' with 'eeg.noreref' in eegfile path

        :return: np.recarray representing events
        '''
        from ptsa.data.MatlabIO import read_single_matlab_matrix_as_numpy_structured_array

        # extract matlab matrix (called 'events') as numpy structured array
        struct_array = read_single_matlab_matrix_as_numpy_structured_array(self.filename, 'events')

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

        if not self.use_reref_eeg:
            evs = self.correct_eegfile_field(evs)

        if self.eliminate_nans:
            # this is
            evs = self.replace_nans(evs)

        return evs

    def replace_nans(self,evs, replacement_val=-999):

        for descr in evs.dtype.descr:
            field_name = descr[0]

            try:
                nan_selector = np.isnan(evs[field_name])
                evs[field_name][nan_selector]=replacement_val
            except TypeError:
                pass
        return evs

    def find_data_dir_prefix(self):
        '''
        determining dir_prefix

        data on rhino database is mounted as /data
        copying rhino /data structure to another directory will cause all files in data have new prefix
        example:
        self._filename='/Users/m/data/events/R1060M_events.mat'
        prefix is '/Users/m'
        we use find_dir_prefix to determine prefix based on common_root in path with and without prefix

        :return: data directory prefix
        '''

        common_root = 'data/events'
        prefix = find_dir_prefix(path_with_prefix=self._filename, common_root=common_root)
        if not prefix:
            raise RuntimeError(
                'Could not determine prefix from: %s using common_root: %s' % (self._filename, common_root))

        return find_dir_prefix(self._filename, 'data/events')


if __name__ == '__main__':



    from ptsa.data.MatlabIO import *

    # d = deserialize_objects_from_matlab_format('/Volumes/rhino_root/home2/yezzyat/R1108J_1_sess2_rawEEG_chans1_2.mat', 'ye')
    d = deserialize_objects_from_matlab_format('/Volumes/rhino_root/home2/yezzyat/R1060M_FR1_sess0_rawEEG_chans2_3.mat', 'ye')

    print d

    from BaseEventReader import BaseEventReader
    # e_path = join('/Volumes/rhino_root', 'data/events/RAM_FR1/R1060M_math.mat')
    e_path = '/Volumes/rhino_root/data/events/RAM_PS/R1108J_1_events.mat'
    e_path = '/Volumes/rhino_root/data/events/RAM_PS/R1108J_1_events.mat'
    # e_path ='/Users/m/data/events/RAM_FR1/R1056M_events.mat'
    e_path = join('/Volumes/rhino_root', 'data/events/RAM_FR1/R1062J_events.mat')

    e_reader = BaseEventReader(filename=e_path, eliminate_events_with_no_eeg=True)


    events = e_reader.read()

    print

    # from ptsa.data.readers.TalReader import TalReader
    #
    # tal_path = '/Volumes/rhino_root/data/eeg/R1108J_1/tal/R1108J_1_talLocs_database_bipol.mat'
    # tal_reader = TalReader(filename=tal_path)
    # monopolar_channels = tal_reader.get_monopolar_channels()
    # bipolar_pairs = tal_reader.get_bipolar_pairs()
    #
    # # ---------------- NEW STYLE PTSA -------------------
    # base_e_reader = BaseEventReader(filename=e_path, eliminate_events_with_no_eeg=True)
    #
    # base_events = base_e_reader.read()
    #
    # base_events = base_events[(base_events.type == 'STIMULATING') | (base_events.type == 'STIM_SINGLE_PULSE')]
    # base_events = base_events[base_events.session == 2]
    #
    #
    # from ptsa.data.readers.EEGReader import EEGReader
    # eeg_reader = EEGReader(events=base_events, channels=monopolar_channels[0:3],
    #                        start_time=-1.1, end_time=-0.1, buffer_time=1.0)
    #
    # base_eegs = eeg_reader.read()
    #
    # print
    #
    #
