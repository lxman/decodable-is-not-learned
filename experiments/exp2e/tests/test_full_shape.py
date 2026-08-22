"""Every verdict-tree terminal, executed end to end on synthetic 2e
trees through 2d's frozen loaders and 2e's referent phase."""
import math

import numpy as np
import pytest

from experiments.exp2d import analyze_2d as a2d
from experiments.exp2d import stats_2d as st
from experiments.exp2e import analyze_2e as a
from experiments.exp2e import functionals_2e as fn
from experiments.exp2e.tests import full_shape as fs


@pytest.fixture(scope="module")
def worlds(tmp_path_factory):
    out = {}
    for name, kwargs, want in fs.world_specs():
        tmp = tmp_path_factory.mktemp(name.split()[0])
        out[name] = (fs.build_world(tmp, **kwargs), want)
    return out


def test_every_terminal_reached(worlds):
    got = {}
    for name, (verdict, want) in worlds.items():
        assert verdict["verdict"] == want, \
            f"{name}: got {verdict['verdict']!r}, want {want!r}\n" \
            f"reason: {verdict.get('reason')}"
        got.setdefault(verdict["verdict"], name)
    assert set(got) == set(fn.WORLDS)


def test_w1_pass_shape(worlds):
    v, _ = worlds["W1 PASS clean separation"]
    p = v["primary"]
    assert p["functional"] == "F1" and p["auc"] == 1.0 and p["block_p"] < .01
    assert p["ci"][0] > .5 and p["n_rising"] == 11 and p["n_flat"] == 23
    assert p["block_method"] == "sampled" and p["n_perms"] == 100_000
    assert p["bootstrap_n_valid"] + p["bootstrap_n_dropped"] == 10_000
    assert p["eps"] == 1 / 64_000 and p["alpha"] == .01 and p["auc_bar"] == .75
    # the disclosure rides verbatim on the record and in the sentence
    assert v["known_inputs_caveat"] == a.KNOWN_INPUTS_CAVEAT_2E
    assert "known to the designer" in v["known_inputs_caveat"]
    s = v["licensed_sentence_if_pass"]
    assert "2d's null was its threshold's" in s and "B0" in s \
        and "floor alone" in s and a.KNOWN_INPUTS_CAVEAT_2E in s
    b0 = v["secondaries"]["functionals"]["B0"]["auc"]
    assert f"{b0:.4f}" in s
    # referent phase recorded
    ref = v["referents"]
    assert ref["failures"] == [] and ref["manifest"]["n_files"] == 273
    assert ref["main_tally_pin"] == "PASS (68/68 cells)"
    assert ref["comparison_2d"]["gate"] == "PASS" and \
        ref["comparison_2d"]["auc"] == v["_pins"]["verdict_2d_pin"]["auc"]
    assert ref["outcome_known_answer_gate"].startswith("PASS")
    # secondaries
    sec = v["secondaries"]
    assert set(sec["functionals"]) == {"F1", "F2", "F3", "B0"}
    for k in ("F2", "F3", "B0"):
        assert "auc" in sec["functionals"][k] and "block_p" in sec["functionals"][k]
    d = sec["f1_minus_b0"]
    assert d["diff_obs"] == pytest.approx(1.0 - b0) and len(d["ci_diff"]) == 2
    assert set(sec["ordering_vs_corrected_ascent"]) == {"F1", "F2", "F3", "B0"}
    assert sec["ordering_vs_corrected_ascent"]["F1"]["rho"] is not None
    pil = sec["pilot_replication"]
    assert pil["eps"] == 1 / 8_000 and pil["n_draws_per_cell"] == 4_000
    assert "auc" in pil and "rho_vs_corrected_ascent" in pil \
        and "rank_corr_pilot_vs_main_f1" in pil
    assert sec["replication_1b_only"]["auc"] == 1.0
    assert sec["replication_410m_only"]["auc"] == 1.0
    pr = sec["probe_predictor_2c"]
    assert pr["auc"] == pytest.approx(a.PROBE_2C_AUC_PIN) and \
        pr["rho_2c"] == a2d.VERDICT_2C_PIN["rho"]
    sens = sec["sensitivity"]
    assert [e["eps"] for e in sens["eps"]] == list(fn.EPS_SENSITIVITY)
    assert sens["eps"][0]["auc"] == p["auc"]      # the first IS the primary
    assert "auc" in sens["majority_floor_only"] and \
        sens["majority_floor_only"]["rungs_affected"] == sorted(
            a2d.bt.OPTION_LISTING_PIN)
    assert sens["drop_first_digit_run_rungs"]["n_rungs"] == 32 and \
        sens["drop_first_digit_run_rungs"]["dropped"] == ["base12_digitsum", "base13"]
    assert sec["comparison_2d_thresholded"]["auc"] == ref["comparison_2d"]["auc"]
    # per-rung table carries everything §5.4 lists
    row = v["per_rung"]["antonym"]
    for k in ("rate_410m", "rate_1b", "floor", "F1", "F2", "F3", "B0",
              "rising", "corrected_ascent", "F1_pilot", "score_2d"):
        assert k in row
    assert row["rising"] and row["F1"] > 0
    assert v["per_rung"]["rev_string7"]["F1"] == pytest.approx(
        math.log((1 / 64_000) / .002))
    assert len(v["per_rung"]) == 34


def test_w1_f1_is_the_tree_input(worlds):
    v, _ = worlds["W1 PASS clean separation"]
    y = np.array([int(v["per_rung"][r]["rising"]) for r in a2d.RUNGS])
    x = np.array([v["per_rung"][r]["F1"] for r in a2d.RUNGS])
    assert v["primary"]["auc"] == st.auc(x, y)


def test_w2_fail_and_w3_indeterminate_reasons(worlds):
    v2, _ = worlds["W2 FAIL predictor uninformative"]
    assert "includes .5" in v2["reason"]
    v3, _ = worlds["W3 INDETERMINATE partial separation"]
    assert v3["primary"]["ci"][0] > .5 and "excludes .5" in v3["reason"]


def test_w9_floor_covariate_is_the_primary_not_the_raw_rate(worlds):
    """F1 and F2 disagree here; the tree must have read F1."""
    v, _ = worlds["W9 PASS floor-relative only"]
    f = v["secondaries"]["functionals"]
    assert v["primary"]["auc"] == f["F1"]["auc"] == 1.0
    assert f["F2"]["auc"] < .75 and f["F2"]["auc"] != f["F1"]["auc"]
    assert v["primary"]["functional"] == "F1"
    # every synthetic rung has draws (the two reversal rungs carry
    # exp3's committed 0/0/1 in every world): no zero-draw ordering
    # artefact among the 32 synthetic rungs
    assert all(r["verified_410m"] > 0 for k, r in v["per_rung"].items()
               if k not in a2d.REVERSAL_RUNGS)
    assert v["per_rung"]["rev_string7"]["verified_410m"] == 0
    # ε at ten draws (1/3,200) dominates the sub-.01 floors and pulls
    # the separation down (.913 here): the sensitivity row is the point
    sens = v["secondaries"]["sensitivity"]["eps"]
    assert sens[0]["auc"] == 1.0 and sens[2]["auc"] < sens[0]["auc"]


def test_refusal_worlds_name_their_reason(worlds):
    v4, _ = worlds["W4 INSUFFICIENT_DATA manifest file changed"]
    assert "pilot/410m_trained/mod17.json" in "".join(v4["referents"]["failures"])
    assert v4["primary"] is None
    v5, _ = worlds["W5 INSUFFICIENT_DATA stored tally disagrees"]
    assert any("disagree with the recompute" in f for f in v5["referents"]["failures"])
    v6, _ = worlds["W6 INSUFFICIENT_DATA 2d primary not reproduced"]
    assert any("2d comparison" in f for f in v6["referents"]["failures"])
    v7, _ = worlds["W7 INSUFFICIENT_DATA tally pin disagrees"]
    assert any("tally pin" in f and "antonym/410m" in f
               for f in v7["referents"]["failures"])
    v8, _ = worlds["W8 INSUFFICIENT_DATA tier file missing"]
    assert any("missing" in f for f in v8["referents"]["failures"])
    for v in (v4, v5, v6, v7, v8):
        assert v["known_inputs_caveat"] == a.KNOWN_INPUTS_CAVEAT_2E
        assert v["verdict"] == "INSUFFICIENT_DATA"
