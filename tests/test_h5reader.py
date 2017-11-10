import os.path as osp
import time
import unittest
import pytest

import h5py
import numpy as np

from ptsa.data.readers.H5RawReader import H5RawReader
from ptsa.data.readers.BaseRawReader import BaseRawReader
from ptsa.data.readers.CMLEventReader import CMLEventReader
from ptsa.data.readers import EEGReader
from ptsa.test.utils import get_rhino_root, skip_without_rhino


@skip_without_rhino
class TestH5Reader(unittest.TestCase):
    def setUp(self):
        root = get_rhino_root()
        self.eeg_path_template = osp.join(
            root, 'data', 'eeg', '{subject:s}', 'behavioral', '{experiment:s}',
            'session_{session:d}', 'host_pc', '{timestamp:s}',
            'eeg_timeseries.h5'
        )

        self.dataroot_template = osp.join(
            root, 'protocols', 'r1', 'subjects', '{subject:s}', 'experiments',
            '{experiment:s}', 'sessions', '{session:d}', 'ephys',
            'current_processed', 'noreref', '{filename:s}'
        )

        # monopolar (old-format) HDF5 file
        self.monopolar_file = self.eeg_path_template.format(
            subject='R1275D',
            experiment='FR1',
            session=0,
            timestamp='20170531_170954'
        )

        # bipolar (new-format) HDF5 file
        self.bipolar_file = self.eeg_path_template.format(
            subject='R1354E',
            experiment='FR1',
            session=0,
            timestamp='20171026_160648'
        )

        self.monopolar_dataroot = osp.join(
            root, 'protocols', 'r1', 'subjects', 'R1275D', 'experiments', 'FR1',
            'sessions', '0', 'ephys', 'current_processed', 'noreref',
            'R1275D_FR1_0_31May17_2109'
        )
        self.channels = np.array(['%.03d' % i for i in range(1, 10)])

    @pytest.mark.only
    def test_h5reader_one_offset(self):
        channels = self.channels
        with h5py.File(self.monopolar_file, 'r') as hfile:
            h5_data, _ = H5RawReader.read_h5file(hfile, channels, [0], 1000)

        raw_timeseries, _ = BaseRawReader(dataroot=self.monopolar_dataroot,
                                          channels=channels,
                                          start_offsets=np.array([0]),
                                          read_size=1000).read()
        assert (raw_timeseries.data == h5_data*raw_timeseries.gain).all()

    def test_h5reader_many_offsets(self):
        offsets = np.arange(0, 210000, 3000)

        with h5py.File(self.monopolar_file, 'r') as hfile:
            h5_data, _ = H5RawReader.read_h5file(hfile, self.channels, offsets, 1000)

        raw_timeseries, _ = BaseRawReader(dataroot=self.monopolar_dataroot,
                                          channels=self.channels,
                                          start_offsets=offsets,
                                          read_size=1000).read()
        assert (raw_timeseries.data == h5_data*raw_timeseries.gain).all()

    def test_h5reader_out_of_bounds(self):
        offsets = np.arange(1000000, 4000000, 1000000)
        with h5py.File(self.monopolar_file, 'r') as hfile:
            h5_data, h5_mask = H5RawReader.read_h5file(hfile, self.channels, offsets, 1000)

        raw_data,raw_mask = BaseRawReader(dataroot=self.monopolar_dataroot,
                                          channels=self.channels,
                                          start_offsets=offsets,
                                          read_size=1000).read()
        assert(raw_mask == h5_mask).all()
        assert(h5_data[h5_mask] == raw_data.data[raw_mask]).all()

    def test_h5reader_constructor(self):
        dataroot = self.dataroot_template.format(
            subject='R1354E',
            experiment='FR1',
            session=0,
            filename='R1354E_FR1_0_26Oct17_2006.h5'
        )
        reader = H5RawReader(dataroot=dataroot, channels=np.array(['%.03d' % i for i in range(1, 10)]))
        reader.read()
        assert reader.channel_name == 'bipolar_pairs'

    def test_with_events(self):
        dataroot_format = osp.join(get_rhino_root(),'scratch','ptsa_test','R1308T', 'experiments', 'FR1', 'sessions', '3',
                                   'behavioral','current_processed','task_events.json')
        events = CMLEventReader(filename=dataroot_format).read()[:20]
        EEGReader(events=events,channels=np.array(['%.03d'%i for i in range(1,10)]),start_time=0.0,end_time=0.5).read()

    def test_h5reader_empty_channels(self):
        dataroot_format = osp.join(get_rhino_root(),'scratch','ptsa_test','R1308T', 'experiments', 'FR1', 'sessions', '3',
                                   'behavioral','current_processed','task_events.json')
        events = CMLEventReader(filename=dataroot_format).read()[:20]
        eeg = EEGReader(events=events,channels=np.array([]),start_time=0.0,end_time=0.5).read()
        assert len(eeg.bipolar_pairs)>0

    @pytest.mark.skip
    @pytest.mark.slow
    def test_h5_reader_timing(self):
        channels = np.array(['%.03d' % i for i in range(1, 100)])
        tic=time.time()
        h5_data,_ = H5RawReader.read_h5file(self.h5_dataroot, channels=channels)
        toc = time.time()
        del h5_data
        h5dur = toc-tic
        tic=time.time()
        raw_data,_ = BaseRawReader(dataroot=self.monopolar_dataroot, channels=channels).read()
        toc=time.time()
        del raw_data
        rawdur = toc-tic
        print('h5 file read in %s seconds'%h5dur)
        print('raw files read in %s seconds'%rawdur)
        assert h5dur<=rawdur



