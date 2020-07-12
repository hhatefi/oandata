import unittest

import factory_test
import instrument_test

loader=unittest.TestLoader()
suite=unittest.TestSuite()

suite.addTest(loader.loadTestsFromModule(factory_test))
suite.addTest(loader.loadTestsFromModule(instrument_test))

runner=unittest.TextTestRunner(verbosity=3)
result=runner.run(suite)
