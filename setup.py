import os
import os.path as osp
import sys
import shutil
from subprocess import check_call

from setuptools import setup, Extension, Command
from setuptools.command.build_ext import build_ext
import distutils
from distutils.sysconfig import get_python_lib  # used to determine location of site-packages

root_dir = osp.dirname(osp.abspath(__file__))
build_subdir = 'build'
morlet_dir = osp.join(root_dir, 'ptsa', 'extensions', 'morlet')
extensions_dir = osp.join(root_dir, 'ptsa', 'extensions')
circ_stat_dir = osp.join(root_dir, 'ptsa', 'extensions', 'circular_stat')
third_party_build_dir = osp.join(root_dir, build_subdir, 'third_party_build')
third_party_install_dir = osp.join(root_dir, build_subdir, 'third_party_install')

# see recipe http://stackoverflow.com/questions/12491328/python-distutils-not-include-the-swig-generated-module

# for windows install see http://stackoverflow.com/questions/2817869/error-unable-to-find-vcvarsall-bat
# for visual studio compilation you need to SET VS90COMNTOOLS=%VS140COMNTOOLS%
if sys.platform.startswith("win"):
    os.environ["VS90COMNTOOLS"] = os.environ["VS140COMNTOOLS"]


def check_dependencies():
    """Checks for dependencies that aren't installable via pip."""
    if not distutils.spawn.find_executable('swig'):
        raise OSError('Missing swig - please `conda install swig`')


def get_version_str():
    from ptsa import versionString
    return versionString.vstr


def get_numpy_include_dir():
    """Returns the numpy include dir. Only a separate function so that we can
    have setuptools fetch numpy for us if we don't have it yet.

    """
    import numpy as np
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


def get_fftw_libs():
    if sys.platform.startswith("win"):
        return ['libfftw3-3']
    else:
        return ['fftw3']


def get_libfftw_path():
    """Returns the path to the built libfftw."""
    if sys.platform.startswith("win"):
        fftw_lib = 'libfftw3-3'
        fftw_install_dir = third_party_install_dir
        return osp.join(fftw_install_dir, fftw_lib + '.dll')
    else:
        fftw_lib = 'fftw3'
        fftw_install_dir = third_party_install_dir
        return osp.join(fftw_install_dir, 'lib', 'lib'+fftw_lib+'.a')


def get_compiler_args():
    """Return extra compiler arguments for building extensions."""
    if sys.platform.startswith('darwin'):
        return ['-std=c++11', '-stdlib=libc++', '-mmacosx-version-min=10.8']
    elif sys.platform.startswith('win'):
        return []
    else:
        return ['-std=c++11']


class CustomCommand(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass


class BuildFftw(CustomCommand):
    description = "Build libfftw"

    def run(self):
        if sys.platform.startswith("win"):
            raise OSError("FIXME Windows not yet supported")

        # Extract
        name = "fftw-3.3.4"
        tarball = name + ".tar.gz"
        archive = osp.join(root_dir, 'third_party', tarball)
        check_call(['tar', '-xzf', archive, '-C', third_party_build_dir])

        fftw_src_dir = osp.join(third_party_build_dir, name)

        orig_dir = os.getcwd()

        try:
            os.chdir(fftw_src_dir)

            # add -fPIC c and cpp flags
            os.environ['CFLAGS'] = '-fPIC -O3'
            os.environ['CPPFLAGS'] = '-fPIC -O3'
            os.environ['CXXFLAGS'] = '-fPIC -O3'

            check_call(['./configure', '--prefix=' + third_party_install_dir])
            check_call(['make'])
            check_call(['make', 'install'])
        finally:
            os.chdir(orig_dir)


class CustomBuild(build_ext):
    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        build_ext.run(self)
        self.run_command("build_fftw")
        # self.run_command("swigify")
        # build_ext.run(self)


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
        libraries=get_fftw_libs(),
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
        libraries=get_fftw_libs(),
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
        'build_fftw': BuildFftw,
        # 'build_ext': CustomBuild
    },
    ext_modules=ext_modules,

    # This doesn't seem to work because of custom commands. For now, just
    # install the prereqs with conda/pip.
    # See: http://stackoverflow.com/questions/20194565/running-custom-setuptools-build-during-install#20196065
    install_requires=[
        "numpy",
        "scipy",
        "xarray",
        "pandas",
        "PyWavelets"
    ],
    # package_dir={},
    packages=[
        'ptsa',
        'ptsa.extensions.morlet',
        'ptsa.extensions.circular_stat',
        'ptsa.tests',
        'ptsa.tests.ptsa_regression',
        'ptsa.data',
        'ptsa.data.readers',
        'ptsa.data.MatlabIO',
        'ptsa.data.common',
        'ptsa.data.filters',
        'ptsa.data.readers',
        'ptsa.data.writers',
        'ptsa.data.tests',
        'ptsa.data.edf',
        'ptsa.plotting',
        'ptsa.plotting.tests',
        'ptsa.stats',
        'dimarray',
        'dimarray.tests'
    ],
    py_modules=['ptsa.extensions.morlet', 'ptsa.extensions.circular_stat']
)

# FIXME
if False:
    # copying fftw .dll - have to find better way of doing it "distutils-style"...
    shutil.copy(
        src=fftw_lib_abspath,
        dst=osp.join(get_python_lib(), 'ptsa', 'extensions', 'morlet')
    )

    shutil.copy(
        src=fftw_lib_abspath,
        dst=osp.join(get_python_lib(), 'ptsa', 'extensions', 'circular_stat')
    )
