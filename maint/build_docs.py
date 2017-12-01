#!/usr/bin/env python

import shutil
from subprocess import Popen

shutil.rmtree('docs/html', True)
shutil.rmtree('docs/doctrees', True)
shutil.rmtree('docs/build', True)
Popen(['make', 'html'], cwd='docs').wait()
