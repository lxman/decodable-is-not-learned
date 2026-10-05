from pathlib import Path
import tempfile
import unittest
from exp7ops.evidence import canonical, digest, once, Refusal
from exp7integration.mutation_specs import validate_targets, MUTANTS
from testing_paths import PACKAGE, WORK
from task_registry import TASKS
from exp7integration.freeze import deterministic_twice


class FreezeBindingTests(unittest.TestCase):
    def test_every_mutation_targets_one_compilable_final_source_span(self):
        rows = validate_targets(PACKAGE, TASKS)
        self.assertEqual(len(rows), len(MUTANTS))
        self.assertGreaterEqual(len(rows), 40)
        self.assertEqual(len({row["id"] for row in rows}), len(rows))

    def test_determinism_controller_uses_two_fixed_guarded_workers(self):
        with tempfile.TemporaryDirectory(dir=WORK) as tmp:
            root = Path(tmp); calls = []
            class Process:
                def run(self, argv, **kw):
                    calls.append((argv, kw))
                    once(Path(argv[-1]), b'{"synthetic-report":"identical"}\n')
            receipt = deterministic_twice(Process(), python="/fixed/python", package=PACKAGE,
                fixture=root/"export.json", fixture_sha256="1"*64, output=root/"results")
            self.assertEqual(receipt["invocations"], 2)
            self.assertEqual(len(calls), 2)
            self.assertTrue(all(c[0][1:3] == ["-I", "-B"] and "--fixture-sha256" in c[0] and c[1]["shell"] is False for c in calls))
