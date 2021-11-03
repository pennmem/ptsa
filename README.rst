PTSA
====

.. image:: https://travis-ci.org/pennmem/ptsa_new.svg?branch=master
    :target: https://travis-ci.org/pennmem/ptsa_new

.. image:: https://codecov.io/gh/pennmem/ptsa_new/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/pennmem/ptsa_new

.. image:: https://img.shields.io/conda/v/pennmem/ptsa.svg
    :target: https://anaconda.org/pennmem/ptsa

For documentation and tutorials, please see https://pennmem.github.io/ptsa_new/


Install via conda
-----------------

Available on Linux, Mac, and Windows 64 bit:

.. code-block:: shell-session

    conda install -c pennmem ptsa


Report bug or feature request
-----------------------------

To report a bug or a feature request please use  https://github.com/pennmem/ptsa_new/issues.

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

Install PTSA:

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

See separte HOW_TO_RELEASE.md document!


License
-------

PTSA is licensed under the GNU GPL version 3.

This repository also includes:

* FFTW_ (GPL license)
* EDFLib_ (BSD license)

.. _FFTW: http://fftw.org/
.. _EDFLib: https://www.teuniz.net/edflib/
