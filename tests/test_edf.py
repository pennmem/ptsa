import os.path as osp
import pytest

from ptsa.extensions.edf import EDFFile


@pytest.fixture
def edffile():
    """Using a section of EEG data obtained from
    https://www.teuniz.net/edf_bdf_testfiles/

    """
    here = osp.realpath(osp.dirname(__file__))
    fname = osp.join(here, 'data', 'eeg.edf')
    edf = EDFFile(fname)
    yield edf
    edf.close()


class TestEDFFile:
    """Direct tests of the ``edffile`` extension module."""
    def test_num_channels(self, edffile):
        assert edffile.num_channels == 37

    def test_num_samples(self, edffile):
        assert edffile.num_samples == 2000

    def test_num_annotations(self, edffile):
        assert edffile.num_annotations == 0

    def test_get_channel_info(self, edffile):
        info = edffile.get_channel_info(0)
        assert info.label == "EEG FP1"
        assert info.smp_in_file == 2000
        assert info.smp_in_datarecord == 20

    def test_get_channel_numbers(self,edffile):
        assert edffile.get_channel_numbers(['EEG FP1'])[0]==0

    @pytest.mark.xfail
    def test_get_channel_numbers_failure(self,edffile):
        edffile.get_channel_numbers(['LA1'])

    def test_read_samples_by_number(self, edffile):
        data = edffile.read_samples([0,3,6], 2000)
        assert data.shape[1] == 2000

    def test_read_samples_by_name(self,edffile):
        data_by_name = edffile.read_samples(['EEG FP1','EEG F4','EEG P3'],2000)
        data_by_num = edffile.read_samples([0,3,6],2000)
        assert (data_by_name==data_by_num).all()

