__author__ = 'm'

import xarray as xray


# xray.backends.api.WRITEABLE_STORES['netcdf4'] = xray.backends.NetCDF4DataStoreRAM

import numpy
import numpy as np


from netCDF4 import chartostring, stringtoarr, Dataset

f = Dataset('my_compound_example.nc','w') # create a new dataset.
# create an unlimited  dimension call 'station'
f.createDimension('station',None)



NUMCHARS = 80 # number of characters to use in fixed-length strings.
winddtype = numpy.dtype([('speed','f4'),('direction','i4')])
statdtype = numpy.dtype([('latitude', 'f4'), ('longitude', 'f4'),
                         ('surface_wind',winddtype),
                         ('temp_sounding','f4',10),('press_sounding','i4',10),
                         ('location_name','S1',NUMCHARS)])
# use this data type definitions to create a compound data types
# called using the createCompoundType Dataset method.
# create a compound type for vector wind which will be nested inside
# the station data type. This must be done first!
wind_data_t = f.createCompoundType(winddtype,'wind_data')
# now that wind_data_t is defined, create the station data type.
station_data_t = f.createCompoundType(statdtype,'station_data')



statdat = f.createVariable('station_obs', station_data_t, ('station',))
# create a numpy structured array, assign data to it.
data = numpy.empty(2,station_data_t)
data['latitude'] = 40.
data['longitude'] = -105.
data['surface_wind']['speed'] = 12.5
data['surface_wind']['direction'] = 270
data['temp_sounding'] = (280.3,272.,270.,269.,266.,258.,254.1,250.,245.5,240.)
data['press_sounding'] = range(800,300,-50)

data['location_name'][0] = stringtoarr('Boulder, Colorado, USA',NUMCHARS)

print('data=',data)







# x = np.array([(1.0, 2), (3.0, 4)], dtype=[('x', 'f8'), ('y', 'i8')])
# x = np.array([(1.0, 'ba'), (3.0, 'ab')], dtype=[('x', 'f8'), ('y', 'S1',2)])

# x = np.array([(1.0, 'ba'), (3.0, 'ab')], dtype=np.dtype({'names':['x','y'], 'formats':['f8',('S1',2)]}))

x = np.array([(1.0, 'ba'), (3.0, 'ab')], dtype=np.dtype({'names':['x','y'], 'formats':['f8','S2']}))


x_dtype = x.dtype

from copy import deepcopy
# x_dtype_copy=deepcopy(x.dtype)

new_dtype_dict = {'names':[],'formats':[]}

for field, dt in list(x_dtype.fields.items()):
    print(field)
    # print type(dt[0])
    # print dir(dt[0])

    print('char = ', dt[0].char)
    print('kind = ', dt[0].kind)
    print('shape = ', dt[0].itemsize)

    if dt[0].kind =='S' and dt[0].itemsize>1:
        new_dtype_dict['names'].append(field)
        new_dtype_dict['formats'].append(('S1',dt[0].itemsize))
    else:
        new_dtype_dict['names'].append(field)
        new_dtype_dict['formats'].append(dt[0].descr[0][1])




def str_array_to_char_array_mapper(array,str_size):
    new_array = map(lambda x: stringtoarr(x,str_size), array)
    return new_array
    pass



print(new_dtype_dict)

x_new = np.empty(x.shape[0],dtype=new_dtype_dict)


print(x_new['y'].dtype)

# sys.exit()



from netCDF4 import chartostring, stringtoarr

x_new['x'] = x['x']

# x_new['y'][0] = stringtoarr('ab',2)
# x_new['y'][1] = stringtoarr('cd',2)



# x_new['y']=map(lambda x:stringtoarr(x,2),x['y'])
x_new['y']=str_array_to_char_array_mapper(x['y'],2)

    # map(lambda x:stringtoarr(x,2),x['y'])



a = np.arange(20).reshape(2,10)

a_xray = xray.DataArray(a, coords=[x_new,np.arange(10)],dims=['events','time'])
# a_xray = xray.DataArray(a, coords=[np.arange(2),np.arange(10)],dims=['events','time'])
a_xray.attrs['samplerate'] = 500
a_xray.attrs['buffer'] = 1.0

print(a_xray)


a_xray_ds = xray.Dataset({'a_xray':a_xray})

a_xray_ds.to_netcdf('a_xray.nc')


a_xray_ds_read = xray.open_dataset('a_xray.nc')

a_xray_read = a_xray_ds_read['a_xray']

print('a_xray_read=',a_xray_read)

from netCDF4 import Dataset

rootgrp = Dataset('custom_xray.nc', 'w', format='NETCDF4')

values_var = rootgrp.createVariable('values','f8',None)


values_var[:] = a_xray.values

rootgrp.close()

sys.exit()

# values_grp = rootgrp.createGroup('values')




import sys
sys.exit()



from netCDF4 import Dataset

# code from tutorial.

# create a file (Dataset object, also the root group).
rootgrp = Dataset('test.nc', 'w', format='NETCDF4')
print((rootgrp.file_format))
rootgrp.close()

rootgrp = Dataset('test.nc', 'a')
fcstgrp = rootgrp.createGroup('forecasts')
lat = rootgrp.createDimension('lat', 73)
latitudes = rootgrp.createVariable('latitude','f4',('lat',))
latitudes = np.arange(73)

# compound types
x_dtype = x.dtype

x_dtype_t = rootgrp.createCompoundType(x_dtype,'x_dtype')
print()


# create a variable with this data type, write some data to it.
rootgrp.createDimension('x_dim',2)
x_var = rootgrp.createVariable('x_var',x_dtype_t,'x_dim')


print('str x.dtype=', str(x.dtype))

# create a variable with this data type, write some data to it.
# rootgrp.createDimension('x_dim',2)
# x_var = rootgrp.createVariable('x_var',x_dtype_t,'x_dim')


x_var[:] = x

rootgrp.close()


f = Dataset('test.nc')
# print(f)
# print(f.variables['x_var'])
# print(f.cmptypes)
# print(f.cmptypes['complex128'])
v = f.variables['x_var']
print((v.shape))

print('v=',v[:])

sys.exit()





# a_xray_ds = a_xray.to_dataset()

a_xray_ds = xray.Dataset({'a_xray':a_xray})
a_xray_ds.attrs = a_xray.attrs



a_xray_ds.to_netcdf('a_xray_ds.nc', format='NETCDF4',engine='netcdf4')
# a_xray_ds.to_netcdf('a_xray_ds.nc', format='NETCDF4',engine='h5netcdf')


a_xray_read_dataset = xray.open_dataset('a_xray_ds.nc')
#
print('a_xray_read_dataset=',a_xray_read_dataset)

print('a_xray_read_dataset.attrs=',a_xray_read_dataset.attrs)

#
#
a_xray_read = a_xray_read_dataset.to_array()
#
print(a_xray_read)
print(a_xray_read.attrs)




# a_xray_ds = xray.Dataset({'a_xray':a_xray})
#
# a_xray_ds.to_netcdf('a_xray_ds.nc', format='NETCDF4',engine='netcdf4')
