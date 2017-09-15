import os
import os.path as osp
import shutil
import sys
from subprocess import check_call
from contextlib import contextmanager
from zipfile import ZipFile
import site

from setuptools import setup, Extension, Command
from setuptools.command.build_py import build_py
from setuptools.command.install import install
import distutils
import numpy as np

root_dir = osp.dirname(osp.abspath(__file__))
build_subdir = 'build'
morlet_dir = osp.join(root_dir, 'ptsa', 'extensions', 'morlet')
extensions_dir = osp.join(root_dir, 'ptsa', 'extensions')
circ_stat_dir = osp.join(root_dir, 'ptsa', 'extensions', 'circular_stat')
third_party_build_dir = osp.join(root_dir, build_subdir, 'third_party_build')
third_party_install_dir = osp.join(root_dir, build_subdir, 'third_party_install')

for path in site.getsitepackages():
    if path.endswith("site-packages"):
        site_packages = path
        break
else:
    raise RuntimeError("site-packages not found?!?")

# see recipe http://stackoverflow.com/questions/12491328/python-distutils-not-include-the-swig-generated-module

# for windows install see http://stackoverflow.com/questions/2817869/error-unable-to-find-vcvarsall-bat
# for visual studio compilation you need to SET VS90COMNTOOLS=%VS140COMNTOOLS%
if sys.platform.startswith("win"):
    os.environ["VS90COMNTOOLS"] = os.environ["VS140COMNTOOLS"]


@contextmanager
def chdir(path):
    """Change to a directory and then change back."""
    orig_cwd = os.getcwd()
    os.chdir(path)
    yield
    os.chdir(orig_cwd)


def check_dependencies():
    """Checks for dependencies that aren't installable via pip."""
    if not distutils.spawn.find_executable('swig'):
        raise OSError('Missing swig - please `conda install swig`')


def get_version_str():
    from ptsa.version import version
    return version


def get_numpy_include_dir():
    """Returns the numpy include dir. Only a separate function so that we can
    have setuptools fetch numpy for us if we don't have it yet.

    """
    return np.get_include()


def get_include_dirs():
    """Return extra include directories for building extensions."""
    dirs = [get_numpy_include_dir(), osp.join(extensions_dir, 'ThreadPool')]

    if sys.platform.startswith("win"):
        dirs += [third_party_install_dir]
    else:
        dirs += [osp.join(third_party_install_dir, 'include')]
    return dirs


def get_lib_dirs():
    """Return extra library directories for building extensions."""
    if sys.platform.startswith('win'):
        return [third_party_install_dir]
    else:
        return [osp.join(third_party_install_dir, 'lib')]


def get_compiler_args():
    """Return extra compiler arguments for building extensions."""
    if sys.platform.startswith('darwin'):
        return ['-std=c++11', '-stdlib=libc++', '-mmacosx-version-min=10.8']
    elif sys.platform.startswith('win'):
        return []
    else:
        return ['-std=c++11']


class CustomBuild(build_py):
    def run(self):
        self.run_command("build_ext")
        build_py.run(self)


class CustomInstall(install):
    def run(self):
        self.run_command("build_ext")
        install.run(self)


ext_modules = [
    Extension(
        'ptsa.extensions.morlet._morlet',
        sources=[osp.join(morlet_dir, 'morlet.cpp'),
                 osp.join(morlet_dir, 'MorletWaveletTransformMP.cpp'),
                 osp.join(morlet_dir, 'morlet.i')],
        swig_opts=['-c++'],
        include_dirs=get_include_dirs(),
        library_dirs=get_lib_dirs(),
        extra_compile_args=get_compiler_args(),
        # libraries=get_fftw_libs(),
    ),

    Extension(
        'ptsa.extensions.circular_stat._circular_stat',
        sources=[
            osp.join(circ_stat_dir, 'circular_stat.cpp'),
            osp.join(circ_stat_dir, 'circular_stat.i')
        ],
        swig_opts=['-c++'],
        include_dirs=get_include_dirs(),
        library_dirs=get_lib_dirs(),
        extra_compile_args=get_compiler_args(),
        # libraries=get_fftw_libs(),
    ),

    Extension(
        "ptsa.data.edf.edf",
        sources=["ptsa/data/edf/edf.c",
                 "ptsa/data/edf/edfwrap.c",
                 "ptsa/data/edf/edflib.c"],
        include_dirs=[get_numpy_include_dir()],
        define_macros=[('_LARGEFILE64_SOURCE', None),
                       ('_LARGEFILE_SOURCE', None)]
    )
]

check_dependencies()

setup(
    name='ptsa',
    version=get_version_str(),
    maintainer=['Per B. Sederberg', 'Maciek Swat'],
    maintainer_email=['psederberg@gmail.com', 'maciekswat@gmail.com'],
    url='https://github.com/maciekswat/ptsa_new',
    cmdclass={
        'build_py': CustomBuild,
        'install': CustomInstall
    },
    ext_modules=ext_modules,

    # This doesn't seem to work because of custom commands. For now, just
    # install the prereqs with conda (see README).
    # See: http://stackoverflow.com/questions/20194565/running-custom-setuptools-build-during-install#20196065
    install_requires=[
        "numpy",
        "scipy",
        "xarray",
        "PyWavelets"
    ],
    packages=[
        'ptsa',
        'ptsa.extensions',
        'ptsa.extensions.morlet',
        'ptsa.extensions.circular_stat',
        'ptsa.data',
        'ptsa.data.readers',
        'ptsa.data.MatlabIO',
        'ptsa.data.common',
        'ptsa.data.filters',
        'ptsa.data.readers',
        'ptsa.data.writers',
        'ptsa.data.experimental',
        # 'ptsa.data.tests',
        'ptsa.data.edf',
        'ptsa.test',
        'ptsa.plotting',
        'ptsa.stats',
        'dimarray',
        'dimarray.tests'
    ]
)
