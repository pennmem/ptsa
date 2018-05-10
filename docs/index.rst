PTSA - EEG Time Series Analysis in Python
=========================================

**PTSA** is an open source Python package that facilitates time-series
analysis of EEG signals. PTSA builds on :mod:`xarray` functionality
and provides several convenience tools that significantly simplify analysis of
EEG data.

The main object that you will be using in the new PTSA API is called
``TimeSeries``. ``TimeSeries`` is built on top of :class:`xarray.DataArray`.
:class:`xarray.DataArray`, defined in the :mod:`xarray` Python package,
represents N-D arrays. Because ``TimeSeries`` is a subclass of
:class:`xarray.DataArray` it has all the functionality of
:class:`xarray.DataArray` in addition to new functions it defines, used
specifically in EEG data analysis.

Besides ``TimeSeries``, PTSA has 2 main categories of objects: readers and
filters. Readers read various data formats (EEG files, event files, etc.) to
make input operations as smooth as possible. Filters take a ``TimeSeries``
object as an input and output a modified ``TimeSeries`` object.

If you'd like to learn Python via series of statistics tutorials look no further than
`introduction to computational statistics in Python <http://people.duke.edu/~ccc14/sta-663-2016/>`__


Installation
------------

Installing pre-built binaries
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The recommended way to install :mod:`ptsa` is to install with conda:

.. code-block:: shell-session

    conda install -c pennmem ptsa


Installing with conda from source
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you'd rather install the latest development version, you'll need to perform
the following steps:

Clone the git repository:

.. code-block:: shell-session

    git clone https://github.com/pennmem/ptsa_new.git

Install dependencies with conda:

.. code-block:: shell-session

   conda install -y numpy scipy xarray swig

Install PTSA:

.. code-block:: shell-session

   python setup.py install


Optional dependencies
^^^^^^^^^^^^^^^^^^^^^

For netCDF and IO
~~~~~~~~~~~~~~~~~

- `netCDF4 <https://github.com/Unidata/netcdf4-python>`__: recommended if you
  want to use :mod:`xarray` for reading or writing netCDF files
- `h5netcdf <https://github.com/shoyer/h5netcdf>`__: an alternative library for
  reading and writing netCDF4 files that does not use the netCDF-C libraries


Contents
--------

.. toctree::
   :maxdepth: 1

   examples/index
   ramdata
   filters
   api/index
   development
