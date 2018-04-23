from ptsa.data import MatlabIO
import os.path as osp

def test_read_matlab_struct():
    filename = osp.join(osp.dirname(__file__),'data','test_events.mat')
    events = MatlabIO.read_single_matlab_matrix_as_numpy_structured_array(filename,'events')
    assert len(events.squeeze()) == 191
    assert events.list.max() == 1


if __name__=='__main__':
    test_read_matlab_struct()