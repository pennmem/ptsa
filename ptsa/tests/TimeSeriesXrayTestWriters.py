__author__ = 'm'

import xray
import numpy as np
import pathlib

from os.path import *

from ptsa.data.common import get_axis_index

from ptsa.data.rawbinwrapper import RawBinWrapper
from ptsa.data.events import Events


def attach_rawbinwrappers(evs):
    evs = evs.add_fields(esrc=np.dtype(RawBinWrapper))

    eegfiles = np.unique(evs.eegfile)

    for eegfile in eegfiles:
        eeg_file_path = str(eegfile)

            # join(prefix, str(pathlib.Path(str(eegfile)).parts[1:]))
        raw_bin_wrapper = RawBinWrapper(eeg_file_path)
        inds = np.where(evs.eegfile == eegfile)[0]
        for i in inds:
            evs[i]['esrc'] = raw_bin_wrapper
    return evs
# self.subject_path = str(pathlib.Path(eeg_file_path).parts[:-2])

# attaching
# evs.add_fields(esrc=np.dtype(RawBinWrapper))




class TimeSeriesXray(xray.DataArray):

    def __init__(self,data,**kwds):
        xray.DataArray.__init__(self,data,**kwds)
        self.a=10
        self.time_axis_index=get_axis_index(self,axis_name='time')



    def filtered(self,freq_range,filt_type='stop',order=4):
        """
        Filter the data using a Butterworth filter and return a new
        TimeSeries instance.

        Parameters
        ----------
        freq_range : {array_like}
            The range of frequencies to filter.
        filt_type = {scipy.signal.band_dict.keys()},optional
            Filter type.
        order = {int}
            The order of the filter.

        Returns
        -------
        ts : {TimeSeries}
            A TimeSeries instance with the filtered data.
        """

        from ptsa.filt  import buttfilt

        filtered_array = buttfilt(self.values, freq_range, self.attrs['samplerate'], filt_type,
                                       order,axis=self.time_axis_index)

        # filtered_time_series = xray.DataArray(
        #     filtered_array,
        #     coords = [xray.DataArray(coord.copy()) for coord_name, coord in self.coords.items() ]
        # )

        filtered_time_series = TimeSeriesXray(
            filtered_array,
            coords = [xray.DataArray(coord.copy()) for coord_name, coord in list(self.coords.items()) ]
        )


        filtered_time_series.attrs = self.attrs.copy()

        return filtered_time_series


    def resampled(self, resampled_rate, window=None,
                  loop_axis=None, num_mp_procs=0, pad_to_pow2=False):
        '''

        :param resampled_rate: resample rate
        :param window: ignored for now - added for legacy reasons
        :param loop_axis: ignored for now - added for legacy reasons
        :param num_mp_procs: ignored for now - added for legacy reasons
        :param pad_to_pow2: ignored for now - added for legacy reasons
        :return: resampled time series
        '''

        from scipy.signal import resample
        samplerate = self.attrs['samplerate']


        time_axis = self['time']
        time_axis_length = np.squeeze(time_axis.shape)
        new_length = int(np.round(time_axis_length*resampled_rate/float(samplerate)))

        # print new_length

        # if self.time_axis_index<0:
        #     self.time_axis_index = get_axis_index(data_array=self, axis_name='time')

        # time_axis = self.coords[ self.dims[self.time_axis_index] ]

        # time_axis = self['time']

        resampled_array, new_time_axis = resample(self.values,
                                         new_length, t=time_axis.values,
                                         axis=self.time_axis_index, window=window)


        # print new_time_axis

        #constructing axes
        coords = []
        for i, dim_name in enumerate(self.dims):
            if i != self.time_axis_index:
                coords.append(self.coords[dim_name].copy())
            else:
                coords.append((dim_name,new_time_axis))


        resampled_time_series = xray.DataArray(resampled_array, coords=coords)
        resampled_time_series.attrs['samplerate'] = resampled_rate

        return resampled_time_series


    def remove_buffer(self, duration):
	"""
        Remove the desired buffer duration (in seconds) and reset the
	time range.

        Parameter
        ---------
        duration : {int,float,({int,float},{int,float})}
            The duration to be removed. The units depend on the samplerate:
            E.g., if samplerate is specified in Hz (i.e., samples per second),
            the duration needs to be specified in seconds and if samplerate is
            specified in kHz (i.e., samples per millisecond), the duration needs
            to be specified in milliseconds.
            A single number causes the specified duration to be removed from the
            beginning and end. A 2-tuple can be passed in to specify different
            durations to be removed from the beginning and the end respectively.

        Returns
        -------
        ts : {TimeSeries}
            A TimeSeries instance with the requested durations removed from the
            beginning and/or end.
        """

        number_of_buffer_samples =  int(np.ceil(duration*self.attrs['samplerate']))
        if number_of_buffer_samples > 0:
            return  self[:,:,number_of_buffer_samples:-number_of_buffer_samples]



    def baseline_corrected(self, base_range):
        """

        Return a baseline corrected timeseries by subtracting the
        average value in the baseline range from all other time points
        for each dimension.

        Parameters
        ----------
        base_range: {tuple}
            Tuple specifying the start and end time range (inclusive)
            for the baseline.

        Returns
        -------
        ts : {TimeSeries}
            A TimeSeries instance with the baseline corrected data.

        """

        return self - self.isel(time=(self['time'] >= base_range[0]) & (self['time'] <= base_range[1])).mean(dim='time')


d = np.arange(120).reshape(4,3,10)


channels = ['002', '003', '004', '005']


from ptsa.data.readers import BaseEventReader

e_path = '/Users/m/data/events/RAM_FR1/R1060M_events.mat'
base_e_reader = BaseEventReader(event_file=e_path, eliminate_events_with_no_eeg=True, use_ptsa_events_class=False)

base_events = base_e_reader.read()

base_events = base_events[base_events.type == 'WORD']



base_e_reader_ptsa = BaseEventReader(event_file=e_path, eliminate_events_with_no_eeg=True, use_ptsa_events_class=False)
base_events_ptsa = base_e_reader_ptsa.read()

base_events_ptsa = base_events_ptsa[base_events_ptsa.type == 'WORD']
base_events_ptsa = Events(base_events_ptsa)

base_events_ptsa = attach_rawbinwrappers(base_events_ptsa)

print(base_events_ptsa)

base_ev_data_ptsa, base_ev_data_xray = base_events_ptsa.get_data(channels=channels, start_time=0.0, end_time=1.6,
                                        buffer_time=1.0, eoffset='eegoffset', keep_buffer=True, eoffset_in_time=False,verbose=True, return_both=True)


# casting data DataArray into TimeSeriesXray
base_ev_data_xray = TimeSeriesXray(base_ev_data_xray)


#baseline_corrected test

corrected_base_ev_data_ptsa = base_ev_data_ptsa.baseline_corrected((0.0,0.2))

corrected_base_ev_data_xray = base_ev_data_xray.baseline_corrected((0.0,0.2))


# remove buffer test
no_buffer_base_ev_data_ptsa = base_ev_data_ptsa.remove_buffer(1.0)
no_buffer_base_ev_data_xray = base_ev_data_xray.remove_buffer(1.0)



#
# print array['events']

from ptsa.data.writers.NetCDF4XrayWriter import NetCDF4XrayWriter
nc4_writer = NetCDF4XrayWriter(no_buffer_base_ev_data_xray)
nc4_writer.write('no_buffer_base_ev_data_xray_new.nc')


from ptsa.data.readers.NetCDF4XrayReader import NetCDF4XrayReader
nc4_reader = NetCDF4XrayReader()
array = nc4_reader.read('no_buffer_base_ev_data_xray_new.nc')

print(array['events'])






# class NetCDF4Writer(object):
#     def __init__(self, array):
#         self.array = array
#
#     def write(self,filename):
#         dim_sizes = map(len,self.array.coords.values())
#         dim_names = self.array.dims
#
#         dim_names_appended = map(lambda x : x, self.array.dims)
#         # dim_names_appended = map(lambda x : x+'_dim', self.array.dims) ##restore it
#
#         values_dict = {'array':(tuple(dim_names_appended),self.array.values)}
#
#         # axes
#         coords_dict = {}
#         # coords_dict = {'axis_names':['channels','time','events']}
#         coords_dict = {'axis_names':list(self.array.dims)}
#
#
#
#
#
#         for dim_name in self.array.dims:
#             # if self.array[dim_name].dtype.isbuiltin:
#             if self.array[dim_name].dtype.fields is None: #indicates simple type, not a recarray
#                 coords_dict['axis__'+dim_name] = self.array[dim_name].values
#             else:
#                 for field, dtype_tuple in self.array[dim_name].dtype.fields.items():
#                     if self.array[dim_name].values[field].dtype.char=='O':
#                         print 'WE ARE NOT STORING VARIABLES OF TYPE=OBJECT IN THIS WRITER '
#                         continue
#                     dtype = dtype_tuple[0]
#                     print field
#                     # print type(dt[0])
#                     # print dir(dt[0])
#
#                     print 'char = ', dtype.char
#                     print 'kind = ', dtype.kind
#                     print 'shape = ', dtype.itemsize
#                     print 'dt.isbuiltin = ',dtype.isbuiltin
#
#                     # print self.array[dim_name].values['y']
#                     # coords_dict['axis__events__y']=x['y']
#                     print 'field=',field,' array=',self.array[dim_name].values[field]
#                     coords_dict['axis__'+dim_name+'__'+field] = self.array[dim_name].values[field]
#
#
#         # print 'coords_dict=',coords_dict
#         # coords_dict['axis__events__stimAnodeTag'] = self.array['events'].values['stimAnodeTag']
#         # coords_dict['axis__events__stimCathode'] = self.array['events'].values['stimCathode']
#         # coords_dict['axis__events__itenmo'] = self.array['events'].values['itemno']
#
#                 #     if dt[0].kind =='S' and dt[0].itemsize>1:
#                 #         new_dtype_dict['names'].append(field)
#                 #         new_dtype_dict['formats'].append(('S1',dt[0].itemsize))
#                 #     else:
#                 #         new_dtype_dict['names'].append(field)
#                 #         new_dtype_dict['formats'].append(dt[0].descr[0][1])
#                 #
#                 # for
#
#
#
#
#         print 'dim_sizes=',dim_sizes
#         print 'dim_names=',dim_names
#
#
#         ds = xray.Dataset(
#             values_dict,
#             coords=coords_dict
#         )
#
#
#         ds.to_netcdf(filename)
#
#
#         print ds
#
# nc4_writer = NetCDF4Writer(no_buffer_base_ev_data_xray)
# nc4_writer.write('no_buffer_base_ev_data_xray.nc')
#
#
#
#
# class NetCDF4Reader(object):
#     def __init__(self):
#         pass
#
#     def read(self,filename):
#         ds = xray.open_dataset(filename)
#
#         array = xray.DataArray(ds['array'])
#         print array
#         print ds
#
#         #reconstructing axes
#         for axis_name in ds['axis_names'].values:
#             axis_array = self.reconstruct_axis(ds,str(axis_name))
#
#             array[axis_name] = axis_array
#
#         return array
#
#
#     def reconstruct_axis(self,ds,axis_name):
#         # axis_element_names = filter(lambda x : x.startswith('axis__'+axis_name), ds.dims)
#         axis_identifier_str = 'axis__'+axis_name
#         axis_element_names = filter(lambda dim_name : dim_name.startswith(axis_identifier_str), list(ds.dims))
#
#         axis_size = len(ds[axis_element_names[0]].values)
#         recarray_flag = len(axis_element_names)>1
#         axis_array = None
#
#         if recarray_flag:
#             print axis_element_names
#             axis_dtype={'names':[],'formats':[]}
#
#             for full_axis_element_name in axis_element_names:
#                 axis_element_name = full_axis_element_name.replace(axis_identifier_str+'__','')
#                 print ds[full_axis_element_name].values
#                 print ds[full_axis_element_name].dtype
#                 axis_dtype['names'].append(axis_element_name)
#                 axis_dtype['formats'].append(str(ds[full_axis_element_name].dtype))
#
#             # creating recarray
#             axis_array = np.empty(axis_size, dtype=axis_dtype)
#
#             # populating columns of the recarray
#             for full_axis_element_name in axis_element_names:
#                 axis_element_name = full_axis_element_name.replace(axis_identifier_str+'__','')
#                 axis_array[axis_element_name] = ds[full_axis_element_name].values
#
#         else:
#             axis_array = ds[axis_element_names[0]].values
#
#         print axis_array
#         print axis_array.dtype
#         return axis_array
#
#
# nc4_reader = NetCDF4Reader()
#
# array = nc4_reader.read('no_buffer_base_ev_data_xray.nc')
