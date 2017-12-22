#include <string>

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>

#include "edffile.hpp"

namespace py = pybind11;
using namespace edf;

/**
 * Convenience class for accesssing EDF annotations.
 */
class EDFAnnotations
{
private:
    std::shared_ptr<EDFFile> edf;
    int cur_index;

public:
    EDFAnnotations(const EDFFile &edf) {
        this->edf = std::make_shared<EDFFile>(edf);
    }

    auto get_annotation(int index) -> struct edf_annotation_struct
    {
        struct edf_annotation_struct annotation;
        edf_get_annotation(this->edf->get_handle(), index, &annotation);
        return annotation;
    }

    void iter() {
        this->cur_index = -1;
    }

    auto next() {
        this->cur_index++;
        if (this->cur_index >= this->edf->get_num_annotations()) {
            throw py::stop_iteration();
        }
        return this->get_annotation(this->cur_index);
    }
};


PYBIND11_MODULE(edffile, m)
{
    py::class_<struct edf_annotation_struct>(m, "EDFAnnotation")
        .def_property_readonly("onset", [](const edf_annotation_struct &self) {
            return self.onset;
        })
        .def_property_readonly("duration", [](const edf_annotation_struct &self) {
            return self.duration;
        })
        .def_property_readonly("annotation", [](const edf_annotation_struct &self) {
            return self.annotation;
        })
    ;

    py::class_<EDFAnnotations>(m, "EDFAnnotations")
        .def(py::init<const EDFFile &>())
        .def("__iter__", [](EDFAnnotations &self) {
            self.iter();
            return self;
        })
        .def("__next__", &EDFAnnotations::next)
    ;

    py::class_<EDFFile>(m, "EDFFile")
        .def(py::init<const std::string &>())
        .def("__enter__", [](EDFFile &self) {
            return self;
        })
        .def("__exit__", [](EDFFile &self, py::object type, py::object value,
                            py::object tb) {
            self.close();
        })
        .def_property_readonly("num_channels", &EDFFile::get_num_channels)
        .def_property_readonly("num_samples", [](EDFFile &self) {
            return self.get_num_samples(0);
        })
        .def("get_all_annotations", &EDFFile::get_all_annotations)
        .def_property_readonly("annotations", [](EDFFile &self) {
            return EDFAnnotations(self);
        })
        .def("read_samples",
             py::overload_cast<std::vector<int>, int, long long>(&EDFFile::read_samples))
        .def("read_samples",
             py::overload_cast<int, int, long long>(&EDFFile::read_samples))
    ;
}
