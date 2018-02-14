from ptsa.data.readers import EDFRawReader,JsonIndexReader,CMLEventReader,EEGReader
import pytest
import os.path as osp
from ptsa.test.utils import get_rhino_root,skip_without_rhino
import numpy as np


class TestEDFReader:

    @classmethod
    def setup(cls):
        root = get_rhino_root()
        cls.bdf_file_template = osp.join(root,'protocols','ltp','subjects','{subject:s}',
                                         'experiments','ltpFR2','sessions','{session:d}',
                                         'ephys','current_processed','{subject:s}_session_{session:d}.bdf')
        here = osp.realpath(osp.dirname(__file__))
        cls.fname = osp.join(here, 'data', 'eeg.edf')

    def test_read_local(self):
        reader = EDFRawReader(dataroot=self.fname,channels = np.array([0,3,6]))
        reader.read()

    @skip_without_rhino
    @pytest.mark.parametrize('subject,session',
                             [('LTP360',2),])
                              #('LTP342',22)])
    def test_1_offset_1_chann_returns(self,subject,session):
        filename = self.bdf_file_template.format(subject=subject,session=session)
        channel = np.array(['002'])
        EDFRawReader(dataroot=filename,channels=channel,start_offsets=np.array([0]),read_size=500).read()

    @skip_without_rhino
    @pytest.mark.parametrize('subject,session',
                             [('LTP360', 2),
                              ('LTP342', 22)])
    def test_1_offset_1_chann_succeeds(self, subject, session):
        filename = self.bdf_file_template.format(subject=subject, session=session)
        channel = np.array(['002'])
        reader  = EDFRawReader(dataroot=filename, channels=channel, start_offsets=np.array([0]), read_size=500)
        data,mask = reader.read_file(reader.dataroot,channel,read_size=500)
        assert mask.all()
        assert not np.isnan(data).any()

    @skip_without_rhino
    @pytest.mark.parametrize('subject,session',
                             [('LTP360', 2),
                              ('LTP342', 22)])
    def test_channels(self,subject,session):
        channels = np.array(['002','004','008','016'])
        filename = self.bdf_file_template.format(subject=subject,session=session)
        data,mask = EDFRawReader(dataroot=filename, channels = channels,
                                          start_offsets=np.array([0]), read_size=500).read()
        assert mask.all()
        assert not np.isnan(data).any()

    @skip_without_rhino
    @pytest.mark.parametrize('subject,session',
                             [('LTP360', 2),
                              ('LTP342', 22)])
    def test_all_channels(self, subject, session):
        filename = self.bdf_file_template.format(subject=subject, session=session)
        data, mask = EDFRawReader(dataroot=filename, channels=np.array([]),
                                  start_offsets=np.array([0]), read_size=500).read()
        return

    @skip_without_rhino
    @pytest.mark.parametrize('subject,session',
                              [('LTP342', 22)])
    def test_full_session(self,subject,session):
        channels = np.array(['002','004','008','016'])
        filename = self.bdf_file_template.format(subject=subject,session=session)
        data,mask = EDFRawReader(dataroot=filename, channels=channels,read_size=-1).read()
        assert mask.all()
        assert not np.isnan(data).any()

    @skip_without_rhino
    @pytest.mark.parametrize('subject,session',
                             [('LTP342', 22)])
    def test_eeg_reader(self,subject,session):
        jr = JsonIndexReader(osp.join(get_rhino_root(),'protocols','ltp.json'))
        events = CMLEventReader(filename=jr.get_value('task_events',subject=subject,session=session)).read()
        EEGReader(events=events[:10],start_time=0.0,end_time=0.1).read()




if __name__ == '__main__':
    TestEDFReader.setup()
    test2 = TestEDFReader()
    test2.test_channels('LTP360',3)
    test2.test_all_channels('LTP360',3)
    test2.test_full_session('LTP342',22)
