import numpy as np
import traits.api

from ptsa.data.timeseries import TimeSeries
from ptsa.data.filters import BaseFilter


class MonopolarToBipolarMapper(BaseFilter):
    """Object that takes as an input time series for monopolar electrodes
    and an array of bipolar pairs and outputs a TimeSeries object
    where the data is a difference between time series corresponding
    to different electrodes as specified by bipolar pairs.

    Parameters
    ----------
    timeseries: TimeSeries
        The time series to filter
    bipolar_pairs: array-like
        An array of bipolar electrode pairs. Must be either a 1-D
        structured array where dtypes has two fields corresponding to
        chan_names or a 2-D container where the first dimension must
        be length 2 corresponding to the two channels in the bipolar
        pair

    Keyword Arguments
    -----------------
    channels_dim: str, optional
        Name of the channels dimension
    chan_names: container, optional
        container with two elements corresponding to the names of the
        two channels in the bipolar pair

    .. versionchanged:: 2.0

        Parameter "time_series" was renamed to "timeseries".
        Support for 2-D bipolar_pairs and specification of channels_dim
        and chan_names was added in version 2.0.

    """
    bipolar_pairs = traits.api.Array()
    channels_dim = traits.api.String()
    chan_names = traits.api.ListStr()

    def __init__(self, bipolar_pairs, channels_dim="channels",
                 chan_names=["ch0", "ch1"]):
        super().__init__()

        if len(np.shape(bipolar_pairs)) == 2:
            if np.shape(bipolar_pairs)[0] == 2:
                self.bipolar_pairs = np.core.records.fromarrays(
                    bipolar_pairs, names=chan_names)
            else:
                raise ValueError(
                    'bipolar_pair must be either a 1-D structured array where'
                    'dtypes has two fields corresponding to chan_names or a 2-D'
                    'container where the first dimension must be length 2'
                    'corresponding to the two channels in the bipolar pair.'
                    'Input was 2-D with the following dimensions: ' +
                    str(np.shape(bipolar_pairs)))
        else:
            self.bipolar_pairs = bipolar_pairs
        self.channels_dim = channels_dim
        self.chan_names = chan_names

    def filter(self, timeseries):
        """Apply the constructed filter.

        Returns
        -------
        A TimeSeries object.

        """
        channel_axis = timeseries[self.channels_dim]

        ch0 = self.bipolar_pairs[self.chan_names[0]]
        ch1 = self.bipolar_pairs[self.chan_names[1]]

        sel0 = channel_axis.loc[ch0]
        sel1 = channel_axis.loc[ch1]

        ts0 = timeseries.loc[{self.channels_dim: sel0}]
        ts1 = timeseries.loc[{self.channels_dim: sel1}]

        dims_bp = list(timeseries.dims)

        coords_bp = {
            coord_name: coord
            for coord_name, coord in list(timeseries.coords.items())
        }
        coords_bp[self.channels_dim] = self.bipolar_pairs

        ts = TimeSeries(data=ts0.values - ts1.values, dims=dims_bp,
                        coords=coords_bp)
        ts['samplerate'] = timeseries['samplerate']

        ts.attrs = timeseries.attrs.copy()
        ts.name = timeseries.name
        return ts
