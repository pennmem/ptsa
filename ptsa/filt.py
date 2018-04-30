#emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
#ex: set sts=4 ts=4 sw=4 et:
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See the COPYING file distributed along with the PTSA package for the
#   copyright and license terms.
#
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##

from scipy.signal import butter
from numpy import asarray
from scipy.signal import filtfilt


def buttfilt(dat,freq_range,sample_rate,filt_type,order,axis=-1):
    """Wrapper for a Butterworth filter.

    """

    # make sure dat is an array
    dat = asarray(dat)

    # reshape the data to 2D with time on the 2nd dimension
    #origshape = dat.shape
    #dat = reshape_to_2d(dat,axis)

    # set up the filter
    freq_range = asarray(freq_range)

    # Nyquist frequency
    nyq=sample_rate/2.

    # generate the butterworth filter coefficients
    [b,a]=butter(order,freq_range/nyq,filt_type)

    # loop over final dimension
    #for i in range(dat.shape[0]):
    #    dat[i] = filtfilt(b,a,dat[i])
    #dat = filtfilt2(b,a,dat,axis=axis)
    dat = filtfilt(b,a,dat,axis=axis)

    # reshape the data back
    #dat = reshape_from_2d(dat,axis,origshape)
    return dat
