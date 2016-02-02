__author__ = 'm'

import numpy as np

import  ptsa.data.common.xr as xr

from ptsa.data.common import TypeValTuple, PropertiedObject
from ptsa.data.TimeSeriesX import TimeSeriesX

class EventDataChopper(PropertiedObject):
    """
    EventDataChopper converts continuous time series of entire session into chunks based on the events specification
    In other words you may read entire eeg session first and then using EventDataChopper
    divide it into chunks corresponding to events of your choice
    """
    _descriptors = [

        TypeValTuple('start_time', float, 0.0),
        TypeValTuple('end_time', float, 0.0),
        TypeValTuple('buffer_time', float, 1.0),
        TypeValTuple('events', np.recarray, np.recarray((1,), dtype=[('x', int)])),
        TypeValTuple('session_data', TimeSeriesX, TimeSeriesX([0.0], dims=['time'])),
    ]

    def __init__(self, **kwds):
        """
        Constructor:

        :param kwds:allowed values are:
        -------------------------------------
        :param start_time {float} -  read start offset in seconds w.r.t to the eegeffset specified in the events recarray
        :param end_time {float} -  read end offset in seconds w.r.t to the eegeffset specified in the events recarray
        :param end_time {float} -  extra buffer in seconds (subtracted from start read and added to end read)
        :param events {np.recarray} - numpy recarray representing events
        :param session_datar {str} -  TimeSeriesX object with eeg session data

        :return: None
        """

        self.init_attrs(kwds)

    def get_event_chunk_size_and_start_point_shift(self, ev, samplerate, offset_time_array):
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

        # start_point = ev.eegoffset - int(np.ceil((self.buffer + self.time_shift) * original_samplerate))
        start_point = ev.eegoffset - int(np.ceil((self.buffer_time - self.start_time) * original_samplerate))
        end_point = ev.eegoffset + int(
            np.ceil((self.end_time + self.buffer_time) * original_samplerate))

        selector_array = np.where((offset_time_array >= start_point) & (offset_time_array < end_point))[0]
        start_point_shift = selector_array[0] - np.where((offset_time_array >= ev.eegoffset))[0][0]

        return len(selector_array), start_point_shift

    def filter(self):
        """
        Chops session into chunks orresponding to events
        :return: timeSeriesX object with chopped session
        """
        evs = self.events[self.events.eegfile == self.session_data.attrs['dataroot']]
        samplerate = self.session_data.attrs['samplerate']
        offset_time_array = self.session_data['offsets']

        event_chunk_size, start_point_shift = self.get_event_chunk_size_and_start_point_shift(
        ev=evs[0],
        samplerate=samplerate,
        offset_time_array=offset_time_array)

        event_time_axis = np.linspace(-self.buffer_time + self.start_time,
                                      self.end_time + self.buffer_time ,
                                      event_chunk_size)

        data_list = []

        for i, ev in enumerate(evs):

            start_chop_pos = np.where(offset_time_array >= ev.eegoffset)[0][0]
            start_chop_pos += start_point_shift
            selector_array = np.arange(start=start_chop_pos, stop=start_chop_pos + event_chunk_size)

            chopped_data_array = self.session_data.isel(time=selector_array)

            chopped_data_array['time'] = event_time_axis
            chopped_data_array['events'] = [i]

            data_list.append(chopped_data_array)

        ev_concat_data = xr.concat(data_list, dim='events')
        ev_concat_data['events'] = evs

        ev_concat_data.attrs['samplerate'] = samplerate
        ev_concat_data.attrs['start_time'] = self.start_time
        ev_concat_data.attrs['end_time'] = self.end_time
        ev_concat_data.attrs['buffer_time'] = self.buffer_time
        return TimeSeriesX(ev_concat_data)



if __name__ == '__main__':
    e_path = '/Users/m/data/events/RAM_FR1/R1060M_events.mat'

    from ptsa.data.readers import BaseEventReader

    base_e_reader = BaseEventReader(filename=e_path, eliminate_events_with_no_eeg=True, use_ptsa_events_class=False)

    base_events = base_e_reader.read()

    base_events = base_events[base_events.type == 'WORD']
    #picking firs session only
    base_events = base_events[base_events.eegfile == base_events[0].eegfile]

    from ptsa.data.readers.TalReader import TalReader

    tal_path = '/Users/m/data/eeg/R1060M/tal/R1060M_talLocs_database_bipol.mat'
    tal_reader = TalReader(filename=tal_path)
    monopolar_channels = tal_reader.get_monopolar_channels()


    dataroot=base_events[0].eegfile
    from ptsa.data.readers import EEGReader
    session_reader = EEGReader(session_dataroot=dataroot, channels=monopolar_channels)
    session_eegs = session_reader.read()


    from ptsa.data.filters import EventDataChopper
    sedc = EventDataChopper(events=base_events, session_data=session_eegs, start_time=0.0, end_time=1.6, buffer_time=1.0)
    chopped_session = sedc.filter()


    # from ptsa.data.readers.TimeSeriesSessionEEGReader import TimeSeriesSessionEEGReader
    #
    # time_series_reader = TimeSeriesSessionEEGReader(events=base_events, channels=['002', '003', '004', '005'])
    # # time_series_reader = TimeSeriesSessionEEGReader(events=base_events, channels=monopolar_channels)
    # ts_dict = time_series_reader.read()
    #
    # print ts_dict
    #
    # from ptsa.data.filters.EventDataChopper import EventDataChopper
    #
    # edc = EventDataChopper(events=base_events, event_duration=1.6, buffer=1.0, data_dict=ts_dict)
    # ev_data_dict = edc.filter()
    # print ev_data_dict
    # #
    # # # from ptsa.data.filters.EventDataChopper import EventDataChopper
    # # #
    # # # edc = EventDataChopper(events=base_events, event_duration=1.6,buffer=1.0,session_data_dict=ts_dict)
    # # # ev_data_dict = edc.filter()
    # # # print ev_data_dict
    # # import sys
    # #
