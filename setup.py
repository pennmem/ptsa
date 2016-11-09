from setup_helper import *

from distutils.command.build import build

# see recipe http://stackoverflow.com/questions/12491328/python-distutils-not-include-the-swig-generated-module

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

circ_stat_dir = join(root_dir,'ptsa','extensions','circular_stat')

if sys.platform.startswith('darwin'):
    extra_compile_args=['-std=c++11','-stdlib=libc++','-mmacosx-version-min=10.7']
else:
    extra_compile_args=['-std=c++11']


morlet_module = Extension('ptsa.extensions.morlet._morlet',
                          sources=[join(morlet_dir, 'morlet.cpp'),
                                   join(morlet_dir,'MorletWaveletTransformMP.cpp'),
                                   join(morlet_dir, 'morlet.i')],
                          swig_opts=['-c++'],
                          include_dirs=[join(get_third_party_install_dir(), 'include'), numpy.get_include()],
                          library_dirs=[join(get_third_party_install_dir(), 'lib')],
                          extra_compile_args=extra_compile_args,
                          libraries=['fftw3'],

                          )

circ_stat_module = Extension('ptsa.extensions.circular_stat._circular_stat',
                          sources=[join(circ_stat_dir, 'circular_stat.cpp'),
                                   join(circ_stat_dir, 'circular_stat.i')],
                          swig_opts=['-c++'],
                          include_dirs=[join(get_third_party_install_dir(), 'include'), numpy.get_include()],
                          library_dirs=[join(get_third_party_install_dir(), 'lib')],
                          extra_compile_args=extra_compile_args,
                          libraries=['fftw3'],

                          )


edf_ext = Extension("ptsa.data.edf.edf",
                    sources = ["ptsa/data/edf/edf.c",
                               "ptsa/data/edf/edfwrap.c",
                               "ptsa/data/edf/edflib.c"],
                    include_dirs=[numpy.get_include()],
                    define_macros = [('_LARGEFILE64_SOURCE', None),
                                     ('_LARGEFILE_SOURCE', None)])



ext_modules.append(morlet_module)
ext_modules.append(circ_stat_module)
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
      py_modules=['ptsa.extensions.morlet','ptsa.extensions.circular_stat']
      )
