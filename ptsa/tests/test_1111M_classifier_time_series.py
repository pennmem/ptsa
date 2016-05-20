import sys
sys.path.append('/Users/m/PTSA_NEW_GIT/')
import numpy as np
from numpy.testing import *
from ptsa.data.readers import BaseEventReader
from ptsa.data.filters.MorletWaveletFilter import MorletWaveletFilter
from ptsa.data.readers.TalReader import TalReader
from ptsa.data.readers import EEGReader
from ptsa.data.filters import MonopolarToBipolarMapper
from ptsa.data.common import xr
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, roc_curve
from scipy.stats.mstats import zscore
from time import time
start_time = time()

e_path = '/Users/m/data/events/RAM_FR1/R1111M_events.mat'
tal_path = '/Users/m/data/eeg/R1111M/tal/R1111M_talLocs_database_bipol.mat'
tal_reader = TalReader(filename=tal_path)
monopolar_channels = tal_reader.get_monopolar_channels()
bipolar_pairs = tal_reader.get_bipolar_pairs()

# ---------------- NEW STYLE PTSA -------------------
base_e_reader = BaseEventReader(filename=e_path, eliminate_events_with_no_eeg=True)

base_events = base_e_reader.read()

base_events = base_events[base_events.type == 'WORD']
base_events.shape

# retaining first session
sessions = np.unique(base_events.session)
# dataroot = base_events[0].eegfile
# base_events = base_events[base_events.eegfile == dataroot]

eeg_reader = EEGReader(events=base_events, channels=monopolar_channels,
                       start_time=0.0, end_time=1.6, buffer_time=1.0)

base_eegs = eeg_reader.read()

m2b = MonopolarToBipolarMapper(time_series=base_eegs, bipolar_pairs=bipolar_pairs)
bp_eegs = m2b.filter()

from time import time
s = time()
# wf = MorletWaveletFilter(time_series=bp_eegs,
#                          freqs=np.logspace(np.log10(3), np.log10(180), 8),
#                          output='power',
#                          frequency_dim_pos=0,
#                          verbose=True
#                          )

# wf = MorletWaveletFilter(time_series=bp_eegs,
#                          freqs=np.logspace(np.log10(3), np.log10(192), 7),
#                          output='power',
#                          frequency_dim_pos=0,
#                          verbose=True
#                          )


# wf = MorletWaveletFilter(time_series=bp_eegs,
#                          freqs=np.logspace(np.log10(3), np.log10(24), 1),
#                          output='power',
#                          frequency_dim_pos=0,
#                          verbose=True
#                          )


# wf = MorletWaveletFilter(time_series=bp_eegs,
#                          freqs=np.logspace(np.log10(48), np.log10(96), 1),
#                          output='power',
#                          frequency_dim_pos=0,
#                          verbose=True
#                          )


wf = MorletWaveletFilter(time_series=bp_eegs,
                         freqs=np.array([96]),
                         output='power',
                         frequency_dim_pos=0,
                         verbose=True
                         )


pow_wavelet, phase_wavelet = wf.filter()
print 'TOTAL WAVELET TIME=', time()-s

pow_wavelet = pow_wavelet.remove_buffer(duration=1.0)

np.log10(pow_wavelet.data, out=pow_wavelet.data);

pow_wavelet = pow_wavelet.transpose("events","bipolar_pairs","frequency","time")

mean_powers_nd = np.nanmean(pow_wavelet.data,axis=-1)

mean_powers_rs = mean_powers_nd.reshape(mean_powers_nd.shape[0],-1)
mean_powers_rs.shape

zscore_mean_powers = zscore(mean_powers_rs, axis=0, ddof=1)


sess_min = 0
sess_max = 1
validation_sess_min = 2
validation_sess_max = 2


evs = base_events

training_session_mask =(evs.session>=sess_min) &(evs.session<=sess_max)




evs_sel = evs[training_session_mask]
evs_sel.shape
recalls_array = evs_sel.recalled.astype(np.int)

training_data = zscore_mean_powers[training_session_mask,...]
training_data.shape

validation_session_mask =(evs.session>=validation_sess_min) &(evs.session<=validation_sess_max)
evs_val = evs[validation_session_mask]
validation_data = zscore_mean_powers[validation_session_mask,...]
validation_data.shape
validation_recalls_array = evs_val.recalled.astype(np.int)
validation_recalls_array .shape




lr_classifier = LogisticRegression(C=7.2e-4, penalty='l2', class_weight='auto', solver='liblinear')
lr_classifier.fit(training_data, recalls_array)


recall_prob_array = lr_classifier.predict_proba(training_data)[:,1]
auc = roc_auc_score(recalls_array, recall_prob_array)
print 'auc=',auc


validation_recall_prob_array = lr_classifier.predict_proba(validation_data)[:,1]
validation_auc = roc_auc_score(validation_recalls_array, validation_recall_prob_array)
print 'validation_auc=',validation_auc