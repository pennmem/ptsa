from collections import namedtuple
from typing import Any, Tuple
import os.path as osp
import struct
import warnings

import numpy as np
import numpy.typing as npt
import six

from ptsa.data.readers import BaseRawReader
from .params import ParamsReader


class BinaryRawReader(BaseRawReader):

    def __init__(self, **kwargs: Any) -> None:
        if 'channels' in kwargs:
            channels = kwargs['channels']
            if channels.dtype.names is not None and 'channel_1' in channels.dtype.names:
                raise IndexError

        super(BinaryRawReader, self).__init__(**kwargs)
        FileFormat = namedtuple('FileFormat', ['data_size', 'format_string'])
        self.file_format_dict = {
            'single': FileFormat(data_size=4, format_string='f'),
            'float32': FileFormat(data_size=4, format_string='f'),
            'short': FileFormat(data_size=2, format_string='h'),
            'int16': FileFormat(data_size=2, format_string='h'),
            'int32': FileFormat(data_size=4, format_string='i'),
            'double': FileFormat(data_size=8, format_string='d'),
            'float64': FileFormat(data_size=8, format_string='d')
        }

        self.file_format = self.file_format_dict['int16']

        # `dataroot` is declared as a `traits.api.Str` descriptor on the base
        # class; at runtime it holds a `str`. Pyright sees the unbound
        # descriptor type, so cast through `Any`.
        dataroot_attr: Any = self.dataroot
        p_reader = ParamsReader(dataroot=dataroot_attr)
        self.params_dict = p_reader.read()
        try:
            format_name = self.params_dict['format']
            try:
                self.file_format = self.file_format_dict[format_name]
            except KeyError:
                raise RuntimeError('Unsupported format: %s. Allowed format names are: %s' % (
                    format_name, list(self.file_format_dict.keys())))
        except KeyError:
            warnings.warn('Could not find data format definition in the params file. Will read the file assuming' \
                          ' data format is int16', RuntimeWarning)
        self.channel_labels_to_string()


    def samplerate(self) -> Any:
        # `BaseRawReader` does not actually expose a `samplerate()` method; the
        # value lives in `self.params_dict['samplerate']`. This override is
        # retained for backwards compatibility but simply delegates to the
        # parent attribute access.
        return super().samplerate()  # type: ignore[misc]

    def get_file_size(self) -> int:
        """
        :return: {int} size of the files whose core name (dataroot) matches self.dataroot. Assumes ALL files with this
        dataroot are of the same length and uses first channel to determin the common file length
        """
        # `channel_labels` is a `traits.api.CArray` descriptor on the base
        # class but holds a `np.ndarray` at runtime; pyright sees the unbound
        # descriptor type, so cast through `Any`.
        channel_labels: Any = self.channel_labels
        first_label = channel_labels[0]
        if isinstance(first_label, six.binary_type):
            ch = first_label.decode()
        else:
            ch = first_label
        dataroot_attr: Any = self.dataroot
        eegfname = dataroot_attr + '.' + ch
        return osp.getsize(eegfname)

    def read_file(
        self,
        filename: str,
        channels: np.ndarray,
        start_offsets: npt.NDArray[Any] = np.array([0]),
        read_size: int = -1,
    ) -> Tuple[npt.NDArray[np.float64], npt.NDArray[np.bool_]]:
        if read_size < 0:
            read_size = int(self.get_file_size() / self.file_format.data_size)
            self.read_size=read_size

        # allocate space for data
        eventdata: npt.NDArray[np.float64] = np.empty(
            (len(channels), len(start_offsets), read_size),
            dtype=np.float64,
        )
        eventdata.fill(np.nan)
        read_ok_mask: npt.NDArray[np.bool_] = np.ones(
            shape=(len(channels), len(start_offsets)), dtype=np.bool_
        )
        # loop over channels
        for c, channel in enumerate(channels):
            try:
                eegfname = filename + '.' + channel
            except TypeError:
                eegfname = filename + '.' + channel.decode()

            with open(eegfname, 'rb') as efile:
                # loop over start offsets
                for e, start_offset in enumerate(start_offsets):
                    # rejecting negative offset
                    if start_offset < 0:
                        read_ok_mask[c, e] = False
                        print(('Cannot read from negative offset %d in file %s' % (start_offset, eegfname)))
                        continue

                    # seek to the position in the file
                    efile.seek(self.file_format.data_size * start_offset, 0)

                    # read the data
                    data: bytes = efile.read(int(self.file_format.data_size * read_size))

                    # convert from string to array based on the format
                    # hard-codes little endian
                    fmt = '<' + str(int(len(data) / self.file_format.data_size)) + self.file_format.format_string
                    unpacked = np.array(struct.unpack(fmt, data))

                    # make sure we got some data
                    if len(unpacked) < read_size:
                        read_ok_mask[c, e] = False

                        print((
                            'Cannot read full chunk of data for offset ' + str(start_offset) +
                            'End of read interval  is outside the bounds of file ' + str(eegfname)))
                    else:
                        # append it to the eventdata
                        eventdata[c, e, :] = unpacked

        return eventdata, read_ok_mask

