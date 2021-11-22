# How to release

As of November 2021 / the release of PTSA 3.0.0, the ptsa repository is configured for automated deployment on tagged commits via TravisCI through
pennmem's open source account. The script at maint/deploy.sh is run automatically and builds the package, converts to all platforms, and upload to anaconda. 

Old Instructions:

The following steps should be taken when making an "official" release:

0. Update CHANGELOG.rst
1. Create a new `staging` branch
2. Run tests, make sure they pass.
3. Increment the version number in `ptsa/__init__.py` and push & commit `staging' branch.
5. Build conda packages on Mac, Linux, Windows: `python maint/build.py`
   - Note:  There is a problem with current (2020-08) conda versions where
     python_abi is automatically added as a dependency at build, and this is
     breaking upgrades in many environments.  This can be resolved by opening
     the tar.bz2 files, and removing the python_abi lines from info/index.json
     and info/recipe/meta.yaml (2 of them).  Then recompress it into a tar.bz2
     of the same name and upload.  Delete this note when this problem is
     resolved.
6. Upload to Anaconda Cloud: `anaconda upload --user pennmem ./ptsa-*.tar.bz2`.
   This needs to be done from the directory where the tarballs are emitted.
7. Rebuild documentation: `python maint/build_docs.py`, commit and push.
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

## Dependencies to pip install and maint/build_docs.py

* nbsphinx
* sphinx_rtd_theme

   
## TODO

- Automate build and upload process



## Old info from README.rst copied here in case it is helpful

If you don't already have it installed, you'll need to install the conda build
tool:

.. code-block:: shell-session

    conda install conda-build

Update the version number in ``conda.recipe/meta.yaml``.

Build packages with:

.. code-block:: shell-session

   conda build conda.recipe

To allow uploads you need to install anaconda-client:

.. code-block:: shell-session

    conda install anaconda-client

After that installing ``anaconda-client`` you need to to provide your anaconda.io login credentials:

.. code-block:: shell-session

    anaconda login

At this point you will be ready to upload newly built conda PTSA packages.
After the build is successfully completed you go to the directory where package tarballs have been generated
and type:

.. code-block:: shell-session

    anaconda upload --user pennmem ./ptsa-*.tar.bz2

**Hint:**  conda packages will be most likely generated in ``<conda installation dir>/conda-bld/<architecture_folder>``
where ``<architecture folder>`` denotes name of the arget architecture for which conda package was build. e.g. on 64-bit
Windows the architecture folder will be called ``win-64`` (hence conda packages will be generated in
``<conda installation dir>/conda-bld/win-64``

Hints for Windows
^^^^^^^^^^^^^^^^^

You'll want to install Microsoft Visual Studio 2015 (or newer) community edition
in order to compile extensions. For environment variables to be setup correctly,
use the "Developer Command Prompt for VS20xy" which can be found for example
in ``Start->All Programs->Visual Studio 2015->Visual Studio Tools``.
