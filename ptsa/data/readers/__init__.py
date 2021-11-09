import warnings

from .base import *
from .edf import EDFRawReader
from .eeg import EEGReader
from .events import *
from .hdf5 import H5RawReader
from .index import JsonIndexReader
from .netcdf import NetCDF4XrayReader
from .params import ParamsReader
from ptsa.data.readers.base import BaseRawReader
from .tal import *
from .binary import BinaryRawReader
from .localization import LocReader

warnings.warn(
    "PTSA readers will be removed in a future release. Please consider using "
    "the cmlreaders package instead: https://github.com/pennmem/cmlreaders",
    FutureWarning
)
