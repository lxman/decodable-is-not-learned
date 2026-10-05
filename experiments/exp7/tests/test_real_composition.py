"""Actual collection producers -> adapter -> full-cardinality miniature stats.

All generated continuations, Git/host/owner records and model sessions are
explicit test doubles. The battery and 84-cell baseline catalog are the actual
certified saved artifacts, reverified model-free. No production statistical API
is invoked. A test-only Campaign subclass admits production:false MINIATURE
power; its saved arithmetic is independently validated with the real validator.
"""
from pathlib import Path
from copy import deepcopy
from contextlib import contextmanager
from fractions import Fraction
import tempfile
import json
import unittest
from exp7core.contract import ARMS, FAMILIES, GRID, canonical, require, Refusal
from exp7core.battery_adapter import load_certified, PREFIX
from exp7core.campaign import Campaign
from exp7core.records import strict_json
from exp7core.collectors import collect_predictor, seal_predictors, collect_endpoint, collect_outcomes, complete_campaign
from exp7core.preflight import predictor_preflight, validate_caps
from exp7stats.common import Shape, SCHEMA, CONTACT_ROOTS, digest, dumps, decode, stage
from exp7stats.data import load_battery, load_predictors
from exp7stats.power import PowerSpec, assemble, verify_power_semantics
from exp7stats.analyzer import _operation
from exp7integration.adapter import StatsCampaignAdapter, sealed_predictor_geometry
from collection_fixtures import fixture, FakeSession, FakeGit, C
from collection_fixture import ROOT, put
from testing_paths import PACKAGE, CONTRACTS

WORK = ROOT / "test-work"
REPO = Path("/Users/michaeljordan/emergence-paper")
MINI_SHAPE = Shape(n=500, grid=GRID, permutations=3, bootstraps=1)
MINI_POWER = PowerSpec(n_sim=1, n_cal=1, n_validate=1, iterations=1, permutations=3,
                       positive_counts=(20,), count_ranges=(3,), targets=(Fraction(3, 20),))


def verify_miniature_power(record, seal, battery, *, geometry):
    require(record.get("production") is False and record.get("fixture") is True, "miniature power only")
    # Strict statistics validator has a production marker even with an explicit
    # miniature spec. Validate an IN-MEMORY copy; never publish production:true.
    checked = verify_power_semantics({**record, "production": True}, seal, battery, spec=MINI_POWER, geometry=geometry)
    require(checked["spec"] == decode(record)["spec"], "miniature spec preserved")
    return None


class SyntheticPowerCampaign(Campaign):
    """One explicit test seam: stock collection requires production:true power.

    Preserve its byte/commit/source/seal gates while requiring the opposite
    marker and the actual miniature statistical semantics. All raw collection,
    grant entry/exit, seals and full completion rederivation are stock methods.
    """
    def verify_power(self):
        self.verify_predictor_seal()
        d, e = self.trust.data, self.trust.data["power"]
        raw = self.trust.read_root(e["path"])
        require(digest(raw) == e["sha256"], "miniature power immutable byte pin")
        value = decode(strict_json(raw))
        require(value["source_bindings"]["code_manifest"] == d["code_manifest_sha256"] and
                value["source_bindings"]["source_manifest"] == d["source_manifest_sha256"], "miniature source bindings")
        _, geometry = sealed_predictor_geometry(self)
        verify_miniature_power(value, d["predictor_seal"]["sha256"], self.battery().bytes_sha256, geometry=geometry)
        self.trust.git.ancestor(d["predictor_tag"]["commit"], e["commit"])
        name = (self.root/e["path"]).relative_to(self.repo).as_posix()
        self.trust.git.blob(e["commit"], name, e["sha256"])
        return value


class FullCardinalityMiniatureAdapter(StatsCampaignAdapter):
    def _dimensions(self):
        return 500, GRID, False

    def _source_paths(self):
        # Runtime source lives in the copied, guarded annex rather than the tiny
        # fake Git repo. This exception is confined to the test class.
        return {p.relative_to(PACKAGE).as_posix(): p for package in ("exp7core", "exp7stats", "exp7ops", "exp7integration")
                for p in (PACKAGE/package).rglob("*.py")}


class CertifiedSession(FakeSession):
    def __init__(self, c, load):
        super().__init__(c, load)
        self.lookup = {prompt: (p, j) for p in c.battery().pairs for j, prompt in enumerate(p.prompts)}

    def sample(self, prompt, **kw):
        if kw["rung"] in ("add_base8", "sub_base8", "ctrl_copy"):
            return super().sample(prompt, **kw)
        p, j = self.lookup[prompt]
        require(p.index == kw["item_idx"] and kw["rung"] == f"exp7/{p.family}/{ARMS[j]}", "fake session address")
        n = kw["draws_per_seed"]
        hits = 40+p.index%25 if n == 64 else 0
        correct, wrong = p.targets[j%2], p.targets[1-j%2]
        self.calls.append(prompt)
        return {z: [correct]*hits+[wrong]*(n-hits) for z in kw["seeds"]}

    def greedy(self, prompts, cap):
        self.calls.extend(prompts)
        step = int(self.spec["model"].split("/")[1])
        result = []
        for prompt in prompts:
            if prompt not in self.lookup:
                result.append("1")  # independently pinned fake OLD anchor fixture
            else:
                p, j = self.lookup[prompt]
                result.append(p.targets[j%2] if p.index%26 <= GRID.index(step) else "MISS")
        return result


class CertifiedBackend:
    def __init__(self, c):
        self.c, self.opened = c, []

    def open(self, load):
        value = CertifiedSession(self.c, load)
        self.opened.append(value)
        return value


def authority(c, path, stage_name, *, adapter_class=FullCardinalityMiniatureAdapter):
    bindings = c.bindings_unopened()
    data = c.trust.data
    entries = []
    if stage_name == "power":
        for p in sorted(c.root.rglob("*")):
            if p.is_file():
                name = p.relative_to(c.root).as_posix()
                phase = "calibration" if name.startswith("statistics/calibration/") else "predictor"
                entries.append({"path": name, "phase": phase, "kind": "unit" if name.startswith("units/") else "operation", "sha256": digest(p.read_bytes())})
        for p in sorted((c.repo/"grants").rglob("*")):
            if p.is_file():
                value = strict_json(p.read_bytes())
                entries.append({"path": "repository/"+p.relative_to(c.repo).as_posix(), "phase": value["scope"].split("-")[0],
                                "kind": "grant", "sha256": digest(p.read_bytes())})
        power_grant = data["grants"]["power"]["canonical_sha256"]
        entries.append({"path": "claims/power.CLAIM", "phase": "power", "kind": "phase", "sha256": digest({"grant_sha256": power_grant})})
    adapter = adapter_class(c, authority_path=path, authority_sha256=digest(b"test-only not-yet-enrolled authority"))
    value = {"schema": "exp7.adapter-authority.v1", "collection_bindings": bindings,
             "adapter_sources": {name: digest(p.read_bytes()) for name, p in adapter._source_paths().items()},
             "receipts": {"seal_sha256": data["predictor_seal"]["sha256"],
                          **({"power_sha256": data["power"]["sha256"], "complete_sha256": data["complete"]["sha256"]} if stage_name == "analysis" else {})},
             "power_inventory": {"covered_roots": list(CONTACT_ROOTS)+["receipts", "preflight", "units/predictor", "units/anchors"],
                                 "repository_roots": list(CONTACT_ROOTS)+["receipts", "preflight"], "entries": entries},
             "calibration_sha256": data["calibration"]["sha256"]}
    sha = put(path.parent, path.name, value)
    return adapter_class(c, authority_path=path, authority_sha256=sha)


class RealCompositionTests(unittest.TestCase):
    def test_certified_full_collection_adapter_statistics_chain(self):
        pins = json.loads((CONTRACTS/"collection-source-pins.json").read_bytes())
        def certified_read(path):
            raw = (REPO/path).read_bytes()
            self.assertEqual(digest(raw), pins[path])
            return raw
        battery, _, _, baseline = load_certified(certified_read)
        with tempfile.TemporaryDirectory(dir=WORK) as tmp:
            outer = Path(tmp)
            repo = outer/"repo"; repo.mkdir()
            f = fixture(repo, with_caps=True)
            f.battery = battery
            f.data["battery_sha256"] = battery.bytes_sha256
            f.data["levels_sha256"] = battery.levels_sha256
            class FakeCharacterTokenizer:
                all_special_ids = [0]
                def encode(self, text, add_special_tokens=True):
                    return list(map(ord, text))
                def decode(self, ids, skip_special_tokens=True):
                    return "".join(map(chr, ids))
            caps = validate_caps(battery, FakeCharacterTokenizer())
            for key in ("pythia_1b", "olmo2_1b"):
                value = {**caps, "assets": f.data["assets"][key]}
                path = f.data["cap_receipts"][key]
                sha = put(repo, path, value)
                f.data["repo_pins"][path] = f.data["prereg"]["bindings"][path] = sha
            for name in ("baseline-outputs.jsonl", "baselines.json"):
                sha = put(repo, PREFIX+name, certified_read(PREFIX+name))
                f.data["repo_pins"][PREFIX+name] = sha
            calibration_name = "statistics/calibration/calibration.json"
            calibration_sha = put(f.root, calibration_name, {"fixture": True, "production": False, "stage": "calibration", "note": "No production calibration executed"})
            f.data["calibration"] = {"path": calibration_name, "sha256": calibration_sha, "commit": C}
            f.data["repo_pins"]["campaign/"+calibration_name] = calibration_sha
            f.data["prereg"]["bindings"]["campaign/"+calibration_name] = calibration_sha

            def campaign():
                original = f.campaign()
                c = SyntheticPowerCampaign(f.root, repo, trust_path=f"trust-{f.serial}.json", trust_sha256=original.trust.sha, git=FakeGit())
                c._battery, c._baselines = battery, baseline
                return c

            # Real full-shape producers, replays, anchors and seal; fake sessions.
            with campaign() as c:
                for model in ("pythia_1b", "olmo2_1b", "twin"):
                    predictor_preflight(c, model, backend=CertifiedBackend(c))
                    collect_predictor(c, model, backend=CertifiedBackend(c))
                seal = seal_predictors(c)
                self.assertEqual(seal["new_draws"], 1152000)
            f.refresh_seal()
            f.stage_grant("power")
            c = campaign()
            adapter = authority(c, outer/"power-authority.json", "power")
            def power_operation(provenance):
                b = load_battery(adapter.battery())
                self.assertEqual(dict(b.baseline_coverage), {"applicable_cells": 49, "not_applicable_cells": 35})
                ps = load_predictors(adapter.predictor_data(), b)
                record = assemble(ps, b, adapter.verify_predictor_seal(), provenance, spec=MINI_POWER)
                return {**record, "fixture": True}
            result = stage(adapter, "power", power_operation, production=False)
            self.assertEqual(result["state"], "COMPLETE", result)
            self.assertIs(result["production"], False)
            with campaign() as verification:
                _, geometry = sealed_predictor_geometry(verification)
            verify_miniature_power(result, f.data["predictor_seal"]["sha256"], battery.bytes_sha256, geometry=geometry)
            corrupt = deepcopy(result)
            corrupt["declarations"].pop(next(iter(corrupt["declarations"])))
            with self.assertRaises(Refusal):
                verify_miniature_power(corrupt, f.data["predictor_seal"]["sha256"], battery.bytes_sha256, geometry=geometry)
            f.data["power"] = {"path": "statistics/power/power.json", "sha256": digest((f.root/"statistics/power/power.json").read_bytes()), "commit": C}
            for scope in ("outcome-preflight", "outcome-collection", "outcome-underpowered-run"):
                f.stage_grant(scope)
            with campaign() as c:
                def verifier(record, collection):
                    _, independent_geometry = sealed_predictor_geometry(collection)
                    return verify_miniature_power(record, collection.trust.data["predictor_seal"]["sha256"], battery.bytes_sha256, geometry=independent_geometry)
                collect_endpoint(c, "fakehost", backend=CertifiedBackend(c), power_validator=verifier)
                collect_outcomes(c, backend=CertifiedBackend(c), power_validator=verifier)
                complete_campaign(c)
            f.refresh_complete()
            f.stage_grant("analysis")
            c = campaign()
            adapter = authority(c, outer/"analysis-authority.json", "analysis")
            # Separate test API: production n/k/grid validation stays literal;
            # only explicit statistics Shape controls miniature B/bootstrap.
            reading = stage(adapter, "analysis", lambda p: _operation(adapter, p, MINI_SHAPE, production=False), production=False)
            self.assertEqual(reading["state"], "COMPLETE", reading)
            self.assertIs(reading["production"], False)
            self.assertEqual(len(reading["secondaries"]), 8)
            self.assertEqual(reading["verification_bindings"]["predictor"], seal["bindings"])
            self.assertTrue((f.root/"claims/analysis.CLAIM").exists())
            self.assertTrue((f.root/"statistics/analysis/COMPLETE.json").exists())
