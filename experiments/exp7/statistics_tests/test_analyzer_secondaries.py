from copy import deepcopy
from fractions import Fraction as F
from pathlib import Path
import tempfile
import unittest
from exp7stats.common import Shape, digest, stage, SCHEMA
from exp7stats.data import load_battery, load_predictors, load_outcomes, cells
from exp7stats.kernels import primary
from exp7stats.analyzer import synthetic_run, run
from exp7stats.secondaries import NAMES
from stats_fixtures import FakeCampaign, WORK, payloads


class AnalysisTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=WORK)
        self.addCleanup(self.tmp.cleanup)
        self.campaign = FakeCampaign(self.tmp.name)
        self.shape = Shape(n=24, grid=(1, 2, 3), permutations=200, bootstraps=3)

    def test_complete_raw_synthetic_world_all_eight_secondaries(self):
        before = digest((self.campaign.b, self.campaign.p, self.campaign.o))
        result = synthetic_run(self.campaign, self.shape)
        self.assertEqual(result["state"], "COMPLETE", result)
        self.assertEqual(result["aggregate"]["aggregate"], "BOTH-PREDICTORS")
        self.assertEqual(set(result["secondaries"]), set(NAMES))
        for name, section in result["secondaries"].items():
            self.assertTrue(section)
            self.assertIn("status", section)
        self.assertEqual(result["primary"]["pythia_1b"]["selectivity"]["consumed"], 200)
        self.assertEqual(result["primary"]["pythia_1b"]["forecast"]["consumed"], 200)
        self.assertEqual(result["primary"]["pythia_1b"]["bootstrap"]["T"]["B"], 3)
        s = result["secondaries"]
        self.assertEqual(s[NAMES[3]]["pythia_1b"]["base"]["dropped_pairs"], 0)
        self.assertEqual(set(s[NAMES[4]]["pythia_1b"]["budgets"]),
                         {"k16", "k32", "k64", "half_first32", "half_last32"})
        self.assertEqual(s[NAMES[5]]["pythia_1b"]["member_q0"]["T"], None)
        self.assertEqual(s[NAMES[5]]["pythia_1b"]["member_q0"]["bootstrap"]["T"]["undefined"], 3)
        self.assertEqual(s[NAMES[1]]["pythia_1b"]["paired_T_difference"]["difference"], 2)
        self.assertEqual(s[NAMES[7]]["status"], "EXACT")
        self.assertEqual(s[NAMES[7]]["predictor_raw_before"], s[NAMES[7]]["predictor_raw_after"])
        self.assertEqual(before, digest((self.campaign.b, self.campaign.p, self.campaign.o)))
        path = Path(self.tmp.name)/"statistics/analysis"
        self.assertTrue((path/"COMPLETE.json").exists())
        text = (path/"REPORT.md").read_text()
        self.assertTrue(all(name in text for name in NAMES))
        events = list(self.campaign.events)
        again = synthetic_run(self.campaign, self.shape)
        self.assertEqual(again["state"], "INSUFFICIENT_DATA")
        self.assertEqual(self.campaign.events, events)

    def test_selected_component_worlds_not_pooled_labels(self):
        for mode, expected in (("constant", "NO-JOINT-SUPPORT"), ("selective_only", "SELECTIVE-ONLY"),
                               ("order_only", "ORDER-ONLY")):
            b, p, o = payloads(mode=mode)
            battery = load_battery(b, self.shape)
            predictors = load_predictors(p, battery, self.shape)
            outcome = load_outcomes(o, battery, self.shape)
            r = primary(cells(predictors["pythia_1b"], outcome, battery), B=200,
                        namespace=("world", mode), full=True)
            self.assertEqual(r["state"], expected)
            self.assertEqual(len(r["eligible"]), 4)

    def test_missing_arm_complete_gate_does_not_hide_schema_failure(self):
        del self.campaign.p["trained"]["pythia_1b"]["units"][0]["draws"]["q0s"]
        result = synthetic_run(self.campaign, self.shape)
        self.assertEqual(result["state"], "INSUFFICIENT_DATA")
        self.assertTrue((Path(self.tmp.name)/"statistics/HALTED.json").exists())
        self.assertFalse((Path(self.tmp.name)/"statistics/analysis/COMPLETE.json").exists())

    def test_exit_pin_failure_prevents_final_success(self):
        self.campaign.exit_failure = True
        small = Shape(n=24, grid=(1, 2, 3), permutations=3, bootstraps=1)
        result = synthetic_run(self.campaign, small)
        self.assertEqual(result["state"], "INSUFFICIENT_DATA")
        self.assertIn("changed at exit", " ".join(result["failures"]))
        self.assertFalse((Path(self.tmp.name)/"statistics/analysis/analysis.json").exists())

    def test_no_grant_no_data_reads_and_empty_injection(self):
        self.campaign.entry_failure = True
        result = synthetic_run(self.campaign, self.shape)
        self.assertEqual(result["state"], "INSUFFICIENT_DATA")
        self.assertEqual(self.campaign.events, [("entry", "analysis")])
        self.assertEqual(run(None)["state"], "INSUFFICIENT_DATA")

    def test_production_cannot_accept_miniature_coverage(self):
        result = run(self.campaign)
        self.assertEqual(result["state"], "INSUFFICIENT_DATA")
        self.assertIn("coverage", " ".join(result["failures"]))

    def test_support_19_and_2_family_refusal(self):
        b, p, o = payloads()
        for family in ("units", "shapes"):
            for row in o["families"][family][19:]:
                row["outputs"] = {str(t): {a: "other" for a in ("q0", "q1", "q0s", "q1s")} for t in self.shape.grid}
        battery = load_battery(b, self.shape)
        pred = load_predictors(p, battery, self.shape)["pythia_1b"]
        outcome = load_outcomes(o, battery, self.shape)
        r = primary(cells(pred, outcome, battery), B=3, namespace="thin")
        self.assertEqual(r["state"], "UNDETERMINED")
        self.assertEqual(len(r["eligible"]), 2)

    def test_network_and_model_imports_hard_refuse(self):
        import importlib
        for name in ("torch", "transformers", "mlx", "huggingface_hub", "tokenizers", "socket", "urllib.request"):
            with self.assertRaisesRegex(ImportError, "HARD-REFUSED"):
                importlib.import_module(name)
