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
import sys
import types
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
        lfs = dict(entry["lfs_sha256"])
        _w(bl.checkpoint_record_path(root, step), {"family": bl.FAMILY, "size": bl.SIZE_OUT, "step": step,
                                                   "revision": entry["revision"], "commit": entry["commit"],
                                                   "sha256": {n: lfs.get(n, f"non-lfs:{n}") for n in entry["files"]},
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


def test_checkpoint_record_failures_2l_measures_provenance_and_coverage():
    """FREEZE F-2: the checkpoint record's revision, commit and tensor
    digest were attested and never measured, and its sha table was
    checked over the 12 LFS shards only — a coverage claim over an
    unstated subset of the 13 candidate files the loader stages."""
    entry = bl.entry_13b(_manifest(), 1000)
    lfs = dict(entry["lfs_sha256"])
    assert len(entry["files"]) == 13 and len(lfs) == 12
    good = {"revision": entry["revision"], "commit": entry["commit"], "digest": "D",
            "sha256": {n: lfs.get(n, "non-lfs") for n in entry["files"]}}
    recs = {r: {"weight_sha256": "D"} for r in R_SMALL}
    assert an.checkpoint_record_failures_2l(good, step=1000, entry=entry, step_records=recs) == []
    for k in ("revision", "commit"):
        bad = an.checkpoint_record_failures_2l(dict(good, **{k: "elsewhere"}), step=1000,
                                               entry=entry, step_records=recs)
        assert any(k in b and "is not the manifest's" in b for b in bad)
    bad = an.checkpoint_record_failures_2l(dict(good, sha256=lfs), step=1000, entry=entry,
                                           step_records=recs)
    assert any("attests no sha" in b and "index.json" in b for b in bad)
    bad = an.checkpoint_record_failures_2l(dict(good, sha256=[]), step=1000, entry=entry,
                                           step_records=recs)
    assert any("not a table" in b for b in bad)
    bad = an.checkpoint_record_failures_2l(dict(good, digest="OTHER"), step=1000, entry=entry,
                                           step_records=recs)
    assert any("tensor digest" in b and R_SMALL[0] in b for b in bad)


def test_load_sweep_13b_carries_the_checkpoint_record_check(tmp_path, monkeypatch):
    _shrink(monkeypatch)
    man, battery = _tree(tmp_path, k_by_step={1000: 2, 2000: 5, bl.ENDPOINT_STEP_13B: 9})
    verify = a2d.load_verify()
    cp = bl.checkpoint_record_path(tmp_path, 2000)
    rec = json.loads(cp.read_text())
    rec["sha256"] = {k: v for k, v in rec["sha256"].items() if not k.endswith("index.json")}
    cp.write_text(json.dumps(rec))
    with pytest.raises(ValueError, match="attests no sha"):
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


def test_collapses_13b_threshold_is_inclusive():
    """Mutation gap (Task 5, #69): >= is inclusive -- exactly
    `threshold` (450) identical continuations must still collapse."""
    sweep = {1000: {"antonym": {"correct": 0,
                                "continuations": [" 13"] * 450 + [f" x{i}" for i in range(50)]}}}
    col = an.collapses_13b(sweep, rungs=("antonym",))
    assert col == [{"rung": "antonym", "step": 1000, "continuation": " 13", "n_identical": 450, "correct": 0}]


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
    # Mutation gap (Task 5, #55): the partition check. Dropping a member
    # from R_EXTRA (leaving R_PRIMARY, hence the subset-of-nine check,
    # untouched) so the union no longer equals R_13B must refuse.
    if rs["R_EXTRA"]:
        _w(bl.rung_set_path(tmp_path), {**rs, "R_EXTRA": rs["R_EXTRA"][:-1], "endpoint_file_sha256": {}})
        with pytest.raises(ValueError, match="do not partition"):
            an._load_rung_set_2l(tmp_path)
    # Mutation gap (Task 5, #56): _check_rung_set_derivation_2l's
    # per-key comparison is ORDER-sensitive -- rung_set_from_counts_2l's
    # own contract is a SORTED tuple, so a same-elements-different-order
    # file (a hand edit, or a producer that stopped sorting) is itself
    # drift and must be flagged, not silently accepted as a set match.
    shuffled = dict(got, R_PRIMARY=list(reversed(got["R_PRIMARY"])))
    bad_order = an._check_rung_set_derivation_2l(shuffled, st1, floors)
    assert any("R_PRIMARY" in b for b in bad_order)


def test_check_rung_set_endpoint_shas_2l(tmp_path, monkeypatch):
    """FREEZE F-3: `endpoint_file_sha256` was required present, published
    in the verdict's referents, and compared to nothing."""
    _shrink(monkeypatch)
    _tree(tmp_path, k_by_step={bl.ENDPOINT_STEP_13B: 480})
    shas = {}
    for which in bl.ENDPOINT_WHICH:
        for r in bt.RUNGS:
            p = bl.endpoint_record_path(tmp_path, which, r)
            shas[str(p.relative_to(tmp_path))] = bg.sha256_file(p)
    assert len(shas) == 68
    assert an._check_rung_set_endpoint_shas_2l({"endpoint_file_sha256": shas}, tmp_path) == []
    bad = an._check_rung_set_endpoint_shas_2l({"endpoint_file_sha256": {}}, tmp_path)
    assert any("attests nothing" in b for b in bad)
    one_rel = sorted(shas)[0]
    bad = an._check_rung_set_endpoint_shas_2l(
        {"endpoint_file_sha256": {**shas, one_rel: "0" * 64}}, tmp_path)
    assert any(one_rel in b and "is not the committed record's" in b for b in bad)
    bad = an._check_rung_set_endpoint_shas_2l(
        {"endpoint_file_sha256": {**shas, "results/endpoint/stray.json": "0" * 64}}, tmp_path)
    assert any("are not the endpoint records" in b for b in bad)
    bad = an._check_rung_set_endpoint_shas_2l({"endpoint_file_sha256": []}, tmp_path)
    assert any("not a table" in b for b in bad)
    bl.endpoint_record_path(tmp_path, "main", bt.RUNGS[0]).unlink()
    bad = an._check_rung_set_endpoint_shas_2l({"endpoint_file_sha256": shas}, tmp_path)
    assert any("is missing" in b for b in bad)


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


def test_load_power_2l_refuses_a_superset_of_rungs(tmp_path):
    """Mutation gap (Task 5, #44): rungs != -> subset. A power record
    whose A.rungs is a SUPERSET of r_primary (an extra, never-audited
    rung silently along for the ride) must be refused exactly as hard
    as a subset -- the field is a claim about R_PRIMARY, not merely a
    superset of it."""
    r_primary = tuple(sorted(bl.R_CAP_2K))
    rec = _power_rec(r_primary)
    _w(bl.power_path(tmp_path), {**rec, "A": dict(rec["A"], rungs=list(r_primary) + ["count_div13"])})
    with pytest.raises(ValueError, match="rungs"):
        an.load_power_2l(tmp_path, r_primary, bl.PREDICTOR_SHA_2L)


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


def test_matched_density_increment_is_thinned_minus_a256():
    """Mutation gap (Task 5, #67): the increment is thinned_B's T minus
    T_A256, not the reverse. Built on hand-synthesized bits_b/x_a64 (not
    2i's real committed draws / 2k's real committed counts, which is
    what makes test_s4_matched_2l_uses_2k_rule_and_2j_blocks slow --
    excluded from the FAST suite by name) so the sign check runs in
    milliseconds and is reachable from FAST. Named without the 's4'
    substring so `-k "not test_s4"` cannot sweep it up too."""
    strata = _strata()
    rungs = ("antonym", "add_base8")
    rng = np.random.default_rng(3)
    bits_b = {r: [[int(v) for v in rng.integers(0, 2, size=64)] for _ in range(bt.N_ITEMS)]
             for r in rungs}
    x_a64 = {r: [int(v) for v in rng.integers(0, 65, size=bt.N_ITEMS)] for r in rungs}
    x_a256 = {r: [min(256, c * 4) for c in x_a64[r]] for r in rungs}
    out = _fake_out(rungs, seed=4)
    s4 = an.s4_matched_2l(bits_b, x_a64, x_a256, out, strata, rungs)
    assert s4["thinned_B"]["T"] is not None and s4["T_A256"] is not None
    assert s4["increment"] == s4["thinned_B"]["T"] - s4["T_A256"]


def test_answer_prior_non_gating_is_a_hardcoded_literal(monkeypatch):
    """Mutation gap (Task 5, #68): non_gating is a hardcoded True (dial
    g), independent of the reading -- stub the two real computations
    (2i's real draws / _run_test's own permutation, what makes
    test_s5_answer_prior_2l_is_2j_functional_on_2i_rows slow --
    excluded from the FAST suite by name) so this runs in
    microseconds and isolates exactly the literal. Named without the
    's5' substring so `-k "not test_s5"` cannot sweep it up too."""
    monkeypatch.setattr(fn, "wrong_target_propensity", lambda rows, cap, **kw: 0.5)
    monkeypatch.setattr(an, "_run_test",
                        lambda *a, **kw: {"stratified": {"T": 0.0, "p": 1.0, "n_perm": 1, "n_ge": 1},
                                          "fires": False, "eligible": [], "per_rung": {}})
    s5 = an.s5_answer_prior_2l({"antonym": []}, {"antonym": {}}, {"antonym": {}}, {}, ("antonym",))
    assert s5["non_gating"] is True


def test_extra_rungs_2l_shape():
    strata = _strata()
    out = _fake_out(("count_div13", "reverse_string"))
    x64 = bi.sampler_counts_pythia("1b", ("count_div13", "reverse_string"))
    x_b = {r: list(x64[r]) for r in x64}
    res = an._extra_rungs_2l(x64, x_b, out, strata, r_eleven_extra=("count_div13",), r_extra=("reverse_string",))
    assert set(res["eleven_extra"]["count_div13"]) == {"stratified_d_A64", "stratified_d_B", "n_pos"}
    assert set(res["extra"]["reverse_string"]) == {"raw_d_A64", "raw_d_B", "n_pos"}


# -------------------------------------------------------------- predictors

def test_load_predictors_2l_on_the_real_trees_is_clean():
    """The happy path: both predictors, real and closed, load with
    zero failures -- the baseline every corruption case below departs
    from."""
    battery, verify = _battery(), a2d.load_verify()
    failures, ctx = an.load_predictors_2l(bi.EXP2I, bk.EXP2K, battery=battery, verify_fn=verify)
    assert failures == []
    assert set(ctx["cells_2k"]) == set(bk.SIZES_2K)
    assert ctx["x_b"] and ctx["bits_b"] and ctx["rows_2i"]


def test_load_predictors_2l_refuses_seal_literal_drift(monkeypatch):
    """Mutation gap (Task 5, #57)."""
    battery, verify = _battery(), a2d.load_verify()
    monkeypatch.setattr(bl, "SEAL_2K_SHA256", "0" * 64)
    failures, _ = an.load_predictors_2l(bi.EXP2I, bk.EXP2K, battery=battery, verify_fn=verify)
    assert any("2l predictor 2k seal sha" in f and "is not the literal" in f for f in failures)


def test_load_predictors_2l_refuses_2i_seal_literal_drift(monkeypatch):
    """Mutation gap (Task 5, #58)."""
    battery, verify = _battery(), a2d.load_verify()
    monkeypatch.setattr(bl, "SEAL_2I_SHA256", "0" * 64)
    failures, _ = an.load_predictors_2l(bi.EXP2I, bk.EXP2K, battery=battery, verify_fn=verify)
    assert any("2l predictor 2i seal sha" in f and "is not the literal" in f for f in failures)


def test_load_predictors_2l_carries_the_2k_seal_vs_rederivation_check(monkeypatch):
    """Mutation gap (Task 5, #59)."""
    battery, verify = _battery(), a2d.load_verify()
    monkeypatch.setattr(an2k, "seal_failures_2k", lambda *a, **kw: ["injected 2k seal mismatch"])
    failures, _ = an.load_predictors_2l(bi.EXP2I, bk.EXP2K, battery=battery, verify_fn=verify)
    assert any("injected 2k seal mismatch" in f for f in failures)


def test_load_predictors_2l_carries_the_2i_counts_check(monkeypatch):
    """Mutation gap (Task 5, #60)."""
    battery, verify = _battery(), a2d.load_verify()
    monkeypatch.setattr(an2i, "_check_predictor_counts_2i", lambda *a, **kw: ["injected 2i counts mismatch"])
    failures, _ = an.load_predictors_2l(bi.EXP2I, bk.EXP2K, battery=battery, verify_fn=verify)
    assert any("injected 2i counts mismatch" in f for f in failures)


def test_load_predictors_2l_refuses_a_wrong_2i_rung_set(monkeypatch):
    """Mutation gap (Task 5, #61)."""
    battery, verify = _battery(), a2d.load_verify()
    monkeypatch.setattr(an2i, "_load_rung_set", lambda root: {"R_CAP": ["antonym"]})
    failures, _ = an.load_predictors_2l(bi.EXP2I, bk.EXP2K, battery=battery, verify_fn=verify)
    assert any("2l predictor 2i rung set: R_CAP" in f for f in failures)


def test_load_predictors_2l_refuses_x_b_bits_mismatch(monkeypatch):
    """Mutation gap (Task 5, #62)."""
    battery, verify = _battery(), a2d.load_verify()
    monkeypatch.setattr(bi, "sampler_counts_olmo",
                        lambda rungs, root=None, battery=None, verify_fn=None: {r: [0] * bt.N_ITEMS for r in rungs})
    failures, _ = an.load_predictors_2l(bi.EXP2I, bk.EXP2K, battery=battery, verify_fn=verify)
    assert any("x_B bits do not reproduce the count" in f for f in failures)


def test_load_predictors_2l_refuses_a_2k_halt_marker(monkeypatch):
    """Mutation gap (Task 5, #65)."""
    battery, verify = _battery(), a2d.load_verify()
    monkeypatch.setattr(bk, "halt_markers", lambda root_2k: [Path("x/y.HALTED")])
    failures, _ = an.load_predictors_2l(bi.EXP2I, bk.EXP2K, battery=battery, verify_fn=verify)
    assert any("2l predictor 2k tier HALTED marker present" in f for f in failures)


_TOTALITY_FORCED_CASES_2L = [
    (an2i, "_load_predictor_seal_content", "2l predictor 2i seal content"),
    (an2i, "_load_rung_set", "2l predictor 2i rung set file"),
    (bi, "load_manifest", "2l predictor 2i manifest"),
    (bi, "entry_1b_endpoint", "2l predictor 2i 1B endpoint entry"),
    (an2i, "_check_predictor_seal_sampling", "2l predictor 2i seal sampling block"),
    (an2i, "_check_predictor_counts_2i", "2l predictor x_B counts vs the sealed attestation"),
    (an2k, "seal_failures_2k", "2l predictor 2k seal vs re-derivation"),
    (fn, "draw_rows_2i", "2l predictor x_B rows and bits"),
]


@pytest.mark.parametrize("mod,attr,label", _TOTALITY_FORCED_CASES_2L)
def test_load_predictors_2l_forced_exceptions_are_graceful(monkeypatch, mod, attr, label):
    """Mutation gap (Task 5, totality survivors #71/#72/#73/#76/#91/
    #92/#93/#106): every collect_total-wrapped thunk inside
    load_predictors_2l converts an exception to a graceful failure
    rather than propagating it. Exercised directly here rather than via
    test_totality_2l.py: these thunks all read the REAL, always-valid
    2k/2i predictor trees (2k and 2i are both closed), so no totality
    world -- which only corrupts the SYNTHETIC 13B tree -- can ever make
    them raise; test_totality_2l.py's own forced-exception tests only
    reach thunks downstream of that synthetic tree."""
    battery, verify = _battery(), a2d.load_verify()

    def _raise(*a, **kw):
        raise ValueError("injected for a Task 5 mutation-closure test")

    monkeypatch.setattr(mod, attr, _raise)
    failures, _ = an.load_predictors_2l(bi.EXP2I, bk.EXP2K, battery=battery, verify_fn=verify)
    assert any(label in f and "injected" in f for f in failures), (label, failures)


def test_load_predictors_2l_seal_read_forced_exception(monkeypatch):
    """Mutation gap (Task 5, totality survivor #70): bk.seal_path is
    ALSO called (unwrapped) inside an2k._seal_paths_2k right after this
    collect_total site -- a blanket mock of the function breaks that
    unwrapped call too (it doesn't call .read_text(), just needs the
    path), crashing the test itself rather than isolating the mutant.
    Scoped instead to the ONE read this label covers: Path.read_text on
    exactly 2k's seal file raises; every other read (including
    an2k._seal_paths_2k's own bare call to bk.seal_path) is untouched."""
    battery, verify = _battery(), a2d.load_verify()
    seal_file = bk.seal_path(bk.EXP2K)
    real_read_text = Path.read_text

    def _flaky_read_text(self, *a, **kw):
        if self == seal_file:
            raise ValueError("injected for a Task 5 mutation-closure test")
        return real_read_text(self, *a, **kw)

    monkeypatch.setattr(Path, "read_text", _flaky_read_text)
    failures, _ = an.load_predictors_2l(bi.EXP2I, bk.EXP2K, battery=battery, verify_fn=verify)
    assert any("2l predictor 2k seal read" in f and "injected" in f for f in failures), failures


_RUN_FORCED_CASES_2L = [
    (bg, "load_battery", "2l battery items"),
    (bg, "load_floors", "2l floors 2d"),
    (a2d, "load_verify", "2l verify criterion 3c"),
    (pr, "load_predictor", "2l strata source 2g predictor"),
    (bg, "check_frozen_imports_2g", "2l upstream 2g frozen imports"),
    (bl, "entry_13b", "2l 13B endpoint entry"),
    (bl, "entry_main_13b", "2l 13B main entry"),
]


@pytest.mark.parametrize("mod,attr,label", _RUN_FORCED_CASES_2L)
def test_run_forced_exceptions_on_the_real_tree_are_graceful(monkeypatch, mod, attr, label):
    """Mutation gap (Task 5, totality survivors #80/#81/#82/#83/#97/
    #96/#98/#99): every collect_total-wrapped thunk on the ENTRY half
    of run() -- battery/floors/verify/strata loads, the four-thunk
    upstream-pins loop, the manifest entry lookups -- must convert an
    exception to a graceful INSUFFICIENT_DATA, not propagate it.
    Exercised directly on the REAL pre-campaign tree (root_2l defaults
    to EXP2L): every totality world sets referents_sha=False and never
    reaches a complete 13B manifest, so none of these sites are
    reachable through test_totality_2l.py's synthetic-root harness --
    the real committed 13B manifest (2k's/2i's real trees too) is what
    makes them executable at all."""
    def _raise(*a, **kw):
        raise ValueError("injected for a Task 5 mutation-closure test")

    monkeypatch.setattr(mod, attr, _raise)
    v = an.run(n_perm=20, n_boot=5)
    assert v["verdict"] == "INSUFFICIENT_DATA"
    assert any(label in f and "injected" in f for f in v["referents"]["failures"]), (label, v["referents"]["failures"])


def test_run_strata_pins_forced_exception(monkeypatch):
    """Mutation gap (Task 5, totality survivor #97): sg.check_strata_pins
    is ALSO called internally by pr.load_predictor (predictor_2g.py's
    own validation) -- a blanket mock of the name breaks the EARLIER
    call site ("2l strata source 2g predictor") before run() ever
    reaches the later, explicit one this test targets. A call-counting
    mock lets the internal (first) call through and fails only run()'s
    own (second) call."""
    real = sg.check_strata_pins
    calls = {"n": 0}

    def _flaky(table):
        calls["n"] += 1
        if calls["n"] >= 2:
            raise ValueError("injected for a Task 5 mutation-closure test")
        return real(table)

    monkeypatch.setattr(sg, "check_strata_pins", _flaky)
    v = an.run(n_perm=20, n_boot=5)
    assert v["verdict"] == "INSUFFICIENT_DATA"
    assert any("2l strata pins 2g" in f and "injected" in f for f in v["referents"]["failures"])


def test_run_frozen_check_forced_exception(monkeypatch):
    """Mutation gap (Task 5, totality survivor #77): `frozen_check or
    bl.check_frozen_2l` always succeeds on the real tree (nothing
    pinned has drifted), so no totality world can make it raise --
    `frozen_check` is a test-only injection made exactly for this."""
    def _raise():
        raise ValueError("injected for a Task 5 mutation-closure test")

    v = an.run(n_perm=20, n_boot=5, frozen_check=_raise)
    assert v["verdict"] == "INSUFFICIENT_DATA"
    assert any("2l frozen modules" in f and "injected" in f for f in v["referents"]["failures"])


def test_run_import_surface_entry_forced_exception(monkeypatch):
    """Mutation gap (Task 5, totality survivor #95): the import-surface
    ENTRY check always passes on the real tree's real import graph."""
    monkeypatch.setattr(an, "check_imports_2l", lambda: (_ for _ in ()).throw(ValueError("injected")))
    v = an.run(n_perm=20, n_boot=5)
    assert v["verdict"] == "INSUFFICIENT_DATA"
    assert any("2l import surface (entry)" in f and "injected" in f for f in v["referents"]["failures"])


def test_run_referent_manifest_check_forced_exception(monkeypatch):
    """Mutation gap (Task 5, totality survivor #107): mkr.check_referents
    is only ever reached with referents_sha at its real, pinned default
    -- every totality world explicitly sets referents_sha=False (a
    synthetic root is not the real committed tree), so no totality test
    can reach this site at all."""
    monkeypatch.setattr(mkr, "check_referents", lambda *a, **kw: (_ for _ in ()).throw(ValueError("injected")))
    v = an.run(n_perm=20, n_boot=5)
    assert v["verdict"] == "INSUFFICIENT_DATA"
    assert any("2l referent manifest" in f and "injected" in f for f in v["referents"]["failures"])


def test_check_imports_2l_real_rule_flags_a_module_outside_tests(monkeypatch):
    """Mutation gap (Task 5, #66): the existing soft check just below
    (a bare try/except, deliberately non-asserting -- 'a real gap
    before Task 5, never a crash elsewhere') cannot distinguish the
    real 'tests' exclusion rule from one rewritten to swallow
    everything. This injects a synthetic sys.modules entry resolved
    under experiments/ but NOT under any tests/ directory and not
    covered by any pin -- the real rule must flag it as unpinned."""
    fake_path = str(bl.EXP2L / "PROGRESS.md")
    assert Path(fake_path).is_file()
    monkeypatch.setitem(sys.modules, "exp2l_fake_module_for_mutation_test",
                        types.SimpleNamespace(__file__=fake_path))
    with pytest.raises(RuntimeError, match="unpinned module"):
        an.check_imports_2l()


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


def test_verdict_2l_discloses_a_test_that_read_fewer_than_three_rungs():
    """FREEZE F-4: §4's THIN rule was keyed to |R_PRIMARY|, so a test
    that `cells_for` reduced to one eligible rung could fire and be
    licensed with no THIN caveat anywhere."""
    powered = {"A": {"declared_status": "POWERED"}, "B": {"declared_status": "POWERED"}}
    nine = tuple(sorted(bl.R_CAP_2K))
    A = {**_prim(0.2, 0.001, True, eligible=("add_base8",)),
         "thin": ["add3_mid", "sub3_mid", "sub4_mid"], "dropped_degenerate": []}
    t = an.verdict_2l([], A, _prim(0.02, 0.5, False), powered, nine[:4])
    assert t["verdict"] == "SHARED"
    assert an.DISCLOSURE_THIN_2L not in t["disclosures"]          # |R_PRIMARY| = 4, not < 3
    hit = [d for d in t["disclosures"]
           if d.startswith(an.DISCLOSURE_THIN_ELIGIBLE_PREFIX_2L + "A")]
    assert hit and "add_base8" in hit[0] and "sub3_mid" in hit[0]
    assert hit[0] in an._licensed_2l(t) and hit[0] in t["reason"]
    assert not any(d.startswith(an.DISCLOSURE_THIN_ELIGIBLE_PREFIX_2L + "B")
                   for d in t["disclosures"])                     # B read three
    t2 = an.verdict_2l([], _prim(0.2, 0.001, True), _prim(0.02, 0.5, False), powered, nine)
    assert not any(d.startswith(an.DISCLOSURE_THIN_ELIGIBLE_PREFIX_2L) for d in t2["disclosures"])


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
