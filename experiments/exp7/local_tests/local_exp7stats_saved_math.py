# Test-only dependency slice; origin in LOCAL-TEST-MAP.json.
import unittest
from fractions import Fraction as F

class SavedMath(unittest.TestCase):

    def test_contract(self):
        from exp7stats.saved_math import pack, unpack, scatter
        from exp7core.contract import Refusal
        raw = pack([0, 1, 255])
        self.assertEqual(list(unpack(raw, 3)), [0, 1, 255])
        with self.assertRaises(Refusal):
            unpack(raw, 2)
        with self.assertRaises(Refusal):
            unpack(raw + '00', 3)
        with self.assertRaises(Refusal):
            pack([256])
        result = scatter([F(1), F(-1), None])
        self.assertEqual((result['mean_defined'], result['population_variance'], result['undefined']), (0, 1, 1))
