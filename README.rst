PTSA
====

.. image:: https://travis-ci.org/pennmem/ptsa_new.svg?branch=master
    :target: https://travis-ci.org/pennmem/ptsa_new

For installation instructions, documentation, and tutorials please see
http://ptsa.readthedocs.io/en/latest/

Installation
------------

Install dependencies:

.. code-block:: shell-session

   conda install -y numpy scipy xarray pywavelets swig

Install:

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
* Automate building on Windows
* Use conda-forge FFTW package for macOS/Linux to reduce build time
