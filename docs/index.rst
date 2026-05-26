PTSA - EEG Time Series Analysis in Python
=========================================

**PTSA** (Python Time-Series Analysis) is the Penn Computational
Memory Lab's open source toolbox for EEG analysis. Its primary use is
**fast multithreaded Morlet wavelet** power and phase computation on
multi-channel EEG data, exposed through a thin
:class:`~ptsa.data.timeseries.TimeSeries` wrapper around
:class:`xarray.DataArray`.

If you have come to PTSA looking for the wavelet transform, jump
straight to :ref:`morlet`.

Core concepts
-------------

* :class:`~ptsa.data.timeseries.TimeSeries` — an
  :class:`xarray.DataArray` subclass that carries a mandatory
  ``samplerate`` coord plus a handful of EEG-specific helpers
  (``resampled``, ``add_mirror_buffer``, ``baseline_corrected``,
  ``filter_with``, ``to_hdf`` / ``from_hdf``).
* :class:`~ptsa.data.filters.MorletWaveletFilter` — the canonical
  wavelet decomposition. Wraps a C++/FFTW kernel and can output
  power, phase, or the raw complex coefficients in one call.
* Auxiliary filters — :class:`~ptsa.data.filters.ButterworthFilter`,
  :class:`~ptsa.data.filters.ResampleFilter`,
  :class:`~ptsa.data.filters.MonopolarToBipolarMapper`, and
  :class:`~ptsa.data.filters.DataChopper`.

All filters share the same 3.0 calling convention:

.. code-block:: python

    from ptsa.data.filters import MorletWaveletFilter
    import numpy as np
    freqs = np.array([5.0, 10.0, 20.0])
    wf = MorletWaveletFilter(freqs=freqs, output='power', verbose=False)
    # `ts` is a TimeSeries; `result` is also a TimeSeries.
    # result = wf.filter(ts)

(The pre-3.0 "pass a ``TimeSeries`` into the constructor" style has
been removed.)


Installation
------------

Recommended (conda)
^^^^^^^^^^^^^^^^^^^

PTSA is published on the ``pennmem`` Anaconda channel and depends on
FFTW, so the cleanest install is via conda:

.. code-block:: shell-session

    conda install -c pennmem -c conda-forge ptsa

From source
^^^^^^^^^^^

Building from source requires SWIG ≥ 4.1 on ``PATH``, FFTW3 headers
and shared libraries, a C++14 compiler, and NumPy and (optionally)
pybind11 already installed in the build environment. From a fresh
clone:

.. code-block:: shell-session

    git clone https://github.com/pennmem/ptsa.git
    cd ptsa
    conda install -y numpy scipy xarray h5py swig fftw pybind11
    python setup.py build_ext --inplace
    pip install --no-build-isolation --no-deps -e .


Contents
--------

.. toctree::
   :maxdepth: 1

   morlet
   filters
   api/index
   development

.. only:: notebooks

   .. toctree::
      :maxdepth: 1

      examples/index

The worked notebook examples (``docs/examples/``) require ``pandoc``
on ``PATH`` for ``nbsphinx`` to render and are excluded from the
default build. Set ``PTSA_DOCS_BUILD_NOTEBOOKS=1`` (and install
``pandoc``) to add them to the toctree. The notebooks are also
browsable directly on GitHub:
https://github.com/pennmem/ptsa/tree/master/docs/examples


Legacy lab-data readers (deprecated)
------------------------------------

PTSA historically shipped a layer of lab-specific I/O readers under
``ptsa.data.readers`` (``BaseEventReader``, ``EEGReader``,
``TalReader``, ``JsonIndexReader``, etc.). These remain in the
package for backward compatibility but are **deprecated**; importing
any of them emits a ``FutureWarning``. New code should use the
`cmlreaders <https://github.com/pennmem/cmlreaders>`__ package
instead, which exposes the same data with a cleaner API. The
:ref:`ramdata` tutorial covers the legacy interface for users still
maintaining older pipelines.

.. toctree::
   :maxdepth: 1
   :hidden:

   ramdata
