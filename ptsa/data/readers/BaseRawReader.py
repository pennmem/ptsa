from ptsa.data.common import TypeValTuple, PropertiedObject
import numpy as np
import struct
from collections import namedtuple
import os
import xray

class BaseRawReader(PropertiedObject):
    _descriptors = [
        TypeValTuple('dataroot', str, ''),
        TypeValTuple('channels', list, []),
        TypeValTuple('start_offsets', np.ndarray, np.ndarray([], dtype=np.int)),
        TypeValTuple('read_size', int, -1),
    ]

    def __init__(self, **kwds):

        self.init_attrs(kwds)

        from ptsa.data.readers import ParamsReader

        FileFormat = namedtuple('FileFormat', ['data_size', 'format_string'])
        self.file_format_dict = {
            'single': FileFormat(data_size=4, format_string='f'),
            'short': FileFormat(data_size=2, format_string='h'),
            'int16': FileFormat(data_size=2, format_string='h'),
            'double': FileFormat(data_size=8, format_string='d'),
        }

        self.file_format = self.file_format_dict['int16']

        p_reader = ParamsReader(dataroot=self.dataroot)
        self.params_dict = p_reader.read()

        try:
            format_name = self.params_dict['format']
            try:
                self.file_format = self.file_format_dict[format_name]
            except KeyError:
                raise RuntimeError('Unsupported format: %s. Allowed format names are: %s' % (
                format_name, self.file_format_dict.keys()))
        except KeyError:
            print 'Could not find data format definition in the params file. Wwilll read te file assuming' \
                  ' data format is int16'

    def read(self):
        # allocate for data
        eventdata = np.empty((len(self.channels), len(self.start_offsets), self.read_size),
                             dtype=np.float) * np.nan

        # loop over channels
        for c, channel in enumerate(self.channels):

            eegfname = self._dataroot + '.' + channel

            # eegfname = '{}.{:0>3}'.format(self._dataroot,channel)
            if os.path.isfile(eegfname):
                efile = open(eegfname, 'rb')
            else:
                raise IOError(
                        'EEG file not found: ' + eegfname)

            # loop over start offsets
            for e, start_offset in enumerate(self.start_offsets):
                # seek to the position in the file
                efile.seek(self.file_format.data_size * start_offset, 0)

                # read the data
                data = efile.read(int(self.file_format.data_size * self.read_size))

                # convert from string to array based on the format
                # hard codes little endian
                data = np.array(struct.unpack(
                        '<' + str(len(data) / self.file_format.data_size) +
                        self.file_format.format_string, data))

                # make sure we got some data
                if len(data) < self.read_size:
                    raise IOError(
                            'Cannot read full chunk of data for offset ' + str(start_offset) +
                            'End of read interval  is outside the bounds of file ' + str(eegfname))

                # append it to the events
                eventdata[c, e, :] = data

        # multiply by the gain
        eventdata *= self.params_dict['gain']

        eventdata = xray.DataArray(eventdata,dims=['channels','start_offsets','offsets'])
        eventdata['start_offsets'] = self.start_offsets.copy()

        from copy import deepcopy
        eventdata.attrs = deepcopy(self.params_dict)

        return eventdata


if __name__ == '__main__':

    e_path = '/Users/m/data/events/RAM_FR1/R1060M_events.mat'
    from ptsa.data.readers import BaseEventReader

    base_e_reader = BaseEventReader(event_file=e_path, eliminate_events_with_no_eeg=True, use_ptsa_events_class=False)

    base_events = base_e_reader.read()

    base_events = base_events[base_events.type == 'WORD']

    # selecting only one session
    base_events = base_events[base_events.eegfile == base_events[0].eegfile]

    from ptsa.data.readers.TalReader import TalReader
    tal_path = '/Users/m/data/eeg/R1060M/tal/R1060M_talLocs_database_bipol.mat'
    tal_reader = TalReader(tal_filename=tal_path)
    monopolar_channels = tal_reader.get_monopolar_channels()
    bipolar_pairs = tal_reader.get_bipolar_pairs()

    print 'bipolar_pairs=', bipolar_pairs

    from ptsa.data.readers.TimeSeriesEEGReader import TimeSeriesEEGReader

    time_series_reader = TimeSeriesEEGReader(events=base_events, start_time=0.0,
                                             end_time=1.6, buffer_time=1.0, keep_buffer=True)

    base_eegs = time_series_reader.read(channels=monopolar_channels)





    # dataroot = '/Users/m/data/eeg/R1060M/eeg.noreref/R1060M_01Aug15_0805'

    dataroot = base_events[0].eegfile

    brr = BaseRawReader(dataroot=dataroot, channels=monopolar_channels, start_offsets=base_events.eegoffset-500,
                        read_size=1801)
    arr = brr.read()

    print arr




