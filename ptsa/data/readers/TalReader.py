__author__ = 'm'

import numpy as np
from ptsa.data.common import TypeValTuple, PropertiedObject
from ptsa.data.readers import BaseReader


class TalReader(PropertiedObject,BaseReader):
    '''
    Reader that reads tal structs Matlab file and converts it to numpy recarray
    '''
    _descriptors = [
        TypeValTuple('filename', str, ''),
        TypeValTuple('struct_name', str, 'bpTalStruct'),
    ]

    def __init__(self, **kwds):
        '''
        Constructor:

        :param kwds:allowed values are:
        -------------------------------------
        :param filename {str} -  path to tal file
        :param struct_name {str} -  name of the matlab struct to load
        :return: None
        '''

        self.init_attrs(kwds)
        self.bipolar_channels=None

        self.tal_structs_array = None

    def get_bipolar_pairs(self):
        '''

        :return: numpy recarray where each record has two fields 'ch0' and 'ch1' storing  channel labels.
        '''
        if self.bipolar_channels is None:
            if self.tal_structs_array is None:
                self.read()
            self.initialize_bipolar_pairs()

        return self.bipolar_channels

    def get_monopolar_channels(self):
        '''

        :return: numpy array of monopolar channel labels
        '''
        bipolar_array = self.get_bipolar_pairs()
        monopolar_set = set(list(bipolar_array['ch0'])+list(bipolar_array['ch1']))
        return np.array(sorted(list(monopolar_set)))

    def initialize_bipolar_pairs(self):
        # initialize bipolar pairs
        self.bipolar_channels = np.recarray(shape=(len(self.tal_struct_array)), dtype=[('ch0','|S3'),('ch1','|S3')])

        channel_record_array = self.tal_struct_array['channel']
        for i, channel_array in enumerate(channel_record_array):
            self.bipolar_channels[i] = tuple(map(lambda x: str(x).zfill(3), channel_array))


    def read(self):
        '''

        :return:np.recarray representing tal struct array (originally defined in Matlab file)
        '''

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

        raise AttributeError('Could not read tal struct data. Try specifying struct_name argument :'
                             '\nTalReader(filename=e_path, struct_name=<name_of_struc_to_read>)')



if __name__=='__main__':
    event_range = range(0, 30, 1)
    e_path = '/Users/m/data/eeg/R1060M/tal/R1060M_talLocs_database_bipol.mat'

    # e_path = '/Users/m/data/eeg/TJ010/tal/TJ010_talLocs_database_bipol.mat'

    # tal_reader = TalReader(filename=e_path, struct_name='subjTalEvents')
    tal_reader = TalReader(filename=e_path)
    tal_reader.read()

    print(tal_reader.get_monopolar_channels())