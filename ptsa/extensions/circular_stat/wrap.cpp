// pybind11 bindings for the circular-statistics C++ kernels.
//
// Replaces circular_stat.i + vendored numpy.i. The Python surface matches
// what SWIG produced -- every ``(ptr, size)`` pair on the C++ side becomes a
// single numpy array on the Python side, and ``cdiff`` / ``cdiff_means`` /
// ``ppcs`` etc. are still in-place output buffers.
#include <complex>
#include <cstddef>
#include <stdexcept>

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/complex.h>

#include "circular_stat.h"

namespace py = pybind11;

namespace {

using DoubleArray = py::array_t<double, py::array::c_style | py::array::forcecast>;
using ComplexArray =
    py::array_t<std::complex<double>, py::array::c_style | py::array::forcecast>;
using BoolArray = py::array_t<bool, py::array::c_style | py::array::forcecast>;

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

inline bool *bptr(BoolArray &a, std::size_t &n) {
    auto info = a.request();
    n = static_cast<std::size_t>(info.size);
    return static_cast<bool *>(info.ptr);
}

}  // namespace

PYBIND11_MODULE(_circular_stat, m) {
    m.doc() = "Circular-statistics kernels (pybind11 bindings).";

    m.def("circ_diff",
          [](ComplexArray c1, ComplexArray c2, ComplexArray cdiff) {
              std::size_t n1 = 0, n2 = 0, n3 = 0;
              auto *p1 = cptr(c1, n1);
              auto *p2 = cptr(c2, n2);
              auto *pd = cptr(cdiff, n3);
              circ_diff(p1, n1, p2, n2, pd, n3);
          },
          py::arg("c1"), py::arg("c2"), py::arg("cdiff"));

    m.def("circ_diff_par",
          [](ComplexArray c1, ComplexArray c2, ComplexArray cdiff,
             std::size_t n_threads) {
              std::size_t n1 = 0, n2 = 0, n3 = 0;
              auto *p1 = cptr(c1, n1);
              auto *p2 = cptr(c2, n2);
              auto *pd = cptr(cdiff, n3);
              circ_diff_par(p1, n1, p2, n2, pd, n3, n_threads);
          },
          py::arg("c1"), py::arg("c2"), py::arg("cdiff"), py::arg("n_threads"));

    m.def("resultant_vector",
          [](ComplexArray c) {
              std::size_t n = 0;
              auto *p = cptr(c, n);
              return resultant_vector(p, n);
          },
          py::arg("c"));

    m.def("resultant_vector_length",
          [](ComplexArray c) {
              std::size_t n = 0;
              auto *p = cptr(c, n);
              return resultant_vector_length(p, n);
          },
          py::arg("c"));

    m.def("circ_mean",
          [](ComplexArray c) {
              std::size_t n = 0;
              auto *p = cptr(c, n);
              return circ_mean(p, n);
          },
          py::arg("c"));

    m.def("circ_diff_time_bins",
          [](ComplexArray c1, ComplexArray c2, ComplexArray cdiff,
             ComplexArray cdiff_means) {
              std::size_t n1 = 0, n2 = 0, n3 = 0, n_bins = 0;
              auto *p1 = cptr(c1, n1);
              auto *p2 = cptr(c2, n2);
              auto *pd = cptr(cdiff, n3);
              auto *pm = cptr(cdiff_means, n_bins);
              circ_diff_time_bins(p1, n1, p2, n2, pd, n3, pm, n_bins);
          },
          py::arg("c1"), py::arg("c2"), py::arg("cdiff"),
          py::arg("cdiff_means"));

    m.def("compute_f_stat",
          [](ComplexArray phase_diff_mat, BoolArray recalls,
             DoubleArray f_stat_mat) {
              std::size_t n_pd = 0, n_ev = 0, n_fs = 0;
              auto *ppd = cptr(phase_diff_mat, n_pd);
              auto *prec = bptr(recalls, n_ev);
              auto *pfs = dptr(f_stat_mat, n_fs);
              compute_f_stat(ppd, n_pd, prec, n_ev, pfs, n_fs);
          },
          py::arg("phase_diff_mat"), py::arg("recalls"),
          py::arg("f_stat_mat"));

    m.def("compute_zscores",
          [](DoubleArray mat, std::size_t n_perms) {
              std::size_t n = 0;
              auto *p = dptr(mat, n);
              compute_zscores(p, n, n_perms);
          },
          py::arg("mat"), py::arg("n_perms"));

    m.def("single_trial_ppc_all_features",
          [](BoolArray recalls, ComplexArray wavelets, DoubleArray ppc_output,
             ComplexArray theta_sum_recalls,
             ComplexArray theta_sum_non_recalls,
             std::size_t n_freqs, std::size_t n_bps, std::size_t n_threads) {
              std::size_t n_ev = 0, n_w = 0, n_ppc = 0, n_tsr = 0, n_tsnr = 0;
              auto *prec = bptr(recalls, n_ev);
              auto *pw = cptr(wavelets, n_w);
              auto *pppc = dptr(ppc_output, n_ppc);
              auto *ptsr = cptr(theta_sum_recalls, n_tsr);
              auto *ptsnr = cptr(theta_sum_non_recalls, n_tsnr);
              single_trial_ppc_all_features(prec, n_ev, pw, n_w, pppc, n_ppc,
                                             ptsr, n_tsr, ptsnr, n_tsnr,
                                             n_freqs, n_bps, n_threads);
          },
          py::arg("recalls"), py::arg("wavelets"), py::arg("ppc_output"),
          py::arg("theta_sum_recalls"), py::arg("theta_sum_non_recalls"),
          py::arg("n_freqs"), py::arg("n_bps"), py::arg("n_threads"));

    m.def("single_trial_outsample_ppc_features",
          [](ComplexArray wavelets, ComplexArray theta_avg_recalls,
             ComplexArray theta_avg_non_recalls,
             DoubleArray outsample_ppc_features,
             std::size_t n_freqs, std::size_t n_bps, std::size_t n_threads) {
              std::size_t n_w = 0, n_tar = 0, n_tanr = 0, n_out = 0;
              auto *pw = cptr(wavelets, n_w);
              auto *ptar = cptr(theta_avg_recalls, n_tar);
              auto *ptanr = cptr(theta_avg_non_recalls, n_tanr);
              auto *pout = dptr(outsample_ppc_features, n_out);
              single_trial_outsample_ppc_features(pw, n_w, ptar, n_tar,
                                                   ptanr, n_tanr, pout, n_out,
                                                   n_freqs, n_bps, n_threads);
          },
          py::arg("wavelets"), py::arg("theta_avg_recalls"),
          py::arg("theta_avg_non_recalls"),
          py::arg("outsample_ppc_features"),
          py::arg("n_freqs"), py::arg("n_bps"), py::arg("n_threads"));
}
