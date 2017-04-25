.. _installing:

Installation
============

Installing with conda from source
---------------------------------

.. tip::

   When experimenting with PTSA, you may want to create a fresh conda
   environment. You can create one with::

       conda create -n ptsa python=$VERSION

   where ``$VERSION`` is whatever Python version you're using.

After cloning the git repository, install dependencies:

.. code-block:: shell-session

   conda install -y numpy pandas scipy xarray pywavelets swig

Install PTSA:

.. code-block:: shell-session

   python setup.py install


Optional dependencies
---------------------

For netCDF and IO
~~~~~~~~~~~~~~~~~

- `netCDF4 <https://github.com/Unidata/netcdf4-python>`__: recommended if you
  want to use xarray for reading or writing netCDF files
- `h5netcdf <https://github.com/shoyer/h5netcdf>`__: an alternative library for
  reading and writing netCDF4 files that does not use the netCDF-C libraries
