from ptsa.data.readers import LocReader
import os.path as osp
import pandas as pd

class TestLocReader:

    @classmethod
    def setup_class(cls):
        loc_file = osp.join(osp.dirname(__file__), 'data', 'localization.json')
        cls.localization =         LocReader(filename=loc_file).read()


    def test_split(self):
        contacts = self.localization.loc['contacts']
        pairs =    self.localization.loc['pairs']

    def test_types(self):
        contacts = self.localization.loc['contacts']
        assert pd.isnull(contacts['type']).sum() == 0

        pairs = self.localization.loc['pairs']
        assert pd.isnull(pairs['type']).sum() == 0
