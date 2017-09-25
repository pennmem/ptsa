from .BaseRawReader import BaseRawReader
import numpy as np
import h5py
import os.path as osp



class H5RawReader(BaseRawReader):

    def __init__(self,**kwargs):
        _,data_ext = osp.splitext(kwargs['dataroot'])
        assert data_ext=='.h5','Dataroot missing extension'
        super(H5RawReader, self).__init__(**kwargs)



    def read_file(self,filename, channels, start_offsets=np.array([0]), read_size=-1):
        with h5py.File(self.dataroot,'r') as eegfile:
            if 'bipolar_info' in eegfile and ('monopolar_possible' in eegfile and eegfile['monopolar_possible'][:]==False):
                channel_mask = np.in1d(channels,eegfile['bipolar_info/ch0_label'])
                if not channel_mask.all():
                    raise IndexError('Channel[s] %s not in recording'%(
                        channels[~np.in1d(channels,eegfile['bipolar_info/ch0_label'][:])])
                                     )
                ch0 = eegfile['bipolar_info/ch0_label'][:]
                ch1 = eegfile['bipolar_info/ch1_label'][:]
                self.channels = np.array(zip(ch0[channel_mask],ch1[channel_mask]),
                                        dtype=[('ch0',int),('ch1',int)]).view(np.recarray)

                self.channel_name = 'bipolar_pairs'
            event_data,read_ok_mask = self.read_h5file(eegfile, channels if self.channel_name=='channels' else self.channels.ch0
                                                       , start_offsets, read_size)
            if self.read_size==-1:
                self.read_size = max(event_data.shape)
            return event_data,read_ok_mask

    @staticmethod
    def read_h5file(eegfile, channels, start_offsets=np.array([0]), read_size=-1):
        timeseries = eegfile['timeseries']
        ports = eegfile['ports']
        channels_to_read = np.where(np.in1d(ports, channels.astype(int)))[0]
        if read_size < 0:
            if 'orient' in timeseries.attrs and timeseries.attrs['orient'] == 'row':
                eventdata = timeseries[:, channels_to_read].T
            else:
                eventdata = timeseries[channels_to_read, :]
            return eventdata[:, None, :], np.ones((len(channels), 1)).astype(bool)

        else:
            eventdata = np.empty((len(channels), len(start_offsets), read_size),
                                 dtype=np.float) * np.nan
            read_ok_mask = np.ones((len(channels), len(start_offsets))).astype(bool)
            for i, start_offset in enumerate(start_offsets):
                try:
                    if 'orient' in timeseries.attrs and timeseries.attrs['orient'] == 'row':
                        data = timeseries[start_offset:start_offset + read_size, channels_to_read].T
                    else:
                        data = timeseries[channels_to_read, start_offset:start_offset + read_size]
                    if data.shape[-1] == read_size:
                        eventdata[:, i, :] = data
                    else:
                        print(
                            'Cannot read full chunk of data for offset ' + str(start_offset) +
                            'End of read interval  is outside the bounds of file ' + eegfile.name)
                        read_ok_mask[:, i] = False
                except IndexError:
                    print(
                        'Cannot read full chunk of data for offset ' + str(start_offset) +
                        'End of read interval  is outside the bounds of file ' + eegfile.name)
                    read_ok_mask[:, i] = False

            return eventdata,read_ok_mask,
