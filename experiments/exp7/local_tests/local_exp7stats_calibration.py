# Test-only dependency slice; origin in LOCAL-TEST-MAP.json.
from fractions import Fraction as F
import unittest
from exp7stats.calibration import exact_binomial_tail

class SimulationContractTests(unittest.TestCase):

    def test_exact_binomial_tail_hand_enumeration(self):
        self.assertEqual(exact_binomial_tail(3, 4, F(1, 2)), F(5, 16))
        self.assertEqual(exact_binomial_tail(0, 4, F(1, 200)), 1)
