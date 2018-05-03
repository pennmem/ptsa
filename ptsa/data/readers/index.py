import copy
import json
import os
import warnings

import pandas as pd

from ptsa.data.common import pathlib
from six import string_types

__all__ = [
    'JsonIndexReader',
]


class JsonIndexReader(object):
    """
    Reads from one of the top level indexing files (r1.json, ltp.json)
    Allows for aggregation of values across any field with any constraint through the use of aggregateValues() or the
    specific methods subject(), experiment(), session() or montage().
    """
    warnings.warn("Lab-specific readers may be moved to the cmlreaders package "
                  "(https://github.com/pennmem/cmlreaders)",
                  PendingDeprecationWarning)
    FIELD_KEYS = (('protocols', '{protocol}'),
                  ('subjects', '{subject}'),
                  ('experiments', '{experiment}'),
                  ('sessions', '{session}'),)

    FIELD_NAMES = ('protocol','subject','experiment','session')

    def __init__(self, index_file):
        """
        Constructor.
        Reads from the passed in index file, and appends the root of the index files to anything that
        appears to be a path
        :param protocols: 'r1', 'ltp'
        """
        self.protocols_root = os.path.dirname(index_file)
        self.index_file = index_file
        with open(index_file, 'r') as infile:
            self.index = json.loads(infile.read())
        self._prepend_db_root(self.protocols_root, self.index)

    def as_dataframe(self, multiindex=True):
        """Flatten the index and format as a pandas :class:`DataFrame`. The
        returned :class:`DataFrame` uses a MultiIndex consisting of subject,
        experiment, session.

        Parameters
        ----------
        multiindex : bool
            Set the :class:`pd.DataFrame` index to be a :class:`MultiIndex`
            using subject, experiment, and session (default: True).

        Returns
        -------
        df : pd.DataFrame

        """
        protocol = os.path.splitext(os.path.basename(self.index_file))[0]
        subjects = self.index["protocols"][protocol]["subjects"]
        entries = []

        for subject in subjects:
            experiments = subjects[subject]["experiments"]
            for experiment in experiments:
                sessions = experiments[experiment]["sessions"]
                for session in sessions:
                    entry = sessions[session]
                    entry["subject"] = subject
                    entry["experiment"] = experiment
                    entry["session"] = int(session)
                    entries.append(entry)

        df = pd.DataFrame(entries)
        if multiindex:
            df.set_index(["subject", "experiment", "session"], inplace=True)

        return df

    @classmethod
    def _prepend_db_root(cls, protocols_root, index):
        """
        Prepends the protocols_root onto elements of index that contain the basename of protocols_root and look
        like paths.
        """
        protocols_basename = os.path.basename(protocols_root)
        for k, v in list(index.items()):
            if isinstance(v, dict):
                cls._prepend_db_root(protocols_root, v)
            elif isinstance(v, string_types):
                v_path = pathlib.Path(str(v))
                root = str(v_path.parts[0])
                if root == protocols_basename:
                    index[k] = os.path.join(protocols_root, str(v_path.parts[1:]))


    @classmethod
    def _merge(cls, index1, index2):
        """
        Merges two dictionaries
        """
        merged = index1
        for k, v in list(index2.items()):
            if k not in merged:
                merged[k] = v
            elif isinstance(v, dict):
                merged[k] = cls._merge(merged[k], v)
            else:
                merged[k] += v
        return merged

    @classmethod
    def _prune(cls, *indexes):
        """
        Removes branches of dictionary tree with no values
        :param indexes: dictionary tree
        :return: None
        """
        for index in indexes:
            for k in list(index.keys()):
                if not isinstance(index[k], dict):
                    continue
                cls._prune(index[k])
                if len(index[k]) == 0:
                    del index[k]

    @classmethod
    def _filter(cls, *indexes, **kwargs):
        """
        Filters a tree of dictionaries by some kwargs
        :param indexes: tree of dictionaries
        :param kwargs: filters
        :return: None
        """
        orig_indexes = indexes
        for f_k, f_v in cls.FIELD_KEYS:
            if len(indexes) == 0:
                break
            if f_k not in indexes[0]:
                continue
            try:
                v = f_v.format(**kwargs)
                for index in indexes:
                    if v not in index[f_k]:
                        del index[f_k]
                    else:
                        for k in list(index[f_k].keys()):
                            if k != v:
                                del index[f_k][k]
            except KeyError:
                pass
            indxs = []
            for indx in indexes:
                if len(indx) > 0:
                    indxs.extend(list(indx[f_k].values()))
            indexes = indxs # Recurse on the level of the index

        # Post: 'protocol','subject','experiment','session' are not in kwargs.keys()

        for kwarg_f, kwarg_v in kwargs.items():
            if len(indexes) == 0:
                break
            for index in indexes:
                try:
                    if str(index[kwarg_f]) != str(kwarg_v):
                        index.clear()
                except KeyError:
                    if kwarg_f in cls.FIELD_NAMES:
                        continue
                    else:
                        index.clear()
        cls._prune(*orig_indexes)

    @classmethod
    def _aggregate_values(cls, index, field, **kwargs):
        these_indexes = [copy.deepcopy(index)]
        cls._filter(*these_indexes, **kwargs)
        sub_indexes = {}
        is_leaf = True
        for key, value in cls.FIELD_KEYS:
            if not these_indexes or not key in these_indexes[0]:
                continue
            sub_indexes = [indx[key] for indx in these_indexes]
            if key == field:
                is_leaf=False
                break
            try:
                value = value.format(**kwargs)
                these_indexes = [indx[value] for indx in sub_indexes]
            except KeyError:
                new_indexes = []
                for indx in sub_indexes:
                    new_indexes.extend(list(indx.values()))
                these_indexes = new_indexes
        out = set()
        if not is_leaf:
            for index_i in sub_indexes:
                out.update(set(index_i.keys()))
        else:
            for index_i in these_indexes:
                if field in index_i:
                    out.add(index_i[field])
        return out

    def get_value(self, field, **kwargs):
        """
        Gets a single field from the dictionary tree. Raises a KeyError if the field is not found, or there
        are multiple entries for the field with the specified constraints
        :param field: the name of the field to retrieve
        :param kwargs: constraints (e.g. subject='R1001P', session=0, experiment='FR3')
        :return: the value requested
        """
        values = self._aggregate_values(self.index, field, **kwargs)
        if len(values) != 1:
            raise ValueError("Expected 1 value for {}, found {}".format(field, len(values)))
        return list(values)[0]

    def aggregate_values(self, field, **kwargs):
        """
        Aggregates values across different experiments, subjects, sessions, etc.
        Allows you to specify constraints for the query (e.g. subject='R1001P', experiment='FR1')
        :param field: The field to aggregate -- can be a leaf or internal node of the json tree.
        :param kwargs: Constraints -- subject='R1001P', experiment='FR1', etc.
        :return: a set of all of the fields that were found
        """
        return self._aggregate_values(self.index, field, **kwargs)

    def subjects(self, **kwargs):
        """
        Requests a list of subjects, filtered by kwargs
        :param kwargs: e.g. experiment='FR1', session=0
        :return: list of subjects
        """
        return sorted(list(self.aggregate_values( 'subjects', **kwargs)))

    def experiments(self, **kwargs):
        """
        Requests a list of experiments, filtered by kwargs
        :param kwargs: e.g. subject='R1001P', localization=1
        :return: list of experiments
        """
        return sorted(list(self.aggregate_values('experiments', **kwargs)))

    def sessions(self, **kwargs):
        """
        Requests a list of session numbers, filtered by kwargs
        :param kwargs: e.g. subject='R1001P', experiment='FR3'
        :return: list of sessions
        """
        return sorted(list(self.aggregate_values('sessions', **kwargs)))

    def montages(self, **kwargs):
        """
        Returns a list of the montage codes (#.#), filtered by kwargs
        :param kwargs: e.g. subject='R1001P', experiment='FR1', session=0
        :return: list of montages
        """
        return sorted(list(self.aggregate_values('montage', **kwargs)))
