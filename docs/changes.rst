Changelog
=========

Version 1.1.1
-------------

**Unreleased**

- Added support for recarray coordinates with unicode in the ``to_hdf`` and
  ``from_hdf`` methods of ``TimeSeriesX``.

Version 1.1.0
-------------

**2017-06-02**

- Greatly simplified the build process from source and included recipes for
  building conda packages
- Added support for modern versions of Python
- Improved unit testing
- Improved documentation and added example Jupyter notebooks
- Added support for EEG data stored in ``int32`` format
- Improved ``TimeSeriesX`` functionality by adding an ``append`` method and a
  way to directly save to and load from HDF5 files
- Fixed several bugs
