from os.path import *

def read_events(e_path, reader_class, **kwds):
    base_e_reader = reader_class(filename=e_path, eliminate_events_with_no_eeg=True, **kwds)
    base_events = base_e_reader.read()
    return base_events


def e_path_matlab(prefix, subject, task):
    """Returns path to matlab RAM events  """
    return join(prefix, 'data/events/%s/%s_events.mat' % (task, subject))


def e_path_matlab_scalp(prefix, subject, task):
    """Returns path to matlab RAM events  """

    return join(prefix, 'data/scalp_events/%s/%s_events.mat' % (task, subject))


def e_path_json(prefix, subject, task):
    """Returns prefix for data location"""
    return join(prefix, 'protocols/r1/subjects/%s/experiments/%s/sessions/0/behavioral/current_processed'
                        '/task_events.json' % (subject, task))
