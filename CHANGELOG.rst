Changes
=======
Version 3.0.6
-------------
**2026.05.26**

Fixes the install-order pain that required a four-step ``mamba``
incantation to land PTSA alongside the rest of the CML stack. PTSA
now installs cleanly in a single conda/mamba solve with no manual
``numpy==1.24.4`` or ``traits<7`` pins, and the source tree is now
compatible with the modern numpy 2 / pandas 3 / traits 7 stack.

* Conda package now pins runtime numpy to the major version it was
  built against (``pin_compatible('numpy', max_pin='x')``). The
  precompiled morlet/circular_stat/edf extensions use the NumPy 1.x
  C API; without an upper bound, mamba was silently pairing the
  binary with NumPy 2.x → ``_ARRAY_API not found`` at import time.
* Removed ``pybind11`` from ``run:`` requirements (it is a build-only
  dep; the compiled .so does not need it at import time).
* Fixed ``traits.api.ListStr`` → ``traits.api.List(traits.api.Str)``
  in ``MonopolarToBipolarMapper``. ``ListStr`` was removed in
  ``traits>=7``; PTSA now works on traits 6 and 7.
* Source compatibility with NumPy 2: replaced the removed
  ``numpy.find_common_type`` with ``numpy.result_type`` in
  ``MatlabIO``, and ``numpy.core.records.fromarrays`` with the
  public ``numpy.rec.fromarrays`` in ``MonopolarToBipolarMapper``.
  When rebuilt against numpy 2 headers the binary now runs against
  any numpy 2.x.
* Source compatibility with pandas 3: ``TalReader.mkdtype`` now uses
  ``pd.api.types.is_string_dtype`` to coerce string columns,
  handling both the legacy ``object`` and the new ``StringDtype``
  (PDEP-14) representations.

Version 3.0.5
-------------
**2024.03.14**
Remove usage of deprecated and removed np.complex.

Version 3.0.4
-------------
**2023.08.08**
Build on numpy 1.24 for compatability with other pennmem packages

Version 3.0.3
-------------
**2023.08.03**
Update SWIG version to support python 3.11


Version 3.0.2
-------------
**2022.11.18**
Added support for hdf5 > 2.9.0


Version 3.0.1
-------------
**2021.11.08**
Bug fixes, automated conda deployment


Version 3.0.0
-------------
**2021.11.08**
Version 3.0 of PTSA is largely a cleanup release. Several deprecated features
have been removed and things have been reorganized.

What's New
^^^^^^^^^^
* Filter objects no longer accept a ``TimeSeries`` object as a positional argument. Rather, these are passed to the object's .filter method instead. This allows for reusing filters on multiple time series as well as adding filter pipeline capabilities. 
* Added a class decorator to ``TimeSeries`` that coerces the return type of xarray methods to be ``TimeSeries`` rather than ``xarray.DataArray``. 
* to_hdf and from_hdf now use xarray's recommended file saving method, netCDF. We use xarray built-ins to do I/O rather than in-house code via h5py.
* to_hdf and from_hdf now support pandas MultiIndexes as coordinates
Removals
^^^^^^^^

* ``TimeSeriesX`` backwards compatibility has been removed. Use ``TimeSeries``
  instead.
* the .filtered method has been removed. Initialize a ButterworthFilter and use .filter_with() instead


Version 2.0.10
--------------
**2020-08-21**

* Drop extra conda dependencies.

Version 2.0.9
-------------
**2020-05-07**

* Updates to conform with new xarray API.


Version 2.0.8
-------------
**2019-10-17**

* Resolved several warnings and a test failure in EEGReader.


Version 2.0.7
-------------
**2019-09-09**

* Identical to 2.0.6 but fixes a file upload error for the Python 3.7 version.


Version 2.0.6
-------------
**2019-08-15**

* MorletWaveletFilter now supports a ``complete`` parameter, defaulting to
  True, which uses a complete Morlet wavelet with a zero mean, and with its
  frequency corrected to be equivalent to a standard Morlet.  This
  significantly improves power and phase accuracy for small wavelet widths.


Version 2.0.4
-------------
**2018-08-31**

* ``TimeSeries.to_hdf`` once again uses a human-readable output format


Version 2.0.3
-------------

**2018-08-17**

* ``TimeSeries.to_hdf`` and ``from_hdf`` have been reverted to the previous
  behavior of base 64-encoding Numpy recarrays before writing to disk. This
  makes the stored files less human-readable, but offers the advantage of being
  much more robust.


Version 2.0.2
-------------

**2018-08-08**

New features:

* ``TimeSeries`` now has a ``filter_with`` method to make applying filters
  slightly easier (#211)

Fixes:

* Resource warnings were resolved by ensuring files get closed (#212)
* ``ButterworthFilter``'s ``freq_range`` argument is now coerced to a list (#214)

Other:

* Filter modules have been renamed to conform with PEP8 (#213). This should not
  affect normal usage since all filters are imported to the top-level filter
  namespace by default.


Version 2.0.1
-------------

**2018-07-18**

This is a minor bugfix release.

Issues addressed:

* Require a newer version of xarray and fix HDF5 serialization (#204)
* Optionally coerce datatypes to double for filters (#205)


Version 2.0.0
-------------

**2018-07-13**

Version 2.0 of PTSA is a major update which includes several breaking changes
including the removal of several packages and modules, name changes, and
deprecations.

PTSA 2.0 is the last major version to support loading of lab-specific data. In
future releases, all of this functionality will be removed in favor of using
the cmlreaders_ package which includes the ability to load timeseries data and
transform into a PTSA-compatible format.

.. _cmlreaders: https://github.com/pennmem/cmlreaders

Removals
^^^^^^^^

The following packages and modules have been removed:

* ``ptsa.plotting`` - see https://github.com/pennmem/ptsa_plot instead (#147)
* ``ptsa.stats`` - most functionality now exists in SciPy (#147)
* ``ptsa.emd``, ``ptsa.iwasobi``, ``ptsa.ica`` and ``ptsa.wica`` (#147)
* ``ptsa.filt`` - filtering is now contained primarily in ``ptsa.data.filters``
  (#158)
* Old time series class (fb08e6c2)
* All modules within ``ptsa.data`` that worked with the deprecated time series
  implementation

Renames
^^^^^^^

* ``TimeSeriesX`` has been renamed to ``TimeSeries`` and is now found in the
  ``ptsa.data.timeseries`` module (#141). ``TimeSeriesX`` still exists as an
  alias but will give a ``DeprecationWarning``.
* Most modules have been renamed to conform to PEP8 module naming conventions.
  These renames are generally not noticed by users if loading readers from the
  ``ptsa.data.readers`` namespace.

Other changes
^^^^^^^^^^^^^

* Reformatted output of ``TalReader.read``

    * The ``atlases`` field is a nested structured array, rather than an array of dictionaries
    * Most idioms for getting coordinates and atlas labels for an electrode should continue to work in the new format
    * The ``channels`` field has been changed from an object array of lists to an array of two integers

* Added IPython notebook demonstrating reading localization information with TalReader (thanks @LoganJF !)
* Replaced custom typing system with the ``traits`` package (b2f4609d)
* Improved ``TimeSeries.to_hdf`` (#138)


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

