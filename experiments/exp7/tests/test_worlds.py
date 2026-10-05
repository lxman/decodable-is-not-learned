import guard
from pathlib import Path
import tempfile
import unittest
from fractions import Fraction
from exp7ops.worlds import make_recipe, STATES, POISONS, GRID
from exp7ops.cold import cold_suite, INTEGRATION_TASKS
from exp7integration.world_harness import exercise
from exp7integration.freeze import deterministic_twice
from exp7ops.evidence import once, Refusal, canonical, strict, digest
from exp7core.scoring import score_draws, outcome_counts

class WorldProtocolTests(unittest.TestCase):
    def test_miniature_full_world_protocol_retains_inputs_and_once_claims(self):
        calls = []
        class Adapter:
            def __init__(self):
                self.roots, self.restores = [], 0
            def install(self, root, recipe):
                self.roots.append(root)
                once(root / "raw.json", recipe)
            def poison(self, root, case):
                once(root / "poison", case.encode())
            def scientific_inputs(self, root):
                return digest((root / "raw.json").read_bytes())
            def claimed(self, root):
                return (root / "analysis.CLAIM").exists()
            def success_published(self, root):
                return (root / "SUCCESS.json").exists()
            def restore_sources(self):
                self.restores += 1
            def analyze(self, root):
                calls.append(root.name)
                if self.claimed(root):
                    return {"states": {"pythia_1b": "INSUFFICIENT_DATA", "olmo2_1b": "INSUFFICIENT_DATA"}, "statistics_executed": False}
                once(root / "analysis.CLAIM", b"fixture once")
                if (root / "poison").exists():
                    poison = (root / "poison").read_text()
                    return {"states": {"pythia_1b": "INSUFFICIENT_DATA", "olmo2_1b": "INSUFFICIENT_DATA"},
                            "statistics_executed": poison in ('entry-only-pin', 'HALTED-before-final')}
                once(root / "SUCCESS.json", {"fake_report": True})
                return {"states": strict((root / "raw.json").read_bytes())["expected"],
                        "statistics_executed": True,
                        "secondaries": list(range(1,9)), "licence": "does not identify an internal algorithm"}
            def summarize(self, report):
                return report
        with tempfile.TemporaryDirectory() as directory:
            adapter = Adapter()
            records = exercise(adapter, Path(directory) / "worlds", recipe_factory=lambda a,b: make_recipe(a,b,pairs=2))
            self.assertEqual(len(records), 17 + len(POISONS))
            self.assertEqual(len(calls), 34 + len(POISONS))
            self.assertEqual({r["poison"] for r in records if "poison" in r}, set(POISONS))
            self.assertEqual({r['poison'] for r in records if r.get('statistics_executed')},
                             {'entry-only-pin', 'HALTED-before-final'})
            self.assertEqual(adapter.restores, 1)
            self.assertEqual(strict((Path(directory) / 'worlds/worlds-receipt.json').read_bytes()), records)
            for root in adapter.roots:
                poison = root.name in POISONS
                self.assertTrue(adapter.claimed(root))
                self.assertEqual(adapter.success_published(root), not poison)
                self.assertEqual(calls.count(root.name), 1 if poison else 2)
                self.assertEqual(strict((root / 'raw.json').read_bytes())['pairs'], 2)
                if poison:
                    self.assertEqual((root / 'poison').read_text(), root.name)
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
            package = root / 'package'
            fixture = root / 'synthetic-fixture.json'
            fixture.write_bytes(b'{"synthetic":"known fixture"}\n')
            fixture_sha256 = digest(fixture.read_bytes())
            def expected(output):
                return [(['/python', '-I', '-B', str(package / 'numerical_worker.py'),
                          '--fixture', str(fixture), '--fixture-sha256', fixture_sha256,
                          '--output', str(output / (name + '.json'))],
                         {'cwd': str(package), 'shell': False, 'timeout': 86400})
                        for name in ('first', 'second')]
            class Fake:
                def run(self, argv, **kw):
                    calls.append((argv, kw))
                    once(Path(argv[-1]), b'{"deterministic":"fixture"}\n')
            result = deterministic_twice(Fake(), python='/python', package=package,
                                         fixture=fixture, fixture_sha256=fixture_sha256, output=root / 'two')
            self.assertEqual(result["invocations"], 2)
            self.assertEqual(calls, expected(root / 'two'))
            self.assertEqual(result['sha256'], digest(b'{"deterministic":"fixture"}\n'))
            self.assertTrue(result['byte_identical'])
            self.assertEqual(strict((root / 'two/determinism.json').read_bytes()), result)
            calls.clear()
            class Different:
                def run(self, argv, **kw):
                    calls.append((argv, kw))
                    once(Path(argv[-1]), str(argv[-1]).encode())
            with self.assertRaisesRegex(Refusal, 'two independent workers differ'):
                deterministic_twice(Different(), python='/python', package=package,
                                    fixture=fixture, fixture_sha256=fixture_sha256, output=root / 'bad')
            self.assertEqual(calls, expected(root / 'bad'))
            self.assertNotEqual((root / 'bad/first.json').read_bytes(), (root / 'bad/second.json').read_bytes())
            self.assertFalse((root / 'bad/determinism.json').exists())

    def test_retired_cold_suite_refuses_before_effects(self):
        with tempfile.TemporaryDirectory() as directory:
            tasks = []
            def run(task):
                tasks.append(task)
                raise AssertionError('retired callback invoked')
            for synthetic in (False, True):
                for integrated in ((), ('G1',), INTEGRATION_TASKS):
                    with self.subTest(synthetic=synthetic, integrated=integrated):
                        output = Path(directory) / 'cold'
                        with self.assertRaisesRegex(Refusal, '^exp7ops\\.cold\\.cold_suite is retired; use run_task_tests\\.py --task with the installed registry$'):
                            cold_suite(run, output, synthetic=synthetic, integrated_tasks=integrated)
                        self.assertEqual(tasks, [])
                        self.assertFalse(output.exists())
                        self.assertFalse((output / 'COMPLETE.json').exists())
            self.assertEqual(list(Path(directory).iterdir()), [])
