from __future__ import annotations

from typing import Union

import numpy as np
import numpy.typing as npt
import traits.api
import xarray as xr

from . import BaseFilter
from ptsa.data.timeseries import TimeSeries

# An ``events`` recarray-or-ndarray; some callers pass a structured
# ``np.ndarray``, others pass an ``np.recarray``. The chopper only uses
# field-style access (``arr.eegfile``, ``arr.eegoffset``).
EventsArray = Union[np.recarray, np.ndarray]


class DataChopper(BaseFilter):
    """
    EventDataChopper converts continuous time series of entire session into chunks based on the events specification
    In other words you may read entire eeg session first and then using EventDataChopper
    divide it into chunks corresponding to events of your choice
    """
    start_time = traits.api.CFloat
    end_time = traits.api.CFloat
    buffer_time = traits.api.CFloat
    events = traits.api.Array
    start_offsets = traits.api.CArray
    timeseries = traits.api.Instance(TimeSeries)

    def __init__(
        self,
        start_time: float = 0.0,
        end_time: float = 0.0,
        buffer_time: float = 0.0,
        events: EventsArray = np.recarray((1,), dtype=[('x', int)]),
        start_offsets: np.ndarray = np.array([], dtype=int),
    ) -> None:
        """
        :param start_time {float} -  read start offset in seconds w.r.t to the eegeffset specified in the events recarray
        :param end_time {float} -  read end offset in seconds w.r.t to the eegeffset specified in the events recarray
        :param end_time {float} -  extra buffer in seconds (subtracted from start read and added to end read)
        :param events {np.recarray} - numpy recarray representing events
        :param startoffsets {np.ndarray} - numpy array with offsets at which chopping should take place


        :return: None

        .. versionchanged:: 2.0

            Parameter "time_series" was renamed to "timeseries".

        """
        super().__init__()
        self.start_time = start_time
        self.end_time = end_time
        self.buffer_time = buffer_time
        self.events = events
        self.start_offsets = start_offsets

    def get_event_chunk_size_and_start_point_shift(
        self,
        eegoffset: int,
        samplerate: float,
        offset_time_array: npt.NDArray,
    ) -> tuple[int, int]:
        """
        Computes number of time points for each event and read offset w.r.t. event's eegoffset
        :param ev: record representing single event
        :param samplerate: samplerate fo the time series
        :param offset_time_array: "offsets" axis of the DataArray returned by EEGReader. This is the axis that represents
        time axis but instead of beind dimensioned to seconds it simply represents position of a given data point in a series
        The time axis is constructed by dividint offsets axis by the samplerate
        :return: event's read chunk size {int}, read offset w.r.t. to event's eegoffset {}
        """
        # figuring out read size chunk and shift w.r.t to eegoffset. We need this fcn in case we pass resampled session data

        original_samplerate = float((offset_time_array[-1] - offset_time_array[0])) / offset_time_array.shape[
            0] * samplerate

        # ``self.buffer_time`` etc. are CFloat traits; on a bound instance
        # they return floats but pyright sees the class descriptor.
        # ``trait_get`` returns a dict[str, Any] of the runtime values, which
        # is the documented way to side-step that descriptor confusion.
        traits_d = self.trait_get('start_time', 'end_time', 'buffer_time')
        start_time = float(traits_d['start_time'])
        end_time = float(traits_d['end_time'])
        buffer_time = float(traits_d['buffer_time'])

        start_point = eegoffset - int(np.ceil((buffer_time - start_time) * original_samplerate))
        end_point = eegoffset + int(
            np.ceil((end_time + buffer_time) * original_samplerate))

        selector_array = np.where((offset_time_array >= start_point) & (offset_time_array < end_point))[0]
        start_point_shift = selector_array[0] - np.where((offset_time_array >= eegoffset))[0][0]

        return len(selector_array), start_point_shift

    def filter(self, timeseries: "TimeSeries") -> "TimeSeries":
        """
        Chops session into chunks corresponding to events
        :return: TimeSeries object with chopped session
        """
        # ``self.start_offsets`` is a CArray trait; coerce to a real ndarray
        # so pyright treats it as Sized/Iterable.
        start_offsets_arr: np.ndarray = np.asarray(self.start_offsets)
        events_arr: np.ndarray = np.asarray(self.events)

        chop_on_start_offsets_flag = bool(len(start_offsets_arr))

        chopping_axis_data: np.ndarray
        if chop_on_start_offsets_flag:

            start_offsets = start_offsets_arr
            chopping_axis_name = 'start_offsets'
            chopping_axis_data = start_offsets
        else:

            evs = events_arr[events_arr['eegfile'] == timeseries.attrs['dataroot']]
            start_offsets = evs['eegoffset']
            chopping_axis_name = 'events'
            chopping_axis_data = evs


        samplerate = float(timeseries['samplerate'])
        offset_time_array = timeseries['offsets']

        event_chunk_size, start_point_shift = self.get_event_chunk_size_and_start_point_shift(
            eegoffset=start_offsets[0],
            samplerate=samplerate,
            offset_time_array=np.asarray(offset_time_array),
        )


        ts_d = self.trait_get('start_time', 'buffer_time')
        event_time_axis = np.arange(event_chunk_size) * (1.0 / samplerate) + (
            float(ts_d['start_time']) - float(ts_d['buffer_time']))

        data_list = []

        for i, eegoffset in enumerate(start_offsets):

            start_chop_pos = np.where(offset_time_array >= eegoffset)[0][0]
            start_chop_pos += start_point_shift
            selector_array = np.arange(start_chop_pos, start_chop_pos + event_chunk_size)

            chopped_data_array = timeseries.isel(time=selector_array)

            chopped_data_array['time'] = event_time_axis
            chopped_data_array = chopped_data_array.expand_dims(start_offsets=[i])

            data_list.append(chopped_data_array)

        ev_concat_data = xr.concat(data_list, dim='start_offsets')


        ev_concat_data = ev_concat_data.rename({'start_offsets': chopping_axis_name})
        ev_concat_data[chopping_axis_name] = chopping_axis_data

        attrs = {
            "start_time": self.start_time,
            "end_time": self.end_time,
            "buffer_time": self.buffer_time,
        }
        ev_concat_data['samplerate'] = samplerate
        return TimeSeries.create(ev_concat_data, samplerate, attrs=attrs)
