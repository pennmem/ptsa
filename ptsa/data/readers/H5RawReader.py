from .BaseRawReader import BaseRawReader
import numpy as np
import tables
from xarray import DataArray

class H5EEGReader(BaseRawReader):

    def read(self):
        eventdata,read_ok_mask = self.read_h5file(self.dataroot,self.channels,self.start_offsets,self.read_size)

        eventdata *= self.params_dict['gain']

        eventdata = DataArray(eventdata,
                              dims=['channels', 'start_offsets', 'offsets'],
                              coords={
                                  'channels': self.channels,
                                  'start_offsets': self.start_offsets.copy(),
                                  'offsets': np.arange(self.read_size),
                                  'samplerate': self.params_dict['samplerate']
                              }
                              )

        from copy import deepcopy
        eventdata.attrs = deepcopy(self.params_dict)

        return eventdata, read_ok_mask



    @staticmethod
    def read_h5file(filename,channels,start_offsets,read_size):
        eegfile = tables.open_file(filename)
        timeseries = eegfile.root.eeg_timeseries
        ports = eegfile.root.ports
        channels_to_read = np.in1d(ports, channels.astype(int))
        if read_size < 0:
            if 'orient' in timeseries.attrs and timeseries.attrs['orient'] == 'row':
                eventdata = timeseries[:, channels_to_read].T
            else:
                eventdata = timeseries[channels_to_read, :]
            eegfile.close()
            return eventdata[:, None, :], np.ones((len(channels), 1)).astype(bool)

        else:
            eventdata = np.empty((len(channels, len(start_offsets), read_size)),
                                 dtype=np.float) * np.nan
            read_ok_mask = np.ones((len(channels), len(start_offsets))).astype(bool)
            for i, start_offset in enumerate(start_offsets):
                if 'orient' in timeseries.attrs and timeseries.attrs['row'] == 'row':
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
            eegfile.close()

        return eventdata, read_ok_mask
