#include <exception>
#include <string>

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>

#include "edflib.h"

namespace py = pybind11;

using ChannelInfo = struct edf_param_struct;

// Stolen from: https://stackoverflow.com/questions/25829143/trim-whitespace-from-a-string
std::string &rtrim(std::string &str)
{
    auto it1 =  std::find_if(str.rbegin(), str.rend(), [](char ch) {
        return !std::isspace<char>(ch, std::locale::classic());
    });
    str.erase(it1.base(), str.end());
    return str;
}


/**
 * Wrapper used to read EDF files via EDFLib.
 */
class EDFFile
{
private:
    struct edf_hdr_struct header;

    /// Keeps track of whether or not the file is open
    bool opened{ false };

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

    /**
     * Open an EDF file.
     * @param filename
     */
    void open(std::string filename)
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
        else
        {
            this->opened = true;
        }
    }

    /**
     * Call to check that the file is opened. Throws an exception if not.
     */
    inline void ensure_open()
    {
        if (!this->opened) {
            throw std::runtime_error("EDF file is not opened!");
        }
    }

public:
    /**
     * Open an EDF file for reading.
     * @param filename
     * @throws std::runtime_error when the EDF file cannot be opened
     */
    EDFFile(std::string filename) {
        this->open(filename);
    }

    ~EDFFile()
    {
        if (this->opened) {
            this->close();
        }
    }

    /**
     * Close the EDF file.
     */
    void close()
    {
        if (edfclose_file(this->handle() < 0)) {
            throw std::runtime_error("Error closing EDF file!");
        }
        else {
            this->opened = false;
        }
    }

    /**
     * Return the number of channels.
     */
    inline int get_num_channels()
    {
        return this->header.edfsignals;
    }

    /**
     * Return channel metadata.
     * @param channel
     * @throws py::index_error when the channel index is out of range
     */
    inline ChannelInfo get_channel_info(int channel)
    {
        ensure_open();
        if (channel >= this->header.edfsignals)
        {
            const auto msg = "Channl " + std::to_string(channel) + " out of range";
            throw py::index_error(msg);
        }
        return this->header.signalparam[channel];
    }

    /**
     * Return the number of samples. It is generally assumed that all channels
     * will contain the same number of samples, but you can also specify a
     * specific channel.
     * @param channel - channel number
     */
    inline long long get_num_samples(int channel)
    {
        ensure_open();
        return this->header.signalparam[channel].smp_in_file;
    }

    inline long long get_num_samples()
    {
        ensure_open();
        return this->get_num_samples(0);
    }

    inline long long get_num_annotations()
    {
        ensure_open();
        return this->header.annotations_in_file;
    }

    /**
     * Get a single annotation.
     * @param index
     */
    struct edf_annotation_struct get_annotation(int index)
    {
        ensure_open();
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
     * @param channels - the channels to read from
     * @param n_samples - number of samples to read
     * @param offset - sample counter offset to start from
     * @return data vector
     * @throws std::runtime_error when an error occurs
     */
    py::array_t<int> read_samples(std::vector<int> channels, int n_samples, long long offset)
    {
        ensure_open();

        const std::vector<ssize_t> shape = {{static_cast<long>(channels.size()), n_samples}};
        auto output = py::array_t<int>(shape);
        auto info = output.request();

        for (const auto &channel: channels)
        {
            auto buffer = py::array_t<int>(shape[1]);
            this->seek(channel, offset);
            const auto samples = edfread_digital_samples(
                this->handle(), channel, n_samples, static_cast<int *>(buffer.request().ptr)
            );

            if (samples < 0) {
                throw std::runtime_error("Error reading EDF samples!");
            }

            for (ssize_t i = 0; i < shape[1]; ++i) {
                output.mutable_unchecked()(channel, i) = *buffer.data(i);
            }
        }

        return output;
    }
};


PYBIND11_MODULE(edffile, m)
{
    py::class_<struct edf_annotation_struct>(m, "EDFAnnotation", R"(An EDF annotation)")
        .def_readonly("onset", &edf_annotation_struct::onset)
        .def_readonly("duration", &edf_annotation_struct::duration)
        .def_readonly("annotation", &edf_annotation_struct::annotation)
    ;

    py::class_<ChannelInfo>(m, "ChannelInfo", R"(
    Channel data including label, number of samples, etc. These objects are
    returned by :meth:`EDFFile.get_channel_info`.

    )")
        .def(py::init<>())
        .def_property_readonly("label", [](const ChannelInfo &self) {
            auto label = std::string(self.label);
            return rtrim(label);
        })
        .def_readonly("smp_in_file", &ChannelInfo::smp_in_file)
        .def_readonly("phys_max", &ChannelInfo::phys_max)
        .def_readonly("phys_min", &ChannelInfo::phys_min)
        .def_readonly("dig_max", &ChannelInfo::dig_max)
        .def_readonly("dig_min", &ChannelInfo::dig_min)
        .def_readonly("smp_in_datarecord", &ChannelInfo::smp_in_datarecord)
        .def_readonly("physdimension", &ChannelInfo::physdimension)
        .def_readonly("prefilter", &ChannelInfo::prefilter)
        .def_readonly("transducer", &ChannelInfo::transducer)
        .def("__str__", [](const ChannelInfo &self) {
            auto label = std::string(self.label);
            return "<channel label=" + rtrim(label) + ">";
        })
    ;

    py::class_<EDFFile>(m, "EDFFile", R"(Read the EDF-family of files.

    Parameters
    ----------
    filename : str
        Path to EDF file.

    Notes
    -----
    This class utilizes EDFlib_ to read EDF/BDF/EDF+/BDF+ files.

    .. _EDFlib: https://www.teuniz.net/edflib/

    )")
        .def(py::init<const std::string &>())
        // .def("__enter__", [](EDFFile &self) {
        //     return self;  // FIXME: this doesn't seem to work...
        // })
        // .def("__exit__", [](EDFFile &self, py::object type, py::object value, py::object tb) {
        //     self.close();
        // })
        .def_property_readonly("num_channels", &EDFFile::get_num_channels)
        .def_property_readonly("num_samples", [](EDFFile &self) {
            return self.get_num_samples(0);
        })
        .def_property_readonly("num_annotations", &EDFFile::get_num_annotations)
        .def("get_channel_info", &EDFFile::get_channel_info)
        .def("close", &EDFFile::close)
        .def("read_samples", &EDFFile::read_samples,
             py::arg("channel"), py::arg("samples"), py::arg("offset") = 0)
    ;
}
