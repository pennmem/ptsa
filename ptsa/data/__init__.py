# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 et:
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See the COPYING file distributed along with the PTSA package for the
#   copyright and license terms.
#
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##

from dimarray import Dim, DimArray, AttrArray
from timeseries import TimeSeries

from basewrapper import BaseWrapper
from arraywrapper import ArrayWrapper

try:
    from edfwrapper import EdfWrapper
except ImportError:
    print('Could not find compiled version of c library for handing edf files. If you want edf support, please run setup.py and compile this library')

from events import Events
