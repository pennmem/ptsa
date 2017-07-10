# How to release

The following steps should be taken when making an "official" release:

0. Run tests, make sure they pass.
1. Increment the version number in `ptsa/version.py`.
2. Increment the version number in `conda.recipe/meta.yaml`
3. Commit changes and tag. For example, if releasing version 1.1.999: `git tag v1.1.999`.
   Don't forget to push tags! `git push --tags`
4. Build conda packages on Mac, Linux, Windows: `python maint/build.py`
5. Upload to Anaconda Cloud: `anaconda upload --user pennmem ./ptsa-*.tar.bz2`.
   This needs to be done from the directory where the tarballs are emitted.
6. Rebuild documentation: `maint/build_docs.sh`
7. Push documentation to Github: `cd /tmp/pennmem.github.io && git push`
   
## TODO

- Automate build and upload process
