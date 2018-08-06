import os
import os.path as osp
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


# Decorator to skip tests that require data on rhino
skip_without_rhino = pytest.mark.skipif("NO_RHINO" in os.environ,
                                        reason="No access to rhino")
