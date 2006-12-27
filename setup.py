

from distutils.core import setup, Extension
from distutils.sysconfig import get_config_var
import os
import sys



setup(name='pyeeg', 
      version='0.0.1', ### MAKE SURE THIS MATCHES src/version.py !!
      package_dir={"pyeeg":"src"},
      packages=['pyeeg'],
      author=['Per B. Sederberg, Christoph T. Weidemann'],
      maintainer=['Per B. Sederberg'],
      maintainer_email=['psederberg@gmail.com'],
      url=[''])

