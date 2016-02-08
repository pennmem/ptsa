__author__ = 'm'

try:
    from xarray import __version__, DataArray, concat
except ImportError:
    from xray import __version__, DataArray, concat

import numpy as np
from ptsa.data.common import get_axis_index
from scipy.signal import resample

major_x_ver, minor_x_ver, build_x_ver = map(int, __version__.split('.'))


class TimeSeriesX(DataArray):
    def __init__(self, data,
                 coords=None,
                 dims=None,
                 name=None,
                 attrs=None,
                 encoding=None,
                 fastpath=False
                 ):

        if major_x_ver == 0 and minor_x_ver < 7:

            DataArray.__init__(self, data=data,
                               coords=coords,
                               dims=dims,
                               name=name,
                               attrs=attrs,
                               encoding=encoding,
                               # fastpath=fastpath
                               )
        else:
            DataArray.__init__(self, data=data,
                               coords=coords,
                               dims=dims,
                               name=name,
                               attrs=attrs,
                               encoding=encoding,
                               fastpath=fastpath
                               )

        # self.time_axis_index = get_axis_index(self,axis_name='time')
        # self._time_axis_index = None
        # tai = get_axis_index(self,axis_name='time')

        # self['time_axis_index'] = get_axis_index(self,axis_name='time')

        # self['time_axis_index']= get_axis_index(self,axis_name='time')
        print self.dims
        self['time_axis_index'] = -1
        # self['a'] = 10.0


        for i, dim_name in enumerate(self.dims):
            if dim_name == 'time':
                self['time_axis_index'] = i
                break


                # def __init__(self,**kwds):
                #     xray.DataArray.__init__(self,**kwds)
                # self.a=10
                # self.time_axis_index=get_axis_index(self,axis_name='time')

    # @property
    # def time_axis_index(self):
    #     if self._time_axis_index is not None:
    #         self._time_axis_index = get_axis_index(self,axis_name='time')
    #     return self._time_axis_index

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

        # filtered_array = buttfilt(self.values, freq_range, self.attrs['samplerate'], filt_type,
        #                                order,axis=time_axis_index)

        # filtered_time_series = xray.DataArray(
        #     filtered_array,
        #     coords = [xray.DataArray(coord.copy()) for coord_name, coord in self.coords.items() ]
        # )

        filtered_time_series = TimeSeriesX(
            filtered_array,
            dims=[dim_name for dim_name in self.dims],
            coords={coord_name: DataArray(coord.copy()) for coord_name, coord in self.coords.items()}
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

        # use ResampleFilter instead
        # samplerate = self.attrs['samplerate']
        samplerate = float(self['samplerate'])

        time_axis = self['time']
        # time_axis_index = get_axis_index(self,axis_name='time')
        time_axis_index = self['time_axis_index'].data
        time_axis_length = np.squeeze(time_axis.shape)
        new_length = int(np.round(time_axis_length * resampled_rate / float(samplerate)))

        # print new_length

        # if self.time_axis_index<0:
        #     self.time_axis_index = get_axis_index(data_array=self, axis_name='time')

        # time_axis = self.coords[ self.dims[self.time_axis_index] ]

        # time_axis = self['time']

        resampled_array, new_time_axis = resample(self.values,
                                                  new_length, t=time_axis.values,
                                                  axis=time_axis_index, window=window)

        # print new_time_axis

        # constructing axes
        coords = []
        for i, dim_name in enumerate(self.dims):
            if i != time_axis_index:
                coords.append(self.coords[dim_name].copy())
            else:
                coords.append((dim_name, new_time_axis))

        resampled_time_series = DataArray(resampled_array, coords=coords)
        resampled_time_series['samplerate'] = resampled_rate
        # resampled_time_series.attrs['samplerate'] = resampled_rate

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
        coords = [self.coords[dim_name] for dim_name in self.dims[:-1]] +[t_axis]

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


if __name__ == '__main__':
    # ts = xray.DataArray(data=np.arange(20).reshape(4,5),dims=['channels','time'])
    ts = TimeSeriesX(data=np.arange(20).reshape(4, 5), dims=['channels', 'time'])
    ts2 = TimeSeriesX(data=np.arange(20).reshape(4, 5), dims=['channels', 'time'])

    print ts + ts2
