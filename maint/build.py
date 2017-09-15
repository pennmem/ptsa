#!/usr/bin/env python

from __future__ import print_function

import os
from functools import partial
from argparse import ArgumentParser
from subprocess import Popen
import shlex

parser = ArgumentParser(description="conda build helper")
add_pyver = partial(parser.add_argument, action='append_const', dest="py_versions")
add_pyver("--py27", help="build for Python 2.7", const="2.7")
add_pyver("--py35", help="build for Python 3.5", const="3.5")
add_pyver("--py36", help="build for Python 3.6", const="3.6")
args = parser.parse_args()

py_versions = args.py_versions or ["2.7", "3.5", "3.6"]
cmd = "conda build --python {version:s} -c conda-forge conda.recipe"

for version in py_versions:
    cmd_str = cmd.format(version=version)

    env = os.environ.copy()
    env["PYTHON_BUILD_VERSION"] = version

    print("Building for Python", version)
    print(cmd_str)
    Popen(shlex.split(cmd_str), env=env).wait()
