"""Every verdict-tree terminal and every specificity annotation,
executed end to end on synthetic four-tree worlds (doc Open item 8)."""
import itertools

import pytest

from experiments.exp3e import stats_3e as st
from experiments.exp3e.tests import full_shape as fs


@pytest.fixture(scope="module")
def worlds(tmp_path_factory):
    out = {}
    for name, kwargs, want in fs.world_specs():
        tmp = tmp_path_factory.mktemp(name.split()[0])
        out[name] = (fs.build_world(tmp, **kwargs), want)
    return out


def test_every_terminal_reached(worlds):
    for name, (verdict, want) in worlds.items():
        assert verdict["verdict"] == want, \
            f"{name}: got {verdict['verdict']!r}, want {want!r}\n" \
            f"reason: {verdict.get('reason')}"


def test_every_annotation_reached(worlds):
    seen = {v["adjudication"]["specificity"]["annotation"]
            for v, _ in worlds.values() if "adjudication" in v}
    assert seen == set(st.SPECIFICITY_ANNOTATIONS)


def test_synthetic_m_min_and_m_s_min(worlds):
    v, _ = worlds["W1 shortcut non-thin, 410m replicated, directed"]
    assert v["partition"]["m_min"] == 7
    assert v["partition"]["m_s_min"] == 3
    assert v["adjudication"]["m_min"] == 7


def test_w1_replication_and_specificity(worlds):
    v, _ = worlds["W1 shortcut non-thin, 410m replicated, directed"]
    a = v["adjudication"]
    assert a["n_fired"] == 11 and a["x_non_reachable"] == 0
    assert not a["thin"]
    assert a["replication_410m"]["rejects"] is True
    assert "replicated at 410m" in v["reason"]
    sp = a["specificity"]
    assert sp["T_obs"] == 14 and sp["events"] == 16
    assert sp["p"] == pytest.approx(1 / 13824)
    comp = v["specificity"]["1b"]["competitor_addresses"]
    assert {(c["item"], c["target"]) for c in comp} == \
        {(8, "mphm"), (9, "pdbp")}


def test_w2_misfire_rate(worlds):
    v, _ = worlds["W2 shortcut thin, 410m unreplicated, misfire-rate"]
    a = v["adjudication"]
    assert a["thin"] and a["replication_410m"]["rejects"] is False
    # exact p cross-checked by brute-force enumeration over the
    # disclosed count vectors (items 8-10 contribute under the null
    # even with r_i = 0)
    vectors = [tuple(it["counts"]) for it in v["specificity"]["1b"]["items"]]
    t_obs = sum(vv[0] for vv in vectors)
    hits = tot = 0
    for pick in itertools.product(*vectors):
        tot += 1
        hits += sum(pick) >= t_obs
    assert a["specificity"]["p"] == pytest.approx(hits / tot)
    assert a["specificity"]["p"] > st.ALPHA_3E
    assert a["specificity"]["annotation"] == "MISFIRE-RATE"
    assert "unreplicated at 410m" in v["reason"]


def test_w3_anti_upper_tail(worlds):
    v, _ = worlds["W3 anti-shortcut (thin), sparse"]
    a = v["adjudication"]
    assert a["p_high"] <= st.ALPHA_3E and a["p_low"] > st.ALPHA_3E
    assert a["x_non_reachable"] == 5


def test_w4_no_rejection_but_adequate(worlds):
    v, _ = worlds["W4 no-shortcut non-thin"]
    a = v["adjudication"]
    assert a["p_low"] > st.ALPHA_3E and a["p_high"] > st.ALPHA_3E
    assert a["n_fired"] == 14 and not a["thin"]
    assert a["p_low"] == pytest.approx(1 - 110 / 120)


def test_w5_at_m_min(worlds):
    v, _ = worlds["W5 no-shortcut thin at n = m_min"]
    a = v["adjudication"]
    assert a["n_fired"] == a["m_min"] == 7


def test_w6_below_m_min(worlds):
    v, _ = worlds["W6 uninformative at n = 2 < m_min"]
    assert v["adjudication"]["n_fired"] == 2
    assert "Retracts NOTHING" in v["reason"]


def test_w7_gate1_diff_disclosed(worlds):
    v, _ = worlds["W7 insufficient-data: gate-1 drift"]
    assert v["gate1"]["1b"]["n_diffs"] == 1
    assert v["gate1"]["1b"]["diffs"][0]["got"] == " x"
    assert "gate 1 failed" in v["reason"]
    assert "fires" in v and "1b" in v["fires"]


def test_w8_all_void(worlds):
    v, _ = worlds["W8 insufficient-data: every fire void"]
    assert len(v["leak_voids"]) == 1
    assert v["leak_voids"][0]["item"] == 6
    assert "every one of the 1 new fired draws is void" in v["reason"]


def test_w9_void_discloses_and_proceeds(worlds):
    v, _ = worlds["W9 void discloses and proceeds; competitor void "
                  "disclosed"]
    # item 6's two fires are void; the competitor emission on item 8 is
    # void too and is disclosed, not counted
    assert {x["item"] for x in v["leak_voids"]} == {6}
    assert 6 not in v["fires"]["1b"]["fired_items"]
    assert v["adjudication"]["n_fired"] == 7
    cv = v["specificity"]["1b"]["competitor_voids"]
    assert len(cv) == 1 and cv[0]["item"] == 8 and cv[0]["target"] == "mphm"
    assert v["adjudication"]["specificity"]["events"] == 5


def test_disclosure_blocks_always_present(worlds):
    for name, (v, _want) in worlds.items():
        for key in ("gate1", "scorer_gates", "fires", "tests",
                    "count_weighted", "sub_class_texture",
                    "entropy_contrast", "persistence", "pooled",
                    "specificity", "s2_descriptive", "twin_record",
                    "blind_region", "partition", "leak_voids",
                    "luck_floor"):
            assert key in v, f"{name} lacks {key}"
        for size in ("410m", "1b"):
            assert v["fires"][size]["new"]["count"] == \
                len([a for a in v["fires"][size]["addresses"]
                     if not a["void"]])


def test_pooled_counts_add_base_and_new(worlds):
    v, _ = worlds["W1 shortcut non-thin, 410m replicated, directed"]
    p = v["pooled"]["1b"]["repeat_class"]
    assert p["committed_count"] == 6     # synthetic 1b repeat-class base
    assert p["new_count"] == 16
    assert p["count"] == 22
    assert p["n_draws"] == 16 * (2560 + 8192)


def test_entropy_contrast_uses_committed_all_distinct_only(worlds):
    v, _ = worlds["W1 shortcut non-thin, 410m replicated, directed"]
    ec = v["entropy_contrast"]["1b"]
    assert ec["all_distinct_committed"]["n_draws"] == 3 * 2560
    assert ec["all_distinct_committed"]["count"] == 2
    assert ec["non_reachable_pooled"]["n_draws"] == 5 * (2560 + 8192)
    assert ec["scramble_prior_factor"] == 2.0
