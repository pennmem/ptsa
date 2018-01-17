import sys

sys.path = sys.path[1:]

from ptsa.data.readers import EDFRawReader
from ptsa.extensions.edf import EDFFile
import pytest
import os.path as osp
from ptsa.test.utils import get_rhino_root,skip_without_rhino
import numpy as np

@skip_without_rhino
class TestEDFFile:
    fname = osp.join(get_rhino_root(), 'data', 'eeg', 'scalp', 'ltp', 'ltpFR2',
                          'LTP360', 'session_1', 'eeg', 'LTP360_session_1.bdf')

    def test_constructor(self):
        edffile = EDFFile(self.fname)
        edffile.close()

    def test_read_samples(self):
        edffile =  EDFFile(self.fname)
        data = edffile.read_samples([1,2],500,0)
        shape = data.shape
        assert shape == (2,500)


    def test_read_rhino_samples(self):
        rhino_file = osp.join(get_rhino_root(),'data','eeg','scalp','ltp','ltpFR2',
                              'LTP360','session_1','eeg','LTP360_session_1.bdf')
        n_samples = 500
        edffile = EDFFile(rhino_file)
        channels = [i for i in range(edffile.num_channels)]
        data = edffile.read_samples(channels,offset=100,samples=n_samples)
        # assert data.shape[0]==len(channels)
        # assert data.shape[1]==n_samples
        edffile.close()
        print(data)


@skip_without_rhino
class TestEDFReader:

    @classmethod
    def setup(cls):
        root = get_rhino_root()
        cls.bdf_file_template = osp.join(root,'data','eeg','scalp',
                                         'ltp','ltpFR2','{subject:s}','session_{session:d}',
                                         'eeg','{subject:s}_session_{session:d}.bdf')


    @pytest.mark.parametrize('subject,session',
                             [('LTP360',3),])
                              #('LTP342',22)])
    def test_1_offset_1_chann_returns(self,subject,session):
        filename = self.bdf_file_template.format(subject=subject,session=session)
        channel = np.array(['002'])
        EDFRawReader(dataroot=filename,channels=channel,start_offsets=np.array([0]),read_size=500).read()

    @pytest.mark.parametrize('subject,session',
                             [('LTP360', 3),
                              ('LTP342', 22)])
    def test_1_offset_1_chann_succeeds(self, subject, session):
        filename = self.bdf_file_template.format(subject=subject, session=session)
        channel = np.array(['002'])
        reader  = EDFRawReader(dataroot=filename, channels=channel, start_offsets=np.array([0]), read_size=500)
        data,mask = reader.read_file(reader.dataroot,channel,read_size=500)
        assert mask.all()
        assert not np.isnan(data).any()

    @pytest.mark.parametrize('subject,session',
                             [('LTP360', 3),
                              ('LTP342', 22)])
    def test_channels(self,subject,session):
        channels = np.array(['002','004','008','016'])
        filename = self.bdf_file_template.format(subject=subject,session=session)
        data,mask = EDFRawReader(dataroot=filename, channels = channels,
                                          start_offsets=np.array([0]), read_size=500).read()
        assert mask.all()
        assert not np.isnan(data).any()


    @pytest.mark.parametrize('subject,session',
                             [('LTP360', 3),
                              ('LTP342', 22)])
    def test_all_channels(self, subject, session):
        filename = self.bdf_file_template.format(subject=subject, session=session)
        data, mask = EDFRawReader(dataroot=filename, channels=np.array([]),
                                  start_offsets=np.array([0]), read_size=500).read()
        return

    @pytest.mark.parametrize('subject,session',
                             [('LTP360', 3),
                              ('LTP342', 22)])
    def test_full_session(self,subject,session):
        channels = np.array(['002','004','008','016'])
        filename = self.bdf_file_template.format(subject=subject,session=session)
        data,mask = EDFRawReader(dataroot=filename, channels=channels,read_size=-1).read()
        assert mask.all()
        assert not np.isnan(data).any()



if __name__ == '__main__':
    test1 = TestEDFFile()
    test1.test_read_rhino_samples()
    TestEDFReader.setup()
    test2 = TestEDFReader()
    test2.test_channels('LTP360',3)
    test2.test_all_channels('LTP360',3)
    test2.test_full_session('LTP342',22)
