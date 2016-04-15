//
// Created by busygin on 1/11/16.
//

#define _USE_MATH_DEFINES

#include <cmath>
#include <cstring>
#include "morlet.h"
#include "log_space.h"
#include <iostream>

using namespace std;


size_t nextpow2(size_t v) {
    --v;
    v |= v >> 1;
    v |= v >> 2;
    v |= v >> 4;
    v |= v >> 8;
    v |= v >> 16;
    v |= v >> 32;
    return ++v;
}


size_t MorletWaveFFT::init(size_t width, double freq, size_t win_size, double sample_freq) {

    double dt = 1.0 / sample_freq;
    double sf = freq / width;
    double st = 1.0 / (2.0 * M_PI * sf);
    double a = 1 / sqrt(st * sqrt(M_PI));
    double omega = 2.0 * M_PI * freq;

    nt = size_t(7.0 * st / dt) + 1;
    len0 = win_size + nt - 1;
    len = nextpow2(len0);
    fft = (fftw_complex *) fftw_malloc(len * sizeof(fftw_complex));

    fftw_complex *cur_wave = (fftw_complex *) fftw_malloc(len * sizeof(fftw_complex));

    double t = -3.5 * st;
    double scale = 2.0 * st * st;
    for (size_t i = 0; i < nt; ++i) {
        double c = a * exp(-t * t / scale);
        double omega_t = omega * t;
        cur_wave[i][0] = c * cos(omega_t);
        cur_wave[i][1] = c * sin(omega_t);
        t += dt;
    }
    for (size_t i = nt; i < len; ++i)
        cur_wave[i][0] = cur_wave[i][1] = 0.0;

    fftw_plan plan = fftw_plan_dft_1d(len, cur_wave, fft, FFTW_FORWARD, FFTW_ESTIMATE);
    fftw_execute(plan);

    fftw_destroy_plan(plan);
    fftw_free(cur_wave);

    return len;
}

MorletWaveletTransform::MorletWaveletTransform(){}

MorletWaveletTransform::MorletWaveletTransform(size_t width, double *freqs, size_t nf, double sample_freq, size_t signal_len){
    init_flex(width, freqs, nf, sample_freq,signal_len);
}

MorletWaveletTransform::MorletWaveletTransform(size_t width, double low_freq, double high_freq, size_t nf, double sample_freq, size_t signal_len) {

    std::vector<double> freqs = logspace(log10(low_freq), log10(high_freq), nf);

    init_flex(width, &freqs[0], nf, sample_freq, signal_len);


}

MorletWaveletTransform::~MorletWaveletTransform() {
    if (n_freqs) {
        delete[] morlet_wave_ffts;
        fftw_free(signal_buf);
        fftw_free(fft_buf);
        fftw_free(prod_buf);
        fftw_free(result_buf);
        for (size_t i = 0; i < n_plans; ++i) {
            fftw_destroy_plan(plan_for_signal[i]);
            fftw_destroy_plan(plan_for_inverse_transform[i]);
        }
        delete[] plan_for_signal;
        delete[] plan_for_inverse_transform;
    }
}




void MorletWaveletTransform::init_flex(size_t width, double *freqs, size_t nf, double sample_freq,
                                       size_t signal_len) {


    cerr << "got freq array size " << nf << endl;
    cout << "got freq array size " << nf << endl;

    for (size_t i=0 ; i < nf; ++i ){
        cerr<<"freqs["<<i<<"]="<<freqs[i]<<endl;

    }

    signal_len_ = signal_len;
    n_freqs = nf;
    morlet_wave_ffts = new MorletWaveFFT[nf];
    n_plans = 0;
    size_t last_len = 0;
    for (size_t i = 0; i < nf; ++i) {
        size_t len = morlet_wave_ffts[i].init(width, freqs[i], signal_len, sample_freq);
        if (len != last_len) {
            last_len = len;
            ++n_plans;
        }
    }

    // initialize buffers
    size_t fft_len_max = morlet_wave_ffts[nf - 1].len;
    if (fft_len_max < morlet_wave_ffts[0].len)
        fft_len_max = morlet_wave_ffts[0].len;
    prod_buf = (fftw_complex *) fftw_malloc(fft_len_max * sizeof(fftw_complex));
    result_buf = (fftw_complex *) fftw_malloc(fft_len_max * sizeof(fftw_complex));
    signal_buf = (double *) fftw_malloc(fft_len_max * sizeof(double));
    memset(signal_buf, 0, fft_len_max * sizeof(double));
    fft_buf = (fftw_complex *) fftw_malloc((fft_len_max / 2 + 1) * sizeof(fftw_complex));

    plan_for_signal = new fftw_plan[n_plans];
    plan_for_inverse_transform = new fftw_plan[n_plans];

    last_len = 0;
    size_t plan = 0;
    for (MorletWaveFFT *wavelet = morlet_wave_ffts; wavelet < morlet_wave_ffts + n_freqs; ++wavelet) {
        size_t len = wavelet->len;
        if (len != last_len) {
            last_len = len;
            plan_for_signal[plan] = fftw_plan_dft_r2c_1d(len, signal_buf, fft_buf, FFTW_PATIENT);
            plan_for_inverse_transform[plan] = fftw_plan_dft_1d(len, prod_buf, result_buf, FFTW_BACKWARD, FFTW_PATIENT);
            ++plan;
        }
    }

}

void MorletWaveletTransform::init(size_t width, double low_freq, double high_freq, size_t nf, double sample_freq,
                                  size_t signal_len) {


    std::vector<double> freqs = logspace(log10(low_freq), log10(high_freq), nf);

    init_flex(width, &freqs[0], nf, sample_freq, signal_len);
}


//void MorletWaveletTransform::init(size_t width, double low_freq, double high_freq, size_t nf, double sample_freq,
//                                  size_t signal_len) {
//    signal_len_ = signal_len;
//    n_freqs = nf;
//    std::vector<double> freqs = logspace(log10(low_freq), log10(high_freq), nf);
//    morlet_wave_ffts = new MorletWaveFFT[nf];
//    n_plans = 0;
//    size_t last_len = 0;
//    for (size_t i = 0; i < nf; ++i) {
//        size_t len = morlet_wave_ffts[i].init(width, freqs[i], signal_len, sample_freq);
//        if (len != last_len) {
//            last_len = len;
//            ++n_plans;
//        }
//    }
//
//    // initialize buffers
//    size_t fft_len_max = morlet_wave_ffts[nf - 1].len;
//    if (fft_len_max < morlet_wave_ffts[0].len)
//        fft_len_max = morlet_wave_ffts[0].len;
//    prod_buf = (fftw_complex *) fftw_malloc(fft_len_max * sizeof(fftw_complex));
//    result_buf = (fftw_complex *) fftw_malloc(fft_len_max * sizeof(fftw_complex));
//    signal_buf = (double *) fftw_malloc(fft_len_max * sizeof(double));
//    memset(signal_buf, 0, fft_len_max * sizeof(double));
//    fft_buf = (fftw_complex *) fftw_malloc((fft_len_max / 2 + 1) * sizeof(fftw_complex));
//
//    plan_for_signal = new fftw_plan[n_plans];
//    plan_for_inverse_transform = new fftw_plan[n_plans];
//
//    last_len = 0;
//    size_t plan = 0;
//    for (MorletWaveFFT *wavelet = morlet_wave_ffts; wavelet < morlet_wave_ffts + n_freqs; ++wavelet) {
//        size_t len = wavelet->len;
//        if (len != last_len) {
//            last_len = len;
//            plan_for_signal[plan] = fftw_plan_dft_r2c_1d(len, signal_buf, fft_buf, FFTW_PATIENT);
//            plan_for_inverse_transform[plan] = fftw_plan_dft_1d(len, prod_buf, result_buf, FFTW_BACKWARD, FFTW_PATIENT);
//            ++plan;
//        }
//    }
//}

void product_with_herm_fft(size_t len, fftw_complex *fft1, fftw_complex *fft_herm, fftw_complex *result) {
    // fft1 and result have length len
    // but fft_herm has length len/2+1
    result[0][0] = fft1[0][0] * fft_herm[0][0] - fft1[0][1] * fft_herm[0][1];
    result[0][1] = fft1[0][0] * fft_herm[0][1] + fft1[0][1] * fft_herm[0][0];

    size_t i;
    for (i = 1; i < len / 2; ++i) {
        result[i][0] = fft1[i][0] * fft_herm[i][0] - fft1[i][1] * fft_herm[i][1];
        result[i][1] = fft1[i][0] * fft_herm[i][1] + fft1[i][1] * fft_herm[i][0];
    }

    result[i][0] = fft1[i][0] * fft_herm[i][0] - fft1[i][1] * fft_herm[i][1];
    result[i][1] = fft1[i][0] * fft_herm[i][1] + fft1[i][1] * fft_herm[i][0];

    size_t j = len / 2 - 1;
    for (++i; i < len; ++i, --j) {
        result[i][0] = fft1[i][0] * fft_herm[j][0] + fft1[i][1] * fft_herm[j][1];
        result[i][1] = fft1[i][1] * fft_herm[j][0] - fft1[i][0] * fft_herm[j][1];
    }
}

void MorletWaveletTransform::multiphasevec_powers(double *signal, double *powers) {
    memcpy(signal_buf, signal, signal_len_ * sizeof(double));

    size_t last_len = 0;
    size_t plan = 0;
    for (MorletWaveFFT *wavelet = morlet_wave_ffts; wavelet < morlet_wave_ffts + n_freqs; ++wavelet) {
        size_t len = wavelet->len;
        if (len != last_len) {
            last_len = len;
            fftw_execute(plan_for_signal[plan]);
            ++plan;
        }

        // construct product
        product_with_herm_fft(len, wavelet->fft, fft_buf, prod_buf);

        // inverse fft
        fftw_execute(plan_for_inverse_transform[plan - 1]);

        // retrieve powers
        size_t first_idx = (wavelet->nt - 1) / 2;
        for (size_t i = first_idx; i < first_idx + signal_len_; ++i) {
            result_buf[i][0] /= len;
            result_buf[i][1] /= len;
            *(powers++) = result_buf[i][0] * result_buf[i][0] + result_buf[i][1] * result_buf[i][1];
        }
    }
}

void MorletWaveletTransform::multiphasevec(double *signal, size_t signal_len, double *powers, size_t power_len) {
    multiphasevec_powers(signal, powers);
}
