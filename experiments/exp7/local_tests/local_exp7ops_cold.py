# Test-only dependency slice; origin in LOCAL-TEST-MAP.json.
from pathlib import Path
import tempfile
import unittest
from exp7ops.cold import cold_suite, deterministic_twice, INTEGRATION_TASKS
from exp7ops.evidence import Refusal

class WorldProtocolTests(unittest.TestCase):

    def test_retired_cold_apis_refuse_before_effects(self):
        with tempfile.TemporaryDirectory() as directory:
            calls = []
            def run(*args, **kwargs):
                calls.append((args, kwargs))
                raise AssertionError('retired callback invoked')
            class Process:
                def run(self, *args, **kwargs):
                    return run(*args, **kwargs)
            for synthetic in (False, True):
                for tasks in ((), ('G1',), INTEGRATION_TASKS):
                    with self.subTest(synthetic=synthetic, tasks=tasks):
                        output = Path(directory) / 'cold'
                        with self.assertRaisesRegex(Refusal, '^exp7ops\\.cold\\.cold_suite is retired; use run_task_tests\\.py --task with the installed registry$'):
                            cold_suite(run, output, synthetic=synthetic, integrated_tasks=tasks)
                        self.assertFalse(output.exists())
                        self.assertEqual(calls, [])
            output = Path(directory) / 'determinism'
            with self.assertRaisesRegex(Refusal, '^exp7ops\\.cold\\.deterministic_twice is retired; use exp7integration\\.freeze\\.deterministic_twice$'):
                deterministic_twice(Process(), python='/python', worker='/worker', fixture='/fixture', output=output)
            self.assertEqual(calls, [])
            self.assertFalse(output.exists())
            self.assertEqual(list(Path(directory).iterdir()), [])
