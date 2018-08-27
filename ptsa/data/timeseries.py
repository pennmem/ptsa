from base64 import b64encode, b64decode
from io import BytesIO
import json
import time
import warnings

import xarray as xr
import numpy as np
from scipy.signal import resample

from ptsa import __version__ as ptsa_version
from ptsa.data.common import get_axis_index
from ptsa.filt import buttfilt


class ConcatenationError(Exception):
    """Raised when an error occurs while trying to concatenate incompatible
    :class:`TimeSeries` objects.

    """


class TimeSeries(xr.DataArray):
    """A thin wrapper around :class:`xr.DataArray` for dealing with time series
    data.

    Note that xarray internals prevent us from overriding the constructor which
    leads to some awkwardness: you must pass coords as a dict with a
    ``samplerate`` entry.

    Parameters
    ----------
    data : array-like
        Time series data
    coords : dict-like
        Coordinate arrays. This must contain at least a ``samplerate``
        coordinate.
    dims : array-like
        Dimension labels
    name : str
        Name of the time series
    attrs : dict
        Dictionary of arbitrary metadata
    encoding : dict
    fastpath : bool
        Not used, but required when subclassing :class:`xr.DataArray`.

    Raises
    ------
    AssertionError
        When ``samplerate`` is not present in ``coords``.

    See also
    --------
    xr.DataArray : Base class

    """
    def __init__(self, data, coords, dims=None, name=None,
                 attrs=None, encoding=None, fastpath=False):
        assert 'samplerate' in coords
        super(TimeSeries, self).__init__(data=data, coords=coords, dims=dims,
                                         name=name, attrs=attrs, encoding=encoding,
                                         fastpath=fastpath)

    @classmethod
    def create(cls, data, samplerate, coords=None, dims=None, name=None,
               attrs=None):
        """Factory function for creating a new timeseries object with passing
        the sample rate as a parameter. See :meth:`__init__` for parameters.

        """
        if coords is None:
            coords = {}
        if samplerate is not None:
            coords['samplerate'] = float(samplerate)
        return cls(data, coords=coords, dims=dims, name=name, attrs=attrs)

    def to_hdf(self, filename, mode='w'):
        """Save to disk using HDF5.

        Parameters
        ----------
        filename : str
            Full path to the HDF5 file
        mode : str
            File mode to use. See the :mod:`h5py` documentation for details.
            Default: ``'w'``

        Notes
        -----
        recarrays/DataFrame fields with "O" dtypes will be assumed to be strings
        and encoded accordingly.

        """
        try:  # pragma: nocover
            import h5py
        except ImportError:
            raise RuntimeError("You must install h5py to load from HDF5")

        with h5py.File(filename, mode) as hfile:
            hfile.create_dataset("data", data=self.data, chunks=True)

            dims = [dim.encode() for dim in self.dims]
            hfile.create_dataset("dims", data=dims)

            coords_group = hfile.create_group("coords")
            coords = []

            for name, data in self.coords.items():
                coords.append(name)
                buffer = BytesIO()
                np.save(buffer, data)
                output = b64encode(buffer.getvalue())
                coords_group.create_dataset(name, data=output)

            names = json.dumps(coords).encode()
            coords_group.attrs.update(names=names)

            root = hfile['/']

            if self.name is not None:
                root.attrs['name'] = self.name.encode()
            if self.attrs is not None:
                root.attrs['attrs'] = json.dumps(self.attrs).encode()

            root.attrs["created"] = time.time()
            root.attrs["ptsa_version"] = ptsa_version

    @staticmethod
    def _from_hdf_base64(hfile):
        """Load non-time series data from the legacy base64-encoded HDF5 format.

        Parameters
        ----------
        hfile : h5py.File
            Open HDF5 file.

        Returns
        -------
        name, dims, coords, names, attrs

        """
        from collections import namedtuple

        rtype = namedtuple("HDFBase64RType", "name,dims,coords,attrs")

        dims = hfile['dims'][:]
        root = hfile['/']

        coords_group = hfile['coords']
        names = json.loads(coords_group.attrs['names'].decode())
        coords = {}

        for name in names:
            buffer = BytesIO(b64decode(coords_group[name].value))
            coord = np.load(buffer)
            coords[name] = coord

        name = root.attrs.get('name', None)
        if name is not None:
            name = name.decode()

        attrs = root.attrs.get('attrs', None)
        if attrs is not None:
            attrs = json.loads(attrs.decode())

        dims = [dim.decode() for dim in dims]

        return rtype(name, dims, coords, attrs)

    @classmethod
    def from_hdf(cls, filename):
        """Load a serialized time series from an HDF5 file.

        Parameters
        ----------
        filename : str
            Path to HDF5 file.

        """
        try:  # pragma: nocover
            import h5py
        except ImportError:
            raise RuntimeError("You must install h5py to load from HDF5")

        with h5py.File(filename, 'r') as hfile:
            loaded = cls._from_hdf_base64(hfile)

            array = cls.create(hfile['data'].value,
                               None,
                               coords=loaded.coords,
                               dims=loaded.dims,
                               name=loaded.name,
                               attrs=loaded.attrs)

            return array

    def append(self, other, dim=None):
        """Append another :class:`TimeSeries` to this one.

        .. versionchanged:: 2.0

           Appending along a dimension not present will cause that
           dimension to be created.

        Parameters
        ----------
        other : TimeSeries
        dim : str or None
            Dimension to concatenate on. If None, attempt to concatenate all
            data using :func:`numpy.concatenate`. If not present, a new
            dimension will be created with coords [0,1].

        Returns
        -------
        Appended TimeSeries

        """
        if not self.dims == other.dims:
            raise ConcatenationError("Dimensions are not identical")

        dims = self.dims
        coords = dict()

        if dim is not None and dim not in dims:
            new_self = self.expand_dims(dim).assign_coords(**{dim:[0]})
            other = other.expand_dims(dim).assign_coords(**{dim:[1]})
            return new_self.append(other,dim=dim)

        for key in self.coords:
            if len(self[key].shape) == 0:
                if self[key].data != other[key].data:
                    raise ConcatenationError(
                        "coordinate {:s} differs\n".format(key) +
                        "self -> {!s}, other -> {!s}".format(self[key],
                                                             other[key])
                    )
                else:
                    coords[key] = self[key]
            elif dim is None:
                coords[key] = np.concatenate(
                    [self.coords[key], other.coords[key]])
            else:
                if key != dim:
                    if (self[key] != other[key]).all():
                        raise ConcatenationError("Dimension {:s} doesn't match".format(key))
                    coords[key] = self[key]
                else:
                    coords[key] = np.concatenate([self[key], other[key]])

        if dim is None:
            data = np.concatenate([self.data, other.data])
        else:
            axis = np.where(np.array(dims) == dim)[0][0]
            data = np.concatenate([self.data, other.data], axis=axis)

        attrs = self.attrs.copy()
        attrs.update(other.attrs)
        name = "{!s} appended with {!s}".format(self.name, other.name)

        new = TimeSeries.create(data, self.samplerate, coords=coords,
                                dims=dims, attrs=attrs, name=name)
        return new

    def __duration_to_samples(self, duration):
        """Convenience function to convert a duration in seconds to number of
        samples.

        """
        return int(np.ceil(float(self['samplerate']) * duration))

    def filter_with(self, filter_class, **kwargs):
        """Filter the time series data using the specified filter class.

        Parameters
        ----------
        filter_class : type
            The filter class to use.
        kwargs
            Keyword arguments to pass along to ``filter_class``.

        Returns
        -------
        filtered : TimeSeries
            The resulting data from the filter.

        Raises
        ------
        TypeError
            When ``filter_class`` is not a valid filter class.

        """
        from ptsa.data.filters.base import BaseFilter

        if not issubclass(filter_class, BaseFilter):
            raise TypeError("filter_class must be a child of BaseFilter")

        filtered = filter_class(self, **kwargs).filter()
        return filtered

    def filtered(self, freq_range, filt_type='stop', order=4):
        """
        Filter the data using a Butterworth filter and return a new
        TimeSeries instance.

        Parameters
        ----------
        freq_range : array-like
            The range of frequencies to filter.
        filt_type : str
            Filter type (default: ``'stop'``).
        order : int
            The order of the filter (default: 4).

        Returns
        -------
        ts : TimeSeries
            A TimeSeries instance with the filtered data.

        """
        warnings.warn("The filtered method is not very flexible. "
                      "Consider using filters in ptsa.data.filters instead.")
        time_axis_index = get_axis_index(self, axis_name='time')
        filtered_array = buttfilt(self.values, freq_range, float(self['samplerate']), filt_type,
                                  order, axis=time_axis_index)
        new_ts = self.copy()
        new_ts.data = filtered_array
        return new_ts

    def resampled(self, resampled_rate, window=None,
                  loop_axis=None, num_mp_procs=0, pad_to_pow2=False):
        """Resamples the time series.

        Parameters
        ----------
        resampled_rate : float
           New sample rate
        window
            ignored for now - added for legacy reasons
        loop_axis
            ignored for now - added for legacy reasons
        num_mp_procs
            ignored for now - added for legacy reasons
        pad_to_pow2
            ignored for now - added for legacy reasons

        Returns
        -------
        Resampled time series

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

            if coord_name == "samplerate":
                continue

            if coord_name == time_axis_name:
                coords[coord_name] = new_time_axis

        resampled_time_series = TimeSeries.create(
            resampled_array, resampled_rate, coords=coords, dims=[dim for dim in self.dims],
            name=self.name, attrs=self.attrs)

        return resampled_time_series

    def remove_buffer(self, duration):
        """
        Remove the desired buffer duration (in seconds) and reset the
        time range.

        Parameters
        ----------
        duration : float
            The duration to be removed. The units depend on the samplerate:
            E.g., if samplerate is specified in Hz (i.e., samples per second),
            the duration needs to be specified in seconds and if samplerate is
            specified in kHz (i.e., samples per millisecond), the duration needs
            to be specified in milliseconds. The specified duration is removed
            from the beginning and end.

        Returns
        -------
        ts : TimeSeries
            A TimeSeries instance with the requested durations removed from the
            beginning and/or end.
        """
        samples = self.__duration_to_samples(duration)

        if samples > len(self['time']):
            raise ValueError("Requested removal time is longer than the data")

        if samples > 0:
            return self[..., samples:-samples]

    def add_mirror_buffer(self, duration):
        """
        Adds mirrors data at both ends of the time series (up to specified
        length/duration) and appends such buffers at both ends of the series.
        The new series total time duration is:

            ``original duration + 2 * duration * samplerate``

        Parameters
        ----------
        duration : float
            Buffer duration in seconds.

        Returns
        -------
        New time series with added mirrored buffer.

        """
        samplerate = float(self['samplerate'])
        samples = self.__duration_to_samples(duration)
        if samples > len(self['time']):
            raise ValueError("Requested buffer time is longer than the data")

        data = self.data

        mirrored_data = np.concatenate(
            (data[..., 1:samples + 1][..., ::-1], data, data[..., -samples - 1:-1][..., ::-1]),
            axis=-1)

        start_time = self['time'].data[0] - duration
        t_axis = (np.arange(mirrored_data.shape[-1]) * (1.0 / samplerate)) + start_time
        # coords = [self.coords[dim_name] for dim_name in self.dims[:-1]] +[t_axis]
        coords = {dim_name:self.coords[dim_name] for dim_name in self.dims[:-1]}
        coords['time'] = t_axis
        coords['samplerate'] = float(self['samplerate'])

        return TimeSeries(mirrored_data, dims=self.dims, coords=coords)

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


class TimeSeriesX(TimeSeries):
    def __init__(self, data, coords, dims=None, name=None,
                 attrs=None, encoding=None, fastpath=False):
        with warnings.catch_warnings():
            warnings.simplefilter('always')
            warnings.warn("TimeSeriesX has been renamed TimeSeries",
                          DeprecationWarning)
            super(TimeSeriesX, self).__init__(data, coords, dims, name, attrs,
                                              encoding, fastpath)
