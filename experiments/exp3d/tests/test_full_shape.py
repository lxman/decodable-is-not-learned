"""Every verdict-tree terminal, executed end to end on synthetic
three-tree worlds (doc Open item 7)."""
import pytest

from experiments.exp3d import rank_test_3d as rt
from experiments.exp3d.tests import full_shape as fs


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


def test_synthetic_m_min_is_two(worlds):
    v, _ = worlds["W1 structured non-thin, 410m replicated"]
    assert v["functional"]["m_min"] == 2
    assert v["adjudication"]["m_min"] == 2


def test_w1_replication_annotation(worlds):
    v, _ = worlds["W1 structured non-thin, 410m replicated"]
    assert v["adjudication"]["replication_410m"]["rejects"] is True
    assert "replicated at 410m" in v["reason"]
    assert v["adjudication"]["n_fired"] == 5
    assert not v["adjudication"]["thin"]


def test_w2_unreplicated_annotation(worlds):
    v, _ = worlds["W2 structured thin, 410m unreplicated"]
    assert v["adjudication"]["replication_410m"]["rejects"] is False
    assert "unreplicated at 410m" in v["reason"]
    assert v["adjudication"]["thin"]


def test_w3_anti_upper_tail(worlds):
    v, _ = worlds["W3 anti-structured (thin)"]
    assert v["adjudication"]["p_high"] <= rt.ALPHA_3D
    assert v["adjudication"]["p_low"] > rt.ALPHA_3D


def test_w4_no_rejection_but_adequate(worlds):
    v, _ = worlds["W4 unstructured (thin)"]
    a = v["adjudication"]
    assert a["p_low"] > rt.ALPHA_3D and a["p_high"] > rt.ALPHA_3D
    assert a["n_fired"] >= v["functional"]["m_min"]


def test_w5_below_m_min(worlds):
    v, _ = worlds["W5 uninformative at |F| = 1 < m_min"]
    assert v["adjudication"]["n_fired"] == 1
    assert v["functional"]["m_min"] == 2
    assert "Retracts NOTHING" in v["reason"]


def test_w6_gate1_diff_disclosed(worlds):
    v, _ = worlds["W6 insufficient-data: gate-1 drift"]
    assert v["gate1"]["1b"]["n_diffs"] == 1
    assert v["gate1"]["1b"]["diffs"][0]["got"] == " x"
    assert "gate 1 failed" in v["reason"]
    # evidence disclosed even when the verdict halts: fires table exists
    assert "fires" in v and "1b" in v["fires"]


def test_w7_all_void(worlds):
    v, _ = worlds["W7 insufficient-data: every fire void"]
    assert len(v["leak_voids"]) == 1
    assert v["leak_voids"][0]["item"] == 6
    assert "every one of the 1 new fired draws is void" in v["reason"]


def test_w8_void_discloses_and_proceeds(worlds):
    v, _ = worlds["W8 void discloses and proceeds"]
    assert len(v["leak_voids"]) == 1
    assert v["leak_voids"][0]["item"] == 6
    # the void fire is excluded from F: 3 clean fires adjudicate
    assert v["adjudication"]["n_fired"] == 3
    assert 6 not in v["fires"]["1b"]["fired_items"]


def test_disclosure_blocks_always_present(worlds):
    for name, (v, _want) in worlds.items():
        for key in ("gate1", "fires", "pooled", "strata", "tests",
                    "bucket_tests", "persistence", "scoring_arm",
                    "twin_record", "blind_region", "functional",
                    "luck_floor_by_length", "leak_voids"):
            assert key in v, f"{name} lacks {key}"
        for size in ("410m", "1b"):
            assert v["fires"][size]["new"]["count"] == \
                len([a for a in v["fires"][size]["addresses"]
                     if not a["void"]])


def test_scoring_arm_present_and_nongating(worlds):
    v, _ = worlds["W1 structured non-thin, 410m replicated"]
    for size in ("410m", "1b"):
        arm = v["scoring_arm"][size]
        assert arm["known_answer_gate"]["passed"] is True
        assert "rank_test" in arm and "calibration_by_stratum" in arm
        assert arm["none_ell_items"] == 1 if size else True


def test_pooled_counts_add_base_and_new(worlds):
    v, _ = worlds["W1 structured non-thin, 410m replicated"]
    p = v["pooled"]["1b"]
    assert p["committed_count"] == 3      # synthetic base: exp3 1 + 3c 2
    assert p["new_count"] == 5
    assert p["count"] == 8
    assert p["n_draws"] == fs.SYN_BASE_DRAWS["1b"] + fs.N * 1536
