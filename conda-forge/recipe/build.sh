#!/usr/bin/env bash
set -euo pipefail

# conda-forge build script for ptsa.
#
# The build is driven by setup.py, which:
#   * imports numpy at module load (it must already be present in $PREFIX)
#   * shells out to swig (>=4.1) to regenerate the morlet / circular_stat
#     Python shims and *_wrap.cpp files
#   * links the morlet extension against libfftw3
#
# conda-build / conda-forge's compiler activation scripts set CC / CXX
# / CFLAGS / CPPFLAGS / LDFLAGS to point at $PREFIX, so as long as fftw
# and the headers are in `host:` no extra flags are needed.

# Make sure FFTW headers / libs in the host prefix are visible to the
# compiler even when activation scripts don't quite cover everything.
export CPATH="${PREFIX}/include${CPATH:+:${CPATH}}"
export LIBRARY_PATH="${PREFIX}/lib${LIBRARY_PATH:+:${LIBRARY_PATH}}"

# macOS still defaults to the old SDK; this matches what setup.py asks for.
if [[ "$(uname)" == "Darwin" ]]; then
    export MACOSX_DEPLOYMENT_TARGET="${MACOSX_DEPLOYMENT_TARGET:-10.9}"
fi

${PYTHON} -m pip install . --no-deps --no-build-isolation -vv
