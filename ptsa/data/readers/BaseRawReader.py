import os
import struct
from collections import namedtuple

import numpy as np

from ptsa.data.common import TypeValTuple, PropertiedObject
from ptsa.data.common.xr import DataArray
from ptsa.data.readers import BaseReader

class BaseRawReader(PropertiedObject,BaseReader):
    '''
    Object that knows how to read binary eeg files
    '''
    _descriptors = [
        TypeValTuple('dataroot', str, ''),
        # TypeValTuple('channels', list, []),
        TypeValTuple('channels', np.ndarray, np.array([],dtype='|S3')),
        TypeValTuple('start_offsets', np.ndarray, np.array([0], dtype=np.int)),
        TypeValTuple('read_size', int, -1),
    ]

    def __init__(self, **kwds):
        '''
        Constructor
        :param kwds:allowed values are:
        -------------------------------------
        :param dataroot {str} -  core name of the eegfile file (i.e. full path except extension e.g. '.002').
        Normally this is eegfile field from events record

        :param channels {list} - list of channels (list of strings) that should be read
        :param start_offsets {ndarray} -  array of ints with read offsets
        :param read_size {int} - size of the read chunk. If -1 the entire file is read
        --------------------------------------
        :return:None
        '''

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
            print 'Could not find data format definition in the params file. Will read te file assuming' \
                  ' data format is int16'

    def get_file_size(self):
        '''

        :return: {int} size of the files whose core name (dataroot) matches self.dataroot. Assumes ALL files with this
        dataroot are of the same length and uses first channel to determin the common file length
        '''
        eegfname = self.dataroot + '.' + self.channels[0]
        return os.path.getsize(eegfname)

    def read(self):
        '''

        :return: DataArray objects populated with data read from eeg files. The size of the output is
        number of channels x number of start offsets x number of time series points
        The corresponding DataArray axes are: 'channels', 'start_offsets', 'offsets'

        '''

        if self.read_size < 0:
            self.read_size = self.get_file_size() / self.file_format.data_size

        # allocate space for data
        eventdata = np.empty((len(self.channels), len(self.start_offsets), self.read_size),
                             dtype=np.float) * np.nan

        read_ok_mask = np.ones(shape=(len(self.channels),len(self.start_offsets)), dtype=np.bool)

        # loop over channels
        for c, channel in enumerate(self.channels):

            eegfname = self.dataroot + '.' + channel

            # eegfname = '{}.{:0>3}'.format(self._dataroot,channel)
            if os.path.isfile(eegfname):
                efile = open(eegfname, 'rb')
            else:
                raise IOError(
                    'EEG file not found: ' + eegfname)

            # loop over start offsets
            for e, start_offset in enumerate(self.start_offsets):
                # rejecting negative offset
                if start_offset<0:
                    read_ok_mask[c,e]=False
                    print('Cannot read from negative offset %d in file %s' % (start_offset,eegfname))
                    continue

                # seek to the position in the file
                efile.seek(self.file_format.data_size * start_offset, 0)

                # read the data
                data = efile.read(int(self.file_format.data_size * self.read_size))

                # convert from string to array based on the format
                # hard-codes little endian
                data = np.array(struct.unpack(
                    '<' + str(len(data) / self.file_format.data_size) +
                    self.file_format.format_string, data))

                # make sure we got some data
                if len(data) < self.read_size:
                    read_ok_mask[c,e]=False

                    print(
                        'Cannot read full chunk of data for offset ' + str(start_offset) +
                        'End of read interval  is outside the bounds of file ' + str(eegfname))
                else:
                    # append it to the eventdata
                    eventdata[c, e, :] = data

        # multiply by the gain
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

