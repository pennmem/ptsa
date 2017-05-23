ptsa.data
*********

.. toctree::
   :maxdepth: 1

   ptsa.data.readers
   ptsa.data.filters
   ptsa.data.edf
   ptsa.data.common

ptsa.data.TimeSeriesX
=====================


ptsa.data.events
================

class ptsa.data.events.Events

   Bases: "numpy.recarray"

   A recarray with the events to be analyzed. Includes convenience
   functions to add and remove fields and a function to get a
   TimeSeries instance with the data linked to each event.

   add_fields(**fields)

      Add fields from the keyword args provided and return a new
      instance.

      >>**<<fields_to_add : {dictionary}
         Names in the dictionary correspond to new field names and the
         values specify their content. To add an empty field, pass a
         dtype as the value.

      New Events instance with the specified new fields.

      events.add_fields(name1=array1, name2=dtype('i4'))

   get_data(channels, start_time, end_time, buffer_time=0.0, resampled_rate=None, filt_freq=None, filt_type='stop', filt_order=4, keep_buffer=False, esrc='esrc', eoffset='eoffset', loop_axis=None, num_mp_procs=0, eoffset_in_time=True, **kwds)

      Return the requested range of data for each event by using the
      proper data retrieval mechanism for each event.

      channels: {list,int,None}
         Channels from which to load data.

      start_time: {float}
         Start of epoch to retrieve (in time-unit of the data).

      end_time: {float}
         End of epoch to retrieve (in time-unit of the data).

      buffer_time: {float},optional
         Extra buffer to add on either side of the event in order to
         avoid edge effects when filtering (in time unit of the data).

      resampled_rate: {float},optional
         New samplerate to resample the data to after loading.

      filt_freq: {array_like},optional
         The range of frequencies to filter (depends on the filter
         type.)

      filt_type = {scipy.signal.band_dict.keys()},optional
         Filter type.

      filt_order = {int},optional
         The order of the filter.

      keep_buffer: {boolean},optional
         Whether to keep the buffer when returning the data.

      esrc : {string},optional
         Name for the field containing the source for the time series
         data corresponding to the event.

      eoffset: {string},optional
         Name for the field containing the offset (in seconds) for the
         event within the specified source.

      eoffset_in_time: {boolean},optional
         If True, the unit of the event offsets is taken to be time
         (unit of the data), otherwise samples.

      verbose: {bool} turns on verbose printout of the function -
         e.g. timing information will be output to the screen

      A TimeSeries instance with dimensions (channels,events,time). or
      A TimeSeries instance with dimensions (channels,events,time) and
      xray.DataArray with dimensions (channels,events,time)

   remove_fields(*fields_to_remove)

      Return a new instance of the recarray with specified fields
      removed.

      >>*<<fields_to_remove : {list of strings}

      New Events instance without the specified fields.


ptsa.data.timeseries
====================

class ptsa.data.timeseries.TimeSeries(data, tdim, samplerate, *args, **kwargs)

   Bases: "dimarray.dimarray.DimArray"

   A subclass of DimArray to hold timeseries data (i.e. data with a
   time dimension and associated sample rate).  It also provides
   methods for manipulating the time dimension, such as resampling and
   filtering the data.

   data : {array_like}
      The time series data.

   tdim : {str}
      The name of the time dimension.

   samplerate : {float}
      The sample rate of the time dimension. Constrained to be of type
      float (any passed in value is converted to a float).

   >>*<<args : {>>*<<args},optional
      Additinal custom attributes

   >>**<<kwargs : {>>**<<kwargs},optional
      Additional custom keyword attributes.

   Useful additional (keyword) attributes include dims, dtype, and
   copy (see DimArray docstring for details).

   DimArray

   >>> import numpy as np
   >>> import dimarray as da
   >>> import ptsa.data.timeseries as ts
   >>> observations = da.Dim(['a','b','c'],'obs')
   >>> time = da.Dim(np.arange(4),'time')
   >>> data = ts.TimeSeries(np.random.rand(3,4),'time',samplerate=1,
                            dims=[observations,time])
   >>> data
   TimeSeries([[ 0.51244513,  0.39930142,  0.63501339,  0.67071605],
      [ 0.46962664,  0.51071395,  0.46748319,  0.78265951],
      [ 0.85515317,  0.10996395,  0.41642481,  0.50561768]])

   >>> data.samplerate
   1.0
   >>> data.tdim
   'time'

   baseline_corrected(base_range)

      Return a baseline corrected timeseries by subtracting the
      average value in the baseline range from all other time points
      for each dimension.

      base_range: {tuple}
         Tuple specifying the start and end time range (inclusive)
         for the baseline.

      ts : {TimeSeries}
         A TimeSeries instance with the baseline corrected data.

   filtered(freq_range, filt_type='stop', order=4)

      Filter the data using a Butterworth filter and return a new
      TimeSeries instance.

      freq_range : {array_like}
         The range of frequencies to filter.

      filt_type = {scipy.signal.band_dict.keys()},optional
         Filter type.

      order = {int}
         The order of the filter.

      ts : {TimeSeries}
         A TimeSeries instance with the filtered data.

   remove_buffer(duration)

      Remove the desired buffer duration (in seconds) and reset the
      time range.

      duration : {int,float,({int,float},{int,float})}
         The duration to be removed. The units depend on the
         samplerate: E.g., if samplerate is specified in Hz (i.e.,
         samples per second), the duration needs to be specified in
         seconds and if samplerate is specified in kHz (i.e., samples
         per millisecond), the duration needs to be specified in
         milliseconds. A single number causes the specified duration
         to be removed from the beginning and end. A 2-tuple can be
         passed in to specify different durations to be removed from
         the beginning and the end respectively.

      ts : {TimeSeries}
         A TimeSeries instance with the requested durations removed
         from the beginning and/or end.

   resampled(resampled_rate, window=None, loop_axis=None, num_mp_procs=0, pad_to_pow2=False)

      Resample the data and reset all the time ranges.

      Uses the resample function from scipy.  This method seems to be
      more accurate than the decimate method.

      resampled_rate : {float}
         New sample rate to resample to.

      window : {None,str,float,tuple}, optional
         See scipy.signal.resample for details

      loop_axis: {None,str,int}, optional
         Sometimes it might be faster to loop over an axis.

      num_mp_procs: int, optional
         Whether to try and use multiprocessing to loop over axis. 0
         means no multiprocessing >0 specifies num procs to use None
         means yes, and use all possible procs

      pad_to_pow2: bool, optional
         Pad along the time dimension to the next power of 2 so that
         the resampling is much faster (experimental).

      ts : {TimeSeries}
         A TimeSeries instance with the resampled data.

      scipy.signal.resample

   taxis

      Numeric time axis (read only).
