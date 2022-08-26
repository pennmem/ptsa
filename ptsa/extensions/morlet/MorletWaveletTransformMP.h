//
// Created by m on 6/10/16.
//
#pragma once

#include <vector>
#include <memory>
#include "enums.h"
#include "unusedparam.h"
#include <complex>


class MorletWaveletTransform;
class ThreadPool;

class MorletWaveletTransformMP {
private:

    unsigned int cpus = 1;
    unsigned int num_freq = -1;

    std::vector<std::shared_ptr<MorletWaveletTransform> > mwt_vec;
    std::shared_ptr<ThreadPool> threadpool_ptr;

    size_t signal_len = -1;
    size_t num_signals = -1;

    double *signal_array = nullptr;
    double *wavelet_pow_array = nullptr;
    double *wavelet_phase_array = nullptr;

    std::complex<double> *wavelet_complex_array = nullptr;

    double *freqs = nullptr;
    double sample_freq = -1.0;
    size_t width = -1;
    bool complete = true;

    OutputType output_type = OutputType::POWER;

public:

    MorletWaveletTransformMP (unsigned int cpus = 1);


    void set_num_freq(unsigned int num_freq) {
        this->num_freq = num_freq;
    }

    void set_signal_array(double *signal_array, size_t num_signals, size_t signal_len) {
        this->signal_len = signal_len;
        this->num_signals = num_signals;
        this->signal_array = signal_array;
    }

    void set_wavelet_pow_array(double *wavelet_pow_array, size_t num_wavelets, size_t signal_len) {
        UnusedParam(num_wavelets);
        UnusedParam(signal_len);
        this->wavelet_pow_array = wavelet_pow_array;
    }

    void set_wavelet_phase_array(double *wavelet_phase_array, size_t num_wavelets, size_t signal_len) {
        UnusedParam(num_wavelets);
        UnusedParam(signal_len);
        this->wavelet_phase_array = wavelet_phase_array;
    }

    void set_wavelet_complex_array(std::complex<double> *wavelet_complex_array, size_t num_wavelets, size_t signal_len) {
        UnusedParam(num_wavelets);
        UnusedParam(signal_len);
        this->wavelet_complex_array = wavelet_complex_array;
    }


    void set_output_type(OutputType output_type) {
        this->output_type = output_type;
    }

    void initialize_signal_props(double sample_freq) {
        this->sample_freq = sample_freq;
    }

    void initialize_wavelet_props(size_t width, double *freqs, size_t nf,
          bool complete=true) {
        this->freqs = freqs;
        this->num_freq = nf;
        this->width = width;
        this->complete = complete;
    }


    void prepare_run();

    int compute_wavelets_worker_fcn(unsigned int thread_no);

    void compute_wavelets_threads();

    inline size_t index(size_t i, size_t j, size_t stride) {

        return i * stride + j;
    }


private:
    std::vector<double> array;
};
