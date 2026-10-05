# Test-only dependency slice; origin in LOCAL-TEST-MAP.json.
import unittest
from fractions import Fraction as F

class Secondaries(unittest.TestCase):

    def test_contract(self):
        from exp7stats.secondaries import render_support
        from exp7core.scoring import Table
        value = render_support([Table(1, 0, 0, 1, 1), Table(0, 0, 0, 0, 1)])
        self.assertEqual(value, {'mean_d': F(1, 2), 'mean_u': F(1, 2), 'unsupported': 1, 'supported_only_mean_x': F(1)})
