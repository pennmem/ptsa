from .raw import BaseRawReader
from collections import namedtuple
from .params import ParamsReader
import six
import warnings
import os.path as osp
import numpy as np
import struct

class BinaryRawReader(BaseRawReader):

    def __init__(self,**kwargs):
        super(BinaryRawReader, self).__init__(**kwargs)
        FileFormat = namedtuple('FileFormat', ['data_size', 'format_string'])
        self.file_format_dict = {
            'single': FileFormat(data_size=4, format_string='f'),
            'float32': FileFormat(data_size=4, format_string='f'),
            'short': FileFormat(data_size=2, format_string='h'),
            'int16': FileFormat(data_size=2, format_string='h'),
            'int32': FileFormat(data_size=4, format_string='i'),
            'double': FileFormat(data_size=8, format_string='d'),
            'float64': FileFormat(data_size=8, format_string='d')
        }

        self.file_format = self.file_format_dict['int16']
        if isinstance(self.dataroot, six.binary_type):
            self.dataroot = self.dataroot.decode()

        try:
            format_name = self.params_dict['format']
            try:
                self.file_format = self.file_format_dict[format_name]
            except KeyError:
                raise RuntimeError('Unsupported format: %s. Allowed format names are: %s' % (
                    format_name, list(self.file_format_dict.keys())))
        except KeyError:
            warnings.warn('Could not find data format definition in the params file. Will read the file assuming' \
                          ' data format is int16', RuntimeWarning)
        if np.issubdtype(self.channel_labels.dtype,np.integer):
            self.channel_labels = np.array(['{:03}'.format(c) for c in self.channel_labels])

    def get_file_size(self):
        """
        :return: {int} size of the files whose core name (dataroot) matches self.dataroot. Assumes ALL files with this
        dataroot are of the same length and uses first channel to determin the common file length
        """
        if isinstance(self.channel_labels[0], six.binary_type):
            ch = self.channel_labels[0].decode()
        else:
            ch = self.channel_labels[0]
        eegfname = self.dataroot + '.' + ch
        return osp.getsize(eegfname)

    def read_file(self,filename,channels,start_offsets=np.array([0]),read_size=-1):
        if read_size < 0:
            read_size = int(self.get_file_size() / self.file_format.data_size)
            self.read_size=read_size

        # allocate space for data
        eventdata = np.empty((len(channels), len(start_offsets), read_size),
                             dtype=np.float) * np.nan
        read_ok_mask = np.ones(shape=(len(channels), len(start_offsets)), dtype=np.bool)
        # loop over channels
        for c, channel in enumerate(channels):
            try:
                eegfname = filename + '.' + channel
            except TypeError:
                eegfname = filename + '.' + channel.decode()

            with open(eegfname, 'rb') as efile:
                # loop over start offsets
                for e, start_offset in enumerate(start_offsets):
                    # rejecting negative offset
                    if start_offset < 0:
                        read_ok_mask[c, e] = False
                        print(('Cannot read from negative offset %d in file %s' % (start_offset, eegfname)))
                        continue

                    # seek to the position in the file
                    efile.seek(self.file_format.data_size * start_offset, 0)

                    # read the data
                    data = efile.read(int(self.file_format.data_size * read_size))

                    # convert from string to array based on the format
                    # hard-codes little endian
                    fmt = '<' + str(int(len(data) / self.file_format.data_size)) + self.file_format.format_string
                    data = np.array(struct.unpack(fmt, data))

                    # make sure we got some data
                    if len(data) < read_size:
                        read_ok_mask[c, e] = False

                        print((
                            'Cannot read full chunk of data for offset ' + str(start_offset) +
                            'End of read interval  is outside the bounds of file ' + str(eegfname)))
                    else:
                        # append it to the eventdata
                        eventdata[c, e, :] = data

        return eventdata, read_ok_mask

