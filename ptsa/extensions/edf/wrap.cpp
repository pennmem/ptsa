#include <pybind11/pybind11.h>
#include "edffile.hpp"

namespace py = pybind11;


// Stolen from: https://stackoverflow.com/questions/25829143/trim-whitespace-from-a-string
std::string &rtrim(std::string &str)
{
    auto it1 =  std::find_if(str.rbegin(), str.rend(), [](char ch) {
        return !std::isspace<char>(ch, std::locale::classic());
    });
    str.erase(it1.base(), str.end());
    return str;
}


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
        .def("get_channel_numbers", &EDFFile::get_channel_numbers)
        .def("read_samples",
             py::overload_cast<std::vector<int>, int, long long>(&EDFFile::read_samples),
             "Read samples from a list of channel numbers",
             py::arg("channels"), py::arg("samples"), py::arg("offset") = 0)
        .def("read_samples",
             py::overload_cast<std::vector<std::string>, int, long long>(&EDFFile::read_samples),
             "Read samples from a list of channel names",
             py::arg("channels"), py::arg("samples"), py::arg("offset") = 0)
        .def("get_samplerate", &EDFFile::get_samplerate, py::arg("channel"))
    ;
}
