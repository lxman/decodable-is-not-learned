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

    def test_exact_rational_report_checksums_and_protocol_receipt(self):
        from hashlib import sha256
        import json
        from pathlib import Path
        import tempfile
        from exp7ops.worlds import exercise_world_protocol

        class EncodingOnlyAdapter:
            """Fake report port, not the production adapter; no statistics run.

            False for every poison deliberately isolates WORLDS-1 encoding.
            WORLDS-2's real late-fault accounting remains separately deferred.
            """

            def __init__(self, value):
                self.report = {'report': {'primary': {'pythia_1b': {
                    'mean_x': value,
                    'nested': [Fraction(-2, 7), (Fraction(5, 11), None)],
                }}}, 'statistics_executed': False}
                self.installs = 0
                self.calls = 0
                self.poison_cases = []

            def install(self, root, recipe):
                self.expected = recipe['expected']
                self.used = False
                self.poisoned = False
                self.installs += 1
                (root / 'synthetic-input.txt').write_bytes(b'encoding-only fixture\n')

            def poison(self, root, case):
                self.poisoned = True
                self.poison_cases.append(case)
                (root / 'synthetic-input.txt').write_text(case)

            def scientific_inputs(self, root):
                return {'synthetic-input.txt': (root / 'synthetic-input.txt').read_bytes()}

            def claimed(self, root):
                return self.used

            def analyze(self, root):
                # A fake callback with no scientific driver or calculation.
                self.refused = self.used or self.poisoned
                self.used = True
                self.calls += 1
                return self.report

            def summarize(self, report):
                return {
                    'states': dict.fromkeys(self.expected, 'INSUFFICIENT_DATA')
                    if self.refused else dict(self.expected),
                    'secondaries': list(range(1, 9)),
                    'licence': 'does not identify an internal algorithm',
                    'statistics_executed': False,
                }

        def recipe(left, right):
            return {'expected': {'pythia_1b': left, 'olmo2_1b': right}}

        # Independent exact bytes, including a pair that collapses under float().
        variants = (
            (Fraction(1, 3), b'{"denominator":3,"numerator":1}'),
            (Fraction(2, 6), b'{"denominator":3,"numerator":1}'),
            (Fraction(1, 3), b'{"denominator":3,"numerator":1}'),
            (Fraction(1, 1), b'{"denominator":1,"numerator":1}'),
            (Fraction(9007199254740993, 9007199254740992),
             b'{"denominator":9007199254740992,"numerator":9007199254740993}'),
        )
        self.assertNotEqual(variants[3][0], variants[4][0])
        self.assertEqual(float(variants[3][0]), float(variants[4][0]))
        cases = [[left, right] for left in STATES[:4] for right in STATES[:4]]
        cases.append(['UNDETERMINED', 'UNDETERMINED'])
        saved_receipts, report_hashes = [], []
        with tempfile.TemporaryDirectory() as temporary:
            for index, (value, exact_value) in enumerate(variants):
                root = Path(temporary) / f'encoding-{index}'
                adapter = EncodingOnlyAdapter(value)
                exact_report = (
                    b'{"report":{"primary":{"pythia_1b":{"mean_x":' + exact_value
                    + b',"nested":[{"denominator":7,"numerator":-2},'
                    b'[{"denominator":11,"numerator":5},null]]}}},"statistics_executed":false}\n'
                )
                expected_hash = sha256(exact_report).hexdigest()
                records = exercise_world_protocol(adapter, root, recipe_factory=recipe)
                from exp7stats.common import dumps
                self.assertEqual(dumps(adapter.report), exact_report)
                expected_records = [
                    {'case': case, 'report_sha256': expected_hash} for case in cases
                ] + [{'poison': case, 'state': 'INSUFFICIENT_DATA'} for case in POISONS]
                self.assertEqual(records, expected_records)
                payload = (root / 'worlds-receipt.json').read_bytes()
                expected_payload = (json.dumps(expected_records, sort_keys=True,
                                               separators=(',', ':')) + '\n').encode()
                self.assertEqual(payload, expected_payload)
                self.assertEqual(json.loads(payload), expected_records)
                self.assertEqual(adapter.installs, len(cases) + len(POISONS))
                self.assertEqual(adapter.calls, 2 * len(cases) + len(POISONS))
                self.assertEqual(adapter.poison_cases, list(POISONS))
                saved_receipts.append(payload)
                report_hashes.append(expected_hash)
        self.assertEqual(saved_receipts[0], saved_receipts[1])  # equivalent fractions
        self.assertEqual(saved_receipts[0], saved_receipts[2])  # repeatability
        self.assertEqual(report_hashes[0], report_hashes[1])
        self.assertNotEqual(report_hashes[3], report_hashes[4])  # exact, not float
        self.assertNotEqual(saved_receipts[3], saved_receipts[4])
