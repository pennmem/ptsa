%module circular_stat
%{
#define SWIG_FILE_WITH_INIT
#include "circular_stat.h"
#include <complex>
%}

%include "numpy.i"

%init %{
import_array();
%}

%numpy_typemaps(bool, NPY_BOOL, size_t)
%numpy_typemaps(double, NPY_DOUBLE, size_t)
%numpy_typemaps(std::complex<double>, NPY_CDOUBLE, size_t)

%apply (std::complex<double>* IN_ARRAY1, size_t DIM1) {(std::complex<double>* c, size_t n)};
%apply (std::complex<double>* IN_ARRAY1, size_t DIM1) {(std::complex<double>* c1, size_t n1)};
%apply (std::complex<double>* IN_ARRAY1, size_t DIM1) {(std::complex<double>* c2, size_t n2)};
%apply (std::complex<double>* INPLACE_ARRAY1, size_t DIM1) {(std::complex<double>* cdiff, size_t n3)};
%apply (std::complex<double>* INPLACE_ARRAY1, size_t DIM1) {(std::complex<double>* cdiff_means, size_t n_bins)};
%apply (std::complex<double>* IN_ARRAY1, size_t DIM1) {(std::complex<double>* phase_diff_mat, size_t n_phase_diffs)};
%apply (bool* IN_ARRAY1, size_t DIM1) {(bool* recalls, size_t n_events)};
%apply (double* INPLACE_ARRAY1, size_t DIM1) {(double* f_stat_mat, size_t n_f_stats)};
%apply (double* INPLACE_ARRAY1, size_t DIM1) {(double* mat, size_t n_mat)};

%apply (std::complex<double>* IN_ARRAY1, size_t DIM1) {(std::complex<double>* wavelet1, size_t n_phases1)};
%apply (std::complex<double>* IN_ARRAY1, size_t DIM1) {(std::complex<double>* wavelet2, size_t n_phases2)};
%apply (double* INPLACE_ARRAY1, size_t DIM1) {(double* ppcs, size_t n_ppcs)};

%apply (std::complex<double>* IN_ARRAY1, size_t DIM1) {(std::complex<double>* wavelets, size_t n_wavelets)};
%apply (double* INPLACE_ARRAY1, size_t DIM1) {(double* ppc_output, size_t n_ppc_output)};

%apply (std::complex<double>* INPLACE_ARRAY1, size_t DIM1) {(std::complex<double>* theta_sum_recalls, size_t n_theta_sum_recalls)};
%apply (std::complex<double>* INPLACE_ARRAY1, size_t DIM1) {(std::complex<double>* theta_sum_non_recalls, size_t n_theta_sum_non_recalls)};

%apply (std::complex<double>* IN_ARRAY1, size_t DIM1) {(std::complex<double>* theta_avg_recalls, size_t n_theta_avg_recalls)};
%apply (std::complex<double>* IN_ARRAY1, size_t DIM1) {(std::complex<double>* theta_avg_non_recalls, size_t n_theta_avg_non_recalls)};

%apply (double* INPLACE_ARRAY1, size_t DIM1) {(double* outsample_ppc_features, size_t n_outsample_ppc_features)};

%include "circular_stat.h"
