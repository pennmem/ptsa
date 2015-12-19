__author__ = 'm'


from collections import namedtuple

TypeValTuple = namedtuple('TypeValTuple', ['name', 'type','default'], verbose=False)

class TypedProperty(object):
    def __init__(self,name,type,default=None):
        self.name = "_" + name
        self.type = type
        self.default = default if default else type()

    def __get__(self,instance,cls):
        return getattr(instance,self.name,self.default)

    def __set__(self,instance,value):
        if not isinstance(value,self.type):
            raise TypeError("Must be a %s" % self.type)
        setattr(instance,self.name,value)

    def __delete__(self,instance):
        raise AttributeError("Can't delete attribute")

class MyMeta(type):
    def __new__(meta, name, bases, dct):
        return super(MyMeta, meta).__new__(meta, name, bases, dct)
        # return type.__new__(meta, name, bases, dct)

    def __init__(cls, name, bases, dct):

        for descr_name_type in cls._descriptors:

            # setattr(cls,descr_name_type[0],TypedProperty(descr_name_type[0],descr_name_type[1]))
            setattr(cls,descr_name_type.name,TypedProperty(descr_name_type.name,descr_name_type.type, descr_name_type.default  ))

        super(MyMeta, cls).__init__(name, bases, dct)

    def __call__(cls, *args, **kwds):
        ret_obj = type.__call__(cls, *args, **kwds)
        return ret_obj


class PropertiedObject(object):
    __metaclass__ = MyMeta
    _descriptors = []



