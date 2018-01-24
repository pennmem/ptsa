from .base import BaseReader
import json, itertools
import pandas as pd


class LocReader(BaseReader):
    """
    Reads a localization file ("localization.json") and returns the data it contains as a flat DataFrame.
    Nested fields in the JSON file have their full paths joined by periods.
    The returned DataFrame is indexed by tyep type of entry ('contacts' or 'pairs') and by the name of the entry
    (either the name of the contact, or a tuple with the names of each half of the pair).
    """

    def __init__(self,filename):
        with open(filename) as f:
            self._dict = json.load(f)

    def read(self):
        leads = self._dict["leads"].values()
        for lead in leads:
            contacts = lead["contacts"]
            if isinstance(contacts,dict):
                contacts = contacts.values()
            for c in contacts:
                c.update({"type":lead["type"],})
            pairs = lead["pairs"]
            if isinstance(pairs,dict):
                pairs = pairs.values()
            for p in pairs:
                p['names'] = tuple(p['names'])
                p.update({"type":lead["type"]})
        flat_contact_data = list(itertools.chain(*[x["contacts"] for x in leads]))
        flat_pairs_data = list(itertools.chain(*[x["pairs"] for x in leads]))
        all_data = []
        all_data.append(pd.io.json.json_normalize(flat_contact_data).set_index('name'))
        all_data.append(pd.io.json.json_normalize(flat_pairs_data).set_index('names'))
        self._data = all_data
        combined_df = pd.concat(all_data,keys=['contacts','pairs'],)
        return combined_df
