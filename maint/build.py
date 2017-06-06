#!/usr/bin/env python

from __future__ import print_function
import os
from subprocess import Popen
import shlex

py_versions = ["2.7", "3.5", "3.6"]
cmd = "conda build --python {version:s} conda.recipe"

for version in py_versions:
    cmd_str = cmd.format(version=version)

    env = os.environ.copy()
    env["PYTHON_BUILD_VERSION"] = version

    print("Building for Python", version)
    print(cmd_str)
    Popen(shlex.split(cmd_str), env=env).wait()
