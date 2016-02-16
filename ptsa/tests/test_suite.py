__author__ = 'm'

import unittest
from test_readers import TestReaders
from ptsa_regression.TestRegressionPTSA import TestRegressionPTSA

if __name__=='__main__':
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestReaders))
    test_suite.addTest(unittest.makeSuite(TestRegressionPTSA))

    runner=unittest.TextTestRunner(verbosity=2)
    runner.run(test_suite)



