import os.path as osp
import json
import numpy as np
import pandas as pd

from ptsa.data.readers import BaseEventReader

here = osp.abspath(osp.dirname(__file__))



class TestBaseEventReader:
    @classmethod
    def setup_class(cls):
        cls.filename = osp.join(here, 'data', 'task_events.json')

    def test_read_json(self):
        ber = BaseEventReader(filename=self.filename)
        events = ber.read_json()
        assert isinstance(events, np.recarray)

        with open(self.filename) as f:
            assert len(events) == len(json.loads(f.read()))

    def test_as_dataframe(self):
        ber = BaseEventReader(filename=self.filename)
        events = ber.as_dataframe()
        assert isinstance(events, pd.DataFrame)

        with open(self.filename) as f:
            assert len(events) == len(json.loads(f.read()))
