from ptsa.test.utils import get_rhino_root,skip_without_rhino
import os.path as osp
import numpy as np
from ptsa.data.readers.H5RawReader import H5RawReader
from ptsa.data.readers.BaseRawReader import BaseRawReader

@skip_without_rhino
def test_h5reader():
    root = get_rhino_root()
    h5_dataroot = osp.join(root,'data','eeg','R1275D','behavioral','FR1','session_0','host_pc','20170531_170954','eeg_timeseries.h5')

    channels = np.array(['%.03d'%i for i in range(1,10)])
    h5_data,_ = H5RawReader.read_h5file(h5_dataroot, channels, [0], 1000)

    raw_dataroot = osp.join(root,'protocols','r1','subjects','R1275D','experiments','FR1','sessions','0',
                            'ephys','current_processed','noreref','R1275D_FR1_0_31May17_2109')

    raw_timeseries,_ = BaseRawReader(dataroot=raw_dataroot,channels=channels,start_offsets=np.array([0]),read_size=1000).read()
    assert (raw_timeseries.data == h5_data*raw_timeseries.gain).all()



if __name__== '__main__':
    test_h5reader()

