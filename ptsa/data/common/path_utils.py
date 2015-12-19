__author__ = 'm'

import pathlib
def find_dir_prefix(path_with_prefix,common_root):

    common_root_parts = pathlib.Path(common_root).parts
    common_root_parts_length = len(common_root_parts)
    full_path_parts = pathlib.Path(path_with_prefix).parts
    for i, part in enumerate(full_path_parts):
        if full_path_parts[i:i+common_root_parts_length] == common_root_parts[:]:
            return str(full_path_parts[:i])
    return None
