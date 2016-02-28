
# coding: utf-8

# In[1]:

import sys
sys.path.append('/Users/m/PTSA_NEW_GIT/')
import numpy as np
from numpy.testing import *
from ptsa.data.readers import BaseEventReader
from ptsa.data.filters.MorletWaveletFilter import MorletWaveletFilter
from ptsa.data.readers.TalReader import TalReader
from ptsa.data.readers import EEGReader
from ptsa.data.filters import MonopolarToBipolarMapper
from ptsa.data.filters import DataChopper
from ptsa.data.TimeSeriesX import TimeSeriesX
from ptsa.data.common import xr
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, roc_curve
from scipy.stats.mstats import zscore
import numpy.testing as npt
import cPickle
import os
from scipy.stats import describe
from collections import namedtuple
from collections import OrderedDict
from time import time

# ------------ SETTING UP MATPLOTLIB
get_ipython().magic(u'matplotlib inline')

import matplotlib
import numpy as np
import matplotlib.pyplot as plt


# When runing first time set compute_classifier_flag to True. Subsequent run can be executed with flag set to False because classifier will be computed and stored on the hard drive at that time. use_session_chopper_for_wavelets flag will cause that wavelets will be computted for the entire session and then chopped into segments correcponding to events

# In[2]:

# -------------- INITIAL SETUP
subject = 'R1111M'
compute_classifier_flag = True
use_session_chopper_for_wavelets = False

start_time=0.0
end_time=1.6
buffer_time=1.0
freqs=np.logspace(np.log10(3), np.log10(180), 8)


e_path = os.path.join('/Users/m/data/events/RAM_FR1/', subject + '_events.mat')

tal_path = os.path.join('/Users/m/data/eeg', subject, 'tal', subject + '_talLocs_database_bipol.mat')

ClassifierData = namedtuple('ClassifierData', ['lr_classifier', 'z_score_dict', 'features', 'recalls'])
ZScoreParams = namedtuple('ZScoreParams', ['mean', 'std'])



# In[3]:

def get_monopolar_and_bipolar_electrodes():
    tal_reader = TalReader(filename=tal_path)
    monopolar_channels = tal_reader.get_monopolar_channels()
    bipolar_pairs = tal_reader.get_bipolar_pairs()
    return monopolar_channels, bipolar_pairs

def get_events():
    # ---------------- NEW STYLE PTSA -------------------
    base_e_reader = BaseEventReader(filename=e_path, eliminate_events_with_no_eeg=True)

    base_events = base_e_reader.read()

    base_events = base_events[base_events.type == 'WORD']
    return base_events

def get_bp_data(evs):
    eeg_reader = EEGReader(events=evs, channels=monopolar_channels,
                           start_time=start_time, end_time=end_time, buffer_time=buffer_time)

    base_eegs = eeg_reader.read()

    m2b = MonopolarToBipolarMapper(time_series=base_eegs, bipolar_pairs=bipolar_pairs)
    bp_eegs = m2b.filter()
    return bp_eegs

def compute_wavelets(evs):
    bp_eegs = get_bp_data(evs)
    wf = MorletWaveletFilter(time_series=bp_eegs,
                             freqs=freqs,
                             output='power',
                             frequency_dim_pos=0,
                             verbose=True
                             )
    pow_wavelet, phase_wavelet = wf.filter()
    pow_wavelet = pow_wavelet.remove_buffer(duration=buffer_time)
    return pow_wavelet

def chop_time_series(time_series, start_offsets):
    dc = DataChopper(start_offsets=start_offsets, session_data=time_series, start_time=start_time, end_time=end_time)
    chopped_time_series = dc.filter()
    return chopped_time_series


def compute_continuous_wavelets(dataroot):
    session_reader = EEGReader(session_dataroot=dataroot, channels=monopolar_channels)
    session_eegs = session_reader.read()

    m2b = MonopolarToBipolarMapper(time_series=session_eegs, bipolar_pairs=bipolar_pairs)
    session_bp_eegs = m2b.filter()

    wf = MorletWaveletFilter(time_series=session_bp_eegs,
                             freqs=np.logspace(np.log10(3), np.log10(180), 8),
                             output='power',
                             frequency_dim_pos=0,
                             verbose=True
                             )

    pow_wavelet_session, phase_wavelet_session = wf.filter()
    return pow_wavelet_session

def compute_event_wavelets_from_session_wavelets(evs):
    s = time()
    session = evs[0].session
    dataroot = base_events[base_events.session == session][0].eegfile

    session_wavelet = compute_continuous_wavelets(dataroot=dataroot)

    session_wavelet_chopped = chop_time_series(time_series=session_wavelet, start_offsets=evs.eegoffset)
    session_wavelet_chopped = session_wavelet_chopped.rename({'start_offsets': 'events'})

    return session_wavelet_chopped

def compute_zscored_features(log_pow_wavelet):
    transposed_log_pow_wavelet = log_pow_wavelet.transpose('events', "bipolar_pairs", "frequency", "time")
    mean_powers_nd = np.nanmean(transposed_log_pow_wavelet.data, axis=-1)
    mean_powers_rs = mean_powers_nd.reshape(mean_powers_nd.shape[0], -1)
    m = np.mean(mean_powers_rs, axis=0)
    s = np.std(mean_powers_rs, axis=0, ddof=1)
    z_score_mean_powers = (mean_powers_rs - m) / s
    
    return z_score_mean_powers, m, s

def compute_features_recalls_normalization_params(session_list, use_session_chopper_for_wavelets=False):
    z_score_params_dict = OrderedDict()

    sessions_mask = np.zeros(base_events.shape[0], dtype=np.bool)
    for session in session_list:
        sessions_mask = sessions_mask | (base_events.session == session)

    sessions_evs = base_events[sessions_mask]


    if use_session_chopper_for_wavelets:
        pow_wavelet_list = []
        for session in session_list:
            session_mask = sessions_evs.session == session
            single_session_evs = sessions_evs[session_mask]
            pow_wavelet = compute_event_wavelets_from_session_wavelets(single_session_evs)
            pow_wavelet_list.append(pow_wavelet)

        pow_wavelet = xr.concat(pow_wavelet_list,dim='events')

    else:
        pow_wavelet = compute_wavelets(sessions_evs)
        # pow_wavelet = pow_wavelet.remove_buffer(duration=1.0)
        
    # -------------- TAKING LOG10    
    np.log10(pow_wavelet.data, out=pow_wavelet.data);

    features_list = []
    recalls_list = []
    for session in session_list:
        session_mask = sessions_evs.session == session
        single_session_evs = sessions_evs[session_mask]
        log_session_wavelet = pow_wavelet[:, :, session_mask, :]

#         mean, std = compute_zscoring_params(log_pow_wavelet=log_session_wavelet)
#         # session_zscore_mean_powers has two axes - 1 ->events , 2->bp x freq
#         session_zscore_mean_powers = compute_features_using_zscoring_params(log_session_wavelet, mean, std)
        
        session_zscore_mean_powers, mean, std = compute_zscored_features(log_pow_wavelet=log_session_wavelet)
        
        
        
        recalls_list.append(single_session_evs.recalled.astype(np.int))
        features_list.append(session_zscore_mean_powers)

        z_score_params_dict[session] = ZScoreParams(mean=mean, std=std)  # packaging int namedtuple for saving
    features = np.concatenate(features_list, axis=0)
    recalls = np.concatenate(recalls_list, axis=0)

    return features, recalls, z_score_params_dict

def compute_features_using_zscoring_params(pow_wavelet, mean, std):
    transposed_log_pow_wavelet = pow_wavelet.transpose('events', "bipolar_pairs", "frequency", "time")

    mean_powers_nd = np.nanmean(transposed_log_pow_wavelet.data, axis=-1)

    mean_powers_rs = mean_powers_nd.reshape(mean_powers_nd.shape[0], -1)
    mean_powers_rs.shape

    z_score_mean_powers = (mean_powers_rs - mean) / std

    return z_score_mean_powers

def compute_classifier(session_list, use_session_chopper_for_wavelets=False):
    features, recalls, z_score_params_dict = compute_features_recalls_normalization_params(
        session_list=session_list,
        use_session_chopper_for_wavelets=use_session_chopper_for_wavelets
    )

    lr_classifier = train_classifier(features, recalls)

    recall_prob_array = lr_classifier.predict_proba(features)[:, 1]
    auc = roc_auc_score(recalls, recall_prob_array)
    print 'auc=', auc

    classifier_data = ClassifierData(lr_classifier=lr_classifier, z_score_dict=z_score_params_dict, features=features,
                                     recalls=recalls)
    return classifier_data

def train_classifier(features, recalls):
    lr_classifier = LogisticRegression(C=7.2e-4, penalty='l2', class_weight='auto', solver='liblinear')
    lr_classifier.fit(features, recalls)
    return lr_classifier



# This function will tak as an input the following:
# 1. wavelets computed for the entire session
# 2. ClassifierData tuple - containing trained classifier, mean and std dev for z scoring
# 3. start_time (in seconds) - determines the time location of the epoch at which we being computting probs tgime series
# 4. end_time (in seconds) - determines the last epoch of thr probs time series
# 5. resolution - separation of the time points (in seconds) at which we calculate recall probabilities
# 5. slice_size - determines  the number of choping operations DataChopper performs  - since Data Chopper returns eeg time series using smaller slice_size has less strain on memory. in principle call Data Chopper only once but if the number of chops is large we might run out of memory...
# 

# In[4]:

def compute_probs_ts(pow_wavelet_session, classifier_data, start_time=10.0, end_time=20.0, slice_size=10,
                     resolution=0.1, session_num=0):
    lr_classifier = classifier_data.lr_classifier
    z_score_dict = classifier_data.z_score_dict

    mean = z_score_dict[session_num].mean
    std = z_score_dict[session_num].std

    # resolution is in seconds
    samplerate = float(pow_wavelet_session['samplerate'])

    number_of_samples_in_resolution = int(round(resolution * samplerate))

    total_number_of_items = int(round((end_time - start_time) / resolution))

    number_of_compute_iterations = total_number_of_items / slice_size

    probs_list = []

    for n in xrange(number_of_compute_iterations):
        st = start_time + n * slice_size * resolution
        initial_offset = int(round(st * samplerate))
        start_offsets = initial_offset + np.arange(slice_size) * number_of_samples_in_resolution

        pow_wavelet_chopped = chop_time_series(time_series=pow_wavelet_session, start_offsets=start_offsets)
        pow_wavelet_chopped = pow_wavelet_chopped.rename({'start_offsets': 'events'})
        np.log10(pow_wavelet_chopped.data, out=pow_wavelet_chopped.data)

        features = compute_features_using_zscoring_params(pow_wavelet_chopped, mean, std)
        probs = lr_classifier.predict_proba(features)[:, 1]

        probs_list.append(probs)

    probs_array = np.hstack(probs_list)
    time_axis = start_time + np.arange(probs_array.shape[0]) * resolution
    return time_axis, probs_array



# Begining of the computational pipeline that computes classifiers
# 

# In[5]:

base_events = get_events()
monopolar_channels, bipolar_pairs = get_monopolar_and_bipolar_electrodes()


# In[6]:

if compute_classifier_flag:
    training_sesssions = [0, 1]
    use_session_chopper = True

    classifier_data = compute_classifier(
        session_list=training_sesssions,
        use_session_chopper_for_wavelets=use_session_chopper_for_wavelets
    )
    # save the classifier
    with open('new_classifier_data_' + subject + '.pkl', 'wb') as fid:
        cPickle.dump(classifier_data, fid)

    training_classifier = classifier_data.lr_classifier

    validation_sesssions = [2]
    validation_classifier_data =     compute_classifier(
        session_list=validation_sesssions,
        use_session_chopper_for_wavelets=use_session_chopper_for_wavelets
    )

    validation_features = validation_classifier_data.features
    validation_recalls = validation_classifier_data.recalls

    validation_recall_prob_array = training_classifier.predict_proba(validation_features)[:, 1]
    auc = roc_auc_score(validation_recalls, validation_recall_prob_array)
    print 'validation auc=', auc

# we read classifier from the disk

with open('new_classifier_data_' + subject + '.pkl', 'rb') as fid:
    classifier_data = cPickle.load(fid)

lr_classifier = classifier_data.lr_classifier
z_score_dict = classifier_data.z_score_dict


# Here we will compute classifier time series. We begin by computing continuous wavelets for the session

# In[7]:

session = 0
dataroot = base_events[base_events.session == session][0].eegfile

pow_wavelet_session = compute_continuous_wavelets(dataroot=dataroot)


# In[8]:

time_axis, classifier_array = compute_probs_ts(pow_wavelet_session,
                                          classifier_data,
                                          start_time=50.0,
                                          end_time=70.0,
                                          slice_size=10,
                                          resolution=0.1
                                          )


# In[9]:

plt.plot(time_axis, classifier_array)
# plt.savefig('classifier_time_series.png')


# In[10]:

if use_session_chopper_for_wavelets:
    label='chopped'
else:
    label='non_chopped'
    
with open('classifier_time_series_'+label+'_' + subject + '.pkl', 'wb') as fid:
    cPickle.dump([time_axis,classifier_array], fid)


# In[20]:

with open('classifier_time_series_'+'chopped'+'_' + subject + '.pkl', 'rb') as fid:
    time_axis_chopped,classifier_array_chopped = cPickle.load(fid)
    
with open('classifier_time_series_'+'non_chopped'+'_' + subject + '.pkl', 'rb') as fid:
    time_axis_non_chopped,classifier_array_non_chopped = cPickle.load(fid)
    


# In[21]:

plt.plot(time_axis_non_chopped, classifier_array_non_chopped)
plt.plot(time_axis_chopped, classifier_array_chopped)


# In[22]:

# long time interval classifier time series
time_axis_long, classifier_array_long = compute_probs_ts(pow_wavelet_session,
                                          classifier_data,
                                          start_time=50.0,
                                          end_time=1250.0,
                                          slice_size=10,
                                          resolution=0.1
                                          )


# In[30]:

s = slice(2000,3000,1)
plt.plot(time_axis_long[s], classifier_array_long[s])


# In[33]:

time_axis_chopped=time_axis
classifier_array_chopped = classifier_array
auc_v_chopped=0.698392954873
auc_t_chopped = 0.884154414327 


# In[51]:

plt.plot(time_axis, classifier_array)
plt.plot(time_axis_chopped, classifier_array_chopped)


# In[ ]:



