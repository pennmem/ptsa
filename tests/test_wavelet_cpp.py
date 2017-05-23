import sys
from ptsa.extensions import morlet
from scipy.stats import describe
import numpy as np


def fixme():
    num_freqs = 8
    min_frequency = 3.0
    max_frequency = 60.0

    morlet_transform = morlet.MorletWaveletTransform(5, np.logspace(np.log10(min_frequency), np.log10(max_frequency), num_freqs),  1000, 4096)
    # morlet_transform = morlet.MorletWaveletTransform(5, min_frequency, max_frequency, num_freqs, 1000, 4096)

    # morlet_transform = morlet.MorletWaveletTransform()
    # morlet_transform.init_flex(5, np.logspace(np.log10(min_frequency), np.log10(max_frequency), num_freqs),  1000, 4096)
    # morlet_transform.init(5, min_frequency, max_frequency, num_freqs, 1000, 4096)

    samplerate = 1000.
    frequency = 60.0
    modulation_frequency = 80.0

    duration = 4.096

    n_points = int(np.round(duration*samplerate))
    x = np.arange(n_points, dtype=np.float)
    signal = np.sin(x*(2*np.pi*frequency/samplerate))-np.cos(x*(2*np.pi*frequency/samplerate))

    powers=np.empty(shape=(signal.shape[0]*num_freqs,), dtype=np.float)
    num_of_iterations = 100
    # for i in xrange(num_of_iterations):
    #     morlet_transform.multiphasevec(signal,powers)
    morlet_transform.multiphasevec(signal,powers)

    powers = powers.reshape(8,powers.shape[0]/8)

    print(describe(powers))
