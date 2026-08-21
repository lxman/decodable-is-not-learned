"""Fixtures for the class-level power model (design §7; doc Open
item 4): exact world probabilities, calibration, the dispersion rule,
the minimum detectable rate ratio, and the specificity scenarios."""
import json

import pytest

from experiments.exp3e import analyze_3e as e
from experiments.exp3e import compute_power_3e as cp
from experiments.exp3e import stats_3e as st


def test_world_probs_sum_to_one_and_degenerate_cases():
    w = cp.world_probs(0.5, 0.5, n_reach=32, n_non=13, m_min=8)
    assert sum(w["worlds"].values()) == pytest.approx(1.0)
    w = cp.world_probs(1.0, 0.0, n_reach=32, n_non=13, m_min=8)
    assert w["worlds"]["SHORTCUT"] == pytest.approx(1.0)
    assert w["expected_n"] == pytest.approx(32.0)
    w = cp.world_probs(0.0, 1.0, n_reach=32, n_non=13, m_min=8)
    assert w["worlds"]["ANTI-SHORTCUT"] == pytest.approx(1.0)
    w = cp.world_probs(0.0, 0.0, n_reach=32, n_non=13, m_min=8)
    assert w["worlds"]["UNINFORMATIVE"] == pytest.approx(1.0)
    assert w["p_thin"] == pytest.approx(1.0)


def test_null_calibrates_at_or_below_alpha_each_side():
    for q in (0.2, 0.5, 0.8):
        w = cp.world_probs(q, q, n_reach=32, n_non=13, m_min=8)
        assert w["worlds"]["SHORTCUT"] <= st.ALPHA_3E + 1e-12
        assert w["worlds"]["ANTI-SHORTCUT"] <= st.ALPHA_3E + 1e-12


def test_fire_probabilities():
    assert cp.p_fire_homogeneous(0.0, 8192) == 0.0
    assert cp.p_fire_homogeneous(1.709e-4, 8192) == \
        pytest.approx(1 - pow(2.718281828459045, -1.709e-4 * 8192), rel=1e-6)
    # gamma mixing lowers P(fire) at the same mean rate
    assert cp.p_fire_gamma(1.709e-4, 8192, shape=0.3) < \
        cp.p_fire_homogeneous(1.709e-4, 8192)
    # and converges to it as the shape grows
    assert cp.p_fire_gamma(1.709e-4, 8192, shape=1e6) == \
        pytest.approx(cp.p_fire_homogeneous(1.709e-4, 8192), rel=1e-4)


def test_dispersion_rule_on_the_committed_reachable_counts():
    counts = [5, 3, 1, 1, 1, 1, 1, 1] + [0] * 24
    h = cp.dispersion_hat(counts)
    assert h["mu_hat"] == pytest.approx(14 / 32)
    assert h["shape"] == pytest.approx(0.3082, abs=2e-4)   # population variance
    with pytest.raises(ValueError, match="overdispersion"):
        cp.dispersion_hat([1, 1, 1, 1])


def test_min_detectable_ratio_is_monotone_and_bounded():
    rows = cp.min_detectable_ratio(1.709e-4, 8192, n_reach=32, n_non=13,
                                   m_min=8, shape=None, grid=(1.0, 0.5,
                                                              0.2, 0.1,
                                                              0.05, 0.0))
    powers = [r["p_shortcut"] for r in rows["grid"]]
    assert powers == sorted(powers)           # grid descends in ratio
    assert rows["grid"][0]["ratio"] == 1.0
    assert rows["max_ratio_at_power_75"] is None or \
        0.0 <= rows["max_ratio_at_power_75"] <= 1.0


def test_specificity_simulation_calibrates_and_has_power():
    m_sizes = [1] * 10 + [2] * 6 + [3] * 5
    null = cp.simulate_specificity(m_sizes, reverse_rate=1.709e-4,
                                   draws=8192, reverse_share=None,
                                   m_s_min=3, n_sims=2000, seed=1)
    assert null["p_reject"] <= 0.08
    alt = cp.simulate_specificity(m_sizes, reverse_rate=1.709e-4,
                                  draws=8192, reverse_share=0.9,
                                  m_s_min=3, n_sims=2000, seed=1)
    assert alt["p_reject"] > null["p_reject"]
    assert 0 <= alt["p_sparse"] <= 1


def test_power_record_pin_entries_and_committed_file():
    rec = json.loads(e.POWER_PATH.read_text())
    for k in ("m_min", "m_s_min", "thin_max", "alpha", "N", "K"):
        assert k in rec
    assert rec["m_min"] == 8 and rec["m_s_min"] == 3
    assert rec["declared_underpowered"] in (True, False)
    assert rec["underpowered_at_H_half"] in (True, False)
    assert isinstance(rec["concessions_printed_in_advance"], list)
    assert "scenarios" in rec and "1b" in rec["scenarios"]
    # the record reproduces from the frozen code (seeded MC + exact DP)
    from experiments.exp3d import analyze_3d as d
    items = d.load_item_file("reverse_string")
    part = e.load_partition_3e(items["answers"])
    again = cp.compute(part, spec_sims=cp.SPEC_SIMS)
    assert json.dumps(again, sort_keys=True) == \
        json.dumps(rec, sort_keys=True)
