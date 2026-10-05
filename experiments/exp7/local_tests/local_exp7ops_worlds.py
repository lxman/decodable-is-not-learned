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

    def test_retired_world_apis_refuse_before_effects(self):
        from pathlib import Path
        import tempfile
        from exp7ops.worlds import full_worlds, exercise_world_protocol
        from exp7ops.evidence import Refusal
        calls = []
        class Adapter:
            def __getattr__(self, name):
                calls.append(name)
                raise AssertionError('retired fixture used: ' + name)
        def recipe(*args):
            calls.append('recipe')
            raise AssertionError('retired recipe constructed')
        with tempfile.TemporaryDirectory() as temporary:
            for name, invoke, replacement in (
                ('full_worlds', lambda root: full_worlds(Adapter(), root), 'full_worlds'),
                ('exercise_world_protocol', lambda root: exercise_world_protocol(Adapter(), root, recipe_factory=recipe), 'exercise'),
            ):
                with self.subTest(api=name):
                    root = Path(temporary) / name
                    with self.assertRaisesRegex(Refusal, '^exp7ops\\.worlds\\.' + name +
                                                ' is retired; use exp7integration\\.world_harness\\.' + replacement + '$'):
                        invoke(root)
                    self.assertEqual(calls, [])
                    self.assertFalse(root.exists())
                    self.assertFalse((root / 'worlds-receipt.json').exists())
            self.assertEqual(list(Path(temporary).iterdir()), [])
