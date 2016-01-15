__author__ = 'm'


import numpy as np
import xray
from ptsa.data.common import TypeValTuple, PropertiedObject, get_axis_index
from scipy.signal import resample

from ptsa.wavelet import phase_pow_multi


class WaveletFilter(PropertiedObject):
    _descriptors = [
        TypeValTuple('freqs', np.ndarray, np.array([],dtype=np.float)),
        TypeValTuple('time_axis_index', int, -1),
        TypeValTuple('bipolar_pairs', np.recarray, np.recarray((0,),dtype=[('ch0', '|S3'),('ch1', '|S3')])),
        TypeValTuple('resamplerate',float,-1)

    ]


    def __init__(self,time_series, **kwds):

        self.window = None
        self.time_series = time_series

        for option_name, val in kwds.items():

            try:
                attr = getattr(self,option_name)
                setattr(self,option_name,val)
            except AttributeError:
                print 'Option: '+ option_name+' is not allowed'


    def filter(self):

        from ptsa.data.filters.ResampleFilter import ResampleFilter

        rs_time_axis = None # resampled time axis
        if self.resamplerate > 0:

            rs_time_filter = ResampleFilter (resamplerate=self.resamplerate)
            rs_time_filter.set_input(self.time_series[0,0,:])
            time_series_resampled = rs_time_filter.filter()
            rs_time_axis = time_series_resampled ['time']
        else:
            rs_time_axis  = self.time_series['time']


        pow_array = xray.DataArray(
            np.empty(
            shape=(self.bipolar_pairs.shape[0],self.time_series['events'].shape[0],self.freqs.shape[0],rs_time_axis.shape[0]),
            dtype=np.float64),
            dims=['bipolar_pair','events','frequency','time']
        )


        # pow_array = xray.DataArray(
        #     np.empty(
        #     shape=(self.bipolar_pairs.shape[0],self.time_series['events'].shape[0],self.freqs.shape[0],self.time_series['time'].shape[0]),
        #     dtype=np.float64),
        #     dims=['bipolar_pair','events','frequency','time']
        # )




        # rand_array = np.random.rand(self.bipolar_pairs.shape[0],self.time_series['events'].shape[0],self.freqs.shape[0],self.time_series['time'].shape[0])


        # pow_array = xray.DataArray(
        #     rand_array,
        #     dims=['bipolar_pair','event','frequency','time']
        # )


        # depending on the reader channel axis may be a rec array or a simple array
        # we are interested in an array that has channel labels
        time_series_channel_axis = self.time_series['channels'].data
        try:
            time_series_channel_axis = time_series_channel_axis['name']
        except (KeyError,IndexError):
            pass

        samplerate = self.time_series.attrs['samplerate']

        for e, ev in enumerate(self.time_series['events']):
            for b, bp_pair in enumerate(self.bipolar_pairs):

                print 'bp_pair=',bp_pair, ' event num = ',e

                ch0 = self.time_series.isel(channels=(time_series_channel_axis == bp_pair['ch0']), events=e).values
                ch1 = self.time_series.isel(channels=(time_series_channel_axis == bp_pair['ch1']), events=e).values

                # ch0 = self.time_series.isel(channels=(time_series_channel_axis == bp_pair['ch0'])).values
                # ch1 = self.time_series.isel(channels=(time_series_channel_axis == bp_pair['ch1'])).values

                # ch0 = self.time_series.isel(channels=(self.time_series['channels']==bp_pair['ch0'])).values
                # ch1 = self.time_series.isel(channels=(self.time_series['channels']==bp_pair['ch1'])).values


                bp_data = ch0-ch1
                # import time
                # time.sleep(0.5)

                bp_data_wavelet = phase_pow_multi(self.freqs, bp_data, to_return='power', samplerates=samplerate)

                bp_data_wavelet = np.squeeze(bp_data_wavelet)

                if self.resamplerate>0.0:
                    bp_data_wavelet = resample(bp_data_wavelet, num=rs_time_axis.shape[0], axis=1)
                # print bp_data_wavelet
                #



                pow_array[b,e] = bp_data_wavelet
                # pow_array[b,e,:,:] = np.squeeze(bp_data_wavelet)[:,:]
                # pow_array[b,e,:,:] = -1.0
                # if b == 2:
                #     break
        #assigning axes
        pow_array['frequency'] = self.freqs
        pow_array['bipolar_pair'] = self.bipolar_pairs
        pow_array['time'] = rs_time_axis

        pow_array.attrs['samplerate'] = samplerate

        if self.resamplerate>0:
            pow_array.attrs['samplerate'] = self.resamplerate



        return pow_array


def test_1():

    import time
    start = time.time()

    e_path = '/Users/m/data/events/RAM_FR1/R1060M_events.mat'

    from ptsa.data.readers import BaseEventReader

    base_e_reader = BaseEventReader(event_file=e_path, eliminate_events_with_no_eeg=True, use_ptsa_events_class=False)

    base_e_reader.read()

    base_events = base_e_reader.get_output()

    base_events = base_events[base_events.type == 'WORD']

    # selecting only one session
    base_events = base_events[base_events.eegfile == base_events[0].eegfile]



    from ptsa.data.readers.TalReader import TalReader
    tal_path = '/Users/m/data/eeg/R1060M/tal/R1060M_talLocs_database_bipol.mat'
    tal_reader = TalReader(tal_filename=tal_path)
    monopolar_channels = tal_reader.get_monopolar_channels()
    bipolar_pairs = tal_reader.get_bipolar_pairs()

    print 'bipolar_pairs=',bipolar_pairs



    from ptsa.data.readers.TimeSeriesSessionEEGReader import TimeSeriesSessionEEGReader

    # time_series_reader = TimeSeriesSessionEEGReader(events=base_events, channels = ['002', '003', '004', '005'])
    time_series_reader = TimeSeriesSessionEEGReader(events=base_events, channels=monopolar_channels)
    ts_dict = time_series_reader.read()

    first_session_data =  ts_dict.items()[0][1]

    print first_session_data


    wf = WaveletFilter(time_series=first_session_data,
                       bipolar_pairs=bipolar_pairs[0:3],
                       freqs=np.logspace(np.log10(3), np.log10(180), 12),
                       # resamplerate=50.0
                       )

    pow_wavelet = wf.filter()


    from ptsa.data.filters.EventDataChopper import EventDataChopper
    edcw = EventDataChopper(events=base_events, event_duration=1.6, buffer=1.0,
                                    data_dict={base_events[0].eegfile:pow_wavelet})

    chopped_wavelets = edcw.filter()


    print 'total time = ',time.time()-start


    return chopped_wavelets

def test_2():


    import time
    start = time.time()

    e_path = '/Users/m/data/events/RAM_FR1/R1060M_events.mat'

    from ptsa.data.readers import BaseEventReader

    base_e_reader = BaseEventReader(event_file=e_path, eliminate_events_with_no_eeg=True, use_ptsa_events_class=False)

    base_e_reader.read()

    base_events = base_e_reader.get_output()

    base_events = base_events[base_events.type == 'WORD']

    # selecting only one session
    base_events = base_events[base_events.eegfile == base_events[0].eegfile]



    from ptsa.data.readers.TalReader import TalReader
    tal_path = '/Users/m/data/eeg/R1060M/tal/R1060M_talLocs_database_bipol.mat'
    tal_reader = TalReader(tal_filename=tal_path)
    monopolar_channels = tal_reader.get_monopolar_channels()
    bipolar_pairs = tal_reader.get_bipolar_pairs()

    print 'bipolar_pairs=',bipolar_pairs



    from ptsa.data.readers.TimeSeriesEEGReader import TimeSeriesEEGReader

    time_series_reader = TimeSeriesEEGReader(events=base_events, start_time=0.0,
                                             end_time=1.6, buffer_time=1.0, keep_buffer=True)

    base_eegs = time_series_reader.read(channels=monopolar_channels)







    wf = WaveletFilter(time_series=base_eegs,
                       bipolar_pairs=bipolar_pairs[0:3],
                       freqs=np.logspace(np.log10(3), np.log10(180), 12),
                       # resamplerate=50.0
                       )

    pow_wavelet = wf.filter()




    print 'total time = ',time.time()-start

    return pow_wavelet

if __name__=='__main__':
    edcw = test_1()
    pow_wavelet = test_2()
    print