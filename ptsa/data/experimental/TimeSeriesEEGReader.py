__author__ = 'm'

import time

import numpy as np
import xray

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




        # usources = np.unique(raw_bin_wrappers)

        ordered_indices = np.arange(len(evs))

        event_indices_list = []

        events = []

        newdat_list = []

        eventdata = None
        # for s,src in enumerate(usources):
        for s,(src,eegfile) in enumerate(zip(raw_bin_wrappers,original_eeg_files)):
            ind = np.atleast_1d( evs.eegfile == eegfile)

            event_indices_list.append(ordered_indices[ind])

            # if verbose:
            #     if not s%10:
            #         print 'Reading event %d'%s
            if len(ind) == 1:
                event_offsets=evs['eegoffset']
                events.append(evs)
            else:
                event_offsets = evs[ind]['eegoffset']
                events.append(evs[ind])

            # print event_offsets
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
        eventdata = xray.concat(newdat_list,dim='events')
        end_extend_time = time.time()


        # concatenate (must eventually check that dims match)
        # ORIGINAL CODE
        tdim = eventdata['time']
        cdim = eventdata['channels']
        # srate = eventdata.samplerate
        srate = eventdata.attrs['samplerate']

        eventdata_xray = eventdata
        # eventdata_xray = xray.DataArray(np.squeeze(eventdata.values), coords=[cdim,tdim], dims=['channels','time'])
        # eventdata_xray.attrs['samplerate'] = eventdata.attrs['samplerate']


        if not self.keep_buffer:
            # trimming buffer data samples
            number_of_buffer_samples =  self.get_number_of_samples_for_interval(self.buffer_time)
            if number_of_buffer_samples > 0:
                eventdata_xray = eventdata_xray[:,:,number_of_buffer_samples:-number_of_buffer_samples]

        return eventdata_xray


if __name__=='__main__':
    event_range = range(0, 30, 1)
    e_path = '/Users/m/data/events/RAM_FR1/R1060M_events.mat'

    from ptsa.data.readers import BaseEventReader

    base_e_reader = BaseEventReader(event_file=e_path, eliminate_events_with_no_eeg=True, use_ptsa_events_class=False)

    base_e_reader.read()

    base_events = base_e_reader.get_output()

    base_events = base_events[base_events.type == 'WORD']

    # sorting names in the order in which they appear in the file
    eegfile_names =  np.unique(base_events.eegfile)
    eeg_file_names_sorter = np.zeros(len(eegfile_names), dtype=np.int)

    for i, eegfile_name in enumerate(eegfile_names):

        eeg_file_names_sorter[i] = np.where(base_events.eegfile==eegfile_name)[0][0]

    eeg_file_names_sorter = np.argsort(eeg_file_names_sorter)

    eegfile_names = eegfile_names [eeg_file_names_sorter]

    print(eegfile_names)


    base_events_0 = base_events[base_events.eegfile==eegfile_names[0]]


    print(base_events_0)

    master_event_0 = base_events_0[[0]] # using fancy indexing to force return of the array
    master_event__1 = base_events_0[[-1]] # using fancy indexing to force return of the array



    print('master_event_0=',master_event_0)
    print('master_event__1=',master_event__1)

    from ptsa.data.experimental.TimeSeriesEEGReader import TimeSeriesEEGReader

    time_series_reader = TimeSeriesEEGReader(events=master_event_0, start_time=0.0,
                                             end_time=1.6, buffer_time=1.0, keep_buffer=True)

    ts = time_series_reader.read_all(channels=['002', '003'],start_offset = master_event_0[0].eegoffset,
                                     end_offset = master_event__1[0].eegoffset, buffer=2000)



    print(ts)

    samplerate = ts.attrs['samplerate']
    ev_duration = 1.6
    buffer = 1.0


    eegoffset_time_array = ts['time'].values['eegoffset']

    ev_data_list = []
    for i, ev  in enumerate(base_events_0):
        print(ev.eegoffset)
        start_offset = ev.eegoffset-int(np.ceil(buffer*samplerate))
        end_offset = ev.eegoffset+int(np.ceil((ev_duration+buffer)*samplerate))
        print("start_offset,end_offset, size=",start_offset,end_offset,end_offset-start_offset)
        # eegoffset_time_array = ts['time'].values['eegoffset']
        selector_array = np.where( (eegoffset_time_array>=start_offset)& (eegoffset_time_array<end_offset))[0]

        event_time_axis = np.linspace(-1.0,2.6,len(selector_array))

        ev_array = ts[:,:,selector_array]

        ev_array['time']=event_time_axis
        ev_array['events']= [i]

        ev_data_list.append(ev_array)
        # ev_data_list.append(ts[:,:,selector_array].values)

        print(i)
        # print ev_array
        if i ==2:
            break


    eventdata = xray.concat(ev_data_list,dim='events')

    # eventdata =np.concatenate(ev_data_list,axis=1)

    # eventdata = xray.concat(ev_data_list,dim='events')


    print(eventdata)




    # eegoffset_time_array = ts['time'].values['eegoffset']
    #
    # ev_data_list = []
    # for i, ev  in enumerate(base_events_0):
    #     print ev.eegoffset
    #     start_offset = ev.eegoffset-int(np.ceil(buffer*samplerate))
    #     end_offset = ev.eegoffset+int(np.ceil((ev_duration+buffer)*samplerate))
    #     print "start_offset,end_offset, size=",start_offset,end_offset,end_offset-start_offset
    #     # eegoffset_time_array = ts['time'].values['eegoffset']
    #     selector_array = np.where( (eegoffset_time_array>=start_offset)& (eegoffset_time_array<end_offset))[0]
    #
    #     event_time_axis = np.linspace(-1.0,2.6,len(selector_array))
    #
    #     ev_array = ts[:,:,selector_array]
    #     ev_array['time']=event_time_axis
    #     ev_array['events']= [i]
    #
    #     ev_data_list.append(ev_array)
    #     # ev_data_list.append(ts[:,:,selector_array])
    #
    #     print i
    #     # print ev_array
    #     if i ==2:
    #         break
    #
    #
    # # eventdata = xray.concat(ev_data_list,dim='events')
    # eventdata = xray.concat(ev_data_list,dim='events')
    #
    #
    # print eventdata

