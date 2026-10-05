"""SR1–SR5 failures against v1. Saved arithmetic only; no RNG/driver calls."""
from copy import deepcopy
from dataclasses import asdict
from fractions import Fraction as F
from pathlib import Path
import importlib
import sys
import tempfile
import unittest
from exp7core.contract import Refusal
from exp7core.scoring import Score, Table
from exp7core.records import strict_json
from exp7stats.common import SCHEMA, PRODUCTION, FAMILIES, PREDICTORS, digest, dumps
from exp7stats.data import Predictor, predictor_support, load_battery
from exp7stats.power import SPEC, grid, cell_id, SUBSETS, declarations, verify_power_semantics
from exp7stats.calibration import envelope_grid, prompt_probabilities, verify_envelope_semantics
from exp7stats.kernels import decision
import test_integration_boundaries as ib
from stats_fixtures import payloads, WORK


def legacy_envelope():
    rows = {}
    for i, pattern, n, delta in envelope_grid():
        name = f"E{i}/f{n}/delta{delta.numerator}_{delta.denominator}"
        row = {"id": name, "pattern": pattern, "families": n, "delta": delta}
        probabilities = [prompt_probabilities(*v[:2], v[2], delta) for v in pattern]
        if any(p["status"] != "SUPPORTED" for p in probabilities):
            row.update(status="UNSUPPORTED", N=0)
        elif all(v[0] == 0 or v[1] == 0 for v in pattern):
            row.update(status="ANALYTIC-ZERO-SUPPORT", N=0, p_fires=F(0))
        else:
            row.update(status="SIMULATED", N=128, fire_count=0, p_fires=F(0), p_only_count=999,
                       p_only_fraction=F(999), mean_x=F(999), mean_u=F(-999),
                       unsupported_render_fraction=F(-1), interval95=(1, 1))
        rows[name] = row
    return rows


def legacy_power():
    s = Score(Table(32, 32, 32, 32, 64), Table(32, 32, 32, 32, 64))
    ps = {p: Predictor(p, (), tuple((f, (s,)*500) for f in FAMILIES),
                       tuple((f, ("block",)*500) for f in FAMILIES), ()) for p in PREDICTORS}
    rows = {}
    for p, subset, n, m, target in grid():
        d = target if target is not None else F(0)
        bound = decision(0 if target is not None else 10000, 10000, 10000)
        summary = lambda v, n: {"Ds": [v]*n, "mean_D": v}
        fit = {"status": "SUPPORTED", "rho": .5 if target is not None else 0., "target": target,
               "iterations": 24, "tolerance": SPEC.tolerance, "mean_D": d,
               "null_fit": summary(F(0), 64), "ceiling_fit": summary(F(1), 64),
               "final_fit": summary(d, 64), "validation": summary(d, 128)}
        name = cell_id(p, subset, n, m, target)
        rows[name] = {"id": name, "predictor": p, "subset": subset, "n_positive": n, "max_count": m,
                      "target_D": target, "status": "SUPPORTED", "N": 128, "Ds": [d]*128, "mean_D": d,
                      "eligibility": [{"eligible": subset}]*128,
                      "permutation_bounds": [{k: bound[k] for k in ("p", "p_low", "p_high", "n_ge", "consumed", "B")}]*128,
                      "fire_count": 128 if target is not None else 0, "p_only_count": 128 if target is not None else 0,
                      "p_fires": F(1) if target is not None else F(0), "permutations_consumed": 1280000, "fit": fit}
    record = {"schema": SCHEMA, "stage": "power", "state": "COMPLETE", "production": True,
              "seal_sha256": "d"*64, "battery_sha256": "a"*64, "spec": asdict(SPEC), "grid": PRODUCTION.grid,
              "rows": rows, "declarations": declarations(rows), "run_stop_required": False,
              "thin_fixtures": {f"{p}/{'-'.join(s)}": {"state": "THIN", "predictor": p, "subset": s,
                                                       "n_positive": 10, "eligible": ()} for p in PREDICTORS for s in SUBSETS},
              "source_bindings": {"code_manifest": "1"*64, "source_manifest": "2"*64,
                                  "calibration": "3"*64, "contact_inventory": "4"*64},
              "calibration_sha256": "3"*64, "selectivity_envelope": legacy_envelope(),
              "predictor_support": {p: predictor_support(ps[p]) for p in PREDICTORS}}
    return record


class SRRegressionTests(unittest.TestCase):
    def candidate(self):
        helper = ib.IntegrationBoundaryTests()
        helper.setUp()
        self.addCleanup(helper.doCleanups)
        return helper.candidate()

    def test_SR1_external_persistent_and_transient_helpers_refuse(self):
        for transient in (False, True):
            ctx, content = self.candidate()
            outside = ctx.repo.parent/"outside"
            outside.mkdir()
            name = "sr_unbound_transient" if transient else "sr_unbound_persistent"
            (outside/f"{name}.py").write_text("MARKER = 'UNPINNED-EXECUTED'\n")
            sys.path.insert(0, str(outside))
            try:
                with self.assertRaisesRegex(Refusal, "(pinned source|unpinned external)"):
                    with ctx.entryexit("calibration"):
                        importlib.import_module(name)
                        if transient:
                            sys.modules.pop(name)
            finally:
                sys.path.remove(str(outside)); sys.modules.pop(name, None)

    def test_SR3_pinned_cold_import_absent_cache_succeeds(self):
        ctx, content = self.candidate()
        name = "sr_pinned_late_helper"
        content[f"{name}.py"] = b"MARKER = 'PINNED'\n"
        (ctx.repo/f"{name}.py").write_bytes(content[f"{name}.py"])
        manifest = strict_json(content["manifest.json"])
        manifest["files"][f"{name}.py"] = {"kind": "source", "sha256": digest(content[f"{name}.py"])}
        content["manifest.json"] = dumps(manifest)
        (ctx.repo/"manifest.json").write_bytes(content["manifest.json"])
        ctx.manifest_sha = digest(content["manifest.json"])
        sys.path.insert(0, str(ctx.repo))
        try:
            with ctx.entryexit("calibration"):
                self.assertEqual(importlib.import_module(name).MARKER, "PINNED")
        finally:
            sys.path.remove(str(ctx.repo)); sys.modules.pop(name, None)

    def test_SR2_default_constant_geometry_cannot_claim_positive_D(self):
        with self.assertRaises(Refusal):
            verify_power_semantics(legacy_power(), "d"*64, "a"*64)

    def test_SR2_subset_loss_cannot_retain_defined_D(self):
        r = legacy_power()
        row = next(v for v in r["rows"].values() if v["target_D"] == F(3, 20))
        row["eligibility"] = [deepcopy(v) for v in row["eligibility"]]
        row["permutation_bounds"] = [deepcopy(v) for v in row["permutation_bounds"]]
        row["eligibility"][0]["eligible"] = row["subset"][:-1]
        row["permutation_bounds"][0] = {"status": "EXACT_SUBSET_LOSS", "eligible": row["subset"][:-1]}
        row.update(fire_count=127, p_only_count=127, p_fires=F(127,128), permutations_consumed=1270000)
        r["declarations"] = declarations(r["rows"])
        with self.assertRaises(Refusal):
            verify_power_semantics(r, "d"*64, "a"*64)

    def test_SR4_impossible_envelope_diagnostics_refuse(self):
        with self.assertRaises(Refusal):
            verify_envelope_semantics(legacy_envelope())

    def test_SR5_production_catalog_20_21_21_22_refuses(self):
        b, _, _ = payloads(n=500, grid=PRODUCTION.grid)
        for fi, f in enumerate(FAMILIES):
            names = [f"method{j}" for j in range((20, 21, 21, 22)[fi])]
            b["baseline_ids"][f] = names
            for row in b["families"][f]:
                row["baselines"] = {name: deepcopy(row["baselines"]["constant"] if sum((20,21,21,22)[:fi])+j < 49
                                                   else row["baselines"]["not_applicable"]) for j, name in enumerate(names)}
        b["baseline_coverage"] = {"applicable_cells": 49, "not_applicable_cells": 35}
        with self.assertRaises(Refusal):
            load_battery(b)
