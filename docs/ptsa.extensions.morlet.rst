ptsa.extensions.morlet package
******************************


Submodules
==========


ptsa.extensions.morlet.morlet module
====================================

class ptsa.extensions.morlet.morlet.MorletWaveFFT

   Bases: "object"

   fft

   init(width, freq, win_size, sample_freq)

   len

   len0

   nt

class ptsa.extensions.morlet.morlet.MorletWaveletTransform(*args)

   Bases: "object"

   fft_buf

   init(width, low_freq, high_freq, nf, sample_freq, signal_len)

   init_flex(width, freqs, sample_freq, signal_len)

   morlet_wave_ffts

   multiphasevec(signal, powers, phases=None)

   multiphasevec_c(signal, wavelets)

   multiphasevec_complex(signal, wavelets)

   multiphasevec_powers(signal, powers)

   multiphasevec_powers_and_phases(signal, powers, phases)

   n_freqs

   n_plans

   phase_and_pow_fcn

   plan_for_inverse_transform

   plan_for_signal

   prod_buf

   result_buf

   set_output_type(output_type)

   signal_buf

   signal_len_

   wavelet_pow_phase(signal, powers, phases, wavelets)

   wavelet_pow_phase_py(signal, powers, phases, wavelets)

   wv_both(r, i, powers, phase, wavelets)

   wv_complex(r, i, powers, phase, wavelet_complex)

   wv_phase(r, i, powers, phase, wavelets)

   wv_pow(r, i, powers, phase, wavelets)

class ptsa.extensions.morlet.morlet.MorletWaveletTransformMP(cpus=1)

   Bases: "object"

   compute_wavelets_threads()

   compute_wavelets_worker_fcn(thread_no)

   index(i, j, stride)

   initialize_signal_props(sample_freq)

   initialize_wavelet_props(width, freqs)

   prepare_run()

   set_num_freq(num_freq)

   set_output_type(output_type)

   set_signal_array(signal_array)

   set_wavelet_complex_array(wavelet_complex_array)

   set_wavelet_phase_array(wavelet_phase_array)

   set_wavelet_pow_array(wavelet_pow_array)


Module contents
===============
