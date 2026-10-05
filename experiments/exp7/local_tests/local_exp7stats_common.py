# Test-only dependency slice; origin in LOCAL-TEST-MAP.json.
import unittest
from fractions import Fraction as F

class Common(unittest.TestCase):

    def test_contract(self):
        from exp7stats.common import encode, decode, receipt, Refusal
        self.assertEqual(decode(encode({'ratio': F(2, 3)})), {'ratio': F(2, 3)})
        self.assertEqual(receipt({'sha': 'a' * 64}, 'sha'), {'sha': 'a' * 64})
        with self.assertRaises(Refusal):
            receipt({'sha': 'a' * 64, 'pass': True}, 'sha')
        with self.assertRaises(Refusal):
            decode({'numerator': 1, 'denominator': 0})
