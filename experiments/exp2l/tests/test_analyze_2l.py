# experiments/exp2l/tests/test_analyze_2l.py
"""analyze_2l: the record-failure functions on hand records (every
pinned field), the 13B loaders on a short synthetic tree, outcomes over
the grid only (step 0 excluded), rung level / first-correct / collapses
/ non-monotone on hand data, the power-record loader and claims check,
S4 matched thinning and S5's answer prior on real committed rows, the
tree with the 2l disclosures and licences, label-prefix disjointness,
the import-surface refusal, run() on an empty tree (INSUFFICIENT_DATA,
never a raise), the referent builder on a temp tree. No model contact."""
from __future__ import annotations

import ast
import json
import re
from pathlib import Path

import numpy as np
import pytest

from experiments.exp2d import analyze_2d as a2d
from experiments.exp2d import battery_2d as bt
from experiments.exp2g import battery_2g as bg
from experiments.exp2g import predictor_2g as pr
from experiments.exp2g import strata_2g as sg
from experiments.exp2h import battery_2h as bh
from experiments.exp2i import analyze_2i as an2i
from experiments.exp2i import battery_2i as bi
from experiments.exp2i.run import endpoint_2i as ep2i
from experiments.exp2j import analyze_2j as an2j
from experiments.exp2j import functionals_2j as fn
from experiments.exp2k import analyze_2k as an2k
from experiments.exp2k import battery_2k as bk
from experiments.exp2l import analyze_2l as an
from experiments.exp2l import battery_2l as bl
from experiments.exp2l import make_referents_2l as mkr

SHORT_GRID = (1000, 2000, bl.ENDPOINT_STEP_13B)
R_SMALL = ("antonym", "antonym6")


@pytest.fixture(autouse=True)
def _frozen_pin(monkeypatch):
    monkeypatch.setattr(bl, "FROZEN_SHA256_2L", bl.frozen_from_disk(strict=False))


def _manifest():
    return json.loads(bl.CHECKPOINTS_PATH.read_text())


def _shrink(monkeypatch):
    monkeypatch.setattr(bl, "GRID_13B", SHORT_GRID)
    monkeypatch.setattr(bl, "load_manifest_13b", lambda path, sha_pin: _manifest())


def _battery():
    return bg.load_battery()


def _strata():
    pred2g = pr.load_predictor(bg.predictor_path(bg.EXP2G), sha_pin=bh.PREDICTOR_2G_SHA)
    return sg.from_json(pred2g["strata"])


def _w(p: Path, obj) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj))


def _ev(cap, k):
    bits = [1] * k + [0] * (bt.N_ITEMS - k)
    conts = [f" {it['answer']}" if b else " zzz" for b, it in zip(bits, cap["eval_items"])]
    return {"bits": bits, "correct": k, "continuations": conts}


def _ckpt(entry, digest="D"):
    return {"revision": entry["revision"], "commit": entry["commit"], "kind": entry["kind"],
            "files": list(entry["files"]), "weight_sha256": digest, "config_source": "cs",
            "tokenizer_source": "ts"}


def _endpoint_rec(which, rung, k, *, entry=None):
    man = _manifest()
    entry = entry or (bl.entry_13b(man, bl.ENDPOINT_STEP_13B) if which == "stage1_final"
                      else bl.entry_main_13b(man))
    cap = _battery()[rung]
    return ep2i.item_record_2i(rung=rung, family=bl.FAMILY, size=bl.SIZE_OUT, which=which, cap=cap,
                               ev=_ev(cap, k), ckpt=_ckpt(entry),
                               seal={"tag": bl.PREDICTOR_TAGS_2L, "sha256": bl.PREDICTOR_SHA_2L}, t_s=0.0)


def _step_rec(step, rung, k, esha="E" * 64):
    entry = bl.entry_13b(_manifest(), step)
    cap = _battery()[rung]
    return bl.item_record_2l(rung=rung, cap=cap, ev=_ev(cap, k), ckpt=_ckpt(entry), step=step,
                             endpoint_sha=esha, t_s=0.0)


# --------------------------------------------------- record failures

def test_endpoint_record_failures_2l_pins_every_field():
    verify = a2d.load_verify()
    cap = _battery()["antonym"]
    entry = bl.entry_13b(_manifest(), bl.ENDPOINT_STEP_13B)
    rec = _endpoint_rec("stage1_final", "antonym", 10)
    ok = an.endpoint_record_failures_2l(rec, which="stage1_final", rung="antonym", cap=cap, entry=entry, verify_fn=verify)
    assert ok == []
    for field, value, needle in (("size", "olmo7b", "size"), ("family", "pythia", "family"),
                                 ("which", "main", "which"), ("rung", "odd6", "rung"),
                                 ("seal_tag", bi.PREDICTOR_SEAL_TAG, "seal_tag"),
                                 ("predictor_sha", "0" * 64, "predictor_sha"),
                                 ("items_sha256", "x", "items_sha256"), ("commit", "0" * 40, "commit"),
                                 ("correct", 11, "correct"), ("n", 499, "n")):
        bad = an.endpoint_record_failures_2l(dict(rec, **{field: value}), which="stage1_final", rung="antonym",
                                             cap=cap, entry=entry, verify_fn=verify)
        assert any(needle in b for b in bad), (field, bad)
    r2 = dict(rec, bits=[1 - b for b in rec["bits"]], correct=bt.N_ITEMS - 10)
    bad = an.endpoint_record_failures_2l(r2, which="stage1_final", rung="antonym", cap=cap, entry=entry, verify_fn=verify)
    assert any("re-verification" in b for b in bad)
    assert all(b.startswith("endpoint olmo13b") for b in bad)


def test_step_record_failures_2l_pins_step_commit_and_endpoint_sha():
    verify = a2d.load_verify()
    cap = _battery()["antonym"]
    man = _manifest()
    rec = _step_rec(1000, "antonym", 5)
    entry = bl.entry_13b(man, 1000)
    assert an.step_record_failures_2l(rec, step=1000, rung="antonym", cap=cap, entry=entry, verify_fn=verify, endpoint_sha="E" * 64) == []
    bad = an.step_record_failures_2l(rec, step=1000, rung="antonym", cap=cap, entry=entry, verify_fn=verify, endpoint_sha="F" * 64)
    assert any("endpoint_sha256" in b for b in bad)
    bad = an.step_record_failures_2l(dict(rec, step=2000), step=1000, rung="antonym", cap=cap, entry=entry, verify_fn=verify, endpoint_sha="E" * 64)
    assert any("step" in b for b in bad)
    bad = an.step_record_failures_2l(rec, step=1000, rung="antonym", cap=cap, entry=bl.entry_13b(man, 2000), verify_fn=verify, endpoint_sha="E" * 64)
    assert any("commit" in b for b in bad)
    bad = an.step_record_failures_2l(dict(rec, seal_tag=bl.PREDICTOR_TAGS_2L), step=1000, rung="antonym", cap=cap, entry=entry, verify_fn=verify, endpoint_sha="E" * 64)
    assert any("seal_tag" in b for b in bad)
    rec0 = _step_rec(bl.STEP0, "antonym", 0)
    assert an.step_record_failures_2l(rec0, step=bl.STEP0, rung="antonym", cap=cap, entry=bl.entry_13b(man, bl.STEP0), verify_fn=verify, endpoint_sha="E" * 64) == []
    assert all(b.startswith("olmo13b/step") for b in bad)


# ----------------------------------------------------------- loaders

def _tree(root, *, k_by_step=None, step0_k=0, esha="E" * 64, main_k=0):
    man = _manifest()
    battery = _battery()
    k_by_step = k_by_step or {}
    for step in bl.GRID_13B + (bl.STEP0,):
        entry = bl.entry_13b(man, step)
        _w(bl.checkpoint_record_path(root, step), {"family": bl.FAMILY, "size": bl.SIZE_OUT, "step": step,
                                                   "revision": entry["revision"], "commit": entry["commit"],
                                                   "sha256": dict(entry["lfs_sha256"]),
                                                   "loading_info": {"missing_keys": 0, "unexpected_keys": 0, "mismatched_keys": 0},
                                                   "digest": "D", "download_seconds": 0.0})
        for r in bt.RUNGS:
            k = step0_k if step == bl.STEP0 else k_by_step.get(step, 0)
            _w(bl.record_path(root, step, r), _step_rec(step, r, k, esha))
    for r in bt.RUNGS:
        _w(bl.endpoint_record_path(root, "stage1_final", r), _endpoint_rec("stage1_final", r, k_by_step.get(bl.ENDPOINT_STEP_13B, 0)))
        _w(bl.endpoint_record_path(root, "main", r), _endpoint_rec("main", r, main_k))
    return man, battery


def test_load_endpoint_and_sweep_13b(tmp_path, monkeypatch):
    _shrink(monkeypatch)
    man, battery = _tree(tmp_path, k_by_step={1000: 2, 2000: 5, bl.ENDPOINT_STEP_13B: 9}, step0_k=1)
    verify = a2d.load_verify()
    st1 = an.load_endpoint_which_2l(tmp_path, "stage1_final", battery, verify, entry=bl.entry_13b(man, bl.ENDPOINT_STEP_13B))
    assert set(st1) == set(bt.RUNGS) and st1["antonym"]["correct"] == 9
    mn = an.load_endpoint_which_2l(tmp_path, "main", battery, verify, entry=bl.entry_main_13b(man))
    assert mn["antonym"]["correct"] == 0
    sweep = an.load_sweep_13b(tmp_path, battery, verify, manifest=man, endpoint_sha="E" * 64)
    assert set(sweep) == set(SHORT_GRID) | {bl.STEP0}
    assert sweep[bl.STEP0]["antonym"]["correct"] == 1
    with pytest.raises(ValueError, match="endpoint_sha256"):
        an.load_sweep_13b(tmp_path, battery, verify, manifest=man, endpoint_sha="F" * 64)
    bl.record_path(tmp_path, 2000, "odd6").unlink()
    with pytest.raises(FileNotFoundError):
        an.load_sweep_13b(tmp_path, battery, verify, manifest=man, endpoint_sha="E" * 64)
    _w(bl.record_path(tmp_path, 2000, "odd6"), _step_rec(2000, "odd6", 5))
    cp = bl.checkpoint_record_path(tmp_path, 1000)
    c = json.loads(cp.read_text())
    c["sha256"] = {k: "0" * 64 for k in c["sha256"]}
    cp.write_text(json.dumps(c))
    with pytest.raises(ValueError, match="downloaded .* sha"):
        an.load_sweep_13b(tmp_path, battery, verify, manifest=man, endpoint_sha="E" * 64)


def test_outcomes_13b_excludes_step0_and_counts_grid_points(tmp_path, monkeypatch):
    _shrink(monkeypatch)
    man, battery = _tree(tmp_path, k_by_step={1000: 2, 2000: 5, bl.ENDPOINT_STEP_13B: 9}, step0_k=50)
    sweep = an.load_sweep_13b(tmp_path, battery, a2d.load_verify(), manifest=man, endpoint_sha="E" * 64)
    out = an.outcomes_13b(sweep, rungs=("antonym",))
    y = out["antonym"]["y"]
    assert y[0] == 3 and y[2] == 2 and y[5] == 1 and y[9] == 0 and max(y) == len(SHORT_GRID)
    assert out["antonym"]["first"][0] == 1000 and out["antonym"]["first"][5] == bl.ENDPOINT_STEP_13B
    assert out["antonym"]["n_pos"] == 9
    assert set(out["antonym"]["counts_by_step"]) == set(SHORT_GRID)       # step 0 absent
    fc = an._first_correct_outcome_13b(out, ("antonym",))
    assert fc["antonym"]["y"][0] == bl.ENDPOINT_STEP_13B + 1 - 1000 and fc["antonym"]["y"][9] == 0
    rl = an.rung_level_13b(out, bg.load_floors(), rungs=("antonym",))
    assert set(rl["antonym"]) == {"s_star", "clears", "final_clears", "transient_clears"}


def test_collapses_and_non_monotone_on_hand_data():
    sweep = {s: {"antonym": {"correct": c, "continuations": [" 13"] * 480 + [" x"] * 20}}
             for s, c in ((1000, 0), (2000, 30), (596057, 20))}
    for s in (2000, 596057):
        sweep[s]["antonym"]["continuations"] = [f" {i}" for i in range(500)]
    col = an.collapses_13b(sweep, rungs=("antonym",))
    assert col == [{"rung": "antonym", "step": 1000, "continuation": " 13", "n_identical": 480, "correct": 0}]
    out = {"antonym": {"counts_by_step": {1000: 0, 2000: 30, 596057: 20}}}
    nm = an.non_monotone_13b(out, ("antonym",))
    assert nm["antonym"] == {"drops": [[2000, 596057, 30, 20]], "n_drops": 1, "max": 30}


# --------------------------------------------------------------- rung set

def test_rung_set_load_and_checks(tmp_path, monkeypatch):
    _shrink(monkeypatch)
    man, battery = _tree(tmp_path, k_by_step={bl.ENDPOINT_STEP_13B: 480})
    floors = bg.load_floors()
    st1 = an.load_endpoint_which_2l(tmp_path, "stage1_final", battery, a2d.load_verify(), entry=bl.entry_13b(man, bl.ENDPOINT_STEP_13B))
    rs = bl.rung_set_from_counts_2l({r: st1[r]["correct"] for r in bt.RUNGS}, floors)
    _w(bl.rung_set_path(tmp_path), {**rs, "endpoint_file_sha256": {}})
    got = an._load_rung_set_2l(tmp_path)
    assert got["R_PRIMARY"] == sorted(bl.R_CAP_2K)
    assert an._check_rung_set_vs_endpoint_2l(got, st1) == []
    assert an._check_rung_set_derivation_2l(got, st1, floors) == []
    bad = an._check_rung_set_derivation_2l(dict(got, R_PRIMARY=got["R_PRIMARY"][:-1]), st1, floors)
    assert any("R_PRIMARY" in b for b in bad)
    st1b = dict(st1, antonym=dict(st1["antonym"], correct=3))
    assert any("antonym" in b for b in an._check_rung_set_vs_endpoint_2l(got, st1b))
    _w(bl.rung_set_path(tmp_path), {**rs, "R_PRIMARY": rs["R_PRIMARY"] + ["count_div13"], "endpoint_file_sha256": {}})
    with pytest.raises(ValueError, match="subset of 2k's nine"):
        an._load_rung_set_2l(tmp_path)


# ------------------------------------------------------------------ power

def _power_rec(r_primary, *, status="POWERED", psha=bl.PREDICTOR_SHA_2L, x256=None, x_b=None, n_pos=None):
    strata = _strata()
    x256 = x256 or bi.sampler_counts_pythia("1b", r_primary)     # any real vector works for shape tests
    x_b = x_b or x256
    dropped_a = list(an2i._degenerate_rungs(x256, strata, r_primary))
    strata_b = an2i._composite_strata_median(strata, x256, r_primary)
    dropped_b = list(an2i._degenerate_rungs(x_b, strata_b, r_primary))
    n_pos = n_pos or {r: 100 for r in r_primary}

    def one(dropped):
        keep = [r for r in r_primary if r not in dropped]
        return {"declared_status": status, "declaration": "x", "rungs": list(r_primary),
                "n_trained_steps": bl.n_trained_13b(), "dropped_degenerate": dropped,
                "rungs_simulated": keep, "n_pos_lower_bound": n_pos, "t_bar": an.T_BAR,
                "alpha": an.ALPHA, "thin": len(keep) < 3}
    return {"A": one(dropped_a), "B": one(dropped_b),
            "block_sd_A": {"n_sim": 3, "mean_block_sd_at_declare": 0.01, "mean_block_sd_null": 0.005,
                           "per_block_mean_T_at_declare": [0.1, 0.1, 0.1, 0.1], "blocks": 4},
            "predictor_sha256": psha, "calibration_note": an2i.CALIBRATION_SENTENCE_2I,
            "shape_note": "x", "note": "x"}


def test_load_power_2l_and_claims(tmp_path):
    r_primary = tuple(sorted(bl.R_CAP_2K))
    rec = _power_rec(r_primary)
    _w(bl.power_path(tmp_path), rec)
    got = an.load_power_2l(tmp_path, r_primary, bl.PREDICTOR_SHA_2L)
    assert got["A"]["declared_status"] == "POWERED" and got["block_sd_A"]["blocks"] == 4
    for mut, needle in ((dict(predictor_sha256="0" * 64), "predictor_sha256"),
                        ({"A": dict(rec["A"], rungs=list(r_primary)[:-1])}, "rungs"),
                        ({"B": dict(rec["B"], n_trained_steps=21)}, "n_trained_steps"),
                        ({"A": dict(rec["A"], declared_status="MAYBE")}, "declared_status"),
                        (dict(block_sd_A=None), "block_sd_A")):
        _w(bl.power_path(tmp_path), {**rec, **mut})
        with pytest.raises(ValueError, match=needle):
            an.load_power_2l(tmp_path, r_primary, bl.PREDICTOR_SHA_2L)
    strata = _strata()
    x256 = bi.sampler_counts_pythia("1b", r_primary)
    stage1 = {r: {"correct": 100} for r in r_primary}
    assert an.check_power_claims_2l(rec, x256, x256, strata, r_primary, stage1) == []
    bad = an.check_power_claims_2l({**rec, "A": dict(rec["A"], n_pos_lower_bound={r: 0 for r in r_primary})},
                                   x256, x256, strata, r_primary, stage1)
    assert any("n_pos_lower_bound" in b and "A" in b for b in bad)
    bad = an.check_power_claims_2l({**rec, "B": dict(rec["B"], rungs_simulated=[])}, x256, x256, strata, r_primary, stage1)
    assert any("rungs_simulated" in b and "B" in b for b in bad)
    bad = an.check_power_claims_2l({**rec, "A": dict(rec["A"], t_bar=0.0)}, x256, x256, strata, r_primary, stage1)
    assert any("t_bar" in b for b in bad)
    assert an.POWER_CLAIM_FIELDS_2L == ("dropped_degenerate", "rungs_simulated", "n_pos_lower_bound", "t_bar", "alpha", "thin")


# ------------------------------------------------------------- secondaries

def _fake_out(rungs, seed=0):
    rng = np.random.default_rng(seed)
    out = {}
    for r in rungs:
        y = [int(v) for v in rng.integers(0, bl.n_trained_13b() + 1, size=bt.N_ITEMS)]
        out[r] = {"y": y, "n_pos": sum(1 for v in y if v > 0),
                  "first": [None if v == 0 else 1000 for v in y]}
    return out


def test_s4_matched_2l_uses_2k_rule_and_2j_blocks():
    strata = _strata()
    rungs = ("antonym", "add_base8")
    battery, verify = _battery(), a2d.load_verify()
    bits_b = {r: fn.verified_bits(fn.draw_rows_2i(bi.EXP2I, r), battery[r], verify) for r in rungs}
    x_a64 = bi.sampler_counts_pythia("1b", rungs)
    x_a256 = {r: [min(64 * 4, c * 4) for c in x_a64[r]] for r in rungs}
    out = _fake_out(rungs)
    s4 = an.s4_matched_2l(bits_b, x_a64, x_a256, out, strata, rungs)
    for r in rungs:
        m = bk.matched_k_256(bk.mean_rate(x_a64[r], 64), bk.mean_rate(fn.counts_from_bits(bits_b[r]), 64))
        assert s4["per_rung"][r]["k"] == m["k"] and s4["per_rung"][r]["n_blocks"] == m["n_blocks"]
        assert set(s4["per_rung"][r]) >= {"k", "capped", "n_blocks", "rate_A64", "rate_B64", "mean", "min", "max", "n_blocks_used"}
    assert s4["T_A256"] == an2j.t_only(x_a256, "1b:k256", out, strata, rungs)["T"]
    assert "thinned_B" in s4 and "T" in s4["thinned_B"]
    assert s4["increment"] == (None if s4["thinned_B"]["T"] is None else s4["thinned_B"]["T"] - s4["T_A256"])


def test_s5_answer_prior_2l_is_2j_functional_on_2i_rows():
    strata = _strata()
    rungs = ("antonym",)
    battery = _battery()
    rows = {r: fn.draw_rows_2i(bi.EXP2I, r) for r in rungs}
    out = _fake_out(rungs)
    s5 = an.s5_answer_prior_2l(rows, battery, out, strata, rungs, n_perm=20, n_boot=5)
    assert s5["pi"]["antonym"] == fn.wrong_target_propensity(rows["antonym"], battery["antonym"])
    assert s5["test"]["stratified"]["T"] is not None and s5["non_gating"] is True
    assert s5["source"] == "2j wrong_target_propensity on 2i's sealed OLMo-2 1B draws"


def test_extra_rungs_2l_shape():
    strata = _strata()
    out = _fake_out(("count_div13", "reverse_string"))
    x64 = bi.sampler_counts_pythia("1b", ("count_div13", "reverse_string"))
    x_b = {r: list(x64[r]) for r in x64}
    res = an._extra_rungs_2l(x64, x_b, out, strata, r_eleven_extra=("count_div13",), r_extra=("reverse_string",))
    assert set(res["eleven_extra"]["count_div13"]) == {"stratified_d_A64", "stratified_d_B", "n_pos"}
    assert set(res["extra"]["reverse_string"]) == {"raw_d_A64", "raw_d_B", "n_pos"}


# ------------------------------------------------------------------- tree

def _prim(T, p, fires, eligible=("a", "b", "c"), named=None):
    return {"stratified": {"T": T, "p": p, "n_perm": 10000, "n_ge": 0}, "fires": fires,
            "named_inside": named, "eligible": list(eligible), "per_rung": {}}


def test_verdict_2l_worlds_disclosures_and_licences():
    powered = {"A": {"declared_status": "POWERED"}, "B": {"declared_status": "POWERED"}}
    under_b = {"A": {"declared_status": "POWERED"}, "B": {"declared_status": "DECLARED UNDERPOWERED IN ADVANCE"}}
    nine = tuple(sorted(bl.R_CAP_2K))
    ins = an.verdict_2l(["x"], None, None, None, nine)
    assert ins["verdict"] == "INSUFFICIENT_DATA" and an._licensed_2l(ins) == an.LICENSED_2L["INSUFFICIENT_DATA"]
    for a, b, want in ((True, False, "SHARED"), (False, True, "LINEAGE"), (True, True, "BOTH"), (False, False, "NEITHER")):
        t = an.verdict_2l([], _prim(0.2 if a else 0.02, 0.001, a), _prim(0.2 if b else 0.02, 0.001, b), powered, nine)
        assert t["verdict"] == want and an._licensed_2l(t).startswith(an.LICENSED_2L[want])
        assert an.KNOWN_INPUTS_CAVEAT_2L in an._licensed_2l(t)
    t = an.verdict_2l([], _prim(0.2, 0.001, True), _prim(0.02, 0.5, False), under_b, nine)
    assert an.DISCLOSURE_UNDERPOWERED_2L["B"] in t["disclosures"] and an.DISCLOSURE_UNDERPOWERED_2L["A"] not in t["disclosures"]
    assert an.DISCLOSURE_UNDERPOWERED_2L["B"] in an._licensed_2l(t)
    t = an.verdict_2l([], _prim(0.2, 0.001, True), _prim(0.02, 0.5, False), powered, nine[:2])
    assert an.DISCLOSURE_THIN_2L in t["disclosures"] and t["verdict"] == "SHARED"
    t = an.verdict_2l([], _prim(0.2, 0.001, True), _prim(None, 1.0, False, eligible=(), named="undefined: no eligible rung"), powered, nine)
    assert an2i.DISCLOSURE_UNDEFINED_2I["B"] in t["disclosures"]
    assert set(an.LICENSED_2L) == {"INSUFFICIENT_DATA", "SHARED", "LINEAGE", "BOTH", "NEITHER"}


def _all_failure_labels(path):
    # DEVIATION (plan defect, one sentence; fix round 1): the brief's
    # pure-regex extractor under-recovers real labels whenever a
    # collect_total thunk contains a comma (measured on the committed
    # upstream files: 14/33 analyze_2i.py, 17/39 analyze_2j.py, 17/37
    # analyze_2k.py), so this AST-based extractor (exp2k's own
    # precedent, `test_analyze_2k.py::_all_failure_labels_2k`) is used
    # for BOTH `mine` and `theirs` — isolating the true second
    # positional argument regardless of commas nested inside the
    # first; the f-string fallback regex (kept, for bare-name-thunk
    # labels) is unchanged from the brief.
    src = Path(path).read_text()
    tree = ast.parse(src)
    labels = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and getattr(node.func, "id", None) == "collect_total" \
                and len(node.args) == 2 and isinstance(node.args[1], ast.Constant):
            labels.append(node.args[1].value)
    for m in re.finditer(r'collect_total\([^,]+,\s*f"([^"{]+)', src):
        labels.append(m.group(1))
    return labels


def _all_failure_labels_2l():
    return _all_failure_labels(bl.EXP2L / "analyze_2l.py")


def test_failure_labels_disjoint_from_2i_2j_2k():
    mine = set(_all_failure_labels_2l())
    assert mine and all(lab.startswith("2l") for lab in mine)
    for other in (bi.EXP2I / "analyze_2i.py", bg.REPO / "experiments/exp2j/analyze_2j.py", bk.EXP2K / "analyze_2k.py"):
        theirs = set(_all_failure_labels(other))
        for a in mine:
            for b in theirs:
                assert not a.startswith(b) and not b.startswith(a), (a, b)


def test_check_imports_2l_refuses_unpinned_and_covers_2k_and_2j(monkeypatch):
    monkeypatch.setattr(an, "IMPORTED_SHA256_2L", None)
    with pytest.raises(RuntimeError, match="not pinned"):
        an.check_imports_2l()
    monkeypatch.setattr(an, "IMPORTED_SHA256_2L", {})
    try:
        an.check_imports_2l()
    except RuntimeError as e:
        assert str(e).startswith("unpinned module")   # a real gap before Task 5, never a crash elsewhere


def test_run_on_empty_tree_is_insufficient_never_raises(tmp_path):
    v = an.run(root_2l=tmp_path, root_2i=bi.EXP2I, root_2k=bk.EXP2K, n_perm=20, n_boot=5,
               referents_sha=False, imports_pinned=False, tag_exists=lambda t: True,
               blob_sha=lambda tag, rel: bg.sha256_file(bl.REPO / rel) if (bl.REPO / rel).is_file() else None,
               blobs_bound=lambda tag, paths, repo_root=None: [])
    assert v["verdict"] == "INSUFFICIENT_DATA" and v["tests"] is None and v["secondaries"] is None
    assert any("2l endpoint stage1_final" in f or "2l rung set" in f for f in v["referents"]["failures"])
    assert v["referents"]["pins_active"] == {"frozen_modules": True, "import_surface": False, "referent_manifest": False}
    assert v["known_inputs_caveat"] == an.KNOWN_INPUTS_CAVEAT_2L and v["model_contact"] == "none at analysis"


# -------------------------------------------------------------- referents

def test_make_referents_2l_lists_the_predictor_stage_and_2l_inputs(tmp_path, monkeypatch):
    files = mkr.referent_files()
    rel = {str(p.relative_to(bl.REPO)) for p in files}
    assert "experiments/exp2k/results/predictor_2k.json" in rel
    assert "experiments/exp2k/results/verdict.json" in rel
    assert "experiments/exp2k/results/k256/1b_trained/antonym.draws.jsonl.gz" in rel
    assert "experiments/exp2i/results/predictor/olmo1b/antonym.draws.jsonl.gz" in rel
    assert "experiments/exp2l/checkpoints_2l.json" in rel and "experiments/exp2l/hub_inventory_olmo13b.json" in rel
    assert "experiments/exp2l/power_2l.py" in rel
    for r in bk.INSTRUMENT_BLOBS_2K:
        assert r in rel
    assert "experiments/exp2i/run/endpoint_2i.py" in rel
    assert len(files) == len(set(files))
    monkeypatch.setattr(mkr, "N_FILES_2L", None)
    p = tmp_path / "r.json"
    rec = mkr.build(p, n_files=len(files))
    assert rec["n_files"] == len(files)
    monkeypatch.setattr(mkr, "N_FILES_2L", len(files))
    assert mkr.check_referents(p, sha_pin=bg.sha256_file(p)) == []
    with pytest.raises(ValueError, match="hashes to"):
        mkr.check_referents(p, sha_pin="0" * 64)
