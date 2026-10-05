# Test-only dependency slice; origin in LOCAL-TEST-MAP.json.
import unittest

class Data(unittest.TestCase):

    def test_contract(self):
        from exp7stats.data import baseline_score, Pair, Baseline
        from exp7core.contract import Refusal
        pair = Pair('words:0000', 0, ('alpha', 'beta'), 'word', 'base', (), ())
        score = baseline_score(pair, Baseline('APPLICABLE', None, ('alpha', 'beta', 'alpha', 'beta'), (False,) * 4))
        self.assertEqual(score.x, 1)
        abstain = baseline_score(pair, Baseline('APPLICABLE', None, ('',) * 4, (True,) * 4))
        self.assertEqual(abstain.x, 0)
