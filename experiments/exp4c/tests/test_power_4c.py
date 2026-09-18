# experiments/exp4c/tests/test_power_4c.py
"""Task 5 brief step 1: `cell_structure_4c`'s shape, `delta_of_mu_4c`'s
symmetry point and monotonicity, `compute`'s monotonicity across arms
and byte-reproducibility, `main`'s write-once refusal, and the
analyzer's three power-record refusal routes (`cells_sha256`
mismatch, `n_sim` mismatch, bytes not reproduced) exercised directly
against `analyze_4c._power_record_failures_4c` /
`analyze_4c._reproduce_power_4c` — the full-pipeline versions of the
same routes are `test_full_shape_4c.py`'s and `test_totality_4c.py`'s
job."""
from __future__ import annotations

import copy
import json

import pytest

from experiments.exp4c import analyze_4c as an
from experiments.exp4c import battery_4c as bc
from experiments.exp4c import power_4c as pw

pytestmark = pytest.mark.filterwarnings("ignore")

N_SIM_TEST = 200


@pytest.fixture(scope="module")
def structure():
    return pw.cell_structure_4c()


@pytest.fixture(scope="module")
def small_record(structure):
    return pw.compute(structure, n_sim=N_SIM_TEST, seed=0)


# ------------------------------------------------------------- cell structure

def test_cell_structure_shape(structure):
    assert len(structure) == 26
    assert len({c["family"] for c in structure}) == 9
    assert sum(1 for c in structure if c["type"] == "arithmetic") == 17

    n_flat = {c["traj"]: c["n_flat"] for c in structure}
    n_flat_arith = {c["traj"]: c["n_flat_arith"] for c in structure}
    # every cell of a trajectory carries the SAME n_flat/n_flat_arith
    for traj in bc.TRAJECTORIES_4C:
        vals_flat = {c["n_flat"] for c in structure if c["traj"] == traj}
        vals_arith = {c["n_flat_arith"] for c in structure if c["traj"] == traj}
        assert len(vals_flat) == 1 and len(vals_arith) == 1
    assert n_flat["pythia_6.9b"] == 24 and n_flat["olmo2_13b"] == 15
    assert n_flat_arith["pythia_6.9b"] == 19 and n_flat_arith["olmo2_13b"] == 12


def test_cell_structure_matches_the_pins_exactly(structure):
    for traj in bc.TRAJECTORIES_4C:
        want_R = set(bc.RUNG_SET_PIN_4C[traj]["R"])
        got_R = {c["rung"] for c in structure if c["traj"] == traj}
        assert got_R == want_R


def test_cell_structure_is_deterministic(structure):
    again = pw.cell_structure_4c()
    assert again == structure


def test_structure_sha256_is_a_pure_function_of_the_structure(structure):
    a = pw.structure_sha256_4c(structure)
    b = pw.structure_sha256_4c(copy.deepcopy(structure))
    assert a == b
    c = pw.structure_sha256_4c(structure[:-1])
    assert c != a


# ------------------------------------------------------------------- delta

def test_delta_of_mu_symmetry_point():
    assert pw.delta_of_mu_4c(0.5) == 0.0


def test_delta_of_mu_monotone():
    d76 = pw.delta_of_mu_4c(0.76)
    d65 = pw.delta_of_mu_4c(0.65)
    assert d76 > d65 > 0.0
    # and the mirror image below .5 is negative, symmetric
    assert pw.delta_of_mu_4c(0.24) == pytest.approx(-pw.delta_of_mu_4c(0.76), abs=1e-9)


# ---------------------------------------------------------------- simulation

def test_simulate_cells_shape(structure):
    import numpy as np
    rng = np.random.default_rng(0)
    cells = pw.simulate_cells_4c(structure, 0.6, 0.6, rho=0.5, rng=rng)
    assert len(cells) == len(structure)
    for c, s in zip(cells, structure):
        assert c["traj"] == s["traj"] and c["rung"] == s["rung"] and c["family"] == s["family"]
        assert 0.0 <= c["q"] <= 1.0
        if s["type"] == "arithmetic":
            assert c["q_arith"] is None or 0.0 <= c["q_arith"] <= 1.0
        else:
            assert c["q_arith"] is None


def test_simulate_cells_is_seed_deterministic(structure):
    import numpy as np
    rng1 = np.random.default_rng(7)
    rng2 = np.random.default_rng(7)
    c1 = pw.simulate_cells_4c(structure, 0.6, 0.7, rho=0.3, rng=rng1)
    c2 = pw.simulate_cells_4c(structure, 0.6, 0.7, rho=0.3, rng=rng2)
    assert c1 == c2


# -------------------------------------------------------------------- compute

def test_compute_null_p01_below_03(small_record):
    assert small_record["arms"]["null"]["P_01"] <= 0.03


def test_compute_monotone_across_uniform_leads(small_record):
    p_null = small_record["arms"]["null"]["P_01"]
    p60 = small_record["arms"]["uniform_60"]["P_01"]
    p70 = small_record["arms"]["uniform_70"]["P_01"]
    assert p70 > p60 > p_null


def test_compute_discovery_shape_below_uniform_70(small_record):
    assert small_record["arms"]["discovery_shape"]["P_01"] < small_record["arms"]["uniform_70"]["P_01"]


def test_compute_is_byte_reproducible(structure):
    r1 = pw.compute(structure, n_sim=N_SIM_TEST, seed=0)
    r2 = pw.compute(structure, n_sim=N_SIM_TEST, seed=0)
    assert json.dumps(r1, sort_keys=True) == json.dumps(r2, sort_keys=True)


def test_compute_different_seed_differs(structure):
    r1 = pw.compute(structure, n_sim=N_SIM_TEST, seed=0)
    r2 = pw.compute(structure, n_sim=N_SIM_TEST, seed=1)
    assert json.dumps(r1["arms"], sort_keys=True) != json.dumps(r2["arms"], sort_keys=True)


def test_compute_top_level_fields(small_record, structure):
    assert small_record["n_sim"] == N_SIM_TEST
    assert small_record["seed"] == 0
    assert small_record["n_cells"] == 26
    assert small_record["n_families"] == 9
    assert small_record["cells_sha256"] == pw.structure_sha256_4c(structure)
    assert small_record["declaration"] in ("POWERED", "DECLARED UNDERPOWERED IN ADVANCE")
    assert small_record["blind_region"] == pw.BLIND_REGION_4C
    assert small_record["prereg_tag"] == bc.PREREG_TAG_4C
    assert len(small_record["realized_alpha_01"]) == len(pw.RHOS_4C)
    assert len(small_record["realized_alpha_05"]) == len(pw.RHOS_4C)
    json.dumps(small_record, allow_nan=False)  # strict JSON


def test_compute_declaration_reads_the_rho_half_discovery_reading(structure):
    """The declaration is `POWERED` iff the discovery-shape arm's
    rho=.5 (last, ascending) reading clears `POWER_BAR_4C` — verified
    directly against the arm's own top-level P_01 convenience field."""
    rec = pw.compute(structure, n_sim=N_SIM_TEST, seed=0)
    disc = rec["arms"]["discovery_shape"]
    assert disc["by_rho"][-1]["rho"] == 0.5
    assert disc["P_01"] == disc["by_rho"][-1]["P_01"]
    want = "POWERED" if disc["P_01"] >= pw.POWER_BAR_4C else "DECLARED UNDERPOWERED IN ADVANCE"
    assert rec["declaration"] == want


def test_compute_min_detectable_grid_reuses_the_arms(structure):
    rec = pw.compute(structure, n_sim=N_SIM_TEST, seed=0)
    grid = {g["mu"]: g["P_01"] for g in rec["min_detectable_grid"]}
    assert grid[0.60] == rec["arms"]["uniform_60"]["P_01"]
    assert grid[0.65] == rec["arms"]["uniform_65"]["P_01"]
    assert grid[0.70] == rec["arms"]["uniform_70"]["P_01"]


def test_compute_insulated_from_rank_4c_alpha_monkeypatch(structure, monkeypatch):
    """The bars power_4c reads are its OWN hardcoded literals, not
    `rank_4c.ALPHA_4C`/`MARGINAL_4C` — a monkeypatch of those globals
    (as `test_full_shape_4c.test_marginal_terminal_is_reachable_by_
    the_tree` does mid-test) must not move a re-derived power record,
    or the analyzer's byte-reproduction gate would fire on an unrelated
    test's monkeypatch."""
    from experiments.exp4c import rank_4c as rk
    r1 = pw.compute(structure, n_sim=N_SIM_TEST, seed=0)
    monkeypatch.setattr(rk, "ALPHA_4C", 1e-9)
    monkeypatch.setattr(rk, "MARGINAL_4C", 1e-9)
    r2 = pw.compute(structure, n_sim=N_SIM_TEST, seed=0)
    assert json.dumps(r1, sort_keys=True) == json.dumps(r2, sort_keys=True)


# ----------------------------------------------------------------------- main

def test_main_writes_once_and_refuses_a_second_write(tmp_path):
    (tmp_path / "results").mkdir()
    rec = pw.main(root=tmp_path, n_sim=N_SIM_TEST, seed=0)
    out = tmp_path / "results" / "power_4c.json"
    assert out.is_file()
    on_disk = json.loads(out.read_text())
    assert on_disk["cells_sha256"] == rec["cells_sha256"]
    with pytest.raises(RuntimeError, match="already exists"):
        pw.main(root=tmp_path, n_sim=N_SIM_TEST, seed=0)


def test_main_creates_the_results_dir_if_absent(tmp_path):
    rec = pw.main(root=tmp_path, n_sim=N_SIM_TEST, seed=0)
    assert (tmp_path / "results" / "power_4c.json").is_file()
    assert rec["n_sim"] == N_SIM_TEST


# ----------------------------------------------------- the analyzer's gate

def test_analyzer_refuses_a_power_record_off_the_live_structure_sha(small_record):
    bad = dict(small_record)
    bad["cells_sha256"] = "0" * 64
    failures = an._power_record_failures_4c(bad, expected_n_sim=None, power_gate="full")
    assert any("cells_sha256" in f for f in failures)


def test_analyzer_refuses_a_power_record_with_the_wrong_n_sim(small_record):
    failures = an._power_record_failures_4c(small_record, expected_n_sim=N_SIM_TEST + 1,
                                             power_gate="full")
    assert any("n_sim" in f for f in failures)


def test_analyzer_accepts_a_record_matching_expectations(small_record):
    failures = an._power_record_failures_4c(small_record, expected_n_sim=N_SIM_TEST,
                                             power_gate="full")
    assert failures == []


def test_analyzer_refuses_a_bad_declaration(small_record):
    bad = dict(small_record)
    bad["declaration"] = "MAYBE"
    failures = an._power_record_failures_4c(bad, expected_n_sim=None, power_gate="full")
    assert any("declaration" in f for f in failures)


def test_analyzer_refuses_a_wrong_prereg_tag(small_record):
    bad = dict(small_record)
    bad["prereg_tag"] = "exp4-preregistered"
    failures = an._power_record_failures_4c(bad, expected_n_sim=None, power_gate="full")
    assert any("prereg_tag" in f for f in failures)


def test_analyzer_reproduction_byte_identical_on_an_untouched_record(small_record):
    rep = an._reproduce_power_4c(small_record)
    assert rep["identical"] is True
    assert rep["first_diff"] is None


def test_analyzer_reproduction_fails_when_bytes_were_not_reproduced(small_record):
    tampered = json.loads(json.dumps(small_record))
    tampered["arms"]["null"]["P_01"] = 0.999
    rep = an._reproduce_power_4c(tampered)
    assert rep["identical"] is False
    assert rep["first_diff"] is not None
