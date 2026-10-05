import guard
from pathlib import Path
import tempfile
import unittest
from exp7ops.mutation import run_mutants
from exp7ops.mutants import MUTANTS
from exp7ops.evidence import snapshot, strict, Refusal

class MutationTests(unittest.TestCase):
    def test_copy_outside_approved_scratch_is_refused(self):
        with self.assertRaises(Refusal):
            run_mutants(Path(__file__).parent, Path("/tmp/exp7-forbidden-copy"), [], lambda *a: {})

    def test_full_list_targets_unique_existing_core_spans(self):
        root = Path(__file__).resolve().parents[1]
        self.assertGreaterEqual(len(MUTANTS), 25)
        for mutant in MUTANTS:
            data = (root / mutant["file"]).read_text()
            with self.subTest(mutant=mutant["id"]):
                self.assertEqual(data.count(mutant["old"]), 1)
                compile(data.replace(mutant["old"], mutant["new"], 1), mutant["file"], "exec")

    def test_one_harmless_fixture_mutant_restores_all_bytes_and_logs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "original"; source.mkdir()
            (source / "fixture.py").write_text("def value():\n    return 1\n")
            original = snapshot(source)
            seen = []
            def evaluate(copy, task):
                ns = {}
                exec(compile((copy / "fixture.py").read_bytes(), str(copy / "fixture.py"), "exec"), ns)
                value = ns["value"]()
                seen.append(value)
                failed = int(value != 1)
                return {"tests": 1, "failures": failed, "errors": 0, "returncode": failed}
            mutant = {"id": "harmless", "file": "fixture.py", "old": "return 1", "new": "return 2", "task": "fixture"}
            result = run_mutants(source, root / "run", [mutant], evaluate)
            self.assertEqual(seen, [1, 2, 1])
            self.assertEqual(result[0]["status"], "KILLED")
            self.assertEqual(snapshot(source), original)
            self.assertEqual(snapshot(root / "run/copy"), original)
            self.assertEqual(len(list((root / "run/logs").glob("*.json"))), 5)

    def test_interruption_restores_before_reraising(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); source = root / "original"; source.mkdir()
            (source / "fixture.py").write_text("value = 1\n")
            calls = []
            def evaluate(copy, task):
                calls.append((copy / "fixture.py").read_text())
                if len(calls) == 2:
                    raise KeyboardInterrupt("fixture interruption")
                return {"tests": 1, "failures": 0, "errors": 0, "returncode": 0}
            mutant = {"id": "interrupt", "file": "fixture.py", "old": "value = 1", "new": "value = 2", "task": "fixture"}
            with self.assertRaises(KeyboardInterrupt):
                run_mutants(source, root / "run", [mutant], evaluate)
            self.assertEqual(calls, ["value = 1\n", "value = 2\n", "value = 1\n"])
            self.assertEqual(strict((root / "run/logs/interrupt.result.json").read_bytes())["status"], "INTERRUPTED")
