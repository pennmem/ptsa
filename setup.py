from setup_helper import *

# used to determine location of site-packages
from distutils.sysconfig import get_python_lib


from glob import glob
from shutil import copy
from distutils.command.build import build




# see recipe http://stackoverflow.com/questions/12491328/python-distutils-not-include-the-swig-generated-module

# for windows install see http://stackoverflow.com/questions/2817869/error-unable-to-find-vcvarsall-bat
# for visual studio compilation you need to SET VS90COMNTOOLS=%VS140COMNTOOLS%


class CustomBuild(build):
    sub_commands = [
        ('build_ext', build.has_ext_modules),
        ('build_py', build.has_pure_modules),
        ('build_clib', build.has_c_libraries),
        ('build_scripts', build.has_scripts),
    ]


root_dir = dirname(abspath(__file__))

clean_previous_build()
check_dependencies()
swig_third_party()

ext_modules = []

morlet_dir = join(root_dir, 'ptsa', 'extensions', 'morlet')
extensions_dir = join(root_dir, 'ptsa', 'extensions')

if sys.platform.startswith('darwin'):
    extra_compile_args = ['-std=c++11', '-stdlib=libc++', '-mmacosx-version-min=10.7']
else:
    extra_compile_args = ['-std=c++11']

morlet_mp_include_dirs = ''
morlet_mp_lib_dirs = ''
if sys.platform.startswith('win'):
    morlet_mp_include_dirs = [get_third_party_install_dir(), numpy.get_include(), join(extensions_dir, 'ThreadPool')]
    morlet_mp_lib_dirs = [get_third_party_install_dir()]
    fftw_lib = 'libfftw3-3'
    fftw_install_dir = get_third_party_install_dir()
    fftw_lib_abspath = join(fftw_install_dir, fftw_lib+'.dll')

    morlet_mp_libs = [fftw_lib]
else:
    morlet_mp_include_dirs = [join(get_third_party_install_dir(), 'include'), numpy.get_include(),
                              join(extensions_dir, 'ThreadPool')]
    morlet_mp_lib_dirs = [join(get_third_party_install_dir(), 'lib')]
    fftw_lib = 'fftw3'
    fftw_install_dir = get_third_party_install_dir()
    fftw_lib_abspath = join(fftw_install_dir, 'lib'+fftw_lib+'.so')

    morlet_mp_libs = [fftw_lib]

morlet_module = Extension('ptsa.extensions.morlet._morlet',
                          sources=[join(morlet_dir, 'morlet.cpp'),
                                   join(morlet_dir, 'MorletWaveletTransformMP.cpp'),
                                   join(morlet_dir, 'morlet.i')],
                          swig_opts=['-c++'],
                          include_dirs=morlet_mp_include_dirs,
                          library_dirs=morlet_mp_lib_dirs,

                          # include_dirs=[join(get_third_party_install_dir(), 'include'), numpy.get_include()],
                          # library_dirs=[join(get_third_party_install_dir(), 'lib')],
                          # extra_compile_args=extra_compile_args,
                          libraries=morlet_mp_libs,

                          )

edf_ext = Extension("ptsa.data.edf.edf",
                    sources=["ptsa/data/edf/edf.c",
                             "ptsa/data/edf/edfwrap.c",
                             "ptsa/data/edf/edflib.c"],
                    include_dirs=[numpy.get_include()],
                    define_macros=[('_LARGEFILE64_SOURCE', None),
                                   ('_LARGEFILE_SOURCE', None)])

ext_modules.append(morlet_module)
ext_modules.append(edf_ext)

setup(name='ptsa',
      cmdclass={'build': CustomBuild},
      version=get_version_str(),
      maintainer=['Per B. Sederberg', 'Maciek Swat'],
      maintainer_email=['psederberg@gmail.com', 'maciekswat@gmail.com'],
      url=['https://github.com/maciekswat/ptsa_new'],
      ext_modules=ext_modules,
      # package_dir={},
      packages=[
          'ptsa',
          'ptsa.extensions.morlet',
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

      py_modules=['ptsa.extensions.morlet']

      )



# copying fftw .dll - have to find better way of doing it "distutils-style"...
copy(
    src=fftw_lib_abspath,
    dst=join(get_python_lib(),'ptsa','extensions','morlet')
)


print 'SETUP COMPLETE'
