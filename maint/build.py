#!/usr/bin/env python

import sys
from subprocess import check_call
import shlex

py_versions = ["2.7", "3.5", "3.6"]
script = "build.sh" if not sys.platform.startswith('win') else "bld.bat"
cmd = "conda build --python {version:s} --output conda.recipe/{script:s}"

for v in py_versions:
    check_call(shlex.split(cmd.format(version=v, script='')))
