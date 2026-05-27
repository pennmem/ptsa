// pybind11 bindings for the Morlet wavelet C++ kernel.
//
// Replaces the old SWIG interface (morlet.i + vendored numpy.i). The Python
// surface intentionally matches what SWIG produced so that callers like
// ``ptsa.data.filters.morlet.MorletWaveletFilter`` continue to work without
// modification. In particular, SWIG collapsed ``(double *ptr, size_t n)``
// argument pairs into a single numpy array. We reproduce that here with
// thin lambdas that pull ``ptr`` and ``size`` out of a ``py::array``.
//
// ``MorletWaveletTransformMP::set_*_array`` only stores raw pointers into the
// caller's buffers, so we use ``py::keep_alive`` to make the wrapped numpy
// arrays outlive the MP object.
#include <complex>
#include <stdexcept>
#include <string>

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/complex.h>

#include "morlet.h"
#include "MorletWaveletTransformMP.h"
#include "enums.h"

namespace py = pybind11;

namespace {

// Request a contiguous double array and return (ptr, total size).
// "c_style | forcecast" matches how SWIG's numpy.i typemaps coerced inputs.
using DoubleArray = py::array_t<double, py::array::c_style | py::array::forcecast>;
using ComplexArray =
    py::array_t<std::complex<double>, py::array::c_style | py::array::forcecast>;

inline double *dptr(DoubleArray &a, std::size_t &n) {
    auto info = a.request();
    n = static_cast<std::size_t>(info.size);
    return static_cast<double *>(info.ptr);
}

inline std::complex<double> *cptr(ComplexArray &a, std::size_t &n) {
    auto info = a.request();
    n = static_cast<std::size_t>(info.size);
    return static_cast<std::complex<double> *>(info.ptr);
}

}  // namespace

PYBIND11_MODULE(_morlet, m) {
    m.doc() = "Morlet wavelet transform (pybind11 bindings).";

    py::enum_<OutputType>(m, "OutputType")
        .value("POWER", OutputType::POWER)
        .value("PHASE", OutputType::PHASE)
        .value("BOTH", OutputType::BOTH)
        .value("COMPLEX", OutputType::COMPLEX)
        .export_values();

    // Also expose enum values as module-level attributes for SWIG compat:
    // ``from ptsa.extensions.morlet import POWER`` and ``morlet.POWER``.
    m.attr("POWER") = py::cast(OutputType::POWER);
    m.attr("PHASE") = py::cast(OutputType::PHASE);
    m.attr("BOTH") = py::cast(OutputType::BOTH);
    m.attr("COMPLEX") = py::cast(OutputType::COMPLEX);

    py::class_<MorletWaveFFT>(m, "MorletWaveFFT")
        .def(py::init<>())
        .def_readwrite("len0", &MorletWaveFFT::len0)
        .def_readwrite("len", &MorletWaveFFT::len)
        .def_readwrite("nt", &MorletWaveFFT::nt)
        .def("init", &MorletWaveFFT::init,
             py::arg("width"), py::arg("freq"), py::arg("win_size"),
             py::arg("sample_freq"), py::arg("complete") = true);

    py::class_<MorletWaveletTransform>(m, "MorletWaveletTransform")
        .def(py::init<>())
        // SWIG exposed both flex (freqs array) and low/high overloads via
        // ``def __init__(self, *args)``. Reproduce both as initializers.
        .def(py::init([](std::size_t width, DoubleArray freqs,
                         double sample_freq, std::size_t signal_len,
                         bool complete) {
                 std::size_t nf = 0;
                 double *fp = dptr(freqs, nf);
                 return new MorletWaveletTransform(width, fp, nf, sample_freq,
                                                   signal_len, complete);
             }),
             py::arg("width"), py::arg("freqs"), py::arg("sample_freq"),
             py::arg("signal_len"), py::arg("complete") = true)
        .def(py::init<std::size_t, double, double, std::size_t, double,
                      std::size_t, bool>(),
             py::arg("width"), py::arg("low_freq"), py::arg("high_freq"),
             py::arg("nf"), py::arg("sample_freq"), py::arg("signal_len"),
             py::arg("complete") = true)
        .def_readwrite("n_freqs", &MorletWaveletTransform::n_freqs)
        .def_readwrite("n_plans", &MorletWaveletTransform::n_plans)
        .def_readwrite("signal_len_", &MorletWaveletTransform::signal_len_)
        .def("init",
             &MorletWaveletTransform::init,
             py::arg("width"), py::arg("low_freq"), py::arg("high_freq"),
             py::arg("nf"), py::arg("sample_freq"), py::arg("signal_len"),
             py::arg("complete") = true)
        .def("init_flex",
             [](MorletWaveletTransform &self, std::size_t width,
                DoubleArray freqs, double sample_freq, std::size_t signal_len,
                bool complete) {
                 std::size_t nf = 0;
                 double *fp = dptr(freqs, nf);
                 self.init_flex(width, fp, nf, sample_freq, signal_len,
                                complete);
             },
             py::arg("width"), py::arg("freqs"), py::arg("sample_freq"),
             py::arg("signal_len"), py::arg("complete") = true)
        .def("set_output_type", &MorletWaveletTransform::set_output_type,
             py::arg("output_type"))
        .def("multiphasevec_powers",
             [](MorletWaveletTransform &self, DoubleArray signal,
                DoubleArray powers) {
                 std::size_t n_sig = 0, n_pow = 0;
                 double *sp = dptr(signal, n_sig);
                 double *pp = dptr(powers, n_pow);
                 self.multiphasevec_powers(sp, pp);
             },
             py::arg("signal"), py::arg("powers"))
        .def("multiphasevec_powers_and_phases",
             [](MorletWaveletTransform &self, DoubleArray signal,
                DoubleArray powers, DoubleArray phases) {
                 std::size_t n = 0;
                 double *sp = dptr(signal, n);
                 double *pp = dptr(powers, n);
                 double *php = dptr(phases, n);
                 self.multiphasevec_powers_and_phases(sp, pp, php);
             },
             py::arg("signal"), py::arg("powers"), py::arg("phases"))
        // ``multiphasevec(signal, powers, phases=None)`` -- SWIG made phases
        // optional.
        .def("multiphasevec",
             [](MorletWaveletTransform &self, DoubleArray signal,
                DoubleArray powers, py::object phases) {
                 std::size_t n_sig = 0, n_pow = 0;
                 double *sp = dptr(signal, n_sig);
                 double *pp = dptr(powers, n_pow);
                 if (phases.is_none()) {
                     self.multiphasevec(sp, n_sig, pp, n_pow, nullptr, 0);
                 } else {
                     DoubleArray ph = phases.cast<DoubleArray>();
                     std::size_t n_ph = 0;
                     double *php = dptr(ph, n_ph);
                     self.multiphasevec(sp, n_sig, pp, n_pow, php, n_ph);
                 }
             },
             py::arg("signal"), py::arg("powers"),
             py::arg("phases") = py::none())
        .def("multiphasevec_complex",
             [](MorletWaveletTransform &self, DoubleArray signal,
                ComplexArray wavelets) {
                 std::size_t n_sig = 0, n_w = 0;
                 double *sp = dptr(signal, n_sig);
                 std::complex<double> *wp = cptr(wavelets, n_w);
                 self.multiphasevec_complex(sp, n_sig, wp, n_w);
             },
             py::arg("signal"), py::arg("wavelets"))
        .def("wavelet_pow_phase",
             [](MorletWaveletTransform &self, DoubleArray signal,
                DoubleArray powers, DoubleArray phases,
                ComplexArray wavelets) {
                 std::size_t n = 0;
                 double *sp = dptr(signal, n);
                 double *pp = dptr(powers, n);
                 double *php = dptr(phases, n);
                 std::complex<double> *wp = cptr(wavelets, n);
                 self.wavelet_pow_phase(sp, pp, php, wp);
             },
             py::arg("signal"), py::arg("powers"), py::arg("phases"),
             py::arg("wavelets"))
        .def("wavelet_pow_phase_py",
             [](MorletWaveletTransform &self, DoubleArray signal,
                DoubleArray powers, DoubleArray phases,
                ComplexArray wavelets) {
                 std::size_t n_sig = 0, n_pow = 0, n_ph = 0, n_w = 0;
                 double *sp = dptr(signal, n_sig);
                 double *pp = dptr(powers, n_pow);
                 double *php = dptr(phases, n_ph);
                 std::complex<double> *wp = cptr(wavelets, n_w);
                 self.wavelet_pow_phase_py(sp, n_sig, pp, n_pow, php, n_ph,
                                            wp, n_w);
             },
             py::arg("signal"), py::arg("powers"), py::arg("phases"),
             py::arg("wavelets"));

    // The MP class only stores raw pointers into caller-owned numpy buffers
    // -- ``py::keep_alive<1, 2>`` ties each input array's lifetime to the MP
    // object (1 = self, 2 = first arg). Otherwise the Python GC could free
    // the array between ``set_*`` and ``compute_wavelets_threads``.
    py::class_<MorletWaveletTransformMP>(m, "MorletWaveletTransformMP")
        .def(py::init<unsigned int>(), py::arg("cpus") = 1)
        .def("set_num_freq", &MorletWaveletTransformMP::set_num_freq,
             py::arg("num_freq"))
        // 2D input arrays for signals + outputs.
        .def("set_signal_array",
             [](MorletWaveletTransformMP &self, DoubleArray arr) {
                 auto info = arr.request();
                 if (info.ndim != 2) {
                     throw std::invalid_argument(
                         "signal_array must be 2-D (num_signals, signal_len)");
                 }
                 std::size_t num_signals = static_cast<std::size_t>(info.shape[0]);
                 std::size_t signal_len = static_cast<std::size_t>(info.shape[1]);
                 self.set_signal_array(static_cast<double *>(info.ptr),
                                        num_signals, signal_len);
             },
             py::arg("signal_array"), py::keep_alive<1, 2>())
        .def("set_wavelet_pow_array",
             [](MorletWaveletTransformMP &self, DoubleArray arr) {
                 auto info = arr.request();
                 if (info.ndim != 2) {
                     throw std::invalid_argument(
                         "wavelet_pow_array must be 2-D");
                 }
                 std::size_t nw = static_cast<std::size_t>(info.shape[0]);
                 std::size_t sl = static_cast<std::size_t>(info.shape[1]);
                 self.set_wavelet_pow_array(static_cast<double *>(info.ptr),
                                             nw, sl);
             },
             py::arg("wavelet_pow_array"), py::keep_alive<1, 2>())
        .def("set_wavelet_phase_array",
             [](MorletWaveletTransformMP &self, DoubleArray arr) {
                 auto info = arr.request();
                 if (info.ndim != 2) {
                     throw std::invalid_argument(
                         "wavelet_phase_array must be 2-D");
                 }
                 std::size_t nw = static_cast<std::size_t>(info.shape[0]);
                 std::size_t sl = static_cast<std::size_t>(info.shape[1]);
                 self.set_wavelet_phase_array(static_cast<double *>(info.ptr),
                                               nw, sl);
             },
             py::arg("wavelet_phase_array"), py::keep_alive<1, 2>())
        .def("set_wavelet_complex_array",
             [](MorletWaveletTransformMP &self, ComplexArray arr) {
                 auto info = arr.request();
                 if (info.ndim != 2) {
                     throw std::invalid_argument(
                         "wavelet_complex_array must be 2-D");
                 }
                 std::size_t nw = static_cast<std::size_t>(info.shape[0]);
                 std::size_t sl = static_cast<std::size_t>(info.shape[1]);
                 self.set_wavelet_complex_array(
                     static_cast<std::complex<double> *>(info.ptr), nw, sl);
             },
             py::arg("wavelet_complex_array"), py::keep_alive<1, 2>())
        .def("set_output_type", &MorletWaveletTransformMP::set_output_type,
             py::arg("output_type"))
        .def("initialize_signal_props",
             &MorletWaveletTransformMP::initialize_signal_props,
             py::arg("sample_freq"))
        .def("initialize_wavelet_props",
             [](MorletWaveletTransformMP &self, std::size_t width,
                DoubleArray freqs, bool complete) {
                 std::size_t nf = 0;
                 double *fp = dptr(freqs, nf);
                 self.initialize_wavelet_props(width, fp, nf, complete);
             },
             py::arg("width"), py::arg("freqs"), py::arg("complete") = true,
             py::keep_alive<1, 3>())
        .def("prepare_run", &MorletWaveletTransformMP::prepare_run)
        .def("compute_wavelets_worker_fcn",
             &MorletWaveletTransformMP::compute_wavelets_worker_fcn,
             py::arg("thread_no"))
        .def("compute_wavelets_threads",
             &MorletWaveletTransformMP::compute_wavelets_threads,
             py::call_guard<py::gil_scoped_release>())
        .def("index", &MorletWaveletTransformMP::index,
             py::arg("i"), py::arg("j"), py::arg("stride"));
}
