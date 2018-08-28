import os
import sys
import pytest

args = sys.argv[1:]

if "NO_RHINO" in os.environ:
    args += ["-m", '"not rhino"']

sys.exit(pytest.main(args))
