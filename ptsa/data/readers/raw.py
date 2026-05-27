"""Deprecation shim: re-exports :class:`BaseRawReader` from its new location."""
import warnings

from .base import BaseRawReader

__all__ = ['BaseRawReader']

warnings.warn('BaseRawReader should be imported from ptsa.data.readers.base',
              DeprecationWarning)