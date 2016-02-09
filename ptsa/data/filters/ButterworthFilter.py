__author__ = 'm'

from ptsa.data.common.xr import DataArray
from ptsa.data.common import TypeValTuple, PropertiedObject
from ptsa.data.TimeSeriesX import TimeSeriesX
from ptsa.data.common import get_axis_index


class ButterworthFilter(PropertiedObject):
    '''
    Applies Butterworth filter to a time series
    '''
    _descriptors = [
        TypeValTuple('time_series', TimeSeriesX, TimeSeriesX([0.0], dims=['time'])),
        TypeValTuple('order', int, 4),
        TypeValTuple('freq_range', list, [58, 62]),
        TypeValTuple('filt_type', str, 'stop'),
    ]

    def __init__(self, **kwds):
        '''
        Constructor
        :param kwds:allowed values are:
        -------------------------------------
        :param time_series  -  TimeSeriesX object
        :param order -  Butterworth filter order
        :param freq_range -  array of frequencies [min_freq, max_freq] to filter out
        :return: None
        '''
        self.init_attrs(kwds)

    def filter(self):
        '''
        Applies Butterwoth filter to input time series and returns filtered TimeSeriesX object
        :return: TimeSeriesX object
        '''

        from ptsa.filt import buttfilt

        time_axis_index = get_axis_index(self.time_series, axis_name='time')
        filtered_array = buttfilt(self.time_series,
                                  self.freq_range, float(self.time_series['samplerate']), self.filt_type,
                                  self.order, axis=time_axis_index)

        coords_dict = {coord_name: DataArray(coord.copy()) for coord_name, coord in self.time_series.coords.items()}
        coords_dict['samplerate'] = self.time_series['samplerate']
        dims = [dim_name for dim_name in self.time_series.dims]
        filtered_time_series = TimeSeriesX(
            filtered_array,
            dims=dims,
            coords=coords_dict
        )

        # filtered_time_series.attrs['samplerate'] = self.time_series.attrs['samplerate']
        # filtered_time_series.attrs['samplerate'] = self.time_series['samplerate']
        filtered_time_series = TimeSeriesX(filtered_time_series)

        return filtered_time_series



from scipy.signal import butter, lfilter


def butter_bandpass(lowcut, highcut, fs, order=4):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    # b, a = butter(order, [low, high], btype='band')
    b, a = butter(order, [low, high], btype='stop')
    return b, a


def butter_bandpass_filter(data, lowcut, highcut, fs, order=4):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = lfilter(b, a, data)
    return y


if __name__ == '__main__':
    import numpy as np
    from numpy.testing import *
    from ptsa.data.readers import BaseEventReader
    from ptsa.data.filters.MorletWaveletFilter import MorletWaveletFilter
    from ptsa.data.filters.ButterworthFilter import ButterworthFilter
    from ptsa.data.readers.TalReader import TalReader
    from ptsa.data.readers import EEGReader
    from ptsa.data.readers import PTSAEventReader
    from ptsa.data.events import Events

    e_path = '/Volumes/rhino_root/data/events/RAM_PS/R1108J_1_events.mat'
    e_path = '/Volumes/rhino_root/data/events/RAM_PS/R1108J_1_events.mat'
    # e_path ='/Users/m/data/events/RAM_FR1/R1056M_events.mat'

    e_reader = BaseEventReader(filename=e_path, eliminate_events_with_no_eeg=True)


    events = e_reader.read()

    from ptsa.data.readers.TalReader import TalReader

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

    print