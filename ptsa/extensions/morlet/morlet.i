
%module ("threads"=1) morlet
%{
#define SWIG_FILE_WITH_INIT
#include "morlet.h"
#include "MorletWaveletTransformMP.h"
#include "MorletWaveletTransformMP_tp.h"
#include "enums.h"
#include <complex>

%}

%include "numpy.i"

%init %{
import_array();
%}

%numpy_typemaps(double, NPY_DOUBLE, size_t)
%numpy_typemaps(std::complex<double>, NPY_CDOUBLE, size_t)

%apply (double* IN_ARRAY1, size_t DIM1) {(double *signal, size_t signal_len)};
%apply (double* INPLACE_ARRAY1, size_t DIM1) {(double *powers, size_t power_len)};
%apply (double* INPLACE_ARRAY1, size_t DIM1) {(double *phases, size_t phase_len)};
%apply (std::complex<double>* INPLACE_ARRAY1, size_t DIM1) {(std::complex<double> *wavelets, size_t wavelet_len)};
%apply (double* IN_ARRAY1, size_t DIM1) {(double *freqs, size_t nf)};

%apply (double* INPLACE_ARRAY2, size_t DIM1, size_t DIM2) {(double *signal_array, size_t num_signals, size_t signal_len)};
%apply (double* INPLACE_ARRAY2, size_t DIM1, size_t DIM2) {(double *wavelet_pow_array, size_t num_wavelets, size_t signal_len)};
// %apply (double* INPLACE_ARRAY2, size_t DIM1, size_t DIM2) {(double *wavelet_pow_array, size_t num_wavelets, size_t signal_len_pow)};
%apply (double* INPLACE_ARRAY2, size_t DIM1, size_t DIM2) {(double *wavelet_phase_array, size_t num_wavelets, size_t signal_len)};
%apply (std::complex<double>* INPLACE_ARRAY1, size_t DIM1) {(std::complex<double> *wavelets_complex_array, size_t wavelet_len)};
%apply (std::complex<double>* INPLACE_ARRAY2, size_t DIM1, size_t DIM2) {(std::complex<double> *wavelet_complex_array, size_t num_wavelets, size_t signal_len)};

// %apply (double* INPLACE_ARRAY2, size_t DIM1, size_t DIM2) {(double *wavelet_array, size_t num_wavelets, size_t signal_len)};
// %apply (double* INPLACE_ARRAY2, size_t DIM1, size_t DIM2) {(double *wavelet_array, size_t num_wavelets, size_t signal_len_1)};



%include "enums.h"
%include "morlet.h"
%include "MorletWaveletTransformMP.h"
%include "MorletWaveletTransformMP_tp.h"

// %clear(double *signal_array, size_t num_signals, size_t signal_len);
