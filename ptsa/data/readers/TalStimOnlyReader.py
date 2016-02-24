__author__ = 'm'

import numpy as np
from ptsa.data.common import TypeValTuple, PropertiedObject
from ptsa.data.readers import BaseReader

from ptsa.data.readers import TalReader


class TalStimOnlyReader(TalReader):
    '''
    Reader that reads tal structs Matlab file and converts it to numpy recarray
    '''

    def __init__(self, **kwds):
        '''
        Constructor:

        :param kwds:allowed values are:
        -------------------------------------
        :param filename {str} -  path to tal file
        :param struct_name {str} -  name of the matlab struct to load
        :return: None
        '''

        TalReader.__init__(self, **kwds)
        self.struct_name = 'virtualTalStruct'
