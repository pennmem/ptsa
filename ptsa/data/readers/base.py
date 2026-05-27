"""Base classes for PTSA readers."""

from __future__ import annotations

import sys
import os
from os.path import join
import re
import json
import unicodedata
from collections import defaultdict
import warnings
from abc import abstractmethod
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union, cast

import numpy as np
import pandas as pd
import traits.api
from xarray import DataArray

from ptsa.data.common.path_utils import find_dir_prefix
from ptsa.data.common import pathlib
from ptsa.data.MatlabIO import read_single_matlab_matrix_as_numpy_structured_array
import six

__all__ = [
    'BaseReader',
    'BaseEventReader',
    'BaseRawReader'
]


# Type aliases ---------------------------------------------------------------

PathLike = Union[str, os.PathLike]
JSONDict = Dict[str, Any]
ListInfo = Dict[str, Dict[str, Any]]


class BaseReader(traits.api.HasTraits):
    """Base reader class. Children should implement the :meth:`read` method."""

    @abstractmethod
    def read(self) -> Any:
        raise NotImplementedError


class BaseEventReader(BaseReader):
    """Reader class that reads event file and returns them as np.recarray.

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

    # Trait declarations. At runtime, ``HasTraits`` interprets these as trait
    # descriptors and arranges for each instance to expose the underlying
    # value (``str``, ``bool``, ...) on attribute access. We annotate each
    # name with its *runtime* value type so pyright sees ``self.filename`` as
    # ``str`` (etc.) rather than ``type[traits.api.Str]``; the per-line
    # ``reportAssignmentType`` ignore covers the descriptor/value-type
    # mismatch on these declarative lines.
    filename: str = traits.api.Str  # pyright: ignore[reportAssignmentType]
    eliminate_events_with_no_eeg: bool = traits.api.Bool  # pyright: ignore[reportAssignmentType]
    eliminate_nans: bool = traits.api.Bool  # pyright: ignore[reportAssignmentType]
    _alter_eeg_path_flag: bool = traits.api.Bool  # pyright: ignore[reportAssignmentType]
    normalize_eeg_path: bool = traits.api.Bool  # pyright: ignore[reportAssignmentType]
    common_root: str = traits.api.Str  # pyright: ignore[reportAssignmentType]
    use_reref_eeg: bool = False

    def __init__(
        self,
        filename: PathLike,
        common_root: str = 'data/events',
        eliminate_events_with_no_eeg: bool = True,
        eliminate_nans: bool = True,
        use_reref_eeg: bool = False,
        normalize_eeg_path: bool = True,
    ) -> None:
        warnings.warn("Lab-specific readers may be moved to the cmlreaders "
                      "package (https://github.com/pennmem/cmlreaders)",
                      FutureWarning)
        super().__init__()
        self.filename = os.fspath(filename)
        self.common_root = common_root
        self.eliminate_events_with_no_eeg = eliminate_events_with_no_eeg
        self.eliminate_nans = eliminate_nans
        self.use_reref_eeg = use_reref_eeg
        self.normalize_eeg_path = normalize_eeg_path
        self._alter_eeg_path_flag = not self.use_reref_eeg

    @property
    def alter_eeg_path_flag(self) -> bool:
        return self._alter_eeg_path_flag

    @alter_eeg_path_flag.setter
    def alter_eeg_path_flag(self, val: bool) -> None:
        self._alter_eeg_path_flag = val
        self.use_reref_eeg = not self._alter_eeg_path_flag

    def normalize_paths(self, events: np.recarray) -> np.recarray:
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

    def modify_eeg_path(self, events: np.recarray) -> np.recarray:
        """
        Replaces 'eeg.reref' with 'eeg.noreref' in eegfile path
        :param events: np.recarray representing events. One of hte field of this array should be eegfile
        :return:None
        """

        for ev in events:
            ev.eegfile = ev.eegfile.replace('eeg.reref', 'eeg.noreref')
        return events

    def read(self) -> np.recarray:
        if os.path.splitext(self.filename)[-1] == '.json':
            return self.read_json()
        else:
            return self.read_matlab()

    def as_dataframe(self) -> pd.DataFrame:
        """Read events and return as a :class:`pd.DataFrame`.

        .. warning::

            This drops the ``stim_params`` field presently as it is not scalar
            in the current event structure scheme and causes issues when trying
            to convert to a :class:`pd.DataFrame`.

        """
        events = self.read()
        fields = events.dtype.fields
        # ``np.dtype.fields`` is ``None`` for unstructured arrays; events
        # produced by readers are always structured so this should not trip
        # in practice, but guard against it for type-narrowing's sake.
        if fields is not None and 'stim_params' in fields:
            exclude: Optional[List[str]] = ['stim_params']
        else:
            exclude = None
        return pd.DataFrame.from_records(events, exclude=exclude)

    def check_reader_settings_for_json_read(self) -> None:

        if self.use_reref_eeg:
            raise NotImplementedError('Reref from JSON not implemented')

    def read_json(self) -> np.recarray:

        self.check_reader_settings_for_json_read()

        evs = self.from_json(self.filename)

        if self.eliminate_events_with_no_eeg:
            # eliminating events that have no eeg file
            indicator = np.empty(len(evs), dtype=bool)
            indicator[:] = False

            for i, ev in enumerate(evs):
                # MAKE THIS CHECK STRONGER
                indicator[i] = (len(str(evs[i].eegfile)) > 3)

            # Boolean-mask slicing a recarray returns a recarray at
            # runtime, but pyright widens to ``ndarray | recarray``.
            evs = evs[indicator].view(np.recarray)

        names = evs.dtype.names
        if names is not None and 'eegfile' in names:
            eeg_dir = os.path.join(os.path.dirname(self.filename), '..', '..', 'ephys', 'current_processed', 'noreref')
            eeg_dir = os.path.abspath(eeg_dir)
            for ev in evs:
                ev.eegfile = os.path.join(eeg_dir, ev.eegfile)

        return evs

    def read_matlab(self) -> np.recarray:
        """
        Reads Matlab event file and returns corresponging np.recarray. Path to the eegfile is changed
        w.r.t original Matlab code to account for the following:
        1. /data dir of the database might have been mounted under different mount point e.g. /Users/m/data
        2. use_reref_eeg is set to True in which case we replaces 'eeg.reref' with 'eeg.noreref' in eegfile path

        :return: np.recarray representing events
        """
        # extract matlab matrix (called 'events') as numpy structured array.
        # ``read_single_matlab_matrix_as_numpy_structured_array`` is
        # untyped; cast its result to recarray to match the documented
        # contract (the function constructs the array as ``np.recarray``).
        evs: np.recarray = cast(
            np.recarray,
            read_single_matlab_matrix_as_numpy_structured_array(self.filename, 'events'),
        )

        names = evs.dtype.names
        if names is not None and 'eegfile' in names:
            if self.eliminate_events_with_no_eeg:

                # eliminating events that have no eeg file
                indicator = np.empty(len(evs), dtype=bool)
                indicator[:] = False

                for i, ev in enumerate(evs):
                    # MAKE THIS CHECK STRONGER
                    indicator[i] = (len(str(evs[i].eegfile)) > 3)
                    # indicator[i] = (type(evs[i].eegfile).__name__.startswith('unicode')) & (len(str(evs[i].eegfile)) > 3)

                evs = evs[indicator].view(np.recarray)

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

    def replace_nans(self, evs: np.recarray, replacement_val: float = -999) -> np.recarray:

        for descr in evs.dtype.descr:
            field_name = descr[0]

            try:
                nan_selector = np.isnan(evs[field_name])
                evs[field_name][nan_selector] = replacement_val
            except TypeError:
                pass
        return evs

    def find_data_dir_prefix(self) -> str:
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

        prefix = find_dir_prefix(path_with_prefix=self.filename, common_root=self.common_root)
        if not prefix:
            raise RuntimeError(
                'Could not determine prefix from: %s using common_root: %s' % (self.filename, self.common_root))

        return prefix

    ### TODO: CLEAN UP, COMMENT

    @classmethod
    def get_element_dtype(cls, element: Any) -> Any:
        if isinstance(element, dict):
            return cls.mkdtype(element)
        elif isinstance(element, int):
            return 'int64'
        elif isinstance(element, six.binary_type):
            return 'S256'
        elif isinstance(element, six.text_type):
            return 'U256'
        elif isinstance(element, bool):
            return 'b'
        elif isinstance(element, float):
            return 'float64'
        elif isinstance(element, list):
            return cls.get_element_dtype(element[0])
        else:
            raise Exception('Could not convert type %s' % type(element))

    @classmethod
    def mkdtype(cls, d: Union[JSONDict, List[Any]]) -> np.dtype:
        if isinstance(d, list):
            dtype = cls.mkdtype(d[0])
            return dtype
        dtype_fields: List[Tuple[str, Any]] = []

        for k, v in list(d.items()):
            dtype_fields.append((str(k), cls.get_element_dtype(v)))

        return np.dtype(dtype_fields)

    @classmethod
    def from_json(cls, json_filename: PathLike) -> np.recarray:
        with open(json_filename, "r") as f:
            d = json.load(f)
        return cls.from_dict(d)

    @classmethod
    def from_dict(cls, d: Union[JSONDict, List[JSONDict]]) -> np.recarray:
        if not isinstance(d, list):
            d = [d]

        list_names: List[str] = []

        for k, v in list(d[0].items()):
            if isinstance(v, list):
                list_names.append(k)

        # The ``lambda *_: ...`` default factory matches the pre-existing
        # behavior. Each value is a dict with keys ``'len'`` (int) and
        # ``'dtype'`` (numpy dtype or None).
        list_info: ListInfo = defaultdict(lambda *_: {'len': 0, 'dtype': None})

        for entry in d:
            for k in list_names:
                # ``list_info[k]['len']`` starts at 0 (int); ``len(entry[k])``
                # is also int, so ``max`` is well-typed even though the dict
                # value type is ``Any``.
                list_info[k]['len'] = max(int(list_info[k]['len']), len(entry[k]))
                if not list_info[k]['dtype'] and len(entry[k]) > 0:
                    if isinstance(entry[k][0], dict):
                        list_info[k]['dtype'] = cls.mkdtype(entry[k][0])
                    else:
                        list_info[k]['dtype'] = cls.get_element_dtype(entry[k])

        dtypes: List[Tuple[Any, ...]] = []
        for k, v in list(d[0].items()):
            if not k in list_info:
                dtypes.append((str(k), cls.get_element_dtype(v)))
            else:
                dtypes.append((str(k), list_info[k]['dtype'], list_info[k]['len']))

        arr: np.ndarray
        if dtypes:
            arr = np.rec.array(np.zeros(len(d), dtypes))
            cls.copy_values(d, arr, list_info)
        else:
            arr = np.array([])
        return np.rec.array(arr)

    @classmethod
    def copy_values(
        cls,
        dict_list: Sequence[JSONDict],
        rec_arr: np.ndarray,
        list_info: Optional[ListInfo] = None,
    ) -> None:
        if len(dict_list) == 0:
            return

        dict_fields: Dict[str, List[Any]] = {}
        for k, v, in list(dict_list[0].items()):
            if isinstance(v, dict):
                dict_fields[k] = [inner_dict[k] for inner_dict in dict_list]

        for i, sub_dict in enumerate(dict_list):
            for k, v in list(sub_dict.items()):
                if k in dict_fields or list_info and k in list_info:
                    continue

                if isinstance(v, dict):
                    cls.copy_values([v], rec_arr[i][k])
                elif isinstance(v, six.string_types):
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

                    rec_arr[i][k] = np.rec.array(arr)

        for k, v in list(dict_fields.items()):
            cls.copy_values(v, rec_arr[k])

    @classmethod
    def strip_accents(cls, s: str) -> str:
        try:
            return str(''.join(c for c in unicodedata.normalize('NFD', six.text_type(s))
                               if unicodedata.category(c) != 'Mn'))
        except UnicodeError:  # If accents can't be converted, just remove them
            return str(re.sub(r'[^A-Za-z0-9 -_.]', '', s))


class BaseRawReader(BaseReader):
    """
    Abstract base class for objects that know how to read binary EEG files.
    Classes inheriting from BaseRawReader should do the following
    * Override :meth:read_file
    * Set self.params_dict['gain'] and self.params_dict['samplerate'] as appropriate,
      either in self.read_file or in the constructor
    * Make sure that self.channel_name as appropriate for the referencing scheme used
    """

    # See note in ``BaseEventReader`` about why each trait is annotated with
    # its runtime value type and tagged with a per-line ignore.
    dataroot: str = traits.api.Str  # pyright: ignore[reportAssignmentType]
    channels: np.ndarray = traits.api.CArray  # pyright: ignore[reportAssignmentType]
    channel_labels: np.ndarray = traits.api.CArray  # pyright: ignore[reportAssignmentType]
    start_offsets: np.ndarray = traits.api.CArray  # pyright: ignore[reportAssignmentType]
    read_size: int = traits.api.Int  # pyright: ignore[reportAssignmentType]

    channel_name: str = 'channels'

    def __init__(
        self,
        dataroot: PathLike,
        channels: Any = tuple(),
        start_offsets: Any = (0,),
        read_size: int = -1,
    ) -> None:
        """
        Constructor
        :param dataroot {str} -  core name of the eegfile file (i.e. full path except extension e.g. '.002').
        Normally this is eegfile field from events record

        :param channels {array-like} - array of channels (array of strings) that should be read
        :param start_offsets {array-like} -  array of ints with read offsets
        :param read_size {int} - size of the read chunk. If -1 the entire file is read
        :return:None

        """
        super().__init__()
        self.dataroot = os.fspath(dataroot)
        # ``traits.api.CArray`` coerces sequences to ndarrays at runtime;
        # ``np.asarray`` here is a no-op for arrays but ensures the static
        # type is ``np.ndarray`` for the rest of this method.
        self.channels = np.asarray(channels)
        self.start_offsets = np.asarray(start_offsets)
        self.read_size = read_size
        self.params_dict: Dict[str, Any] = self.init_params()
        if self.channels.dtype.names is None:
            self.channel_labels = self.channels
        else:
            self.channel_labels = self.channels['channel']


    def init_params(self) -> Dict[str, Any]:
        from ptsa.data.readers.params import ParamsReader
        p_reader = ParamsReader(dataroot=self.dataroot)
        return p_reader.read()

    def channel_labels_to_string(self) -> None:
        if np.issubdtype(self.channel_labels.dtype, np.integer):
            self.channel_labels = np.array(['{:03}'.format(c).encode() for c in self.channel_labels])


    def read(self) -> Tuple[DataArray, np.ndarray]:
        """Read EEG data.

        Returns
        -------
        event_data : DataArray
            Populated with data read from eeg files. The size of the output is
            number of channels * number of start offsets * number of time series
            points. The corresponding DataArray axes are: 'channels',
            'start_offsets', 'offsets'
        read_ok_mask : np.ndarray
            Mask of chunks that were properly read.

        Notes
        -----
        This method should *not* be overridden by subclasses. Instead, override
        the :meth:`read_file` method to implement new file types (see for
        example the HDF5 reader).

        """

        eventdata, read_ok_mask = self.read_file(self.dataroot,
                                                 self.channel_labels,
                                                 self.start_offsets,
                                                 self.read_size)
        # multiply by the gain
        eventdata *= self.params_dict['gain']

        eventdata = DataArray(eventdata,
                              dims=[self.channel_name, 'start_offsets', 'offsets'],
                              coords={
                                  self.channel_name: self.channels,
                                  'start_offsets': self.start_offsets.copy(),
                                  'offsets': np.arange(self.read_size),
                                  'samplerate': self.params_dict['samplerate']
                              }
                              )

        from copy import deepcopy
        eventdata.attrs = deepcopy(self.params_dict)

        return eventdata, read_ok_mask

    @abstractmethod
    def read_file(
        self,
        filename: PathLike,
        channels: np.ndarray,
        start_offsets: np.ndarray = np.array([0]),
        read_size: int = -1,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Reads raw data from binary files into a numpy array of shape (len(channels),len(start_offsets), read_size).
         For each channel and offset, indicates whether the data at that offset on that channel could be read successfully.

         For each channel and offset, indicates whether the data at that offset
         on that channel could be read successfully.

         Parameters
         ----------
         filename : str
            The name of the file to read
        channels : list
            The channels to read from the file
        start_offsets : np.ndarray
            The indices in the array to start reading at
        read_size : int
            The number of samples to read at each offset.

        Returns
        -------
        eventdata : np.ndarray
            The EEG data corresponding to each offset
        read_ok_mask : np.ndarray
            Boolean mask indicating whether each offset was read successfully.

        """
        raise NotImplementedError
