from ptsa.data.readers import ParamsReader
import pytest
import os

data_dir = os.path.join(os.path.dirname(__file__),'data')

@pytest.fixture
def txt_path():
    return os.path.join(data_dir,'params','params.txt')

@pytest.fixture
def json_path():
    return os.path.join(data_dir,'params','sources.json')

def test_read_txt(txt_path):
    params = ParamsReader(filename=txt_path).read()
    assert params['samplerate'] == 499.71
    assert params['format'] == 'int16'

def test_read_json(json_path):
    params = ParamsReader(filename=json_path,dataroot='R1111M_FR1_0_22Jan16_1638').read()
    assert params['samplerate'] == 500.
    assert params['dataformat'] == 'int16'