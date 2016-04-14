__author__ = 'm'

import numpy as np

import  ptsa.data.common.xr as xr

from ptsa.data.common import TypeValTuple, PropertiedObject
from ptsa.data.TimeSeriesX import TimeSeriesX
from ptsa.data.filters import BaseFilter


class DataChopper(PropertiedObject,BaseFilter):
    """
    EventDataChopper converts continuous time series of entire session into chunks based on the events specification
    In other words you may read entire eeg session first and then using EventDataChopper
    divide it into chunks corresponding to events of your choice
    """
    _descriptors = [

        TypeValTuple('start_time', float, 0.0),
        TypeValTuple('end_time', float, 0.0),
        TypeValTuple('buffer_time', float, 0.0),
        TypeValTuple('events', np.recarray, np.recarray((1,), dtype=[('x', int)])),
        TypeValTuple('start_offsets', np.ndarray, np.array([], dtype=int)),
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
        :param startoffsets {np.ndarray} - numpy array with offsets at which chopping should take place
        :param session_datar {str} -  TimeSeriesX object with eeg session data

        :return: None
        """

        self.init_attrs(kwds)

    def get_event_chunk_size_and_start_point_shift(self, eegoffset, samplerate, offset_time_array):
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


        start_point = eegoffset - int(np.ceil((self.buffer_time - self.start_time) * original_samplerate))
        end_point = eegoffset + int(
            np.ceil((self.end_time + self.buffer_time) * original_samplerate))

        selector_array = np.where((offset_time_array >= start_point) & (offset_time_array < end_point))[0]
        start_point_shift = selector_array[0] - np.where((offset_time_array >= eegoffset))[0][0]

        return len(selector_array), start_point_shift


    def filter(self):
        """
        Chops session into chunks orresponding to events
        :return: timeSeriesX object with chopped session
        """
        chop_on_start_offsets_flag = bool(len(self.start_offsets))

        if chop_on_start_offsets_flag:

            start_offsets = self.start_offsets
            chopping_axis_name = 'start_offsets'
            chopping_axis_data = start_offsets
        else:

            evs = self.events[self.events.eegfile == self.session_data.attrs['dataroot']]
            start_offsets = evs.eegoffset
            chopping_axis_name = 'events'
            chopping_axis_data = evs


        # samplerate = self.session_data.attrs['samplerate']
        samplerate = float(self.session_data['samplerate'])
        offset_time_array = self.session_data['offsets']

        event_chunk_size, start_point_shift = self.get_event_chunk_size_and_start_point_shift(
        eegoffset=start_offsets[0],
        samplerate=samplerate,
        offset_time_array=offset_time_array)


        event_time_axis = np.arange(event_chunk_size)*(1.0/samplerate)+(self.start_time-self.buffer_time)

        data_list = []

        for i, eegoffset in enumerate(start_offsets):

            start_chop_pos = np.where(offset_time_array >= eegoffset)[0][0]
            start_chop_pos += start_point_shift
            selector_array = np.arange(start=start_chop_pos, stop=start_chop_pos + event_chunk_size)

            chopped_data_array = self.session_data.isel(time=selector_array)

            chopped_data_array['time'] = event_time_axis
            chopped_data_array['start_offsets'] = [i]

            data_list.append(chopped_data_array)

        ev_concat_data = xr.concat(data_list, dim='start_offsets')


        ev_concat_data = ev_concat_data.rename({'start_offsets':chopping_axis_name})
        ev_concat_data[chopping_axis_name] = chopping_axis_data

        # ev_concat_data.attrs['samplerate'] = samplerate
        ev_concat_data['samplerate'] = samplerate
        ev_concat_data.attrs['start_time'] = self.start_time
        ev_concat_data.attrs['end_time'] = self.end_time
        ev_concat_data.attrs['buffer_time'] = self.buffer_time
        return TimeSeriesX(ev_concat_data)

