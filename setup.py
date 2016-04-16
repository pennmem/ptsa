from setup_helper import *

root_dir = dirname(abspath(__file__))




check_dependencies()
swig_third_party()



ext_modules = []

morlet_dir = join(root_dir,'ptsa','extensions','morlet')

morlet_module = Extension('ptsa.extensions.morlet._morlet',
                          sources=[join(morlet_dir, 'morlet.cpp'), join(morlet_dir, 'morlet.i')],
                          swig_opts=['-c++'],
                          include_dirs=[join(get_third_party_install_dir(), 'include'), numpy.get_include()],
                          library_dirs=[join(get_third_party_install_dir(), 'lib')],
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
ext_modules.append(edf_ext)


setup(name='ptsa',
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


