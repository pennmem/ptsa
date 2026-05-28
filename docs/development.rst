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
but the slow ones, use the `-m "not slow"` command line option.

.. _pytest: https://docs.pytest.org/en/latest/

Building the documentation
--------------------------

The docs are built with Sphinx. The build needs ``ptsa`` importable (for
autodoc) plus the doc toolchain::

    pip install sphinx sphinx_rtd_theme nbsphinx

From the ``docs/`` directory, build the HTML site into ``_build/html``::

    cd docs
    sphinx-build -b html . _build/html
    # then open _build/html/index.html

The build should be warning-free. The example notebooks under
``docs/examples/`` are excluded by default because rendering them needs
``pandoc`` (not part of the standard environment). To include them, install
pandoc (e.g. ``conda install pandoc`` or ``brew install pandoc``) and set the
opt-in flag::

    PTSA_DOCS_BUILD_NOTEBOOKS=1 sphinx-build -b html . _build/html

The rendered site published to GitHub Pages lives in ``docs/html/``. That
directory is a *generated artifact* — it is regenerated at publish time with
``python maint/build_docs.py`` (which runs ``make html``) rather than being
committed on every change.
