import sys

sys.path = sys.path[1:]

from ptsa.data.readers import EDFRawReader
import pytest
import os.path as osp
from ptsa.test.utils import get_rhino_root,skip_without_rhino
import numpy as np


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
        data,mask = EDFRawReader(dataroot=filename, channels=channel, start_offsets=np.array([0]), read_size=500).read()
        assert mask.all()
        assert not np.isnan(data).any()

    @pytest.mark.parametrize('subject,session',
                             [('LTP360', 3),
                              ('LTP342', 22)])
    def test_channels(self,subject,session):
        channels = np.array(['002','004','008','016'])
        filename = self.bdf_file_template.format(subject=subject,session=session)
        data,mask = EDFRawReader(dataroot=filename, channels=channels,
                                          start_offsets=np.array([0]), read_size=500).read()
        assert mask.all()
        assert not np.isnan(data).any()


    @pytest.mark.parametrize('subject,session',
                             [('LTP360', 3),
                              ('LTP342', 22)])
    def test_full_session(self,subject,session):
        channels = np.array(['002','004','008','016'])
        filename = self.bdf_file_template.format(subject=subject,session=session)
        data,mask = EDFRawReader(dataroot=filename, channels=channels,read_size=-1).read()
        assert mask.all()
        assert not np.isnan(data).any()
