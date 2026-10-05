# Test-only dependency slice; origin in LOCAL-TEST-MAP.json.
import unittest

class Baselines(unittest.TestCase):

    def test_contract(self):
        from exp7core.certified.baselines import METHODS, FAMILIES, nonapplicable, predict
        self.assertEqual(len(METHODS), 21)
        self.assertEqual(sum((nonapplicable(m, f) is None for m in METHODS for f in FAMILIES)), 49)
        self.assertEqual(sum((nonapplicable(m, f) is not None for m in METHODS for f in FAMILIES)), 35)
        self.assertEqual(predict('position2', 'units', 'q\nOptions: 1, 2, 3, 4, 5', None), '2')
