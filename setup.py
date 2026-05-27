from contextlib import contextmanager
import json
import os
import os.path as osp
from setuptools import setup, Extension, find_packages
from setuptools.command.build_py import build_py
from setuptools.command.install import install
from setuptools.command.develop import develop
import site
import subprocess
import sys

import numpy as np

root_dir = osp.dirname(osp.abspath(__file__))
build_subdir = 'build'
morlet_dir = osp.join(root_dir, 'ptsa', 'extensions', 'morlet')
extensions_dir = osp.join(root_dir, 'ptsa', 'extensions')
circ_stat_dir = osp.join(root_dir, 'ptsa', 'extensions', 'circular_stat')

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


def get_version_str():
    from ptsa import __version__
    return __version__


def get_include_dirs():
    """Return extra include directories for building extensions."""
    dirs = [
        np.get_include(),
        osp.join(extensions_dir, 'ThreadPool'),
    ]

    conda_include = []

    try:
        # Note: we can't just call conda because that might find the wrong one.
        # Instead, we use the CONDA_EXE environment variable that conda should
        # set.
        p = subprocess.Popen([os.environ["CONDA_EXE"], "info", "--json"],
                             env=os.environ,
                             stdout=subprocess.PIPE)
        stdout, _ = p.communicate()
        info = json.loads(stdout)
        conda_include.append(os.path.join(info["active_prefix"], "include"))
    except Exception as e:
        # looks like we're not using conda
        pass

    dirs += conda_include
    return dirs


def get_fftw_libs():
    if sys.platform.startswith("win"):
        return ['libfftw3-3']
    else:
        return ['fftw3']


def get_library_dirs():
    """Return extra library search dirs so the linker finds libfftw3.

    On Linux the conda compiler-activation scripts export ``-L$PREFIX/lib``
    via ``LDFLAGS`` and the link "just works", but the macOS (clang) and
    Windows (MSVC) builds do not reliably pick that up — the morlet link
    step fails with ``ld: library 'fftw3' not found``. Add the active conda
    prefix's lib dir explicitly so the search path is correct everywhere.
    """
    dirs = []

    def _add(prefix):
        if not prefix:
            return
        # POSIX conda layout, plus the Windows ``Library\{lib,bin}`` layout.
        for sub in (('lib',), ('Library', 'lib'), ('Library', 'bin')):
            dirs.append(os.path.join(prefix, *sub))

    # conda-build always exports PREFIX (and LIBRARY_PREFIX on Windows) for
    # the host env that carries the fftw dependency; prefer those.
    for var in ("PREFIX", "LIBRARY_PREFIX", "CONDA_PREFIX"):
        _add(os.environ.get(var))

    # Fall back to `conda info`'s active prefix (mirrors get_include_dirs).
    try:
        p = subprocess.Popen([os.environ["CONDA_EXE"], "info", "--json"],
                             env=os.environ, stdout=subprocess.PIPE)
        stdout, _ = p.communicate()
        _add(json.loads(stdout).get("active_prefix"))
    except Exception:
        pass

    # De-duplicate while preserving order; keep only dirs that exist.
    seen = []
    for d in dirs:
        if d and d not in seen and os.path.isdir(d):
            seen.append(d)
    return seen


def get_compiler_args():
    """Return extra compiler arguments for building extensions."""
    if sys.platform.startswith('darwin'):
        return ['-std=c++14', '-stdlib=libc++', '-mmacosx-version-min=10.9']
    elif sys.platform.startswith('win'):
        return ['/EHsc']  # exception handling
    else:
        return ['-std=c++14']


class CustomBuild(build_py):
    def run(self):
        self.run_command("build_ext")
        build_py.run(self)


class CustomDevelop(develop):
    def run(self):
        self.run_command("build_ext")
        develop.run(self)


class CustomInstall(install):
    def run(self):
        self.run_command("build_ext")
        install.run(self)

        # FIXME: check if this is still necessary on windows
        # if sys.platform.startswith("win"):
        #     dll_path = osp.join(third_party_install_dir, "libfftw3-3.dll")
        #     ext_path = osp.join(site_packages, "ptsa", "extensions")
        #     morlet_path = osp.join(ext_path, "morlet")
        #     circ_stat_path = osp.join(ext_path, "circular_stat")
        #     shutil.copy(dll_path, morlet_path)
        #     shutil.copy(dll_path, circ_stat_path)


def make_pybind_extension(module, **kwargs):
    """Create a pybind11 extension module.

    This requires a compiler that supports C++11 or newer.

    Parameters
    ----------
    module : str
        Name of the extension module to produce.

    Returns
    -------
    Extension

    Raises
    ------
    ImportError
        If pybind11 is not found.

    Notes
    -----
    This will automatically include the pybind11 and numpy include directories.

    Keyword arguments are passsed to the constructor of :class:`Extension`.

    """
    import pybind11

    include_dirs = kwargs.pop('include_dirs', [])
    include_dirs += [
        pybind11.get_include(),
        pybind11.get_include(user=True),
        np.get_include(),
    ]

    compile_args = kwargs.pop('extra_compile_args', [])
    compile_args += get_compiler_args()

    library_dirs = kwargs.pop('library_dirs', [])
    library_dirs += get_library_dirs()

    return Extension(
        module,
        include_dirs=include_dirs,
        library_dirs=library_dirs,
        extra_compile_args=compile_args,
        language='c++',
        **kwargs
    )


# Install pybind11 if missing (used by morlet, circular_stat, and edf).
try:
    import pybind11  # noqa: F401
except ImportError:
    if subprocess.call([sys.executable, '-m', 'pip', 'install', 'pybind11']):
        raise RuntimeError('ERROR, failed:  pip install pybind11')

ext_modules = [
    make_pybind_extension(
        'ptsa.extensions.morlet._morlet',
        sources=[
            osp.join(morlet_dir, 'morlet.cpp'),
            osp.join(morlet_dir, 'MorletWaveletTransformMP.cpp'),
            osp.join(morlet_dir, 'wrap.cpp'),
        ],
        include_dirs=get_include_dirs(),
        libraries=get_fftw_libs(),
    ),

    make_pybind_extension(
        'ptsa.extensions.circular_stat._circular_stat',
        sources=[
            osp.join(circ_stat_dir, 'circular_stat.cpp'),
            osp.join(circ_stat_dir, 'wrap.cpp'),
        ],
        include_dirs=get_include_dirs(),
    ),
]

ext_modules += [
    make_pybind_extension(
        'ptsa.extensions.edf.edffile',
        sources=[
            'ptsa/extensions/edf/edflib.cpp',
            'ptsa/extensions/edf/edffile.cpp',
            'ptsa/extensions/edf/wrap.cpp',
        ],
    ),
]


setup(
    name='ptsa',
    version=get_version_str(),
    maintainer=['Ryan A. Colyer', 'Joseph Rudoler'],
    maintainer_email=['rcolyer@sas.upenn.edu', 'jrudoler@sas.upenn.edu', 'kahana-sysadmin@sas.upenn.edu'],
    url='https://github.com/pennmem/ptsa',
    cmdclass={
        'build_py': CustomBuild,
        'install': CustomInstall,
        'develop': CustomDevelop,
    },
    ext_modules=ext_modules,

    # This doesn't seem to work because of custom commands. For now, just
    # install the prereqs with conda/pip.
    # See: http://stackoverflow.com/questions/20194565/running-custom-setuptools-build-during-install#20196065
    install_requires=[
        "numpy",
        "scipy",
        "xarray",
    ],
    packages=find_packages(
        exclude=['*.tests', 'tests', 'tests.*', '*.outdated_tests']
    ),
)
