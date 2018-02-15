import numpy as np
from xarray import DataArray
from ptsa.data.common import TypeValTuple, PropertiedObject
from ptsa.data.readers.base import BaseReader
from ptsa.data.readers.params import ParamsReader
from ptsa import six
from abc import abstractmethod


class BaseRawReader(PropertiedObject, BaseReader):
    """
    Abstract base class for objects that know how to read binary EEG files.
    Classes inheriting from BaseRawReader should do the following
    * Override :meth:read_file
    * Set self.params_dict['gain'] and self.params_dict['samplerate'] as appropriate,
      either in self.read_file or in the constructor
    * Make sure that self.channel_name as appropriate for the referencing scheme used
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

        :param channels {ndarray} - array of channels (array of strings) that should be read
        :param start_offsets {ndarray} -  array of ints with read offsets
        :param read_size {int} - size of the read chunk. If -1 the entire file is read
        --------------------------------------
        :return:None

        """

        self.init_attrs(kwds)
        if isinstance(self.dataroot, six.binary_type):
            self.dataroot = self.dataroot.decode()
        self.params_dict = {'gain':1,'samplerate':self.samplerate()}

    def read(self):
        """Read EEG data.

        Returns
        -------
        event_data : DataArray
            Populated with data read from eeg files. The size of the output is
            number of channels * number of start offsets * number of time series
            points. The corresponding DataArray axes are: 'channels',
            'start_offsets', 'offsets'
        read_ok_mask : np.ndarray
            Mask of chunks that were properly read.

        Notes
        -----
        This method should *not* be overridden by subclasses. Instead, override
        the :meth:`read_file` method to implement new file types (see for
        example the HDF5 reader).

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


    @abstractmethod
    def samplerate(self):
        """
        Get the samplerate for the EEG recording ```filename```.
        The default behavior is to read a separate params file that holds the samplerate.
        :param filename: The EEG recording whose sample rate we want
        :return: {float} The sampling rate of the recording, in Hz
        """
        params = ParamsReader(dataroot=self.dataroot).read()
        return params['samplerate']

    @abstractmethod
    def read_file(self,filename,channels,start_offsets=np.array([0]),read_size=-1):
        """
        Reads raw data from binary files into a numpy array of shape (len(channels),len(start_offsets), read_size).
         For each channel and offset, indicates whether the data at that offset on that channel could be read successfully.

         For each channel and offset, indicates whether the data at that offset
         on that channel could be read successfully.

         Parameters
         ----------
         filename : str
            The name of the file to read
        channels : list
            The channels to read from the file
        start_offsets : np.ndarray
            The indices in the array to start reading at
        read_size : int
            The number of samples to read at each offset.

        Returns
        -------
        eventdata : np.ndarray
            The EEG data corresponding to each offset
        read_ok_mask : np.ndarray
            Boolean mask indicating whether each offset was read successfully.

        """
        raise NotImplementedError
