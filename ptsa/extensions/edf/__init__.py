import warnings

try:
    from .edffile import EDFFile
except ImportError:
    warnings.warn("edffile extension module not found", UserWarning)
    EDFFile = None
