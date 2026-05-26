"""Compatibility shim for the historical SWIG layout.

External lab code imports these symbols as::

    from ptsa.extensions.circular_stat.circular_stat import (
        circ_diff, circ_mean, compute_f_stat, compute_zscores, ...
    )

In the pybind11 build the compiled module is ``_circular_stat``; this file
just re-exports its public symbols so the SWIG-era import path still works.
"""

from ._circular_stat import (  # noqa: F401
    circ_diff,
    circ_diff_par,
    circ_diff_time_bins,
    circ_mean,
    compute_f_stat,
    compute_zscores,
    resultant_vector,
    resultant_vector_length,
    single_trial_outsample_ppc_features,
    single_trial_ppc_all_features,
)

__all__ = [
    "circ_diff",
    "circ_diff_par",
    "circ_diff_time_bins",
    "circ_mean",
    "compute_f_stat",
    "compute_zscores",
    "resultant_vector",
    "resultant_vector_length",
    "single_trial_outsample_ppc_features",
    "single_trial_ppc_all_features",
]
