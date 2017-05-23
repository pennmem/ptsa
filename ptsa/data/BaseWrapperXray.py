import numpy as np
from xarray import DataArray

from .basewrapper import BaseWrapper


class BaseWrapperXray(BaseWrapper):
    def get_event_data_xray(self, channels, events,
                            start_time, end_time, buffer_time=0.0,
                            resampled_rate=None,
                            filt_freq=None, filt_type='stop', filt_order=4,
                            keep_buffer=False,
                            loop_axis=None, num_mp_procs=0, eoffset='eoffset',
                            eoffset_in_time=True):
        """
        Return an TimeSeries containing data for the specified channel
        in the form [events,duration].

        Parameters
        ----------
        channels: {int} or {dict}
            Channels from which to load data.
        events: {array_like} or {recarray}
            Array/list of event offsets (in time or samples as
            specified by eoffset_in_time; in time by default) into
            the data, specifying each event onset time.
        start_time: {float}
            Start of epoch to retrieve (in time-unit of the data).
        end_time: {float}
            End of epoch to retrieve (in time-unit of the data).
        buffer_time: {float},optional
            Extra buffer to add on either side of the event in order
            to avoid edge effects when filtering (in time unit of the
            data).
        resampled_rate: {float},optional
            New samplerate to resample the data to after loading.
        filt_freq: {array_like},optional
            The range of frequencies to filter (depends on the filter
            type.)
        filt_type = {scipy.signal.band_dict.keys()},optional
            Filter type.
        filt_order = {int},optional
            The order of the filter.
        keep_buffer: {boolean},optional
            Whether to keep the buffer when returning the data.
        eoffset_in_time: {boolean},optional
            If True, the unit of the event offsets is taken to be
            time (unit of the data), otherwise samples.
        """

        # translate back to dur and offset
        dur = end_time - start_time
        offset = start_time
        buf = buffer_time

        # get the event offsets
        if ((not (hasattr(events, 'dtype') or hasattr(events, 'columns'))) or
                (hasattr(events, 'dtype') and events.dtype.names is None)):
            # they just passed in a list
            event_offsets = events
        elif ((hasattr(events, 'dtype') and (eoffset in events.dtype.names)) or
                  (hasattr(events, 'columns') and (eoffset in events.columns))):
            event_offsets = events[eoffset]
        else:
            raise ValueError(eoffset + ' must be a valid fieldname ' +
                             'specifying the offset for the data.')

        # Sanity checks:
        if (dur < 0):
            raise ValueError('Duration must not be negative! ' +
                             'Specified duration: ' + str(dur))
        if (np.min(event_offsets) < 0):
            raise ValueError('Event offsets must not be negative!')

        # make sure the events are an actual array:
        event_offsets = np.asarray(event_offsets)
        if eoffset_in_time:
            # convert to samples
            event_offsets = np.atleast_1d(np.int64(
                np.round(event_offsets * self.samplerate)))

        # set event durations from rate
        # get the samplesize
        samplesize = 1. / self.samplerate

        # get the number of buffer samples
        buf_samp = int(np.ceil(buf / samplesize))

        # calculate the offset samples that contains the desired offset
        offset_samp = int(np.ceil((np.abs(offset) - samplesize * .5) / samplesize) *
                          np.sign(offset))

        # finally get the duration necessary to cover the desired span
        # dur_samp = int(np.ceil((dur - samplesize*.5)/samplesize))
        dur_samp = (int(np.ceil((dur + offset - samplesize * .5) / samplesize)) -
                    offset_samp + 1)

        # add in the buffer
        dur_samp += 2 * buf_samp
        offset_samp -= buf_samp

        # check that we have all the data we need before every event:
        if (np.min(event_offsets + offset_samp) < 0):
            bad_evs = ((event_offsets + offset_samp) < 0)
            raise ValueError('The specified values for offset and buffer ' +
                             'require more data than is available before ' +
                             str(np.sum(bad_evs)) + ' of all ' +
                             str(len(bad_evs)) + ' events.')

        # process the channels
        if isinstance(channels, dict):
            # turn into indices
            ch_info = self.channels
            key = list(channels.keys())[0]
            channels = [np.nonzero(ch_info[key] == c)[0][0] for c in channels[key]]
        elif isinstance(channels, str):
            # find that channel by name
            channels = np.nonzero(self.channels['name'] == channels)[0][0]
        if channels is None or len(np.atleast_1d(channels)) == 0:
            channels = np.arange(self.nchannels)
        channels = np.atleast_1d(channels)
        channels.sort()

        # load the timeseries (this must be implemented by subclasses)
        eventdata = self._load_data(channels, event_offsets, dur_samp, offset_samp)

        # calc the time range
        # get the samplesize
        samp_start = offset_samp * samplesize
        samp_end = samp_start + (dur_samp - 1) * samplesize
        time_range = np.linspace(samp_start, samp_end, dur_samp)

        # when channels is and array of channels labels i.e. strings like  '002','003',...
        # we need to use xray arrays to do fancy indexing

        self.channels_xray = DataArray(self.channels.number, coords=[self.channels.name], dims=['name'])

        if channels.dtype.char == 'S':

            self.channels_xray = self.channels_xray.loc[channels]

        else:

            self.channels_xray = self.channels_xray[channels]

        # ORIGINAL CODE
        # self.channels_xray = np.rec.fromarrays([self.channels_xray.values, self.channels_xray.coords['name'].values],
        #                                        names='number,name')


        self.channels_xray = self.channels_xray.coords['name'].values

        eventdata = DataArray(eventdata, coords=[self.channels_xray, events, time_range],
                              dims=['channels', 'events', 'time'])
        eventdata.attrs['samplerate'] = self.samplerate

        return eventdata

    # def get_event_data_xray_simple(self, channels, events, start_offset, end_offset, buffer=0):
    #
    #     # process the channels
    #     if isinstance(channels, dict):
    #         # turn into indices
    #         ch_info = self.channels
    #         key = channels.keys()[0]
    #         channels = [np.nonzero(ch_info[key] == c)[0][0] for c in channels[key]]
    #     elif isinstance(channels, str):
    #         # find that channel by name
    #         channels = np.nonzero(self.channels['name'] == channels)[0][0]
    #     if channels is None or len(np.atleast_1d(channels)) == 0:
    #         channels = np.arange(self.nchannels)
    #     channels = np.atleast_1d(channels)
    #     channels.sort()
    #
    #     # load the timeseries (this must be implemented by subclasses)
    #
    #     event_offsets = np.array(start_offset, ndmin=1)
    #     dur_samp = end_offset - start_offset + 2 * buffer
    #     offset_samp = -buffer
    #
    #     # eventdata = self._load_data(channels,event_offsets,dur_samp,offset_samp)
    #     eventdata = self._load_all_data(channels, start_offset - buffer)
    #
    #
    #     # calc the time range
    #     number_of_time_points = eventdata.shape[2] # third axis is time exis in event data returned from _load_all_data
    #     # get the samplesize
    #
    #     samplesize = 1.0 / self.samplerate
    #     samp_start = (start_offset - buffer) * samplesize
    #     samp_end = samp_start + number_of_time_points * samplesize
    #
    #     time_range = np.linspace(samp_start, samp_end, number_of_time_points)
    #     eegoffset = np.arange(start_offset - buffer, start_offset - buffer+number_of_time_points)
    #
    #     time_axis = np.rec.fromarrays([time_range, eegoffset], names='time,eegoffset')
    #
    #
    #
    #     # when channels is and array of channels labels i.e. strings like  '002','003',...
    #     # we need to use xray arrays to do fancy indexing
    #
    #     self.channels_xray = DataArray(self.channels.number, coords=[self.channels.name], dims=['name'])
    #
    #     if channels.dtype.char == 'S':
    #
    #         self.channels_xray = self.channels_xray.loc[channels]
    #
    #     else:
    #
    #         self.channels_xray = self.channels_xray[channels]
    #
    #     self.channels_xray = np.rec.fromarrays([self.channels_xray.values, self.channels_xray.coords['name'].values],
    #                                            names='number,name')
    #
    #
    #     # eventdata = DataArray(eventdata,coords=[self.channels_xray,np.arange(len(events)),time_range],dims=['channels','events','time'])
    #     eventdata = DataArray(eventdata, coords=[self.channels_xray, np.arange(len(events)), time_axis],
    #                           dims=['channels', 'events', 'time'])
    #     eventdata.attrs['samplerate'] = self.samplerate
    #
    #     return eventdata

    def get_event_data_xray_simple(self,channels,events,start_offset,end_offset,buffer=0):


            # process the channels
        if isinstance(channels, dict):
            # turn into indices
            ch_info = self.channels
            key = list(channels.keys())[0]
            channels = [np.nonzero(ch_info[key]==c)[0][0] for c in channels[key]]
        elif isinstance(channels, str):
            # find that channel by name
            channels = np.nonzero(self.channels['name']==channels)[0][0]
        if channels is None or len(np.atleast_1d(channels))==0:
            channels = np.arange(self.nchannels)
        channels = np.atleast_1d(channels)
        channels.sort()

        # load the timeseries (this must be implemented by subclasses)

        event_offsets = np.array(start_offset,ndmin=1)
        dur_samp = end_offset-start_offset + 2*buffer
        offset_samp = -buffer

        eventdata = self._load_data(channels,event_offsets,dur_samp,offset_samp)
        # eventdata = self._load_all_data(channels,start_offset-buffer)

        # calc the time range
        # get the samplesize
        samplesize = 1.0/self.samplerate
        samp_start = (start_offset-buffer)*samplesize
        samp_end =   (end_offset+buffer)*samplesize

        time_range = np.linspace(samp_start,samp_end,dur_samp)
        eegoffset = np.arange(start_offset-buffer,  end_offset+buffer)


        time_axis = np.rec.fromarrays([time_range,eegoffset],names='time,eegoffset')



        # when channels is and array of channels labels i.e. strings like  '002','003',...
        # we need to use xray arrays to do fancy indexing

        self.channels_xray = DataArray(self.channels.number,coords=[self.channels.name],dims=['name'])

        if channels.dtype.char=='S':

            self.channels_xray = self.channels_xray.loc[channels]

        else:

            self.channels_xray = self.channels_xray[channels]

        self.channels_xray=np.rec.fromarrays([self.channels_xray.values,self.channels_xray.coords['name'].values],names='number,name')


        # eventdata = DataArray(eventdata,coords=[self.channels_xray,np.arange(len(events)),time_range],dims=['channels','events','time'])
        eventdata = DataArray(eventdata,coords=[self.channels_xray,np.arange(len(events)),time_axis],dims=['channels','events','time'])
        eventdata.attrs['samplerate'] = self.samplerate

        return eventdata
