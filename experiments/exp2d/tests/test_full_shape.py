"""Every verdict-tree terminal, executed end to end on synthetic 2d
trees through the frozen loaders (the freeze rule)."""
import pytest

from experiments.exp2d import analyze_2d as a
from experiments.exp2d import stats_2d as st
from experiments.exp2d.tests import full_shape as fs


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
        got[verdict["verdict"]] = name
    assert set(got) == set(st.WORLDS)


def test_worlds_w1_pass_shape(worlds):
    v, _ = worlds["W1 PASS clean separation"]
    p = v["primary"]
    assert p["auc"] == 1.0 and p["block_p"] < 0.01
    assert p["ci"][0] > 0.5 and p["n_rising"] == 11 and p["n_flat"] == 23
    assert p["block_method"] == "sampled" and p["n_perms"] == 100_000
    assert p["bootstrap_n_valid"] + p["bootstrap_n_dropped"] == 10_000
    assert v["gate1"]["diff_cells"] == [] and \
        v["gate1"]["total_draws_compared"] == 128_000
    assert v["outcome_summary"]["n_rising"] == 11
    assert v["twin_referent"]["fires"] == 0
    assert "whose outcome was known" in v["licensed_sentence_if_pass"]
    assert "ZERO free parameters" in v["known_outcome_caveat"]
    sec = v["secondaries"]
    assert sec["argmax_from_below"]["n_removed"] == 0
    assert sec["percolation_candidates"]["rungs"] == []
    assert sec["replication_1b_only"]["auc"] == 1.0
    # the probe predictor's AUC on the same label, from committed records
    import numpy as np
    probe = a.load_probe_predictor()
    y = np.array([int(v["rising"]) for v in v["per_rung"].values()])
    xp = np.array([probe[r] for r in a.RUNGS])
    assert sec["probe_predictor_auc"]["auc"] == pytest.approx(st.auc(xp, y))
    assert sec["ordering_vs_2c_frozen_ascent"]["comparability"][
        "2c_probe_predictor"]["rho"] == pytest.approx(0.368, abs=1e-3)
    assert v["per_rung"]["antonym"]["predictor_score"] > 0
    assert v["per_rung"]["reverse_string"]["sampled"]["1b"]["verified"] == 1
    assert v["per_rung"]["rev_string7"]["sampled"]["410m"]["verified"] == 0


def test_worlds_w2_fail_and_candidates(worlds):
    v, _ = worlds["W2 FAIL predictor uninformative"]
    p = v["primary"]
    assert p["ci"][0] <= 0.5 <= p["ci"][1]
    cands = v["secondaries"]["percolation_candidates"]
    # rising rungs with zero 1b draws AND probe zero in this world
    assert "sub3_mid" in cands["rungs"] and "arith_next" in cands["rungs"]
    assert cands["both_pair_rungs_land"] is True
    pair = v["secondaries"]["pair_5_4"]
    assert pair["sub3_mid"]["sampled"]["1b"]["verified"] == 0
    assert pair["sub3_mid"]["sampled"]["1b"]["cp95"][1] == pytest.approx(
        st.clopper_pearson(0, 32_000)[1])


def test_worlds_w3_indeterminate(worlds):
    v, _ = worlds["W3 INDETERMINATE partial separation"]
    p = v["primary"]
    assert p["ci"][0] > 0.5
    assert not (p["block_p"] < 0.01 and p["auc"] >= 0.75)


def test_worlds_w4_gate1_drift(worlds):
    v, _ = worlds["W4 INSUFFICIENT_DATA gate-1 drift"]
    assert v["gate1"]["diff_cells"] == ["reverse_string/1b"]
    d = v["gate1"]["diffs_verbatim"]["reverse_string/1b"]
    assert len(d) == 1 and d[0]["item"] == 7 and d[0]["draw"] == 11
    assert "got" in d[0] and "committed" in d[0]
    assert "differ from exp3's committed bytes" in v["reason"]


def test_restriction_removes_performable_rising(tmp_path):
    """A rising rung whose 1b greedy clears the floor is REMOVED from
    the restricted primary and the families recomputed."""
    _, floors = fs.battery()
    ris = fs.rising_rungs()
    v = fs.build_world(
        tmp_path,
        main_verified=fs.counts_for({r: floors[r]["floor"] + 0.2 for r in ris}),
        argmax_correct={("antonym", "1b"): 300, ("median5", "1b"): 250,
                        ("hamming12", "1b"): 400})
    fb = v["secondaries"]["argmax_from_below"]
    assert set(fb["rising_already_performable_at_1b"]) == {"antonym", "median5"}
    assert fb["n_removed"] == 2
    assert fb["per_rung"]["hamming12"]["performable_at_1b"] is True
    r = fb["restricted_primary"]
    assert r["n_rising"] == 9 and r["n_flat"] == 23
    assert v["primary"]["n_rising"] == 11           # the primary untouched
