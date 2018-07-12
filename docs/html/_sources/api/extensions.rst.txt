Extension Modules
=================

C/C++ extension modules, for accelerated calculations.

ptsa.extensions.circular_stat
-----------------------------

.. automodule:: ptsa.extensions.circular_stat
    :members:
    :undoc-members:

.. py:function:: circ_diff(X,Y,Z)

    Computes the angular difference of the complex arrays X and Y, storing the value in Z

    :param X,Y,Z: np.array[np.complex]


.. function:: circ_diff_par(X,Y,Z, n_threads)

    Computes the angular difference of the complex arrays X and Y, storing the value in Z.
    The computation is performed in parallel over ``n_threads`` threads

    :param X,Y,Z: np.array[np.complex]
    :param n_threads: int

.. function:: circ_mean(Z)

    Returns the average angle of a vector of complex numbers,
    weighted by the magnitude of each number.
    Thus, circ_mean([1+0j, 1+0j, 0+1j]) == circ_mean([2+0j, 0+1j])

.. function:: circ_diff_time_bins(c1, c2, c_diff, cdiff_means)

    Computes the circular difference of ``c1`` and ``c2``,
    stores the result in ``c_diff``, then fills ``cdiff_means`` with the average
    binned differences.

    ``len(cdiff_means)`` must divide ``len(c1)``

    :returns: None

.. function:: compute_f_stat(phase_diffs, classes, f_stat)

    Performs an F-test, i.e. a circular ANOVA, comparing the variance of ``phase_diffs``
    when partitioned into two classes, and stores the results in fstat.

    :param phase_diffs: A matrix of phase differences
    :param classes: A boolean vector indicating which observation belongs in which class Should be the same length as the first dimension of ``phase_diffs``

    :param f_stat: An empty vector the same length as the second dimension of ``phase_diffs``

.. function:: compute_z_scores(m, n_perms)

.. function:: single_trial_ppc_all_features(recalls, wavelets, ppc_output,\
    theta_sum_recalls, theta_sum_non_recalls, n_freqs, n_bps, n_threads)

.. function:: single_trial_ppc_all_features(wavelets, theta_avg_recalls,\
    theta_avg_non_recalls, outsample_features,n_freqs, n_bps, n_threads)


ptsa.extensions.morlet
----------------------

.. py:module:: ptsa.extensions.morlet

Low-level extension module for quickly computing Morlet wavelet decompositions.

This module uses the following wavelet for frequency :math:`f` and Gaussian width :math:`w`:

.. math::

    \Phi(t) =  \sigma^{-\frac{1}{2}} \pi^{-\frac{1}{4}}
    e^{\frac{-t^2}{{2 \sigma^2}}} e^{\frac{iwt}{\sigma}}

where

.. math::

    \sigma = \frac{w}{2\pi f}

The Gaussian envelope is only computed to a width of :math:`3.5\sigma`
on each side of the peak. Any points beyond that are rounded to 0.

The convolution of a signal :math:`\Psi` with a wavelet :math:`\Phi`
is computed using the identity

.. math::

    \Psi * \Phi = N^{-1} \big(\widehat{\hat{\Psi} \cdot \hat \Phi }\big)

where :math:`N` is the number of samples in the the signal :math:`\Psi`,
in order to take advantage of the speed provided by the FFTW library.

.. code-block:: python
    :caption: Example:

    signal = #... A 1D array
    n_freqs = 10
    pow_mat = np.empty(shape=n_freqs*len(signal),dtype=float)
    transform = MorletWaveletTransform(width=4,
                                       low_freq=3,
                                       high_freq=100,
                                       nf=n_freqs,
                                       sample_freq=1000,
                                       signal_len = len(signal)
                                       )
    transformed_signal = transform.multiphasevec(signal,pow_mat).reshape((n_freqs,-1))

.. seealso::

    :mod:`ptsa.data.filters.MorletWaveletFilterCpp`


.. :class:: MorletWaveletTransform

    Implementation of the Morlet wavelet transform. Should be constructed
    using either `freqs` or using `low_freq` and `high_freq`,
    in which case an array of `nf` log-spaced frequencies between
    `low_freq` and `high_freq` is used.

    :param width: The width of the Gaussian window
    :param freqs: An array of frequencies to use in the decomposition
    :param low_freq: Lowest frequency to use
    :param high_freq: Highest frequency to use
    :param nf: The number of frequencies to use. If `freqs` is present,
        this should be the length of `freqs`.

    :param sample_freq: The sampling rate of the signal, in Hz
    :param signal_len: The size of the array containing the signal

    .. py:method:: multiphasevec(signal,powers, phases=None)

    .. py:method:: multiphasevec_c(signal,wavelets)



ptsa.extensions.edf
-------------------
File-like wrapper around parts of EDFlib_ to provide an interface
for reading the EDF+ family of EEG formats.
:mod:`ptsa.data.readers.EDFRawReader` provides a
slightly higher-level interface for doing the same thing.

.. class:: ChannelInfo

    Channel data including label, number of samples, etc. These objects are
    returned by :meth:`EDFFile.get_channel_info`, and have the following
    read-only attributes:

    :ivar str label: The name of the channel
    :ivar int smp_in_file: Number of samples in file
    :ivar float phys_max: Maximum representable value in physical units
    :ivar float phys_min: Minimum representable value in physical units
    :ivar int dig_max: Maximum representable value in digital units
    :ivar int dig_min: Minimum representable value in digital units
    :ivar int smp_in_datarecord: Number of samples stored in one record
    :ivar str physdimension: Dimension of physical units
    :ivar str prefilter: Type of prefiltering performed on signal
    :ivar str transducer: Transducer type (e.g. 'AgAgCl electrode')

.. class:: EDFFile

    Reads the EDF family of files.

    This class utilizes EDFlib_ to read EDF/BDF/EDF+/BDF+ files.

    .. _EDFlib: https://www.teuniz.net/edflib/

    .. method:: __init__(filename)

        :param str filename:

    .. method:: get_channel_info(channel)

        Return the information on a given channel

        :param channel: int

    .. method:: get_channel_numbers(channel_names)

    .. method:: get_samplerate(channel)

    .. method:: read_samples(channels,samples,offset)

        Read samples from a list of channels. Channels
        can be specified by either a list of numbers or a list of labels.
