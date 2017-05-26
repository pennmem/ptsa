import sys
import functools
import numpy as np

from .MatlabIO import *

# mapping from python type specification (scipy loadmat will report those) to numpy dtype string abbreviation


if sys.platform.startswith('win'):

    numpy_type_dict = {
        type(int()): '<i8',
        # type(np.float128()): '<f16',
        # type(np.complex256()): '<c32',
        type(complex()): '<c16',
        type(str()): '|S1',
        type(bool()): '|b1',
        type(float()): '<f8',
    }

else:
    numpy_type_dict = {
        type(int()): '<i8',
        type(np.float128()): '<f16',
        type(np.complex256()): '<c32',
        type(complex()): '<c16',
        type(str()): '|S1',
        type(bool()): '|b1',
        type(float()): '<f8',
    }

if sys.version_info[0] == 2:
    numpy_type_dict.update({
        type(long()): '<i8',
        type(unicode()): '|U1'
    })


def read_single_matlab_matrix_as_numpy_structured_array(file_name, object_name, verbose=False):
    matlab_matrix_as_python_obj_dict = deserialize_objects_from_matlab_format(file_name, object_name)

    try:
        matlab_matrix_as_python_obj = matlab_matrix_as_python_obj_dict[object_name]
    except KeyError:
        return None

    # picking first first elment  plus 20 randomly selected elements to determine type
    selector_array = [0] + np.random.randint(len(matlab_matrix_as_python_obj), size=20)
    selector_array = np.hstack(([0], selector_array))
    template_element_array = matlab_matrix_as_python_obj[selector_array]

    record = matlab_matrix_as_python_obj[0]
    # format_dict = get_np_format([record])
    format_dict = get_np_format(template_element_array)
    # format_dict = get_np_format(record)

    array_fd = np.recarray(shape=matlab_matrix_as_python_obj.shape, dtype=format_dict)

    populate_record_array(source_array=matlab_matrix_as_python_obj, target_array=array_fd, format_dict=format_dict,
                          prepend_name='',verbose=verbose)

    if verbose:
        print(array_fd)

    return array_fd


def get_np_type(record, _fieldname, verbose=False):
    kind_2_type = {'U': '|S256',
                   'S': 'S256',
                   'u': '<i8',
                   'i': '<i8',
                   'f': '<f8'
                   }

    attr = getattr(record, _fieldname)
    attr_dtype = np.dtype(type(attr))
    # if _fieldname =='eegfile':
    #     print
    if hasattr(attr, 'dtype'):
        attr_dtype = attr.dtype
        attr_shape = attr.shape
        if not attr_shape[0]:
            return None

        if attr_dtype.kind in list(kind_2_type.keys()):

            format = (kind_2_type[attr_dtype.kind], attr_shape)
            return format
        else:
            print('COULD NOT FIGURE OUT TYPE FOR ', _fieldname)
            # format_list.append(format)

    else:
        attr_dtype = np.array([attr]).dtype
        attr_dtype_kind = attr_dtype.kind
        if attr_dtype_kind in list(kind_2_type.keys()):
            return kind_2_type[attr_dtype_kind]
        elif attr_dtype_kind == 'O':
            # print 'got object'
            format_dict = get_np_format([attr])
            # format_dict = get_np_format(attr)
            # format_dict = get_np_type(attr,_fieldname)
            if len(format_dict['names']):
                return format_dict

            if verbose:
                print('got format:', format_dict)
                # print
        else:

            return attr_dtype.str


def get_np_format(record_array, verbose=False):
    names_list = []
    format_list = []

    first_record = record_array[0]

    dt = {'names': ['a', 'b'], 'formats': ['<f8', {'names': ['x'], 'formats': ['<f8']}]}
    array_fd = np.recarray(shape=(10,), dtype=dt)

    for _fieldname in first_record._fieldnames:
        formats = []
        for record in record_array:
            format = get_np_type(record, _fieldname)
            if format is not None:
                if len(np.dtype(format).shape):
                    formats.append(format)
                    break
                elif isinstance(format, dict):
                    formats.append(format)
                    break
                elif np.dtype(format).kind == 'S':
                    formats.append(format)
                    break
                else:
                    formats.append(format)

                    # if format is not None:
                    #     formats.append(format)
        # print formats


        if not len(formats):
            # for record fields for which we could not determine the format we assume it is |S256
            names_list.append(_fieldname)
            format_list.append('|S256')

            pass
        elif len(formats) == 1:
            names_list.append(_fieldname)
            format_list.append(formats[0])
        else:

            try:
                # arrays = map(lambda dtype_: np.ndarray(shape=(1), dtype=dtype_), formats)
                #
                # common_format = np.dtype(np.common_type(*arrays)).str
                common_format = np.find_common_type([],formats)
                names_list.append(_fieldname)
                format_list.append(common_format)

                # numpy_type_abbreviation = np.dtype(np.common_type(np.array(formats))).str

            except TypeError:
                print('COULD NOT FIGURE OUT FORMAT FOR: ' + _fieldname)
            pass

    if verbose:
        print(names_list)
        print(format_list)

    # fd = {'names':names_list,'formats':format_list}
    return {'names': names_list, 'formats': format_list}


def rgetattr(obj, attr):
    return functools.reduce(getattr, [obj] + attr.split('.'))


def populate_record_array(source_array, target_array, format_dict, prepend_name='', verbose=False):
    for i, field_name in enumerate(format_dict['names']):
        format = format_dict['formats'][i]
        if isinstance(format, dict):
            populate_record_array(source_array=source_array, target_array=target_array[field_name],
                                  format_dict=format, prepend_name=prepend_name + field_name + '.')
        else:

            for index, x in np.ndenumerate(source_array):
                try:
                    target_array[field_name][index] = rgetattr(source_array[index], prepend_name + field_name)
                except ValueError:
                    pass

    if verbose:
        print(target_array)


def deserialize_objects_from_matlab_format(file_name, *object_names):
    # store deserialized objects in the dictionary and return it later
    object_dict = {}

    try:
        deserializer = MatlabIO()
        deserializer.deserialize(file_name)
    except IOError:
        raise IOError('Could not deserialize ' + file_name)

    object_names_not_found = []
    for object_name in object_names:
        try:

            object_dict[object_name] = getattr(deserializer, object_name)

        except AttributeError:
            object_names_not_found.append(object_name)

    if len(object_names_not_found):

        print('WARNING: Could not retrieve the following objects:')

        for object_name in object_names_not_found:
            print(object_name)

    return object_dict
