import inspect
import scipy.io as sio


class MatlabIO(object):
    __class_name = ''

    def __init__(self):
        pass

    def fill_dict(self,a_dict):
        """
        Recursively fills a dictionary of class members that are non-special
        :param a_dict: dictionary from previous recursion level
        :return: dictionary of class members that are non-special
        """
        for class_member in inspect.getmembers(self, lambda a : not(inspect.isroutine(a))):

            class_member_name = class_member[0]
            class_member_val = class_member[1]

            if not(class_member_name.startswith('__') and class_member_name.endswith('__')):
                # print 'class_member_name=', class_member_name
                if isinstance(class_member_val, MatlabIO):
                    a_dict[class_member_name] = {}
                    class_member_val.fill_dict(a_dict[class_member_name])
                    # print 'GOT MATLAB IO CLASS'
                else:
                    # print 'LEAF CLASS'
                    a_dict[class_member_name] = class_member_val

    def serialize(self, name, format='matlab'):
        a_dict = {}
        self.fill_dict(a_dict)

        print(a_dict)
        sio.savemat(name, a_dict)

    def deserialize(self, name, format='matlab'):
        res = sio.loadmat(name,squeeze_me=True, struct_as_record=False)
        # res = sio.loadmat(name,squeeze_me=True, struct_as_record=True)

        # print res
        # print '\n\n\n'

        for attr_name, attr_val in list(res.items()):
            if not(attr_name .startswith('__') and attr_name .endswith('__')):
                # print 'attr_name=',attr_name
                    # , ' val=', val, 'type =', type(val)
                # print 'fetching ',attr_name
                setattr(self, attr_name , attr_val)

