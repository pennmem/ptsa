import os.path as osp


def get_rhino_root():
    """Return where the root directory structure is for data. Works by checking
    some common places and looking for ``/etc/hostname``.

    """
    data_roots = [
        '/',  # rhino
        '/Volumes/rhino',  # where some people mount rhino
        osp.expanduser('~/mnt/rhino'),  # where mvd mounts rhino
    ]

    for root in data_roots:
        hostname_file = osp.join(root, 'etc', 'hostname')
        if osp.exists(osp.join(root, 'etc', 'hostname')):
            try:
                with open(hostname_file, 'r') as f:
                    if f.read().startswith("rhino"):
                        return root
            except:
                continue
    raise OSError("Rhino root not found!")
