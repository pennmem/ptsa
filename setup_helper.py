import sys

import distutils
from distutils.core import setup, Extension
from distutils.sysconfig import get_config_var
from distutils.extension import Extension
import distutils.ccompiler
import os
from os.path import *
import sys
import shutil
from glob import glob

from subprocess import call

root_dir = dirname(abspath(__file__))
build_subdir = 'build'


sys.path.append(join(root_dir,'ptsa'))



fftw_name = 'fftw-3.3.4'
fftw_tar = fftw_name+'.tar.gz'

third_party_build_dir = join(root_dir,build_subdir,'third_party_build')
third_party_install_dir = join(root_dir,build_subdir,'third_party_install')

python_executable = sys.executable

print 'python_executable=',python_executable

print 'PYTHON LIB=',  distutils.sysconfig.get_python_lib(standard_lib=True)
print distutils.sysconfig.get_python_inc()
print distutils.sysconfig.get_python_version()


def get_version_str():
    import versionString

    version_str = versionString.vstr
    return version_str

def get_third_party_build_dir():
    return third_party_build_dir

def get_third_party_install_dir():
    return third_party_install_dir


def clean_previous_build():
    """
    This function removes previous build dirs that were
    used to build c/c++ extension modules
    :return: None
    """


    dirs = glob(join(root_dir,build_subdir,'*'))
    dirs.remove(third_party_build_dir)
    dirs.remove(third_party_install_dir)

    for d in dirs:
        shutil.rmtree(d)



def check_dependencies():

    try:
        import numpy
    except ImportError:
        print 'numpy is required to build PTSA. Please install numpy before proceeding'
        sys.exit(1)


    try:
        import scipy
    except ImportError:
        print 'scipy is required to build PTSA. Please install scipy before proceeding'

        sys.exit(1)



    try:
        import pywt
    except ImportError:
        print 'pywt is required to build PTSA. Please install pywt before proceeding. ' \
              'you may try runnig the following command from your shell:' \
              'pip install PyWavelets'

        sys.exit(1)

    try:
        import xarray
    except ImportError:
        try:
            import xray
        except ImportError:
            print 'xarray (aka xray) is required to build PTSA. Please install xarray before proceeding'

            sys.exit(1)


    swig_executable = distutils.spawn.find_executable('swig')
    if not swig_executable:
        raise OSError('Missing cmake - please install swig to proceed (www.swig.org)')



    compiler=distutils.ccompiler.new_compiler()
    lib_dirs=[join(third_party_install_dir,'lib')]

    if compiler.find_library_file(lib_dirs,'fftw3'):
        print 'FOUND FFTW3 library'
    else:
        print 'DID NOT FIND FFTW3 LIBRARY - WILL BUILD FROM SOURCE'
        build_third_party_libs()


def build_third_party_libs():
    try:
        shutil.rmtree(third_party_build_dir)
    except OSError:
        pass

    try:
        shutil.rmtree(third_party_install_dir)
    except OSError:
        pass

    try:
        os.makedirs(third_party_install_dir)
    except OSError:
        pass

    try:
        os.makedirs(third_party_build_dir)
    except OSError:
        pass


    call (['tar','-xzf',join(root_dir,'third_party',fftw_tar),'-C',third_party_build_dir])

    fftw_src_dir = join(third_party_build_dir,fftw_name)

    orig_dir = os.getcwd()

    os.chdir(fftw_src_dir)

    # add -fPIC c and cpp flags
    os.environ['CFLAGS']='-fPIC -O3'
    os.environ['CPPFLAGS'] = '-fPIC -O3'
    os.environ['CXXFLAGS'] = '-fPIC -O3'

    call(['./configure','--prefix='+join(third_party_install_dir)])
    call(['make'])
    call(['make', 'install'])
    os.chdir(orig_dir)

def swig_third_party():
    call(['swig','-python','-outdir', 'morlet', 'morlet.i'])


check_dependencies()
swig_third_party()

import numpy

ext_modules = []
morlet_dir = join(root_dir,'ptsa','extensions','morlet')
