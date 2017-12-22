import os
import os.path as osp
import shutil
import sys
from subprocess import check_call
from contextlib import contextmanager
from zipfile import ZipFile
import site

from setuptools import setup, Extension, Command, find_packages
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
        return osp.join(fftw_install_dir, 'lib', 'lib' + fftw_lib + '.a')


def get_compiler_args():
    """Return extra compiler arguments for building extensions."""
    if sys.platform.startswith('darwin'):
        return ['-std=c++11', '-stdlib=libc++', '-mmacosx-version-min=10.8']
    elif sys.platform.startswith('win'):
        return []
    else:
        return ['-std=c++11']


class BuildFftw(Command):
    description = "Build libfftw"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    @staticmethod
    def find_fftw():
        """Check if we already have FFTW installed via conda-forge or otherwise.

        Returns None if not found, otherwise the full path to the library.

        """
        import ctypes.util

        ext = '.a' if sys.platform.startswith('linux') else '.dylib'
        lib_path = ctypes.util.find_library('libfftw3' + ext)
        if lib_path is None:
            # FIXME: more elegant solution for Travis CI's nonsense
            deb_path = "/usr/lib/x86_64-linux-gnu/libfftw3.a"
            if osp.exists(deb_path):
                lib_path = deb_path
                print("Found existing FFTW:", lib_path)
            else:
                print("No installation of FFTW found")
        else:
            print("Found existing FFTW:", lib_path)
        return lib_path

    def run(self):
        try:
            os.makedirs(third_party_build_dir)
        except OSError:  # directories likely already exist
            pass

        if self.find_fftw():
            return

        if sys.platform.startswith("win"):
            build_dir = osp.join(third_party_build_dir, "fftw")
            archive = osp.join(root_dir, 'third_party', 'fftw-3.3.5-dll64.zip')

            try:
                os.makedirs(build_dir)
            except OSError:
                pass

            with chdir(build_dir):
                # Extract. Windows binaries are already built.
                with ZipFile(archive) as zfile:
                    zfile.extractall()

                try:
                    shutil.copytree(build_dir, third_party_install_dir)
                except OSError:
                    print("WARNING: skipping copying fftw contents (already exist?)")
        else:
            if osp.exists(get_libfftw_path()):
                print("libfftw already built... skipping")
                print("To force a rebuild, remove the build directory")
                return

            # Extract
            name = "fftw-3.3.4"
            tarball = name + ".tar.gz"
            archive = osp.join(root_dir, 'third_party', tarball)
            check_call(['tar', '-xzf', archive, '-C', third_party_build_dir])

            build_dir = osp.join(third_party_build_dir, name)

            with chdir(build_dir):
                # add -fPIC c and cpp flags
                # Supposedly we could only use CPPFLAGS: http://stackoverflow.com/a/5542170
                os.environ['CFLAGS'] = '-fPIC -O3'
                os.environ['CPPFLAGS'] = '-fPIC -O3'
                os.environ['CXXFLAGS'] = '-fPIC -O3'

                check_call(['./configure', '--prefix=' + third_party_install_dir])
                check_call(['make'])
                check_call(['make', 'install'])


class CustomBuild(build_py):
    def run(self):
        self.run_command("build_fftw")
        self.run_command("build_ext")
        build_py.run(self)


class CustomInstall(install):
    def run(self):
        self.run_command("build_fftw")
        self.run_command("build_ext")
        install.run(self)

        if sys.platform.startswith("win"):
            # FIXME: copy DLLs in a less stupid way
            dll_path = osp.join(third_party_install_dir, "libfftw3-3.dll")
            ext_path = osp.join(site_packages, "ptsa", "extensions")
            print(site_packages)
            morlet_path = osp.join(ext_path, "morlet")
            circ_stat_path = osp.join(ext_path, "circular_stat")
            shutil.copy(dll_path, morlet_path)
            shutil.copy(dll_path, circ_stat_path)


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
        "ptsa.data.readers.edf._edffile",
        sources=[
            "ptsa/data/readers/edf/edffile.i",
            "ptsa/data/readers/edf/edflib.cpp",
        ],
        swig_opts=["-c++"],
        extra_compile_args=get_compiler_args(),
        define_macros=[
            ('_LARGEFILE64_SOURCE', None),
            ('_LARGEFILE_SOURCE', None),
        ],
    ),
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
        'build_py': CustomBuild,
        'install': CustomInstall
    },
    ext_modules=ext_modules,

    # This doesn't seem to work because of custom commands. For now, just
    # install the prereqs with conda/pip.
    # See: http://stackoverflow.com/questions/20194565/running-custom-setuptools-build-during-install#20196065
    install_requires=[
        "numpy",
        "scipy",
        "xarray",
        "PyWavelets"
    ],
    packages=find_packages(
        exclude=['*.tests', 'tests', 'tests.*', '*.outdated_tests']
    ),
)
