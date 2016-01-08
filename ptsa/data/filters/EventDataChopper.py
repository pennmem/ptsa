__author__ = 'm'

from ptsa.data.RawBinWrapperXray import RawBinWrapperXray

from collections import OrderedDict

import numpy as np

import xray

from ptsa.data.common import TypeValTuple, PropertiedObject


class EventDataChopper(PropertiedObject):
    _descriptors = [

        TypeValTuple('time_shift', float, 0.0),
        TypeValTuple('event_duration', float, 0.0),
        TypeValTuple('buffer', float, 1.0),
        TypeValTuple('events', np.recarray, np.recarray((1,),dtype=[('x', int)]) ),
        TypeValTuple('session_data_dict', dict, {}),
    ]

    def __init__(self, **kwds):



        for option_name, val in kwds.items():

            try:
                attr = getattr(self,option_name)
                setattr(self,option_name,val)
            except AttributeError:
                print 'Option: '+ option_name+' is not allowed'


    def filter(self):

        session_event_data_dict = OrderedDict()

        for eegfile_name ,eeg_session_data in self.session_data_dict.items():

            evs = self.events[self.events.eegfile==eegfile_name]

            samplerate = eeg_session_data.attrs['samplerate']

            #used in constructing time_axis
            eegoffset_time_array = eeg_session_data['time'].values['eegoffset']

            ev_data_list = []
            for i, ev  in enumerate(evs):
                print ev.eegoffset
                start_offset = ev.eegoffset-int(np.ceil(self.buffer*samplerate))
                end_offset = ev.eegoffset+int(np.ceil((self.event_duration+self.buffer)*samplerate))
                #adding additional time shift if user requests it
                start_offset += int(np.ceil(self.time_shift*samplerate))
                end_offset += int(np.ceil(self.time_shift*samplerate))

                print "start_offset,end_offset, size=",start_offset,end_offset,end_offset-start_offset
                # eegoffset_time_array = ts['time'].values['eegoffset']
                selector_array = np.where( (eegoffset_time_array>=start_offset)& (eegoffset_time_array<end_offset))[0]



                event_time_axis = np.linspace(-1.0,2.6,len(selector_array))

                ev_array = eeg_session_data[:,:,selector_array]

                ev_array['time']=event_time_axis
                ev_array['events']= [i]

                ev_data_list.append(ev_array)


                print i

            eventdata = xray.concat(ev_data_list,dim='events')

            eventdata.attrs['samplerate'] = samplerate
            eventdata.attrs['time_shift'] = self.time_shift
            eventdata.attrs['event_duration'] = self.event_duration
            eventdata.attrs['buffer'] = self.buffer

            session_event_data_dict[eegfile_name] = eventdata

            break

        self._session_event_data_dict = session_event_data_dict
        return session_event_data_dict


    def get_output(self):
        return self._session_event_data_dict

    def set_output(self,evs):
        pass



if __name__=='__main__':
    e_path = '/Users/m/data/events/RAM_FR1/R1060M_events.mat'

    from ptsa.data.readers import BaseEventReader

    base_e_reader = BaseEventReader(event_file=e_path, eliminate_events_with_no_eeg=True, use_ptsa_events_class=False)

    base_e_reader.read()

    base_events = base_e_reader.get_output()

    base_events = base_events[base_events.type == 'WORD']


    from ptsa.data.readers.TimeSeriesSessionEEGReader import TimeSeriesSessionEEGReader

    time_series_reader = TimeSeriesSessionEEGReader(events=base_events, channels = ['002', '003', '004', '005'])

    ts = time_series_reader.read()

    print ts

    from ptsa.data.filters.EventDataChopper import EventDataChopper

    edc = EventDataChopper(events=base_events, event_duration=1.6,buffer=1.0,session_data_dict=ts)
    ev_data = edc.filter()
    print ev_data
    import sys
    sys.exit()
