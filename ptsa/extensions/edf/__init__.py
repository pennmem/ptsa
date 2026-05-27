"""EDF reader extension package.

Re-exports the pybind11-compiled :class:`EDFFile` from ``.edffile`` if the
extension is available; if not (e.g. PTSA built without pybind11) the
symbol is ``None`` and any attempt to construct it from
``ptsa.data.readers.edf.EDFRawReader`` raises at construction time.
"""
from __future__ import annotations

import warnings
from typing import Any

EDFFile: Any
try:
    from .edffile import EDFFile as EDFFile
except ImportError:
    warnings.warn("edffile extension module not found", UserWarning)
    EDFFile = None

__all__ = ["EDFFile"]
