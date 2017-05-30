from ptsa.data.common import TypeValTuple
from ptsa.data.readers import BaseEventReader
from ptsa import six

class CMLEventReader(BaseEventReader):
    '''
    Event reader that returns original PTSA Events object with attached rawbinwrappers
    rawbinwrappers are objects that know how to read eeg binary data
    '''

    _descriptors = [

        TypeValTuple('eeg_fname_search_pattern', six.string_types, ''),
        TypeValTuple('eeg_fname_replace_pattern', six.string_types, ''),
        TypeValTuple('normalize_eeg_path', bool, False),


    ]

    def __init__(self, **kwds):

        """
        Constructor:

        :param kwds: allowed values are:
        -------------------------------------
        :param filename {str}: path to event file

        :param eliminate_events_with_no_eeg {bool}: flag to automatically remove events with no eegfile (default True)

        :param eliminate_nans {bool}: flag to automatically replace nans in the event structs with -999 (default True)

        :param eeg_fname_search_pattern {str}: pattern in the eeg filename to search for in order to repalce it with
        eeg_fname_replace_pattern

        :param eeg_fname_replace_pattern {str}: replace pattern for eeg filename.
        It will replace all occurrences specified by "eeg_fname_replace_pattern"

        :param normalize_eeg_path {bool}: flag that determines if 'data1', 'data2', etc... in eeg path will get
        converted to 'data'. The flag is False by default meaning all 'data1', 'data2', etc... are converted to 'data'

        :return: None
        """

        BaseEventReader.__init__(self, **kwds)

        if self.eeg_fname_search_pattern != '' and self.eeg_fname_replace_pattern != '':

            self.alter_eeg_path_flag = True

        else:
            self.alter_eeg_path_flag = False

    def modify_eeg_path(self, events):
        """
        Replaces search pattern (self.eeg_fname_search_patter') with replace pattern (self.eeg_fname_replace_pattern)
        in every eegfile entry in the events recarray
        :param events: np.recarray representing events. One of the field of this array should be eegfile
        :return: None
        """

        for ev in events:
            ev.eegfile = ev.eegfile.replace(self.eeg_fname_search_pattern, self.eeg_fname_replace_pattern)
        return events

    def check_reader_settings_for_json_read(self):
        pass


if __name__ == '__main__':
    from os.path import *
    import sys
    prefix = '/Volumes/rhino_root'
    task = 'RAM_FR1'
    subject = 'R1111M'

    e_path = join(prefix, 'data/events/%s/%s_events.mat' % (task, subject))
    ber = BaseEventReader(filename=e_path, eliminate_events_with_no_eeg=True)

    ber_evs = ber.read()

    cml_er = CMLEventReader(filename=e_path,
                            eliminate_events_with_no_eeg=True,
                            eeg_fname_search_pattern='eeg.reref',
                            eeg_fname_replace_pattern='eeg.noreref')

    cml_er_evs = cml_er.read()

    print
