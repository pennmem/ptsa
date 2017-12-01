PTSA
====

.. image:: https://travis-ci.org/pennmem/ptsa_new.svg?branch=master
    :target: https://travis-ci.org/pennmem/ptsa_new

.. image:: https://codecov.io/gh/pennmem/ptsa_new/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/pennmem/ptsa_new

.. image:: https://img.shields.io/conda/v/pennmem/ptsa.svg
    :target: https://anaconda.org/pennmem/ptsa

For documentation and tutorials, please see https://pennmem.github.io/ptsa_new/

Warning
-------

This is the development branch for PTSA 2.0. It is subject to large changes and
should not be considered stable.


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

   conda install -y numpy scipy xarray pywavelets swig

You can also optionally install FFTW. If it is not found, PTSA ships with a copy
of it and will automatically compile it. To install FFTW with conda on Linux or
Mac:

.. code-block:: shell-session

    conda install -y -c conda-forge fftw=3.3.4

Alternatively, it can be installed with the system package manager on Linux
(Debian-based command shown below):

.. code-block:: shell-session

    sudo apt-get install libfftw3-dev

or on Mac using homebrew:

.. code-block:: shell-session

    brew install fftw

Install PTSA:

.. code-block:: shell-session

   python setup.py install


Building conda packages
-----------------------

Before we begin building conda PTSA packages we need to set the PYTHON_BUILD_NUMBER system variable. For example,
if we are building PTSA conda package for Python 2.7 we set PYTHON_BUILD_NUMBER to be 2.7. On linux you do it via

.. code-block:: shell-session

    export PYTHON_BUILD_VERSION=2.7

on Windows:

.. code-block:: shell-session

    set PYTHON_BUILD_VERSION=2.7

Next, in the root conda environment, install ``conda-build``:

.. code-block:: shell-session

   conda install conda-build

Update the version number in ``conda.recipe/meta.yaml``.

Build packages with:

.. code-block:: shell-session

   conda build conda.recipe

To allow uploads you need to install anaconda-client:

.. code-block:: shell-session

    conda install anaconda-client

After that installing ``anaconda-client`` you need to to provide your anaconda.io login credentials:

.. code-block:: shell-session

    anaconda login

At this point you will be ready to upload newly built conda PTSA packages.
After the build is successfully completed you go to the directory where package tarballs have been generated
and type:

.. code-block:: shell-session

    anaconda upload --user pennmem ./ptsa-*.tar.bz2

**Hint:**  conda packages will be most likely generated in ``<conda installation dir>/conda-bld/<architecture_folder>``
where ``<architecture folder>`` denotes name of the arget architecture for which conda package was build. e.g. on 64-bit
Windows the architecture folder will be called ``win-64`` (hence conda packages will be generated in
``<conda installation dir>/conda-bld/win-64``
