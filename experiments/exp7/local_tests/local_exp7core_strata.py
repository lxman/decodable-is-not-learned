# Test-only dependency slice; origin in LOCAL-TEST-MAP.json.
import unittest
from fractions import Fraction as F
from exp7core.strata import availability_buckets

class StrataTests(unittest.TestCase):

    def test_median_tie_blocks_and_constant(self):
        s, report = availability_buckets(('a',) * 6, tuple(map(F, [0, 0, 0, 0, 1, 1])))
        self.assertEqual([v[1] for v in s], [0, 0, 0, 0, 1, 1])
        self.assertEqual(report[0]['sizes'], {0: 4, 1: 2})
        s, _ = availability_buckets(('a',) * 5, (F(0),) * 5, parts=3)
        self.assertEqual(len(set(s)), 1)
