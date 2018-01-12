import numpy as np
from xarray import DataArray
from ptsa.data.common import TypeValTuple, PropertiedObject
from ptsa.data.readers import BaseReader
from ptsa import six


class BaseRawReader(PropertiedObject, BaseReader):
    """
    Object that knows how to read EEG files
    """
    _descriptors = [
        TypeValTuple('dataroot', six.string_types, ''),
        TypeValTuple('channels', np.ndarray, np.array([], dtype='|S3')),
        TypeValTuple('start_offsets', np.ndarray, np.array([0], dtype=np.int)),
        TypeValTuple('read_size', int, -1),
    ]

    channel_name = 'channels'

    def __init__(self, **kwds):
        """
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
        """
        self.init_attrs(kwds)
        self.params_dict = {'gain':1.0,}

    def read(self):
        """

        :return: DataArray objects populated with data read from eeg files. The size of the output is
        number of channels x number of start offsets x number of time series points
        The corresponding DataArray axes are: 'channels', 'start_offsets', 'offsets'

        """

        eventdata, read_ok_mask = self.read_file(self.dataroot,self.channels,self.start_offsets,self.read_size)
        # multiply by the gain
        eventdata *= self.params_dict['gain']

        eventdata = DataArray(eventdata,
                              dims=[self.channel_name, 'start_offsets', 'offsets'],
                              coords={
                                  self.channel_name: self.channels,
                                  'start_offsets': self.start_offsets.copy(),
                                  'offsets': np.arange(self.read_size),
                                  'samplerate': self.params_dict['samplerate']

                              }
                              )

        from copy import deepcopy
        eventdata.attrs = deepcopy(self.params_dict)

        return eventdata, read_ok_mask
    
    def read_file(self,filename,channels,start_offsets=np.array([0]),read_size=-1):
        """
        Reads raw data from binary files into a numpy array of shape (len(channels),len(start_offsets), read_size).
         For each channel and offset, indicates whether the data at that offset on that channel could be read successfully.

        :param filename: The name of the file to read
        :param channels: The channels to read from the file
        :param start_offsets: The indices in the array to start reading at
        :param read_size: The number of samples to read at each offset.
        :return: event_data: The EEG data corresponding to each offset
        :return: read_ok_mask: Boolean mask indicating whether each offset was read successfully.
        """
        raise NotImplementedError