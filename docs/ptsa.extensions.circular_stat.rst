ptsa.extensions.circular_stat package
*************************************


Submodules
==========


ptsa.extensions.circular_stat.circular_stat module
==================================================


Module contents
===============

:pyfunc: circ_diff(X,Y,Z):

    Computes the angular difference of the complex arrays X and Y, storing the value in Z

    :params:
    X,Y,Z : {np.array[np.complex*]}


:pyfunc: circ_diff_par(X,Y,Z, n_threads)

    Computes the angular difference of the complex arrays X and Y, storing the value in Z.
    The computation is performed in parallel over *n_threads* threads

    :params:
    X,Y,Z : {np.array[np.complex*]}
    n_threads: {int}



:pyfunc: circ_mean(Z)
    Returns the average angle of a vector of complex numbers, weighted by the magnitude of each number.
    Thus, circ_mean([1+0j, 1+0j, 0+1j]) == circ_mean([2+0j, 0+1j])


:pyfunc: circ_diff_time_bins(c1, c2, c_diff, cdiff_means)
    Computes the circular difference of c1 and c2, stores the result in c_diff, then fills cdiff_means with the average
    binned differences.

    len(cdiff_means) must divide len(c1)

    :returns: None

:pyfunc: compute_f_stat(phase_diffs, classes, fstat)

    :returns: None

:pyfunc: compute_z_scores(m, n_perms)

:pyfunc: single_trial_ppc_all_features(recalls, wavelets, ppc_output, theta_sum_recalls, theta_sum_non_recalls,
n_freqs, n_bps, n_threads)


:pyfunc: single_trial_ppc_all_features(wavelets, theta_avg_recalls, theta_avg_non_recalls, outsample_features,
n_freqs, n_bps, n_threads)


