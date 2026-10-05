# Test-only dependency slice; origin in LOCAL-TEST-MAP.json.
import unittest
from types import SimpleNamespace as NS
from fractions import Fraction as F

class EnvelopeMath(unittest.TestCase):

    def test_contract(self):
        from exp7stats.envelope_math import envelope_record
        from exp7core.contract import Refusal
        pattern = ((F(0), F(0), F(1, 2)),) * 2
        value = envelope_record(0, pattern, 1, F(0), NS())
        self.assertEqual((value['status'], value['N'], value['p_fires']), ('ANALYTIC-ZERO-SUPPORT', 0, 0))
        with self.assertRaises(Refusal):
            envelope_record(0, pattern, 1, F(0), NS(), samples=['forged'])
