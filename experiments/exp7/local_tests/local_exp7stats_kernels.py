# Test-only dependency slice; origin in LOCAL-TEST-MAP.json.
from fractions import Fraction as F
import unittest
from exp7stats.kernels import decision

class KernelTests(unittest.TestCase):

    def test_early_decision_is_exact_and_does_not_fake_p(self):
        self.assertTrue(decision(50, 50, 10000)['nonreject'])
        self.assertFalse(decision(49, 50, 10000)['nonreject'])
        self.assertTrue(decision(0, 9951, 10000)['reject'])
        self.assertIsNone(decision(0, 9951, 10000)['p'])
        self.assertFalse(decision(0, 9950, 10000)['reject'])
        self.assertEqual(decision(49, 10000, 10000)['p'], F(50, 10001))
