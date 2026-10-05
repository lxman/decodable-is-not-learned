# Test-only dependency slice; origin in LOCAL-TEST-MAP.json.
import unittest
from fractions import Fraction as F
from exp7core.scoring import Table, Score

class ScoreTests(unittest.TestCase):

    def test_fixed_odds_counterexample(self):
        t = Table(18, 2, 9, 1, 100)
        s = Score(t, t)
        self.assertEqual(s.x, 0)
        self.assertEqual(s.d, F(1, 25))
        self.assertEqual(s.rate, (s.u + s.d) / 2)
