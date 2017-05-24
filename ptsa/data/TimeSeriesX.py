import xarray as xr
from xarray import concat

import numpy as np
from ptsa.data.common import get_axis_index
from scipy.signal import resample


class TimeSeriesX(xr.DataArray):
    """A thin wrapper around :class:`xr.DataArray` for dealing with time series
    data.

    Parameters
    ----------
    data : array-like
        Time series data
    coords : array-like
        Coordinate arrays
    dims : array-like
        Dimension labels
    name : str
        Name of the time series
    attrs : dict
        Dictionary of arbitrary metadata
    encoding : dict

    """
    def __init__(self, data, coords=None, dims=None, name=None, attrs=None,
                 encoding=None):
        super(TimeSeriesX, self).__init__(data=data, coords=coords, dims=dims,
                                          name=name, attrs=attrs,
                                          encoding=encoding)

    def filtered(self, freq_range, filt_type='stop', order=4):
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

        from ptsa.filt import buttfilt
        time_axis_index = get_axis_index(self, axis_name='time')
        filtered_array = buttfilt(self.values, freq_range, float(self['samplerate']), filt_type,
                                  order, axis=time_axis_index)


        coords={}


        for coord_name, coord in list(self.coords.items()):
            if len(coord.shape):
                coords[coord_name] = coord

        filtered_time_series = TimeSeriesX(
            filtered_array,
            dims=[dim_name for dim_name in self.dims],
            coords=coords
        )
        filtered_time_series['samplerate']=self['samplerate']

        filtered_time_series.attrs = self.attrs.copy()

        return filtered_time_series

    def resampled(self, resampled_rate, window=None,
                  loop_axis=None, num_mp_procs=0, pad_to_pow2=False):
        """

        :param resampled_rate: resample rate
        :param window: ignored for now - added for legacy reasons
        :param loop_axis: ignored for now - added for legacy reasons
        :param num_mp_procs: ignored for now - added for legacy reasons
        :param pad_to_pow2: ignored for now - added for legacy reasons
        :return: resampled time series

        """
        # use ResampleFilter instead
        # samplerate = self.attrs['samplerate']
        samplerate = float(self['samplerate'])

        time_axis = self['time']
        # time_axis_index = get_axis_index(self,axis_name='time')
        time_axis_index = self.get_axis_num('time')

        time_axis_length = np.squeeze(time_axis.shape)
        new_length = int(np.round(time_axis_length * resampled_rate / float(samplerate)))

        resampled_array, new_time_axis = resample(self.values,
                                                  new_length, t=time_axis.values,
                                                  axis=time_axis_index, window=window)

        # constructing axes
        coords = {}
        time_axis_name = self.dims[time_axis_index]
        for coord_name, coord in list(self.coords.items()):
            if len(coord.shape):
                coords[coord_name] = coord
            else:
                continue

            if coord_name == time_axis_name:
                coords[coord_name] = new_time_axis

        coords['samplerate'] = float(resampled_rate)

        resampled_time_series = TimeSeriesX(
            resampled_array,
            dims=[dim_name for dim_name in self.dims],
            coords=coords
        )

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

        # number_of_buffer_samples = int(np.ceil(duration * self.attrs['samplerate']))
        number_of_buffer_samples = int(np.ceil(duration * float(self['samplerate'])))
        if number_of_buffer_samples > 0:
            return self[..., number_of_buffer_samples:-number_of_buffer_samples]

    def add_mirror_buffer(self, duration):
        """
        Adds mirrors data at both ends of the time series (up to specified length/duration) and appends
        such buffers at both ends of the series. The new series total time duration is:
        original duration + 2*duration
        :param duration: {float} buffer duration in seconde
        :return: {TimeSeriesX} new time series with added mirrored buffer
        """
        samplerate = float(self['samplerate'])
        nb_ = int(np.ceil(samplerate * duration))

        data = self.data

        mirrored_data = np.concatenate(
            (data[..., 1:nb_ + 1][..., ::-1], data, data[..., -nb_ - 1:-1][..., ::-1]),
            axis=-1)

        start_time = self['time'].data[0] - duration
        t_axis = (np.arange(mirrored_data.shape[-1]) * (1.0 / samplerate)) + start_time
        # coords = [self.coords[dim_name] for dim_name in self.dims[:-1]] +[t_axis]
        coords = {dim_name:self.coords[dim_name] for dim_name in self.dims[:-1]}
        coords['time'] = t_axis
        coords['samplerate'] = float(self['samplerate'])



        return TimeSeriesX(mirrored_data, dims=self.dims, coords=coords)

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
