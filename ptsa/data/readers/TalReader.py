import os
import json

import numpy as np
import pandas as pd

from ptsa.data.common import TypeValTuple, PropertiedObject
from ptsa.data.readers import BaseReader


class TalReader(PropertiedObject,BaseReader):
    """
    Reader that reads tal structs Matlab file and converts it to numpy recarray
    """
    _descriptors = [
        TypeValTuple('filename', basestring, ''),
        TypeValTuple('struct_name', basestring, 'bpTalStruct'),
    ]

    def __init__(self, **kwds):
        """
        Keyword arguments
        -----------------

        :param filename {str} -  path to tal file or pairs.json file
        :param struct_name {str} -  name of the matlab struct to load
        :return: None

        """

        self.init_attrs(kwds)
        self.bipolar_channels=None

        self.tal_structs_array = None
        self._json = os.path.splitext(self.filename)[-1]=='.json'

    def get_bipolar_pairs(self):
        """

        :return: numpy recarray where each record has two fields 'ch0' and 'ch1' storing  channel labels.
        """
        if self.bipolar_channels is None:
            if self.tal_structs_array is None:
                self.read()
            self.initialize_bipolar_pairs()

        return self.bipolar_channels

    def get_monopolar_channels(self):
        """

        :return: numpy array of monopolar channel labels
        """
        bipolar_array = self.get_bipolar_pairs()
        monopolar_set = set(list(bipolar_array['ch0'])+list(bipolar_array['ch1']))
        return np.array(sorted(list(monopolar_set)))

    def initialize_bipolar_pairs(self):
        # initialize bipolar pairs
        self.bipolar_channels = np.recarray(shape=(len(self.tal_struct_array)), dtype=[('ch0','|S3'),('ch1','|S3')])

        channel_record_array = self.tal_struct_array['channel']
        for i, channel_array in enumerate(channel_record_array):
            self.bipolar_channels[i] = tuple(map(lambda x: str(x).zfill(3), channel_array))

    @staticmethod
    def from_dict(pairs):
        pairs = pd.DataFrame.from_dict(list(pairs.values())[0]['pairs'], orient='index').sort_values(by=['channel_1','channel_2'])
        pairs.index.name = 'tagName'
        pairs['channel'] = [[ch1, ch2] for ch1, ch2 in zip(pairs.channel_1.values, pairs.channel_2.values)]
        pairs['eType'] = pairs.type_1
        return pairs.to_records()

    def read(self):
        """

        :return:np.recarray representing tal struct array (originally defined in Matlab file)
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


if __name__ == '__main__':
    event_range = range(0, 30, 1)
    e_path = '/Users/m/data/eeg/R1060M/tal/R1060M_talLocs_database_bipol.mat'

    # e_path = '/Users/m/data/eeg/TJ010/tal/TJ010_talLocs_database_bipol.mat'

    # tal_reader = TalReader(filename=e_path, struct_name='subjTalEvents')
    tal_reader = TalReader(filename=e_path)
    tal_reader.read()

    print(tal_reader.get_monopolar_channels())
