PTSA
====

.. image:: https://travis-ci.org/pennmem/ptsa_new.svg?branch=master
    :target: https://travis-ci.org/pennmem/ptsa_new

For installation instructions, documentation, and tutorials please see
http://ptsa.readthedocs.io/en/latest/

Install via conda
-----------------

(Only available on Linux and Mac)

.. code-block:: shell-session

    conda install -c pennmem ptsa


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

In the root conda environment, install ``conda-build``:

.. code-block:: shell-session

   conda install conda-build

Build packages with:

.. code-block:: shell-session

   conda build conda.recipe

TODO:

* Automate building for multiple Python versions
* Make builds on Windows work
