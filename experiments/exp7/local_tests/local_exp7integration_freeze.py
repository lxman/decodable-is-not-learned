# Test-only dependency slice; origin in LOCAL-TEST-MAP.json.
from pathlib import Path
import tempfile
import unittest
from exp7ops.evidence import once
from testing_paths import PACKAGE, WORK
from exp7integration.freeze import deterministic_twice

class FreezeBindingTests(unittest.TestCase):

    def test_determinism_controller_uses_two_fixed_guarded_workers(self):
        with tempfile.TemporaryDirectory(dir=WORK) as tmp:
            root = Path(tmp)
            calls = []

            class Process:

                def run(self, argv, **kw):
                    calls.append((argv, kw))
                    once(Path(argv[-1]), b'{"synthetic-report":"identical"}\n')
            receipt = deterministic_twice(Process(), python='/fixed/python', package=PACKAGE, fixture=root / 'export.json', fixture_sha256='1' * 64, output=root / 'results')
            self.assertEqual(receipt['invocations'], 2)
            self.assertEqual(len(calls), 2)
            self.assertTrue(all((c[0][1:3] == ['-I', '-B'] and '--fixture-sha256' in c[0] and (c[1]['shell'] is False) for c in calls)))
