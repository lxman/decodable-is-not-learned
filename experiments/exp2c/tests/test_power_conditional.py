# experiments/exp2c/tests/test_power_conditional.py
"""Tests for conditional power given the REALIZED Stage 1 predictor.

The frozen `power_table_exact` machinery simulates both the predictor
and the outcome from a continuous latent model. After M2 the predictor
is no longer a random variable -- it is 34 observed probe scores, 22 of
which are exactly zero (9 of 16 families entirely flat). These tests
cover a new module that holds x FIXED at the realized scores and
simulates only y, so the reported power conditions on what is known.

Probe-side only: no eval-side quantity enters any function under test.
"""

import numpy as np
import pytest

from experiments.exp2c.run import power_conditional as pc
from experiments.exp2c.run import power_table as pt
from experiments.exp2c.battery import family_map


# ------------------------------------------------------- battery layout

def test_battery_layout_blocks_match_frozen_family_sizes():
    """The x vector must be laid out so family blocks are contiguous and
    sized exactly as `family_map.family_sizes` reports -- that is the
    layout `_block_perm_offsets` assumes."""
    rungs, families = pc.battery_layout()
    assert families == family_map.family_sizes()
    assert len(rungs) == sum(families)
    assert len(set(rungs)) == len(rungs)


def test_battery_layout_rungs_are_contiguous_by_family():
    rungs, families = pc.battery_layout()
    fmap = family_map.scored_battery_families()
    i = 0
    for size in families:
        block = rungs[i:i + size]
        assert len({fmap[r] for r in block}) == 1, \
            f"block {block} spans more than one family"
        i += size


def test_realized_scores_have_the_observed_tie_structure():
    """22 of 34 rungs scored exactly zero at M2; the 12 live ones are
    all distinct. This is a regression guard: if the underlying probe
    records change, the conditional-power run is no longer describing
    the battery it claims to describe."""
    rungs, families = pc.battery_layout()
    x = pc.realized_probe_scores()
    assert len(x) == len(rungs)
    assert np.count_nonzero(x == 0.0) == 22
    live = x[x > 0.0]
    assert len(live) == 12
    assert len(set(live.tolist())) == 12


# ------------------------------------------------- tie-corrected ceiling

def test_tie_corrected_max_rho_is_one_for_an_untied_predictor():
    x = np.arange(34, dtype=float)
    assert pc.tie_corrected_max_rho(x) == pytest.approx(1.0, abs=1e-12)


def test_tie_corrected_max_rho_matches_rank_arithmetic():
    """Hand derivation for the realized shape (22 tied at the bottom,
    12 distinct above), with y continuous so its ranks are 1..34.

    rank(x): 22 values at the average rank (1+..+22)/22 = 11.5, then
    23..34. Mean rank 17.5. Centred: 22 at -6, then 5.5..16.5.
      Sxx = 22*36 + sum((5.5..16.5)^2) = 792 + 1595 = 2387
      Syy = n(n^2-1)/12 = 34*1155/12 = 3272.5
    The maximising assignment puts y-ranks 1..22 on the tied block
    (its centred x is negative) and 23..34 on the live rungs in order:
      Sxy = (-6)*(sum(1..22) - 22*17.5) + sum((5.5..16.5)^2)
          = (-6)*(-132) + 1595 = 2387
    so rho_max = Sxy/sqrt(Sxx*Syy) = sqrt(2387/3272.5).
    """
    x = np.concatenate([np.zeros(22), np.arange(1.0, 13.0)])
    expected = np.sqrt(2387.0 / 3272.5)
    assert expected == pytest.approx(0.854056, abs=1e-6)
    assert pc.tie_corrected_max_rho(x) == pytest.approx(expected, abs=1e-9)


def test_target_rho_above_the_ceiling_raises():
    """A target Spearman the tie structure cannot express must fail
    loudly rather than silently calibrate to the nearest achievable
    value and report it as if it were the requested one."""
    x = np.concatenate([np.zeros(22), np.arange(1.0, 13.0)])
    ceiling = pc.tie_corrected_max_rho(x)
    with pytest.raises(ValueError, match="ceiling"):
        pc.calibrate_shared(x, [34], rho_family=0.5,
                            rho_true=min(0.999, ceiling + 0.05), seed=0)


# ------------------------------------------------------ y calibration

def test_calibrated_y_attains_the_target_spearman():
    """`calibrate_shared` must return a loading whose induced mean
    Spearman against the fixed x lands on the requested rho_true."""
    rng = np.random.default_rng(0)
    x = rng.normal(size=34)
    families = [4, 2, 2, 4, 2, 2, 1, 2, 1, 1, 2, 4, 2, 2, 1, 2]
    for target in (0.3, 0.6):
        shared = pc.calibrate_shared(x, families, rho_family=0.5,
                                     rho_true=target, seed=1)
        achieved = pc.mean_spearman(x, families, rho_family=0.5,
                                    shared=shared, n_sims=600, seed=2)
        assert achieved == pytest.approx(target, abs=0.02)


def test_calibration_holds_with_the_realized_tied_predictor():
    x = pc.realized_probe_scores()
    _, families = pc.battery_layout()
    shared = pc.calibrate_shared(x, families, rho_family=0.5,
                                 rho_true=0.6, seed=1)
    achieved = pc.mean_spearman(x, families, rho_family=0.5,
                                shared=shared, n_sims=600, seed=2)
    assert achieved == pytest.approx(0.6, abs=0.02)


# --------------------------------------------------- validity and power

def test_conditional_alpha_stays_bounded_under_the_null():
    """The headline worry is power, but type I error is the thing that
    must NOT move: with x held fixed and heavily tied, the block
    permutation test must still reject at <= alpha under H0."""
    x = pc.realized_probe_scores()
    _, families = pc.battery_layout()
    out = pc.simulate_conditional(x, families, rho_family=0.5,
                                  rho_true=0.0, n_sims=1200, seed=0)
    assert out["power"] <= 0.02  # .01 target + MC slack at n_sims=1200


def test_conditional_power_rises_with_the_target_rho():
    """Basic correctness: a stronger predictor-outcome relationship must
    be rejected more often, holding the predictor fixed."""
    x = pc.realized_probe_scores()
    _, families = pc.battery_layout()
    weak = pc.simulate_conditional(x, families, rho_family=0.5,
                                   rho_true=0.5, n_sims=600, seed=0)
    strong = pc.simulate_conditional(x, families, rho_family=0.5,
                                     rho_true=0.7, n_sims=600, seed=0)
    assert weak["power"] < strong["power"]


def test_simulate_conditional_reports_the_realized_predictor_shape():
    x = pc.realized_probe_scores()
    _, families = pc.battery_layout()
    out = pc.simulate_conditional(x, families, rho_family=0.5,
                                  rho_true=0.6, n_sims=200, seed=0)
    assert out["n_rungs"] == 34
    assert out["n_tied_at_zero"] == 22
    assert out["n_live_families"] == 7
    assert out["n_families"] == 16
    assert out["method"] == "sampled"
    assert out["rho_ceiling"] == pytest.approx(
        pc.tie_corrected_max_rho(x), abs=1e-12)


# ------------------------------------------------------------- the table

def test_conditional_table_covers_the_frozen_grid():
    """The deliverable must be readable row-for-row against
    power_table_exact.md: same rho_true grid, same rho_family sweep."""
    out = pc.run_conditional_table(n_sims=60, n_sample=2000, seed=0)
    assert list(out["rho_true_values"]) == list(pt.RHO_TRUE_VALUES)
    assert set(out["runs"]) == {str(r) for r in pt.RHO_TRUE_VALUES}
    assert set(out["power_sweep"]) == {str(r)
                                       for r in pt.RHO_FAMILY_SWEEP_EXACT}
    assert out["n_tied_at_zero"] == 22
    assert out["n_live_families"] == 7
    assert out["families"] == family_map.family_sizes()


def test_conditional_table_marks_grid_points_above_the_ceiling():
    """A target the predictor cannot express is recorded as unreachable,
    not silently dropped and not crashed on."""
    x = np.concatenate([np.zeros(30), np.arange(1.0, 5.0)])
    out = pc.run_conditional_table(x=x, families=[34], n_sims=40,
                                   n_sample=500, seed=0)
    assert out["rho_ceiling"] < 0.8
    assert out["runs"]["0.8"]["unreachable"] is True
    assert out["runs"]["0.8"]["power"] is None
    assert out["runs"]["0.0"]["unreachable"] is False


def test_alpha_check_pools_seeds_and_reports_an_interval():
    """One 5000-sim null row has SE ~.0014, too coarse to tell .0124
    from .0100. The recorded validity check pools seeds so the artifact
    carries an interval rather than a single noisy draw."""
    x = pc.realized_probe_scores()
    _, families = pc.battery_layout()
    out = pc.alpha_check(x, families, rho_family=0.5, seeds=(0, 1),
                         n_sims=300, n_sample=2000)
    assert out["n"] == 600
    assert len(out["per_seed"]) == 2
    assert out["ci95"][0] <= out["alpha_hat"] <= out["ci95"][1]
    assert out["target"] == 0.01


def test_conditional_table_records_the_alpha_check():
    out = pc.run_conditional_table(n_sims=40, n_sample=500, seed=0,
                                   alpha_check_seeds=(0, 1),
                                   alpha_check_n_sims=200)
    assert out["alpha_check"]["n"] == 400
    assert "ci95" in out["alpha_check"]


def test_markdown_states_the_predictor_shape_and_the_frozen_comparison(tmp_path):
    """The written table has to carry its own caveats: what it is
    conditional on, the tie ceiling, and the frozen figures it should be
    read against -- otherwise the number travels without them."""
    out = pc.run_conditional_table(n_sims=40, n_sample=500, seed=0)
    path = tmp_path / "power_conditional.md"
    pc.write_markdown(out, path)
    text = path.read_text()
    assert "22 of 34" in text
    assert "9 of 16" in text
    assert "0.8541" in text            # the tie-corrected ceiling
    assert "0.7690" in text            # frozen power_table_exact at rho=0.6
    assert "eval" in text.lower()      # the no-eval-information statement


def test_uses_the_frozen_permutation_machinery():
    """The test statistic must be the frozen one, not a reimplementation:
    same block-permutation group, same add-one sampled p convention."""
    rng = np.random.default_rng(0)
    families = [2, 1, 1]
    perms = pt.sampled_block_perms(families, 50, rng)
    x = np.array([3.0, 1.0, 2.0, 4.0])
    y = np.array([1.0, 2.0, 3.0, 4.0])
    assert pc.block_p(x, y, perms) == pt._sampled_block_p_from_perms(
        x, y, perms)["p"]
