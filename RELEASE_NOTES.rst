Release Notes
=============

Version 1.1.5
-------------

**2018-2-1**

Summary of changes:

* Removed further debug printing from Morlet filters (#111)
* Cleaned up ``ptsa.data.readers`` to be more in line with PEP8 naming (#112)
* Added support for reading EDF files (#113)
* Included ``h5py`` in conda requirements (#118)
* Suppressed unhelpful messages by default (#121). These can be "re-enabled" by adding a non-null log handler.
* Fixed incompatibility between ``TalReader`` and ``pairs.json`` (#116)
* Added a ``LocReader`` class that produces a flat view on ``localization.json`` files


Version 1.1.4
-------------

**2017-12-01**

Summary of changes:

* Removed ``cerr`` debugging output from compiled extension modules (#93)
* Changed to use ``h5py`` instead of ``pytables`` whenever HDF5 files are
  involved (#94)
* Fixed behavior of EEG reader to warn when removing "bad" events and optionally
  disable this behavior with a keyword argument (#95)
* Updated conversion from structured arrays to avoid potential issues in numpy
  1.13 (#103)


Version 1.1.3
-------------

**2017-09-28**

New Features
^^^^^^^^^^^^

- Added H5RawReader as a subclass of BaseRawReader, to read raw EEG data stored in HDF5 format
  - H5RawReader dataroots should have a file extension (e.g. '.h5'), as opposed to BaseRawReader dataroots
    which should *not* have a file extension
  - H5RawReader (and EEGReader, when reading data from HDF5 files) allow one to pass an empty list of channels to read,
    in which case data from all channels will be read, similar to passing -1 as the read_size to read an entire session.
- EEGReader returns TimeSeriesX with 'bipolar_pairs' axis instead of 'channels' axis when loading data recorded using
  bipolar referencing scheme.

Bug Fixes
^^^^^^^^^

- Fixed bug in JsonIndexReader in which passing two conditions with the same value (e.g "session=0,montage=0") would
  cause the reader to not return any values.
- `BaseEventReader.as_dataframe()` excludes the 'stim_params' field from the DataFrame it returns, since Pandas doesn't
  support nested DataFrames.

Version 1.1.2
-------------

**2017-08-29**

- Added support for monopolar structures to TalReader
- Added 'float32', 'float64' as alternatives to 'single','double' in BaseRawReader.file_format_dict
- Added `as_dataframe` methods to `BaseEventReader` and `JsonIndexReader` to
  simplify usage.
- Saving timeseries to HDF5 now includes attributes describing the PTSA version and creation time.


Version 1.1.1
-------------

**2017-06-20**

- Patched MorletWaveletFilter, ResampleFilter, ButterworthFilter classes to work with the new ``TimeSeriesX`` constructor.
- Fixed bug in which filtering on the value of a field could fail if that field was not consistently present.
- Added support for recarray coordinates with unicode in the ``to_hdf`` and
  ``from_hdf`` methods of ``TimeSeriesX``.
- Simplified importing ``JsonIndexReader``.


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
^^^^^^^^^

Fixed bugs related to missing ``samplerate`` in the TimeSeriesX. As of now ``TimeSeriesX`` by default will include ``samplerate`` attribute

Known Issues
^^^^^^^^^^^^

- BaseEventReader and CMLEventReader are not "fool-proof" and may misinterpret types of certain columns and replace NaN with random integers
  This is due to the fact that numpy does not allow marking NaN in sht array of integers. Suggested solution is to use curate events files
  and replace NaNs with sentinel values (as was done for RAM dataset)
- ``to_hdf`` function of the TimeSeriesX does not work when elements of the structured array it tries to save are unicode.
  This is a known limitation of the h5py library. The temporary workaround it to replace all unicode strings with ASCII based equivalents

