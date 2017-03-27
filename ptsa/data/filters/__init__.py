from .BaseFilter import BaseFilter
from .ButterworthFilter import ButterworthFilter
from .MonopolarToBipolarMapper import MonopolarToBipolarMapper
from .MorletWaveletFilter import MorletWaveletFilter
from .ResampleFilter import ResampleFilter
from .DataChopper import DataChopper


try:
    from .MorletWaveletFilterCppLegacy import MorletWaveletFilterCppLegacy

except ImportError as ie:
    print('Could not import MorletWaveletFilterCppLegacy (single-core C++ version of MorletWaveletFilter): '+ str(ie))
    print('You can still use MorletWaveletFilter')

try:
    from .MorletWaveletFilterCpp import MorletWaveletFilterCpp
except ImportError as ie:
    print('Could not import MorletWaveletFilterCpp (multi-core C++ version of MorletWaveletFilter): '+ str(ie))
    print('You can still use MorletWaveletFilter')
