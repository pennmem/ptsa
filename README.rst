PTSA
====

.. image:: https://github.com/pennmem/ptsa/actions/workflows/build.yml/badge.svg?branch=master
    :target: https://github.com/pennmem/ptsa/actions/workflows/build.yml
    :alt: build status

.. image:: https://codecov.io/gh/pennmem/ptsa/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/pennmem/ptsa

.. image:: https://img.shields.io/conda/v/pennmem/ptsa.svg
    :target: https://anaconda.org/pennmem/ptsa

For documentation and tutorials, please see https://pennmem.github.io/ptsa/


Install via conda
-----------------

Available on Linux, Mac, and Windows 64 bit:

.. code-block:: shell-session

    conda install -c pennmem -c conda-forge ptsa


Report bug or feature request
-----------------------------

To report a bug or a feature request please use  https://github.com/pennmem/ptsa/issues.

Build from source
-----------------

Install dependencies:

.. code-block:: shell-session

   conda install -y numpy scipy xarray swig traits

You will also need to install FFTW. To install FFTW with conda on Linux or Mac:

.. code-block:: shell-session

    conda install -y -c pennmem fftw

Alternatively, it can be installed with the system package manager on Linux
(Debian-based command shown below):

.. code-block:: shell-session

    sudo apt-get install libfftw3-dev

or on Mac using homebrew:

.. code-block:: shell-session

    brew install fftw

To read EDF__ files, you will also need to install pybind11:


.. code-block:: shell-session

    conda install -y -c conda-forge pybind11

__ http://www.edfplus.info/

System prerequisites
~~~~~~~~~~~~~~~~~~~~

The following must already be available on the system before you build
PTSA from source — ``pip`` cannot install them:

* ``swig >= 4.1`` on ``PATH`` (the morlet and circular_stat extensions
  are SWIG-wrapped).
* The FFTW3 development headers and shared library (e.g. via
  ``conda install -c conda-forge fftw`` or
  ``sudo apt-get install libfftw3-dev``).

Install PTSA
~~~~~~~~~~~~

The recommended path is ``pip install``. PTSA ships a ``pyproject.toml``
that declares ``numpy`` and ``pybind11`` as build-time requirements, so
pip can build the C++ extensions cleanly. ``numpy`` and ``pybind11``
must already be importable in the *current* env when you run pip
(separate from pip's build env), because ``setup.py`` reads the package
version by importing ``ptsa.__init__``:

.. code-block:: shell-session

   pip install numpy pybind11
   pip install --no-build-isolation .

For an editable dev install, add ``-e``:

.. code-block:: shell-session

   pip install --no-build-isolation -e .

Legacy fallback (works but ``setup.py install`` is deprecated by
setuptools):

.. code-block:: shell-session

   python setup.py install

.. note::

   ``pip install .`` *with* PEP 517 build isolation (the default) does
   not currently work end-to-end: pyproject.toml fixes the original
   ``ModuleNotFoundError: No module named 'numpy'`` build-time error,
   but ``setup.py`` separately imports ``ptsa`` at top level to read
   ``__version__``, which ``setuptools.build_meta`` cannot resolve
   inside its isolated build env. Use ``--no-build-isolation`` until
   that is refactored.

If you encounter problems installing, some environment variables may need to be
set, particularly if you installed FFTW with conda. If your anaconda
distribution is installed in ``$HOME/anaconda3`` and the environment name is
``ptsa``, set the ``CPATH`` and the ``LD_LIBRARY_PATH`` as follows:

.. code-block:: shell-session

    export CPATH=$HOME/anaconda3/envs/ptsa/include
    export LD_LIBRARY_PATH=$HOME/anaconda3/envs/ptsa/lib


Running Tests
-------------

To run the PTSA test suite locally, first set up a testing environment:

.. code-block:: shell-session

    conda env create -f environment.yml
    source activate ptsa

and then build build the extension modules and run the  test suite:

.. code-block:: shell-session

    python setup.py develop
    pytest tests/

The shell script `run_tests` will also run the test suite, assuming the
environment is configured.

To skip tests that depend on Rhino the NO_RHINO environment variable must be set:

.. code-block:: shell-session

    export NO_RHINO=TRUE

When running tests which require rhino access, the path to the root rhino
directory is guessed based on common mount points.


Building conda packages
-----------------------

See separte HOW_TO_RELEASE.md document! Alternatively, this repository is now set up to deploy automatically on tagged commits.


Continuous integration
----------------------

Every push to ``master`` and every pull request runs the GitHub Actions
workflow in ``.github/workflows/build.yml`` across a cross-platform
build matrix:

* **Operating systems:** ``ubuntu-latest``, ``macos-latest``,
  ``windows-latest``
* **Python:** 3.10, 3.11, 3.12, 3.13
* **NumPy:** 1.24 and 2.x (NumPy 1.24 wheels only ship for Python
  <=3.11, so the 3.12 / 3.13 cells are exercised only against NumPy 2)

Each cell does a full ``conda-build`` of ``conda.recipe/``, which both
compiles the C++ extensions (Morlet wavelet, circular statistics, EDF)
against the requested NumPy ABI and runs the entire pytest suite
inside conda-build's stripped-down test environment. A separate smoke
step then installs the resulting ``.conda`` artifact into a brand-new
environment to verify it lays down and imports outside the build tree.

When a tag matching ``v*`` is pushed, a follow-up ``deploy`` job
gathers every matrix artifact and uploads them to
`anaconda.org/pennmem <https://anaconda.org/pennmem/ptsa>`_ via the
``ANACONDA_TOKEN`` repository secret.

This workflow replaces the legacy TravisCI configuration; TravisCI
shut down most open-source builds in 2021 and the old ``.travis.yml``
no longer ran.


License
-------

PTSA is licensed under the GNU GPL version 3.

This repository also includes:

* FFTW_ (GPL license)
* EDFLib_ (BSD license)

.. _FFTW: http://fftw.org/
.. _EDFLib: https://www.teuniz.net/edflib/
