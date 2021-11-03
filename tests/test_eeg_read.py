from numpy.testing import assert_array_equal
import pytest
import numpy as np
from tests.utils import skip_without_rhino, get_rhino_root



@skip_without_rhino
@pytest.mark.current
class TestTalEEG:
    def _test_eeg_with_tal_struct(self, subject, experiment, session,
                                  struct_type='mono'):
        from ptsa.data.readers import JsonIndexReader, TalReader
        from ptsa.data.readers import EEGReader,BaseEventReader
        import os
        tal_file = 'contacts' if struct_type=='mono' else 'pairs'
        jr = JsonIndexReader(
            os.path.join(get_rhino_root(), 'protocols', 'r1.json'))
        events = BaseEventReader(filename=jr.get_value(
            'task_events', subject=subject,
            experiment=experiment, session=session)).read()
        tal_struct = TalReader(
            filename=jr.get_value(tal_file, subject=subject),
            struct_type=struct_type).read()
        eeg_reader = EEGReader(events=events[:10], channels=tal_struct[:10],
                               start_time=0.0, end_time=0.1)
        eeg = eeg_reader.read()
        print(eeg)
        channel_name = eeg_reader.channel_name
        for col in tal_struct.dtype.names:
            if col != 'atlases':
                # Because I don't want to deal with NaNs at the moment
                if (col == 'channel') & (struct_type == 'bi'):
                    assert_array_equal(np.c_[eeg[channel_name].data['channel_1'],
                                             eeg[channel_name].data['channel_2']],
                                       tal_struct[:10][col])
                else:
                    assert_array_equal(eeg[channel_name].data[col],tal_struct[:10][col])

    def test_split_eeg_with_channels(self):
       self._test_eeg_with_tal_struct('R1111M','FR1',0)

    def test_split_eeg_with_pairs(self):
        with pytest.raises(IndexError):
            self._test_eeg_with_tal_struct('R1111M','FR1',0,'bi')

    def test_hdf5_eeg_with_channels(self):
        with pytest.raises(IndexError):
            self._test_eeg_with_tal_struct('R1364C','FR1',0)

    def test_hdf5_eeg_with_pairs(self):
        self._test_eeg_with_tal_struct('R1364C','FR1',0,'bi')


if __name__ =='__main__':
    TestTalEEG().test_split_eeg_with_pairs()
    TestTalEEG().test_hdf5_eeg_with_pairs()
