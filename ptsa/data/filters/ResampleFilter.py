__author__ = 'm'

import numpy as np
import xray
from ptsa.data.common import TypeValTuple, PropertiedObject, get_axis_index
from scipy.signal import resample



class ResampleFilter(PropertiedObject):
    _descriptors = [
        TypeValTuple('resamplerate', float, -1.0),
        TypeValTuple('time_axis_index', int, -1),
    ]


    def __init__(self,**kwds):

        self.window = None
        self.time_series = None

        for option_name, val in kwds.items():

            try:
                attr = getattr(self,option_name)
                setattr(self,option_name,val)
            except AttributeError:
                print 'Option: '+ option_name+' is not allowed'



    def set_input(self, time_series):
        self.time_series = time_series

    def get_output(self):
        return self.filtered_time_series


    def filter(self):
        samplerate = self.time_series.attrs['samplerate']


        time_axis_length = np.squeeze(self.time_series.coords['time'].shape)
        new_length = int(np.round(time_axis_length*self.resamplerate/samplerate))

        print new_length

        if self.time_axis_index<0:
            self.time_axis_index = get_axis_index(data_array=self.time_series,axis_name='time')

        time_axis = self.time_series.coords[ self.time_series.dims[self.time_axis_index] ]

        try:
            time_axis_data = time_axis.data['time'] # time axis can be recarray with one of the arrays being time
        except KeyError:
            time_axis_data = time_axis.data

        time_idx_array = np.arange(len(time_axis))



        filtered_array, new_time_idx_array = resample(self.time_series.data,
                                         new_length, t=time_idx_array,
                                         axis=self.time_axis_index, window=self.window)

        # print new_time_axis

        new_time_idx_array = np.rint(new_time_idx_array).astype(np.int)

        new_time_axis = time_axis[new_time_idx_array]

        coords = []
        for i, dim_name in enumerate(self.time_series.dims):
            if i != self.time_axis_index:
                coords.append(self.time_series.coords[dim_name].copy())
            else:
                coords.append((dim_name,new_time_axis))


        self.filtered_time_series = xray.DataArray(filtered_array, coords=coords)
        self.filtered_time_series.attrs['samplerate'] = self.resamplerate

        return self.filtered_time_series





if __name__ == '__main__':


        event_range = range(0, 30, 1)
        e_path = '/Users/m/data/events/RAM_FR1/R1060M_events.mat'

        ##################################################################

        from ptsa.data.readers import PTSAEventReader
        from ptsa.data.events import Events
        e_reader = PTSAEventReader(event_file=e_path, eliminate_events_with_no_eeg=True)
        e_reader.read()

        events = e_reader.get_output()

        events = events[events.type == 'WORD']

        events = events[event_range]

        ev_order = np.argsort(events, order=('session','list','mstime'))
        events = events[ev_order]

        # in case fancy indexing looses Eventness of events we need to create Events object explicitely
        if not isinstance(events, Events):
            events = Events(events)

        eegs = events.get_data(channels=['003', '004'], start_time=0.0, end_time=1.6,
                               buffer_time=1.0, eoffset='eegoffset', keep_buffer=True,
                               eoffset_in_time=False, verbose=True)


        print
        eegs = eegs.resampled(50)

        ############################################################
        from ptsa.data.readers import BaseEventReader

        base_e_reader = BaseEventReader(event_file=e_path, eliminate_events_with_no_eeg=True, use_ptsa_events_class=False)

        base_e_reader.read()

        base_events = base_e_reader.get_output()

        base_events = base_events[base_events.type == 'WORD']

        base_ev_order = np.argsort(base_events, order=('session','list','mstime'))
        base_events = base_events[base_ev_order]

        base_events = base_events[event_range]
        print base_events

        from ptsa.data.readers.TimeSeriesEEGReader import TimeSeriesEEGReader

        time_series_reader = TimeSeriesEEGReader(events=base_events, start_time=0.0,
                                                 end_time=1.6, buffer_time=1.0, keep_buffer=True)

        time_series_reader.read(channels=['002', '003'])

        base_eegs = time_series_reader.get_output()



        resample_filter = ResampleFilter(time_series=base_eegs, resamplerate=50.0)

        base_eegs_resampled = resample_filter.filter()
