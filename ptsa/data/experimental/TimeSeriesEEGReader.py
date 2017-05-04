import time

import numpy as np
import xarray as xr

from ptsa.data.RawBinWrapperXray import RawBinWrapperXray
from ptsa.data.TimeSeriesX import TimeSeriesX
from ptsa.data.common import TypeValTuple, PropertiedObject
from ptsa.data.events import Events


class TimeSeriesEEGReader(PropertiedObject):
    _descriptors = [
        TypeValTuple('samplerate', float, -1.0),
        TypeValTuple('keep_buffer', bool, True),
        TypeValTuple('buffer_time', float, 0.0),
        TypeValTuple('start_time', float, 0.0),
        TypeValTuple('end_time', float, 0.0),
        TypeValTuple('events', np.recarray, np.recarray((0,), dtype=[('x', int)])),
    ]

    def __init__(self,**kwds):

        self.init_attrs(kwds)

    def __create_bin_readers(self):
        evs = self.events
        eegfiles = np.unique(evs.eegfile)
        raw_bin_wrappers = []
        original_eeg_files = []

        for eegfile in eegfiles:
            events_with_matched_eegfile = evs[evs.eegfile == eegfile]
            ev_with_matched_eegfile = events_with_matched_eegfile[0]
            try:
                # eeg_file_path = join(self.data_dir_prefix, str(pathlib.Path(str(ev_with_matched_eegfile.eegfile)).parts[1:]))
                # raw_bin_wrappers.append(RawBinWrapperXray(eeg_file_path))

                eeg_file_path = ev_with_matched_eegfile.eegfile

                raw_bin_wrappers.append(RawBinWrapperXray(eeg_file_path))

                original_eeg_files.append(eegfile)

                inds = np.where(evs.eegfile == eegfile)[0]

                if self.samplerate < 0.0:
                    data_params = raw_bin_wrappers[-1]._get_params(eeg_file_path)

                    self.samplerate = data_params['samplerate']

            except TypeError:
                print('skipping event with eegfile=',evs.eegfile)
                pass

        raw_bin_wrappers = np.array(raw_bin_wrappers, dtype=np.dtype(RawBinWrapperXray))

        return raw_bin_wrappers, original_eeg_files

    def get_number_of_samples_for_interval(self,time_interval):
        return int(np.ceil(time_interval*self.samplerate))

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

    def read(self,channels):
        evs = self.events

        raw_bin_wrappers, original_eeg_files = self.__create_bin_readers()

        # we need to create rawbinwrappers first to figure out sample rate before calling __compute_time_series_length()
        time_series_length = self.__compute_time_series_length()

        time_series_data = np.empty((len(channels),len(evs),time_series_length),
                             dtype=np.float)*np.nan

        ordered_indices = np.arange(len(evs))
        event_indices_list = []
        events = []
        newdat_list = []
        eventdata = None

        for s,(src,eegfile) in enumerate(zip(raw_bin_wrappers,original_eeg_files)):
            ind = np.atleast_1d( evs.eegfile == eegfile)

            event_indices_list.append(ordered_indices[ind])

            if len(ind) == 1:
                event_offsets=evs['eegoffset']
                events.append(evs)
            else:
                event_offsets = evs[ind]['eegoffset']
                events.append(evs[ind])

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
        eventdata = xr.concat(newdat_list, dim='events')
        end_extend_time = time.time()

        # concatenate (must eventually check that dims match)
        # ORIGINAL CODE
        tdim = eventdata['time']
        cdim = eventdata['channels']
        # srate = eventdata.samplerate
        srate = eventdata.attrs['samplerate']
        events = np.concatenate(events).view(Events)

        eventdata_xray = xr.DataArray(eventdata.values, coords=[cdim, events, tdim], dims=['channels', 'events', 'time'])
        eventdata_xray.attrs['samplerate'] = eventdata.attrs['samplerate']
        eventdata_xray = eventdata_xray[:,event_indices_restore_sort_order_array,:] #### RESTORE THIS

        if not self.keep_buffer:
            # trimming buffer data samples
            number_of_buffer_samples =  self.get_number_of_samples_for_interval(self.buffer_time)
            if number_of_buffer_samples > 0:
                eventdata_xray = eventdata_xray[:,:,number_of_buffer_samples:-number_of_buffer_samples]

        return TimeSeriesX(eventdata_xray)

    def read_all(self,channels, start_offset,  end_offset, buffer):
        evs = self.events

        raw_bin_wrappers, original_eeg_files = self.__create_bin_readers()

        # we need to create rawbinwrappers first to figure out sample rate before calling __compute_time_series_length()
        time_series_length = self.__compute_time_series_length()

        time_series_data = np.empty((len(channels),len(evs),time_series_length),
                             dtype=np.float)*np.nan

        events = []

        newdat_list = []

        # for s,src in enumerate(usources):
        for s,(src,eegfile) in enumerate(zip(raw_bin_wrappers,original_eeg_files)):
            ind = np.atleast_1d( evs.eegfile == eegfile)

            if len(ind) == 1:
                events.append(evs[0])
            else:
                events.append(evs[ind])

            # print event_offsets
            #print "Loading %d events from %s" % (ind.sum(),src)
            # get the timeseries for those events
            newdat = src.get_event_data_xray_simple(channels=channels,events=events,
                                                    start_offset=start_offset,end_offset=end_offset,buffer=buffer)

            newdat_list.append(newdat)

        start_extend_time = time.time()
        #new code
        eventdata = xr.concat(newdat_list, dim='events')
        end_extend_time = time.time()

        # concatenate (must eventually check that dims match)
        # ORIGINAL CODE
        tdim = eventdata['time']
        cdim = eventdata['channels']
        # srate = eventdata.samplerate
        srate = eventdata.attrs['samplerate']

        eventdata_xray = eventdata

        if not self.keep_buffer:
            # trimming buffer data samples
            number_of_buffer_samples =  self.get_number_of_samples_for_interval(self.buffer_time)
            if number_of_buffer_samples > 0:
                eventdata_xray = eventdata_xray[:,:,number_of_buffer_samples:-number_of_buffer_samples]

        return eventdata_xray
