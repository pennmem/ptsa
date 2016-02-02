__author__ = 'm'


from collections import namedtuple

TypeValTuple = namedtuple('TypeValTuple', ['name', 'type','default'], verbose=False)

class TypedProperty(object):
    def __init__(self,name,type,default=None):
        self.name = "_" + name
        self.type = type
        self.default = default if default is not None else type()

    def __get__(self,instance,cls):
        return getattr(instance,self.name,self.default)

    def __set__(self,instance,value):
        # print 'self.name=',self.name,' val=',value
        if not isinstance(value,self.type):
            raise TypeError(" Property %s must be a %s" %(self.name[1:],self.type))
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

    def init_attrs(self, kwds):
        for option_name, val in kwds.items():
            try:
                attr = getattr(self,option_name)
                setattr(self,option_name,val)
            except AttributeError:
                s = 'Option: '+ option_name+' is not allowed'
                print s
                raise AttributeError(s)






if __name__=='__main__':

    class RF(PropertiedObject):
        _descriptors = [
            TypeValTuple('resamplerate', float, -1.0),
            TypeValTuple('time_axis_index', int, -1),
        ]


        def __init__(self,**kwds):

            self.window = None
            self.time_series = None

            self.init_attrs(kwds)


    rf = RF(resamplerate=20.0,time_axis_index=2,window=[0,1])

    print rf.resamplerate
    print rf.window
