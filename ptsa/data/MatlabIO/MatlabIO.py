import inspect
from typing import Any

import scipy.io as sio


class MatlabIO(object):
    __class_name = ''

    def __init__(self) -> None:
        pass

    def fill_dict(self, a_dict: dict[str, Any]) -> None:
        """
        Recursively fills a dictionary of class members that are non-special
        :param a_dict: dictionary from previous recursion level
        :return: dictionary of class members that are non-special
        """
        for class_member in inspect.getmembers(self, lambda a : not(inspect.isroutine(a))):

            class_member_name = class_member[0]
            class_member_val = class_member[1]

            if not(class_member_name.startswith('__') and class_member_name.endswith('__')):
                if isinstance(class_member_val, MatlabIO):
                    a_dict[class_member_name] = {}
                    class_member_val.fill_dict(a_dict[class_member_name])
                else:
                    a_dict[class_member_name] = class_member_val

    def serialize(self, name: str, format: str = 'matlab') -> None:
        a_dict: dict[str, Any] = {}
        self.fill_dict(a_dict)

        print(a_dict)
        sio.savemat(name, a_dict)

    def deserialize(self, name: str, format: str = 'matlab') -> None:
        res = sio.loadmat(name, squeeze_me=True, struct_as_record=False)

        for attr_name, attr_val in list(res.items()):
            if not(attr_name.startswith('__') and attr_name.endswith('__')):
                setattr(self, attr_name, attr_val)

