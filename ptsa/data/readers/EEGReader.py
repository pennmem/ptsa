from ptsa.data.TimeSeriesXray import TimeSeriesXray

from ptsa.data.events import Events
import numpy as np
from ptsa.data.readers import ParamsReader
from ptsa.data.readers.BaseRawReader import BaseRawReader

import xray

import time

from ptsa.data.common import TypeValTuple, PropertiedObject


class EEGReader(PropertiedObject):
    _descriptors = [
        TypeValTuple('channels', list, []),
        TypeValTuple('start_time', float, 0.0),
        TypeValTuple('end_time', float, 0.0),
        TypeValTuple('buffer_time', float, 0.0),
        TypeValTuple('events', np.recarray, np.recarray((0,), dtype=[('x', int)])),
        TypeValTuple('session_dataroot', str, ''),
    ]

    def __init__(self, **kwds):
        self.init_attrs(kwds)

        assert self.start_time <= self.end_time , \
            'start_time (%s) must be less or equal to end_time(%s) '%(self.start_time,self.end_time)

        self.read_fcn = self.read_events_data
        if self.session_dataroot:
            self.read_fcn = self.read_session_data

    def compute_read_offsets(self, dataroot):
        p_reader = ParamsReader(dataroot=dataroot)
        params = p_reader.read()
        samplerate = params['samplerate']
        start_offset = int(np.ceil(self.start_time * samplerate))
        end_offset = int(np.ceil(self.end_time * samplerate))
        buffer_offset = int(np.ceil(self.buffer_time * samplerate))
        return start_offset, end_offset, buffer_offset

    def __create_base_raw_readers(self):
        evs = self.events
        dataroots = np.unique(evs.eegfile)
        raw_readers = []
        original_dataroots = []

        for dataroot in dataroots:
            events_with_matched_dataroot = evs[evs.eegfile == dataroot]

            start_offset, end_offset, buffer_offset = self.compute_read_offsets(dataroot=dataroot)

            read_size = end_offset - start_offset + 2 * buffer_offset

            start_offsets = events_with_matched_dataroot.eegoffset - start_offset - buffer_offset

            brr = BaseRawReader(dataroot=dataroot, channels=self.channels, start_offsets=start_offsets,read_size=read_size)
            raw_readers.append(brr)

            original_dataroots.append(dataroot)

        return raw_readers, original_dataroots

    def read_session_data(self):
        p_reader = ParamsReader(dataroot=self.session_dataroot)
        params = p_reader.read()
        brr = BaseRawReader(dataroot=self.session_dataroot, channels=self.channels)
        return brr.read()


    def read_events_data(self):
        evs = self.events

        raw_readers, original_dataroots = self.__create_base_raw_readers()

        #used for restoring original order of the events
        ordered_indices = np.arange(len(evs))
        event_indices_list = []
        events = []

        ts_array_list = []

        for s,(raw_reader,dataroot) in enumerate(zip(raw_readers,original_dataroots)):

            ind = np.atleast_1d(evs.eegfile == dataroot)
            event_indices_list.append(ordered_indices[ind])
            events.append(evs[ind])


            ts_array = raw_reader.read()
            ts_array_list.append(ts_array)


        event_indices_array = np.hstack(event_indices_list)

        event_indices_restore_sort_order_array = event_indices_array.argsort()

        start_extend_time = time.time()
        #new code
        eventdata = xray.concat(ts_array_list,dim='start_offsets')
        # tdim = np.linspace(self.start_time-self.buffer_time,self.end_time+self.buffer_time,num=eventdata['offsets'].shape[0])
        tdim = np.arange(eventdata.shape[-1])*(1.0/eventdata.attrs['samplerate'])+(self.start_time-self.buffer_time)
        cdim = eventdata['channels']
        edim = np.concatenate(events).view(np.recarray).copy()

        attrs = eventdata.attrs.copy()
        # constructing TimeSeries Object
        eventdata = TimeSeriesXray(eventdata.data,dims=['channels','events','time'],coords=[cdim,edim,tdim])
        eventdata.attrs = attrs

        # restoring original order of the events
        eventdata = eventdata[:,event_indices_restore_sort_order_array,:]

        return eventdata

    def read(self):
        return self.read_fcn()


if __name__=='__main__':


    e_path = '/Users/m/data/events/RAM_FR1/R1060M_events.mat'
    from ptsa.data.readers import BaseEventReader

    base_e_reader = BaseEventReader(event_file=e_path, eliminate_events_with_no_eeg=True, use_ptsa_events_class=False)

    base_events = base_e_reader.read()

    base_events = base_events[base_events.type == 'WORD']

    # selecting only one session
    # base_events = base_events[base_events.eegfile == base_events[0].eegfile]

    from ptsa.data.readers.TalReader import TalReader
    tal_path = '/Users/m/data/eeg/R1060M/tal/R1060M_talLocs_database_bipol.mat'
    tal_reader = TalReader(tal_filename=tal_path)
    monopolar_channels = tal_reader.get_monopolar_channels()
    bipolar_pairs = tal_reader.get_bipolar_pairs()


    s = time.time()
    from ptsa.data.readers.TimeSeriesEEGReader import TimeSeriesEEGReader

    time_series_reader = TimeSeriesEEGReader(events=base_events, start_time=0.0,
                                             end_time=1.6, buffer_time=1.0, keep_buffer=True)

    base_eegs = time_series_reader.read(channels=monopolar_channels)
    print 'TimeSeriesEEGReader total read time = ',time.time()-s
    #############################################################################################
    #
    s = time.time()
    from ptsa.data.readers import EEGReader
    eeg_reader = EEGReader(events=base_events, channels=monopolar_channels, start_time=0.0,end_time=1.6, buffer_time=1.0)

    n_eegs = eeg_reader.read()

    print 'EEGReader total read time = ',time.time()-s


    s = time.time()
    dataroot=base_events[0].eegfile
    from ptsa.data.readers import EEGReader
    session_reader = EEGReader(session_dataroot=dataroot, channels=monopolar_channels)
    session_eegs = session_reader.read()
    print 'SESSION EEGReader total read time = ',time.time()-s


    from ptsa.data.readers.TimeSeriesSessionEEGReader import TimeSeriesSessionEEGReader

    time_series_reader = TimeSeriesSessionEEGReader(events=base_events[0:1], channels=monopolar_channels)

    ts = time_series_reader.read()
    print