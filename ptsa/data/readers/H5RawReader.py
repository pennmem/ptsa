from .BaseRawReader import BaseRawReader
import numpy as np
import tables
import os.path as osp

class H5RawReader(BaseRawReader):

    def __init__(self,**kwargs):
        dataroot,data_ext = osp.splitext(kwargs['dataroot'])
        assert data_ext=='.h5','Dataroot missing extension'
        kwargs['dataroot']=dataroot
        super(H5RawReader, self).__init__(**kwargs)
        self.dataroot+=data_ext


    def read_file(self,filename, channels, start_offsets=np.array([0]), read_size=-1):
        event_data,read_ok_mask = self.read_h5file(filename, channels, start_offsets, read_size)
        eegfile = tables.open_file(filename=filename)
        if 'bipolar_info' in eegfile.root:
            self.channels = np.array([eegfile.root.bipolar_info.ch0_label[:],eegfile.root.bipolar_info.ch1_label[:]],
                                    dtype=[('ch0',int),('ch1',int)])

            self.channel_name = 'bipolar_pairs'
        if self.read_size==-1:
            self.read_size = max(event_data.shape)
        return event_data,read_ok_mask

    @staticmethod
    def read_h5file(filename, channels, start_offsets=np.array([0]), read_size=-1):
        eegfile = tables.open_file(filename)
        timeseries = eegfile.root.timeseries
        ports = eegfile.root.ports
        channels_to_read = np.where(np.in1d(ports, channels.astype(int)))[0]
        if read_size < 0:
            if 'orient' in timeseries.attrs and timeseries.attrs['orient'] == 'row':
                eventdata = timeseries[:, channels_to_read].T
            else:
                eventdata = timeseries[channels_to_read, :]
            eegfile.close()
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
                            'End of read interval  is outside the bounds of file ' + filename)
                        read_ok_mask[:, i] = False
                except IndexError:
                    print(
                        'Cannot read full chunk of data for offset ' + str(start_offset) +
                        'End of read interval  is outside the bounds of file ' + filename)
                    read_ok_mask[:, i] = False

            eegfile.close()

        return eventdata,read_ok_mask,
