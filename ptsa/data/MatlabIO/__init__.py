from MatlabIO import *
import scipy.io as sio
import numpy as np

__author__ = 'm'

# mapping from python type specification (scipy loadmat will report those) to numpy dtype string abbreviation
numpy_type_dict = {
    type(int()): '<i8',
    type(long()): '<i8',
    type(np.float128()): '<f16',
    type(np.complex256()): '<c32',
    type(complex()): '<c16',
    type(str()): '|S1',
    type(unicode()): '|U1',
    type(bool()): '|b1',
    type(float()): '<f8',

}


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
                          prepend_name='')

    if verbose:
        print array_fd

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

        if attr_dtype.kind in kind_2_type.keys():

            format = (kind_2_type[attr_dtype.kind], attr_shape)
            return format
        else:
            print 'COULD NOT FIGURE OUT TYPE FOR ', _fieldname
            # format_list.append(format)

    else:
        attr_dtype = np.array([attr]).dtype
        attr_dtype_kind = attr_dtype.kind
        if attr_dtype_kind in kind_2_type.keys():
            return kind_2_type[attr_dtype_kind]
        elif attr_dtype_kind == 'O':
            # print 'got object'
            format_dict = get_np_format([attr])
            # format_dict = get_np_format(attr)
            # format_dict = get_np_type(attr,_fieldname)
            if len(format_dict['names']):
                return format_dict

            if verbose:
                print 'got format:', format_dict
                # print
        else:

            return attr_dtype.str


def get_np_format(record_array, verbose=False):
    names_list = []
    format_list = []

    record = record_array[0]

    dt = {'names': ['a', 'b'], 'formats': ['<f8', {'names': ['x'], 'formats': ['<f8']}]}
    array_fd = np.recarray(shape=(10,), dtype=dt)

    for _fieldname in record._fieldnames:
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
                print 'COULD NOT FIGURE OUT FORMAT FOR: ' + _fieldname
            pass

    if verbose:
        print names_list
        print format_list

    # fd = {'names':names_list,'formats':format_list}
    return {'names': names_list, 'formats': format_list}


import functools


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
        print target_array


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

        print 'WARNING: Could not retrieve the following objects:'

        for object_name in object_names_not_found:
            print object_name

    return object_dict

# def determine_dtype_abbreviation(inspect_member_info, default_string_length=256):
#     '''
#     Determines numpy dtype abbreviation for a given type returned by type() fcn
#
#     :param inspect_member_info:
#     :param default_string_length: default length for the string parameters
#     :return:
#     '''
#     class_member_name = inspect_member_info[0]
#     class_member_val = inspect_member_info[1]
#     class_member_type = type(class_member_val)
#
#     if class_member_name=='avgSurf':
#         pass
#
#     if class_member_type.__name__ == 'ndarray':
#         # print 'found array'
#         # print 'class_member_val=', class_member_val
#         # print 'class_member_val.dtype=', class_member_val.dtype
#         # print 'class_member_val.shape=', class_member_val.shape
#         # print 'class_member_val.dtype.descr=', class_member_val.dtype.descr
#
#         # in case inferred array has zero size we will mark it as Python object
#         # '0'
#
#         shape = class_member_val.shape
#         if shape[0] == 0:
#             numpy_type_char_abbreviation = 'O'
#
#         else:
#             numpy_type_char_abbreviation = (class_member_val.dtype.descr[0][1], shape)
#
#
#             # sys.exit()
#     else:
#
#         # ('f2', '>f8', (2, 3))
#         # numpy_type_char_abbreviation = numpy_type_dict[class_member_type][0]
#         numpy_type_char_abbreviation = numpy_type_dict[class_member_type]
#
#         if numpy_type_char_abbreviation == '|S1':
#             numpy_type_char_abbreviation = '|S' + str(default_string_length)
#
#             # we override unicode and use ascii instead. We assume we do not have true unicode characters in our input
#         elif numpy_type_char_abbreviation == '|U1':
#             numpy_type_char_abbreviation = '|S' + str(default_string_length)
#
#     return numpy_type_char_abbreviation
#
#
# def serialize_objects_in_matlab_format(file_name, *object_name_pairs):
#     class Serializer(MatlabIO):
#         def __init__(self):
#             pass
#
#     serializer = Serializer()
#     for obj, name in object_name_pairs:
#         setattr(serializer, name, obj)
#
#     serializer.serialize(file_name)
#
#
# def deserialize_objects_from_matlab_format(file_name, *object_names):
#     # store deserialized objects in the dictionary and return it later
#     object_dict = {}
#
#     try:
#         deserializer = MatlabIO()
#         deserializer.deserialize(file_name)
#     except IOError:
#         raise IOError('Could not deserialize ' + file_name)
#
#     object_names_not_found = []
#     for object_name in object_names:
#         try:
#
#             object_dict[object_name] = getattr(deserializer, object_name)
#
#         except AttributeError:
#             object_names_not_found.append(object_name)
#
#     if len(object_names_not_found):
#
#         print 'WARNING: Could not retrieve the following objects:'
#
#         for object_name in object_names_not_found:
#             print object_name
#
#     return object_dict
#
#
# def deserialize_single_object_from_matlab_format(file_name, object_name):
#     object_dict = deserialize_objects_from_matlab_format(file_name, object_name)
#     try:
#         return object_dict[object_name]
#     except LookupError:
#         return None
#
#
# def deserialize_objects_from_matlab_format_struct_as_record(file_name, *object_names):
#     # store deserialized objects in the dictionary and return it later
#     object_dict = {}
#
#     try:
#         res = sio.loadmat(file_name, squeeze_me=True, struct_as_record=True)
#
#     except IOError:
#         raise IOError('Could not deserialize ' + file_name)
#
#     object_names_not_found = []
#
#     for object_name in object_names:
#         try:
#
#             # object_dict[object_name] = getattr(res,object_name)
#             object_dict[object_name] = res[object_name]
#
#         except AttributeError:
#             object_names_not_found.append(object_name)
#
#     if len(object_names_not_found):
#
#         print 'WARNING: Could not retrieve the following objects:'
#
#         for object_name in object_names_not_found:
#             print object_name
#
#     return object_dict
#
#
# def deserialize_single_object_from_matlab_format_struct_as_record(file_name, object_name):
#     object_dict = deserialize_objects_from_matlab_format_struct_as_record(file_name, object_name)
#     try:
#         return object_dict[object_name]
#     except LookupError:
#         return None
#
#
# def read_matlab_matrices_as_numpy_structured_arrays(file_name, *object_names):
#     var_record_dict = deserialize_objects_from_matlab_format_struct_as_record(file_name, *object_names)
#     var_object_dict = deserialize_objects_from_matlab_format(file_name, *object_names)
#
#     # print 'var_record_dict=',var_record_dict
#     # print 'var_object_dict=',var_object_dict
#
#     structured_array_dict = {}
#
#     for (obj_name, obj), (record_rame, record_val), in zip(var_object_dict.items(), var_record_dict.items()):
#         structured_array_dict[record_rame] = \
#             reinterpret_matlab_matrix_as_structured_array(matlab_matrix_as_python_obj=obj,
#                                                           matlab_matrix_structured=record_val)
#
#     return structured_array_dict
#
#
# # def read_single_matlab_matrix_as_numpy_structured_array(file_name, object_name):
# #     structured_array_dict = read_matlab_matrices_as_numpy_structured_arrays(file_name, object_name)
# #     try:
# #         return structured_array_dict[object_name]
# #     except LookupError:
# #         return None
#
#
#
# def reinterpret_matlab_matrix_as_structured_array(matlab_matrix_as_python_obj, matlab_matrix_structured):
#     template_element = None
#
#     # picking first first elment  plus 20 randomly selected elements to determine type
#     selector_array = [0]+np.random.randint(len(matlab_matrix_as_python_obj),size=20)
#     selector_array = np.hstack(([0],selector_array))
#     template_element_array = matlab_matrix_as_python_obj[selector_array]
#
#
#     record = matlab_matrix_as_python_obj[0]
#     # format_dict = get_np_format([record])
#     format_dict = get_np_format(template_element_array)
#     # format_dict = get_np_format(record)
#
#     array_fd = np.recarray(shape=matlab_matrix_as_python_obj.shape, dtype=format_dict)
#
#     populate_record_array(source_array=matlab_matrix_as_python_obj, target_array=array_fd,format_dict=format_dict,prepend_name='')
#
#     print array_fd
#     return array_fd
#
#
#     # for i, field_name in enumerate(format_dict['names']):
#     #     format = format_dict['format'][i]
#     #     if isinstance(format,dict):
#     #         populate_single_record_array(source_array=matlab_matrix_as_python_obj,
#     #                                      target_array=array_fd[field_name],
#     #                                      field_name=field_name,
#     #                                         field_prepend=)
#     #     else:
#     #         populate_single_record_array(source_array=matlab_matrix_as_python_obj, target_array=array_fd[field_name],field_name=field_name)
#
#     for field_name in format_dict['names']:
#
#         # print 'field_name = ', field_name
#         # print 'array_value=',matlab_matrix_structured [field_name]
#         field_val = getattr(record, field_name)
#         # print field_val, type(field_val).__name__
#         field_val_type = type(field_val).__name__
#
#         matlab_matrix_as_python_obj[0].avgSurf.x
#
#         if field_name=='avgSurf':
#             print
#         if field_val_type == 'ndarray':
#             for index, x in np.ndenumerate(array_fd):
#                 # print 'index, x = ',index,reconstructed_array[field_name][index]
#                 # print 'index, x = ',index,matlab_matrix_structured ['m'][index]
#                 array_fd[field_name][index] = matlab_matrix_structured[field_name][index]
#
#             pass
#         else:
#             try:
#                 array_fd[field_name] = matlab_matrix_structured[field_name]
#             except ValueError:
#                 pass
#
#
#
#
#
#     for index, x in np.ndenumerate(matlab_matrix_as_python_obj):
#         template_element = x
#         break
#
#     import sys
#     # print 'template_element=',template_element
#
#
#     # print '------------------extracting new format'
#
#     # template_element_record_format = get_record_format(template_element) #### RESTORE THIS - ORIGINAL
#     template_element_record_format = get_record_format_multi_trial(template_element_array)
#     pass
#
#     # print '--------- extracted template_element_recort_format=',template_element_record_format
#
#     # idx = 1
#     # # template_element_record_format_1 = {'names':template_element_record_format['names'][:idx],'formats':template_element_record_format['formats'][:idx]}
#     #
#     # template_element_record_format_1 = {'names':['aa'],'formats':[('<f8',())]}
#     # # print '--------- extracted new_template=',template_element_record_format_1
#     #
#     # reconstructed_array = np.recarray(shape=matlab_matrix_as_python_obj.shape, dtype=template_element_record_format_1)
#     #
#     # # reconstructed_array = np.recarray(shape=matlab_matrix_as_python_obj.shape, dtype=template_element_record_format)
#     # print 'reconstructed_array=',reconstructed_array
#     # return reconstructed_array
#     # # sys.exit()
#
#     reconstructed_array = np.recarray(shape=matlab_matrix_as_python_obj.shape, dtype=template_element_record_format)
#
#     for field_name in template_element_record_format['names']:
#
#         # print 'field_name = ', field_name
#         # print 'array_value=',matlab_matrix_structured [field_name]
#         field_val = getattr(template_element, field_name)
#         # print field_val, type(field_val).__name__
#         field_val_type = type(field_val).__name__
#
#         if field_val_type == 'ndarray':
#             for index, x in np.ndenumerate(reconstructed_array):
#                 # print 'index, x = ',index,reconstructed_array[field_name][index]
#                 # print 'index, x = ',index,matlab_matrix_structured ['m'][index]
#                 reconstructed_array[field_name][index] = matlab_matrix_structured[field_name][index]
#
#             pass
#         else:
#             try:
#                 reconstructed_array[field_name] = matlab_matrix_structured[field_name]
#             except ValueError:
#                 pass
#
#     return reconstructed_array
#
#
# def get_non_special_class_members(obj):
#     for class_member in inspect.getmembers(obj, lambda a: not (inspect.isroutine(a))):
#         class_member_name = class_member[0]
#         class_member_val = class_member[1]
#         class_member_type = type(class_member_val).__name__
#
#         if not (class_member_name.startswith('__') and class_member_name.endswith('__')):
#             yield class_member, class_member_name, class_member_val
#
#
# def get_record_format(obj):
#     names_list = []
#     format_list = []
#
#     for class_member, class_member_name, class_member_value in get_non_special_class_members(obj):
#         # print 'class_member, class_member_name, class_member_value=',(class_member, class_member_name, class_member_value)
#         #
#         # print 'class_member=',class_member
#         # print 'class_member_name=',class_member_name
#         # print 'class_member_value',class_member_value
#
#
#         try:
#             numpy_type_abbreviation = determine_dtype_abbreviation(class_member)
#             # print 'numpy_type_abbreviation=',numpy_type_abbreviation
#         except:
#             # print 'COULD NOT DETERMINE FORMAT FOR:'
#             # print 'class_member_name=', class_member_value
#             # print 'class_member_values=', class_member_value
#             # print 'SKIPPING this'
#             continue
#
#         names_list.append(class_member_name)
#         format_list.append(numpy_type_abbreviation)
#
#     return {'names': names_list, 'formats': format_list}
#
#
# # def get_record_format_multi_trial(obj_array):
# #
# #     names_list = []
# #     format_list = []
# #     obj = obj_array[0]
# #
# #     for class_member, class_member_name, class_member_value in get_non_special_class_members(obj):
# #         # print 'class_member, class_member_name, class_member_value=',(class_member, class_member_name, class_member_value)
# #         #
# #         # print 'class_member=',class_member
# #         # print 'class_member_name=',class_member_name
# #         # print 'class_member_value',class_member_value
# #
# #         # for obj_tmp in obj_array:
# #         try:
# #             numpy_type_abbreviation = determine_dtype_abbreviation(class_member)
# #             # print 'numpy_type_abbreviation=',numpy_type_abbreviation
# #         except:
# #             # print 'COULD NOT DETERMINE FORMAT FOR:'
# #             # print 'class_member_name=', class_member_value
# #             # print 'class_member_values=', class_member_value
# #             # print 'SKIPPING this'
# #             continue
# #
# #         # if initial guess for dtype is generic object type 'O' we try to improve this by
# #         # probing sample of record searching for a record where the inferred dtype is different than 'O'
# #         if numpy_type_abbreviation == 'O':
# #             for obj_tmp in obj_array:
# #                 class_member_fetched = getattr(obj_tmp,class_member_name)
# #                 try:
# #                     numpy_type_abbreviation_new_guess = determine_dtype_abbreviation(class_member_fetched)
# #                     # print 'numpy_type_abbreviation=',numpy_type_abbreviation
# #                 except:
# #                     continue
# #
# #                 if numpy_type_abbreviation_new_guess !='O':
# #                     numpy_type_abbreviation = numpy_type_abbreviation_new_guess
# #                     break
# #
# #
# #         names_list.append(class_member_name)
# #         format_list.append(numpy_type_abbreviation)
# #
# #     return {'names': names_list, 'formats': format_list}
#
#
#
# def get_record_format_multi_trial(obj_array):
#
#     names_list = []
#     format_list = []
#     obj = obj_array[0]
#
#     for class_member, class_member_name, class_member_value in get_non_special_class_members(obj):
#         # print 'class_member, class_member_name, class_member_value=',(class_member, class_member_name, class_member_value)
#         #
#         # print 'class_member=',class_member
#         # print 'class_member_name=',class_member_name
#         # print 'class_member_value',class_member_value
#         # if class_member_name=='avgSurf':
#         #     pass
#
#         # if class_member_name=='amplitude':
#         #     pass
#
#
#         if class_member_name=='avgSurf':
#             pass
#         # np.dtype(type(getattr(class_member[1],class_member[1]._fieldnames[0])))
#         # # for obj_tmp in obj_array:
#         # try:
#         #     numpy_type_abbreviation = determine_dtype_abbreviation(class_member)
#         #     # print 'numpy_type_abbreviation=',numpy_type_abbreviation
#         # except:
#         #     # print 'COULD NOT DETERMINE FORMAT FOR:'
#         #     # print 'class_member_name=', class_member_value
#         #     # print 'class_member_values=', class_member_value
#         #     # print 'SKIPPING this'
#         #     continue
#
#         # for obj_tmp in obj_array:
#         try:
#             numpy_type_abbreviation = determine_dtype_abbreviation(class_member)
#             # numpy_type_abbreviation = np.dtype(np.common_type(np.array([class_member]))).str
#             # print 'numpy_type_abbreviation=',numpy_type_abbreviation
#         except:
#             # print 'COULD NOT DETERMINE FORMAT FOR:'
#             # print 'class_member_name=', class_member_value
#             # print 'class_member_values=', class_member_value
#             # print 'SKIPPING this'
#             continue
#
#         # if initial guess for dtype is generic object type 'O' we try to improve this by
#         # probing sample of record searching for a record where the inferred dtype is different than 'O'
#
#
#         if numpy_type_abbreviation != 'O':
#             # sample_obj_array = []
#             # for obj_tmp in obj_array:
#             #     sample_obj_array.append(getattr(obj_tmp,class_member_name))
#             #
#             #
#             # try:
#             #     numpy_type_abbreviation = np.dtype(np.common_type(np.array(sample_obj_array))).str
#             # except TypeError:
#             #     print 'COULD NOT FIGURE OUT '+class_member_name
#             # pass
#
#             guessed_types = []
#             for obj_tmp in obj_array:
#                 class_member_fetched = getattr(obj_tmp,class_member_name)
#                 try:
#                     numpy_type_abbreviation_new_guess = np.array([class_member_fetched]).dtype.kind
#                     guessed_types.append(numpy_type_abbreviation_new_guess)
#                 except:
#                     continue
#                 # try:
#                 #     numpy_type_abbreviation_new_guess = determine_dtype_abbreviation(class_member_fetched)
#                 #     guessed_types.append(numpy_type_abbreviation_new_guess)
#                 #     # print 'numpy_type_abbreviation=',numpy_type_abbreviation
#                 # except:
#                 #     continue
#
#             guessed_types_np = np.array(guessed_types)
#
#             if 'f' in guessed_types_np:
#                 numpy_type_abbreviation = 'f8'
#
#         else:
#         # if numpy_type_abbreviation == 'O':
#             for obj_tmp in obj_array:
#                 class_member_fetched = getattr(obj_tmp,class_member_name)
#                 try:
#                     numpy_type_abbreviation_new_guess = determine_dtype_abbreviation(class_member_fetched)
#                     # print 'numpy_type_abbreviation=',numpy_type_abbreviation
#                 except:
#                     continue
#
#                 if numpy_type_abbreviation_new_guess !='O':
#                     numpy_type_abbreviation = numpy_type_abbreviation_new_guess
#                     break
#
#
#         names_list.append(class_member_name)
#         format_list.append(numpy_type_abbreviation)
#
#     return {'names': names_list, 'formats': format_list}
#
#
#
# def get_numpy_type_dict():
#     '''
#     this fcn is used to generate text of te dictionary that we use to manually construct numpy_type_dict
#     essentially this function examines all numpy types and figures out numpy dtype abbreviations. We use those to select most
#     accomodative types e.g. for python float we use '<f8' for python int we use '<i8' etc... This function prints report of
#     what numpy types are available and how objects of those types "seen" by Python's 'type' function
#     The output of this fcn will look something like:
#
#     <type 'float'> : ['<f4','<f8','<f2'],
#     <type 'int'> : ['<i4','<i8','<i2'],
#     ...
#
#     :return:numpy_type_dict
#     '''
#     from collections import defaultdict
#     # d = defaultdict(set)
#     numpy_type_dict = defaultdict(list)
#
#     for name in dir(np):
#         obj = getattr(np, name)
#
#         if hasattr(obj, 'dtype'):
#             # print 'name=',name
#             # print 'obj=',obj
#
#             try:
#                 npn = obj(0)  # creating object of a type in the dtype list
#                 # print 'npn=',npn
#                 nat = npn.item()
#                 # print('%s (%r) -> %s'%(name, npn.dtype.char, type(nat)))
#
#                 # d[type(nat)].add(npn.dtype.char)
#                 # numpy_type_dict[type(nat)].append(npn.dtype.char)
#                 numpy_type_dict[type(nat)].append(npn.dtype.str)
#             except:
#                 pass
#     for key, val in numpy_type_dict.items():
#         print str(key) + ':' + str(val)
#
#     return numpy_type_dict
#
# # numpy_type_dict = get_numpy_type_dict()
