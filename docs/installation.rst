.. _installing:

Installation
============

Required dependencies
---------------------

- Python 2.7
- `numpy <http://www.numpy.org/>`__ (1.7 or later)
- `pandas <http://pandas.pydata.org/>`__ (0.15.0 or later)
- `scipy <https://www.scipy.org/>`__ (0.17.0 or later)
- `xarray <http://xarray.pydata.org/en/stable/>`__ (0.6.0 or later , see also `bug fix for 0.7.x branch`_)
- `PyWavelets <http://www.pybytes.com/pywavelets/>`__
- `swig <http://www.swig.org>`__ (1.3 or later)
- working c/c++ compiler

.. _`bug fix for 0.7.x branch`:

xarray Bug fix
------------------

.. warning::
    xarray (0.7.x branch) has a bug that prevents it from handling properly DataArrays whose dimensions are numpy record arrays.
    PTSA actually relies on this functionality quite a lot so you have two choices:

    1. Downgrade to xarray 0.6.x branch (in which case you will be installing xray not xarray)
    2. Patch xarray code


Patching your xarray installation (versions 0.7.x only!)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To patch your existing xarray installation you need to replace

.. code-block:: python

    def array_equiv(arr1, arr2):

function in xarray/core/ops.py (it will be located in site-packages directory of your Python installation) with te following code:

.. code-block:: python

    def array_equiv(arr1, arr2):
        """Like np.array_equal, but also allows values to be NaN in both arrays
        """
        arr1, arr2 = as_like_arrays(arr1, arr2)
        if arr1.shape != arr2.shape:
            return False

        flag_array = (arr1 == arr2)

        # GH837, GH861
        # isnull fcn from pandas will throw TypeError when run on numpy structured array
        # therefore for dims that are np structured arrays we skip testing for nan

        try:

            flag_array |= (isnull(arr1) & isnull(arr2))

        except TypeError:
            pass

        return bool(flag_array.all())


.. note::
    This bug will be fixed in the upcoming release of xarray


Optional dependencies
---------------------

For netCDF and IO
~~~~~~~~~~~~~~~~~

- `netCDF4 <https://github.com/Unidata/netcdf4-python>`__: recommended if you
  want to use xarray for reading or writing netCDF files
- `h5netcdf <https://github.com/shoyer/h5netcdf>`__: an alternative library for
  reading and writing netCDF4 files that does not use the netCDF-C libraries



Instructions
------------

.. note::
    If you are reinstalling PTSA please go to `Reinstalling PTSA`_ first and follow the instructions

To download PTSA you can either clone PTSA repository by typing the following from your shell:

.. code-block:: bash

    mkdir PTSA_GIT
    cd PTSA_GIT
    git clone https://github.com/maciekswat/ptsa_new .
    git checkout ptsa_1.0.0

or click the following link:

https://github.com/maciekswat/ptsa_new/archive/ptsa_1.0.0.zip

which will download zipped repository to your machine.

.. note::
    It is a good idea to check the latest version of PTSA
    using https://github.com/maciekswat/ptsa_new page interface and replace `<latest_version>` in the checkout call below.

    .. code-block:: bash

        git checkout <latest_version>

    with the most recent version e.g.

    .. code-block:: bash

        git checkout ptsa_1.0.1


After you downloaded PTSA go to PTSA directory and run the following command

    .. code-block:: bash

        python setup.py install

This will start the installation process that will involve compilation of fftw library,
compilation of c/c++ PTSA extension modules and copying of Python files into '''site-packages'''
directory of your python distribution

Assuming everything went OK , at this point you should have PTSA distribution ready to run.


.. _`Reinstalling PTSA`:

Reinstalling PTSA
-------------------

Before you reinstall PTSA you should remove previous build files (C/C++ compiler outputs). To do so go to

.. code-block:: bash

    <YOUR_COPY_OF_PTSA>/build

and remove the directories that begin with

.. code-block:: bash

    lib
    temp

We will automate this process soon but for now some manual labor is requires

