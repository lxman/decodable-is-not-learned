# Test-only dependency slice; origin in LOCAL-TEST-MAP.json.
import unittest
from fractions import Fraction as F
from exp7core.simulations import expected_x

class MiniatureSimulationTests(unittest.TestCase):

    def test_support_attenuation(self):
        self.assertEqual(expected_x(0, 1, F(1, 5), 64), 0)
        self.assertEqual(expected_x(1, 1, F(1, 5), 64), F(1, 5))
        self.assertEqual(expected_x(F(1, 2), F(1, 2), F(1, 5), 1), F(1, 20))
