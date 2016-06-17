//
// Created by busygin on 1/11/16.
//

#pragma once

#include <fftw3.h>
#include <cmath>
#include <complex>
#include "enums.h"
#include <functional>
#include <map>

#include <iostream>


class MorletWaveFFT {
public:
    size_t len0;
    size_t len;
    fftw_complex *fft;
    size_t nt;

    MorletWaveFFT() : len0(0), len(0), fft(NULL) { }

    ~MorletWaveFFT() { if (fft) fftw_free(fft); }

    size_t init(size_t width, double freq, size_t win_size, double sample_freq);
};

class MorletWaveletTransform {
public:
    typedef std::function<void(MorletWaveletTransform *, double, double, double *&, double *&,std::complex<double> *&)> Fcn_t;


public:


    size_t n_freqs = 0;
    MorletWaveFFT *morlet_wave_ffts = NULL;

    size_t signal_len_;

    double *signal_buf = NULL;
    fftw_complex *fft_buf = NULL;
    fftw_complex *prod_buf = NULL;
    fftw_complex *result_buf = NULL;

    size_t n_plans = 0;
    fftw_plan *plan_for_signal = NULL;
    fftw_plan *plan_for_inverse_transform = NULL;


    MorletWaveletTransform();

    MorletWaveletTransform(size_t width, double *freqs, size_t nf, double sample_freq, size_t signal_len);

    MorletWaveletTransform(size_t width, double low_freq, double high_freq, size_t nf, double sample_freq,
                           size_t signal_len);

    ~MorletWaveletTransform();


    std::function<void(MorletWaveletTransform *, double, double, double *&, double *&, std::complex<double> *&)>
            phase_and_pow_fcn = &MorletWaveletTransform::wv_pow;


    void init(size_t width, double low_freq, double high_freq, size_t nf, double sample_freq, size_t signal_len);

    void init_flex(size_t width, double *freqs, size_t nf, double sample_freq, size_t signal_len);

    void multiphasevec_powers(double *signal,
                              double *powers);  // input: signal, output: n_freqs*signal_len_ 1d array of powers

    void multiphasevec_powers_and_phases(double *signal, double *powers, double *phases);

    void wavelet_pow_phase(double *signal, double *powers, double *phases, std::complex<double> *wavelets);

    void wavelet_pow_phase_py(double *signal, size_t signal_len, double *powers, size_t power_len, double *phases,
                              size_t phase_len, std::complex<double> *wavelets, size_t wavelet_len);


    void set_output_type(OutputType output_type) {
        auto mitr = output_type_2_fcn_map.find(output_type);
        if (mitr != output_type_2_fcn_map.end()) {
            phase_and_pow_fcn = mitr->second;
        }
    }

    void wv_pow(double r, double i, double *&powers, double *&phase, std::complex<double> *&wavelets) {
        *(powers++) = r * r + i * i;
    }

    void wv_phase(double r, double i, double *&powers, double *&phase, std::complex<double> *&wavelets) {

        *(phase++) = atan2(i, r);

    }

    void wv_both(double r, double i, double *&powers, double *&phase, std::complex<double> *&wavelets) {
        wv_pow(r, i, powers, phase, wavelets);
        wv_phase(r, i, powers, phase, wavelets);
    }

    void wv_complex(double r, double i, double *&powers, double *&phase, std::complex<double> *&wavelet_complex) {
        *(wavelet_complex++) = std::complex<double>(r, i);
    }


    void multiphasevec_c(double *signal, std::complex<double> *wavelets);

    // this is to make numpy interface possible
    void multiphasevec(double *signal, size_t signal_len, double *powers, size_t power_len, double *phases = NULL,
                       size_t phase_len = 0);

    void multiphasevec_complex(double *signal, size_t signal_len, std::complex<double> *wavelets, size_t wavelet_len);

private:
    std::map<OutputType, Fcn_t> output_type_2_fcn_map{
            {OutputType::POWER,   &MorletWaveletTransform::wv_pow},
            {OutputType::PHASE,   &MorletWaveletTransform::wv_phase},
            {OutputType::BOTH,    &MorletWaveletTransform::wv_both},
            {OutputType::COMPLEX, &MorletWaveletTransform::wv_complex},
    };


};

