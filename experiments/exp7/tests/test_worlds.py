import guard
from pathlib import Path
import tempfile
import unittest
from fractions import Fraction
from exp7ops.worlds import make_recipe, STATES, POISONS, GRID, exercise_world_protocol
from exp7ops.cold import deterministic_twice, cold_suite, COLD_TASKS
from exp7ops.evidence import once, Refusal, canonical, strict, digest
from exp7core.scoring import score_draws, outcome_counts

class WorldProtocolTests(unittest.TestCase):
    def test_miniature_full_world_protocol_retains_inputs_and_once_claims(self):
        calls = []
        class Adapter:
            def install(self, root, recipe):
                once(root / "raw.json", recipe)
            def poison(self, root, case):
                once(root / "poison", case.encode())
            def scientific_inputs(self, root):
                return digest((root / "raw.json").read_bytes())
            def claimed(self, root):
                return (root / "analysis.CLAIM").exists()
            def analyze(self, root):
                calls.append(root.name)
                if self.claimed(root) or (root / "poison").exists():
                    if not self.claimed(root):
                        once(root / "analysis.CLAIM", b"fixture once")
                    return {"states": {"pythia_1b": "INSUFFICIENT_DATA", "olmo2_1b": "INSUFFICIENT_DATA"}, "statistics_executed": False}
                once(root / "analysis.CLAIM", b"fixture once")
                return {"states": strict((root / "raw.json").read_bytes())["expected"],
                        "secondaries": list(range(1,9)), "licence": "does not identify an internal algorithm"}
            def summarize(self, report):
                return report
        with tempfile.TemporaryDirectory() as directory:
            records = exercise_world_protocol(Adapter(), Path(directory) / "worlds", recipe_factory=lambda a,b: make_recipe(a,b,pairs=2))
            self.assertEqual(len(records), 17 + len(POISONS))
            self.assertEqual(len(calls), 34 + len(POISONS))
            self.assertEqual({r["poison"] for r in records if "poison" in r}, set(POISONS))
    def test_raw_recipes_have_correct_direction_constant_and_thin_support(self):
        for mode in STATES:
            recipe = make_recipe(mode, mode, pairs=21)
            for family, rows in recipe["families"].items():
                xs, ys = [], []
                for row in rows:
                    score = score_draws(row["trained"]["pythia_1b"], row["targets"], "word", k=64)
                    counts = outcome_counts({int(k):v for k,v in row["outputs"].items()}, row["targets"], "word", steps=GRID)
                    xs.append(score.x); ys.append(counts["y"])
                if mode == "ORDER-ONLY":
                    self.assertEqual(sum(xs), 0)
                    self.assertEqual(xs, sorted(xs))
                elif mode == "INPUT-SENSITIVE-FORECAST":
                    self.assertGreater(sum(xs) / len(xs), Fraction(1,20))
                elif mode == "SELECTIVE-ONLY":
                    self.assertEqual(set(xs), {1})
                elif mode == "UNDETERMINED" and family in ("units", "shapes"):
                    self.assertEqual(set(ys), {0})
        self.assertEqual(len(GRID), 26)
        self.assertGreaterEqual(len(POISONS), 20)

    def test_two_process_protocol_with_fake_adapter_and_byte_difference(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); calls = []
            class Fake:
                def run(self, argv, **kw):
                    calls.append((argv, kw))
                    once(Path(argv[-1]), b'{"deterministic":"fixture"}\n')
            result = deterministic_twice(Fake(), python="/python", worker="/guarded_worker.py", fixture="/fixture", output=root / "two")
            self.assertEqual(result["invocations"], 2)
            self.assertTrue(all(c[1]["shell"] is False for c in calls))
            class Different:
                def run(self, argv, **kw):
                    once(Path(argv[-1]), str(argv[-1]).encode())
            with self.assertRaises(Refusal):
                deterministic_twice(Different(), python="/python", worker="/guarded_worker.py", fixture="/fixture", output=root / "bad")

    def test_cold_suite_task_selection_no_real_read_sweep(self):
        with tempfile.TemporaryDirectory() as directory:
            tasks = []
            def run(task):
                tasks.append(task)
                return {"tests": 1, "failures": 0, "errors": 0, "returncode": 0}
            cold_suite(run, Path(directory) / "cold", synthetic=False)
            self.assertEqual(tuple(tasks), COLD_TASKS)
