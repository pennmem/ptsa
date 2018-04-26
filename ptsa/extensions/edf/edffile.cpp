#include "edffile.hpp"


void EDFFile::open(std::string filename)
{
    auto res = edfopen_file_readonly(filename.c_str(), &this->header, EDFLIB_DO_NOT_READ_ANNOTATIONS);
    if (res != 0) {
        // We're not going to try to catch each specific type of error, but
        // just the most likely to be seen. More helpful error messages can
        // be added in the future if need be.
        const auto code = this->header.filetype;
        if (code == EDFLIB_NO_SUCH_FILE_OR_DIRECTORY) {
            const auto msg = "No such file or directory: " + filename;
            throw std::runtime_error(msg);
        }
        else if (code == EDFLIB_FILE_CONTAINS_FORMAT_ERRORS) {
            throw std::runtime_error("EDF file contains format errors");
        }
        else if (code == EDFLIB_FILE_READ_ERROR) {
            throw std::runtime_error("Error reading EDF file " + filename);
        }
        else {
            const auto msg = "Unhandled error reading EDF file (code " + std::to_string(code) + ")";
            throw std::runtime_error(msg);
        }
    }
    else {
        this->opened = true;
    }
}


EDFFile::EDFFile(std::string filename)
{
    this->open(filename);
}


EDFFile::~EDFFile()
{
    if (this->opened) {
        this->close();
    }
}


void EDFFile::close()
{
    if (edfclose_file(this->handle() < 0)) {
        throw std::runtime_error("Error closing EDF file!");
    }
    else {
        this->opened = false;
    }
}


ChannelInfo EDFFile::get_channel_info(int channel)
{
    ensure_open();
    if (channel >= this->header.edfsignals) {
        const auto msg = "Channel " + std::to_string(channel) + " out of range";
        throw py::index_error(msg);
    }
    return this->header.signalparam[channel];
}


struct edf_annotation_struct EDFFile::get_annotation(int index)
{
    ensure_open();
    struct edf_annotation_struct annotation;
    edf_get_annotation(this->header.handle, index, &annotation);
    return annotation;
}


void EDFFile::seek(int channel, long long offset)
{
    const auto new_offset = edfseek(this->handle(), channel, offset, EDFSEEK_SET);
    if (new_offset != offset && new_offset != -1) {
        throw std::runtime_error(
            "edfseek returned " + std::to_string(new_offset)
            + " when expected " + std::to_string(offset)
        );
    }
}


std::vector<int> EDFFile::get_channel_numbers(std::vector<std::string> channel_names)
{
    std::vector<int> channel_numbers;
    for (const std::string &name: channel_names) {
        for(int c = 0; c < this->get_num_channels(); c++) {
            auto info = this->get_channel_info(c);
            std::string label = info.label;
            if(label.compare(0, name.size(), name) == 0) {
                channel_numbers.push_back(c);
                break;
            }
        }
    }

    if(channel_numbers.size() == channel_names.size()) {
        return channel_numbers;
    }
    else {
        throw std::runtime_error("Bad channel name");
    }
}


py::array_t<double> EDFFile::read_samples(std::vector<int> channels, int n_samples, long long offset)
{
    ensure_open();

    const std::vector<ssize_t> shape = {{static_cast<long>(channels.size()), n_samples}};
    auto output = py::array_t<double>(shape);
    auto info = output.request();

    for (ssize_t j = 0; j<shape[0]; ++j)
    {
        auto channel = channels[j];
        auto buffer = py::array_t<double>(shape[1]);
        this->seek(channel, offset);
        const auto samples = edfread_physical_samples(
            this->handle(), channel, n_samples, static_cast<double *>(buffer.request().ptr)
        );

        if (samples < 0) {
            throw std::runtime_error("Error reading EDF samples!");
        }

        for (ssize_t i = 0; i < shape[1]; ++i) {
            output.mutable_unchecked()(j, i) = *buffer.data(i);
        }
    }

    return output;
}


py::array_t<double> EDFFile::read_samples(std::vector<std::string> channel_names,
                                          int n_samples, long long offset)
{
    ensure_open();
    auto numbers = get_channel_numbers(channel_names);
    return read_samples(numbers, n_samples, offset);
}
