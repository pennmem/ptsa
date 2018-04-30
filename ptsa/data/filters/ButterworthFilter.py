from numpy import asarray
from xarray import DataArray
from ptsa.data.timeseries import TimeSeries
from ptsa.data.common import get_axis_index
from ptsa.data.filters import BaseFilter
import traits.api
from scipy.signal import butter, filtfilt

class ButterworthFilter(BaseFilter):
    """Applies Butterworth filter to a time series.

    Keyword Arguments
    -----------------

    time_series
         TimeSeries object
    order
         Butterworth filter order
    freq_range: list-like
       Array [min_freq, max_freq] describing the filter range

    """
    order=traits.api.Int
    freq_range = traits.api.List(maxlen=2)
    filt_type=traits.api.Str


    def __init__(self, time_series,freq_range,order=4,filt_type='stop'):
        super(ButterworthFilter, self).__init__(time_series)

        self.freq_range = freq_range
        self.order = order
        self.filt_type = filt_type

    def filter(self):
        """
        Applies Butterwoth filter to input time series and returns filtered TimeSeriesX object

        Returns
        -------
        filtered: TimeSeries
            The filtered time series

        """
        time_axis_index = get_axis_index(self.time_series, axis_name='time')
        filtered_array = buttfilt(self.time_series,
                                  self.freq_range, float(self.time_series['samplerate']), self.filt_type,
                                  self.order, axis=time_axis_index)

        coords_dict = {coord_name: DataArray(coord.copy()) for coord_name, coord in list(self.time_series.coords.items())}
        coords_dict['samplerate'] = self.time_series['samplerate']
        dims = [dim_name for dim_name in self.time_series.dims]
        filtered_time_series = TimeSeries(
            filtered_array,
            dims=dims,
            coords=coords_dict
        )

        # filtered_time_series = TimeSeries(filtered_time_series)
        filtered_time_series.attrs = self.time_series.attrs.copy()
        return filtered_time_series


def buttfilt(dat,freq_range,sample_rate,filt_type,order,axis=-1):
    """Wrapper for a Butterworth filter.

    """

    # make sure dat is an array
    dat = asarray(dat)

    # reshape the data to 2D with time on the 2nd dimension
    #origshape = dat.shape
    #dat = reshape_to_2d(dat,axis)

    # set up the filter
    freq_range = asarray(freq_range)

    # Nyquist frequency
    nyq=sample_rate/2.

    # generate the butterworth filter coefficients
    [b,a]=butter(order,freq_range/nyq,filt_type)

    # loop over final dimension
    #for i in range(dat.shape[0]):
    #    dat[i] = filtfilt(b,a,dat[i])
    #dat = filtfilt2(b,a,dat,axis=axis)
    dat = filtfilt(b,a,dat,axis=axis)

    # reshape the data back
    #dat = reshape_from_2d(dat,axis,origshape)
    return dat

if __name__ == '__main__':
    import numpy as np
    from numpy.testing import *
    from ptsa.data.readers import BaseEventReader
    from ptsa.data.filters.morlet import MorletWaveletFilter
    from ptsa.data.filters.ButterworthFilter import ButterworthFilter
    from ptsa.data.readers.tal import TalReader
    from ptsa.data.readers import EEGReader
    from ptsa.data.readers import PTSAEventReader
    from ptsa.data.events import Events

    e_path = '/Volumes/rhino_root/data/events/RAM_PS/R1108J_1_events.mat'
    e_path = '/Volumes/rhino_root/data/events/RAM_PS/R1108J_1_events.mat'
    # e_path ='/Users/m/data/events/RAM_FR1/R1056M_events.mat'

    e_reader = BaseEventReader(filename=e_path, eliminate_events_with_no_eeg=True)


    events = e_reader.read()

    from ptsa.data.readers.tal import TalReader

    tal_path = '/Volumes/rhino_root/data/eeg/R1108J_1/tal/R1108J_1_talLocs_database_bipol.mat'
    tal_reader = TalReader(filename=tal_path)
    monopolar_channels = tal_reader.get_monopolar_channels()
    bipolar_pairs = tal_reader.get_bipolar_pairs()

    # ---------------- NEW STYLE PTSA -------------------
    base_e_reader = BaseEventReader(filename=e_path, eliminate_events_with_no_eeg=True)

    base_events = base_e_reader.read()

    base_events = base_events[(base_events.type == 'STIMULATING') ]
    base_events = base_events[base_events.session == 2]


    from ptsa.data.readers.EEGReader import EEGReader
    eeg_reader = EEGReader(events=base_events, channels=monopolar_channels[0:3],
                           start_time=-1.1, end_time=-0.1, buffer_time=1.0)

    base_eegs = eeg_reader.read()

    bw_base_eegs = base_eegs.filtered(freq_range=[58.,62.], filt_type='stop', order=4)


    b, a = butter_bandpass(58.,62.,float(base_eegs['samplerate']), 4)
    y_in = base_eegs[0,0,:].data


    y_out = butter_bandpass_filter(y_in, 58.,62.,float(base_eegs['samplerate']), 4)


    import matplotlib;
    matplotlib.use('Qt4Agg')


    import matplotlib.pyplot as plt
    plt.get_current_fig_manager().window.raise_()


    # plt.plot(np.arange(y_in.shape[0]),y_in,'k')
    plt.plot(np.arange(y_out.shape[0]),y_out,'r--')


    plt.plot(np.arange(bw_base_eegs[0,0,:].shape[0]),bw_base_eegs[0,0,:],'b--')




    plt.show()

    print()


