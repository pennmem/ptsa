import warnings

from .base import BaseEventReader, BaseRawReader, BaseReader
from .binary import BinaryRawReader
from .edf import EDFRawReader
from .eeg import EEGReader
from .events import CMLEventReader
from .hdf5 import H5RawReader
from .index import JsonIndexReader
from .localization import LocReader
from .netcdf import NetCDF4XrayReader
from .params import ParamsReader
from .tal import TalReader, TalStimOnlyReader

__all__ = [
    "BaseEventReader",
    "BaseRawReader",
    "BaseReader",
    "BinaryRawReader",
    "CMLEventReader",
    "EDFRawReader",
    "EEGReader",
    "H5RawReader",
    "JsonIndexReader",
    "LocReader",
    "NetCDF4XrayReader",
    "ParamsReader",
    "TalReader",
    "TalStimOnlyReader",
]

warnings.warn(
    "PTSA readers will be removed in a future release. Please consider using "
    "the cmlreaders package instead: https://github.com/pennmem/cmlreaders",
    FutureWarning
)
