#!/usr/bin/env python

from __future__ import print_function

from argparse import ArgumentParser
import os
import shlex
import shutil
from subprocess import check_call

parser = ArgumentParser()
parser.add_argument('--no-clean', action='store_true', default=False,
                    help='remove build directory')
parser.add_argument('--no-build', action='store_true', default=False,
                    help='do not build packages')


def clean():
    """Clean the build directory."""
    try:
        shutil.rmtree('build')
        os.mkdir('build')
    except OSError:
        pass


def build():
    """Build conda packages."""
    for pyver in ['3.6']:
        build_cmd = "conda build conda.recipe --python {} --output-folder build/".format(pyver)
        print(build_cmd)
        check_call(shlex.split(build_cmd))


if __name__ == "__main__":
    args = parser.parse_args()

    if not args.no_clean:
        clean()

    if not args.no_build:
        build()
