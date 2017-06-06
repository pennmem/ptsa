Release Notes
=============

Version 1.1.0
-------------

**2017-06-06**

- Added new demo suite (anotated ipython notebook examples)
- Improved documentation (currently still under development)
- Added conda installer for easy deployment
- Expanded test suite
- Cleaned up docstring documentation
- Provided support for both Python 2.x and 3.x on Windows, Linux, OSX
- Added Continuous Integration system to the development pipeline
- Added CMLEventsReader (CML stands for Computational Memory Lab) that by default reads events data "as-is" without doing any pre-processing
- Serialization of TimeSeriesX object to HDF5  

Bug Fixes
---------

Fixed bugs related to missing ``samplerate`` in the TimeSeriesX. As of now ``TimeSeriesX`` by default will include ``samplerate`` attribute

Known Issues
------------

BaseEventreader and CMLEventReader are not "fool-proof" and may misinterpret types of certain columns and replace NaN with random integers
This is due to the fact that numpy does not allow marking NaN in sht array of integeers. Suggested solution is to use curate events files 
and replace NaNs with sentinel values (as was done for RAM dataset)
