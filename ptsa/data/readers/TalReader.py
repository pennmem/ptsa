__author__ = 'm'

from os.path import *
from ptsa.data.common import pathlib
# from ptsa.data.rawbinwrapper import RawBinWrapper
from ptsa.data.RawBinWrapperXray import RawBinWrapperXray
from ptsa.data.events import Events
import numpy as np

import xray

import time

from ptsa.data.common import TypeValTuple, PropertiedObject
from ptsa.data.common.path_utils import find_dir_prefix


class TalReader(PropertiedObject):
# class TimeSeriesEEGReader(object):
    _descriptors = [
        TypeValTuple('samplerate', float, -1.0),
        TypeValTuple('keep_buffer', bool, True),
        TypeValTuple('buffer_time', float, 0.0),
        TypeValTuple('start_time', float, 0.0),
        TypeValTuple('tal_filename', str, ''),
    ]


    def __init__(self, **kwds):

        self.bipolar_channels=None
        for option_name, val in kwds.items():

            try:
                attr = getattr(self,option_name)
                setattr(self,option_name,val)
            except AttributeError:
                print 'Option: '+ option_name+' is not allowed'


    def read(self):
        from ptsa.data.MatlabIO import deserialize_single_object_from_matlab_format
        bp_tal_struct = deserialize_single_object_from_matlab_format(self.tal_filename,'bpTalStruct')
        #extract bipolar pairs
        self.bipolar_channels = np.empty(shape=(len(bp_tal_struct),2), dtype=np.str)

        for record in  bp_tal_struct:
            self.bipolar_channels = np.asarray(map(lambda x: str(x).zfill(3),record.channel), dtype=np.str)

            # print record.channel

    def get_bipolar_pairs(self):
        if self.bipolar_channels is None
            self.read()
        self.bipolar_channels is


if __name__=='__main__':
    event_range = range(0, 30, 1)
    e_path = '/Users/m/data/eeg/R1060M/tal/R1060M_talLocs_database_bipol.mat'

    tal_reader = TalReader(tal_filename=e_path)
    tal_reader.read()