from .BaseReader import BaseReader
from .BaseRawReader import BaseRawReader
import numpy as np
import tables
from xarray import DataArray

class H5EEGReader(BaseRawReader):

    def read(self):
        eegfile = tables.open_file(self.dataroot)
        timeseries = eegfile.root.eeg_timeseries
        ports = eegfile.root.ports
        channels_to_read = np.in1d(ports, self.channels.astype(int))
        if self.read_size < 0:
            if 'orient' in eegfile.root.attrs and eegfile.root.attrs['orient'] == 'row':
                eventdata = timeseries[:, channels_to_read].T
            else:
                eventdata = timeseries[channels_to_read, :]
            eegfile.close()
            return eventdata[:, None, :], np.ones((len(self.channels), 1)).astype(bool)

        else:
            eventdata = np.empty((len(self.channels, len(self.start_offsets), self.read_size)),
                                 dtype=np.float) * np.nan
            read_ok_mask = np.ones((len(self.channels), len(self.start_offsets))).astype(bool)
            for i, start_offset in enumerate(self.start_offsets):
                if 'by_row' in eegfile.root.attrs and eegfile.root.attrs['by_row'] == True:
                    data = timeseries[start_offset:start_offset + self.read_size, channels_to_read].T
                else:
                    data = timeseries[channels_to_read, start_offset:start_offset + self.read_size]
                if data.shape[-1] == self.read_size:
                    eventdata[:, i, :] = data
                else:
                    print(
                        'Cannot read full chunk of data for offset ' + str(start_offset) +
                        'End of read interval  is outside the bounds of file ' + self.dataroot)
                    read_ok_mask[:, i] = False
            eegfile.close()


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



