.. PTSA documentation master file, created by
   sphinx-quickstart on Wed Jun  1 13:07:22 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

PTSA - EEG Time Series Analysis in Python
=========================================

**PTSA**  is an open source project and Python package that facilitates time-series
analysis of EEG signals using Python. PTSA builds on xarray functionality
and provides several convenience tools that significantly simplify analysis of the EEG data..

To use all features provided by PTSA you will need to install several dependencies:
xarray, scipy, numpy, PyWavelets and make sure you have working C/C++ compiler on your machine when you install PTSA

The main object that you will be using in the new PTSA API is called ``TimeSeriesX``. ``TimeSeriesX`` is built on
top of ``xarray.DataArray``. ``xarray.DataArray``, defined in the ``xarray`` Python package, represents N-D arrays.
Because ``TimeSeriesX`` is a subclass of ``xarray.DataArray`` it has all the functionality of ``xarray.DataArray``
in addition to new functions it defines, used specifically in EEG data analysis.

.. note::
    In legacy versions of PTSA the object representing time series is called ``TimeSeries`` and is built on
    top of custom-written ``dimarray`` module. To keep the old analysis code written for older PTSA versions running,
    we prepended letter **X** to the object representing time-series in the new PTSA , hence the name ``TimeSeriesX``.


Besides ``TimeSeriesX``, PTSA has 3 main categories of objects: readers, writers, filters. Readers ,
read various data formats (e.g eeg files, bipolar electrodes files etc..) to make input operations as smooth as possible.
Writers (still under development) will output data in several formats (currently only NetCDF output is supported). Filters
take as an input ``TimeSeriesX`` object and output diffrent ``TimeSeriesX`` object. Most of the tasks
related to EEG analysis will rely on using those 3 categories of PTSA objects.

If you'd like to learn Python via series of statistics tutorials look no further than
`introduction to computational statistics in Python <http://people.duke.edu/~ccc14/sta-663-2016/>`__



Contents:

.. toctree::
   :maxdepth: 1

   installation
   tutorial
   ramdata

