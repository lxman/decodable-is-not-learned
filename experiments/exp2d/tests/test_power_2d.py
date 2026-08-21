"""compute_power_2d: the frozen §7 procedure's pieces, small sims."""
import numpy as np
import pytest

from experiments.exp2d import analyze_2d as a
from experiments.exp2d import battery_2d as bt
from experiments.exp2d import compute_power_2d as cp
from experiments.exp2d import stats_2d as st
from experiments.exp2d.tests import full_shape as fs


def test_population_auc_null_and_monotone():
    for tau in (-1.0, 0.0, 0.7, 2.0):
        assert cp.population_auc(0.0, tau) == pytest.approx(0.5, abs=1e-9)
        vals = [cp.population_auc(d, tau) for d in (0.5, 1.0, 2.0, 4.0)]
        assert vals == sorted(vals) and vals[-1] > 0.97


def test_solve_effect_inverts_population_auc():
    for tau in (-0.5, 0.6, 1.5):
        for t in (0.75, 0.85):
            d = cp.solve_effect(t, tau)
            assert cp.population_auc(d, tau) == pytest.approx(t, abs=1e-8)
    assert cp.solve_effect(0.5, 0.3) == 0.0


def test_population_auc_matches_monte_carlo():
    rng = np.random.default_rng(0)
    tau = 0.4
    d = cp.solve_effect(0.8, tau)
    L0 = rng.normal(0, 1, 300_000)
    L1 = rng.normal(d, 1, 300_000)
    S0, S1 = np.maximum(0, L0 - tau), np.maximum(0, L1 - tau)
    mc = (S1 > S0).mean() + 0.5 * (S1 == S0).mean()
    assert mc == pytest.approx(0.8, abs=0.005)


def test_tau_from_zero_fraction_finite_at_extremes():
    assert np.isfinite(cp.tau_from_zero_fraction(0, 21))
    assert np.isfinite(cp.tau_from_zero_fraction(21, 21))
    assert cp.tau_from_zero_fraction(21, 21) > cp.tau_from_zero_fraction(10, 21)
    with pytest.raises(ValueError):
        cp.tau_from_zero_fraction(0, 0)


def test_score_cap_is_zero_for_every_real_floor():
    _, floors = fs.battery()
    assert cp.PILOT_CP_UPPER == pytest.approx(st.clopper_pearson(0, 4000)[1])
    assert all(cp.score_cap(floors[r]["floor"]) == 0.0 for r in a.RUNGS)
    assert cp.score_cap(0.0005) > 0.0


def test_simulate_scores_honours_ties_and_caps():
    rng = np.random.default_rng(1)
    rising = [True, True, False, False]
    held = [False, False, True, False]
    caps = [None, 0.0, None, None]
    for _ in range(200):
        s = cp.simulate_scores(rng, rising=rising, held_zero=held, caps=caps,
                               tau=0.3, d=1.5)
        assert s[2] == 0.0            # held at zero
        assert s[1] == 0.0            # rising, capped at 0 → zero
        assert s[3] > 0.0             # non-rising, not held → positive part
        assert s[0] >= 0.0


def test_pilot_zero_set_from_predictor():
    outcome = fs.outcome()
    pred = {r: {"score": 0.0, "raw_zero": {"410m": True, "1b": True}}
            for r in a.RUNGS}
    pred["antonym"] = {"score": 0.3, "raw_zero": {"410m": False, "1b": False}}
    pred["hamming12"] = {"score": 0.1, "raw_zero": {"410m": False, "1b": False}}
    pred["median5"] = {"score": 0.0, "raw_zero": {"410m": True, "1b": False}}
    zs = cp.pilot_zero_set(pred, outcome)
    n1 = outcome["n_rising"]
    assert zs["n0"] == 34 - n1 == 23 and zs["z0"] == 22
    assert "hamming12" not in zs["non_rising_zero_set"]
    assert "antonym" not in zs["rising_raw_zero_set"]
    assert "median5" not in zs["rising_raw_zero_set"]   # one size nonzero
    assert len(zs["rising_raw_zero_set"]) == n1 - 2 == 9
    assert all(v == 0.0 for v in zs["rising_raw_zero_caps"].values())


def test_run_procedure_small_and_declaration_rule():
    outcome = fs.outcome()
    # every rising rung alive in the pilot, every flat rung at zero:
    pred = {r: {"score": (0.2 if outcome["rungs"][r]["rising"] else 0.0),
                "raw_zero": {s: not outcome["rungs"][r]["rising"]
                             for s in a.PROBE_SIZES}}
            for r in a.RUNGS}
    rec = cp.run_procedure(pred, outcome, n_sims=40, targets=(0.5, 0.85))
    assert set(rec["power"]) == {"0.5", "0.85"}
    assert rec["power"]["0.5"]["p_pass"] <= 0.1
    assert rec["power"]["0.85"]["p_pass"] > rec["power"]["0.5"]["p_pass"]
    assert rec["declared_status"] in ("POWERED",
                                      "DECLARED UNDERPOWERED IN ADVANCE")
    assert rec["declared_underpowered"] == (rec["power"]["0.85"]["p_pass"] < .75)
    assert "runs regardless" in rec["run_anyway"]
    # the pilot's zero set: all rising alive → no raw-zero rising
    assert rec["pilot_zero_set"]["rising_raw_zero_set"] == []
    assert rec["pilot_zero_set"]["z0"] == 23


def test_rising_raw_zeros_cost_power():
    outcome = fs.outcome()
    ris = [r for r in a.RUNGS if outcome["rungs"][r]["rising"]]
    base = {r: {"score": (0.2 if outcome["rungs"][r]["rising"] else 0.0),
                "raw_zero": {s: not outcome["rungs"][r]["rising"]
                             for s in a.PROBE_SIZES}} for r in a.RUNGS}
    hurt = {r: dict(v) for r, v in base.items()}
    for r in ris[:6]:
        hurt[r] = {"score": 0.0, "raw_zero": {"410m": True, "1b": True}}
    p0 = cp.run_procedure(base, outcome, n_sims=60, targets=(0.85,))
    p6 = cp.run_procedure(hurt, outcome, n_sims=60, targets=(0.85,))
    assert p6["power"]["0.85"]["p_pass"] < p0["power"]["0.85"]["p_pass"]
    assert p6["power"]["0.85"]["mean_realized_auc"] < \
        p0["power"]["0.85"]["mean_realized_auc"]


def test_procedure_is_seeded_and_reproducible():
    outcome = fs.outcome()
    pred = {r: {"score": (0.2 if outcome["rungs"][r]["rising"] else 0.0),
                "raw_zero": {s: not outcome["rungs"][r]["rising"]
                             for s in a.PROBE_SIZES}} for r in a.RUNGS}
    r1 = cp.run_procedure(pred, outcome, n_sims=25, targets=(0.75,))
    r2 = cp.run_procedure(pred, outcome, n_sims=25, targets=(0.75,))
    assert r1["power"] == r2["power"] and r1["tau"] == r2["tau"]
    assert bt.N_FAMILIES == 16


def test_power_literals():
    assert cp.POWER_BAR == 0.75 and cp.DECLARATION_TARGET == 0.85
    assert cp.AUC_TARGETS == (0.5, 0.75, 0.85)
    assert cp.N_SIMS == 2000 and cp.POWER_SEED == 20260821


def test_truncated_rising_rung_moves_below_a_positive_cap():
    """With a positive cap the truncated alternative must produce
    scores in (0, cap] — not be held at zero."""
    rng = np.random.default_rng(4)
    s = np.array([cp.simulate_scores(rng, rising=[True], held_zero=[False],
                                     caps=[0.5], tau=0.0, d=2.0)[0]
                  for _ in range(400)])
    assert s.max() <= 0.5 + 1e-12
    assert (s > 0).mean() > 0.5


def test_declaration_flag_follows_the_bar():
    outcome = fs.outcome()
    ris = [r for r in a.RUNGS if outcome["rungs"][r]["rising"]]
    dead = {r: {"score": 0.0, "raw_zero": {"410m": True, "1b": True}}
            for r in a.RUNGS}
    rec = cp.run_procedure(dead, outcome, n_sims=20, targets=(0.85,))
    assert rec["pilot_zero_set"]["rising_raw_zero_set"] == ris
    assert rec["power"]["0.85"]["p_pass"] == 0.0
    assert rec["declared_underpowered"] is True
    assert rec["declared_status"] == "DECLARED UNDERPOWERED IN ADVANCE"
