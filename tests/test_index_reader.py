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

    @pytest.mark.parametrize('multi', [True, False])
    def test_as_dataframe(self, reader, multi):
        df = reader.as_dataframe(multiindex=multi)

        if multi:
            assert df.index.levels[0].name == 'subject'
            assert len(df.index.levels[0]) == 256

            assert df.index.levels[1].name == 'experiment'
            assert len(df.index.levels[1]) == 20

            assert df.index.levels[2].name == 'session'
            assert len(df.index.levels[2]) == 13

            sessions = df.loc['R1111M', 'FR1']
            assert len(sessions) == 4
        else:
            assert len(df[(df.subject == 'R1111M') & (df.experiment == 'FR1')]) == 4
