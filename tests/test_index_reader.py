import os.path as osp
import pytest
from ptsa.data.readers.IndexReader import JsonIndexReader


@pytest.fixture
def reader():
    here = osp.abspath(osp.dirname(__file__))
    path = osp.join(here, 'data', 'r1.json')
    return JsonIndexReader(path)


class TestJsonIndexReader:
    def test_aggregate_values(self, reader):
        vals = reader.aggregate_values('experiments', subject='R1111M')
        assert vals == {'FR1', 'FR2', 'PAL1', 'PAL2', 'PS2', 'catFR1'}

    def test_subjects(self, reader):
        assert len(reader.subjects()) == 256

    def test_experiments(self, reader):
        assert len(reader.experiments()) == 20

    def test_sessions(self, reader):
        sessions = [int(n) for n in reader.sessions(subject="R1111M", experiment="FR1")]
        assert sessions == list(range(4))

    def test_montages(self, reader):
        assert len(reader.montages(subject='R1286J')) == 1
