import numpy as np

from ptsa import six
from ptsa.data.common import TypeValTuple
from ptsa.data.events import Events
from ptsa.data.rawbinwrapper import RawBinWrapper
from ptsa.data.readers.base import BaseReader, BaseEventReader

__all__ = [
    'CMLEventReader',
    'PTSAEventReader',
]


class CMLEventReader(BaseEventReader):
    """Event reader that returns original PTSA Events object with attached
    rawbinwrappers -- objects that know how to read eeg binary data

    Keyword arguments
    -----------------
    filename : str
        path to event file
    eliminate_events_with_no_eeg : bool
        flag to automatically remove events with no eegfile (default True)
    eliminate_nans : bool
        flag to automatically replace nans in the event structs with -999
        (default True)
    eeg_fname_search_pattern : str
        pattern in the eeg filename to search for in order to repalce it with
        eeg_fname_replace_pattern
    eeg_fname_replace_pattern : str
        replace pattern for eeg filename. It will replace all occurrences
        specified by "eeg_fname_replace_pattern"
    normalize_eeg_path : bool
        flag that determines if 'data1', 'data2', etc... in eeg path will get
        converted to 'data'. The flag is False by default meaning all 'data1',
        'data2', etc... are converted to 'data'

    """

    _descriptors = [
        TypeValTuple('eeg_fname_search_pattern', six.string_types, ''),
        TypeValTuple('eeg_fname_replace_pattern', six.string_types, ''),
        TypeValTuple('normalize_eeg_path', bool, False),
    ]

    def __init__(self, **kwds):
        BaseEventReader.__init__(self, **kwds)

        if self.eeg_fname_search_pattern != '' and self.eeg_fname_replace_pattern != '':

            self.alter_eeg_path_flag = True

        else:
            self.alter_eeg_path_flag = False

    def modify_eeg_path(self, events):
        """Replaces search pattern (self.eeg_fname_search_patter') with replace
        pattern (self.eeg_fname_replace_pattern) in every eegfile entry in the
        events recarray

        Parameters
        ----------
        events : np.recarray
            representing events. One of the field of this array should be
            eegfile

        """
        for ev in events:
            ev.eegfile = ev.eegfile.replace(self.eeg_fname_search_pattern, self.eeg_fname_replace_pattern)
        return events

    def check_reader_settings_for_json_read(self):
        pass


class PTSAEventReader(BaseEventReader, BaseReader):
    """
    Event reader that returns original PTSA Events object with attached rawbinwrappers
    rawbinwrappers are objects that know how to read eeg binary data
    """

    _descriptors = [

        TypeValTuple('attach_rawbinwrapper', bool, True),
        TypeValTuple('use_groupped_rawbinwrapper', bool, True),

    ]

    def __init__(self, **kwds):
        """
        Keyword arguments
        -----------------
        :param filename {str} -  path to event file
        :param eliminate_events_with_no_eeg {bool} - flag to automatically remov events woth no eegfile (default True)
        :param use_reref_eeg {bool} -  flag that changes eegfiles to point reref eegs. Default is False and eegs read
        are nonreref ones
        :param attach_rawbinwrapper {bool} - flag signaling whether to attach rawbinwrappers to Event obj or not.
        Default is True
        :param use_groupped_rawbinwrapper {bool} - flag signaling whether to use groupped rawbinwrappers
        (i.e. shared between many events with same eeglile) or not. Default is True. When True data reads are much faster
        :return: None

        """
        BaseEventReader.__init__(self, **kwds)

    def read(self):
        """
        Reads Matlab event file , converts it to np.recarray and attaches rawbinwrappers (if appropriate flags indicate so)
        :return: Events object. depending on flagg settings the rawbinwrappers may be attached as well
        """

        # calling base class read fcn
        evs = BaseEventReader.read(self)

        # in case evs is simply recarray
        if not isinstance(evs, Events):
            evs = Events(evs)

        if self.attach_rawbinwrapper:
            evs = evs.add_fields(esrc=np.dtype(RawBinWrapper))

            if self.use_groupped_rawbinwrapper:  # this should be default choice - much faster execution
                self.attach_rawbinwrapper_groupped(evs)
            else:  # used for debugging purposes
                self.attach_rawbinwrapper_individual(evs)

        return evs

    def attach_rawbinwrapper_groupped(self, evs):
        """
        attaches raw bin wrappers to individual records. Single rawbinwrapper is shared between events that have same
        eegfile
        :param evs: Events object
        :return: Events object with attached rawbinarappers
        """

        eegfiles = np.unique(evs.eegfile)

        for eegfile in eegfiles:

            raw_bin_wrapper = RawBinWrapper(eegfile)
            inds = np.where(evs.eegfile == eegfile)[0]
            for i in inds:
                evs[i]['esrc'] = raw_bin_wrapper

    def attach_rawbinwrapper_individual(self, evs):
        """
        attaches raw bin wrappers to individual records. Uses separate rawbinwrapper for each record
        :param evs: Events object
        :return: Events object with attached rawbinarappers
        """

        for ev in evs:
            try:
                if self.attach_rawbinwrapper:
                    ev.esrc = RawBinWrapper(ev.eegfile)
            except TypeError:
                print('skipping event with eegfile=', ev.eegfile)
                pass
