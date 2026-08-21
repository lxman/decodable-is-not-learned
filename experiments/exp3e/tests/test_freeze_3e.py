"""Freeze-session fixtures (session 3 of 3): each freeze finding's
closure, executable — the arm's void-exclusion rule (F-1), the power
record's shape-rule sensitivity (F-2), and the gate-1-vs-tranche pins
(F-3). See FREEZE_CHECKLIST.md / PROGRESS.md (2026-08-21, freeze)."""
import json

import pytest

from experiments.exp3c import analyze_3c as c
from experiments.exp3e import analyze_3e as e
from experiments.exp3e import compute_power_3e as cp
from experiments.exp3e import partition_3e as pt
from experiments.exp3e import scorer_3e as sc
from experiments.exp3e.tests import full_shape as fs


# ------------------------------------------------ F-1: arm void exclusion

def _arm_world():
    """Three arm items: ecde (|M| = 2), qaba (|M| = 1), mhmp (|M| = 3);
    cbaa is non-reachable and sits outside the arm. Item 0's competitor
    'edec' is planted in its prompt (void) while the item ALSO carries
    two reverse fires and three competitor emissions."""
    answers = ["ecde", "qaba", "mhmp", "cbaa"]
    partition = pt.build_partition(answers)
    assert partition["arm_items"] == [0, 1, 2]
    filler = [" ~z"] * 5
    rows = {
        0: {"40": [" ecde", " edec", " edec"] + filler,
            "41": [" ecde", " edec"] + filler},
        1: {"40": [" qaba"] + filler, "41": list(filler)},
        2: {"40": list(filler), "41": [" mhmp"] + filler},
        3: {"40": list(filler), "41": list(filler)},
    }
    prompts = {i: f"Q: Spell the string '{a[::-1]}' backwards.\nA:"
               for i, a in enumerate(answers)}
    prompts[0] = prompts[0].replace("backwards", "backwards (hint edec)")
    return answers, partition, rows, prompts


def test_arm_excludes_an_item_with_a_void_target_from_the_test():
    answers, partition, rows, prompts = _arm_world()
    arm = e._specificity_arm("1b", rows, partition, prompts, answers,
                             "word", sc.load_scorer())
    ex = arm["arm_void_excluded"]
    assert [x["item"] for x in ex] == [0]
    assert ex[0]["void_targets"] == ["edec"]
    assert ex[0]["raw_counts"] == [2, 3, 0]       # disclosed, not tested
    assert arm["n_arm_items"] == 3
    assert arm["test"]["n_items"] == 2
    # items 1 (θ = 1/2) and 2 (θ = 1/4), one reverse event each: the
    # exact p is the product of thetas, 1/8. Under the superseded
    # zeroing semantics item 0's vector (2, 0, 0) would have multiplied
    # in a further 1/3 — p = 1/24 — i.e. the void would have ARGUED
    # for DIRECTED.
    assert arm["test"]["T_obs"] == 2 and arm["test"]["events"] == 2
    assert arm["test"]["p"] == pytest.approx(1 / 8)
    by_item = {x["item"]: x for x in arm["items"]}
    assert by_item[0]["in_test"] is False and by_item[1]["in_test"] is True
    # the competitor emissions are still disclosed verbatim as voids
    assert len(arm["competitor_voids"]) == 3
    assert all(v["item"] == 0 and v["target"] == "edec"
               for v in arm["competitor_voids"])
    assert arm["competitor_addresses"] == []


def test_arm_with_no_void_is_unchanged():
    answers, partition, rows, prompts = _arm_world()
    prompts[0] = prompts[0].replace(" (hint edec)", "")
    arm = e._specificity_arm("1b", rows, partition, prompts, answers,
                             "word", sc.load_scorer())
    assert arm["arm_void_excluded"] == []
    assert arm["test"]["n_items"] == 3
    # item 0's live vector is (2, 3, 0): P(T ≥ 4) = 1/6 + 1/24 + 1/24
    assert arm["test"]["p"] == pytest.approx(1 / 4)
    assert len(arm["competitor_addresses"]) == 3
    # the three semantics side by side, exact: competitor live 1/4;
    # item excluded (F-1) 1/8; competitor ZEROED (the superseded
    # reading of slip f) 1/24 — the void would have argued for DIRECTED
    from experiments.exp3e import stats_3e as st
    assert st.designation_test([(2, 3, 0), (1, 0), (1, 0, 0, 0)])["p"] \
        == pytest.approx(1 / 4)
    assert st.designation_test([(1, 0), (1, 0, 0, 0)])["p"] \
        == pytest.approx(1 / 8)
    assert st.designation_test([(2, 0, 0), (1, 0), (1, 0, 0, 0)])["p"] \
        == pytest.approx(1 / 24)


# ------------------------------------------ F-2: shape-rule sensitivity

def test_sample_variance_shape_is_disclosed_and_below_bar():
    counts = [5, 3, 1, 1, 1, 1, 1, 1] + [0] * 24
    h = cp.dispersion_hat(counts)
    assert h["shape_sample_variance"] == pytest.approx(0.2921, abs=2e-4)
    assert h["shape_sample_variance"] < h["shape"]
    rec = json.loads(e.POWER_PATH.read_text())
    s = rec["dispersion_shape_sensitivity"]
    assert s["shape_sample_variance"] == pytest.approx(
        h["shape_sample_variance"])
    r = rec["committed_rates"]["1b"]["H_shortcut"]
    w = cp.world_probs(
        cp.p_fire_gamma(r["reach"], e.K_NEW_3E["1b"], s["shape_sample_variance"]),
        cp.p_fire_gamma(r["non"], e.K_NEW_3E["1b"], s["shape_sample_variance"]),
        n_reach=32, n_non=13, m_min=rec["m_min"])
    assert s["P_shortcut_H_shortcut"]["1b"] == pytest.approx(
        w["worlds"]["SHORTCUT"])
    # the finding itself, executable: .7447 < .75 while the frozen rule
    # gives .7636 — within one estimator convention of the bar
    assert s["P_shortcut_H_shortcut"]["1b"] < cp.POWER_BAR
    assert rec["power_at_named_alternative"]["1b"] >= cp.POWER_BAR
    assert s["below_bar_under_sample_variance"] is True
    assert rec["declared_underpowered_under_sample_variance_shape"] is True
    assert any("SHAPE-RULE SENSITIVITY" in line
               for line in rec["concessions_printed_in_advance"])
    # Michael's ruling (2026-08-21): declared underpowered in advance
    assert rec["declared_underpowered_ruling"]["declared"] is True
    assert any("DECLARED UNDERPOWERED IN ADVANCE" in line
               for line in rec["concessions_printed_in_advance"])


# --------------------------------------- F-3: gate-1 vs tranche pins

def _trees(tmp):
    e3 = fs.write_exp3_tree(tmp / "exp3")
    c3 = fs.write_3c_tree(tmp / "exp3c")
    d3 = fs.write_3d_tree(tmp / "exp3d")
    fs.write_3e_tree(tmp / "exp3e", d3,
                     new_fires={"1b": [(0, 40, 0)], "410m": []})


def _load_both(tmp):
    labels, answers = fs.rung_items("reverse_string")
    cells = e.load_new_cells_3e(tmp / "exp3e", verify_fn=c.load_verify_3c(),
                                items=fs.SUBSET, answers=answers,
                                labels=labels, answer_type_pin="word")
    gate1 = e.load_gate1_3e(
        tmp / "exp3e", items=fs.SUBSET,
        expected_fires={s: fs.e_expected_gate1_fires(s)
                        for s in e.SIZES_3E})
    return cells, gate1


def test_gate1_vs_tranche_passes_on_a_coherent_world(tmp_path):
    _trees(tmp_path)
    cells, gate1 = _load_both(tmp_path)
    assert cells["1b"]["model_sha"] == "synthetic-1b"
    e.check_gate1_vs_tranche_3e(
        gate1, cells, items_sha_pin=fs.SYN_ITEMS_SHA["reverse_string"])


def test_gate1_refuses_items_sha_off_the_pin(tmp_path):
    _trees(tmp_path)
    p = tmp_path / "exp3e/results/gate1/1b_trained/reverse_string.json"
    rec = json.loads(p.read_text())
    rec["items_sha256"] = "items-some-other-file"
    p.write_text(json.dumps(rec))
    cells, gate1 = _load_both(tmp_path)
    with pytest.raises(ValueError, match="items_sha256"):
        e.check_gate1_vs_tranche_3e(
            gate1, cells, items_sha_pin=fs.SYN_ITEMS_SHA["reverse_string"])


def test_gate1_refuses_model_sha_unlike_the_tranche(tmp_path):
    _trees(tmp_path)
    p = tmp_path / "exp3e/results/gate1/410m_trained/reverse_string.json"
    rec = json.loads(p.read_text())
    rec["model_sha"] = "synthetic-other-weights"
    p.write_text(json.dumps(rec))
    cells, gate1 = _load_both(tmp_path)
    with pytest.raises(ValueError, match="model_sha"):
        e.check_gate1_vs_tranche_3e(
            gate1, cells, items_sha_pin=fs.SYN_ITEMS_SHA["reverse_string"])


def test_shards_refuse_incoherent_or_missing_model_sha(tmp_path):
    _trees(tmp_path)
    block = e.SEED_BLOCKS["1b"][2]
    p = (tmp_path / "exp3e/results/sampling/1b_trained"
         / f"{e.shard_name(block)}.json")
    rec = json.loads(p.read_text())
    rec["model_sha"] = "synthetic-other-weights"
    p.write_text(json.dumps(rec))
    with pytest.raises(ValueError, match="not one model"):
        _load_both(tmp_path)
    del rec["model_sha"]
    p.write_text(json.dumps(rec))
    with pytest.raises(ValueError, match="no model_sha"):
        _load_both(tmp_path)
