# Test-only dependency slice; origin in LOCAL-TEST-MAP.json.
import unittest
from fractions import Fraction as F
from exp7core.resampling import interval, paired_difference

class WorldBootstrapTests(unittest.TestCase):

    def test_undefined_bootstrap_counted_and_paired(self):
        r = interval([F(0), None, F(1)])
        self.assertEqual(r['undefined'], 1)
        self.assertEqual((r['low'], r['high']), (F(1, 40), F(39, 40)))
        r = paired_difference([F(1), None, F(3)], [F(0), F(8), None])
        self.assertEqual(r['defined'], 1)
        self.assertEqual(r['undefined'], 2)
