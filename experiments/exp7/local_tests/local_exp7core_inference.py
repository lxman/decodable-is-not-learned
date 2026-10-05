# Test-only dependency slice; origin in LOCAL-TEST-MAP.json.
import unittest
from fractions import Fraction as F
from exp7core.inference import somers

class InferenceTests(unittest.TestCase):

    def test_pool_counts_before_family_mean(self):
        r = somers((0, 1, 0, 1, 2), (0, 1, 2, 1, 0), (0, 0, 1, 1, 1))
        self.assertEqual(r['D'], F(-1, 2))
