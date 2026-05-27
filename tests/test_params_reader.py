"""Tests for ParamsReader — the EEG parameter-file reader.

ParamsReader supports three on-disk formats, all of which feed
samplerate + gain + data format into the binary EEG readers:

* ``params.txt`` — whitespace-delimited ``key value`` lines (legacy).
* ``sources.json`` — the modern per-dataroot JSON sidecar.
* ``<dataroot>.params`` — legacy per-channel params (parsed as JSON
  by the current dispatch; effectively unused on modern data).

Before this module, ParamsReader was only exercised *indirectly*
through BinaryRawReader on rhino. These tests cover the txt + json
parse paths directly (no rhino needed) plus one real-data sanity
check.
"""

import os.path as osp

import pytest

from ptsa.data.readers import ParamsReader
from tests.utils import get_rhino_root, skip_without_rhino

DATA = osp.join(osp.dirname(osp.abspath(__file__)), "data")


def test_params_txt():
    """params.txt: whitespace key/value lines → samplerate/gain/format."""
    path = osp.join(DATA, "params_fixtures", "txt", "params.txt")
    params = ParamsReader(filename=path).read()
    assert params["samplerate"] == 500.0
    assert params["gain"] == 2.5
    assert params["format"] == "int16"


def test_params_txt_defaults_gain_when_absent(tmp_path):
    """A params.txt without a gain line defaults gain to 1.0 (with a
    RuntimeWarning), but still requires samplerate."""
    p = tmp_path / "params.txt"
    p.write_text("samplerate 256.0\ndataformat int16\n")
    with pytest.warns(RuntimeWarning):
        params = ParamsReader(filename=str(p)).read()
    assert params["samplerate"] == 256.0
    assert params["gain"] == 1.0


def test_params_txt_missing_samplerate_raises(tmp_path):
    """samplerate is mandatory; its absence is an error."""
    p = tmp_path / "params.txt"
    p.write_text("gain 1.0\ndataformat int16\n")
    with pytest.raises(ValueError):
        ParamsReader(filename=str(p)).read()


def test_sources_json_via_dataroot():
    """sources.json: located next to a dataroot, keyed by its basename."""
    dataroot = osp.join(DATA, "params_fixtures", "json", "myeeg")
    params = ParamsReader(dataroot=dataroot).read()
    assert params["samplerate"] == 1000
    assert params["gain"] == 1
    assert params["format"] == "int16"
    assert params["dataformat"] == "int16"


def test_params_missing_file_raises():
    """A dataroot with no params file anywhere should raise IOError."""
    with pytest.raises(IOError):
        ParamsReader(dataroot="/nonexistent/path/to/eeg")


@skip_without_rhino
def test_sources_json_real_rhino():
    """Read a real sources.json sidecar from rhino and confirm it
    yields a positive samplerate and a recognized data format."""
    dataroot = osp.join(
        get_rhino_root(),
        "protocols/r1/subjects/R1234D/experiments/TH1/sessions/0/ephys/"
        "20161112.031150_processed/R1234D_TH1_0_17Oct16_1938",
    )
    params = ParamsReader(dataroot=dataroot).read()
    assert params["samplerate"] > 0
    assert params["format"] in (
        "int16", "int32", "float32", "float64", "single", "short", "double",
    )
