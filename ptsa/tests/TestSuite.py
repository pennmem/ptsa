__author__ = 'm'

import unittest
from TestReaders import TestReaders
from ptsa_regression.TestRegressionPTSA import TestRegressionPTSA
from TestFilters import TestFilters

if __name__=='__main__':
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestFilters))
    test_suite.addTest(unittest.makeSuite(TestReaders))
    test_suite.addTest(unittest.makeSuite(TestRegressionPTSA))

    runner=unittest.TextTestRunner(verbosity=2)
    runner.run(test_suite)



