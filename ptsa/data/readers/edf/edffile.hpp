#pragma once

#include <iostream>
#include <memory>
#include <string>
#include <vector>

#include "edflib.h"

namespace edf {

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

    ~EDFFile()
    {
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
    std::vector<struct edf_annotation_struct> get_all_annotations()
    {
        const auto n_annotations = this->header.annotations_in_file;
        std::vector<struct edf_annotation_struct> annotations(n_annotations);

        for (int i = 0; i < n_annotations; ++i)
        {
            struct edf_annotation_struct annotation;
            edf_get_annotation(this->header.handle, i, &annotation);
            annotations.push_back(annotation);
        }

        return annotations;
    }

    /**
     * Read raw samples.
     * @param channels - the channels to read from
     * @param n_samples - number of samples to read
     * @param offset - sample counter offset to start from
     * @return (number of channels) x (number of samples) vector
     */
    std::vector< std::vector<int> > read_samples(std::vector<int> channels, int n_samples, long long offset=0)
    {
        std::vector< std::vector<int> > output;

        for (auto chan: channels)
        {
            edfrewind(this->header.handle, chan);
            std::vector<int> samples(n_samples);
            auto res = edfread_digital_samples(this->header.handle, chan, n_samples, &samples[0]);
            output.push_back(samples);
        }

        return output;
    }

    /**
     * Read raw samples from a single channel.
     * @param channel - the channel to read from
     * @param n_samples - number of samples to read
     * @param offset - sample counter offset to start from
     * @return data vector
     */
    std::vector<int> read_samples(int channel, int n_samples, long long offset=0)
    {
        std::vector<int> channels = { channel };
        return this->read_samples(channels, n_samples, offset)[0];
    }
};

}  // namespace edf
