__author__ = 'm'

import numpy as np
from ptsa.data.common import TypeValTuple, PropertiedObject


class TalReader(PropertiedObject):
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
        # from ptsa.data.MatlabIO import deserialize_single_object_from_matlab_format
        # bp_tal_struct = deserialize_single_object_from_matlab_format(self.tal_filename,'bpTalStruct')

        from ptsa.data.MatlabIO import read_single_matlab_matrix_as_numpy_structured_array
        tal_struct_array = read_single_matlab_matrix_as_numpy_structured_array(self.tal_filename,'bpTalStruct')

        #extract bipolar pairs
        # self.bipolar_channels = np.empty(shape=(len(bp_tal_struct),2), dtype='|S3')
        # self.bipolar_channels = np.recarray(shape=(len(bp_tal_struct)), dtype=[('ch0','|S3'),('ch1','|S3')])
        self.bipolar_channels = np.recarray(shape=(len(tal_struct_array)), dtype=[('ch0','|S3'),('ch1','|S3')])

        channel_record_array = tal_struct_array['channel']
        for i, channel_array in enumerate(channel_record_array):
            # self.bipolar_channels[i] = np.asarray(map(lambda x: str(x).zfill(3),record.channel), dtype=np.str)

            # self.bipolar_channels[i] = tuple(map(lambda x: str(x).zfill(3), record.channel))
            self.bipolar_channels[i] = tuple(map(lambda x: str(x).zfill(3), channel_array))

        # for i, record in enumerate(bp_tal_struct):
        #     # self.bipolar_channels[i] = np.asarray(map(lambda x: str(x).zfill(3),record.channel), dtype=np.str)
        #     self.bipolar_channels[i] = tuple(map(lambda x: str(x).zfill(3), record.channel))


    def get_bipolar_pairs(self):
        if self.bipolar_channels is None:
            self.read()
        return self.bipolar_channels

    def get_monopolar_channels(self):
        bipolar_array = self.get_bipolar_pairs()
        # monopolar_set = set(bipolar_array.flatten())
        monopolar_set = set(list(bipolar_array['ch0'])+list(bipolar_array['ch1']))
        return np.array(sorted(list(monopolar_set)))

if __name__=='__main__':
    event_range = range(0, 30, 1)
    e_path = '/Users/m/data/eeg/R1060M/tal/R1060M_talLocs_database_bipol.mat'

    tal_reader = TalReader(tal_filename=e_path)
    tal_reader.read()

    print tal_reader.get_monopolar_channels()