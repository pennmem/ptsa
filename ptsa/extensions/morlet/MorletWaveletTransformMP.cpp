//
// Created by m on 6/10/16.
//
#include <iostream>
#include "MorletWaveletTransformMP.h"

#include <thread>
#include <list>
#include <cmath>
#include<ThreadPool.h>

#include "morlet.h"

using namespace std;

MorletWaveletTransformMP::MorletWaveletTransformMP (unsigned int cpus) : cpus(cpus) {

    array.assign(1000000, 0.0);

    threadpool_ptr = std::make_shared<ThreadPool>(cpus);

}

void MorletWaveletTransformMP ::prepare_run() {

    for (unsigned int i = 0; i < cpus; ++i) {
        mwt_vec.push_back(shared_ptr<MorletWaveletTransform>(new MorletWaveletTransform));
        auto &mwt_ptr = mwt_vec[i];

        mwt_ptr->init_flex(width, freqs, num_freq, sample_freq, signal_len,
            complete);
        mwt_ptr->set_output_type(output_type);

    }
}


int MorletWaveletTransformMP ::compute_wavelets_worker_fcn(unsigned int thread_no) {

    auto &mwt = mwt_vec[thread_no];

    size_t chunk = num_signals / cpus;

    size_t idx_start = thread_no * chunk;
    size_t idx_stop = thread_no * chunk + chunk;

    if (thread_no == cpus - 1) {
        idx_stop = num_signals;
    }

    auto mwt_wavelet_pow_phase = [=](double *signal, size_t idx_out) { mwt->wavelet_pow_phase(signal,
                                                                                              wavelet_pow_array +
                                                                                              idx_out,
                                                                                              wavelet_phase_array +
                                                                                              idx_out, nullptr);
    };
    auto mwt_wavelet_complex = [=](double *signal, size_t idx_out) { mwt->wavelet_pow_phase(signal, nullptr, nullptr,
                                                                                            wavelet_complex_array +
                                                                                            idx_out);
    };
//    auto mwt_wavelet_complex = [=]( double *signal, size_t idx_out ) {mwt->multiphasevec_c(signal, wavelet_complex_array + idx_out);};

    std::map<OutputType, std::function<void(double *, size_t)>> wavelet_compute_fcn_map{
            {OutputType::POWER,   mwt_wavelet_pow_phase},
            {OutputType::PHASE,   mwt_wavelet_pow_phase},
            {OutputType::BOTH,    mwt_wavelet_pow_phase},
            {OutputType::COMPLEX, mwt_wavelet_complex},
    };

    std::function<void(double *, size_t)> wavelet_compute_fcn;

    auto mitr = wavelet_compute_fcn_map.find(this->output_type);
    if (mitr != wavelet_compute_fcn_map.end()) {
        wavelet_compute_fcn = mitr->second;
    }

    for (size_t sig_num = idx_start; sig_num < idx_stop; ++sig_num) {
        size_t idx_signal = index(sig_num, 0, signal_len);
        auto signal = signal_array + idx_signal;

        size_t idx_out = index(num_freq * sig_num, 0, signal_len);

        wavelet_compute_fcn(signal, idx_out);

    }

    return 0;

}


void MorletWaveletTransformMP ::compute_wavelets_threads() {
    std::vector< std::future<int> > results;

    for (unsigned int i = 0; i < cpus; ++i) {
        results.emplace_back(
            threadpool_ptr->enqueue(
                [=] { return compute_wavelets_worker_fcn(i); }
            )
        );
    }

    //barrier
    for(auto && result: results){
         result.get();
    }
}
