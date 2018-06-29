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

   conda install -y numpy scipy xarray swig

You can also optionally install FFTW. If it is not found, PTSA ships with a copy
of it and will automatically compile it. To install FFTW with conda on Linux or
Mac:

.. code-block:: shell-session

    conda install -y -c conda-forge fftw
    
Alternatively, it can be installed with the system package manager on Linux
(Debian-based command shown below):

.. code-block:: shell-session

    sudo apt-get install libfftw3-dev

or on Mac using homebrew:

.. code-block:: shell-session

    brew install fftw

On Rhino:

Some environment variables need to be set for the installation to succeed.
If your anaconda distribution is installed in `$HOME/anaconda3` and the environment name is `ptsa`,
set the `CPATH` and the `LD_LIBRARY_PATH` as follows:

.. code-block:: shell-session

    export CPATH=$HOME/anaconda3/envs/ptsa/include
    export LD_LIBRARY_PATH=$HOME/anaconda3/envs/ptsa/lib

Install PTSA:

.. code-block:: shell-session

   python setup.py install


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

The shell script `run_tests` will also run the test suite,
 assuming the environment is configured.

To skip tests that depend on Rhino the NO_RHINO environment variable must be set:

.. code-block:: shell-session

    export NO_RHINO=TRUE



Building conda packages
-----------------------

If you don't already have it installed, you'll need to install the conda build
tool:

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

Hints for Windows
^^^^^^^^^^^^^^^^^

You'll want to install Microsoft Visual Studio 2015 (or newer) community edition
in order to compile extensions. For environment variables to be setup correctly,
use the "Developer Command Prompt for VS20xy" which can be found for example
in ``Start->All Programs->Visual Studio 2015->Visual Studio Tools``.

License
-------

PTSA is licensed under the GNU GPL version 3.

This repository also includes:

* FFTW_ (GPL license)
* EDFLib_ (BSD license)

.. _FFTW: http://fftw.org/
.. _EDFLib: https://www.teuniz.net/edflib/
