"""Fixture suite for the frozen Exp 1c analysis. One synthetic case per
preregistered provision (design §4, §5). No test reads real records.

The per-site fire rule is 1c's verdict-adjacent operationalization, ruled by
Michael on 2026-08-14 before any probe ran: a site fires iff BOTH the
label-permutation null (Bonferroni across all 8 sites, alpha 0.01) AND the
per-site floor correction (trained accuracy strictly above its twin's at the
SAME site) admit it. 1b measured that these two gates are load-bearing on
different rows, so both are tested here in both directions.
"""
import pytest

from experiments.exp1c import analyze_1c as a


# ------------------------------------------------------------------ builders

def site(layer, token, accuracy, null_p_raw=0.0001):
    return {"layer": layer, "token": token, "accuracy": accuracy,
            "null_p_raw": null_p_raw}


def profile(acc_by_layer, null_p_raw=0.0001):
    """8 sites from {layer: accuracy}; both tokens get the same accuracy."""
    return [site(l, t, acc_by_layer[l], null_p_raw)
            for l in a.LAYERS for t in a.TOKENS]


# --------------------------------------------------- the per-site fire rule

def test_site_fires_when_null_and_floor_both_admit_it():
    tr = site(2, -1, 0.40, null_p_raw=0.0001)   # corrected 0.0008 < 0.01
    tw = site(2, -1, 0.10)
    assert a.site_fires(tr, tw) is True


def test_site_does_not_fire_when_the_null_rejects_it():
    """The gate 1b measured on lubana_below/1M/seed100: margin positive,
    permutation null p = .847, so the margin alone would have fired it."""
    tr = site(2, -1, 0.40, null_p_raw=0.847)
    tw = site(2, -1, 0.10)
    assert a.site_fires(tr, tw) is False


def test_site_does_not_fire_when_it_only_matches_its_twin():
    """The gate that demoted grokking/10M/seed104 in 1b: trained .017333 vs
    twin .017333. Strict inequality — a tie is not evidence."""
    tr = site(2, -1, 0.10, null_p_raw=0.0001)
    tw = site(2, -1, 0.10)
    assert a.site_fires(tr, tw) is False


def test_site_does_not_fire_when_it_reads_below_its_twin():
    tr = site(2, -1, 0.08, null_p_raw=0.0001)
    tw = site(2, -1, 0.10)
    assert a.site_fires(tr, tw) is False


def test_null_is_bonferroni_corrected_across_all_eight_sites():
    """raw .005 x 8 = .04, above alpha .01 — fires only without correction."""
    tr = site(2, -1, 0.40, null_p_raw=0.005)
    tw = site(2, -1, 0.10)
    assert a.site_fires(tr, tw) is False
    assert a.site_fires(tr, tw, n_sites=1) is True


def test_fire_rule_refuses_a_mismatched_site_pair():
    """Pairing is per SITE. Comparing layer 2 against layer 0's twin would
    silently substitute a different channel's floor."""
    with pytest.raises(ValueError, match="same site"):
        a.site_fires(site(2, -1, 0.40), site(0, -1, 0.10))


# ------------------------------------------------------------- the margins

def test_depth_margin_averages_only_layers_at_or_above_one():
    tr = profile({0: 0.90, 1: 0.30, 2: 0.30, 3: 0.30})
    tw = profile({0: 0.10, 1: 0.10, 2: 0.10, 3: 0.10})
    assert a.depth_margin(tr, tw) == pytest.approx(0.20)


def test_layer0_margin_averages_only_layer_zero():
    tr = profile({0: 0.90, 1: 0.30, 2: 0.30, 3: 0.30})
    tw = profile({0: 0.10, 1: 0.10, 2: 0.10, 3: 0.10})
    assert a.l0_margin(tr, tw) == pytest.approx(0.80)


def test_margins_are_means_not_maxima():
    """A max over paired differences is biased upward and its null depends on
    the number of sites — design §4 rules that out explicitly."""
    tr = profile({0: 0.10, 1: 0.10, 2: 0.10, 3: 0.10})
    for s in tr:
        if (s["layer"], s["token"]) == (3, -1):
            s["accuracy"] = 0.70
    tw = profile({0: 0.10, 1: 0.10, 2: 0.10, 3: 0.10})
    assert a.depth_margin(tr, tw) == pytest.approx(0.10)   # 0.60/6, not 0.60


def test_margin_refuses_an_incomplete_profile():
    tr = profile({0: 0.5, 1: 0.5, 2: 0.5, 3: 0.5})[:7]
    tw = profile({0: 0.1, 1: 0.1, 2: 0.1, 3: 0.1})
    with pytest.raises(ValueError, match="8 sites"):
        a.depth_margin(tr, tw)


# -------------------------------------------------------- cell classification

def test_cell_with_a_firing_depth_site_is_classified_depth():
    tr = profile({0: 0.10, 1: 0.10, 2: 0.40, 3: 0.10})
    tw = profile({0: 0.10, 1: 0.10, 2: 0.10, 3: 0.10})
    out = a.classify(tr, tw)
    assert out["class"] == "depth"
    assert out["n_depth_fired"] == 2      # both tokens at layer 2
    assert out["n_l0_fired"] == 0


def test_cell_firing_only_at_layer_zero_is_classified_l0_only():
    tr = profile({0: 0.40, 1: 0.10, 2: 0.10, 3: 0.10})
    tw = profile({0: 0.10, 1: 0.10, 2: 0.10, 3: 0.10})
    out = a.classify(tr, tw)
    assert out["class"] == "L0-only"
    assert out["n_l0_fired"] == 2
    assert out["n_depth_fired"] == 0


def test_cell_with_no_firing_site_is_silent():
    tr = profile({0: 0.10, 1: 0.10, 2: 0.10, 3: 0.10})
    tw = profile({0: 0.10, 1: 0.10, 2: 0.10, 3: 0.10})
    assert a.classify(tr, tw)["class"] == "silent"


def test_depth_precedence_never_hides_a_layer_zero_cofire():
    """Precedence picks `depth`, but the L0 count must stay visible — design
    §4 requires the pair be reported alongside the class."""
    tr = profile({0: 0.40, 1: 0.10, 2: 0.40, 3: 0.10})
    tw = profile({0: 0.10, 1: 0.10, 2: 0.10, 3: 0.10})
    out = a.classify(tr, tw)
    assert out["class"] == "depth"
    assert out["n_l0_fired"] == 2
    assert out["n_depth_fired"] == 2
