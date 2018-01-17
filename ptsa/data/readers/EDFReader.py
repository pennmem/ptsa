from . import edf
from . import BaseRawReader
import numpy as np

class EDFReader(BaseRawReader):
    """Class for reading ~raw~ EEG data stored in EDF format.
    """

    def __init__(self,**kwargs):
        """
                Constructor
        Allowed keywords are:
        -------------------------------------
        :param dataroot {str}: The name of the EEG file

        :param channels {list} - list of channel numbers that should be read
        :param start_offsets {ndarray} -  array of ints with read offsets
        :param read_size {int} - size of the read chunk. If -1 the entire file is read
        --------------------------------------
        :return:None
        """


        self.init_attrs(kwargs)

        self.params_dict = {'gain':1.0,}


    def read_file(self,filename,channels,start_offsets=np.array([0]),read_size=-1):
        """
        Overloads BaseRawReader.read_file().
        :param filename:
        :param channels:
        :param start_offsets:
        :param read_size:
        :return:
        """
        self.params_dict['samplerate'] = edf.read_samplerate(filename,1)
        if len(channels)==0:
            channels = np.arange(edf.read_number_of_samples(filename,1))
            self.channels = np.array(['%.03d'%c for c in channels])
        if read_size<0:
            self.read_size =read_size = int(edf.read_number_of_samples(filename,1))
            start_offsets = np.array([0])
        data = np.zeros(shape=(len(channels),len(start_offsets),read_size))*np.nan
        read_ok_mask = np.ones(shape=(len(channels),len(start_offsets)),dtype=bool)
        for i,channel in enumerate(channels):
            for j,offset in enumerate(start_offsets):
                try:
                    data[i,j,:] = edf.read_samples(filename,int(channel),offset,read_size)
                except Exception:
                    read_ok_mask[i,j] = 0
        return (data,read_ok_mask)
