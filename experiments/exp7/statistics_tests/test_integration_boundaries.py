from pathlib import Path
from copy import deepcopy
from contextlib import contextmanager
import tempfile
import unittest
from exp7core.contract import Refusal
from exp7stats.common import (ARMS, FAMILIES, SCHEMA, Shape, CONTACT_ROOTS, dumps, digest,
                              require_preoutcome, require_preoutcome_inventory, stage)
from exp7stats.data import load_battery, load_predictors, load_outcomes
from exp7stats.analyzer import synthetic_run
from exp7stats.calibration_context import CalibrationContext
from stats_fixtures import FakeCampaign, WORK
from runtime_fixture import allowance
from read_fixture import FakeColdPort


class MiniCandidateContext(CalibrationContext):
    # Only source discovery is substituted; manifest, blob, stage and read/exit
    # checks are the actual production context. Never calls calibration.run.
    def _source_inventory(self):
        return [self.repo/"candidate.py", self.repo/"helper.py"]


class IntegrationBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=WORK)
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def test_all_actual_outcome_tree_paths_refuse_even_empty_or_dangling(self):
        for name in ("units/outcome", "units/endpoint", "units/outcome-anchors", "contacts/outcome"):
            path = self.root/name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.mkdir()
            with self.assertRaises(Refusal):
                require_preoutcome(self.root)
            path.rmdir()
        path.symlink_to(self.root/"never-created")
        with self.assertRaises(Refusal):
            require_preoutcome(self.root)

    def test_contact_probe_grant_phase_inventory_not_just_outcome_directories(self):
        inv = {"schema": "exp7.contact-inventory.v1", "covered_roots": CONTACT_ROOTS, "entries": []}
        def check(v):
            return require_preoutcome_inventory({"contact_inventory": v, "input_sha256": {"contact_inventory": digest(v)}})
        self.assertEqual(check(inv), inv)
        for kind in ("probe", "grant", "phase", "contact", "operation", "endpoint"):
            bad = deepcopy(inv)
            bad["entries"] = [{"path": f"probes/arbitrary-{kind}.json", "kind": kind,
                               "phase": "outcome", "sha256": "a"*64}]
            with self.assertRaises(Refusal):
                check(bad)
        for phase in ("unknown", None):
            bad["entries"][0]["phase"] = phase
            with self.assertRaises(Refusal):
                check(bad)
        with self.assertRaises(Refusal):
            require_preoutcome_inventory({"input_sha256": {"synthetic": "a"*64}})

    def test_exit_inventory_change_blocks_power_publication(self):
        class Campaign(FakeCampaign):
            @contextmanager
            def entryexit(self, name):
                with super().entryexit(name) as provenance:
                    yield provenance
                    self.contact_inventory["entries"].append({"path": "probes/test.json", "kind": "probe",
                                                               "phase": "outcome", "sha256": "a"*64})
        campaign = Campaign(self.root)
        result = stage(campaign, "power", lambda p: {"schema": SCHEMA, "state": "COMPLETE"}, production=False)
        self.assertEqual(result["state"], "INSUFFICIENT_DATA")
        self.assertFalse((self.root/"statistics/power/power.json").exists())

    def candidate(self):
        repo, root = self.root/"repo", self.root/"output"
        repo.mkdir(); root.mkdir()
        content = {"candidate.py": b"# candidate\n", "helper.py": b"# helper\n", "design.md": b"# synthetic design\n",
                   "cases.json": b'{"schema":"synthetic-only"}\n'}
        content["runtime.json"] = dumps(allowance())
        files = {k: {"kind": "source" if k.endswith(".py") else "design" if k.endswith(".md") else "synthetic_spec",
                     "sha256": digest(v)} for k, v in content.items()}
        files["runtime.json"]["kind"] = "runtime_spec"
        content["manifest.json"] = dumps({"schema": "exp7.calibration-candidate.v1", "files": files})
        for k, v in content.items():
            (repo/k).write_bytes(v)
        ctx = MiniCandidateContext(root, repo, candidate_commit="1"*40, manifest_path="manifest.json",
                                   manifest_sha256=digest(content["manifest.json"]),
                                    blob_reader=lambda repo, commit, path: content[path], tag_probe=lambda repo: False,
                                    read_port=FakeColdPort())
        return ctx, content

    def test_pretag_context_works_without_seal_projection_or_contact_grant(self):
        ctx, _ = self.candidate()
        def operation(provenance):
            self.assertEqual(provenance["candidate_commit"], "1"*40)
            self.assertEqual(provenance["synthetic_spec"], {"schema": "synthetic-only"})
            self.assertEqual((ctx.repo/"helper.py").read_bytes(), b"# helper\n")
            return {"schema": SCHEMA, "state": "SYNTHETIC-CONTEXT-CHECK", "stage": "calibration"}
        result = stage(ctx, "calibration", operation, production=False)
        self.assertEqual(result["state"], "SYNTHETIC-CONTEXT-CHECK", result)
        self.assertFalse(result["production"])
        self.assertTrue((ctx.root/"statistics/calibration/COMPLETE.json").exists())

    def test_pre_tag_context_changed_source_and_unpinned_read_refuse(self):
        ctx, _ = self.candidate()
        (ctx.repo/"hidden.txt").write_text("unbound")
        with self.assertRaisesRegex(Refusal, "unpinned"):
            with ctx.entryexit("calibration"):
                (ctx.repo/"hidden.txt").read_text()
        with self.assertRaisesRegex(Refusal, "binding"):
            with ctx.entryexit("calibration"):
                (ctx.repo/"helper.py").write_text("# changed\n")

    def test_pre_tag_context_missing_source_closure_or_existing_tag_refuses(self):
        ctx, content = self.candidate()
        ctx.tag_probe = lambda repo: True
        with self.assertRaisesRegex(Refusal, "precede"):
            with ctx.entryexit("calibration"):
                self.fail("entered after tag")
        ctx.tag_probe = lambda repo: False
        from exp7core.records import strict_json
        manifest = strict_json(content["manifest.json"])
        del manifest["files"]["helper.py"]
        content["manifest.json"] = dumps(manifest)
        (ctx.repo/"manifest.json").write_bytes(content["manifest.json"])
        ctx.manifest_sha = digest(content["manifest.json"])
        with self.assertRaisesRegex(Refusal, "omitted"):
            with ctx.entryexit("calibration"):
                self.fail("entered with omitted package module")

    def test_full_84_baseline_cells_keep49_applicable_and_abstentions(self):
        campaign = FakeCampaign(self.root)
        names = [f"method{j:02d}" for j in range(21)]
        for fi, f in enumerate(FAMILIES):
            campaign.b["baseline_ids"][f] = names
            for row in campaign.b["families"][f]:
                row["baselines"] = {name: ({"status": "APPLICABLE", "na_reason": None,
                                            "outputs": dict.fromkeys(ARMS, ""), "abstained": dict.fromkeys(ARMS, True)}
                                           if fi*21+j < 49 else {"status": "NOT_APPLICABLE", "na_reason": "synthetic N/A",
                                                                  "outputs": None, "abstained": None})
                                    for j, name in enumerate(names)}
        campaign.b["baseline_coverage"] = {"applicable_cells": 49, "not_applicable_cells": 35}
        result = synthetic_run(campaign, Shape(n=24, grid=(1, 2, 3), permutations=2, bootstraps=1))
        self.assertEqual(result["state"], "COMPLETE", result)
        s = result["secondaries"]["S7_baselines_twin"]
        self.assertEqual(s["applicability_coverage"]["applicable_denominator"], 49)
        rows = [r for family in s["pythia_1b"]["baselines"].values() for r in family.values()]
        self.assertEqual(sum(r["status"] == "NOT_APPLICABLE" for r in rows), 35)
        self.assertTrue(all(r["N"] == 24 and r["reading"]["mean"] == 0 for r in rows if r["status"] == "APPLICABLE"))
        self.assertIn('"abstentions_by_arm"', (self.root/"statistics/analysis/REPORT.md").read_text())

    def test_unknown_baseline_missing_cell_and_model_None_refuse(self):
        campaign = FakeCampaign(self.root)
        shape = Shape(n=24, grid=(1, 2, 3), permutations=2, bootstraps=1)
        bad = deepcopy(campaign.b)
        del bad["families"][FAMILIES[0]][0]["baselines"]["constant"]
        with self.assertRaises(Refusal):
            load_battery(bad, shape)
        broken = FakeCampaign(self.root)
        broken.b = bad
        refusal = synthetic_run(broken, shape)
        self.assertTrue(refusal["baseline_missing"])
        bad = deepcopy(campaign.b)
        bad["families"][FAMILIES[0]][0]["baselines"]["constant"]["outputs"]["q0"] = None
        with self.assertRaises(Refusal):
            load_battery(bad, shape)
        battery = load_battery(campaign.b, shape)
        campaign.p["twin"][FAMILIES[0]][0]["draws"]["q0"][0] = None
        with self.assertRaises(Refusal):
            load_predictors(campaign.p, battery, shape)
        campaign.o["families"][FAMILIES[0]][0]["outputs"]["1"]["q0"] = None
        with self.assertRaises(Refusal):
            load_outcomes(campaign.o, battery, shape)

    def test_failed_calibration_publishes_failure_not_success(self):
        campaign = FakeCampaign(self.root)
        result = stage(campaign, "calibration", lambda p: {"schema": SCHEMA, "stage": "calibration",
                                                          "state": "CALIBRATION-FAILED", "fixture": True}, production=False)
        self.assertEqual(result["state"], "CALIBRATION-FAILED")
        self.assertTrue((self.root/"statistics/HALTED.json").exists())
        self.assertTrue((self.root/"statistics/calibration/REFUSED.json").exists())
        self.assertFalse((self.root/"statistics/calibration/COMPLETE.json").exists())
