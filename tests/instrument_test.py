import unittest, configparser
from datetime import date, timedelta
from context import instrument as ins

class InstrumentTest(unittest.TestCase):
    def testGet(self):
        si=ins.getSplits(date(2020, 1, 1), date(2020, 1, 1), splits=1)
        self.assertEqual(len(si), 1)
        self.assertEqual(si[0][0], date(2020, 1, 1))
        self.assertEqual(si[0][1], date(2020, 1, 1))

        si=ins.getSplits(date(2020, 1, 1), date(2020, 1, 5), splits=1)
        self.assertEqual(len(si), 1)
        self.assertEqual(si[0][0], date(2020, 1, 1))
        self.assertEqual(si[0][1], date(2020, 1, 5))

        si=ins.getSplits(date(2020, 1, 1), date(2020, 1, 5), splits=10)
        self.assertEqual(len(si), 5)
        for i,(s,e) in enumerate(si):
            self.assertEqual(s, date(2020, 1, 1) + timedelta(days=i))
            self.assertEqual(e, date(2020, 1, 1) + timedelta(days=i))

        si=ins.getSplits(date(2020, 1, 1), date(2020, 1, 2), splits=3)
        self.assertEqual(len(si), 2)
        self.assertEqual(si[0][0], date(2020, 1, 1))
        self.assertEqual(si[0][1], date(2020, 1, 1))
        self.assertEqual(si[1][0], date(2020, 1, 2))
        self.assertEqual(si[1][1], date(2020, 1, 2))

if __name__ == '__main__':
    unittest.main()
