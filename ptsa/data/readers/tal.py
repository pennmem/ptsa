import json
import os
import warnings
from typing import TYPE_CHECKING, Any, Iterable, Union

import numpy as np
import pandas as pd
import traits.api

from ptsa.data.readers import BaseReader

__all__ = [
    'TalReader',
    'TalStimOnlyReader',
]


class TalReader(BaseReader, traits.api.HasTraits):
    """
    Reader that reads tal structs Matlab file or pairs.json file and converts it to numpy recarray
    """

    # See `ParamsReader` for the rationale on the TYPE_CHECKING split:
    # traits.api descriptors are unrecognised by pyright, so we declare
    # the bound attribute types separately for type-checking.
    if TYPE_CHECKING:
        filename: str
        struct_name: str
        struct_type: str
        unpack: bool
    else:
        filename = traits.api.Str
        struct_name = traits.api.Str
        struct_type = traits.api.Enum('bi', 'mono')
        unpack = traits.api.Bool

    def __init__(
        self,
        filename: str,
        struct_name: str = 'bpTalStruct',
        struct_type: str = 'bi',
        unpack: bool = True,
    ) -> None:
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
        warnings.warn("Lab-specific readers may be moved to the cmlreaders "
                      "package (https://github.com/pennmem/cmlreaders)",
                      FutureWarning)

        super(TalReader, self).__init__()
        self.filename = filename
        self.struct_name = struct_name
        self.struct_type = struct_type

        self.bipolar_channels: np.recarray | None = None

        self.tal_struct_array: np.recarray | None = None
        self.unpack = unpack
        if not self.unpack:
            warnings.warn('Unpack option will be removed in a future release,'
                          'at which point behavior will be as with unpack=True',
                          PendingDeprecationWarning)
        self._json: bool = os.path.splitext(self.filename)[-1] == '.json'
        if self.struct_type not in ['bi', 'mono']:
            raise AttributeError('Value %s not a valid struct_type. Please choose either "mono" or "bi"' % self.struct_type)
        if self.struct_type == 'mono':
            self.struct_name = 'talStruct'

    def get_bipolar_pairs(self) -> np.recarray:
        """

        :return: numpy recarray where each record has two fields 'ch0' and 'ch1' storing  channel labels.
        """
        if self.bipolar_channels is None:
            if self.tal_struct_array is None:
                self.read()
            self.initialize_bipolar_pairs()

        assert self.bipolar_channels is not None  # populated by initialize_bipolar_pairs
        return self.bipolar_channels

    def get_monopolar_channels(self) -> np.ndarray:
        """

        :return: numpy array of monopolar channel labels
        """
        if self.struct_type == 'bi':
            bipolar_array = self.get_bipolar_pairs()
            monopolar_set = set(list(bipolar_array['ch0']) + list(bipolar_array['ch1']))
            return np.array(sorted(list(monopolar_set)))
        else:
            if self.tal_struct_array is None:
                self.read()
            assert self.tal_struct_array is not None
            return np.array(['{:03d}'.format(c) for c in self.tal_struct_array['channel']])

    def initialize_bipolar_pairs(self) -> None:
        # initialize bipolar pairs
        assert self.tal_struct_array is not None
        self.bipolar_channels = np.recarray(shape=(len(self.tal_struct_array),), dtype=[('ch0', '|S3'), ('ch1', '|S3')])

        channel_record_array = self.tal_struct_array['channel']
        for i, channel_array in enumerate(channel_record_array):
            self.bipolar_channels[i] = tuple(map(lambda x: str(x).zfill(3), channel_array))

    @classmethod
    def from_records(cls, contact_dict: Iterable[Any]) -> np.recarray:
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
        dict_cols = [col for col in contact_df.columns if any(isinstance(val, dict) for val in contact_df[col])]
        flat_cols = [col for col in contact_df.columns if not col in dict_cols]
        # `contact_df[flat_cols]` returns a DataFrame when given a list,
        # but pyright's pandas stubs widen the result to Series | DataFrame.
        flat_df: pd.DataFrame = contact_df.loc[:, flat_cols]
        dtype = cls.mkdtype(flat_df)

        nested_arrs = [cls.from_records(contact_df[col]) for col in dict_cols]
        nested_dtypes = [np.dtype([(str(col), x.dtype)]) for col, x in zip(dict_cols, nested_arrs)]
        new_dtype = cls.merge_dtypes(dtype, *nested_dtypes)
        new_arr = np.empty(len(contact_df), dtype=new_dtype)
        for col in flat_cols:
            new_arr[col] = np.asarray(flat_df[col])
        for (i, col) in enumerate(dict_cols):
            new_arr[col] = nested_arrs[i]
        return np.rec.array(new_arr)

    def from_dict(
        self,
        json_dict: dict,
        unpack: bool = True,
    ) -> Union[np.recarray, pd.DataFrame]:
        """
        Reads a JSON localization file into a record array.
        :param json_dict: A dictionary of localization information, with one entry for each contact or pair.
        :return:
        """
        keys = json_dict.keys()
        subject = [k for k in keys if k not in ['version', 'info', 'meta']][0]
        records = json_dict[subject]['contacts' if self.struct_type == 'mono' else 'pairs'].values()
        if not unpack:
            return pd.DataFrame.from_records(list(records)).to_records(index=False)
        else:
            ts = self.from_records(records)
            if self.struct_type == 'bi':
                extended_dt = self.merge_dtypes(ts.dtype, np.dtype([('channel', int, 2),
                                                                   ('eType', 'U256'), ('tagName', 'U256')]))
            else:
                extended_dt = self.merge_dtypes(ts.dtype, np.dtype([('eType', 'U2'), ('tagName', 'U256')]))
            # Add some additional fields for compatibility
            new_ts = np.empty(ts.shape, dtype=extended_dt)
            assert ts.dtype.names is not None
            for col in ts.dtype.names:
                new_ts[col] = ts[col]
            if self.struct_type == 'bi':
                new_ts['channel'][:, 0] = ts['channel_1']
                new_ts['channel'][:, 1] = ts['channel_2']
                new_ts['eType'] = ts['type_1']
                new_ts['tagName'] = ts['code']
            new_ts.sort(order='channel')
            return np.rec.array(new_ts)

    @classmethod
    def mkdtype(cls, flat_df: pd.DataFrame) -> np.dtype:
        """
        Invariant: there are no subfields of flat_df whose elements are dictionaries
        :param flat_df: {pandas.DataFrame}
        :return: {np.dtype}
        """
        # pandas >=3 returns StringDtype for what used to be object
        # columns (PDEP-14). is_string_dtype matches both, so any
        # column of strings gets coerced to fixed-width unicode.
        def _col_dtype(col: Any) -> Any:
            if pd.api.types.is_string_dtype(col):
                return 'U256'
            return np.asarray(col).dtype
        dt_list = [(str(c), _col_dtype(flat_df[c])) for c in flat_df.columns]
        return np.dtype(dt_list)

    @classmethod
    def merge_dtypes(cls, *dtypes: np.dtype) -> np.dtype:
        if len(dtypes) == 1:
            return dtypes[0]
        elts = [(n, dt[n]) for dt in dtypes for n in (dt.names or ())]
        return np.dtype(elts)

    def read(self) -> np.recarray:
        """
        :return: np.recarray representing tal struct array
        """
        if not self._json:
            from ptsa.data.MatlabIO import read_single_matlab_matrix_as_numpy_structured_array

            struct_names = ['bpTalStruct', 'subjTalEvents']
            # struct_names = ['bpTalStruct']
            if self.struct_name not in struct_names:
                self.tal_struct_array = read_single_matlab_matrix_as_numpy_structured_array(self.filename, self.struct_name, verbose=False)
                if self.tal_struct_array is not None:
                    return self.tal_struct_array
                else:
                    raise AttributeError('Could not read tal struct data for the specified struct_name=' + self.struct_name)

            else:

                for sn in struct_names:
                    self.tal_struct_array = read_single_matlab_matrix_as_numpy_structured_array(self.filename, sn, verbose=False)
                    if self.tal_struct_array is not None:
                        return self.tal_struct_array
        else:
            with open(self.filename) as fp:
                pairs = json.load(fp)
            result = self.from_dict(pairs, unpack=self.unpack)
            # `unpack=True` (the default) goes through the recarray branch
            # of `from_dict`; the DataFrame branch is the legacy path
            # reachable only when `unpack=False`.
            assert isinstance(result, np.recarray)
            self.tal_struct_array = result
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

    def __init__(self, **kwds: Any) -> None:
        TalReader.__init__(self, **kwds)
        self.struct_name = 'virtualTalStruct'
