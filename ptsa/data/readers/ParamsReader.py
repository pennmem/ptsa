from ptsa.data.common import TypeValTuple, PropertiedObject
from ptsa.data.common.path_utils import find_dir_prefix
from ptsa.data.common import pathlib
from os.path import *
import collections


class ParamsReader(PropertiedObject):
    _descriptors = [
        TypeValTuple('params_file', str, ''),
        TypeValTuple('dataroot', str, ''),
    ]

    def __init__(self, **kwds):

        self.init_attrs(kwds)

        if self.params_file and not isfile(self.params_file):
            raise IOError('Could not open params file: %s' % self.params_file)

        elif self.dataroot:
            self.params_file = self.locate_params_file(dataroot=self.dataroot)
        else:
            raise IOError('Could not find params file using dataroot: %s or using direct path:%s'%(self.dataroot,self.params_file))

        Converter = collections.namedtuple('Converter', ['convert', 'name'])
        self.param_to_convert_fcn = {
            'samplerate': Converter(convert=float, name='samplerate'),
            'gain': Converter(convert=float, name='gain'),
            'format': Converter(convert=lambda s: s.replace("'", "").replace('"', ''), name='format'),
            'dataformat': Converter(convert=lambda s: s.replace("'", "").replace('"', ''), name='format')
        }

    def locate_params_file(self, dataroot):

        for param_file in (abspath(dataroot + '.params'),
                          abspath(join(dirname(dataroot), 'params.txt'))):

            if isfile(param_file):
                return param_file


        raise IOError('No params file found in ' + str(dir) +
                      '. Params files must be in the same directory ' +
                      'as the EEG data and must be named .params ' +
                      'or params.txt.')

    def read(self):
        params = {}
        param_file = self.params_file

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

    p_reader = ParamsReader(params_file=p_path)
    params = p_reader.read()
    print params


    dataroot = '/Users/m/data/eeg/R1060M/eeg.noreref/R1060M_01Aug15_0805'
    p_reader = ParamsReader(dataroot=dataroot)
    params = p_reader.read()
    print params
