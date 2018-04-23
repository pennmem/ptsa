#pragma once

#include <exception>
#include <locale>
#include <string>

#include <pybind11/numpy.h>
#include <pybind11/stl.h>

#include "edflib.h"

namespace py = pybind11;

using ChannelInfo = struct edf_param_struct;


/**
 * Wrapper used to read EDF files via EDFLib.
 */
class EDFFile {
private:
    struct edf_hdr_struct header;

    /// Keeps track of whether or not the file is open
    bool opened{ false };

    inline int handle() {
        return this->header.handle;
    }

    void seek(int channel, long long offset);

    /**
     * Open an EDF file.
     * @param filename
     */
    void open(std::string filename);

    /**
     * Call to check that the file is opened. Throws an exception if not.
     */
    inline void ensure_open() {
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
    EDFFile(std::string filename);

    ~EDFFile();

    /**
     * Close the EDF file.
     */
    void close();

    /**
     * Return the number of channels.
     */
    inline int get_num_channels() {
        return this->header.edfsignals;
    }

    /**
     * @brief Get channel numbers from a list of names.
     * @param channel_names
     */
    std::vector<int> get_channel_numbers(std::vector<std::string> channel_names);

    /**
     * Return channel metadata.
     * @param channel
     * @throws py::index_error when the channel index is out of range
     */
    ChannelInfo get_channel_info(int channel);

    /**
     * Return the number of samples. It is generally assumed that all channels
     * will contain the same number of samples, but you can also specify a
     * specific channel.
     * @param channel - channel number
     */
    inline long long get_num_samples(int channel) {
        ensure_open();
        return this->header.signalparam[channel].smp_in_file;
    }

    /**
     * Return the sampling rate of the recording. It is generally assumed that all channels
     * will be recorded at the same sampling rate, but you can also specify a
     * specific channel.
     * @param channel - channel number
     **/
    inline auto get_samplerate(int channel) {
        if (channel >= this->header.edfsignals) {
            const auto msg = "Channel " + std::to_string(channel) + " out of range";
            throw py::index_error(msg);
        }
        return (static_cast<double>(this->header.signalparam[channel].smp_in_datarecord) / static_cast<double>(this->header.datarecord_duration)) * EDFLIB_TIME_DIMENSION;
    }

    inline long long get_num_samples() {
        ensure_open();
        return this->get_num_samples(0);
    }

    inline long long get_num_annotations() {
        ensure_open();
        return this->header.annotations_in_file;
    }

    /**
     * Get a single annotation.
     * @param index
     */
    struct edf_annotation_struct get_annotation(int index);

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
     * Read raw samples from a list of channels.
     * @param channels - the channels to read from
     * @param n_samples - number of samples to read
     * @param offset - sample counter offset to start from
     * @return data vector
     * @throws std::runtime_error when an error occurs
     */
    py::array_t<double> read_samples(std::vector<int> channels, int n_samples, long long offset);

    /**
     * @brief Read raw samples from a list of channel names
     * @param channel_names vector of channel names to read
     * @param n_samples number of samples to read
     * @param offset sample counter offset to start from
     * @return data array
     */
    py::array_t<double> read_samples(std::vector<std::string> channel_names, int n_samples, long long offset);
};
