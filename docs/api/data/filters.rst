Filters
=======

.. autoclass:: ptsa.data.filters.MorletWaveletFilter
    :members:

.. class:: ptsa.data.filters.MorletWaveletFilterCpp

    The same as ptsa.data.filters.MorletWaveletFilter,
    except it utilizes a C++ thread pool to parallelize the computations.

    Additional keyword arguments:

    * cpus `(int)` - The number of threads to launch

.. autoclass:: ptsa.data.filters.ButterworthFilter
    :members:

.. autoclass:: ptsa.data.filters.ResampleFilter
    :members:
