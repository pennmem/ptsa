Development guidelines
======================

- All new functionality must include testing. Modifying existing functionality
  that is not already tested also requires adding testing.
- Don't commit directly to master; make a separate branch and submit a pull
  request instead.
- Run tests before merging into master
- Python 3 is the present and future. Use this cheatsheet_ for tips on writing
  code that is compatible with legacy Python 2 and modern Python 3.

.. _cheatsheet: http://python-future.org/compatible_idioms.html

Testing
-------

PTSA uses pytest_ as the test runner. Some tests are slow as they involve
processing large amounts of data, so these are marked as such. To run all tests
but the slow ones, use the ``-m "not slow"` command line option.

.. _pytest: https://docs.pytest.org/en/latest/
