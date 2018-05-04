import numpy as np
from .base import BaseEventReader
import traits.api
__all__ = [
    'CMLEventReader',
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
    eeg_fname_search_pattern = traits.api.Str
    eeg_fname_replace_pattern = traits.api.Str

    def __init__(self, filename,eeg_fname_search_pattern = '',eeg_fname_replace_pattern='',**kwargs):
        BaseEventReader.__init__(self, filename,**kwargs)
        self.eeg_fname_replace_pattern = eeg_fname_replace_pattern
        self.eeg_fname_search_pattern = eeg_fname_search_pattern

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
