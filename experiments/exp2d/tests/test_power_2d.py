"""compute_power_2d: the frozen §7 procedure's pieces, small sims."""
import numpy as np
import pytest

from experiments.exp2d import analyze_2d as a
from experiments.exp2d import battery_2d as bt
from experiments.exp2d import compute_power_2d as cp
from experiments.exp2d import stats_2d as st
from experiments.exp2d.tests import full_shape as fs


def _pred(score, raw_zero, k=None):
    """A synthetic pilot predictor entry with the per-size counts
    `predictor_from_tier` carries (k per size; 0 when raw zero)."""
    ks = {s: (0 if raw_zero[s] else (k if k is not None else 40))
          for s in a.PROBE_SIZES}
    return {"score": score, "raw_zero": dict(raw_zero),
            "per_size": {s: {"k": ks[s], "n": a.PILOT_DRAWS_PER_RUNG}
                         for s in a.PROBE_SIZES}}


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
    pred = {r: _pred(0.0, {"410m": True, "1b": True}) for r in a.RUNGS}
    pred["antonym"] = _pred(0.3, {"410m": False, "1b": False})
    pred["hamming12"] = _pred(0.1, {"410m": False, "1b": False})
    pred["median5"] = _pred(0.0, {"410m": True, "1b": False}, k=2)
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
    pred = {r: _pred(0.2 if outcome["rungs"][r]["rising"] else 0.0,
                     {s: not outcome["rungs"][r]["rising"]
                      for s in a.PROBE_SIZES})
            for r in a.RUNGS}
    rec = cp.run_procedure(pred, outcome, n_sims=40, targets=(0.5, 0.85))
    assert set(rec["power"]) == {"0.5", "0.85"}
    # the unconditional α check is the ratified sensitivity's .5 row
    rat = rec["sensitivity_ratified_rule"]["power"]
    assert rat["0.5"]["p_pass"] <= 0.1
    assert rat["0.85"]["p_pass"] > rat["0.5"]["p_pass"]
    # the symmetric rule declares; with every rising rung pilot-positive
    # and every flat rung at zero the pilot already separates: 1.0
    assert rec["declaration_rule"] == "symmetric"
    assert rec["power"]["0.85"]["p_pass"] == 1.0
    assert rec["declared_status"] in ("POWERED",
                                      "DECLARED UNDERPOWERED IN ADVANCE")
    assert rec["declared_underpowered"] == (rec["power"]["0.85"]["p_pass"] < .75)
    assert rec["declared_status"] == "POWERED"
    assert "runs regardless" in rec["run_anyway"]
    # the pilot's zero set: all rising alive → no raw-zero rising
    assert rec["pilot_zero_set"]["rising_raw_zero_set"] == []
    assert rec["pilot_zero_set"]["z0"] == 23


def test_rising_raw_zeros_cost_power():
    outcome = fs.outcome()
    ris = [r for r in a.RUNGS if outcome["rungs"][r]["rising"]]
    base = {r: _pred(0.2 if outcome["rungs"][r]["rising"] else 0.0,
                     {s: not outcome["rungs"][r]["rising"]
                      for s in a.PROBE_SIZES}) for r in a.RUNGS}
    hurt = {r: dict(v) for r, v in base.items()}
    for r in ris[:6]:
        hurt[r] = _pred(0.0, {"410m": True, "1b": True})
    p0 = cp.run_procedure(base, outcome, n_sims=60, targets=(0.85,))
    p6 = cp.run_procedure(hurt, outcome, n_sims=60, targets=(0.85,))
    assert p6["power"]["0.85"]["p_pass"] < p0["power"]["0.85"]["p_pass"]
    assert p6["power"]["0.85"]["mean_realized_auc"] < \
        p0["power"]["0.85"]["mean_realized_auc"]


def test_procedure_is_seeded_and_reproducible():
    outcome = fs.outcome()
    pred = {r: _pred(0.2 if outcome["rungs"][r]["rising"] else 0.0,
                     {s: not outcome["rungs"][r]["rising"]
                      for s in a.PROBE_SIZES}) for r in a.RUNGS}
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
    dead = {r: _pred(0.0, {"410m": True, "1b": True}) for r in a.RUNGS}
    rec = cp.run_procedure(dead, outcome, n_sims=20, targets=(0.85,))
    assert rec["pilot_zero_set"]["rising_raw_zero_set"] == ris
    assert rec["power"]["0.85"]["p_pass"] == 0.0
    assert rec["declared_underpowered"] is True
    assert rec["declared_status"] == "DECLARED UNDERPOWERED IN ADVANCE"


# ----------------------------------------- freeze F-4: the symmetric rule

def test_symmetric_rule_holds_pilot_positive_rising_rungs_positive():
    rng = np.random.default_rng(2)
    s = np.array([cp.simulate_scores(rng, rising=[True, True, False],
                                     held_zero=[False, False, True],
                                     caps=[None, None, None], tau=2.0, d=2.5,
                                     held_positive=[True, False, False])
                  for _ in range(300)])
    assert (s[:, 0] > 0).all()                 # held positive: never silent
    assert 0.15 < (s[:, 1] == 0).mean() < 0.5  # ratified: re-silenced w.p. Φ(τ−d)≈.31
    assert (s[:, 2] == 0).all()


def test_symmetric_rule_leaves_the_ratified_draw_sequence_untouched():
    """held_positive all False consumes the generator exactly as the
    ratified rule does — the declaring numbers cannot move."""
    kw = dict(rising=[True, False, True, False], held_zero=[False, True, False, False],
              caps=[None, None, 0.0, None], tau=0.4, d=1.3)
    a1 = np.array([cp.simulate_scores(np.random.default_rng(i), **kw) for i in range(50)])
    a2 = np.array([cp.simulate_scores(np.random.default_rng(i), **kw,
                                      held_positive=[False] * 4) for i in range(50)])
    assert np.array_equal(a1, a2)


def test_score_cap_from_counts_generalizes_the_raw_zero_cap():
    assert cp.score_cap_from_counts(0.006, [0, 0]) == cp.score_cap(0.006) == 0.0
    assert cp.score_cap_from_counts(0.006, [14, 14]) == 0.0        # CP upper < floor
    assert cp.score_cap_from_counts(0.006, [30, 0]) > 0.0          # one size above
    assert cp.score_cap_from_counts(0.006, [0, 30]) == \
        pytest.approx(cp.score_cap_from_counts(0.006, [30, 0]))


def test_pilot_structure_symmetric_partitions_rising_rungs():
    outcome = fs.outcome()
    pred = {r: _pred(0.0, {"410m": True, "1b": True}) for r in a.RUNGS}
    pred["antonym"] = _pred(0.3, {"410m": False, "1b": False})
    pred["sub4_mid"] = _pred(0.0, {"410m": False, "1b": True}, k=30)   # 30/4000 > floor .006 bound
    pred["add3_mid"] = _pred(0.0, {"410m": False, "1b": False}, k=3)   # 3/4000: CP upper < .006
    st_ = cp.pilot_structure_symmetric(pred, outcome)
    assert st_["rising_held_positive"] == ["antonym"]
    assert st_["z0"] == 23 and st_["n0"] == 23
    assert st_["rising_capped"]["sub4_mid"]["cap"] > 0.0
    assert st_["rising_capped"]["add3_mid"]["cap"] == 0.0
    assert st_["rising_capped"]["add3_mid"]["pilot_counts"] == {"410m": 3, "1b": 3}
    assert len(st_["rising_capped"]) == 10
    i = a.RUNGS.index("antonym")
    assert st_["held_positive"][i] and st_["caps"][i] is None


def test_symmetric_rule_declares_and_the_tobit_is_printed_beside_it():
    """Ruling m (2026-08-21): the symmetric rule declares; the Tobit
    as built rides along NON-DECLARING with its own would_declare."""
    outcome = fs.outcome()
    pred = {r: _pred(0.2 if outcome["rungs"][r]["rising"] else 0.0,
                     {s: not outcome["rungs"][r]["rising"] for s in a.PROBE_SIZES})
            for r in a.RUNGS}
    rec = cp.run_procedure(pred, outcome, n_sims=40, targets=(0.85,))
    assert rec["declaration_rule"] == "symmetric"
    assert rec["pilot_structure"]["rising_held_positive"] == \
        [r for r in a.RUNGS if outcome["rungs"][r]["rising"]]
    assert rec["pilot_structure"]["rising_capped"] == {}
    assert rec["power"]["0.85"]["p_pass"] == 1.0 and \
        rec["declared_status"] == "POWERED"
    rat = rec["sensitivity_ratified_rule"]
    assert set(rat["power"]) == {"0.85"}
    assert rat["power"]["0.85"]["p_pass"] < 1.0          # re-silences ~30 %
    assert rat["would_declare"] in ("POWERED", "DECLARED UNDERPOWERED IN ADVANCE")
    assert rat["agrees_with_declaration"] == (
        (rat["power"]["0.85"]["p_pass"] < .75) == rec["declared_underpowered"])
    # a rising rung at pilot zero with sub-floor counts is capped at 0 → held silent
    pred["sub4_mid"] = _pred(0.0, {"410m": False, "1b": False}, k=3)
    rec2 = cp.run_procedure(pred, outcome, n_sims=40, targets=(0.85,))
    assert rec2["pilot_structure"]["rising_capped"]["sub4_mid"]["cap"] == 0.0
    assert rec2["power"]["0.85"]["p_pass"] == 1.0         # one silent: still PASS
