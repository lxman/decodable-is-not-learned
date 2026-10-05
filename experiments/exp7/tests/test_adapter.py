from pathlib import Path
from copy import deepcopy
from dataclasses import replace
from contextlib import contextmanager
import tempfile
import unittest
from exp7core.contract import Refusal
from exp7stats.common import ARMS, FAMILIES, PREDICTORS, GRID, Shape, SCHEMA, stage, digest, dumps
from exp7stats.data import load_battery, load_predictors, load_outcomes
from exp7stats.analyzer import synthetic_run
from exp7integration.adapter import StatsCampaignAdapter
from collection_fixture import StrictCollection, ROOT, put

WORK = ROOT / "test-work"
WORK.mkdir(exist_ok=True)
SHAPE = Shape(n=24, grid=(1, 2, 3), permutations=3, bootstraps=1)


class AdapterTests(unittest.TestCase):
    @contextmanager
    def fixture(self, **kwargs):
        with tempfile.TemporaryDirectory(dir=WORK) as tmp:
            root = Path(tmp) / "campaign"
            root.mkdir()
            yield StrictCollection(root, **kwargs)

    def probe(self, f, operation, *, name="analysis", production=False):
        adapter = f.adapter(miniature=not production)
        def run(provenance):
            operation(adapter, provenance)
            return {"schema": SCHEMA, "stage": "protocol-test", "state": "COMPLETE"}
        return stage(adapter, name, run, production=production)

    def assert_refused(self, value, substring=None):
        self.assertEqual(value["state"], "INSUFFICIENT_DATA", value)
        if substring:
            self.assertIn(substring, " ".join(value["failures"]))

    def test_constructor_and_unentered_context_do_not_read_inputs(self):
        with self.fixture() as f:
            a = f.adapter()
            ctx = a.entryexit("analysis")
            self.assertEqual(f.events, [])
            for method in (a.battery, a.predictor_data, a.outcomes, a.verify_predictor_seal, a.verify_power, a.verify_complete):
                with self.assertRaises(Refusal):
                    method()
            with self.assertRaises(FileNotFoundError):
                with ctx:
                    self.fail("missing claim admitted")
            self.assertEqual(f.events, [])

    def test_absent_grant_consumes_stats_claim_before_no_input_reads(self):
        with self.fixture() as f:
            f.grant = False
            f.authority_name.write_bytes(b"must not be read")
            result = synthetic_run(f.adapter(), SHAPE)
            self.assert_refused(result, "grant absent")
            self.assertEqual(f.events, ["claim_observed"])
            self.assertTrue((f.root/"statistics/analysis/CLAIM.json").is_file())
            self.assertTrue((f.root/"statistics/analysis/REFUSED.json").is_file())

    def test_full500_certified_metadata_shape_all84_cells(self):
        with self.fixture(n=500, grid=GRID) as f:
            def check(a, provenance):
                got = a.battery()
                loaded = load_battery(got)
                self.assertEqual(dict(loaded.baseline_coverage), {"applicable_cells": 49, "not_applicable_cells": 35})
                self.assertEqual(provenance["provenance_sha256"], f.binding_values["trust_sha256"])
                self.assertEqual(provenance["input_sha256"]["normalizer"], digest(b"fixture-normalizer"))
                for family in FAMILIES:
                    self.assertEqual(len(got["families"][family]), 500)
                    for i, row in enumerate(got["families"][family]):
                        p = f.b.family(family)[i]
                        self.assertEqual((row["id"], row["index"], row["targets"], row["base"]),
                                         (p.pair_id, i, list(p.targets), f.base[family][i]))
                        self.assertEqual(row["prompts_sha256"], {a: digest(p.prompts[j].encode()) for j, a in enumerate(ARMS)})
                        self.assertEqual(len(row["baselines"]), 21)
            result = self.probe(f, check, production=True)
            self.assertEqual(result["state"], "COMPLETE", result)
            self.assertNotIn("predictor_draws", f.events)

    def test_baseline_none_only_mapping_and_all_counts(self):
        with self.fixture() as f:
            def check(a, _):
                got = a.battery()
                for method in f.methods:
                    for family in FAMILIES:
                        abstentions = emissions = 0
                        for i, row in enumerate(got["families"][family]):
                            cell = row["baselines"][method]
                            if not f.catalog[method][family]["applicable"]:
                                self.assertIsNone(cell["outputs"])
                                self.assertIsNone(cell["abstained"])
                                self.assertEqual(cell["na_reason"], f.catalog[method][family]["reason"])
                            else:
                                for arm in ARMS:
                                    original = f.raw_baselines[method][family][i][arm]
                                    self.assertEqual(cell["outputs"][arm], "" if original is None else original)
                                    self.assertIs(cell["abstained"][arm], original is None)
                                    abstentions += original is None
                                    emissions += original is not None
                        if f.catalog[method][family]["applicable"]:
                            self.assertEqual(abstentions, f.catalog[method][family]["abstentions"])
                            self.assertEqual(emissions, f.catalog[method][family]["emissions"])
            self.assertEqual(self.probe(f, check)["state"], "COMPLETE")

    def test_raw_mapping_all_predictor_draw_and_outcome_orientation_indexes(self):
        with self.fixture(grid=GRID, orientation=True) as f:
            def check(a, _):
                predictors, outcome = a.predictor_data(), a.outcomes()
                self.assertEqual(outcome["grid"], list(GRID))
                for name in (*PREDICTORS, "twin"):
                    families = predictors["twin"] if name == "twin" else predictors["trained"][name]
                    for family in FAMILIES:
                        for i, row in enumerate(families[family]):
                            self.assertEqual(row["id"], f"{family}:{i:04d}")
                            for arm in ARMS:
                                self.assertEqual(row["draws"][arm], [f"{name}/{family}/{i}/{arm}/{j}" for j in range(16 if name == "twin" else 64)])
                for family in FAMILIES:
                    for i, row in enumerate(outcome["families"][family]):
                        for t in GRID:
                            self.assertEqual(row["outputs"][str(t)], {arm: f"{family}/{i}/{t}/{arm}" for arm in ARMS})
            self.assertEqual(self.probe(f, check)["state"], "COMPLETE")
            self.assertNotIn("SCORES_MUST_NOT_BE_USED", f.events)

    def test_miniature_complete_statistics_composition(self):
        with self.fixture() as f:
            result = synthetic_run(f.adapter(), SHAPE)
            self.assertEqual(result["state"], "COMPLETE", result)
            self.assertIs(result["production"], False)
            self.assertEqual(len(result["secondaries"]), 8)
            self.assertEqual(f.events[:3], ["claim_observed", "grant_consumed", "entered"])
            self.assertNotIn("SCORES_MUST_NOT_BE_USED", f.events)
            self.assertTrue((f.root/"statistics/analysis/COMPLETE.json").exists())
            again = synthetic_run(f.adapter(), SHAPE)
            self.assert_refused(again)
            self.assertEqual(f.events.count("grant_consumed"), 1)

    def test_model_none_rejected_trained_twin_and_outcome(self):
        for source in (*PREDICTORS, "twin", "outcome"):
            with self.subTest(source=source), self.fixture() as f:
                if source == "outcome":
                    rows = list(f.o[FAMILIES[0]])
                    steps = list(rows[0]); arms = list(steps[0]); arms[2] = None
                    steps[0] = tuple(arms); rows[0] = tuple(steps); f.o[FAMILIES[0]] = tuple(rows)
                    operation = lambda a, _: a.outcomes()
                else:
                    rows = list(f.p[source][FAMILIES[0]])
                    arms = list(rows[0]); draws = list(arms[3]); draws[0] = None
                    arms[3] = tuple(draws); rows[0] = tuple(arms); f.p[source][FAMILIES[0]] = tuple(rows)
                    operation = lambda a, _: a.predictor_data()
                self.assert_refused(self.probe(f, operation), "None/non-string")

    def test_production_cannot_shorten_family_or_budget(self):
        with self.fixture() as f:
            self.assert_refused(self.probe(f, lambda a, _: a.battery(), production=True), "exact battery pair count")
        for name in (*PREDICTORS, "twin"):
            with self.fixture() as f:
                rows = list(f.p[name][FAMILIES[0]]); arms = list(rows[0]); arms[0] = arms[0][:-1]
                rows[0] = tuple(arms); f.p[name][FAMILIES[0]] = tuple(rows)
                self.assert_refused(self.probe(f, lambda a, _: a.predictor_data()), "draw coverage")

    def test_missing_catalog_cells_arms_and_false_na_refuse(self):
        attacks = [lambda f: f.catalog.pop(f.methods[0]),
                   lambda f: f.catalog[f.methods[0]].pop(FAMILIES[0]),
                   lambda f: f.raw_baselines[f.methods[0]][FAMILIES[0]][0].pop("q1s"),
                   lambda f: f.catalog[f.methods[0]][FAMILIES[0]].update(applicable=False, reason="invented missing"),
                   lambda f: f.catalog[f.methods[-1]][FAMILIES[-1]].update(reason=""),
                   lambda f: f.catalog[f.methods[0]][FAMILIES[0]].update(abstentions=0)]
        for attack in attacks:
            with self.subTest(attack=attack), self.fixture() as f:
                attack(f)
                self.assert_refused(self.probe(f, lambda a, _: a.battery()), "baseline")

    def test_base_and_pair_identity_coverage_refuse(self):
        attacks = [lambda f: f.base.update({FAMILIES[0]: f.base[FAMILIES[0]][:-1]}),
                   lambda f: setattr(f, "b", replace(f.b, pairs=(replace(f.b.pairs[0], pair_id="swapped"), *f.b.pairs[1:])))]
        for attack in attacks:
            with self.fixture() as f:
                attack(f)
                self.assert_refused(self.probe(f, lambda a, _: a.battery()))

    def test_code_and_battery_drift_during_transform_refuse(self):
        for mutate in (lambda f: f.binding_values.update(code_manifest_sha256=digest(b"changed")),
                       lambda f: object.__setattr__(f.b.pairs[0], "targets", ("mutated", "beta"))):
            with self.fixture() as f:
                f.hooks["predictor_draws"] = mutate
                self.assert_refused(self.probe(f, lambda a, _: a.predictor_data()))

    def test_exit_failure_prevents_published_success_both_claims_spent(self):
        with self.fixture() as f:
            f.fail_exit = True
            result = synthetic_run(f.adapter(), SHAPE)
            self.assert_refused(result, "exit source/receipt drift")
            self.assertTrue(f.consumed)
            self.assertFalse((f.root/"statistics/analysis/analysis.json").exists())
            self.assertFalse((f.root/"statistics/analysis/COMPLETE.json").exists())

    def test_canonical_receipts_preserve_bindings_and_decoded_fraction(self):
        from fractions import Fraction
        with self.fixture() as f:
            f.power_record["fraction"] = {"numerator": 2, "denominator": 3}
            sha = put(f.root, "statistics/power/power.json", f.power_record)
            f.power.update(power_sha256=sha, bindings={"statistics/power/power.json": sha})
            f.authority["receipts"]["power_sha256"] = sha
            f.save_authority()
            def check(a, _):
                self.assertEqual(a.verify_predictor_seal(), f.seal)
                self.assertEqual(a.verify_complete(), f.complete)
                self.assertEqual(a.verify_power()["record"]["fraction"], Fraction(2, 3))
                self.assertEqual(a.verify_power()["bindings"], f.power["bindings"])
            self.assertEqual(self.probe(f, check)["state"], "COMPLETE")

    def test_forged_receipt_hashes_empty_bindings_and_renamed_fields_refuse(self):
        attacks = [(lambda f: f.seal["bindings"].update({"seal.json": digest(b"forged")}), "verify_predictor_seal"),
                   (lambda f: f.seal.update(bindings={}), "verify_predictor_seal"),
                   (lambda f: f.seal.update(battery_hash=f.seal.pop("battery_sha256")), "verify_predictor_seal"),
                   (lambda f: f.power.update(power_hash=f.power.pop("power_sha256")), "verify_power"),
                   (lambda f: f.power.update(records=f.power.pop("record")), "verify_power"),
                   (lambda f: f.complete.update(complete_sha256=digest(b"forged")), "verify_complete"),
                   (lambda f: f.complete.update(bindings={"../escape": digest(b"forged")}), "verify_complete")]
        for attack, method in attacks:
            with self.subTest(method=method), self.fixture() as f:
                attack(f)
                self.assert_refused(self.probe(f, lambda a, _: getattr(a, method)()))

    def test_adapter_authority_and_named_provenance_forgery_refuse(self):
        with self.fixture() as f:
            f.authority["collection_bindings"]["trust_sha256"] = digest(b"different authority")
            f.save_authority()
            self.assert_refused(self.probe(f, lambda a, _: self.fail("entered")), "independent collection identity")
        with self.fixture() as f:
            old = f.statistics_bindings
            def forged(s):
                result = old(s); result["input_sha256"].pop("source_manifest"); return result
            f.statistics_bindings = forged
            self.assert_refused(self.probe(f, lambda a, _: self.fail("entered")), "named source identity")

    def test_power_real_inventory_and_calibration_sha_no_outcomes_read(self):
        with self.fixture(stage="power") as f:
            def check(a, provenance):
                inventory = provenance["contact_inventory"]
                self.assertGreater(len(inventory["entries"]), 1)
                self.assertEqual(provenance["input_sha256"]["contact_inventory"], digest(inventory))
                self.assertIn("claims/power.json", {r["path"] for r in inventory["entries"]})
                a.verify_predictor_seal()
                with self.assertRaises(Refusal):
                    a.outcomes()
            result = self.probe(f, check, name="power")
            self.assertEqual(result["state"], "COMPLETE", result)
            self.assertNotIn("outcome_draws", f.events)

    def test_power_missing_or_different_calibration_refuses_before_predictors(self):
        for change in (lambda f: (f.root/"statistics/calibration/calibration.json").unlink(),
                       lambda f: (f.root/"statistics/calibration/calibration.json").write_bytes(b"changed")):
            with self.fixture(stage="power") as f:
                change(f)
                self.assert_refused(self.probe(f, lambda a, _: a.predictor_data(), name="power"))
                self.assertNotIn("predictor_draws", f.events)

    def test_power_all_outcome_contact_paths_and_unknown_markers_refuse(self):
        paths = ("units/outcome", "units/endpoint", "units/outcome-anchors", "contacts/outcome", "probes/new.json",
                 "loads/failed.json", "operations/probe.json", "claims/custom.CLAIM", "phases/new.json", "misc/unknown.json")
        for name in paths:
            with self.subTest(name=name), self.fixture(stage="power") as f:
                put(f.root, name+"/marker" if name.startswith("units/") or name == "contacts/outcome" else name, b"unknown contact")
                self.assert_refused(self.probe(f, lambda a, _: a.predictor_data(), name="power"))
                self.assertNotIn("predictor_draws", f.events)

    def test_power_pinned_future_grant_cannot_be_mislabeled(self):
        for metadata in ({"stage": "outcome-preflight"}, {"scope": "outcome-collection"}, {"stage": "unrecognized"},
                         {"stage": "predictor-collection", "subject": "SmolLM3-3B"}):
            with self.fixture(stage="power") as f:
                sha = put(f.root, "grants/future.json", metadata)
                f.authority["power_inventory"]["entries"].append({"path": "grants/future.json", "phase": "predictor", "kind": "grant", "sha256": sha})
                f.save_authority()
                self.assert_refused(self.probe(f, lambda a, _: a.predictor_data(), name="power"))

    def test_power_accepts_independently_pinned_actual_predictor_grant(self):
        with self.fixture(stage="power") as f:
            sha = put(f.root, "grants/future.json", {"scope": "predictor-collection", "subject": "twin"})
            f.authority["power_inventory"]["entries"].append({"path": "grants/future.json", "phase": "predictor", "kind": "grant", "sha256": sha})
            f.save_authority()
            self.assertEqual(self.probe(f, lambda a, _: None, name="power")["state"], "COMPLETE")

    def test_power_transient_new_and_collection_exit_markers_refuse(self):
        for transient, at_exit in ((False, False), (True, False), (False, True), (True, True)):
            with self.fixture(stage="power") as f:
                def mutate(*_):
                    p = f.root/"probe-transient.json"
                    p.write_bytes(b"outcome contact")
                    if transient:
                        p.unlink()
                if at_exit:
                    f.hooks["exit"] = mutate
                self.assert_refused(self.probe(f, (lambda a, _: None) if at_exit else mutate, name="power"))
                self.assertFalse((f.root/"statistics/power/COMPLETE.json").exists())

    def test_power_symlink_unknown_empty_directory_and_halted_refuse(self):
        attacks = (lambda f: (f.root/"operations").symlink_to(f.root/"absent", target_is_directory=True),
                   lambda f: (f.root/"unknown-empty-probe").mkdir(),
                   lambda f: put(f.root, "operations/HALTED.json", b"failed"))
        for attack in attacks:
            with self.fixture(stage="power") as f:
                attack(f)
                self.assert_refused(self.probe(f, lambda a, _: None, name="power"))

    def test_calibration_must_use_standalone_context(self):
        with self.fixture() as f:
            put(f.root, "statistics/calibration/CLAIM.json", {"stage": "calibration"})
            with self.assertRaisesRegex(Refusal, "standalone"):
                with f.adapter().entryexit("calibration"):
                    self.fail("collection calibration entered")
            self.assertEqual(f.events, [])

    def test_external_repository_roots_are_enumerated_and_semantically_classified(self):
        for metadata in ({"scope": "predictor-preflight"}, {"scope": "outcome-preflight"}, {"stage": "unknown"}):
            with self.fixture(stage="power") as f:
                name = "custom-grants/owner.json"
                sha = put(f.repo, name, metadata)
                spec = f.authority["power_inventory"]
                spec["repository_roots"].append("custom-grants")
                spec["entries"].append({"path": "repository/"+name, "phase": "predictor", "kind": "grant", "sha256": sha})
                f.save_authority()
                result = self.probe(f, lambda a, _: None, name="power")
                self.assertEqual(result["state"], "COMPLETE" if metadata == {"scope": "predictor-preflight"} else "INSUFFICIENT_DATA")

    def test_external_repository_unknown_and_transient_contact_refuse(self):
        for transient in (False, True):
            with self.fixture(stage="power") as f:
                folder = f.repo/"probes"; folder.mkdir(exist_ok=True)
                def mutate(a, provenance):
                    path = folder/"hidden.json"
                    path.write_bytes(b'{"scope":"outcome-preflight"}')
                    if transient: path.unlink()
                self.assert_refused(self.probe(f, mutate, name="power"))
                self.assertFalse((f.root/"statistics/power/COMPLETE.json").exists())

    def test_real_grant_parent_must_be_in_external_inventory(self):
        from types import SimpleNamespace
        with self.fixture(stage="power") as f:
            f.trust = SimpleNamespace(data={"grants": {"power": {"path": "unlisted-root/power.json"}}})
            self.assert_refused(self.probe(f, lambda a, _: None, name="power"), "grant root omitted")
