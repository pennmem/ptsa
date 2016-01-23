from ptsa.data.common import TypeValTuple, PropertiedObject
from ptsa.data.common.path_utils import find_dir_prefix
from ptsa.data.common import pathlib
import os
import collections


class ParamsReader(PropertiedObject):
    _descriptors = [
        TypeValTuple('params_path', str, ''),
        TypeValTuple('dataroot', str, ''),
    ]

    def __init__(self, **kwds):

        self.init_attrs(kwds)
        if self.params_path and not os.path.isfile(self.params_path):
            raise IOError('Could not open params file: %' % self.params_path)

        Converter = collections.namedtuple('Converter', ['convert', 'name'])
        self.param_to_convert_fcn = {
            'samplerate': Converter(convert=float, name='samplerate'),
            'gain': Converter(convert=float, name='gain'),
            'format': Converter(convert=lambda s: s.replace("'", "").replace('"', ''), name='format'),
            'dataformat': Converter(convert=lambda s: s.replace("'", "").replace('"', ''), name='format')
        }

    def get_params_file_from_dataroot(self, dataroot):
        for param_file_name in ('.params', 'params.txt'):
            full_param_file_name = os.path.join(dataroot, param_file_name)
            if os.path.isfile(full_param_file_name):
                return full_param_file_name

        raise IOError('No params file found in ' + str(dataroot) +
                      '. Params files must be in the same directory ' +
                      'as the EEG data and must be named .params ' +
                      'or params.txt.')

    def read(self):
        params = {}
        param_file = self.params_path
        if self.dataroot:
            param_file = self.get_params_file_from_dataroot(self.dataroot)

        # we have a file, so open and process it
        for line in open(param_file, 'r').readlines():
            # get the columns by splitting
            param_name, str_to_convert = line.strip().split()[:2]
            try:
                convert_tuple = self.param_to_convert_fcn[param_name]
                params[convert_tuple.name] = convert_tuple.convert(str_to_convert)
            except KeyError:
                pass
        if not set(params.keys()).issuperset(set(['gain', 'samplerate'])):
            raise ValueError(
                    'Params file must contain samplerate and gain!\n' +
                    'The following fields were supplied:\n' + str(params.keys()))

        return params


if __name__ == '__main__':
    p_path = '/Users/m/data/eeg/R1060M/eeg.noreref/params.txt'
    from ptsa.data.readers.ParamsReader import ParamsReader

    p_reader = ParamsReader(params_path=p_path)
    params = p_reader.read()
    print params
