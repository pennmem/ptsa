import os
import os.path as osp
from numpy.testing import assert_equal
import pytest


def get_rhino_root():
    """Return where the root directory structure is for data. Works by checking
    some common places and looking for ``/etc/hostname``.

    """
    data_roots = [
        '/',  # rhino
        '/Volumes/rhino',  # where some people mount rhino
        '/Volumes/rhino_root',  # where some people mount rhino
        osp.expanduser('~/mnt/rhino'),  # where mvd mounts rhino
    ]

    for root in data_roots:
        hostname_file = osp.join(root, 'etc', 'hostname')
        if osp.exists(osp.join(root, 'etc', 'hostname')):
            try:
                with open(hostname_file, 'r') as f:
                    # if we're not on the head node, the hostname won't start
                    # with rhino, so just check that it's in there somewhere
                    names = f.read().split(".")
                    if "rhino" in names:
                        return root
            except:
                continue
    raise OSError("Rhino root not found!")


def assert_timeseries_equal(ts1, ts2):
    """Checks that two :class:`TimeSeries` objects contain the same data."""
    assert ts1.dims == ts2.dims

    # ordering of keys can be different, so we use sets instead of lists
    keys = set(ts1.coords.keys())
    keys2 = set(ts2.coords.keys())
    assert keys == keys2

    for key in keys:
        try:
            assert all(ts1[key].data == ts2[key].data)
        except TypeError:
            # samplerate is scalar so the comparison is not iterable
            assert ts1[key].data == ts2[key].data

    assert_equal(ts1.data, ts2.data)


# Decorator to skip tests that require data on rhino
skip_without_rhino = pytest.mark.skipif("NO_RHINO" in os.environ,
                                        reason="No access to rhino")
