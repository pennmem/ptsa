from .morlet import *
from ._python_reference import python_morlet_wavelet as _python_morlet_wavelet


def get_time_domain_wavelet(freq, width, samplerate, complete=True):
    """Python reference implementation of the wavelet PTSA convolves with."""
    return _python_morlet_wavelet(freq, width, samplerate, complete=complete)
