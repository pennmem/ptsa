# How to release

The following steps should be taken when making an "official" release:

0. Update CHANGELOG.rst
1. Create a new `staging` branch
2. Run tests, make sure they pass.
3. Increment the version number in `ptsa/__init__.py`.
5. Build conda packages on Mac, Linux, Windows: `python maint/build.py`
6. Upload to Anaconda Cloud: `anaconda upload --user pennmem ./ptsa-*.tar.bz2`.
   This needs to be done from the directory where the tarballs are emitted.
7. Rebuild documentation: `maint/build_docs.py`
8. Create a pull request for the `staging` branch titled `Version x.y.z` where
   `x.y.z` is the new version number.
9. Merge.
10. Commit changes and tag. For example, if releasing version 1.1.999: `git tag v1.1.999`.
    Don't forget to push tags! `git push --tags`

## Dependencies to conda install

* swig
* conda >= 4.6
* fftw
* pytest
* pytest-cov

## Dependencies to pip install

* nbsphinx
* sphinx_rtd_theme
   
## TODO

- Automate build and upload process
