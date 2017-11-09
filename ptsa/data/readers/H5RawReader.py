from .BaseRawReader import BaseRawReader
import numpy as np
import h5py
import os.path as osp


class H5RawReader(BaseRawReader):
    """Class for reading raw EEG data stored in HDF5 format."""
    def __init__(self, **kwargs):
        """
        :param kwds:allowed values are:
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
        _,data_ext = osp.splitext(kwargs['dataroot'])
        assert len(data_ext), 'Dataroot missing extension'
        super(H5RawReader, self).__init__(**kwargs)

    def read_file(self, filename, channels, start_offsets=np.array([0]), read_size=-1):
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
            if len(channels)==0:
                channels = self.channels = np.array(['{:03d}'.format(x) for x in eegfile.root.ports[:]])
            if 'bipolar_info' in eegfile and ('monopolar_possible' in eegfile and not eegfile['/monopolar_possible'][0]):
                if not (np.in1d(channels, eegfile['/bipolar_info/ch0_label']).all()):
                    raise IndexError('Channel[s] %s not in recording'%(
                        channels[~np.in1d(channels, eegfile['/bipolar_info/ch0_label'])])
                                     )
                channel_mask = np.in1d(eegfile['/bipolar_info/ch0_label'], channels)
                self.channels = np.array(zip(eegfile['/bipolar_info/ch0_label'][channel_mask],
                                          eegfile['/bipolar_info/ch1_label'][channel_mask]),
                                        dtype=[('ch0', int), ('ch1', int)]).view(np.recarray)

                self.channel_name = 'bipolar_pairs'
            event_data,read_ok_mask = self.read_h5file(eegfile, channels if self.channel_name=='channels' else self.channels.ch0
                                                       , start_offsets, read_size)
            if self.read_size==-1:
                self.read_size = max(event_data.shape)
            return event_data,read_ok_mask

    @staticmethod
    def read_h5file(eegfile, channels, start_offsets=np.array([0]), read_size=-1):
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
        channels_to_read = np.where(np.in1d(ports, channels.astype(int)))[0]
        if read_size < 0:
            if 'orient' in timeseries.attrs and timeseries.attrs['orient'] == 'row':
                eventdata = timeseries[:, channels_to_read].T
            else:
                eventdata = timeseries[channels_to_read, :]
            return eventdata[:, None, :], np.ones((len(channels), 1)).astype(bool)

        else:
            eventdata = np.empty((len(channels), len(start_offsets), read_size),
                                 dtype=np.float) * np.nan
            read_ok_mask = np.ones((len(channels), len(start_offsets))).astype(bool)
            for i, start_offset in enumerate(start_offsets):
                try:
                    if 'orient' in timeseries.attrs and timeseries.attrs['orient'] == 'row':
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

            return eventdata, read_ok_mask
