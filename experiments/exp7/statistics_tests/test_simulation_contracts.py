from dataclasses import replace
from fractions import Fraction as F
import unittest
import numpy as np
from exp7core.contract import Refusal
from exp7core.inference import eligibility
from exp7stats.common import FAMILIES, PREDICTORS, Shape, digest
from exp7stats.data import load_battery, load_predictors
from exp7stats.power import (grid, SPEC as POWER_SPEC, PowerSpec, fit_target, LatentBank,
                            assemble, declarations, verify_power_semantics, run as power_run, thin_fixture, SUBSETS)
from exp7stats.calibration import (null_case, TRUE_NULLS, CASES, envelope_grid, prompt_probabilities,
                                  exact_binomial_tail, case_record, CalibrationSpec, assemble as calibration_assemble)
from stats_fixtures import payloads, FakeCampaign, WORK
from pathlib import Path
import tempfile


class SimulationContractTests(unittest.TestCase):
    def test_finite_grid_exact_counts_without_running_grid(self):
        rows = list(grid())
        self.assertEqual(sum(r[-1] is None for r in rows), 80)
        self.assertEqual(sum(r[-1] is not None for r in rows), 240)
        self.assertEqual(len({str(r) for r in rows}), 320)
        cells = list(envelope_grid())
        impossible = sum(any(prompt_probabilities(*row[:2], row[2], d)["status"] == "UNSUPPORTED" for row in pattern)
                         for _, pattern, _, d in cells)
        self.assertEqual((len(cells), impossible), (80, 16))

    def test_one_small_draw_of_each_true_null_generator_no_frequency(self):
        for case in CASES:
            generated = null_case(case, 0, n=120)
            self.assertEqual(generated["true_nulls"], TRUE_NULLS[case])
            for p in PREDICTORS:
                self.assertEqual(eligibility(generated["cells"][p])[0], FAMILIES)
            if case in ("N5", "N6"):
                for c in generated["cells"][PREDICTORS[0]]:
                    self.assertGreater(len(set(c.y)), len(set(c.strata)))
            if case == "N9":
                for a, b in zip(generated["cells"][PREDICTORS[0]], generated["cells"][PREDICTORS[1]]):
                    self.assertEqual(a.strata, b.strata)
                    self.assertEqual(a.x, b.x)
                    blocks = generated["N9_blocks"][a.family]
                    self.assertEqual(sum(len(v["indices"]) for v in blocks), 120)
                    self.assertEqual(sum(v["n_positive"] for v in blocks), sum(y > 0 for y in a.y))

    def test_N9_conditional_law_uniform_assignment_enumeration(self):
        # Exhaustive small block: each permutation assigns the same y multiset;
        # composing with any fixed predictor permutation is a bijection.
        from itertools import permutations
        values = (0, 0, 1, 3)
        all_assignments = [tuple(values[i] for i in order) for order in permutations(range(4))]
        transform = (2, 0, 3, 1)
        transformed = [tuple(row[i] for i in transform) for row in all_assignments]
        self.assertEqual(sorted(all_assignments), sorted(transformed))

    def test_case_failure_is_not_skipped_or_denominator_changed(self):
        calls = []
        def fail(case, replicate, spec):
            calls.append(replicate)
            raise Refusal("eligibility not all four")
        result = case_record("N5", CalibrationSpec(n=120, replicates=2, permutations=3, envelope_replicates=2), evaluator=fail)
        self.assertEqual(result["status"], "CASE_FAILURE")
        self.assertIsNone(result["frequencies"])
        self.assertEqual(calls, [0])

    def test_aggregate_final_fit_None_and_validation_None_are_total(self):
        spec = PowerSpec(n_sim=2, n_cal=1, n_validate=1, iterations=1, permutations=3,
                         positive_counts=(20,), count_ranges=(3,), targets=(F(3, 20),))
        calls = []
        def evaluate(rho):
            calls.append(rho)
            value = None if rho == .25 else F(-1) if rho == 0 else F(1)
            return {"mean_D": value}
        result = fit_target(evaluate, lambda rho: self.fail("validation must not run"), F(3, 20), spec)
        self.assertEqual(result["status"], "UNSUPPORTED")
        self.assertIn("final", result["reason"])
        self.assertEqual(calls, [0., 1., .5, .25])
        spec = replace(spec, tolerance=F(1, 2))
        result = fit_target(lambda rho: {"mean_D": F(0) if rho == 0 else F(3, 20)},
                            lambda rho: {"mean_D": None}, F(3, 20), spec)
        self.assertEqual(result["status"], "UNSUPPORTED")
        self.assertIn("validation", result["reason"])

    def test_latent_bank_counts_and_constant_ties_no_power_estimate(self):
        b, p, _ = payloads(mode="constant")
        shape = Shape(n=24, grid=(1, 2, 3), permutations=3, bootstraps=1)
        battery = load_battery(b, shape)
        pred = load_predictors(p, battery, shape)[PREDICTORS[0]]
        bank = LatentBank(pred, FAMILIES[:3], n_reps=2, namespace="miniature-bank")
        ys = bank.outcomes(1., 20, 3)
        for values in ys.values():
            self.assertEqual(np.count_nonzero(values, axis=1).tolist(), [20, 20])
            self.assertTrue(np.all(values <= 3))
        self.assertEqual(bank.means(1., 20, 3)["mean_D"], 0)

    def test_all_power_addresses_with_scripted_unsupported_not_simulation(self):
        b, p, _ = payloads()
        shape = Shape(n=24, grid=(1, 2, 3), permutations=3, bootstraps=1)
        battery = load_battery(b, shape)
        predictors = load_predictors(p, battery, shape)
        seen = []
        from exp7stats.power import cell_id
        def scripted(pred, subset, n, m, target, spec):
            name = cell_id(pred.name, subset, n, m, target)
            seen.append(name)
            return {"id": name, "predictor": pred.name, "subset": subset, "n_positive": n,
                    "max_count": m, "target_D": target, "status": "UNSUPPORTED", "N": 0,
                    "p_fires": None, "mean_D": None, "reason": "scripted coverage fixture, no simulation"}
        result = assemble(predictors, battery, {"seal_sha256": "d"*64},
                          {"input_sha256": {"synthetic": "f"*64}}, evaluator=scripted)
        self.assertEqual(len(seen), 320)
        self.assertEqual(len(result["declarations"]), 10)
        self.assertTrue(all(v["status"] != "FORECAST-POWERED" for v in result["declarations"].values()))
        self.assertTrue(result["run_stop_required"])
        self.assertEqual(len(result["thin_fixtures"]), 10)
        self.assertTrue(all(row["state"] == "THIN" for row in result["thin_fixtures"].values()))

    def test_saved_power_arithmetic_rederived_without_simulations(self):
        from copy import deepcopy
        from saved_fixtures import power_record
        spec = PowerSpec(n_sim=1, n_cal=1, n_validate=1, iterations=1, permutations=3,
                         positive_counts=(20,), count_ranges=(3,), targets=(F(3, 20),))
        r, geometry = power_record(spec=spec, n=24, mode="constant")
        self.assertIsNotNone(verify_power_semantics(r, "d"*64, "a"*64, geometry=geometry, spec=spec))
        bad = deepcopy(r)
        key = next(k for k in bad["rows"] if k.endswith("/null"))
        bad["rows"][key]["fire_count"] = 1
        bad["rows"][key]["p_fires"] = F(1)
        with self.assertRaises(Refusal):
            verify_power_semantics(bad, "d"*64, "a"*64, geometry=geometry, spec=spec)

    def test_power_refuses_preexisting_outcome_before_data_read(self):
        with tempfile.TemporaryDirectory(dir=WORK) as directory:
            campaign = FakeCampaign(directory)
            (Path(directory)/"outcomes").mkdir()
            result = power_run(campaign)
            self.assertEqual(result["state"], "INSUFFICIENT_DATA")
            self.assertEqual(campaign.events, [("entry", "power")])

    def test_exact_binomial_tail_hand_enumeration(self):
        self.assertEqual(exact_binomial_tail(3, 4, F(1, 2)), F(5, 16))
        self.assertEqual(exact_binomial_tail(0, 4, F(1, 200)), 1)

    def test_calibration_scripted_coverage_and_envelope_failure_no_simulation(self):
        seen = []
        def scripted(case, b, spec):
            seen.append((case, b))
            return {"components": {f"{p}/{c}": {"p_reject": False, "fires": False} for p, c in TRUE_NULLS[case]},
                    "union": False}
        def envelope(i, pattern, n, d, spec):
            return {"id": f"E{i}/f{n}/delta{d.numerator}_{d.denominator}", "status": "SCRIPTED-NO-SIMULATION"}
        spec = CalibrationSpec(n=120, replicates=2, permutations=3, envelope_replicates=2)
        r = calibration_assemble(spec, evaluator=scripted, envelope_evaluator=envelope)
        self.assertEqual(len(seen), 18)
        self.assertEqual(set(r["cases"]), set(CASES))
        self.assertEqual(len(r["selectivity_envelope"]), 80)
        self.assertEqual(r["state"], "NO-DETECTED-CALIBRATION-DEFECT")
        def fail(*args):
            raise ValueError("scripted case-generation defect")
        r = calibration_assemble(spec, evaluator=scripted, envelope_evaluator=fail)
        self.assertEqual(r["state"], "CALIBRATION-FAILED")
        self.assertEqual(sum(v["status"] == "CASE_FAILURE" for v in r["selectivity_envelope"].values()), 1)
        self.assertEqual(sum(v["status"] == "NOT-RUN-AFTER-CASE-FAILURE" for v in r["selectivity_envelope"].values()), 79)
