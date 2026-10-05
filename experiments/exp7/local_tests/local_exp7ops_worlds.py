# Test-only dependency slice; origin in LOCAL-TEST-MAP.json.
import unittest
from fractions import Fraction
from exp7ops.worlds import make_recipe, STATES, POISONS, GRID
from exp7core.scoring import score_draws, outcome_counts

class WorldProtocolTests(unittest.TestCase):

    def test_raw_recipes_have_correct_direction_constant_and_thin_support(self):
        for mode in STATES:
            recipe = make_recipe(mode, mode, pairs=21)
            for family, rows in recipe['families'].items():
                xs, ys = ([], [])
                for row in rows:
                    score = score_draws(row['trained']['pythia_1b'], row['targets'], 'word', k=64)
                    counts = outcome_counts({int(k): v for k, v in row['outputs'].items()}, row['targets'], 'word', steps=GRID)
                    xs.append(score.x)
                    ys.append(counts['y'])
                if mode == 'ORDER-ONLY':
                    self.assertEqual(sum(xs), 0)
                    self.assertEqual(xs, sorted(xs))
                elif mode == 'INPUT-SENSITIVE-FORECAST':
                    self.assertGreater(sum(xs) / len(xs), Fraction(1, 20))
                elif mode == 'SELECTIVE-ONLY':
                    self.assertEqual(set(xs), {1})
                elif mode == 'UNDETERMINED' and family in ('units', 'shapes'):
                    self.assertEqual(set(ys), {0})
        self.assertEqual(len(GRID), 26)
        self.assertGreaterEqual(len(POISONS), 20)
