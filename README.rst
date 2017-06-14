PTSA
====

.. image:: https://travis-ci.org/pennmem/ptsa_new.svg?branch=master
    :target: https://travis-ci.org/pennmem/ptsa_new

For documentation and tutorials, please see https://pennmem.github.io/ptsa/

Install via conda
-----------------

Available on Linux, Mac, and Windows 64 bit:

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

TODO:

* Automate building for multiple Python versions
* Make builds on Windows work
