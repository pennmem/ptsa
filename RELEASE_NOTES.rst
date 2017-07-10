Release Notes
=============

Version 1.1.2
-------------

- Added support for monopolar structures to TalReader
- Added 'float32', 'float64' as alternatives to 'single','double' in BaseRawReader.file_format_dict


Version 1.1.1
-------------
**2017-06-20**

- Added support for recarray coordinates with unicode in the ``to_hdf`` and
  ``from_hdf`` methods of ``TimeSeriesX``.


Bug Fixes:
----------
- Patched MorletWaveletFilter, ResampleFilter, ButterworthFilter classes to work with the new ``TimeSeriesX`` constructor
- Fixed bug in which filtering on the value of a field could fail if that field was not consistently present

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

- BaseEventReader and CMLEventReader are not "fool-proof" and may misinterpret types of certain columns and replace NaN with random integers
  This is due to the fact that numpy does not allow marking NaN in sht array of integers. Suggested solution is to use curate events files
  and replace NaNs with sentinel values (as was done for RAM dataset)
- ``to_hdf`` function of the TimeSeriesX does not work when elements of the structured array it tries to save are unicode.
  This is a known limitation of the h5py library. The temporary workaround it to replace all unicode strings with ASCII based equivalents

``