import json
import os

import numpy as np
import pandas as pd
from ptsa.data.readers import BaseReader
import warnings
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
    unpack = traits.api.Bool

    def __init__(self, filename,struct_name='bpTalStruct',struct_type='bi',unpack=True):
        """
        Keyword arguments
        -----------------

        :param filename {str} -  path to tal file or pairs.json file
        :param struct_name {str} -  name of the struct to load. Default is 'bpTalStruct'. Only relevant when reading
        MATLAB tal struct files.
        :param struct_type {str} - either 'mono', indicating a monopolar struct, or 'bi', indicating a bipolar struct.
        Default is 'bi'.
        :param unpack {bool} - If :py:val:False, returns the "atlases" column as an array of python dicts, rather
        than unpacking them into nested structured arrays. Default is :py:True.
        :return: None

        """
        super(TalReader, self).__init__()
        self.filename = filename
        self.struct_name = struct_name
        self.struct_type  = struct_type

        self.bipolar_channels=None

        self.tal_struct_array = None
        self.unpack = unpack
        if not self.unpack:
            warnings.warn('Unpack option will be removed in a future release,'
                          'at which point behavior will be as with unpack=True',
                          PendingDeprecationWarning)
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

    @classmethod
    def from_records(cls,contact_dict):
        """
        Helper method for :meth:from_dict.
        Takes a list of records (dictionaries with semi-consistent fields)
        and returns a structured array whose fields are the keys of each record.
        Nested records are handled by recursion.

        Missing entries should be represented by either None, NaN, or an empty dictionary.

        :param contact_dict: {List[Union(Dict,None,NaN)]}
        :return: {np.array} A structured array with the same indexing structure as :arg:contact_dict
        """
        contact_df = pd.DataFrame.from_records([x if not pd.isnull(x) else {} for x in contact_dict])
        dict_cols = [col for col in contact_df.columns if any(isinstance(val,dict) for val in contact_df[col])]
        flat_cols = [col for col in contact_df.columns if not col in dict_cols]
        flat_df = contact_df[flat_cols]
        dtype = cls.mkdtype(flat_df)

        nested_arrs = [cls.from_records(contact_df[col]) for col in dict_cols]
        nested_dtypes = [np.dtype([(str(col),x.dtype)]) for col,x in zip(dict_cols,nested_arrs)]
        new_dtype = cls.merge_dtypes(dtype,*nested_dtypes)
        new_arr = np.empty(len(contact_df),dtype=new_dtype)
        for col in flat_cols:
            new_arr[col] = flat_df[col].values
        for (i,col) in enumerate(dict_cols):
            new_arr[col] = nested_arrs[i]
        return np.rec.array(new_arr)

    def from_dict(self,json_dict,unpack=True):
        """
        Reads a JSON localization file into a record array.
        :param json_dict: A dictionary of localization information, with one entry for each contact or pair.
        :return:
        """
        keys = json_dict.keys()
        subject = [k for k in keys if k not in ['version', 'info', 'meta']][0]
        records =json_dict[subject]['contacts' if self.struct_type == 'mono' else 'pairs'].values()
        if not unpack:
            return pd.DataFrame.from_records(list(records)).to_records(index=False)
        else:
            ts = self.from_records(records)
            if self.struct_type=='bi':
                extended_dt = self.merge_dtypes(ts.dtype,np.dtype([('channel',int,2),
                                                                   ('eType','U256'),('tagName','U256')]))
            else:
                extended_dt = self.merge_dtypes(ts.dtype,np.dtype([('eType','U2'),('tagName','U256')]))
            # Add some additional fields for compatibility
            new_ts = np.empty(ts.shape,dtype=extended_dt)
            for col in ts.dtype.names:
                new_ts[col] = ts[col]
            if self.struct_type == 'bi':
                new_ts['channel'][:,0] = ts['channel_1']
                new_ts['channel'][:,1] = ts['channel_2']
                new_ts['eType'] = ts['type_1']
                new_ts['tagName'] = ts['code']
            new_ts.sort(order='channel')
            return np.rec.array(new_ts)


    @classmethod
    def mkdtype(cls,flat_df):
        """
        Invariant: there are no subfields of flat_df whose elements are dictionaries
        :param flat_df: {pandas.DataFrame}
        :return: {np.dtype}
        """
        dt_list =  [(str(c),flat_df[c].values.dtype if flat_df[c].values.dtype != np.dtype('O') else 'U256') for c in flat_df.columns]
        return np.dtype(dt_list)

    @classmethod
    def merge_dtypes(cls,*dtypes):
        if len(dtypes) == 1:
            return dtypes[0]
        elts = [(n,dt[n]) for dt in dtypes for n in dt.names]
        return np.dtype(elts)

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
            self.tal_struct_array = self.from_dict(pairs,unpack=self.unpack)
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
