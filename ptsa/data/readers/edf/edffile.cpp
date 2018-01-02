#include <exception>
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

    inline int handle() {
        return this->header.handle;
    }

    inline void seek(int channel, long long offset)
    {
        const auto new_offset = edfseek(this->handle(), channel, offset, EDFSEEK_SET);
        if (new_offset != offset) {
            throw std::runtime_error(
                "edfseek returned " + std::to_string(new_offset)
                + " when expected " + std::to_string(offset)
            );
        }
    }

public:
    /**
     * Open an EDF file for reading.
     * @param filename
     * @throws std::runtime_error when the EDF file cannot be opened
     */
    EDFFile(std::string filename)
    {
        auto res = edfopen_file_readonly(filename.c_str(), &this->header, EDFLIB_DO_NOT_READ_ANNOTATIONS);
        if (res != 0)
        {
            // We're not going to try to catch each specific type of error, but
            // just the most likely to be seen. More helpful error messages can
            // be added in the future if need be.
            const auto code = this->header.filetype;
            if (code == EDFLIB_NO_SUCH_FILE_OR_DIRECTORY)
            {
                const auto msg = "No such file or directory: " + filename;
                throw std::runtime_error(msg);
            }
            else if (code == EDFLIB_FILE_CONTAINS_FORMAT_ERRORS)
            {
                throw std::runtime_error("EDF file contains format errors");
            }
            else if (code == EDFLIB_FILE_READ_ERROR)
            {
                throw std::runtime_error("Error reading EDF file " + filename);
            }
            else
            {
                const auto msg = "Unhandled error reading EDF file (code " + std::to_string(code) + ")";
                throw std::runtime_error(msg);
            }
        }
    }

    ~EDFFile() {
        this->close();
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
     * @throws std::runtime_error when an error occurs
     */
    py::array_t<int> read_samples(int channel, int n_samples, long long offset)
    {
        auto output = py::array_t<int, py::array::c_style | py::array::forcecast>(n_samples);
        auto info = output.request();
        this->seek(channel, offset);
        auto samples = edfread_digital_samples(
            this->header.handle, channel, n_samples, static_cast<int *>(info.ptr)
        );
        if (samples < 0) {
            throw std::runtime_error("Error reading EDF samples!");
        }

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

    py::class_<EDFFile>(m, "EDFFile")
        .def(py::init<const std::string &>())
        .def("__enter__", [](EDFFile &self) {
            return self;  // FIXME: this doesn't seem to work...
        })
        .def("__exit__", [](EDFFile &self, py::object type, py::object value, py::object tb) {
            self.close();
        })
        .def_property_readonly("num_channels", &EDFFile::get_num_channels)
        .def_property_readonly("num_samples", [](EDFFile &self) {
            return self.get_num_samples(0);
        })
        .def("close", &EDFFile::close)
        .def("read_samples", &EDFFile::read_samples,
             py::arg("channel"), py::arg("samples"), py::arg("offset") = 0)
    ;
}
