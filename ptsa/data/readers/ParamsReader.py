from ptsa.data.common import TypeValTuple, PropertiedObject
from ptsa.data.readers import BaseReader
from os.path import *
import json
import collections
import warnings

class ParamsReader(PropertiedObject, BaseReader):
    """
    Reader for parameter file (e.g. params.txt)
    """
    _descriptors = [
        TypeValTuple('filename', str, ''),
        TypeValTuple('dataroot', str, ''),
    ]

    def __init__(self, **kwds):
        """
        Constructor
        :param kwds:allowed values are:
        -------------------------------------
        :param filename {str} -  path t params file
        :param dataroot {str} -  core name of the eegfiles

        :return: None
        """
        self.init_attrs(kwds)

        if self.filename:
            if not isfile(self.filename):
                raise IOError('Could not open params file: %s' % self.filename)

        elif self.dataroot:
            self.filename = self.locate_params_file(dataroot=self.dataroot)
        else:
            raise IOError('Could not find params file using dataroot: %s or using direct path:%s' % (
            self.dataroot, self.filename))

        if splitext(self.filename)[-1] == '.txt':
            Converter = collections.namedtuple('Converter', ['convert', 'name'])
            self.param_to_convert_fcn = {
                'samplerate': Converter(convert=float, name='samplerate'),
                'gain': Converter(convert=float, name='gain'),
                'format': Converter(convert=lambda s: s.replace("'", "").replace('"', ''), name='format'),
                'dataformat': Converter(convert=lambda s: s.replace("'", "").replace('"', ''), name='format')
            }

    def locate_params_file(self, dataroot):
        """
        Identifies exact path to param file.
        :param dataroot: {str} eeg core file name
        :return: {str}
        """

        for param_file in (abspath(dataroot + '.params'),
                           abspath(join(dirname(dataroot), 'params.txt'))):

            if isfile(param_file):
                return param_file

        param_file = join(dirname(dataroot), '..', 'sources.json')
        if isfile(param_file):
            return param_file

        raise IOError('No params file found in ' + str(dataroot) +
                      '. Params files must be in the same directory ' +
                      'as the EEG data and must be named .params ' +
                      'or params.txt, or in the directory above and '
                      'named sources.json')

    def read(self):
        if splitext(self.filename)[-1] == '.txt':
            return self.read_txt()
        else:
            return self.read_json()

    def read_json(self):
        json_params = json.load(open(self.filename))[basename(self.dataroot)]
        params = {}
        params['samplerate'] = json_params['sample_rate']
        params['gain'] = 1
        params['format'] = json_params['data_format']
        params['dataformat'] = json_params['data_format']
        return params

    def read_txt(self):
        """
        Parses param file
        :return: {dict} dictionary with param file content
        """
        params = {}
        param_file = self.filename

        # we have a file, so open and process it
        with open(param_file, 'r') as f:
            for line in f.readlines():

                stripped_line_list = line.strip().split()
                if len(stripped_line_list) < 2:
                    continue

                # get the columns by splitting
                # param_name, str_to_convert = line.strip().split()[:2]
                param_name, str_to_convert = stripped_line_list[:2]
                try:
                    convert_tuple = self.param_to_convert_fcn[param_name]
                    params[convert_tuple.name] = convert_tuple.convert(str_to_convert)
                except KeyError:
                    pass

        if not 'gain' in params.keys():
            params['gain'] = 1.0
            warnings.warn('Did not find "gain" in the params.txt file. Assuming gain=1.0', RuntimeWarning)

        if not set(params.keys()).issuperset(set(['gain', 'samplerate'])):
            raise ValueError(
                'Params file must contain samplerate and gain!\n' +
                'The following fields were supplied:\n' + str(list(params.keys())))

        return params


if __name__ == '__main__':
    # p_path = '/Users/m/data/eeg/R1060M/eeg.noreref/params.txt'
    # from ptsa.data.readers.ParamsReader import ParamsReader
    #
    # p_reader = ParamsReader(filename=p_path)
    # params = p_reader.read()
    # print params
    #
    #
    # dataroot = '/Users/m/data/eeg/R1060M/eeg.noreref/R1060M_01Aug15_0805'
    # p_reader = ParamsReader(dataroot=dataroot)
    # params = p_reader.read()
    # print params

    dataroot = '/Volumes/db_root/protocols/r1/subjects/R1001P/experiments/FR1/sessions/0/ephys/current_processed/noreref/R1001P_FR1_0_12Oct14_1034'
    p_reader = ParamsReader(dataroot=dataroot)
    params = p_reader.read()
    print(params)
