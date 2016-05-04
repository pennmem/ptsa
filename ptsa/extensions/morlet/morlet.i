%module morlet
%{
#define SWIG_FILE_WITH_INIT
#include "morlet.h"
%}

%include "numpy.i"

%init %{
import_array();
%}

%numpy_typemaps(double, NPY_DOUBLE, size_t)

%apply (double* IN_ARRAY1, size_t DIM1) {(double *signal, size_t signal_len)};
%apply (double* INPLACE_ARRAY1, size_t DIM1) {(double *powers, size_t power_len)};
%apply (double* INPLACE_ARRAY1, size_t DIM1) {(double *phases, size_t phase_len)};
%apply (double* IN_ARRAY1, size_t DIM1) {(double *freqs, size_t nf )};

%include "morlet.h"
