__author__ = 'm'

from ptsa.data.RawBinWrapperXray import RawBinWrapperXray

from collections import OrderedDict

import numpy as np

import xray

from ptsa.data.common import TypeValTuple, PropertiedObject


class TimeSeriesSessionEEGReader(PropertiedObject):
    _descriptors = [
        TypeValTuple('samplerate', float, -1.0),
        TypeValTuple('channels', list, []),
        TypeValTuple('offset', int, 0),
        TypeValTuple('event_data_only', bool, False),
        TypeValTuple('default_buffer', float, 10.0),
        TypeValTuple('events', np.recarray, np.recarray((1,), dtype=[('x', int)])),

    ]

    def __init__(self, **kwds):

        for option_name, val in kwds.items():

            try:
                attr = getattr(self, option_name)
                setattr(self, option_name, val)
            except AttributeError:
                print 'Option: ' + option_name + ' is not allowed'

        self.eegfile_names = self._extract_session_eegfile_names()

        self._extract_samplerate(self.eegfile_names[0])

        self._create_bin_readers(self.eegfile_names)

        self.bin_readers_dict = self._create_bin_readers(self.eegfile_names)

    def get_session_eegfile_names(self):
        return self.eegfile_names

    def get_number_of_sessions(self):
        return self.eegfile_names

    def _extract_session_eegfile_names(self):

        # sorting file names in the order in which they appear in the file
        evs = self.events
        eegfile_names = np.unique(evs.eegfile)
        eeg_file_names_sorter = np.zeros(len(eegfile_names), dtype=np.int)

        for i, eegfile_name in enumerate(eegfile_names):
            eeg_file_names_sorter[i] = np.where(evs.eegfile == eegfile_name)[0][0]

        eeg_file_names_sorter = np.argsort(eeg_file_names_sorter)

        eegfile_names = eegfile_names[eeg_file_names_sorter]

        # print eegfile_names

        return eegfile_names

    def _extract_samplerate(self, eegfile_name):
        rbw_xray = RawBinWrapperXray(eegfile_name)
        data_params = rbw_xray._get_params(eegfile_name)
        self.samplerate = data_params['samplerate']

    def _create_bin_readers(self, eegfile_names):

        bin_readers_dict = OrderedDict()

        for eegfile_name in eegfile_names:
            try:
                bin_readers_dict[eegfile_name] = RawBinWrapperXray(eegfile_name)
            except TypeError:
                warning_str = 'Could not create reader for %s' % eegfile_name
                print warning_str
                raise TypeError(warning_str)

        return bin_readers_dict

    def determine_read_offset_range(self, eegfile_name):
        # determine events that have matching eegfile_name
        evs = self.events[self.events.eegfile == eegfile_name]

        start_offset = evs[0].eegoffset - int(np.ceil(self.default_buffer*self.samplerate))
        if start_offset<0:
            start_offset

        end_offset = evs[-1].eegoffset + int(np.ceil(self.default_buffer*self.samplerate))

        return start_offset,end_offset

    def read_session(self, eegfile_name):
        samplesize = 1.0 / self.samplerate

        bin_reader = self.bin_readers_dict[eegfile_name]

        print 'reading ', eegfile_name

        start_offset = self.offset
        end_offset = -1
        if self.event_data_only:
            #reading continuous data containig events and small buffer
            start_offset, end_offset = self.determine_read_offset_range(eegfile_name)

        eegdata = bin_reader._load_all_data(channels=self.channels, start_offset=start_offset, end_offset=end_offset)


        # constructing time exis as record array [(session_time_in_sec,offset)]

        number_of_time_points = eegdata.shape[2]
        start_time = start_offset * samplesize
        end_time = start_time + number_of_time_points * samplesize

        time_range = np.linspace(start_time, end_time, number_of_time_points)
        eegoffset = np.arange(start_offset, start_offset+ number_of_time_points)

        time_axis = np.rec.fromarrays([time_range, eegoffset], names='time,eegoffset')

        # constructing xray Data Array with session eeg data - note we are adding event dimension to simplify
        # chopping of the data sample into events - single events will be concatenated allong events axis
        eegdata_xray = xray.DataArray(eegdata, coords=[self.channels, np.arange(1), time_axis],
                                      dims=['channels', 'events', 'time'])
        eegdata_xray.attrs['samplerate'] = self.samplerate

        print 'last_time_stamp=',eegdata_xray['time'][-1]

        return eegdata_xray

    def read(self, session_list=[]):

        session_eegdata_dict = OrderedDict()
        samplesize = 1.0 / self.samplerate

        eegfile_names =  self.bin_readers_dict.keys() if len(session_list)==0 else session_list
        for eegfile_name in eegfile_names:
            eegdata_xray = self.read_session(eegfile_name)
            session_eegdata_dict[eegfile_name] = eegdata_xray

        return session_eegdata_dict


if __name__ == '__main__':
    event_range = range(0, 30, 1)
    e_path = '/Users/m/data/events/RAM_FR1/R1060M_events.mat'

    from ptsa.data.readers import BaseEventReader

    base_e_reader = BaseEventReader(event_file=e_path, eliminate_events_with_no_eeg=True, use_ptsa_events_class=False)

    base_e_reader.read()

    base_events = base_e_reader.get_output()

    base_events = base_events[base_events.type == 'WORD']

    from ptsa.data.readers.TimeSeriesSessionEEGReader import TimeSeriesSessionEEGReader

    time_series_reader = TimeSeriesSessionEEGReader(events=base_events, event_data_only=True, channels=['002', '003', '004', '005'])

    # time_series_reader = TimeSeriesSessionEEGReader(events=base_events, event_data_only=True, channels=['002', '003', '004', '005'])
    ts = time_series_reader.read()

    print ts

    # #
    # # sys.exit()
    # print ts
    #
    # for eegfile_name, eeg_session_data in ts.items():
    #     base_events_0 = base_events[base_events.eegfile == eegfile_name]
    #     break
    #
    # print base_events_0
    #
    # samplerate = eeg_session_data.attrs['samplerate']
    # ev_duration = 1.6
    # buffer = 1.0
    #
    # eegoffset_time_array = eeg_session_data['time'].values['eegoffset']
    #
    # ev_data_list = []
    # for i, ev in enumerate(base_events_0):
    #     print ev.eegoffset
    #     start_offset = ev.eegoffset - int(np.ceil(buffer * samplerate))
    #     end_offset = ev.eegoffset + int(np.ceil((ev_duration + buffer) * samplerate))
    #     print "start_offset,end_offset, size=", start_offset, end_offset, end_offset - start_offset
    #     # eegoffset_time_array = ts['time'].values['eegoffset']
    #     selector_array = np.where((eegoffset_time_array >= start_offset) & (eegoffset_time_array < end_offset))[0]
    #
    #     event_time_axis = np.linspace(-1.0, 2.6, len(selector_array))
    #
    #     ev_array = eeg_session_data[:, :, selector_array]
    #
    #     ev_array['time'] = event_time_axis
    #     ev_array['events'] = [i]
    #
    #     ev_data_list.append(ev_array)
    #     # ev_data_list.append(ts[:,:,selector_array].values)
    #
    #     print i
    #     # print ev_array
    #     # if i==2:
    #     #     break
    #
    # eventdata = xray.concat(ev_data_list, dim='events')
    #
    # # eventdata =np.concatenate(ev_data_list,axis=1)
    #
    # # eventdata = xray.concat(ev_data_list,dim='events')
    #
    #
    # print eventdata
    # #
    # #
    # #
    # #
    # # # eegoffset_time_array = ts['time'].values['eegoffset']
    # # #
    # # # ev_data_list = []
    # # # for i, ev  in enumerate(base_events_0):
    # # #     print ev.eegoffset
    # # #     start_offset = ev.eegoffset-int(np.ceil(buffer*samplerate))
    # # #     end_offset = ev.eegoffset+int(np.ceil((ev_duration+buffer)*samplerate))
    # # #     print "start_offset,end_offset, size=",start_offset,end_offset,end_offset-start_offset
    # # #     # eegoffset_time_array = ts['time'].values['eegoffset']
    # # #     selector_array = np.where( (eegoffset_time_array>=start_offset)& (eegoffset_time_array<end_offset))[0]
    # # #
    # # #     event_time_axis = np.linspace(-1.0,2.6,len(selector_array))
    # # #
    # # #     ev_array = ts[:,:,selector_array]
    # # #     ev_array['time']=event_time_axis
    # # #     ev_array['events']= [i]
    # # #
    # # #     ev_data_list.append(ev_array)
    # # #     # ev_data_list.append(ts[:,:,selector_array])
    # # #
    # # #     print i
    # # #     # print ev_array
    # # #     if i ==2:
    # # #         break
    # # #
    # # #
    # # # # eventdata = xray.concat(ev_data_list,dim='events')
    # # # eventdata = xray.concat(ev_data_list,dim='events')
    # # #
    # # #
    # # # print eventdata
    # #
