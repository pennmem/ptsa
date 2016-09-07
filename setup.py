from setup_helper import *

from distutils.command.build import build

# see recipe http://stackoverflow.com/questions/12491328/python-distutils-not-include-the-swig-generated-module

# for windows install see http://stackoverflow.com/questions/2817869/error-unable-to-find-vcvarsall-bat


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

morlet_dir = join(root_dir,'ptsa','extensions','morlet')

if sys.platform.startswith('darwin'):
    extra_compile_args=['-std=c++11','-stdlib=libc++','-mmacosx-version-min=10.7']
else:
    extra_compile_args=['-std=c++11']


morlet_mp_include_dirs = ''
morlet_mp_lib_dirs = ''
if sys.platform.startswith('win'):
    morlet_mp_include_dirs = [get_third_party_install_dir(), numpy.get_include()]
    morlet_mp_lib_dirs = [get_third_party_install_dir()]
    morlet_mp_libs=['libfftw3-3']
else:
    morlet_mp_include_dirs = [join(get_third_party_install_dir(), 'include'), numpy.get_include()]
    morlet_mp_lib_dirs = [join(get_third_party_install_dir(), 'lib')]
    morlet_mp_libs=['fftw3']
    
    
morlet_module = Extension('ptsa.extensions.morlet._morlet',
                          sources=[join(morlet_dir, 'morlet.cpp'),
                                   join(morlet_dir,'MorletWaveletTransformMP.cpp'),
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
                    sources = ["ptsa/data/edf/edf.c",
                               "ptsa/data/edf/edfwrap.c",
                               "ptsa/data/edf/edflib.c"],
                    include_dirs=[numpy.get_include()],
                    define_macros = [('_LARGEFILE64_SOURCE', None),
                                     ('_LARGEFILE_SOURCE', None)])



ext_modules.append(morlet_module)
ext_modules.append(edf_ext)


setup(name='ptsa',
      cmdclass={'build': CustomBuild},
      version=get_version_str(),
      maintainer=['Per B. Sederberg', 'Maciek Swat'],
      maintainer_email=['psederberg@gmail.com','maciekswat@gmail.com'],
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
