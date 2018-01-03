from .BaseReader import BaseReader
import json, itertools
import pandas as pd

class LocReader(BaseReader):

    def __init__(self,filename):
        with open(filename) as f:
            self._dict = json.load(f)

    def read(self):
        leads = self._dict["leads"].values()
        for lead in leads:
            for c in lead["contacts"].values():
                c.update(lead["lead_type"])
            for p in lead["pairs"].values():
                p.update(lead["lead_type"])
        flat_contact_data = list(itertools.chain(*[x["contacts"] for x in leads]))
        flat_pairs_data = list(itertools.chain(*[x["pairs"] for x in leads]))
        all_data = []
        all_data.append(pd.io.json.json_normalize(flat_contact_data))
        all_data.append(pd.io.json.json_normalize(flat_pairs_data))
        combined_df = pd.concat(all_data)
        return combined_df
