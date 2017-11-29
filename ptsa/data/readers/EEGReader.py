from collections import defaultdict
import os.path
import warnings

import numpy as np
import xarray as xr

from ptsa.data.common import TypeValTuple, PropertiedObject
from ptsa.data.readers.ParamsReader import ParamsReader
from ptsa.data.readers.BaseRawReader import BaseRawReader
from ptsa.data.readers.H5RawReader import H5RawReader
from ptsa.data.readers import BaseReader
from ptsa import six
from ptsa.data.TimeSeriesX import TimeSeriesX


class IncompatibleDataError(Exception):
    pass


class EEGReader(PropertiedObject, BaseReader):
    """
    Reader that knows how to read binary eeg files. It can read chunks of the eeg signal based on events input
    or can read entire session if session_dataroot is non empty.

    Keyword Arguments
    -----------------
    channels : np.ndarray
        numpy array of channel labels
    start_time : float
        read start offset in seconds w.r.t to the eegeffset specified in the events recarray
    end_time:
        read end offset in seconds w.r.t to the eegeffset specified in the events recarray
    buffer_time : float
        extra buffer in seconds (subtracted from start read and added to end read)
    events : np.recarray
        numpy recarray representing Events
    session_dataroot : str
        path to session dataroot. When set the reader will read the entire session
    remove_bad_events : bool
        Remove "bad" events. Defaults to True.

    Returns
    -------
    None

    """
    _descriptors = [
        TypeValTuple('channels', np.ndarray, np.array([], dtype='|S3')),
        TypeValTuple('start_time', float, 0.0),
        TypeValTuple('end_time', float, 0.0),
        TypeValTuple('buffer_time', float, 0.0),
        TypeValTuple('events', object, object),
        TypeValTuple('session_dataroot', six.string_types, ''),
        TypeValTuple('remove_bad_events', bool, True)
    ]

    READER_FILETYPE_DICT = defaultdict(lambda : BaseRawReader)
    READER_FILETYPE_DICT.update({'.h5':H5RawReader})

    def __init__(self, **kwds):
        self.init_attrs(kwds)
        self.removed_corrupt_events = False
        self.event_ok_mask_sorted = None

        assert self.start_time <= self.end_time, \
            'start_time (%s) must be less or equal to end_time(%s) ' % (self.start_time, self.end_time)

        self.read_fcn = self.read_events_data
        if self.session_dataroot:
            self.read_fcn = self.read_session_data
        self.channel_name = 'channels'

    def compute_read_offsets(self, dataroot):
        """
        Reads Parameter file and exracts sampling rate that is used to convert from start_time, end_time, buffer_time
        (expressed in seconds)
        to start_offset, end_offset, buffer_offset expressed as integers indicating number of time series data points (not bytes!)

        :param dataroot: core name of the eeg datafile
        :return: tuple of 3 {int} - start_offset, end_offset, buffer_offset
        """
        p_reader = ParamsReader(dataroot=dataroot)
        params = p_reader.read()
        samplerate = params['samplerate']

        start_offset = int(np.round(self.start_time * samplerate))
        end_offset = int(np.round(self.end_time * samplerate))
        buffer_offset = int(np.round(self.buffer_time * samplerate))

        return start_offset, end_offset, buffer_offset

    def __create_base_raw_readers(self):
        """
        Creates BaseRawreader for each (unique) dataroot present in events recarray
        :return: list of BaseRawReaders and list of dataroots
        :raises: [IncompatibleDataError] if the readers are not all the same class
        """
        evs = self.events
        dataroots = np.unique(evs.eegfile)
        raw_readers = []
        original_dataroots = []

        for dataroot in dataroots:
            events_with_matched_dataroot = evs[evs.eegfile == dataroot]

            start_offset, end_offset, buffer_offset = self.compute_read_offsets(dataroot=dataroot)

            read_size = end_offset - start_offset + 2 * buffer_offset

            # start_offsets = events_with_matched_dataroot.eegoffset + start_offset - buffer_offset
            start_offsets = events_with_matched_dataroot.eegoffset + start_offset - buffer_offset

            brr = self.READER_FILETYPE_DICT[os.path.splitext(dataroot)[-1]](dataroot=dataroot, channels=self.channels, start_offsets=start_offsets,
                                read_size=read_size)
            raw_readers.append(brr)

            original_dataroots.append(dataroot)

        return raw_readers, original_dataroots

    def read_session_data(self):
        """
        Reads entire session worth of data

        :return: TimeSeriesX object (channels x events x time) with data for entire session the events dimension has length 1
        """
        brr = self.READER_FILETYPE_DICT[self.session_dataroot](dataroot=self.session_dataroot, channels=self.channels)
        session_array,read_ok_mask = brr.read()
        self.channel_name = brr.channel_name

        offsets_axis = session_array['offsets']
        number_of_time_points = offsets_axis.shape[0]
        samplerate = float(session_array['samplerate'])
        physical_time_array = np.arange(number_of_time_points) * (1.0 / samplerate)

        # session_array = session_array.rename({'start_offsets': 'events'})

        session_time_series = TimeSeriesX(session_array.values,
                                          dims=[self.channel_name, 'start_offsets', 'time'],
                                          coords={
                                              self.channel_name: session_array[self.channel_name],
                                              'start_offsets': session_array['start_offsets'],
                                              'time': physical_time_array,
                                              'offsets': ('time', session_array['offsets']),
                                              'samplerate': session_array['samplerate']
                                          }
                                          )
        session_time_series.attrs = session_array.attrs.copy()
        session_time_series.attrs['dataroot'] = self.session_dataroot

        return session_time_series

    def removed_bad_data(self):
        return self.removed_corrupt_events

    def get_event_ok_mask(self):
        return self.event_ok_mask_sorted

    def read_events_data(self):
        """
        Reads eeg data for individual event

        :return: TimeSeriesX  object (channels x events x time) with data for individual events
        """
        self.event_ok_mask_sorted = None  # reset self.event_ok_mask_sorted

        evs = self.events

        raw_readers, original_dataroots = self.__create_base_raw_readers()

        # used for restoring original order of the events
        ordered_indices = np.arange(len(evs))
        event_indices_list = []
        events = []

        ts_array_list = []

        event_ok_mask_list = []

        for s, (raw_reader, dataroot) in enumerate(zip(raw_readers, original_dataroots)):

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
        edim = np.concatenate(events).view(np.recarray).copy()

        attrs = eventdata.attrs.copy()
        eventdata = TimeSeriesX(eventdata.data,
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

    def read(self):
        """
        Calls read_events_data or read_session_data depending on user selection

        :return: TimeSeriesX object
        """
        return self.read_fcn()
