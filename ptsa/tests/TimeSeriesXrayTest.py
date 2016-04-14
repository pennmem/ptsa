__author__ = 'm'

import xray
import numpy as np
from ptsa.data.TimeSeriesXray import TimeSeriesXray
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






d = np.arange(120).reshape(4, 3, 10)

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

print base_events_ptsa

base_ev_data_ptsa, base_ev_data_xray = base_events_ptsa.get_data(channels=channels, start_time=0.0, end_time=1.6,
                                                                 buffer_time=1.0, eoffset='eegoffset', keep_buffer=True,
                                                                 eoffset_in_time=False, verbose=True, return_both=True)


# casting data DataArray into TimeSeriesXray
base_ev_data_xray = TimeSeriesXray(base_ev_data_xray)


# baseline_corrected test

corrected_base_ev_data_ptsa = base_ev_data_ptsa.baseline_corrected((0.0, 0.2))

corrected_base_ev_data_xray = base_ev_data_xray.baseline_corrected((0.0, 0.2))


# remove buffer test
no_buffer_base_ev_data_ptsa = base_ev_data_ptsa.remove_buffer(1.0)
no_buffer_base_ev_data_xray = base_ev_data_xray.remove_buffer(1.0)

no_buffer_dataset = xray.Dataset({'no_buffer': no_buffer_base_ev_data_xray})

from ptsa.data.writers.NetCDF4XrayWriter import NetCDF4XrayWriter

nc4_writer = NetCDF4XrayWriter(no_buffer_base_ev_data_xray)
nc4_writer.write('no_buffer_base_ev_data_xray_new.nc')

from ptsa.data.readers.NetCDF4XrayReader import NetCDF4XrayReader

nc4_reader = NetCDF4XrayReader()
array = nc4_reader.read('no_buffer_base_ev_data_xray_new.nc')

print array['events']

sys.exit()

a = no_buffer_base_ev_data_xray
a['events'] = np.arange(len(a['events']))
a['channels'] = np.arange(len(a['channels']))
# a['channels']=np.arange(len(a['channels']))
# a['events']=np.arange(len(a['events']))
print a
nb = xray.Dataset({'no_buffer': a})
nb.to_netcdf('no_buffer.nc')

print 'EXITING AFTER BUFFER TEST'
import sys

sys.exit(0)

# filtered_test

base_ev_data_ptsa_filtered = base_ev_data_ptsa.filtered([58, 62], filt_type='stop', order=4)

base_ev_data_xray_filtered = base_ev_data_xray.filtered([58, 62], filt_type='stop', order=4)

# resample test
import time

s = time.time()
print 'starting resampling'
base_ev_data_ptsa_resampled = base_ev_data_ptsa_filtered.resampled(50)
f = time.time()
print 'finished resampleing base_ev_data_ptsa_resampled time= ', f - s

s = time.time()
base_ev_data_xray_resampled = base_ev_data_xray_filtered.resampled(50)
f = time.time()
print 'finished resampleing base_ev_data_xray_resampled time= ', f - s

print
# ts = TimeSeriesXray(ts_ev_data)
#
# ###################################################################################################################
# from ptsa.data.readers.TimeSeriesEEGReader import TimeSeriesEEGReader
#
# time_series_reader = TimeSeriesEEGReader(events=base_events, start_time=0.0,
#                                              end_time=1.6, buffer_time=1.0, keep_buffer=True)
# # time_series_reader = TimeSeriesSessionEEGReader(events=base_events, channels=monopolar_channels)
# ts_ev_data = time_series_reader.read(channels = channels)
#
# print ts_ev_data




# d_x = xray.DataArray(d,coords=[np.arange(d.shape[0])*10, np.arange(d.shape[1])*100,np.arange(d.shape[2])*1000],dims=['channels','events','time'])
#
# ts = TimeSeriesXray(d_x)




# ts = TimeSeriesXray(ts_ev_data)




# print  'ts=',ts





# class TimeSeriesXray(xray.DataArray):
#
#     def __init__(self,data,**kwds):
#         xray.DataArray.__init__(self,data,**kwds)
#         self.a=10
#         self.time_axis_index=get_axis_index(self,axis_name='time')
#
#
#
#     def filtered(self,freq_range,filt_type='stop',order=4):
#         """
#         Filter the data using a Butterworth filter and return a new
#         TimeSeries instance.
#
#         Parameters
#         ----------
#         freq_range : {array_like}
#             The range of frequencies to filter.
#         filt_type = {scipy.signal.band_dict.keys()},optional
#             Filter type.
#         order = {int}
#             The order of the filter.
#
#         Returns
#         -------
#         ts : {TimeSeries}
#             A TimeSeries instance with the filtered data.
#         """
#
#         from ptsa.filt  import buttfilt
#
#         filtered_array = buttfilt(self.values, freq_range, self.attrs['samplerate'], filt_type,
#                                        order,axis=self.time_axis_index)
#
#         # filtered_time_series = xray.DataArray(
#         #     filtered_array,
#         #     coords = [xray.DataArray(coord.copy()) for coord_name, coord in self.coords.items() ]
#         # )
#
#         filtered_time_series = TimeSeriesXray(
#             filtered_array,
#             coords = [xray.DataArray(coord.copy()) for coord_name, coord in self.coords.items() ]
#         )
#
#
#         filtered_time_series.attrs = self.attrs.copy()
#
#         return filtered_time_series
#
#
#     def resampled(self, resampled_rate, window=None,
#                   loop_axis=None, num_mp_procs=0, pad_to_pow2=False):
#         '''
#
#         :param resampled_rate: resample rate
#         :param window: ignored for now - added for legacy reasons
#         :param loop_axis: ignored for now - added for legacy reasons
#         :param num_mp_procs: ignored for now - added for legacy reasons
#         :param pad_to_pow2: ignored for now - added for legacy reasons
#         :return: resampled time series
#         '''
#
#         from scipy.signal import resample
#         samplerate = self.attrs['samplerate']
#
#
#         time_axis = self['time']
#         time_axis_length = np.squeeze(time_axis.shape)
#         new_length = int(np.round(time_axis_length*resampled_rate/float(samplerate)))
#
#         # print new_length
#
#         # if self.time_axis_index<0:
#         #     self.time_axis_index = get_axis_index(data_array=self, axis_name='time')
#
#         # time_axis = self.coords[ self.dims[self.time_axis_index] ]
#
#         # time_axis = self['time']
#
#         resampled_array, new_time_axis = resample(self.values,
#                                          new_length, t=time_axis.values,
#                                          axis=self.time_axis_index, window=window)
#
#
#         # print new_time_axis
#
#         #constructing axes
#         coords = []
#         for i, dim_name in enumerate(self.dims):
#             if i != self.time_axis_index:
#                 coords.append(self.coords[dim_name].copy())
#             else:
#                 coords.append((dim_name,new_time_axis))
#
#
#         resampled_time_series = xray.DataArray(resampled_array, coords=coords)
#         resampled_time_series.attrs['samplerate'] = resampled_rate
#
#         return resampled_time_series
#
#
#     def remove_buffer(self, duration):
# 	"""
#         Remove the desired buffer duration (in seconds) and reset the
# 	time range.
#
#         Parameter
#         ---------
#         duration : {int,float,({int,float},{int,float})}
#             The duration to be removed. The units depend on the samplerate:
#             E.g., if samplerate is specified in Hz (i.e., samples per second),
#             the duration needs to be specified in seconds and if samplerate is
#             specified in kHz (i.e., samples per millisecond), the duration needs
#             to be specified in milliseconds.
#             A single number causes the specified duration to be removed from the
#             beginning and end. A 2-tuple can be passed in to specify different
#             durations to be removed from the beginning and the end respectively.
#
#         Returns
#         -------
#         ts : {TimeSeries}
#             A TimeSeries instance with the requested durations removed from the
#             beginning and/or end.
#         """
#
#         number_of_buffer_samples =  int(np.ceil(duration*self.attrs['samplerate']))
#         if number_of_buffer_samples > 0:
#             return  self[:,:,number_of_buffer_samples:-number_of_buffer_samples]
#
#
#
#     def baseline_corrected(self, base_range):
#         """
#
#         Return a baseline corrected timeseries by subtracting the
#         average value in the baseline range from all other time points
#         for each dimension.
#
#         Parameters
#         ----------
#         base_range: {tuple}
#             Tuple specifying the start and end time range (inclusive)
#             for the baseline.
#
#         Returns
#         -------
#         ts : {TimeSeries}
#             A TimeSeries instance with the baseline corrected data.
#
#         """
#
#         return self - self.isel(time=(self['time'] >= base_range[0]) & (self['time'] <= base_range[1])).mean(dim='time')
