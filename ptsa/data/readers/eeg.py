from collections import defaultdict
import os.path
import warnings
from typing import Callable, DefaultDict, List, Optional, Tuple, Type

import numpy as np
import numpy.typing as npt
import xarray as xr

import traits.api
from ptsa.data.readers.edf import EDFRawReader
from ptsa.data.readers.binary import BinaryRawReader
from ptsa.data.readers.hdf5 import H5RawReader
from ptsa.data.readers.base import BaseRawReader
from ptsa.data.timeseries import TimeSeries

__all__ = [
    'EEGReader',
]


# FIXME: centralize PTSA exception classes
class IncompatibleDataError(Exception):
    pass


class EEGReader(traits.api.HasTraits):
    """
    Reader that knows how to read binary eeg files. It can read chunks of the eeg signal based on events input
    or can read entire session if session_dataroot is non empty.

    Keyword Arguments
    -----------------
    channels : np.ndarray
        numpy array of channel labels, or a structured array with a 'channels' field
    start_time : float
        read start offset in seconds w.r.t to the eegeffset specified in the events recarray
    end_time:
        read end offset in seconds w.r.t to the eegeffset specified in the
        events recarray
    buffer_time : float
        extra buffer in seconds (subtracted from start read and added to end
        read)
    events : np.recarray
        numpy recarray representing Events
    session_dataroot : str
        path to session dataroot. When set the reader will read the entire
        session
    remove_bad_events : bool
        Remove "bad" events. Defaults to True.

    Notes
    -----
    An EEGReader must be constructed using either :py:arg:events or :py:arg:session_dataroot.
    """

    # Class-level trait declarations (descriptors on HasTraits). Pyright
    # cannot model the trait descriptor → runtime-type conversion, so the
    # instance-level types are pinned in ``__init__`` below and the trait
    # types are reported to pyright as their runtime-coerced types.
    channels: npt.NDArray = traits.api.CArray  # pyright: ignore[reportAssignmentType]
    start_time: float = traits.api.CFloat  # pyright: ignore[reportAssignmentType]
    end_time: float = traits.api.CFloat  # pyright: ignore[reportAssignmentType]
    buffer_time: float = traits.api.CFloat  # pyright: ignore[reportAssignmentType]
    session_dataroot: str = traits.api.Str  # pyright: ignore[reportAssignmentType]
    remove_bad_events: bool = traits.api.Bool  # pyright: ignore[reportAssignmentType]

    READER_FILETYPE_DICT: DefaultDict[str, Type[BaseRawReader]] = defaultdict(
        lambda: BinaryRawReader
    )
    READER_FILETYPE_DICT.update({'.h5': H5RawReader,
                                 '.bdf': EDFRawReader,
                                 '.edf': EDFRawReader})

    def __init__(self,
                 events: Optional[np.recarray] = None,
                 channels: npt.NDArray = np.array([], dtype='|S3'),
                 start_time: float = 0.0,
                 end_time: float = 0.0,
                 buffer_time: float = 0.0,
                 session_dataroot: str = '',
                 remove_bad_events: bool = True) -> None:
        warnings.warn("Lab-specific readers may be moved to the cmlreaders "
                      "package (https://github.com/pennmem/cmlreaders)",
                      FutureWarning)
        self.events: Optional[np.recarray] = events
        self.channels = channels
        self.start_time = float(start_time)
        self.end_time = float(end_time)
        self.buffer_time = float(buffer_time)
        self.session_dataroot = session_dataroot
        self.remove_bad_events = remove_bad_events
        self.removed_corrupt_events: bool = False
        self.event_ok_mask_sorted: Optional[npt.NDArray] = None

        assert self.start_time <= self.end_time, \
            'start_time (%s) must be less or equal to end_time(%s) ' % (self.start_time, self.end_time)
        assert self.events is not None or self.session_dataroot, 'Either events or session_dataroot must be present'

        self.read_fcn: Callable[[], TimeSeries] = self.read_events_data
        if self.session_dataroot:
            self.read_fcn = self.read_session_data
        self.channel_name: str = 'channels'

    def compute_read_offsets(self, reader: BaseRawReader) -> Tuple[int, int, int]:
        """
        Reads Parameter file and exracts sampling rate that is used to convert from start_time, end_time, buffer_time
        (expressed in seconds)
        to start_offset, end_offset, buffer_offset expressed as integers indicating number of time series data points (not bytes!)

        :param dataroot: core name of the eeg datafile
        :return: tuple of 3 {int} - start_offset, end_offset, buffer_offset
        """

        samplerate = reader.params_dict['samplerate']

        start_offset = int(np.round(self.start_time * samplerate))
        end_offset = int(np.round(self.end_time * samplerate))
        buffer_offset = int(np.round(self .buffer_time * samplerate))

        return start_offset, end_offset, buffer_offset

    def __create_base_raw_readers(self) -> Tuple[List[BaseRawReader], List[str]]:
        """
        Creates BaseRawreader for each (unique) dataroot present in events recarray
        :return: list of BaseRawReaders and list of dataroots
        :raises: :py:class:IncompatibleDataError if the readers are not all the same class
        """
        assert self.events is not None, 'events must be set to read events data'
        evs = self.events
        dataroots = np.unique(evs.eegfile)
        raw_readers = []
        original_dataroots = []

        for dataroot in dataroots:
            RawReader = self.READER_FILETYPE_DICT[os.path.splitext(dataroot)[-1]]
            brr = RawReader(dataroot =dataroot)

            # np.recarray subscripted with a boolean mask returns a recarray at
            # runtime, but numpy's stubs declare the return as ndarray.
            events_with_matched_dataroot: np.recarray = evs[evs.eegfile == dataroot]  # pyright: ignore[reportAssignmentType]

            start_offset, end_offset, buffer_offset = self.compute_read_offsets(brr)

            read_size = end_offset - start_offset + 2 * buffer_offset

            start_offsets = events_with_matched_dataroot.eegoffset + start_offset - buffer_offset

            brr = RawReader(dataroot=dataroot,
                            channels=self.channels,
                            start_offsets=start_offsets,
                            read_size=read_size)
            raw_readers.append(brr)

            original_dataroots.append(dataroot)

        return raw_readers, original_dataroots

    def read_session_data(self) -> TimeSeries:
        """
        Reads entire session worth of data

        :return: TimeSeries object (channels x events x time) with data for entire session the events dimension has length 1
        """
        brr = self.READER_FILETYPE_DICT[os.path.splitext(self.session_dataroot)[-1]](dataroot=self.session_dataroot, channels=self.channels)
        session_array, _read_ok_mask = brr.read()
        self.channel_name = brr.channel_name

        offsets_axis = session_array['offsets']
        number_of_time_points = offsets_axis.shape[0]
        samplerate = float(session_array['samplerate'])
        physical_time_array = np.arange(number_of_time_points) * (1.0 / samplerate)

        session_time_series = TimeSeries(session_array.values,
                                         dims=[self.channel_name, 'start_offsets', 'time'],
                                         coords={
                                              self.channel_name: session_array[self.channel_name],
                                              'start_offsets': session_array['start_offsets'],
                                              'time': physical_time_array,
                                              # modern xarray rejects building a coord variable
                                              # from a DataArray; pass the raw .data instead.
                                              'offsets': ('time', session_array['offsets'].data),
                                              'samplerate': session_array['samplerate']
                                          }
                                         )
        session_time_series.attrs = session_array.attrs.copy()
        session_time_series.attrs['dataroot'] = self.session_dataroot

        return session_time_series

    def removed_bad_data(self) -> bool:
        return self.removed_corrupt_events

    def get_event_ok_mask(self) -> Optional[npt.NDArray]:
        return self.event_ok_mask_sorted

    def read_events_data(self) -> TimeSeries:
        """
        Reads eeg data for individual event

        :return: TimeSeries  object (channels x events x time) with data for individual events
        """
        self.event_ok_mask_sorted = None  # reset self.event_ok_mask_sorted

        assert self.events is not None, 'events must be set to read events data'
        evs = self.events

        raw_readers, original_dataroots = self.__create_base_raw_readers()

        # used for restoring original order of the events
        ordered_indices = np.arange(len(evs))
        event_indices_list: List[npt.NDArray] = []
        events: List[npt.NDArray] = []

        ts_array_list: List[xr.DataArray] = []

        event_ok_mask_list: List[npt.NDArray] = []

        for raw_reader, dataroot in zip(raw_readers, original_dataroots):

            ts_array, read_ok_mask = raw_reader.read()

            event_ok_mask_list.append(np.all(read_ok_mask,axis=0))

            ind = np.atleast_1d(evs.eegfile == dataroot)
            event_indices_list.append(ordered_indices[ind])
            events.append(evs[ind])

            ts_array_list.append(ts_array)

        if not all([r.channel_name==raw_readers[0].channel_name for r in raw_readers]):
            raise IncompatibleDataError('cannot read monopolar and bipolar data together')

        self.channel_name = raw_readers[0].channel_name

        event_indices_array = np.hstack(event_indices_list)
        event_indices_restore_sort_order_array = event_indices_array.argsort()

        eventdata = xr.concat(ts_array_list, dim='start_offsets')
        samplerate = float(eventdata['samplerate'])
        tdim = np.arange(eventdata.shape[-1]) * (1.0 / samplerate) + (self.start_time - self.buffer_time)
        cdim = eventdata[self.channel_name]
        edim = np.rec.array(np.concatenate(events))

        attrs = eventdata.attrs.copy()
        eventdata = TimeSeries(eventdata.data,
                               dims=[self.channel_name, 'events', 'time'],
                               coords={self.channel_name: cdim,
                                        'events': edim,
                                        'time': tdim,
                                        'samplerate': samplerate
                                        }
                               )

        eventdata.attrs = attrs

        # restoring original order of the events
        eventdata = eventdata[:, event_indices_restore_sort_order_array, :]

        event_ok_mask = np.hstack(event_ok_mask_list)
        event_ok_mask_sorted = event_ok_mask[event_indices_restore_sort_order_array]

        # removing bad events
        if self.remove_bad_events:
            if np.any(~event_ok_mask_sorted):
                warnings.warn("Found some bad events. Removing!", UserWarning)
                self.removed_corrupt_events = True
                self.event_ok_mask_sorted = event_ok_mask_sorted

        eventdata = eventdata[:, event_ok_mask_sorted, :]

        return eventdata

    def read(self) -> TimeSeries:
        """
        Calls read_events_data or read_session_data depending on user selection

        :return: TimeSeries object
        """
        return self.read_fcn()
