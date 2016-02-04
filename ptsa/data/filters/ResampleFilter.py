__author__ = 'm'

import numpy as np
import xray
from scipy.signal import resample

from ptsa.data.TimeSeriesX import TimeSeriesX
from ptsa.data.common import TypeValTuple, PropertiedObject


class ResampleFilter(PropertiedObject):

    '''
    Resample Filter
    '''

    _descriptors = [
        # TypeValTuple('time_series', np.ndarray, np.array([0.0])),
        TypeValTuple('time_series',TimeSeriesX, TimeSeriesX([0.0],dims=['time'])),
        # TypeValTuple('time_series', np.ndarray, np.array([0.0])),
        TypeValTuple('resamplerate', float, -1.0),
        TypeValTuple('time_axis_index', int, -1),
        TypeValTuple('round_to_original_timepoints', bool, False),

    ]


    # def __aaa(self):
    #     self.resamplerate = None
    #     self.time_axis_index = None
    #     self.round_to_original_timepoints = None
    #     # self.round_to_original_timepoints = None
    #     # setattr(self,'round_to_original_timepoints',None)

    def ___syntax_helper(self):
        self.time_series = None
        self.resamplerate = None
        self.time_axis_index = None
        self.round_to_original_timepoints = None


    def __init__(self,**kwds):
        '''

        :param kwds: allowed values are:
        -------------------------------------
        :param resamplerate - new sampling frequency
        :param time_series - TimeSeriesX object
        :param time_axis_index - index of the time axis
        :param round_to_original_timepoints  -  boolean flag indicating if timepoints from original time axis
        should be reused after proper rounding. Default setting is False
        -------------------------------------
        :return:
        '''
        self.window = None
        # self.time_series = None
        self.init_attrs(kwds)



    def filter(self):
        '''
        resamples time series
        :return:resampled time series with sampling frequency set to resamplerate
        '''
        samplerate = self.time_series.attrs['samplerate']


        time_axis_length = np.squeeze(self.time_series.coords['time'].shape)
        new_length = int(np.round(time_axis_length*self.resamplerate/samplerate))

        print new_length

        if self.time_axis_index<0:
            self.time_axis_index = self.time_series.get_axis_num('time')

        time_axis = self.time_series.coords[ self.time_series.dims[self.time_axis_index] ]

        try:
            time_axis_data = time_axis.data['time'] # time axis can be recarray with one of the arrays being time
        except (KeyError ,IndexError) as excp:
            # if we get here then most likely time axis is ndarray of floats
            time_axis_data = time_axis.data

        time_idx_array = np.arange(len(time_axis))


        if self.round_to_original_timepoints:
            filtered_array, new_time_idx_array = resample(self.time_series.data,
                                             new_length, t=time_idx_array,
                                             axis=self.time_axis_index, window=self.window)

            # print new_time_axis

            new_time_idx_array = np.rint(new_time_idx_array).astype(np.int)

            new_time_axis = time_axis[new_time_idx_array]

        else:
            filtered_array, new_time_axis = resample(self.time_series.data,
                                             new_length, t=time_axis_data,
                                             axis=self.time_axis_index, window=self.window)



        coords = []
        for i, dim_name in enumerate(self.time_series.dims):
            if i != self.time_axis_index:
                coords.append(self.time_series.coords[dim_name].copy())
            else:
                coords.append((dim_name,new_time_axis))


        filtered_time_series = xray.DataArray(filtered_array, coords=coords)
        filtered_time_series.attrs['samplerate'] = self.resamplerate
        filtered_time_series['samplerate'] = self.resamplerate
        return TimeSeriesX(filtered_time_series)


if __name__ == '__main__':


    event_range = range(0, 30, 1)
    e_path = '/Users/m/data/events/RAM_FR1/R1060M_events.mat'


    ##################################################################

    # from ptsa.data.readers import PTSAEventReader
    # from ptsa.data.events import Events
    # e_reader = PTSAEventReader(event_file=e_path, eliminate_events_with_no_eeg=True)
    # e_reader.read()
    #
    # events = e_reader.get_output()
    #
    # events = events[events.type == 'WORD']
    #
    # events = events[event_range]
    #
    # ev_order = np.argsort(events, order=('session','list','mstime'))
    # events = events[ev_order]
    #
    # # in case fancy indexing looses Eventness of events we need to create Events object explicitely
    # if not isinstance(events, Events):
    #     events = Events(events)
    #
    # eegs = events.get_data(channels=['003', '004'], start_time=0.0, end_time=1.6,
    #                        buffer_time=1.0, eoffset='eegoffset', keep_buffer=True,
    #                        eoffset_in_time=False, verbose=True)
    #
    #
    #
    # eegs = eegs.resampled(50)
    #
    # ############################################################
    from ptsa.data.readers import BaseEventReader

    base_e_reader = BaseEventReader(filename=e_path, eliminate_events_with_no_eeg=True, use_ptsa_events_class=False)

    base_events = base_e_reader.read()

    base_events = base_events[base_events.type == 'WORD']

    base_ev_order = np.argsort(base_events, order=('session','list','mstime'))
    base_events = base_events[base_ev_order]

    base_events = base_events[event_range]


#####################
    from ptsa.data.experimental.TimeSeriesSessionEEGReader import TimeSeriesSessionEEGReader

    time_series_session_reader = TimeSeriesSessionEEGReader(events=base_events, channels=np.array(['003', '004', '005']))

    ts_dict = time_series_session_reader.read()
    print ts_dict
    ts=ts_dict.items()[0][1]

    resample_filter_rounded = ResampleFilter(time_series=ts, resamplerate=50.0,round_to_original_timepoints=True)
    # resample_filter_rounded = ResampleFilter(time_series=ts, resamplerate=50.0)
    base_eegs_resampled_rounded = resample_filter_rounded.filter()

######################################

    from ptsa.data.experimental.TimeSeriesEEGReader import TimeSeriesEEGReader

    time_series_reader = TimeSeriesEEGReader(events=base_events, start_time=0.0,
                                             end_time=1.6, buffer_time=1.0, keep_buffer=True)

    base_eegs = time_series_reader.read(channels=['003', '004'])


    resample_filter = ResampleFilter(time_series=base_eegs, resamplerate=50.0)

    base_eegs_resampled = resample_filter.filter()


    resample_filter_rounded = ResampleFilter(time_series=base_eegs, resamplerate=50.0, round_to_original_timepoints=True)

    base_eegs_resampled_rounded = resample_filter_rounded.filter()


    print
