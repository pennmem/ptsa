__author__ = 'm'

import numpy as np
from ptsa.data.events import Events
from ptsa.data.rawbinwrapper import RawBinWrapper
from BaseEventReader import BaseEventReader
from ptsa.data.common import TypeValTuple


class PTSAEventReader(BaseEventReader):
    '''
    Event reader that returns original PTSA Events object with attached rawbinwrappers
    rawbinwrappers are objects that know how to read eeg binary data
    '''

    # _descriptors = BaseEventReader._descriptors+[
    #
    #     TypeValTuple('attach_rawbinwrapper', bool, True),
    #     TypeValTuple('use_groupped_rawbinwrapper', bool, True),
    #
    #     # TypeValTuple('event_file', str, ''),
    #     # TypeValTuple('eliminate_events_with_no_eeg', bool, True),
    #     # TypeValTuple('use_reref_eeg', bool, False),
    # ]

    _descriptors = [

        TypeValTuple('attach_rawbinwrapper', bool, True),
        TypeValTuple('use_groupped_rawbinwrapper', bool, True),

    ]

    def __init__(self, **kwds):
        '''
        Constructor:

        :param kwds:allowed values are:
        -------------------------------------
        :param event_file {str} -  path to event file
        :param eliminate_events_with_no_eeg {bool} - flag to automatically remov events woth no eegfile (default True)
        :param use_reref_eeg {bool} -  flag that changes eegfiles to point reref eegs. Default is False and eegs read
        are nonreref ones
        :param attach_rawbinwrapper {bool} - flag signaling whether to attach rawbinwrappers to Event obj or not.
        Default is True
        :param use_groupped_rawbinwrapper {bool} - flag signaling whether to use groupped rawbinwrappers
        (i.e. shared between many events with same eeglile) or not. Default is True. When True data reads are much faster
        :return: None
        '''
        BaseEventReader.__init__(self, **kwds)


    def read(self):
        '''
        Reads Matlab event file , converts it to np.recarray and attaches rawbinwrappers (if appropriate flags indicate so)
        :return: Events object. depending on flagg settings the rawbinwrappers may be attached as well
        '''

        # calling base class read fcn
        evs = BaseEventReader.read(self)

        # determining data_dir_prefix in case rhino /data filesystem was mounted under different root
        data_dir_prefix = self.find_data_dir_prefix()

        # in case evs is simply recarray
        if not isinstance(evs, Events):
            evs = Events(evs)

        if self.attach_rawbinwrapper:
            evs = evs.add_fields(esrc=np.dtype(RawBinWrapper))

            if self.use_groupped_rawbinwrapper: # this should be default choice - much faster execution
                self.attach_rawbinwrapper_groupped(evs)
            else:    # used for debugging purposes
                self.attach_rawbinwrapper_individual(evs)


        return evs


    def attach_rawbinwrapper_groupped(self,evs):
        '''
        attaches raw bin wrappers to individual records. Single rawbinwrapper is shared between events that have same
        eegfile
        :param evs: Events object
        :return: Events object with attached rawbinarappers
        '''

        eegfiles = np.unique(evs.eegfile)

        for eegfile in eegfiles:

            raw_bin_wrapper = RawBinWrapper(eegfile)
            inds = np.where(evs.eegfile == eegfile)[0]
            for i in inds:
                evs[i]['esrc'] = raw_bin_wrapper


    def attach_rawbinwrapper_individual(self,evs):
        '''
        attaches raw bin wrappers to individual records. Uses separate rawbinwrapper for each record
        :param evs: Events object
        :return: Events object with attached rawbinarappers
        '''

        for ev in evs:
            try:
                if self.attach_rawbinwrapper:
                    ev.esrc = RawBinWrapper(ev.eegfile)
            except TypeError:
                print 'skipping event with eegfile=', ev.eegfile
                pass


if __name__ == '__main__':
    from PTSAEventReader import PTSAEventReader
    # e_path = join('/Volumes/rhino_root', 'data/events/RAM_FR1/R1060M_events.mat')
    e_path = '/Users/m/data/events/RAM_FR1/R1060M_events.mat'

    e_reader = PTSAEventReader(event_file=e_path, eliminate_events_with_no_eeg=True)

    events = e_reader.read()

    events = e_reader.get_output()

    print events


