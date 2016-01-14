__author__ = 'm'

import xray
import numpy as np


class NetCDF4XrayWriter(object):
    def __init__(self, array):
        self.array = array

    def write(self,filename):
        dim_sizes = map(len,self.array.coords.values())
        dim_names = self.array.dims

        dim_names_appended = map(lambda x : x, self.array.dims)
        # dim_names_appended = map(lambda x : x+'_dim', self.array.dims) ##restore it

        values_dict = {'array':(tuple(dim_names_appended),self.array.values)}

        # axes
        coords_dict = {}
        # coords_dict = {'axis_names':['channels','time','events']}
        coords_dict = {'axis_names':list(self.array.dims)}





        for dim_name in self.array.dims:
            # if self.array[dim_name].dtype.isbuiltin:
            if self.array[dim_name].dtype.fields is None: #indicates simple type, not a recarray
                coords_dict['axis__'+dim_name] = self.array[dim_name].values
            else:
                for field, dtype_tuple in self.array[dim_name].dtype.fields.items():
                    if self.array[dim_name].values[field].dtype.char=='O':
                        print 'WE ARE NOT STORING VARIABLES OF TYPE=OBJECT IN THIS WRITER '
                        continue
                    dtype = dtype_tuple[0]
                    print field
                    # print type(dt[0])
                    # print dir(dt[0])

                    print 'char = ', dtype.char
                    print 'kind = ', dtype.kind
                    print 'shape = ', dtype.itemsize
                    print 'dt.isbuiltin = ',dtype.isbuiltin

                    # print self.array[dim_name].values['y']
                    # coords_dict['axis__events__y']=x['y']
                    print 'field=',field,' array=',self.array[dim_name].values[field]
                    coords_dict['axis__'+dim_name+'__'+field] = self.array[dim_name].values[field]


        # print 'coords_dict=',coords_dict
        # coords_dict['axis__events__stimAnodeTag'] = self.array['events'].values['stimAnodeTag']
        # coords_dict['axis__events__stimCathode'] = self.array['events'].values['stimCathode']
        # coords_dict['axis__events__itenmo'] = self.array['events'].values['itemno']

                #     if dt[0].kind =='S' and dt[0].itemsize>1:
                #         new_dtype_dict['names'].append(field)
                #         new_dtype_dict['formats'].append(('S1',dt[0].itemsize))
                #     else:
                #         new_dtype_dict['names'].append(field)
                #         new_dtype_dict['formats'].append(dt[0].descr[0][1])
                #
                # for




        print 'dim_sizes=',dim_sizes
        print 'dim_names=',dim_names


        ds = xray.Dataset(
            values_dict,
            coords=coords_dict
        )


        ds.to_netcdf(filename)


        print ds
