"""Real serialized producer export, cold-copy mini analysis and genuine poisons."""
from pathlib import Path
import json
import tempfile
import unittest
from exp7ops.worlds import make_recipe, POISONS
from exp7stats.common import dumps
from exp7integration.world_harness import LATE_FAULTS
from world_fixture import ProducerWorldFixture
from freeze_workers import analysis_worker
from testing_paths import WORK, CONTRACTS
from test_real_composition import REPO


class ProducerWorldTests(unittest.TestCase):
    def test_export_copy_determinism_and_phase_correct_raw_poisons(self):
        with tempfile.TemporaryDirectory(dir=WORK) as tmp:
            root = Path(tmp); base = root/"producer"; base.mkdir()
            fixture = ProducerWorldFixture(source_repo=REPO,
                source_pins=json.loads((CONTRACTS/"collection-source-pins.json").read_bytes()), miniature=True)
            fixture.install(base, make_recipe("INPUT-SENSITIVE-FORECAST", "INPUT-SENSITIVE-FORECAST"))
            print("\nproducer export ready (full shape; miniature numerics)", flush=True)
            exported = root/"export.json"; sha = fixture.export(base, exported)
            first, second = root/"first.json", root/"second.json"
            # Same-process cold tree copies verify worker plumbing. The future
            # two-process task remains separate and is not claimed by this test.
            analysis_worker(exported, sha, first, miniature=True)
            analysis_worker(exported, sha, second, miniature=True)
            self.assertEqual(first.read_bytes(), second.read_bytes())
            print("two worker-copy reports byte-identical", flush=True)
            result = json.loads(first.read_bytes())
            self.assertEqual({v["state"] for v in result["primary"].values()}, {"NO-JOINT-SUPPORT"})
            self.assertEqual(len(result["secondaries"]), 8)
            # Source poisons require their own disposable module worker; the
            # remaining 21 exercise actual corrupted serialized input/authority.
            for poison in POISONS:
                if poison in ("changed-init", "missing-secondary"):
                    continue
                with self.subTest(poison=poison):
                    target = root/poison; target.mkdir()
                    fixture.clone_export(exported, sha, target)
                    fixture.poison(target, poison)
                    before = fixture.scientific_inputs(target)
                    wrapper = fixture.analyze(target); view = fixture.summarize(wrapper)
                    self.assertEqual(set(view["states"].values()), {"INSUFFICIENT_DATA"}, wrapper)
                    self.assertIs(view["statistics_executed"], poison in LATE_FAULTS, wrapper)
                    self.assertFalse(fixture.success_published(target), wrapper)
                    self.assertEqual(fixture.scientific_inputs(target), before)
                    print("poison checked: "+poison, flush=True)
