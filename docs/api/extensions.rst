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

    Returns the average angle of a vector of complex numbers, weighted by the magnitude of each number.
    Thus, circ_mean([1+0j, 1+0j, 0+1j]) == circ_mean([2+0j, 0+1j])

.. function:: circ_diff_time_bins(c1, c2, c_diff, cdiff_means)

    Computes the circular difference of ``c1`` and ``c2``, stores the result in ``c_diff``, then fills ``cdiff_means`` with the average
    binned differences.

    ``len(cdiff_means)`` must divide ``len(c1)``

    :returns: None

.. function:: compute_f_stat(phase_diffs, classes, f_stat)

    Performs an F-test, i.e. a circular ANOVA, comparing the variance of ``phase_diffs``
    when partitioned into two classes, and stores the results in fstat.

    :param phase_diffs: A matrix of phase differences
    :param classes: A boolean vector indicating which observation belongs in which class. Should be the same length as
                    the first dimension of ``phase_diffs``
    :param f_stat: An empty vector the same length as the second dimension of ``phase_diffs``


.. function:: compute_z_scores(m, n_perms)

.. function:: single_trial_ppc_all_features(recalls, wavelets, ppc_output, theta_sum_recalls, theta_sum_non_recalls, n_freqs, n_bps, n_threads)

.. function:: single_trial_ppc_all_features(wavelets, theta_avg_recalls, theta_avg_non_recalls, outsample_features,n_freqs, n_bps, n_threads)



ptsa.extensions.morlet
----------------------

Low-level functions for quickly computing Morlet wavelet decompositions.

It uses the following wavelet for frequency decomposition at frequency :math:`f` and with width :math:`w`
.. math::
   \Phi(t) =  (\sigma)^{-1/2} \pi^{-1/4} e^{-t^2/{2 \sigma^2}} e^{iwt/\sigma}
where
.. math::
    \sigma = w/{2\pi f}
The Gaussian envelope is only computed to a width of :math:`3.5\sigma` on each side of the peak. Any points beyond
that are rounded to 0.

The convolution of a signal :math:`\Sigma` with a wavelet :math:`\Phi` is done using the following algorithm:
.. math::
    \Sigma * \Phi = \hat{\hat Sigma \cdot \hat \Phi }/len(\Sigma)
in order to take advantage of the speed provided by the FFTW library.

:py:mod:`~ptsa.data.filters.MorletWaveletFilterCpp` provides a higher-level interface for these same functions.


.. automodule:: ptsa.extensions.morlet


ptsa.extensions.edf
-------------------
File-like wrapper around parts of edflib to provide an interface for reading the EDF+ family of EEG formats.
:py:mod:`ptsa.data.readers.EDFRawReader` provides a slightly higher-level interface for doing the same thing.

.. automodule:: ptsa.extensions.edf