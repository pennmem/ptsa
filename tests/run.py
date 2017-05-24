from __future__ import print_function

import sys
import pytest
import ptsa

print("Path:", sys.path)
print("ptsa location:", ptsa.__file__)

sys.exit(pytest.main(sys.argv[1:]))
