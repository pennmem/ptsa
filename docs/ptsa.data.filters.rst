ptsa.data.filters
*****************


ptsa.data.filters.ButterworthFilter
===================================

class ptsa.data.filters.ButterworthFilter.ButterworthFilter(**kwds)

   Bases: "ptsa.data.common.TypedUtils.PropertiedObject",
   "ptsa.data.filters.BaseFilter.BaseFilter"

   Applies Butterworth filter to a time series

   Parameters:
      **kwds** -- allowed values are:

   :param time_series
      TimeSeriesX object

   :param order
      Butterworth filter order

   :param freq_range{list-like}
      Array [min_freq, max_freq] describing the filter range

   :return :None

   filter()

      Applies Butterwoth filter to input time series and returns
      filtered TimeSeriesX object :return: TimeSeriesX object


ptsa.data.filters.DataChopper
=============================

class ptsa.data.filters.DataChopper.DataChopper(**kwds)

   Bases: "ptsa.data.common.TypedUtils.PropertiedObject",
   "ptsa.data.filters.BaseFilter.BaseFilter"

   EventDataChopper converts continuous time series of entire session
   into chunks based on the events specification In other words you
   may read entire eeg session first and then using EventDataChopper
   divide it into chunks corresponding to events of your choice

   filter()

      Chops session into chunks orresponding to events :return:
      timeSeriesX object with chopped session

   get_event_chunk_size_and_start_point_shift(eegoffset, samplerate, offset_time_array)

      Computes number of time points for each event and read offset
      w.r.t. event's eegoffset :param ev: record representing single
      event :param samplerate: samplerate fo the time series :param
      offset_time_array: "offsets" axis of the DataArray returned by
      EEGReader. This is the axis that represents time axis but
      instead of beind dimensioned to seconds it simply represents
      position of a given data point in a series The time axis is
      constructed by dividint offsets axis by the samplerate :return:
      event's read chunk size {int}, read offset w.r.t. to event's
      eegoffset {}


ptsa.data.filters.MonopolarToBipolarMapper
==========================================

class ptsa.data.filters.MonopolarToBipolarMapper.MonopolarToBipolarMapper(**kwds)

   Bases: "ptsa.data.common.TypedUtils.PropertiedObject",
   "ptsa.data.filters.BaseFilter.BaseFilter"

   Object that takes as an input time series for monopolar electrodes
   and an array of bipolar pairs and outputs Time series where
   'channels' axis is replaced by 'bipolar_pairs' axis and the time
   series data is a difference between time series corresponding to
   different electrodes as specified by bipolar pairs

   bipolar_pairs = rec.array([],            dtype=[('ch0', 'S3'), ('ch1', 'S3')])

   filter()

      Turns time series for monopolar electrodes into time series
      where where 'channels' axis is replaced by 'bipolar_pairs' axis
      and the time series data is a difference between time series
      corresponding to different electrodes as specified by bipolar
      pairs

      Returns:
         TimeSeriesX object

   time_series = <xarray.TimeSeriesX (time: 1)> array([ 0.]) Coordinates:   * time     (time) int64 0

ptsa.data.filters.MonopolarToBipolarMapper.main_fcn()

ptsa.data.filters.MonopolarToBipolarMapper.new_fcn()


ptsa.data.filters.MorletWaveletFilter
=====================================


ptsa.data.filters.ResampleFilter
================================

class ptsa.data.filters.ResampleFilter.ResampleFilter(**kwds)

   Bases: "ptsa.data.common.TypedUtils.PropertiedObject",
   "ptsa.data.filters.BaseFilter.BaseFilter"

   Resample Filter

   filter()

      resamples time series :return:resampled time series with
      sampling frequency set to resamplerate
