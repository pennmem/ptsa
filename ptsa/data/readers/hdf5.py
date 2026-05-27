import os.path as osp
from typing import Any, Tuple

import h5py
import numpy as np
import numpy.typing as npt

from ptsa.data.readers import BaseRawReader

__all__ = [
    'H5RawReader',
]


class H5RawReader(BaseRawReader):
    """Class for reading raw EEG data stored in HDF5 format."""
    def __init__(self, **kwargs: Any) -> None:
        """
        :param kwargs: allowed values are:
        -------------------------------------
        :param dataroot {str} -  Full name of hdf5 file. Normally this is the eegfile field from events record

        :param channels {list} - list of channels (list of strings) that should be read.
            If empty, all channels are read. If a channel passed to the reader was not recorded from, any attempt to read
            will result in an IndexError.
        :param start_offsets {ndarray} -  array of ints with read offsets.
        :param read_size {int} - size of the read chunk. If -1 the entire file is read
        --------------------------------------
        :return:None
        """
        _, data_ext = osp.splitext(kwargs['dataroot'])
        assert len(data_ext), 'Dataroot missing extension'
        super(H5RawReader, self).__init__(**kwargs)
        channels = self.channels
        if channels.dtype.names is not None:
            if 'channel_1' not in channels.dtype.names:
                raise IndexError('Cannot load bipolar data from monopolar channel list')
            kwargs['channels'] = channels['channel_1']
        super(H5RawReader, self).__init__(**kwargs)
        with h5py.File(self.dataroot, 'r') as eegfile:
            if 'samplerate' in eegfile:
                samplerate_ds = eegfile['samplerate']
                assert isinstance(samplerate_ds, h5py.Dataset)
                self.params_dict['samplerate'] = samplerate_ds[()]
        self.channels = channels
        self.channel_labels_to_string()


    def read_file(
        self,
        filename: str,
        channels: npt.NDArray[Any],
        start_offsets: npt.NDArray[Any] = np.array([0]),
        read_size: int = -1,
    ) -> Tuple[npt.NDArray[Any], npt.NDArray[np.bool_]]:
        """
        Overloads BaseRawReader.read_file(). Does some mangling of the channels parameter if it is empty or if the
        HDF5 file is a bipolar recording

        :param filename: The name of the file to read
        :param channels: The channels to read from the file
        :param start_offsets: The indices in the array to start reading at
        :param read_size: The number of samples to read at each offset.
        :return: event_data: The EEG data corresponding to each offset
        :return: read_ok_mask: Boolean mask indicating whether each offset was read successfully.
        """
        with h5py.File(self.dataroot, 'r') as eegfile:
            if len(channels) == 0:
                ports_ds = eegfile['/ports']
                assert isinstance(ports_ds, h5py.Dataset)
                channels_ = self.channel_labels = np.array(
                    ['{:03d}'.format(x).encode() for x in ports_ds[:]]
                )
            else:
                channels_ = channels
            try:
                monopolar_ds = eegfile['/monopolar_possible']
                assert isinstance(monopolar_ds, h5py.Dataset)
                monopolar_possible = bool(monopolar_ds[0])

                if 'bipolar_info' in eegfile and not monopolar_possible:
                    ch0_label_ds = eegfile['/bipolar_info/ch0_label']
                    ch1_label_ds = eegfile['/bipolar_info/ch1_label']
                    assert isinstance(ch0_label_ds, h5py.Dataset)
                    assert isinstance(ch1_label_ds, h5py.Dataset)
                    ch0_label = ch0_label_ds[:]
                    ch1_label = ch1_label_ds[:]

                    if not (np.isin(channels_, ch0_label).all()):
                        raise IndexError('Channel[s] %s not in recording' % (
                            channels_[~np.isin(channels_, ch0_label)]))
                    channel_mask = np.isin(ch0_label, channels_)
                    self.channel_labels = np.rec.array(
                        list(
                            zip(ch0_label[channel_mask],
                                ch1_label[channel_mask]),
                        ),
                        dtype=[('ch0', int), ('ch1', int)])

                    is_bipolar = True
                else:
                    is_bipolar = False
            except KeyError:
                is_bipolar = False

            channels_ = channels_ if not is_bipolar else self.channel_labels['ch0']
            event_data, read_ok_mask = self.read_h5file(eegfile, channels_,
                                                        start_offsets, read_size)
            if self.read_size == -1:
                self.read_size = max(event_data.shape)
            if len(channels) == 0:
                self.channels = self.channel_labels
            return event_data, read_ok_mask

    @staticmethod
    def read_h5file(
        eegfile: h5py.File,
        channels: npt.NDArray[Any],
        start_offsets: npt.NDArray[Any] = np.array([0]),
        read_size: int = -1,
    ) -> Tuple[npt.NDArray[Any], npt.NDArray[np.bool_]]:
        """
        Reads raw data from HDF5 files into a numpy array of shape (len(channels),len(start_offsets), read_size).
        For each channel and offset, indicates whether the data at that offset on that channel could be read successfully.

        :param eegfile: An open HDF5 file
        :param channels: The channels to read from the file
        :param start_offsets: The indices in the array to start reading at
        :param read_size: The number of samples to read at each offset.
        :return: event_data: The EEG data corresponding to each offset
        :return: read_ok_mask: Boolean mask indicating whether each offset was read successfully.

        """
        timeseries = eegfile['/timeseries']
        ports = eegfile['/ports']
        assert isinstance(timeseries, h5py.Dataset)
        assert isinstance(ports, h5py.Dataset)
        channels_to_read = np.where(np.isin(ports[:], channels.astype(int)))[0]
        if read_size < 0:
            if 'orient' in timeseries.attrs and timeseries.attrs['orient'] == 'row':
                eventdata = timeseries[:, channels_to_read].T
            else:
                eventdata = timeseries[channels_to_read, :]
            return eventdata[:, None, :], np.ones((len(channels), 1)).astype(bool)

        else:
            eventdata = np.empty((len(channels), len(start_offsets), read_size),
                                 dtype=np.float64)
            eventdata.fill(np.nan)
            read_ok_mask = np.ones((len(channels), len(start_offsets))).astype(bool)
            for i, start_offset in enumerate(start_offsets):
                if start_offset<0:
                    print('Cannot read negative offset %s '%start_offset)
                    read_ok_mask[:,i] = False
                else:
                    try:
                        if 'orient' in timeseries.attrs.keys() and timeseries.attrs['orient'] == b'row':
                            data = timeseries[start_offset:start_offset + read_size, channels_to_read].T
                        else:
                            data = timeseries[channels_to_read, start_offset:start_offset + read_size]
                        if data.shape[-1] == read_size:
                            eventdata[:, i, :] = data
                        else:
                            print(
                                'Cannot read full chunk of data for offset ' + str(start_offset) +
                                'End of read interval  is outside the bounds of file ' + eegfile.filename)
                            read_ok_mask[:, i] = False
                    except IndexError:
                        print(
                            'Cannot read full chunk of data for offset ' + str(start_offset) +
                            'End of read interval  is outside the bounds of file ' + eegfile.filename)
                        read_ok_mask[:, i] = False

            if np.isnan(eventdata).all():
                raise RuntimeError("All eventdata is nan!")

            return eventdata, read_ok_mask
