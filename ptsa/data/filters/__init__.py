import logging
from .BaseFilter import BaseFilter
from .ButterworthFilter import ButterworthFilter
from .MonopolarToBipolarMapper import MonopolarToBipolarMapper
from .MorletWaveletFilter import MorletWaveletFilter
from .ResampleFilter import ResampleFilter
from .DataChopper import DataChopper

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

try:
    from .MorletWaveletFilterCppLegacy import MorletWaveletFilterCppLegacy
except ImportError:
    logger.warning('Could not import MorletWaveletFilterCppLegacy '
                   '(single-core C++ version of MorletWaveletFilter) '
                   'You can still use MorletWaveletFilter', exc_info=True)

try:
    from .MorletWaveletFilterCpp import MorletWaveletFilterCpp
except ImportError:
    logger.warning('Could not import MorletWaveletFilterCpp '
                   '(multi-core C++ version of MorletWaveletFilter) '
                   'You can still use MorletWaveletFilter', exc_info=True)
