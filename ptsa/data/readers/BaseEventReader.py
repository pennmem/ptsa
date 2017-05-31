import sys
import os
from os.path import *
import re
import json
import unicodedata
from collections import defaultdict
import numpy as np

from ptsa.data.common import TypeValTuple, PropertiedObject
from ptsa.data.readers import BaseReader
from ptsa.data.common.path_utils import find_dir_prefix
from ptsa.data.common import pathlib
from ptsa.data.MatlabIO import read_single_matlab_matrix_as_numpy_structured_array
from ptsa import six

class BaseEventReader(PropertiedObject, BaseReader):
    """Reader class that reads event file and returns them as np.recarray"""
    _descriptors = [
        TypeValTuple('filename', six.string_types, ''),
        TypeValTuple('eliminate_events_with_no_eeg', bool, True),
        TypeValTuple('eliminate_nans', bool, True),
        TypeValTuple('use_reref_eeg', bool, False),
        TypeValTuple('normalize_eeg_path', bool, True),
        TypeValTuple('common_root', six.string_types, 'data/events')
    ]

    def __init__(self, **kwds):
        r"""
        Keyword arguments
        -----------------
        filename : str
            path to event file
        eliminate_events_with_no_eeg : bool
            flag to automatically remove events with no eegfile (default True)
        eliminate_nans : bool
            flag to automatically replace nans in the event structs with -999 (default True)
        use_reref_eeg : bool
            flag that changes eegfiles to point reref eegs. Default is False
            and eegs read are nonreref ones
        normalize_eeg_path : bool
            flag that determines if 'data1', 'data2', etc... in eeg path will
            get converted to 'data'. The flag is True by default meaning all
            'data1', 'data2', etc... are converted to 'data'
        common_root : str
            partial path to root events folder e.g. if you events are placed in
            /data/events/RAM_FR1 the path should be 'data/events'. If your
            events are placed in the '/data/scalp_events/catFR' the common root
            should be 'data/scalp_events'. Note that you do not include opening
            '/' in the common_root

        """
        self.init_attrs(kwds)
        self._alter_eeg_path_flag = not self.use_reref_eeg

    @property
    def alter_eeg_path_flag(self):
        return self._alter_eeg_path_flag

    @alter_eeg_path_flag.setter
    def alter_eeg_path_flag(self, val):
        self._alter_eeg_path_flag = val
        self.use_reref_eeg = not self._alter_eeg_path_flag

    def normalize_paths(self, events):
        """
        Replaces data1, data2 etc... in the eegfile column of the events with data
        :param events: np.recarray representing events. One of hte field of this array should be eegfile
        :return: None
        """
        subject = events[0].subject
        if sys.platform.startswith('win'):
            data_dir_bad = r'\\data.*\\' + subject + r'\\eeg'
            data_dir_good = r'\\data\\eeg\\' + subject + r'\\eeg'
        else:
            data_dir_bad = r'/data.*/' + subject + r'/eeg'
            data_dir_good = r'/data/eeg/' + subject + r'/eeg'

        for ev in events:
            # ev.eegfile = ev.eegfile.replace('eeg.reref', 'eeg.noreref')
            ev.eegfile = re.sub(data_dir_bad, data_dir_good, ev.eegfile)
        return events

    def modify_eeg_path(self, events):
        """
        Replaces 'eeg.reref' with 'eeg.noreref' in eegfile path
        :param events: np.recarray representing events. One of hte field of this array should be eegfile
        :return:None
        """

        for ev in events:
            ev.eegfile = ev.eegfile.replace('eeg.reref', 'eeg.noreref')
        return events

    def read(self):
        if os.path.splitext(self.filename)[-1] == '.json':
            return self.read_json()
        else:
            return self.read_matlab()

    def check_reader_settings_for_json_read(self):

        if self.use_reref_eeg:
            raise NotImplementedError('Reref from JSON not implemented')

    def read_json(self):

        self.check_reader_settings_for_json_read()

        evs = self.from_json(self.filename)

        if self.eliminate_events_with_no_eeg:
            # eliminating events that have no eeg file
            indicator = np.empty(len(evs), dtype=bool)
            indicator[:] = False

            for i, ev in enumerate(evs):
                # MAKE THIS CHECK STRONGER
                indicator[i] = (len(str(evs[i].eegfile)) > 3)

            evs = evs[indicator]

        if 'eegfile' in evs.dtype.names:
            eeg_dir = os.path.join(os.path.dirname(self.filename), '..', '..', 'ephys', 'current_processed', 'noreref')
            eeg_dir = os.path.abspath(eeg_dir)
            for ev in evs:
                ev.eegfile = os.path.join(eeg_dir, ev.eegfile)

        return evs

    def read_matlab(self):
        """
        Reads Matlab event file and returns corresponging np.recarray. Path to the eegfile is changed
        w.r.t original Matlab code to account for the following:
        1. /data dir of the database might have been mounted under different mount point e.g. /Users/m/data
        2. use_reref_eeg is set to True in which case we replaces 'eeg.reref' with 'eeg.noreref' in eegfile path

        :return: np.recarray representing events
        """
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
        if self.normalize_eeg_path:
            data_dir_prefix = self.find_data_dir_prefix()
            for i, ev in enumerate(evs):
                ev.eegfile = join(data_dir_prefix, str(pathlib.Path(str(ev.eegfile)).parts[1:]))

            evs = self.normalize_paths(evs)

        # if not self.use_reref_eeg:
        if self._alter_eeg_path_flag:
            evs = self.modify_eeg_path(evs)

        if self.eliminate_nans:
            # this is
            evs = self.replace_nans(evs)

        return evs

    def replace_nans(self, evs, replacement_val=-999):

        for descr in evs.dtype.descr:
            field_name = descr[0]

            try:
                nan_selector = np.isnan(evs[field_name])
                evs[field_name][nan_selector] = replacement_val
            except TypeError:
                pass
        return evs

    def find_data_dir_prefix(self):
        """
        determining dir_prefix

        data on rhino database is mounted as /data
        copying rhino /data structure to another directory will cause all files in data have new prefix
        example:
        self._filename='/Users/m/data/events/R1060M_events.mat'
        prefix is '/Users/m'
        we use find_dir_prefix to determine prefix based on common_root in path with and without prefix

        :return: data directory prefix
        """

        prefix = find_dir_prefix(path_with_prefix=self._filename, common_root=self.common_root)
        if not prefix:
            raise RuntimeError(
                'Could not determine prefix from: %s using common_root: %s' % (self._filename, self.common_root))

        return find_dir_prefix(self._filename, self.common_root)

    ### TODO: CLEAN UP, COMMENT

    @classmethod
    def get_element_dtype(cls, element):
        if isinstance(element, dict):
            return cls.mkdtype(element)
        elif isinstance(element, int):
            return 'int64'
        elif isinstance(element, (str, unicode)):
            return 'S256'
        elif isinstance(element, bool):
            return 'b'
        elif isinstance(element, float):
            return 'float64'
        elif isinstance(element, list):
            return cls.get_element_dtype(element[0])
        else:
            raise Exception('Could not convert type %s' % type(element))

    @classmethod
    def mkdtype(cls, d):
        if isinstance(d, list):
            dtype = cls.mkdtype(d[0])
            return dtype
        dtype = []

        for k, v in list(d.items()):
            dtype.append((str(k), cls.get_element_dtype(v)))

        return np.dtype(dtype)

    @classmethod
    def from_json(cls, json_filename):
        d = json.load(open(json_filename))
        return cls.from_dict(d)

    @classmethod
    def from_dict(cls, d):
        if not isinstance(d, list):
            d = [d]

        list_names = []

        for k, v in list(d[0].items()):
            if isinstance(v, list):
                list_names.append(k)

        list_info = defaultdict(lambda *_: {'len': 0, 'dtype': None})

        for entry in d:
            for k in list_names:
                list_info[k]['len'] = max(list_info[k]['len'], len(entry[k]))
                if not list_info[k]['dtype'] and len(entry[k]) > 0:
                    if isinstance(entry[k][0], dict):
                        list_info[k]['dtype'] = cls.mkdtype(entry[k][0])
                    else:
                        list_info[k]['dtype'] = cls.get_element_dtype(entry[k])

        dtypes = []
        for k, v in list(d[0].items()):
            if not k in list_info:
                dtypes.append((str(k), cls.get_element_dtype(v)))
            else:
                dtypes.append((str(k), list_info[k]['dtype'], list_info[k]['len']))

        if dtypes:
            arr = np.zeros(len(d), dtypes).view(np.recarray)
            cls.copy_values(d, arr, list_info)
        else:
            arr = np.array([])
        return arr.view(np.recarray)

    @classmethod
    def copy_values(cls, dict_list, rec_arr, list_info=None):
        if len(dict_list) == 0:
            return

        dict_fields = {}
        for k, v, in list(dict_list[0].items()):
            if isinstance(v, dict):
                dict_fields[k] = [inner_dict[k] for inner_dict in dict_list]

        for i, sub_dict in enumerate(dict_list):
            for k, v in list(sub_dict.items()):
                if k in dict_fields or list_info and k in list_info:
                    continue

                if isinstance(v, dict):
                    cls.copy_values([v], rec_arr[i][k])
                elif isinstance(v, basestring):
                    rec_arr[i][k] = cls.strip_accents(v)
                else:
                    rec_arr[i][k] = v

        for i, sub_dict in enumerate(dict_list):
            for k, v in list(sub_dict.items()):
                if list_info and k in list_info:
                    arr = np.zeros(list_info[k]['len'], list_info[k]['dtype'])
                    if len(v) > 0:
                        if isinstance(v[0], dict):
                            cls.copy_values(v, arr)
                        else:
                            for j, element in enumerate(v):
                                arr[j] = element

                    rec_arr[i][k] = arr.view(np.recarray)

        for k, v in list(dict_fields.items()):
            cls.copy_values(v, rec_arr[k])

    @classmethod
    def strip_accents(cls, s):
        try:
            return str(''.join(c for c in unicodedata.normalize('NFD', unicode(s))
                               if unicodedata.category(c) != 'Mn'))
        except UnicodeError:  # If accents can't be converted, just remove them
            return str(re.sub(r'[^A-Za-z0-9 -_.]', '', s))
