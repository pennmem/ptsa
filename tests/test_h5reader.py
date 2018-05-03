import os.path as osp
import time
import pytest

import h5py
import numpy as np

from ptsa.data.readers.hdf5 import H5RawReader
from ptsa.data.readers.binary import BinaryRawReader
from ptsa.data.readers.events import CMLEventReader
from ptsa.data.readers import EEGReader
from ptsa.test.utils import get_rhino_root, skip_without_rhino



class TestH5Reader:
    @classmethod
    def setup_class(cls):
        cls.eegfile = osp.join(osp.dirname(__file__), 'data','eeg','eeg.h5')
        cls.channels = np.array(['{:03d}'.format(i).encode() for i in range(1, 10)])

    @pytest.mark.parametrize(
        'offsets', [np.array([0]), np.arange(0, 2000, 500)]
    )
    def test_with_offsets(self, offsets):
        with h5py.File(self.eegfile, 'r') as hfile:
            h5_data, _ = H5RawReader.read_h5file(hfile, self.channels, offsets,
                                                 1000)


    def test_with_negative_offsets(self):
        offsets = np.array([-1, 0])
        with h5py.File(self.eegfile, 'r') as hfile:
            h5_data, h5_mask = H5RawReader.read_h5file(hfile, self.channels,
                                                       offsets, 1000)


    def test_out_of_bounds(self):
        offsets = np.arange(0, 5000, 2000)
        with h5py.File(self.eegfile, 'r') as hfile:
            h5_data, h5_mask = H5RawReader.read_h5file(hfile, self.channels,
                                                       offsets, 1000)
        assert not h5_mask.all()

    def test_constructor(self):

        reader = H5RawReader(dataroot=self.eegfile,
                             channels=self.channels,
                             start_offsets= [0, 500,1000],
                             read_size=200)
        reader.read()
        assert reader.channel_name == 'bipolar_pairs'



@skip_without_rhino
class TestH5ReaderRhino:
    @classmethod
    def setup_class(cls):
        root = get_rhino_root()
        cls.eeg_path_template = osp.join(
            root, 'data', 'eeg', '{subject:s}', 'behavioral', '{experiment:s}',
            'session_{session:d}', 'host_pc', '{timestamp:s}',
            'eeg_timeseries.h5'
        )

        cls.dataroot_template = osp.join(
            root, 'protocols', 'r1', 'subjects', '{subject:s}', 'experiments',
            '{experiment:s}', 'sessions', '{session:d}', 'ephys',
            'current_processed', 'noreref', '{filename:s}'
        )

        cls.task_events_template = osp.join(
            root, 'protocols', 'r1', 'subjects', '{subject:s}', 'experiments',
            '{experiment:s}', 'sessions', '{session:d}', 'behavioral',
            'current_processed', 'task_events.json'
        )

        # monopolar (old-format) HDF5 file
        cls.monopolar_file = cls.eeg_path_template.format(
            subject='R1275D',
            experiment='FR1',
            session=0,
            timestamp='20170531_170954'
        )

        # bipolar (new-format) HDF5 file
        cls.bipolar_file = cls.eeg_path_template.format(
            subject='R1354E',
            experiment='FR1',
            session=0,
            timestamp='20171026_160648'
        )

        cls.monopolar_dataroot = cls.dataroot_template.format(
            subject='R1275D',
            experiment='FR1',
            session=0,
            filename='R1275D_FR1_0_31May17_2109'
        )

        cls.channels = np.array(['{:03d}'.format(i).encode() for i in range(1, 10)])

    @pytest.mark.parametrize(
        'offsets', [np.array([0]), np.arange(0, 210000, 3000)]
    )
    def test_with_offsets(self, offsets):
        with h5py.File(self.monopolar_file, 'r') as hfile:
            h5_data, _ = H5RawReader.read_h5file(hfile, self.channels, offsets, 1000)

        raw_timeseries, _ = BinaryRawReader(dataroot=self.monopolar_dataroot,
                                          channels=self.channels,
                                          start_offsets=offsets,
                                          read_size=1000).read()
        assert (raw_timeseries.data == h5_data*raw_timeseries.gain).all()

    @pytest.mark.parametrize(
        'offsets', [np.array([-1,0]), np.arange(0, 210000, 3000)]
    )
    def test_with_negative_offsets(self, offsets):
        with h5py.File(self.monopolar_file, 'r') as hfile:
            h5_data, h5_mask = H5RawReader.read_h5file(hfile, self.channels, offsets, 1000)

        raw_timeseries, raw_mask = BinaryRawReader(dataroot=self.monopolar_dataroot,
                                          channels=self.channels,
                                          start_offsets=offsets,
                                          read_size=1000).read()
        assert raw_timeseries.data[raw_mask].shape == h5_data[h5_mask].shape
        assert (raw_timeseries.data[raw_mask] == h5_data[h5_mask]*raw_timeseries.gain).all()

    def test_out_of_bounds(self):
        offsets = np.arange(1000000, 4000000, 1000000)
        with h5py.File(self.monopolar_file, 'r') as hfile:
            h5_data, h5_mask = H5RawReader.read_h5file(hfile, self.channels, offsets, 1000)

        raw_data,raw_mask = BinaryRawReader(dataroot=self.monopolar_dataroot,
                                          channels=self.channels,
                                          start_offsets=offsets,
                                          read_size=1000).read()
        assert(raw_mask == h5_mask).all()
        assert(h5_data[h5_mask] == raw_data.data[raw_mask]).all()

    def test_constructor(self):
        dataroot = self.dataroot_template.format(
            subject='R1354E',
            experiment='FR1',
            session=0,
            filename='R1354E_FR1_0_26Oct17_2006.h5'
        )
        reader = H5RawReader(dataroot=dataroot, channels=np.array(['{:03d}'.format(i).encode() for i in range(1, 10)]))
        reader.read()
        assert reader.channel_name == 'bipolar_pairs'

    def test_with_events(self):
        dataroot = self.task_events_template.format(
            subject='R1358T',
            experiment='FR1',
            session=0
        )
        events = CMLEventReader(filename=dataroot).read()[:20]
        EEGReader(events=events,
                  channels=np.array(['{:03d}'.format(i).encode() for i in range(1, 10)]),
                  start_time=0.0,
                  end_time=0.5).read()

    def test_h5reader_empty_channels(self):
        dataroot = self.task_events_template.format(
            subject='R1358T',
            experiment='FR1',
            session=0
        )
        events = CMLEventReader(filename=dataroot).read()[:20]
        eeg = EEGReader(events=events, channels=np.array([]),
                        start_time=0.0, end_time=0.5).read()
        assert len(eeg.bipolar_pairs) > 0

    def test_h5reader_full_session(self):
        dataroot = self.dataroot_template.format(
            subject='R1354E',
            experiment='FR1',
            session=0,
            filename='R1354E_FR1_0_26Oct17_2006.h5'
        )
        EEGReader(session_dataroot=dataroot,channels=np.array([])).read()

    @pytest.mark.slow
    def test_timing(self):
        channels = np.array(['%.03d' % i for i in range(1, 100)])
        tic = time.time()
        with h5py.File(self.monopolar_file, 'r') as hfile:
            h5_data, _ = H5RawReader.read_h5file(hfile, channels=channels)
        toc = time.time()
        del h5_data
        h5dur = toc-tic
        tic = time.time()
        raw_data, _ = BinaryRawReader(dataroot=self.monopolar_dataroot,
                                    channels=channels).read()
        toc = time.time()
        del raw_data
        rawdur = toc-tic
        print('h5 file read in %s seconds'%h5dur)
        print('raw files read in %s seconds'%rawdur)
        assert h5dur <= rawdur



if __name__ == '__main__':
    test = TestH5Reader()
    test.setup_class()
    test.test_constructor()