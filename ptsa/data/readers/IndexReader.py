import os
import json
import copy
from ptsa.data.common import pathlib

class JsonIndexReader(object):
    """
    Reads from one of the top level indexing files (r1.json, ltp.json)
    Allows for aggregation of values across any field with any constraint through the use of aggregateValues() or the
    specific methods subject(), experiment(), session() or montage().
    """

    FIELDS = (('protocols', '{protocol}'),
              ('subjects', '{subject}'),
              ('experiments', '{experiment}'),
              ('sessions', '{session}'),)

    def __init__(self, index_file):
        """
        Constructor.
        Reads from the passed in index file, and appends the root of the index files to anything that
        appears to be a path
        :param protocols: 'r1', 'ltp'
        """
        self.protocols_root = os.path.dirname(index_file)
        self.index_file = index_file
        self.index = json.load(open(index_file))
        self._prepend_db_root(self.protocols_root, self.index)

    @classmethod
    def _prepend_db_root(cls, protocols_root, index):
        """
        Prepends the protocols_root onto elements of index that contain the basename of protocols_root and look
        like paths.
        """
        protocols_basename = os.path.basename(protocols_root)
        for k, v in index.items():
            if isinstance(v, dict):
                cls._prepend_db_root(protocols_root, v)
            elif isinstance(v, basestring):
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
        for k, v in index2.items():
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
            for k in index.keys():
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
        for f_k, f_v in cls.FIELDS:
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
                        for k in index[f_k].keys():
                            if k != v:
                                del index[f_k][k]
            except KeyError:
                pass
            indxs = []
            for indx in indexes:
                if len(indx) > 0:
                    indxs.extend(indx[f_k].values())
            indexes = indxs
        for kwarg_f, kwarg_v in kwargs.items():
            if kwarg_f in indexes[0]:
                for i, index in enumerate(indexes):
                    if str(index[kwarg_f]) != str(kwarg_v):
                        index.clear()
        cls._prune(*orig_indexes)

    @classmethod
    def _aggregate_values(cls, index, field, **kwargs):
        these_indexes = [copy.deepcopy(index)]
        cls._filter(*these_indexes, **kwargs)
        sub_indexes = {}
        is_leaf = True
        for key, value in cls.FIELDS:
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
                    new_indexes.extend(indx.values())
                these_indexes = new_indexes
        out = set()
        if not is_leaf:
            for index_i in sub_indexes:
                out.update(set(index_i.keys()))
        else:
            for index_i in these_indexes:
                out.add(index_i[field])
        return out

    def aggregate_values(self, field, **kwargs):
        """
        Aggregates values across different experiments, subjects, sessions, etc.
        Allows you to specify constraints for the query (e.g. subject='R1001P', experiment='FR1')
        :param field: The field to aggregate -- can be a leaf or internal node of the json tree.
        :param kwargs: Constraints -- subject='R1001P', experiment='FR1', etc.
        :return:
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
        localizations = self.aggregate_values('localization', **kwargs)
        montages = []
        for localization in localizations:
            for montage in self.aggregate_values('montage', localization=localization, **kwargs):
                montages.append('{}.{}'.format(localization, montage))
        return sorted(montages)

if __name__ == '__main__':
    reader = IndexReader('/Volumes/db_root/protocols/r1.json')
    print reader.aggregate_values('sessions', subject='R1093J', experiment='PS2')
    print reader.aggregate_values('subjects', experiment='FR3')
    print reader.aggregate_values('experiments', subject='R1001P')
    print reader.aggregate_values('task_events', subject='R1001P', experiment='FR1')
