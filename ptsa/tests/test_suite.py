__author__ = 'm'

import unittest
from test_event_read import TestEventRead
from test_eeg_read import TestEEGRead
# from test_wavelet import test_morlet_multi

if __name__=='__main__':
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestEventRead))
    test_suite.addTest(unittest.makeSuite(TestEEGRead))

    # test_suite.addTest(unittest.makeSuite(test_morlet_multi))

    runner=unittest.TextTestRunner()
    runner.run(test_suite)