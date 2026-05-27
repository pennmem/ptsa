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

Available for Linux (``linux-64``) and macOS (``osx-64`` / ``osx-arm64``):

.. code-block:: shell-session

    conda install -c pennmem -c conda-forge ptsa

.. note::

   There is no native Windows (``win-64``) package. On Windows, run PTSA
   under `WSL <https://learn.microsoft.com/windows/wsl/>`_: install a
   Linux distribution, then a Linux ``conda``/``miniforge`` inside it, and
   use the ``linux-64`` package above. The compiled extensions and the
   full test suite are validated on Linux in CI.


Report bug or feature request
-----------------------------

To report a bug or a feature request please use  https://github.com/pennmem/ptsa/issues.

Build from source
-----------------

Install dependencies:

.. code-block:: shell-session

   conda install -y -c conda-forge numpy scipy xarray pandas h5py netcdf4 traits six

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
PTSA from source — ``pip`` cannot install them (they are not Python
packages):

* A **C++ compiler**. The morlet, circular_stat, and edf extensions are
  C++ (pybind11). On Linux use ``gcc``/``g++`` (or conda's
  ``gxx_linux-64``); on macOS the Xcode command-line tools
  (``xcode-select --install``); on Windows, MSVC.
* **FFTW3** development headers and shared library (e.g.
  ``conda install -c conda-forge fftw`` or
  ``sudo apt-get install libfftw3-dev``). The morlet extension links
  against ``libfftw3``.

(``numpy`` and ``pybind11`` are also build-time requirements, but pip
installs them automatically into its build environment from
``pyproject.toml`` — you do not need to install them yourself.)

Install PTSA
~~~~~~~~~~~~

PTSA ships a ``pyproject.toml`` declaring its build-time requirements
(``setuptools``, ``wheel``, ``numpy``, ``pybind11``), so a standard pip
install builds the C++ extensions cleanly:

.. code-block:: shell-session

   pip install .

**Development (editable) install** — your source edits take effect
without reinstalling, the recommended setup for developing PTSA (and a
way to run a locally-built PTSA when the conda channel is unavailable).

pip compiles the C++ extensions from source, so a **C++ compiler and
FFTW must be in the environment first** — pip cannot install those (FFTW
is a native library, not a Python package). pip *does* provide
everything else automatically (``numpy``/``pybind11`` for the build, and
the runtime deps ``scipy``/``xarray``/``traits``/``h5py``/… on install).
A complete setup from scratch with conda:

.. code-block:: shell-session

   # 1. env with the native build prerequisites pip can't provide:
   #    FFTW + a C++ compiler.
   conda create -y -n ptsa-dev -c conda-forge python=3.11 pip fftw gxx_linux-64
   conda activate ptsa-dev

   # 2. editable install: pip builds the extensions against the FFTW
   #    above and pulls the Python runtime deps from PyPI.
   pip install -e .

On macOS, use the system clang instead of ``gxx_linux-64`` (drop it from
step 1 and run ``xcode-select --install`` once). FFTW can alternatively
come from the system package manager instead of conda
(``sudo apt-get install libfftw3-dev`` on Debian/Ubuntu, ``brew install
fftw`` on macOS) — see *System prerequisites* below.

If you would rather build against the ``numpy``/``pybind11`` already in
your environment (skipping pip's isolated build env), pass
``--no-build-isolation``:

.. code-block:: shell-session

   pip install --no-build-isolation -e .

Legacy fallback (works but ``setup.py install`` is deprecated by
setuptools):

.. code-block:: shell-session

   python setup.py install

If you encounter problems installing, some environment variables may need to be
set, particularly if you installed FFTW with conda. If your anaconda
distribution is installed in ``$HOME/anaconda3`` and the environment name is
``ptsa``, set the ``CPATH`` and the ``LD_LIBRARY_PATH`` as follows:

.. code-block:: shell-session

    export CPATH=$HOME/anaconda3/envs/ptsa/include
    export LD_LIBRARY_PATH=$HOME/anaconda3/envs/ptsa/lib


Running Tests
-------------

Install PTSA in editable mode first (see *Install PTSA* above), then add
the test tooling:

.. code-block:: shell-session

    conda install -y -c conda-forge pytest pytest-cov sybil

Both extras are required to run the suite as configured:

* ``sybil`` — the top-level ``conftest.py`` uses it to execute every
  ``.. code-block:: python`` example in ``docs/*.rst`` as a test, so
  pytest will not even start collecting without it.
* ``pytest-cov`` — satisfies the coverage options declared in
  ``setup.cfg`` (``--cov``). (Alternatively, disable them for a run with
  ``pytest -o addopts=""``.)

**By default a plain ``pytest`` run includes the rhino-only tests** —
about 30 tests that read lab data from the rhino filesystem (the
``ptsa.data.readers`` layer against real EEG / event / tal files). On
rhino they run normally; **anywhere else (a laptop, CI) they error**
with ``OSError: Rhino root not found!``, because the data isn't
present.

To run only the portable tests, set the ``NO_RHINO`` environment
variable, which skips the rhino-only ones:

.. code-block:: shell-session

    NO_RHINO=1 pytest

Either way the run covers the unit tests in ``tests/`` **and** the
documentation examples in ``docs/*.rst``. The ``run_tests`` shell script
wraps the ``NO_RHINO=1`` invocation, and CI always runs with
``NO_RHINO=1`` set.


Building conda packages
-----------------------

See separte HOW_TO_RELEASE.md document! Alternatively, this repository is now set up to deploy automatically on tagged commits.


Continuous integration
----------------------

Every push to ``master`` and every pull request runs the GitHub Actions
workflow in ``.github/workflows/build.yml`` across a cross-platform
build matrix:

* **Operating systems:** ``ubuntu-latest`` and ``macos-latest``.
  (Windows is not built — see the WSL note under *Install via conda*.)
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
