#!/usr/bin/env bash

# Macs are weird and don't generally include /usr/local things in the path
UNAME=`uname`
if [[ "$UNAME" == 'Darwin' ]]; then
   export CPATH=/usr/local/include;
   export LIBRARY_PATH=/usr/local/lib;
fi

# FIXME: figure out how to depend on conda-forge package of this only
pip install pybind11
$PYTHON setup.py install
