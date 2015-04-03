import sys
sys.path[0:0] = ['.', '..']

import unittest


suite = unittest.TestLoader().loadTestsFromNames(
    [
        'test_if',
        'test_call',
        'test_while',
        'test_general',
        'test_dvfs_generator'
    ]
)

testresult = unittest.TextTestRunner(verbosity=2).run(suite)
sys.exit(0 if testresult.wasSuccessful() else 1)


