import json
import os

import numpy as np
import pandas as pd

import six
from ptsa.data.common import TypeValTuple, PropertiedObject
from ptsa.data.readers import BaseReader
import traits.api

__all__ = [
    'TalReader',
    'TalStimOnlyReader',
]


class TalReader(BaseReader,traits.api.HasTraits):
    """
    Reader that reads tal structs Matlab file or pairs.json file and converts it to numpy recarray
    """

    filename = traits.api.Str
    struct_name = traits.api.Str
    struct_type = traits.api.Enum('bi','mono')

    def __init__(self, filename,struct_name='bpTalStruct',struct_type='bi'):
        """
        Keyword arguments
        -----------------

        :param filename {str} -  path to tal file or pairs.json file
        :param struct_name {str} -  name of the struct to load
        :param struct_type {str} - either 'mono', indicating a monopolar struct, or 'bi', indicating a bipolar struct
        :return: None

        """
        super(TalReader, self).__init__()
        self.filename = filename
        self.struct_name = struct_name
        self.struct_type  = struct_type

        self.bipolar_channels=None

        self.tal_struct_array = None
        self._json = os.path.splitext(self.filename)[-1]=='.json'
        if self.struct_type not in ['bi','mono']:
            raise AttributeError('Value %s not a valid struct_type. Please choose either "mono" or "bi"'%self.struct_type)
        if self.struct_type=='mono':
            self.struct_name='talStruct'

    def get_bipolar_pairs(self):
        """

        :return: numpy recarray where each record has two fields 'ch0' and 'ch1' storing  channel labels.
        """
        if self.bipolar_channels is None:
            if self.tal_struct_array is None:
                self.read()
            self.initialize_bipolar_pairs()

        return self.bipolar_channels

    def get_monopolar_channels(self):
        """

        :return: numpy array of monopolar channel labels
        """
        if self.struct_type=='bi':
            bipolar_array = self.get_bipolar_pairs()
            monopolar_set = set(list(bipolar_array['ch0'])+list(bipolar_array['ch1']))
            return np.array(sorted(list(monopolar_set)))
        else:
            if self.tal_struct_array is None:
                self.read()
            return np.array(['{:03d}'.format(c) for c in self.tal_struct_array['channel']])

    def initialize_bipolar_pairs(self):
        # initialize bipolar pairs
        self.bipolar_channels = np.recarray(shape=(len(self.tal_struct_array)), dtype=[('ch0','|S3'),('ch1','|S3')])

        channel_record_array = self.tal_struct_array['channel']
        for i, channel_array in enumerate(channel_record_array):
            self.bipolar_channels[i] = tuple(map(lambda x: str(x).zfill(3), channel_array))

    def from_dict(self,pairs):
        keys = pairs.keys()
        subject = [k for k in keys if k not in ['version','info','meta']][0]

        if self.struct_type=='bi':
            pairs = pd.DataFrame.from_dict(pairs[subject]['pairs'], orient='index').sort_values(by=['channel_1','channel_2'])
            pairs.index.name = 'tagName'
            pairs['channel'] = [[ch1, ch2] for ch1, ch2 in zip(pairs.channel_1.values, pairs.channel_2.values)]
            pairs['eType'] = pairs.type_1
            return pairs.to_records()
        elif self.struct_type == 'mono':
            contacts = pd.DataFrame.from_dict(pairs[subject]['contacts'],orient='index').sort_values(by='channel')
            contacts.index.name = 'tagName'
            return contacts.to_records()

    def read(self):

        """

        :return: np.recarray representing tal struct array
        """
        if not self._json:
            from ptsa.data.MatlabIO import read_single_matlab_matrix_as_numpy_structured_array

            struct_names = ['bpTalStruct','subjTalEvents']
            # struct_names = ['bpTalStruct']
            if self.struct_name not in struct_names:
                self.tal_struct_array = read_single_matlab_matrix_as_numpy_structured_array(self.filename, self.struct_name,verbose=False)
                if self.tal_struct_array is not None:
                    return self.tal_struct_array
                else:
                    raise AttributeError('Could not read tal struct data for the specified struct_name='+self.struct_name)

            else:

                for sn in struct_names:
                    self.tal_struct_array = read_single_matlab_matrix_as_numpy_structured_array(self.filename,sn,verbose=False)
                    if self.tal_struct_array is not None:
                        return self.tal_struct_array
        else:
            with open(self.filename) as fp:
                pairs= json.load(fp)
            self.tal_struct_array = self.from_dict(pairs)
            return self.tal_struct_array

        raise AttributeError('Could not read tal struct data. Try specifying struct_name argument :'
                             '\nTalReader(filename=e_path, struct_name=<name_of_struc_to_read>)')


class TalStimOnlyReader(TalReader):
    """Reader that reads tal structs file and converts it to numpy
    recarray.

    Keyword arguments
    -----------------
    filename : str
        path to tal file
    struct_name : str
        name of the struct to load

    """

    def __init__(self, **kwds):
        TalReader.__init__(self, **kwds)
        self.struct_name = 'virtualTalStruct'
