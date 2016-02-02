__author__ = 'm'

from collections import OrderedDict

import numpy as np
import xray

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

        for eegfile_name, data in self.data_dict.items():

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

            ev_concat_data = xray.concat(data_list, dim='events')

            # replacing simple events axis (consecutive integers) with recarray of events
            ev_concat_data['events'] = evs

            ev_concat_data.attrs['samplerate'] = samplerate
            ev_concat_data.attrs['time_shift'] = self.time_shift
            ev_concat_data.attrs['event_duration'] = self.event_duration
            ev_concat_data.attrs['buffer'] = self.buffer

            event_data_dict[eegfile_name] = TimeSeriesX(ev_concat_data)

            break  # REMOVE THIS

        return event_data_dict


if __name__ == '__main__':
    e_path = '/Users/m/data/events/RAM_FR1/R1060M_events.mat'

    from ptsa.data.readers import BaseEventReader

    base_e_reader = BaseEventReader(filename=e_path, eliminate_events_with_no_eeg=True)

    base_events = base_e_reader.read()

    base_events = base_events[base_events.type == 'WORD']

    from ptsa.data.readers.TalReader import TalReader

    tal_path = '/Users/m/data/eeg/R1060M/tal/R1060M_talLocs_database_bipol.mat'
    tal_reader = TalReader(filename=tal_path)
    monopolar_channels = tal_reader.get_monopolar_channels()

    from ptsa.data.experimental.TimeSeriesSessionEEGReader import TimeSeriesSessionEEGReader

    time_series_reader = TimeSeriesSessionEEGReader(events=base_events, channels=['002', '003', '004', '005'])
    # time_series_reader = TimeSeriesSessionEEGReader(events=base_events, channels=monopolar_channels)
    ts_dict = time_series_reader.read()

    print ts_dict

    from ptsa.data.experimental.EventDataChopper import EventDataChopper

    edc = EventDataChopper(events=base_events, event_duration=1.6, buffer=1.0, data_dict=ts_dict)
    ev_data_dict = edc.filter()
    print ev_data_dict

    # from ptsa.data.filters.EventDataChopper import EventDataChopper
    #
    # edc = EventDataChopper(events=base_events, event_duration=1.6,buffer=1.0,session_data_dict=ts_dict)
    # ev_data_dict = edc.filter()
    # print ev_data_dict

    # wavelets

    freqs = np.logspace(np.log10(3), np.log10(180), 12)
    for session_file, ev_data in ev_data_dict.items():
        break

    print ev_data

    bp = ev_data.values[0, 0, :] - ev_data.values[1, 0, :]

    from ptsa.wavelet import phase_pow_multi

    pow_ev_new = phase_pow_multi(freqs, bp, to_return='power', samplerates=ev_data.attrs['samplerate'])

    print 'pow_ev_new=', pow_ev_new

    for session_file, session_data in ts_dict.items():
        break

    bp_sess_0 = session_data.values[0, 0, :] - session_data.values[1, 0, :]
    print bp_sess_0

    pow_sess_new_0 = phase_pow_multi(freqs, bp_sess_0, to_return='power', samplerates=ev_data.attrs['samplerate'])

    print pow_sess_new_0

    pow_xray_0 = xray.DataArray(pow_sess_new_0.reshape(1, 1, pow_sess_new_0.shape[0], pow_sess_new_0.shape[1]),
                                coords=[['002_003'], np.arange(1), freqs, session_data['time']],
                                dims=['channels', 'events', 'frequency', 'time']
                                )

    bp_sess_1 = session_data.values[1, 0, :] - session_data.values[2, 0, :]
    print bp_sess_1

    pow_sess_new_1 = phase_pow_multi(freqs, bp_sess_1, to_return='power', samplerates=ev_data.attrs['samplerate'])

    print pow_sess_new_1

    pow_xray_1 = xray.DataArray(pow_sess_new_1.reshape(1, 1, pow_sess_new_1.shape[0], pow_sess_new_1.shape[1]),
                                coords=[['003_004'], np.arange(1), freqs, session_data['time']],
                                dims=['channels', 'events', 'frequency', 'time']
                                )

    pow_combined = xray.concat([pow_xray_0, pow_xray_1], dim='channels')

    pow_combined.attrs['samplerate'] = ev_data.attrs['samplerate']

    edcw = EventDataChopper(events=base_events, event_duration=1.6, buffer=1.0,
                            data_dict={base_events[0].eegfile: pow_combined})

    chopped_wavelets = edcw.filter()

    print

    # class EventDataChopper(PropertiedObject):
    #     _descriptors = [
    #
    #         TypeValTuple('time_shift', float, 0.0),
    #         TypeValTuple('event_duration', float, 0.0),
    #         TypeValTuple('buffer', float, 1.0),
    #         TypeValTuple('events', np.recarray, np.recarray((1,),dtype=[('x', int)]) ),
    #         TypeValTuple('session_data_dict', dict, {}),
    #     ]
    #
    #     def __init__(self, **kwds):
    #
    #
    #
    #         for option_name, val in kwds.items():
    #
    #             try:
    #                 attr = getattr(self,option_name)
    #                 setattr(self,option_name,val)
    #             except AttributeError:
    #                 print 'Option: '+ option_name+' is not allowed'
    #
    #
    #     def filter(self):
    #
    #         session_event_data_dict = OrderedDict()
    #
    #         for eegfile_name ,eeg_session_data in self.session_data_dict.items():
    #
    #             evs = self.events[self.events.eegfile==eegfile_name]
    #
    #             samplerate = eeg_session_data.attrs['samplerate']
    #
    #             #used in constructing time_axis
    #             eegoffset_time_array = eeg_session_data['time'].values['eegoffset']
    #
    #             ev_data_list = []
    #             for i, ev  in enumerate(evs):
    #                 print ev.eegoffset
    #                 start_offset = ev.eegoffset-int(np.ceil(self.buffer*samplerate))
    #                 end_offset = ev.eegoffset+int(np.ceil((self.event_duration+self.buffer)*samplerate))
    #                 #adding additional time shift if user requests it
    #                 start_offset += int(np.ceil(self.time_shift*samplerate))
    #                 end_offset += int(np.ceil(self.time_shift*samplerate))
    #
    #                 print "start_offset,end_offset, size=",start_offset,end_offset,end_offset-start_offset
    #                 # eegoffset_time_array = ts['time'].values['eegoffset']
    #                 selector_array = np.where( (eegoffset_time_array>=start_offset)& (eegoffset_time_array<end_offset))[0]
    #
    #
    #
    #                 event_time_axis = np.linspace(-1.0,2.6,len(selector_array))
    #
    #                 ev_array = eeg_session_data[:,:,selector_array]
    #
    #                 ev_array['time']=event_time_axis
    #                 ev_array['events']= [i]
    #
    #                 ev_data_list.append(ev_array)
    #
    #
    #                 print i
    #
    #             eventdata = xray.concat(ev_data_list,dim='events')
    #
    #             # replacing simple events axis (consecutive integers) with recarray of events
    #             eventdata['events'] = evs
    #
    #
    #
    #             eventdata.attrs['samplerate'] = samplerate
    #             eventdata.attrs['time_shift'] = self.time_shift
    #             eventdata.attrs['event_duration'] = self.event_duration
    #             eventdata.attrs['buffer'] = self.buffer
    #
    #             session_event_data_dict[eegfile_name] = eventdata
    #
    #             break
    #
    #         self._session_event_data_dict = session_event_data_dict
    #         return session_event_data_dict
    #
    #
    #     def get_output(self):
    #         return self._session_event_data_dict
    #
    #     def set_output(self,evs):
    #         pass


    #
    # class EventDataChopper(PropertiedObject):
    #     _descriptors = [
    #
    #         TypeValTuple('time_shift', float, 0.0),
    #         TypeValTuple('event_duration', float, 0.0),
    #         TypeValTuple('buffer', float, 1.0),
    #         TypeValTuple('events', np.recarray, np.recarray((1,),dtype=[('x', int)]) ),
    #         TypeValTuple('session_data_dict', dict, {}),
    #     ]
    #
    #     def __init__(self, **kwds):
    #
    #
    #
    #         for option_name, val in kwds.items():
    #
    #             try:
    #                 attr = getattr(self,option_name)
    #                 setattr(self,option_name,val)
    #             except AttributeError:
    #                 print 'Option: '+ option_name+' is not allowed'
    #
    #
    #     def filter(self):
    #
    #         session_event_data_dict = OrderedDict()
    #
    #         for eegfile_name ,eeg_session_data in self.session_data_dict.items():
    #
    #             evs = self.events[self.events.eegfile==eegfile_name]
    #
    #             samplerate = eeg_session_data.attrs['samplerate']
    #
    #             #used in constructing time_axis
    #             eegoffset_time_array = eeg_session_data['time'].values['eegoffset']
    #
    #             ev_data_list = []
    #             for i, ev  in enumerate(evs):
    #                 print ev.eegoffset
    #                 start_offset = ev.eegoffset-int(np.ceil(self.buffer*samplerate))
    #                 end_offset = ev.eegoffset+int(np.ceil((self.event_duration+self.buffer)*samplerate))
    #                 #adding additional time shift if user requests it
    #                 start_offset += int(np.ceil(self.time_shift*samplerate))
    #                 end_offset += int(np.ceil(self.time_shift*samplerate))
    #
    #                 print "start_offset,end_offset, size=",start_offset,end_offset,end_offset-start_offset
    #                 # eegoffset_time_array = ts['time'].values['eegoffset']
    #                 selector_array = np.where( (eegoffset_time_array>=start_offset)& (eegoffset_time_array<end_offset))[0]
    #
    #
    #
    #                 event_time_axis = np.linspace(-self.buffer, self.event_duration+self.buffer, len(selector_array))
    #
    #                 ev_array = eeg_session_data[:,:,selector_array]
    #
    #                 ev_array['time']=event_time_axis
    #                 ev_array['events']= [i]
    #
    #                 ev_data_list.append(ev_array)
    #
    #
    #                 print i
    #
    #             eventdata = xray.concat(ev_data_list,dim='events')
    #
    #             # replacing simple events axis (consecutive integers) with recarray of events
    #             eventdata['events'] = evs
    #
    #
    #
    #             eventdata.attrs['samplerate'] = samplerate
    #             eventdata.attrs['time_shift'] = self.time_shift
    #             eventdata.attrs['event_duration'] = self.event_duration
    #             eventdata.attrs['buffer'] = self.buffer
    #
    #             session_event_data_dict[eegfile_name] = eventdata
    #
    #             break
    #
    #         self._session_event_data_dict = session_event_data_dict
    #         return session_event_data_dict
    #
    #
    #     def get_output(self):
    #         return self._session_event_data_dict
    #
    #     def set_output(self,evs):
    #         pass
