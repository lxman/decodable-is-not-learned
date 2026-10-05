# Test-only dependency slice; origin in LOCAL-TEST-MAP.json.
import unittest
import tempfile
from pathlib import Path

class WorldHarness(unittest.TestCase):

    def test_contract(self):
        from exp7integration.world_harness import exercise, LATE_FAULTS
        from exp7ops.worlds import STATES, POISONS
        from exp7ops.evidence import Refusal

        class Fixture:

            def __init__(self, lie=False):
                self.lie = lie
                self.rows = {}
                self.restored = False

            def install(self, root, recipe):
                self.rows[root] = {'recipe': recipe, 'calls': 0}

            def scientific_inputs(self, root):
                return b'unchanged fabricated evidence'

            def poison(self, root, poison):
                self.rows[root]['poison'] = poison

            def analyze(self, root):
                row = self.rows[root]
                row['calls'] += 1
                p = row.get('poison')
                bad = p is not None or row['calls'] > 1
                return {'states': {'a': 'INSUFFICIENT_DATA'} if bad else row['recipe']['expected'], 'statistics_executed': (False if self.lie else p in LATE_FAULTS) if p else row['calls'] == 1, 'secondaries': list(range(1, 9)), 'licence': 'does not identify an internal algorithm'}

            def summarize(self, report):
                return report

            def claimed(self, root):
                return True

            def success_published(self, root):
                return 'poison' not in self.rows[root]

            def restore_sources(self):
                self.restored = True
        recipe = lambda a, b: {'expected': {'a': a, 'b': b}}
        with tempfile.TemporaryDirectory() as tmp:
            fixture = Fixture()
            rows = exercise(fixture, Path(tmp) / 'ok', recipe_factory=recipe)
            self.assertEqual(len(rows), 17 + len(POISONS))
            self.assertTrue(fixture.restored)
            self.assertEqual({r['poison'] for r in rows if r.get('statistics_executed')}, set(LATE_FAULTS))
            liar = Fixture(True)
            with self.assertRaises(Refusal):
                exercise(liar, Path(tmp) / 'bad', recipe_factory=recipe)
            self.assertTrue(liar.restored)

    def test_exact_rational_report_checksums_and_protocol_receipt(self):
        from fractions import Fraction
        from hashlib import sha256
        import json
        from exp7integration.world_harness import exercise
        from exp7ops.worlds import STATES, POISONS

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
        # Independent I4 oracle, not the harness's LATE_FAULTS constant.
        late = {'entry-only-pin', 'HALTED-before-final'}
        receipts, hashes = [], []
        with tempfile.TemporaryDirectory() as tmp:
            for index, (value, exact_value) in enumerate(variants):
                root = Path(tmp) / f'rational-{index}'
                fixture = _ReportFixture({'mean_x': value, 'nested': [
                    Fraction(-2, 7), (Fraction(5, 11), None)]})
                # These expected bytes do not use either production serializer.
                exact_report = (
                    b'{"report":{"primary":{"pythia_1b":{"mean_x":' + exact_value
                    + b',"nested":[{"denominator":7,"numerator":-2},'
                    b'[{"denominator":11,"numerator":5},null]]}}},"statistics_executed":true}\n'
                )
                expected_hash = sha256(exact_report).hexdigest()
                try:
                    records = exercise(fixture, root, recipe_factory=_recipe)
                finally:
                    # Also checks cleanup when the original encoder raises.
                    self.assertEqual(fixture.restores, 1)
                from exp7stats.common import dumps
                self.assertEqual(dumps(fixture.first_report), exact_report)
                self.assertIsInstance(fixture.first_report['report']['primary']['pythia_1b']['mean_x'], Fraction)
                expected_records = [
                    {'case': case, 'report_sha256': expected_hash} for case in cases
                ] + [{'poison': poison, 'state': 'INSUFFICIENT_DATA',
                      'statistics_executed': poison in late} for poison in POISONS]
                self.assertEqual(records, expected_records)
                self.assertEqual({r['poison'] for r in records if r.get('statistics_executed')}, late)
                payload = (root / 'worlds-receipt.json').read_bytes()
                expected_payload = (json.dumps(expected_records, sort_keys=True,
                                               separators=(',', ':')) + '\n').encode()
                self.assertEqual(payload, expected_payload)
                self.assertEqual(json.loads(payload), expected_records)
                self.assertEqual(len(fixture.rows), 17 + len(POISONS))
                self.assertEqual(sum(row['calls'] for row in fixture.rows.values()),
                                 34 + len(POISONS))
                self.assertEqual(fixture.poison_cases, list(POISONS))
                for target, row in fixture.rows.items():
                    poison = row.get('poison')
                    expected_input = poison.encode() if poison else b'fake protocol input\n'
                    self.assertEqual(fixture.scientific_inputs(target), expected_input)
                    self.assertTrue(fixture.claimed(target))
                    self.assertEqual(fixture.success_published(target), poison is None)
                    self.assertEqual(row['calls'], 1 if poison else 2)
                receipts.append(payload)
                hashes.append(expected_hash)
        self.assertEqual(receipts[0], receipts[1])  # equivalent fractions
        self.assertEqual(receipts[0], receipts[2])  # repeatability
        self.assertEqual(hashes[0], hashes[1])
        self.assertNotEqual(hashes[3], hashes[4])  # unequal exact, equal float
        self.assertNotEqual(receipts[3], receipts[4])

    def test_truthful_phase_refusals_and_callback_cleanup(self):
        from exp7integration.world_harness import exercise
        from exp7ops.evidence import Refusal

        with tempfile.TemporaryDirectory() as tmp:
            # Both late faults must report computation; early faults must not.
            for poison in ('entry-only-pin', 'HALTED-before-final', 'missing-sham'):
                with self.subTest(poison=poison):
                    root = Path(tmp) / poison
                    fixture = _ReportFixture({'mean_x': 0}, phase_lie=poison)
                    try:
                        with self.assertRaisesRegex(Refusal, 'incorrect phase accounting: ' + poison):
                            exercise(fixture, root, recipe_factory=_recipe)
                    finally:
                        self.assertEqual(fixture.restores, 1)
                    self.assertEqual(fixture.poison_cases[-1], poison)
                    self.assertFalse((root / 'worlds-receipt.json').exists())
                    self.assertFalse(fixture.success_published(root / poison))
                    self.assertEqual(fixture.scientific_inputs(root / poison), poison.encode())
            root = Path(tmp) / 'callback-error'
            fixture = _ReportFixture({'mean_x': 0}, callback_error=True)
            try:
                with self.assertRaisesRegex(RuntimeError, 'fake analyze callback failed'):
                    exercise(fixture, root, recipe_factory=_recipe)
            finally:
                self.assertEqual(fixture.restores, 1)
            self.assertFalse((root / 'worlds-receipt.json').exists())


def _recipe(left, right):
    return {'expected': {'pythia_1b': left, 'olmo2_1b': right}}


class _ReportFixture:
    """Fake report port only: phase flags are simulated; no statistics execute."""

    def __init__(self, primary, *, phase_lie=None, callback_error=False):
        self.primary = primary
        self.phase_lie = phase_lie
        self.callback_error = callback_error
        self.rows = {}
        self.poison_cases = []
        self.restores = 0
        self.first_report = None

    def install(self, root, recipe):
        self.rows[root] = {'expected': recipe['expected'], 'calls': 0}
        (root / 'synthetic-input.txt').write_bytes(b'fake protocol input\n')

    def poison(self, root, poison):
        self.rows[root]['poison'] = poison
        self.poison_cases.append(poison)
        (root / 'synthetic-input.txt').write_bytes(poison.encode())

    def scientific_inputs(self, root):
        return (root / 'synthetic-input.txt').read_bytes()

    def claimed(self, root):
        return self.rows[root]['calls'] > 0

    def success_published(self, root):
        return self.claimed(root) and 'poison' not in self.rows[root]

    def analyze(self, root):
        row = self.rows[root]
        row['calls'] += 1
        if self.callback_error:
            raise RuntimeError('fake analyze callback failed')
        poison = row.get('poison')
        refused = poison is not None or row['calls'] > 1
        executed = poison in ('entry-only-pin', 'HALTED-before-final') if poison else row['calls'] == 1
        if poison is not None and poison == self.phase_lie:
            executed = not executed
        self.states = dict.fromkeys(row['expected'], 'INSUFFICIENT_DATA') if refused else row['expected']
        report = {'report': {'primary': {'pythia_1b': self.primary}},
                  'statistics_executed': executed}
        if self.first_report is None:
            self.first_report = report
        return report

    def summarize(self, report):
        return {'states': self.states, 'secondaries': list(range(1, 9)),
                'licence': 'does not identify an internal algorithm',
                'statistics_executed': report['statistics_executed']}

    def restore_sources(self):
        self.restores += 1
