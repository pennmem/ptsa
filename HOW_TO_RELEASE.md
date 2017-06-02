# How to release

The following steps should be taken when making an "official" release:

0. Run tests, make sure they pass.
1. Increment the version number in `ptsa/version.py`.
2. Increment the version number in `conda.recipe/meta.yaml`
3. Build conda packages on Mac, Linux, Windows: `python maint/build.py`
