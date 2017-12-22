#include <string>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>

#include "edflib.h"

namespace py = pybind11;


/**
 * Wrapper used to read EDF files via EDFLib.
 */
class EDFFile
{
private:
    struct edf_hdr_struct header;

public:
    /**
     * Open an EDF file for reading.
     * @param filename
     */
    EDFFile(std::string filename)
    {
        auto res = edfopen_file_readonly(filename.c_str(), &this->header, EDFLIB_DO_NOT_READ_ANNOTATIONS);
        if (res != 0) {
            std::cerr << "Got error code " << this->header.filetype << std::endl;
        }
    }

    ~EDFFile() {
        this->close();
    }

    int get_handle() {
        return this->header.handle;
    }

    /**
     * Close the EDF file.
     */
    void close() {
        edfclose_file(this->header.handle);
    }

    /**
     * Return the number of channels.
     */
    int get_num_channels()
    {
        return this->header.edfsignals;
    }

    /**
     * Return the number of samples. It is generally assumed that all channels
     * will contain the same number of samples, but you can also specify a
     * specific channel.
     * @param channel - channel number
     */
    long long get_num_samples(int channel)
    {
        return this->header.signalparam[channel].smp_in_file;
    }

    long long get_num_samples()
    {
        return this->get_num_samples(0);
    }

    long long get_num_annotations() {
        return this->header.annotations_in_file;
    }

    /**
     * Get a single annotation.
     * @param index
     */
    struct edf_annotation_struct get_annotation(int index)
    {
        struct edf_annotation_struct annotation;
        edf_get_annotation(this->header.handle, index, &annotation);
        return annotation;
    }

    /**
     * Read all annotation data.
     */
    // FIXME
    // std::vector<struct edf_annotation_struct> get_all_annotations()
    // {
    //     const auto n_annotations = this->header.annotations_in_file;
    //     std::vector<struct edf_annotation_struct> annotations(n_annotations);

    //     for (int i = 0; i < n_annotations; ++i)
    //     {
    //         struct edf_annotation_struct annotation;
    //         edf_get_annotation(this->header.handle, i, &annotation);
    //         annotations.push_back(annotation);
    //     }

    //     return annotations;
    // }

    /**
     * Read raw samples from a single channel.
     * @param channel - the channel to read from
     * @param n_samples - number of samples to read
     * @param offset - sample counter offset to start from
     * @return data vector
     */
    py::array_t<int> read_samples(int channel, int n_samples, long long offset=0)
    {
        auto output = py::array_t<int>(n_samples);
        edfrewind(this->header.handle, channel);
        edfread_digital_samples(this->header.handle, channel, n_samples, (int *)output.request().ptr);
        return output;
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

    // FIXME: fix or remove
    // py::class_<EDFAnnotations>(m, "EDFAnnotations")
    //     .def(py::init<const EDFFile &>())
    //     .def("__iter__", [](EDFAnnotations &self) {
    //         self.iter();
    //         return self;
    //     })
    //     .def("__next__", &EDFAnnotations::next)
    // ;

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
        .def("read_samples", &EDFFile::read_samples)
        // .def("read_samples",
        //      py::overload_cast<std::vector<int>, int, long long>(&EDFFile::read_samples))
        // .def("read_samples",
        //      py::overload_cast<int, int, long long>(&EDFFile::read_samples))
    ;
}
