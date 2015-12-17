__author__ = 'm'

from os.path import *
import pathlib
from ptsa.data.rawbinwrapper import RawBinWrapper
from ptsa.data.events import Events
import numpy as np

import xray

import time


class TimeSeriesEEGReader(object):
    def __init__(self, events, **kwds):
        self.__events = events
        self.data_dir_prefix = kwds['data_dir_prefix']
        self.__time_series = None
        self._start_time=0.0
        self._end_time=0.0
        self._buffer_time=0.0
        self._keep_buffer=False
        self._samplerate=None
    


    def __create_bin_readers(self):
        evs = self.__events
        raw_bin_wrappers = np.empty([len(evs),], dtype=np.dtype(RawBinWrapper))
        for i, ev in enumerate(evs):
            try:
                eeg_file_path = join(self.data_dir_prefix, str(pathlib.Path(str(ev.eegfile)).parts[1:]))
                raw_bin_wrappers[i] = RawBinWrapper(eeg_file_path)
                #setting samplerate
                if self.samplerate is None:
                    data_params = raw_bin_wrappers[i]._get_params(eeg_file_path)

                    self.samplerate = data_params['samplerate']

                # self.raw_data_root=str(eeg_file_path)
            except TypeError:
                print 'skipping event with eegfile=',ev.eegfile
                pass
        return raw_bin_wrappers

    
    @property
    def samplerate(self):
        return self._samplerate

    @samplerate.setter
    def samplerate(self, val):
        self._samplerate = val

    
    @property
    def start_time(self):
        return self._start_time

    @start_time.setter
    def start_time(self, val):
        self._start_time = val

    @property
    def end_time(self):
        return self._end_time

    @end_time.setter
    def end_time(self, val):
        self._end_time = val

    @property
    def buffer_time(self):
        return self._buffer_time

    @buffer_time.setter
    def buffer_time(self, val):
        self._buffer_time = val

    @property
    def keep_buffer(self):
        return self._keep_buffer

    @keep_buffer.setter
    def keep_buffer(self, val):
        self._keep_buffer = val

        
    def __compute_time_series_length(self):

        # translate back to dur and offset
        dur = self.end_time - self.start_time
        offset = self.start_time
        buf = self.buffer_time


        # set event durations from rate
        # get the samplesize
        # SHOULD NOT WE CALL IT SAMPLE_INTERVAL???
        samplesize = 1./self.samplerate

        # get the number of buffer samples
        buf_samp = int(np.ceil(buf/samplesize))

        # calculate the offset samples that contains the desired offset
        offset_samp = int(np.ceil((np.abs(offset)-samplesize*.5)/samplesize)*
                          np.sign(offset))

        # finally get the duration necessary to cover the desired span
        #dur_samp = int(np.ceil((dur - samplesize*.5)/samplesize))
        dur_samp = (int(np.ceil((dur+offset - samplesize*.5)/samplesize)) -
                    offset_samp + 1)

        # add in the buffer
        dur_samp += 2*buf_samp
        offset_samp -= buf_samp

        return dur_samp

    # def read(self,channels,start_time,end_time,buffer_time=0.0,keep_buffer=True):
    def read(self,channels):
        evs = self.__events

        raw_bin_wrappers = self.__create_bin_readers()

        # we need to create rawbinwrappers first to figure out sample rate before calling __compute_time_series_length()
        time_series_length = self.__compute_time_series_length()

        time_series_data = np.empty((len(channels),len(evs),time_series_length),
                             dtype=np.float)*np.nan




        usources = np.unique(raw_bin_wrappers)

        ordered_indices = np.arange(len(evs))

        event_indices_list = []

        events = []

        newdat_list = []

        eventdata = None
        for s,src in enumerate(usources):
            # get the eventOffsets from that source
            ind = np.atleast_1d(raw_bin_wrappers==src)

            event_indices_list.append(ordered_indices[ind])

            # events.offsets



            # if verbose:
            #     if not s%10:
            #         print 'Reading event %d'%s
            if len(ind) == 1:
                event_offsets=evs['eegoffset']
                events.append(evs)
            else:
                event_offsets = evs[ind]['eegoffset']
                events.append(evs[ind])

            print event_offsets
            #print "Loading %d events from %s" % (ind.sum(),src)
            # get the timeseries for those events
            newdat = src.get_event_data_xray(channels,
                                        event_offsets,
                                        self.start_time,
                                        self.end_time,
                                        self.buffer_time,
                                        resampled_rate=None,
                                        filt_freq=None,
                                        filt_type=None,
                                        filt_order=None,
                                        keep_buffer=self.keep_buffer,
                                        loop_axis=None,
                                        num_mp_procs=0,
                                        eoffset='eegoffset',
                                        eoffset_in_time=False)

            newdat_list.append(newdat)


        event_indices_array = np.hstack(event_indices_list)

        event_indices_restore_sort_order_array = event_indices_array.argsort()



        start_extend_time = time.time()
        #new code
        eventdata = xray.concat(newdat_list,dim='events')
        end_extend_time = time.time()


        # concatenate (must eventually check that dims match)
        # ORIGINAL CODE
        tdim = eventdata['time']
        cdim = eventdata['channels']
        # srate = eventdata.samplerate
        srate = eventdata.attrs['samplerate']
        events = np.concatenate(events).view(Events)

        eventdata_xray = xray.DataArray(eventdata.values, coords=[cdim,events,tdim], dims=['channels','events','time'])


        eventdata_xray = eventdata_xray[:,event_indices_restore_sort_order_array,:] #### RESTORE THIS



        self.__time_series = eventdata_xray





    def get_output(self):
        return self.__time_series

    def set_output(self,evs):
        pass


        # eventdata = TimeSeries(eventdata,
        #                        'time', srate,
        #                        dims=[cdim,Dim(events,'events'),tdim])
        # new code - older version
        # eventdata = newdat_list[0]
        #
        # eventdata = eventdata.extend(newdat_list[1:],axis=1)
