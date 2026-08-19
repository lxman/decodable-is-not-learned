"""Unit fixtures for the committed power record (doc Open items 2, 3):
the frozen λ rule reproduces from the §4 pins, m_min and the
best-case table agree with the machinery, and the declaration line is
arithmetic, not judgment. The full byte-identity re-run is a freeze
cold-battery item (compute_power_3c's convention)."""
import json

import pytest

from experiments.exp3d import analyze_3d as d
from experiments.exp3d import compute_power_3d as cp
from experiments.exp3d import rank_test_3d as rt

REC = json.loads(d.POWER_PATH.read_text())


def test_lambda_rule_reproduces_from_pins():
    lam = cp.lambda_hat()
    mu = 10 / 500
    ec2 = 18 / 500
    var = ec2 - mu * mu
    assert lam["lambda"] == pytest.approx(mu * mu / (var - mu))
    assert REC["lambda"]["lambda"] == pytest.approx(lam["lambda"])


def test_m_min_and_best_case_table():
    assert REC["m_min"] == 1
    row = REC["best_case_table"][0]
    assert row["m"] == 1 and row["rejects_at_alpha"]
    # m_min = 1 lands in the len-6 stratum: 'rxxxxd' is the unique
    # cheapest len-6 item, p = 1/151
    assert row["best_composition"] == {"4": 0, "5": 0, "6": 1}
    assert row["best_case_p"] == pytest.approx(1 / 151)


def test_frozen_seeds_and_counts():
    assert REC["alpha"] == rt.ALPHA_3D
    assert REC["mc_permutation"]["count"] == rt.MC_PERM_COUNT
    assert REC["mc_permutation"]["seed"] == rt.MC_PERM_SEED
    assert REC["power_sim"]["seed"] == cp.POWER_SIM_SEED
    assert REC["power_sim"]["n_sims"] == cp.POWER_SIM_M


def test_declaration_is_arithmetic():
    p = REC["power_at_observed_concentration_1b"]
    assert REC["declared_underpowered_in_advance"] == (p < 0.75)
    assert REC["declared_underpowered_in_advance"] is True


def test_null_inputs_carry_the_strata():
    ni = REC["null_inputs"]
    assert {k: v["n_items"] for k, v in ni.items()} == \
        {"4": 194, "5": 155, "6": 151}
    for v in ni.values():
        assert len(v["doubled_midranks_multiset"]) == v["n_items"]


def test_alternative_rates_normalize_to_cell_rate():
    lam = REC["lambda"]["lambda"]
    for size in d.SIZES_3D:
        r = cp.alternative_rates(size, lam, 1.0)
        cell = sum(d.COMMITTED_FIRE_COUNTS[size].values()) \
            / d.COMMITTED_BASE_DRAWS[size]
        assert r.mean() == pytest.approx(cell)
        assert (r > 0).all()
    flat = cp.alternative_rates("1b", 1.0, 0.0)
    assert flat.min() == pytest.approx(flat.max())


def test_flat_row_is_null_calibrated():
    w = REC["cells"]["1b"]["FLAT_committed_rate"]["worlds"]
    assert w["STRUCTURED"] <= 0.055     # ≈ α, discreteness-conservative
    assert w["STRUCTURED"] >= 0.035
