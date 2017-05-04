__author__ = 'm'

from collections import OrderedDict

import numpy as np
import xarray as xr

from ptsa.data.TimeSeriesX import TimeSeriesX
from ptsa.data.common import TypeValTuple, PropertiedObject


class EventDataChopper(PropertiedObject):
    _descriptors = [

        TypeValTuple('time_shift', float, 0.0),
        TypeValTuple('event_duration', float, 0.0),
        TypeValTuple('buffer', float, 1.0),
        TypeValTuple('events', np.recarray, np.recarray((1,), dtype=[('x', int)])),
        TypeValTuple('data_dict', dict, {}),
    ]

    def __init__(self, **kwds):

        self.init_attrs(kwds)

    def get_event_chunk_size_and_start_point_shift(self, ev, samplerate, offset_time_array):
        # figuring out read size chunk and shift w.r.t to eegoffset

        original_samplerate = float((offset_time_array[-1] - offset_time_array[0])) / offset_time_array.shape[
            0] * samplerate

        start_point = ev.eegoffset - int(np.ceil((self.buffer + self.time_shift) * original_samplerate))
        end_point = ev.eegoffset + int(
            np.ceil((self.event_duration + self.buffer + self.time_shift) * original_samplerate))

        selector_array = np.where((offset_time_array >= start_point) & (offset_time_array < end_point))[0]
        start_point_shift = selector_array[0] - np.where((offset_time_array >= ev.eegoffset))[0][0]

        return len(selector_array), start_point_shift

    def filter(self):

        event_data_dict = OrderedDict()

        for eegfile_name, data in list(self.data_dict.items()):

            evs = self.events[self.events.eegfile == eegfile_name]

            samplerate = data.attrs['samplerate']

            # used in constructing time_axis
            offset_time_array = data['time'].values['eegoffset']

            event_chunk_size, start_point_shift = self.get_event_chunk_size_and_start_point_shift(ev=evs[0],
                                                                                                  samplerate=samplerate,
                                                                                                  offset_time_array=offset_time_array)

            event_time_axis = np.linspace(-self.buffer + self.time_shift,
                                          self.event_duration + self.buffer + self.time_shift,
                                          event_chunk_size)

            data_list = []

            shape = None

            for i, ev in enumerate(evs):
                # print ev.eegoffset
                start_chop_pos = np.where(offset_time_array >= ev.eegoffset)[0][0]
                start_chop_pos += start_point_shift
                selector_array = np.arange(start=start_chop_pos, stop=start_chop_pos + event_chunk_size)

                # ev_array = eeg_session_data[:,:,selector_array] # ORIG CODE

                chopped_data_array = data.isel(time=selector_array)

                chopped_data_array['time'] = event_time_axis
                chopped_data_array['events'] = [i]

                data_list.append(chopped_data_array)

                # print i

            ev_concat_data = xr.concat(data_list, dim='events')

            # replacing simple events axis (consecutive integers) with recarray of events
            ev_concat_data['events'] = evs

            ev_concat_data.attrs['samplerate'] = samplerate
            ev_concat_data.attrs['time_shift'] = self.time_shift
            ev_concat_data.attrs['event_duration'] = self.event_duration
            ev_concat_data.attrs['buffer'] = self.buffer

            event_data_dict[eegfile_name] = TimeSeriesX(ev_concat_data)

            break  # REMOVE THIS

        return event_data_dict
