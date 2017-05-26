__author__ = 'm'

import unittest
from test_eeg_readers import TestEEGReaders
from test_event_readers import TestEventReaders


if __name__=='__main__':
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestEEGReaders))
    test_suite.addTest(unittest.makeSuite(TestEventReaders))


    runner=unittest.TextTestRunner(verbosity=2)
    runner.run(test_suite)
