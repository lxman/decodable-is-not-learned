# experiments/exp2m/tests/test_analyze_2m.py
"""analyze_2m: the record-failure functions on hand records (every
pinned field incl. dtype and the twin's shape), the SmolLM3 loaders on
a short synthetic tree (three whichs, the twin), outcomes over the grid
only (the twin excluded) and over the log-head subset, rung level /
first-correct / collapses / non-monotone / ceiling fraction on hand
data, the power-record loader and claims check (B on base strata), S3's
paired difference, S4/S5 on real committed rows, S8 on synthetic
committed outcomes, the 2m tree with its four worlds and disclosures,
label-prefix disjointness from 2i/2j/2k/2l, the import-surface refusal,
run() on an empty tree (INSUFFICIENT_DATA, never a raise), the referent
builder on a temp tree. No model contact."""
from __future__ import annotations

import ast
import json
import re
import sys
import types
from functools import lru_cache
from pathlib import Path

import numpy as np
import pytest

from experiments.exp2d import analyze_2d as a2d
from experiments.exp2d import battery_2d as bt
from experiments.exp2g import battery_2g as bg
from experiments.exp2g import predictor_2g as pr
from experiments.exp2g import stats_2g as st
from experiments.exp2g import strata_2g as sg
from experiments.exp2h import battery_2h as bh
from experiments.exp2i import analyze_2i as an2i
from experiments.exp2i import battery_2i as bi
from experiments.exp2j import analyze_2j as an2j
from experiments.exp2j import functionals_2j as fn
from experiments.exp2k import analyze_2k as an2k
from experiments.exp2k import battery_2k as bk
from experiments.exp2l import battery_2l as bl
from experiments.exp2m import analyze_2m as an
from experiments.exp2m import battery_2m as bm
from experiments.exp2m import make_referents_2m as mkr

SHORT_GRID = (40000, 80000, bm.ENDPOINT_STEP_2M)
SHORT_SUBSET = (40000, bm.ENDPOINT_STEP_2M)
R_SMALL = ("antonym", "antonym6")


@pytest.fixture(autouse=True)
def _frozen_pin(monkeypatch):
    monkeypatch.setattr(bm, "FROZEN_SHA256_2M", bm.frozen_from_disk(strict=False))


@lru_cache(maxsize=1)
def _manifest_raw():
    return bm.CHECKPOINTS_PATH.read_bytes()


def _manifest():
    return json.loads(_manifest_raw())


def _shrink(monkeypatch):
    monkeypatch.setattr(bm, "GRID_3B", SHORT_GRID)
    monkeypatch.setattr(bm, "LOG_HEAD_SUBSET_2M", SHORT_SUBSET)
    monkeypatch.setattr(bm, "load_manifest_3b", lambda path, sha_pin: _manifest())


@lru_cache(maxsize=1)
def _battery():
    return bg.load_battery()


@lru_cache(maxsize=1)
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


def _twin_ckpt(entry, digest="T"):
    return {"revision": bm.TWIN, "commit": None, "kind": "from_config", "files": [], "weight_sha256": digest,
            "config_source": f"{bm.REPO_CKPT}@{entry['config_commit']}",
            "tokenizer_source": f"{bm.REPO_CKPT}@{entry['config_commit']}"}


def _endpoint_rec(which, rung, k, *, entry=None):
    entry = entry or bm.entry_which_3b(_manifest(), which)
    cap = _battery()[rung]
    return bm.endpoint_item_record_2m(rung=rung, cap=cap, ev=_ev(cap, k), ckpt=_ckpt(entry), which=which,
                                      seal={"tag": bm.PREDICTOR_TAGS_2M, "sha256": bm.PREDICTOR_SHA_2M}, t_s=0.0)


def _step_rec(step, rung, k, esha="E" * 64):
    entry = bm.entry_3b(_manifest(), step)
    cap = _battery()[rung]
    ckpt = _twin_ckpt(entry) if step == bm.TWIN else _ckpt(entry)
    return bm.item_record_2m(rung=rung, cap=cap, ev=_ev(cap, k), ckpt=ckpt, step=step, endpoint_sha=esha, t_s=0.0)


# --------------------------------------------------- record failures

def test_endpoint_record_failures_2m_pins_every_field_incl_dtype():
    verify = a2d.load_verify()
    cap = _battery()["antonym"]
    entry = bm.entry_which_3b(_manifest(), "base")
    rec = _endpoint_rec("base", "antonym", 10)
    assert an.endpoint_record_failures_2m(rec, which="base", rung="antonym", cap=cap, entry=entry, verify_fn=verify) == []
    for field, value, needle in (("size", "olmo13b", "size"), ("family", "olmo2", "family"),
                                 ("which", "stage1_final", "which"), ("rung", "odd6", "rung"),
                                 ("seal_tag", bi.PREDICTOR_SEAL_TAG, "seal_tag"),
                                 ("predictor_sha", bl.PREDICTOR_SHA_2L, "predictor_sha"),
                                 ("items_sha256", "x", "items_sha256"), ("commit", "0" * 40, "commit"),
                                 ("correct", 11, "correct"), ("n", 499, "n"), ("dtype", "bfloat16", "dtype")):
        bad = an.endpoint_record_failures_2m(dict(rec, **{field: value}), which="base", rung="antonym",
                                             cap=cap, entry=entry, verify_fn=verify)
        assert any(needle in b for b in bad), (field, bad)
    r2 = dict(rec, bits=[1 - b for b in rec["bits"]], correct=bt.N_ITEMS - 10)
    bad = an.endpoint_record_failures_2m(r2, which="base", rung="antonym", cap=cap, entry=entry, verify_fn=verify)
    assert any("re-verification" in b for b in bad)
    assert all(b.startswith("endpoint smollm3_3b") for b in bad)


def test_step_record_failures_2m_pins_step_commit_endpoint_sha_and_the_twin():
    verify = a2d.load_verify()
    cap = _battery()["antonym"]
    man = _manifest()
    rec = _step_rec(40000, "antonym", 5)
    entry = bm.entry_3b(man, 40000)
    ok = an.step_record_failures_2m(rec, step=40000, rung="antonym", cap=cap, entry=entry, verify_fn=verify, endpoint_sha="E" * 64)
    assert ok == []
    assert any("endpoint_sha256" in b for b in an.step_record_failures_2m(rec, step=40000, rung="antonym", cap=cap, entry=entry, verify_fn=verify, endpoint_sha="F" * 64))
    assert any("step" in b for b in an.step_record_failures_2m(dict(rec, step=80000), step=40000, rung="antonym", cap=cap, entry=entry, verify_fn=verify, endpoint_sha="E" * 64))
    assert any("commit" in b for b in an.step_record_failures_2m(rec, step=40000, rung="antonym", cap=cap, entry=bm.entry_3b(man, 80000), verify_fn=verify, endpoint_sha="E" * 64))
    assert any("seal_tag" in b for b in an.step_record_failures_2m(dict(rec, seal_tag=bm.PREDICTOR_TAGS_2M), step=40000, rung="antonym", cap=cap, entry=entry, verify_fn=verify, endpoint_sha="E" * 64))
    assert any("dtype" in b for b in an.step_record_failures_2m(dict(rec, dtype="float32"), step=40000, rung="antonym", cap=cap, entry=entry, verify_fn=verify, endpoint_sha="E" * 64))
    tw = _step_rec(bm.TWIN, "antonym", 0)
    te = bm.entry_3b(man, bm.TWIN)
    assert an.step_record_failures_2m(tw, step=bm.TWIN, rung="antonym", cap=cap, entry=te, verify_fn=verify, endpoint_sha="E" * 64) == []
    assert any("commit" in b for b in an.step_record_failures_2m(dict(tw, commit="c" * 40), step=bm.TWIN, rung="antonym", cap=cap, entry=te, verify_fn=verify, endpoint_sha="E" * 64))
    assert any("kind" in b for b in an.step_record_failures_2m(dict(tw, kind="thin-loader"), step=bm.TWIN, rung="antonym", cap=cap, entry=te, verify_fn=verify, endpoint_sha="E" * 64))
    bad = an.step_record_failures_2m(dict(rec, step=80000), step=40000, rung="antonym", cap=cap, entry=entry, verify_fn=verify, endpoint_sha="E" * 64)
    assert all(b.startswith("smollm3_3b/step") for b in bad)


# ----------------------------------------------------------- loaders

def _tree(root, *, k_by_step=None, twin_k=0, esha="E" * 64, which_k=None):
    man = _manifest()
    battery = _battery()
    k_by_step = k_by_step or {}
    which_k = which_k or {}
    for step in bm.GRID_3B:
        entry = bm.entry_3b(man, step)
        lfs = dict(entry["lfs_sha256"])
        _w(bm.checkpoint_record_path(root, step), {"family": bm.FAMILY, "size": bm.SIZE_OUT, "step": step,
                                                   "repo": entry["repo"], "revision": entry["revision"],
                                                   "commit": entry["commit"],
                                                   "sha256": {n: lfs.get(n, f"non-lfs:{n}") for n in entry["files"]},
                                                   "loading_info": {"missing_keys": 0, "unexpected_keys": 0, "mismatched_keys": 0},
                                                   "digest": "D", "download_seconds": 0.0})
        for r in bt.RUNGS:
            _w(bm.record_path(root, step, r), _step_rec(step, r, k_by_step.get(step, 0), esha))
    te = bm.entry_3b(man, bm.TWIN)
    _w(bm.checkpoint_record_path(root, bm.TWIN),
       bm.twin_checkpoint_record_2m(info={"repo": bm.REPO_CKPT, "revision": bm.TWIN, "seed": bm.TWIN_SEED,
                                          "config_source": f"{bm.REPO_CKPT}@{te['config_commit']}", "tensor_digest": "T"}))
    for r in bt.RUNGS:
        _w(bm.record_path(root, bm.TWIN, r), _step_rec(bm.TWIN, r, twin_k, esha))
    for which in bm.ENDPOINT_WHICH_2M:
        k = k_by_step.get(bm.ENDPOINT_STEP_2M, 0) if which == "stage1_final" else which_k.get(which, 0)
        for r in bt.RUNGS:
            _w(bm.endpoint_record_path(root, which, r), _endpoint_rec(which, r, k))
    return man, battery


def test_load_endpoint_and_sweep_3b(tmp_path, monkeypatch):
    _shrink(monkeypatch)
    man, battery = _tree(tmp_path, k_by_step={40000: 2, 80000: 5, bm.ENDPOINT_STEP_2M: 9}, twin_k=1,
                         which_k={"stage3_final": 3, "base": 4})
    verify = a2d.load_verify()
    for which, want in (("stage1_final", 9), ("stage3_final", 3), ("base", 4)):
        got = an.load_endpoint_which_2m(tmp_path, which, battery, verify, entry=bm.entry_which_3b(man, which))
        assert set(got) == set(bt.RUNGS) and got["antonym"]["correct"] == want
    sweep = an.load_sweep_3b(tmp_path, battery, verify, manifest=man, endpoint_sha="E" * 64)
    assert set(sweep) == set(SHORT_GRID) | {bm.TWIN}
    assert sweep[bm.TWIN]["antonym"]["correct"] == 1
    with pytest.raises(ValueError, match="endpoint_sha256"):
        an.load_sweep_3b(tmp_path, battery, verify, manifest=man, endpoint_sha="F" * 64)
    bm.record_path(tmp_path, 80000, "odd6").unlink()
    with pytest.raises(FileNotFoundError):
        an.load_sweep_3b(tmp_path, battery, verify, manifest=man, endpoint_sha="E" * 64)
    _w(bm.record_path(tmp_path, 80000, "odd6"), _step_rec(80000, "odd6", 5))
    cp = bm.checkpoint_record_path(tmp_path, 40000)
    c = json.loads(cp.read_text())
    c["sha256"] = {k: "0" * 64 for k in c["sha256"]}
    cp.write_text(json.dumps(c))
    with pytest.raises(ValueError, match="downloaded .* sha"):
        an.load_sweep_3b(tmp_path, battery, verify, manifest=man, endpoint_sha="E" * 64)


def test_checkpoint_record_failures_2m_measure_provenance_coverage_and_the_twin():
    entry = bm.entry_3b(_manifest(), 40000)
    lfs = dict(entry["lfs_sha256"])
    assert len(entry["files"]) == 3 and len(lfs) == 2
    good = {"revision": entry["revision"], "commit": entry["commit"], "digest": "D",
            "sha256": {n: lfs.get(n, "non-lfs") for n in entry["files"]}}
    recs = {r: {"weight_sha256": "D"} for r in R_SMALL}
    assert an.checkpoint_record_failures_2m(good, step=40000, entry=entry, step_records=recs) == []
    for k in ("revision", "commit"):
        bad = an.checkpoint_record_failures_2m(dict(good, **{k: "elsewhere"}), step=40000, entry=entry, step_records=recs)
        assert any(k in b and "is not the manifest's" in b for b in bad)
    assert any("attests no sha" in b and "index.json" in b
               for b in an.checkpoint_record_failures_2m(dict(good, sha256=lfs), step=40000, entry=entry, step_records=recs))
    assert any("not a table" in b for b in an.checkpoint_record_failures_2m(dict(good, sha256=[]), step=40000, entry=entry, step_records=recs))
    assert any("tensor digest" in b and R_SMALL[0] in b
               for b in an.checkpoint_record_failures_2m(dict(good, digest="OTHER"), step=40000, entry=entry, step_records=recs))
    te = bm.entry_3b(_manifest(), bm.TWIN)
    tgood = {"revision": bm.TWIN, "commit": None, "kind": "from_config", "seed": bm.TWIN_SEED, "digest": "T",
             "config_source": f"{bm.REPO_CKPT}@{te['config_commit']}"}
    trecs = {r: {"weight_sha256": "T"} for r in R_SMALL}
    assert an.twin_checkpoint_record_failures_2m(tgood, entry=te, step_records=trecs) == []
    for mut, needle in ((dict(commit="c" * 40), "commit"), (dict(kind="thin-loader"), "kind"), (dict(seed=1), "seed"),
                        (dict(config_source="x@y"), "config_source"), (dict(digest="X"), "tensor digest")):
        bad = an.twin_checkpoint_record_failures_2m(dict(tgood, **mut), entry=te, step_records=trecs)
        assert any(needle in b for b in bad), (mut, bad)


def test_load_sweep_3b_carries_the_checkpoint_record_checks(tmp_path, monkeypatch):
    _shrink(monkeypatch)
    man, battery = _tree(tmp_path, k_by_step={40000: 2, 80000: 5, bm.ENDPOINT_STEP_2M: 9})
    verify = a2d.load_verify()
    cp = bm.checkpoint_record_path(tmp_path, 80000)
    rec = json.loads(cp.read_text())
    rec["sha256"] = {k: v for k, v in rec["sha256"].items() if not k.endswith("index.json")}
    cp.write_text(json.dumps(rec))
    with pytest.raises(ValueError, match="attests no sha"):
        an.load_sweep_3b(tmp_path, battery, verify, manifest=man, endpoint_sha="E" * 64)
    _tree(tmp_path, k_by_step={40000: 2, 80000: 5, bm.ENDPOINT_STEP_2M: 9})
    tp = bm.checkpoint_record_path(tmp_path, bm.TWIN)
    trec = json.loads(tp.read_text())
    trec["seed"] = 7
    tp.write_text(json.dumps(trec))
    with pytest.raises(ValueError, match="seed"):
        an.load_sweep_3b(tmp_path, battery, verify, manifest=man, endpoint_sha="E" * 64)


def test_outcomes_3b_excludes_the_twin_counts_grid_points_and_takes_a_subset(tmp_path, monkeypatch):
    _shrink(monkeypatch)
    man, battery = _tree(tmp_path, k_by_step={40000: 2, 80000: 5, bm.ENDPOINT_STEP_2M: 9}, twin_k=50)
    sweep = an.load_sweep_3b(tmp_path, battery, a2d.load_verify(), manifest=man, endpoint_sha="E" * 64)
    out = an.outcomes_3b(sweep, rungs=("antonym",))
    y = out["antonym"]["y"]
    assert y[0] == 3 and y[2] == 2 and y[5] == 1 and y[9] == 0 and max(y) == len(SHORT_GRID)
    assert out["antonym"]["first"][0] == 40000 and out["antonym"]["first"][5] == bm.ENDPOINT_STEP_2M
    assert out["antonym"]["n_pos"] == 9
    assert set(out["antonym"]["counts_by_step"]) == set(SHORT_GRID)          # the twin absent
    sub = an.outcomes_3b(sweep, rungs=("antonym",), steps=bm.LOG_HEAD_SUBSET_2M)
    assert max(sub["antonym"]["y"]) == len(SHORT_SUBSET) and sub["antonym"]["y"][0] == 2
    with pytest.raises(ValueError, match="grid"):
        an.outcomes_3b(sweep, rungs=("antonym",), steps=(40000, bm.TWIN))
    with pytest.raises(ValueError, match="grid"):
        an.outcomes_3b(sweep, rungs=("antonym",), steps=(40000, 120000))
    fc = an._first_correct_outcome_3b(out, ("antonym",))
    assert fc["antonym"]["y"][0] == bm.ENDPOINT_STEP_2M + 1 - 40000 and fc["antonym"]["y"][9] == 0
    rl = an.rung_level_3b(out, bg.load_floors(), rungs=("antonym",))
    assert set(rl["antonym"]) == {"s_star", "clears", "final_clears", "transient_clears"}
    cf = an.ceiling_fraction_3b(out, ("antonym",), n_steps=len(SHORT_GRID))
    assert cf["antonym"] == {"n_ceiling": 2, "fraction": 2 / bt.N_ITEMS, "n_pos": 9,
                             "fraction_of_positives": 2 / 9}


def test_collapses_and_non_monotone_on_hand_data():
    sweep = {s: {"antonym": {"correct": c, "continuations": [" 13"] * 480 + [" x"] * 20}}
             for s, c in ((40000, 0), (80000, 30), (3440000, 20))}
    for s in (80000, 3440000):
        sweep[s]["antonym"]["continuations"] = [f" {i}" for i in range(500)]
    col = an.collapses_3b(sweep, rungs=("antonym",))
    assert col == [{"rung": "antonym", "step": 40000, "continuation": " 13", "n_identical": 480, "correct": 0}]
    sweep2 = {40000: {"antonym": {"correct": 0, "continuations": [" 13"] * 450 + [f" x{i}" for i in range(50)]}}}
    assert an.collapses_3b(sweep2, rungs=("antonym",))[0]["n_identical"] == 450     # inclusive threshold
    out = {"antonym": {"counts_by_step": {40000: 0, 80000: 30, 3440000: 20}}}
    assert an.non_monotone_3b(out, ("antonym",))["antonym"] == {"drops": [[80000, 3440000, 30, 20]], "n_drops": 1, "max": 30}


# --------------------------------------------------------------- rung set

def test_rung_set_load_and_checks(tmp_path, monkeypatch):
    _shrink(monkeypatch)
    man, battery = _tree(tmp_path, k_by_step={bm.ENDPOINT_STEP_2M: 480})
    floors = bg.load_floors()
    st1 = an.load_endpoint_which_2m(tmp_path, "stage1_final", battery, a2d.load_verify(), entry=bm.entry_which_3b(man, "stage1_final"))
    rs = bm.rung_set_from_counts_2m({r: st1[r]["correct"] for r in bt.RUNGS}, floors)
    _w(bm.rung_set_path(tmp_path), {**rs, "endpoint_file_sha256": {}})
    got = an._load_rung_set_2m(tmp_path)
    assert got["R_PRIMARY"] == sorted(bm.R_CAP_2K)
    assert an._check_rung_set_vs_endpoint_2m(got, st1) == []
    assert an._check_rung_set_derivation_2m(got, st1, floors) == []
    assert any("R_PRIMARY" in b for b in an._check_rung_set_derivation_2m(dict(got, R_PRIMARY=got["R_PRIMARY"][:-1]), st1, floors))
    st1b = dict(st1, antonym=dict(st1["antonym"], correct=3))
    assert any("antonym" in b for b in an._check_rung_set_vs_endpoint_2m(got, st1b))
    _w(bm.rung_set_path(tmp_path), {**rs, "R_PRIMARY": rs["R_PRIMARY"] + ["count_div13"], "endpoint_file_sha256": {}})
    with pytest.raises(ValueError, match="subset of 2k's nine"):
        an._load_rung_set_2m(tmp_path)
    if rs["R_EXTRA"]:
        _w(bm.rung_set_path(tmp_path), {**rs, "R_EXTRA": rs["R_EXTRA"][:-1], "endpoint_file_sha256": {}})
        with pytest.raises(ValueError, match="do not partition"):
            an._load_rung_set_2m(tmp_path)
    shuffled = dict(got, R_PRIMARY=list(reversed(got["R_PRIMARY"])))
    assert any("R_PRIMARY" in b for b in an._check_rung_set_derivation_2m(shuffled, st1, floors))


def test_check_rung_set_endpoint_shas_2m_over_102(tmp_path, monkeypatch):
    _shrink(monkeypatch)
    _tree(tmp_path, k_by_step={bm.ENDPOINT_STEP_2M: 480})
    shas = {}
    for which in bm.ENDPOINT_WHICH_2M:
        for r in bt.RUNGS:
            p = bm.endpoint_record_path(tmp_path, which, r)
            shas[str(p.relative_to(tmp_path))] = bg.sha256_file(p)
    assert len(shas) == 102
    assert an._check_rung_set_endpoint_shas_2m({"endpoint_file_sha256": shas}, tmp_path) == []
    assert any("attests nothing" in b for b in an._check_rung_set_endpoint_shas_2m({"endpoint_file_sha256": {}}, tmp_path))
    one_rel = sorted(shas)[0]
    assert any(one_rel in b and "is not the committed record's" in b
               for b in an._check_rung_set_endpoint_shas_2m({"endpoint_file_sha256": {**shas, one_rel: "0" * 64}}, tmp_path))
    assert any("are not the endpoint records" in b
               for b in an._check_rung_set_endpoint_shas_2m({"endpoint_file_sha256": {**shas, "results/endpoint/stray.json": "0" * 64}}, tmp_path))
    assert any("not a table" in b for b in an._check_rung_set_endpoint_shas_2m({"endpoint_file_sha256": []}, tmp_path))
    bm.endpoint_record_path(tmp_path, "base", bt.RUNGS[0]).unlink()
    assert any("is missing" in b for b in an._check_rung_set_endpoint_shas_2m({"endpoint_file_sha256": shas}, tmp_path))
    assert len(an._endpoint_seal_paths_2m(tmp_path)) == 104


# ------------------------------------------------------------------ power

def _power_rec(r_primary, *, status="POWERED", psha=bm.PREDICTOR_SHA_2M, x256=None, x_b=None, n_pos=None):
    strata = _strata()
    x256 = x256 or bi.sampler_counts_pythia("1b", r_primary)
    x_b = x_b or x256
    dropped_a = list(an2i._degenerate_rungs(x256, strata, r_primary))
    dropped_b = list(an2i._degenerate_rungs(x_b, strata, r_primary))          # B on BASE strata
    n_pos = n_pos or {r: 100 for r in r_primary}

    def one(dropped):
        keep = [r for r in r_primary if r not in dropped]
        return {"declared_status": status, "declaration": "x", "rungs": list(r_primary),
                "n_trained_steps": bm.n_trained_3b(), "dropped_degenerate": dropped,
                "rungs_simulated": keep, "n_pos_lower_bound": n_pos, "t_bar": an.T_BAR,
                "alpha": an.ALPHA, "thin": len(keep) < 3}
    return {"A": one(dropped_a), "B": one(dropped_b),
            "block_sd_A": {"n_sim": 3, "mean_block_sd_at_declare": 0.01, "mean_block_sd_null": 0.005,
                           "per_block_mean_T_at_declare": [0.1, 0.1, 0.1, 0.1], "blocks": 4,
                           "rungs": [r for r in r_primary if r not in dropped_a]},
            "r_primary": list(r_primary),
            "primary_is_the_nine": tuple(sorted(r_primary)) == tuple(sorted(bm.R_CAP_2K)),
            "predictor_sha256": psha, "calibration_note": an.CALIBRATION_SENTENCE_2M,
            "shape_note": "x", "note": "x"}


def test_load_power_2m_and_claims_on_base_strata(tmp_path):
    r_primary = tuple(sorted(bm.R_CAP_2K))
    rec = _power_rec(r_primary)
    _w(bm.power_path(tmp_path), rec)
    got = an.load_power_2m(tmp_path, r_primary, bm.PREDICTOR_SHA_2M)
    assert got["A"]["declared_status"] == "POWERED" and got["block_sd_A"]["blocks"] == 4
    for mut, needle in ((dict(predictor_sha256="0" * 64), "predictor_sha256"),
                        ({"A": dict(rec["A"], rungs=list(r_primary)[:-1])}, "rungs"),
                        ({"A": dict(rec["A"], rungs=list(r_primary) + ["count_div13"])}, "rungs"),
                        ({"B": dict(rec["B"], n_trained_steps=16)}, "n_trained_steps"),
                        ({"A": dict(rec["A"], declared_status="MAYBE")}, "declared_status"),
                        (dict(block_sd_A=None), "block_sd_A"),
                        (dict(r_primary=list(r_primary)[:-1]), "r_primary"),
                        (dict(primary_is_the_nine=False), "primary_is_the_nine"),
                        (dict(block_sd_A=dict(rec["block_sd_A"], blocks=3)), "blocks"),
                        (dict(block_sd_A=dict(rec["block_sd_A"], per_block_mean_T_at_declare=[0.1])), "per_block_mean_T_at_declare"),
                        (dict(block_sd_A={k: v for k, v in rec["block_sd_A"].items() if k != "rungs"}), "attests no rung set")):
        _w(bm.power_path(tmp_path), {**rec, **mut})
        with pytest.raises(ValueError, match=needle):
            an.load_power_2m(tmp_path, r_primary, bm.PREDICTOR_SHA_2M)
    strata = _strata()
    x256 = bi.sampler_counts_pythia("1b", r_primary)
    stage1 = {r: {"correct": 100} for r in r_primary}
    assert an.check_power_claims_2m(rec, x256, x256, strata, r_primary, stage1) == []
    assert any("n_pos_lower_bound" in b and "A" in b for b in an.check_power_claims_2m(
        {**rec, "A": dict(rec["A"], n_pos_lower_bound={r: 0 for r in r_primary})}, x256, x256, strata, r_primary, stage1))
    assert any("rungs_simulated" in b and "B" in b for b in an.check_power_claims_2m(
        {**rec, "B": dict(rec["B"], rungs_simulated=[])}, x256, x256, strata, r_primary, stage1))
    assert any("t_bar" in b for b in an.check_power_claims_2m({**rec, "A": dict(rec["A"], t_bar=0.0)}, x256, x256, strata, r_primary, stage1))
    assert any("block_sd_A" in b and "non-degenerate set" in b for b in an.check_power_claims_2m(
        {**rec, "block_sd_A": dict(rec["block_sd_A"], rungs=list(r_primary)[:-1])}, x256, x256, strata, r_primary, stage1))
    assert an.POWER_CLAIM_FIELDS_2M == ("dropped_degenerate", "rungs_simulated", "n_pos_lower_bound", "t_bar", "alpha", "thin")


def test_check_power_claims_2m_reads_b_on_base_strata_not_a_composite():
    """B is UNCONDITIONED (dial b): its degeneracy set is computed on
    2g's base strata. A predictor degenerate on the base strata but not
    in a finer composite must be reported as dropped."""
    r_primary = ("antonym", "add_base8")
    strata = _strata()
    x256 = bi.sampler_counts_pythia("1b", r_primary)
    x_b = {"antonym": [0] * bt.N_ITEMS, "add_base8": list(x256["add_base8"])}     # constant on antonym
    rec = _power_rec(r_primary, x256=x256, x_b=x_b)
    assert rec["B"]["dropped_degenerate"] == ["antonym"]
    stage1 = {r: {"correct": 100} for r in r_primary}
    assert an.check_power_claims_2m(rec, x256, x_b, strata, r_primary, stage1) == []
    bad = an.check_power_claims_2m({**rec, "B": dict(rec["B"], dropped_degenerate=[])}, x256, x_b, strata, r_primary, stage1)
    assert any("dropped_degenerate" in b and "B" in b for b in bad)


# ------------------------------------------------------------- secondaries

def _fake_out(rungs, seed=0, n_steps=None):
    n_steps = n_steps or bm.n_trained_3b()
    rng = np.random.default_rng(seed)
    out = {}
    for r in rungs:
        y = [int(v) for v in rng.integers(0, n_steps + 1, size=bt.N_ITEMS)]
        out[r] = {"y": y, "n_pos": sum(1 for v in y if v > 0), "first": [None if v == 0 else 40000 for v in y]}
    return out


def test_s3_paired_difference_2m_shape_sign_and_ci():
    strata = _strata()
    rungs = ("antonym", "add_base8")
    rng = np.random.default_rng(5)
    out = _fake_out(rungs, seed=6)
    x_a = {r: [int(v) for v in rng.integers(0, 257, size=bt.N_ITEMS)] for r in rungs}
    x_b = {r: list(out[r]["y"]) for r in rungs}                       # B tracks the outcome exactly
    s3 = an.s3_paired_difference_2m(x_a, x_b, out, strata, rungs, n_boot=40, seed=0)
    assert s3["rungs"] == list(rungs) and s3["n_boot"] == 40
    assert s3["T_B"] > s3["T_A"] and s3["diff_B_minus_A"] == s3["T_B"] - s3["T_A"]
    assert s3["ci95"][0] <= s3["diff_B_minus_A"] <= s3["ci95"][1] and s3["ci95"][0] > 0
    da = {r: st.somers_d_within(x_a[r], out[r]["y"], strata[r]["strata"])["d"] for r in rungs}
    assert abs(s3["T_A"] - float(np.mean(list(da.values())))) < 1e-12   # the full-data T is the plain mean of within-stratum D
    same = an.s3_paired_difference_2m(x_a, x_a, out, strata, rungs, n_boot=10, seed=0)
    assert same["diff_B_minus_A"] == 0.0 and same["ci95"] == [0.0, 0.0]
    empty = an.s3_paired_difference_2m(x_a, x_b, out, strata, (), n_boot=10, seed=0)
    assert empty["T_A"] is None and empty["diff_B_minus_A"] is None and empty["ci95"] is None


def test_s4_matched_2m_uses_2k_rule_and_2j_blocks():
    strata = _strata()
    rungs = ("antonym", "add_base8")
    battery, verify = _battery(), a2d.load_verify()
    bits_b = {r: fn.verified_bits(fn.draw_rows_2i(bi.EXP2I, r), battery[r], verify) for r in rungs}
    x_a64 = bi.sampler_counts_pythia("1b", rungs)
    x_a256 = {r: [min(64 * 4, c * 4) for c in x_a64[r]] for r in rungs}
    out = _fake_out(rungs)
    s4 = an.s4_matched_2m(bits_b, x_a64, x_a256, out, strata, rungs)
    for r in rungs:
        m = bk.matched_k_256(bk.mean_rate(x_a64[r], 64), bk.mean_rate(fn.counts_from_bits(bits_b[r]), 64))
        assert s4["per_rung"][r]["k"] == m["k"] and s4["per_rung"][r]["n_blocks"] == m["n_blocks"]
    assert s4["T_A256"] == an2j.t_only(x_a256, "1b:k256", out, strata, rungs)["T"]
    assert s4["increment"] == (None if s4["thinned_B"]["T"] is None else s4["thinned_B"]["T"] - s4["T_A256"])


def test_matched_density_increment_is_thinned_minus_a256():
    strata = _strata()
    rungs = ("antonym", "add_base8")
    rng = np.random.default_rng(3)
    bits_b = {r: [[int(v) for v in rng.integers(0, 2, size=64)] for _ in range(bt.N_ITEMS)] for r in rungs}
    x_a64 = {r: [int(v) for v in rng.integers(0, 65, size=bt.N_ITEMS)] for r in rungs}
    x_a256 = {r: [min(256, c * 4) for c in x_a64[r]] for r in rungs}
    s4 = an.s4_matched_2m(bits_b, x_a64, x_a256, _fake_out(rungs, seed=4), strata, rungs)
    assert s4["increment"] == s4["thinned_B"]["T"] - s4["T_A256"]


def test_s5_answer_prior_2m_is_2j_functional_on_2i_rows():
    strata = _strata()
    rungs = ("antonym",)
    battery = _battery()
    rows = {r: fn.draw_rows_2i(bi.EXP2I, r) for r in rungs}
    s5 = an.s5_answer_prior_2m(rows, battery, _fake_out(rungs), strata, rungs, n_perm=20, n_boot=5)
    assert s5["pi"]["antonym"] == fn.wrong_target_propensity(rows["antonym"], battery["antonym"])
    assert s5["test"]["stratified"]["T"] is not None and s5["non_gating"] is True


def test_answer_prior_non_gating_is_a_hardcoded_literal(monkeypatch):
    monkeypatch.setattr(fn, "wrong_target_propensity", lambda rows, cap, **kw: 0.5)
    monkeypatch.setattr(an, "_run_test",
                        lambda *a, **kw: {"stratified": {"T": 0.0, "p": 1.0, "n_perm": 1, "n_ge": 1},
                                          "fires": False, "eligible": [], "per_rung": {}})
    assert an.s5_answer_prior_2m({"antonym": []}, {"antonym": {}}, {"antonym": {}}, {}, ("antonym",))["non_gating"] is True


def test_s8_outcome_order_2m_reads_each_committed_outcome_over_its_own_rungs():
    strata = _strata()
    r_primary = tuple(sorted(bm.R_CAP_2K))
    out_3b = _fake_out(r_primary, seed=8)
    committed = {"pythia_2.8b": {r: {"y": list(out_3b[r]["y"])} for r in ("antonym", "add_base8")},     # tracks 3B exactly
                 "olmo2_13b": _fake_out(r_primary, seed=9, n_steps=16)}                                  # independent
    s8 = an.s8_outcome_order_2m(out_3b, strata, r_primary, committed, n_perm=30, n_boot=5)
    assert set(s8) == {"pythia_2.8b", "olmo2_13b"}
    assert s8["pythia_2.8b"]["rungs"] == ["add_base8", "antonym"]
    assert s8["olmo2_13b"]["rungs"] == list(r_primary)
    assert s8["pythia_2.8b"]["test"]["stratified"]["T"] > 0.5
    assert abs(s8["olmo2_13b"]["test"]["stratified"]["T"]) < 0.15
    assert all(v["descriptive"] is True for v in s8.values())


def test_extra_rungs_2m_shape():
    strata = _strata()
    out = _fake_out(("count_div13", "reverse_string"))
    x64 = bi.sampler_counts_pythia("1b", ("count_div13", "reverse_string"))
    x_b = {r: list(x64[r]) for r in x64}
    res = an._extra_rungs_2m(x64, x_b, out, strata, r_eleven_extra=("count_div13",), r_extra=("reverse_string",))
    assert set(res["eleven_extra"]["count_div13"]) == {"stratified_d_A64", "stratified_d_B", "n_pos"}
    assert set(res["extra"]["reverse_string"]) == {"raw_d_A64", "raw_d_B", "n_pos"}


# -------------------------------------------------------------- predictors

def test_load_predictors_2m_on_the_real_trees_is_clean():
    battery, verify = _battery(), a2d.load_verify()
    failures, ctx = an.load_predictors_2m(bi.EXP2I, bk.EXP2K, battery=battery, verify_fn=verify)
    assert failures == []
    assert set(ctx["cells_2k"]) == set(bk.SIZES_2K) and ctx["x_b"] and ctx["bits_b"] and ctx["rows_2i"]


@pytest.mark.parametrize("attr,needle", [("SEAL_2K_SHA256", "2m predictor 2k seal sha"),
                                         ("SEAL_2I_SHA256", "2m predictor 2i seal sha")])
def test_load_predictors_2m_refuses_seal_literal_drift(monkeypatch, attr, needle):
    battery, verify = _battery(), a2d.load_verify()
    monkeypatch.setattr(bm, attr, "0" * 64)
    failures, _ = an.load_predictors_2m(bi.EXP2I, bk.EXP2K, battery=battery, verify_fn=verify)
    assert any(needle in f and "is not the literal" in f for f in failures)


@pytest.mark.parametrize("mod,attr,needle", [
    (an2k, "seal_failures_2k", "injected 2k seal mismatch"),
    (an2i, "_check_predictor_counts_2i", "injected 2i counts mismatch"),
])
def test_load_predictors_2m_carries_the_upstream_checks(monkeypatch, mod, attr, needle):
    battery, verify = _battery(), a2d.load_verify()
    monkeypatch.setattr(mod, attr, lambda *a, **kw: [needle])
    failures, _ = an.load_predictors_2m(bi.EXP2I, bk.EXP2K, battery=battery, verify_fn=verify)
    assert any(needle in f for f in failures)


def test_load_predictors_2m_refuses_a_wrong_2i_rung_set_x_b_mismatch_and_a_halt(monkeypatch):
    battery, verify = _battery(), a2d.load_verify()
    monkeypatch.setattr(an2i, "_load_rung_set", lambda root: {"R_CAP": ["antonym"]})
    assert any("2m predictor 2i rung set: R_CAP" in f for f in an.load_predictors_2m(bi.EXP2I, bk.EXP2K, battery=battery, verify_fn=verify)[0])
    monkeypatch.undo()
    monkeypatch.setattr(bi, "sampler_counts_olmo",
                        lambda rungs, root=None, battery=None, verify_fn=None: {r: [0] * bt.N_ITEMS for r in rungs})
    assert any("x_B bits do not reproduce the count" in f for f in an.load_predictors_2m(bi.EXP2I, bk.EXP2K, battery=battery, verify_fn=verify)[0])
    monkeypatch.undo()
    monkeypatch.setattr(bk, "halt_markers", lambda root_2k: [Path("x/y.HALTED")])
    assert any("2m predictor 2k tier HALTED marker present" in f for f in an.load_predictors_2m(bi.EXP2I, bk.EXP2K, battery=battery, verify_fn=verify)[0])


_TOTALITY_FORCED_CASES_2M = [
    (an2i, "_load_predictor_seal_content", "2m predictor 2i seal content"),
    (an2i, "_load_rung_set", "2m predictor 2i rung set file"),
    (bi, "load_manifest", "2m predictor 2i manifest"),
    (bi, "entry_1b_endpoint", "2m predictor 2i 1B endpoint entry"),
    (an2i, "_check_predictor_seal_sampling", "2m predictor 2i seal sampling block"),
    (an2i, "_check_predictor_counts_2i", "2m predictor x_B counts vs the sealed attestation"),
    (an2k, "seal_failures_2k", "2m predictor 2k seal vs re-derivation"),
    (fn, "draw_rows_2i", "2m predictor x_B rows and bits"),
]


@pytest.mark.parametrize("mod,attr,label", _TOTALITY_FORCED_CASES_2M)
def test_load_predictors_2m_forced_exceptions_are_graceful(monkeypatch, mod, attr, label):
    battery, verify = _battery(), a2d.load_verify()

    def _raise(*a, **kw):
        raise ValueError("injected for a mutation-closure test")

    monkeypatch.setattr(mod, attr, _raise)
    failures, _ = an.load_predictors_2m(bi.EXP2I, bk.EXP2K, battery=battery, verify_fn=verify)
    assert any(label in f and "injected" in f for f in failures), (label, failures)


def test_load_predictors_2m_seal_read_forced_exception(monkeypatch):
    battery, verify = _battery(), a2d.load_verify()
    seal_file = bk.seal_path(bk.EXP2K)
    real_read_text = Path.read_text

    def _flaky_read_text(self, *a, **kw):
        if self == seal_file:
            raise ValueError("injected for a mutation-closure test")
        return real_read_text(self, *a, **kw)

    monkeypatch.setattr(Path, "read_text", _flaky_read_text)
    failures, _ = an.load_predictors_2m(bi.EXP2I, bk.EXP2K, battery=battery, verify_fn=verify)
    assert any("2m predictor 2k seal read" in f and "injected" in f for f in failures), failures


_RUN_FORCED_CASES_2M = [
    (bg, "load_battery", "2m battery items"),
    (bg, "load_floors", "2m floors 2d"),
    (a2d, "load_verify", "2m verify criterion 3c"),
    (pr, "load_predictor", "2m strata source 2g predictor"),
    (bg, "check_frozen_imports_2g", "2m upstream 2g frozen imports"),
    (bm, "entry_which_3b", "2m SmolLM3 endpoint entries"),
]


@pytest.mark.parametrize("mod,attr,label", _RUN_FORCED_CASES_2M)
def test_run_forced_exceptions_on_the_real_tree_are_graceful(monkeypatch, mod, attr, label):
    def _raise(*a, **kw):
        raise ValueError("injected for a mutation-closure test")

    monkeypatch.setattr(mod, attr, _raise)
    v = an.run(n_perm=20, n_boot=5)
    assert v["verdict"] == "INSUFFICIENT_DATA"
    assert any(label in f and "injected" in f for f in v["referents"]["failures"]), (label, v["referents"]["failures"])


def test_run_strata_pins_forced_exception(monkeypatch):
    real = sg.check_strata_pins
    calls = {"n": 0}

    def _flaky(table):
        calls["n"] += 1
        if calls["n"] >= 2:
            raise ValueError("injected for a mutation-closure test")
        return real(table)

    monkeypatch.setattr(sg, "check_strata_pins", _flaky)
    v = an.run(n_perm=20, n_boot=5)
    assert v["verdict"] == "INSUFFICIENT_DATA"
    assert any("2m strata pins 2g" in f and "injected" in f for f in v["referents"]["failures"])


def test_run_frozen_check_forced_exception():
    def _raise():
        raise ValueError("injected for a mutation-closure test")

    v = an.run(n_perm=20, n_boot=5, frozen_check=_raise)
    assert v["verdict"] == "INSUFFICIENT_DATA"
    assert any("2m frozen modules" in f and "injected" in f for f in v["referents"]["failures"])


def test_run_import_surface_entry_forced_exception(monkeypatch):
    # `imports_pinned=True` is passed explicitly rather than left to the
    # default: it makes the branch under test independent of whether
    # IMPORTED_SHA256_2M happens to be pinned (it is, since Task 5), so
    # the injected exception is the only thing this case observes.
    monkeypatch.setattr(an, "check_imports_2m", lambda: (_ for _ in ()).throw(ValueError("injected")))
    v = an.run(n_perm=20, n_boot=5, imports_pinned=True)
    assert v["verdict"] == "INSUFFICIENT_DATA"
    assert any("2m import surface (entry)" in f and "injected" in f for f in v["referents"]["failures"])


def test_run_referent_manifest_check_forced_exception(monkeypatch):
    # Same reasoning as above for REFERENTS_2M_SHA256: a truthy
    # referents_sha is passed explicitly so mkr.check_referents is
    # actually called whatever the pinned literal is.
    monkeypatch.setattr(mkr, "check_referents", lambda *a, **kw: (_ for _ in ()).throw(ValueError("injected")))
    v = an.run(n_perm=20, n_boot=5, referents_sha="0" * 64)
    assert v["verdict"] == "INSUFFICIENT_DATA"
    assert any("2m referent manifest" in f and "injected" in f for f in v["referents"]["failures"])


def test_core_reads_both_tests_on_the_bare_base_strata_ast():
    """Dial b as a property of the SOURCE (mutation closure, Task 5 fix
    round 1, #88), at zero cost: inside `run()`'s nested `_core`, BOTH
    `_run_test` calls pass `strata` — the bare base strata, an
    `ast.Name` — as their fourth positional argument, never a composite
    built by a call. 2l made Test B's strata a composite; 2m's dial b
    does not, and a world test that only rules the composite OUT costs a
    full predictor load to run."""
    tree = ast.parse((an.EXP2M / "analyze_2m.py").read_text())
    run_fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "run")
    core = next(n for n in ast.walk(run_fn) if isinstance(n, ast.FunctionDef) and n.name == "_core")
    calls = [n for n in ast.walk(core)
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "_run_test"]
    assert len(calls) == 2, [ast.dump(c) for c in calls]
    for c in calls:
        arg = c.args[3]
        assert isinstance(arg, ast.Name) and arg.id == "strata", ast.dump(arg)
    labels = []
    for c in calls:
        a1 = c.args[1]
        labels.append(a1.value if isinstance(a1, ast.Constant) else
                      (a1.attr if isinstance(a1, ast.Attribute) else ast.dump(a1)))
    assert labels == ["1b:k256", "SIZE_PRED"], labels
    assert isinstance(calls[1].args[1], ast.Attribute)          # bi.SIZE_PRED, not a literal


def test_check_imports_2m_real_rule_flags_a_module_outside_tests(monkeypatch):
    fake_path = str(bm.EXP2M / "PROGRESS.md")
    assert Path(fake_path).is_file()
    monkeypatch.setitem(sys.modules, "exp2m_fake_module_for_mutation_test", types.SimpleNamespace(__file__=fake_path))
    if an.IMPORTED_SHA256_2M is None:
        monkeypatch.setattr(an, "IMPORTED_SHA256_2M", {})
    with pytest.raises(RuntimeError, match="unpinned module"):
        an.check_imports_2m()


# ------------------------------------------------------------------- tree

def _prim(T, p, fires, eligible=("a", "b", "c"), named=None):
    return {"stratified": {"T": T, "p": p, "n_perm": 10000, "n_ge": 0}, "fires": fires,
            "named_inside": named, "eligible": list(eligible), "per_rung": {}}


def test_verdict_tree_2m_names_the_four_worlds():
    for a, b, want in ((True, False, "PYTHIA-ONLY"), (False, True, "OLMO-ONLY"), (True, True, "SHARED"),
                       (False, False, "NEITHER")):
        t = an.verdict_tree_2m([], _prim(0.2 if a else 0.02, 0.001, a), _prim(0.2 if b else 0.02, 0.001, b))
        assert t["verdict"] == want and "A: T=" in t["reason"] and "B: T=" in t["reason"]
    assert an.verdict_tree_2m(["x"], None, None)["verdict"] == "INSUFFICIENT_DATA"
    t = an.verdict_tree_2m([], _prim(0.2, 0.001, True), _prim(None, 1.0, False, eligible=(), named="undefined: no eligible rung"))
    assert an.DISCLOSURE_UNDEFINED_2M["B"] in t["disclosures"] and t["verdict"] == "PYTHIA-ONLY"
    assert an.WORLDS_2M == ("INSUFFICIENT_DATA", "SHARED", "PYTHIA-ONLY", "OLMO-ONLY", "NEITHER")
    assert "PYTHIA-ONLY" in an.CALIBRATION_SENTENCE_2M and "LINEAGE" not in an.CALIBRATION_SENTENCE_2M


def test_verdict_2m_worlds_disclosures_and_licences():
    powered = {"A": {"declared_status": "POWERED"}, "B": {"declared_status": "POWERED"}}
    under_b = {"A": {"declared_status": "POWERED"}, "B": {"declared_status": "DECLARED UNDERPOWERED IN ADVANCE"}}
    nine = tuple(sorted(bm.R_CAP_2K))
    ins = an.verdict_2m(["x"], None, None, None, nine)
    assert ins["verdict"] == "INSUFFICIENT_DATA" and an._licensed_2m(ins) == an.LICENSED_2M["INSUFFICIENT_DATA"]
    for a, b, want in ((True, False, "PYTHIA-ONLY"), (False, True, "OLMO-ONLY"), (True, True, "SHARED"), (False, False, "NEITHER")):
        t = an.verdict_2m([], _prim(0.2 if a else 0.02, 0.001, a), _prim(0.2 if b else 0.02, 0.001, b), powered, nine)
        assert t["verdict"] == want and an._licensed_2m(t).startswith(an.LICENSED_2M[want])
        assert an.KNOWN_INPUTS_CAVEAT_2M in an._licensed_2m(t)
    t = an.verdict_2m([], _prim(0.2, 0.001, True), _prim(0.02, 0.5, False), under_b, nine)
    assert an.DISCLOSURE_UNDERPOWERED_2M["B"] in t["disclosures"] and an.DISCLOSURE_UNDERPOWERED_2M["A"] not in t["disclosures"]
    assert an.DISCLOSURE_UNDERPOWERED_2M["B"] in an._licensed_2m(t)
    t = an.verdict_2m([], _prim(0.2, 0.001, True), _prim(0.02, 0.5, False), powered, nine[:2])
    assert an.DISCLOSURE_THIN_2M in t["disclosures"] and t["verdict"] == "PYTHIA-ONLY"
    assert set(an.LICENSED_2M) == set(an.WORLDS_2M)


def test_verdict_2m_discloses_a_test_that_read_fewer_than_three_rungs():
    powered = {"A": {"declared_status": "POWERED"}, "B": {"declared_status": "POWERED"}}
    nine = tuple(sorted(bm.R_CAP_2K))
    A = {**_prim(0.2, 0.001, True, eligible=("add_base8",)), "thin": ["add3_mid", "sub3_mid", "sub4_mid"], "dropped_degenerate": []}
    t = an.verdict_2m([], A, _prim(0.02, 0.5, False), powered, nine[:4])
    assert t["verdict"] == "PYTHIA-ONLY" and an.DISCLOSURE_THIN_2M not in t["disclosures"]
    hit = [d for d in t["disclosures"] if d.startswith(an.DISCLOSURE_THIN_ELIGIBLE_PREFIX_2M + "A")]
    assert hit and "add_base8" in hit[0] and hit[0] in an._licensed_2m(t) and hit[0] in t["reason"]
    assert not any(d.startswith(an.DISCLOSURE_THIN_ELIGIBLE_PREFIX_2M + "B") for d in t["disclosures"])


def test_which_coherence_failures_2m():
    """Freeze F-2: a `which` has no checkpoint record, so nothing
    measured that its 34 records came from ONE load."""
    recs = {r: {"weight_sha256": "D", "commit": "c" * 40, "config_source": "repo@c"}
            for r in bm.bt.RUNGS}
    assert an.which_coherence_failures_2m("stage1_final", recs) == []
    for field, label in (("weight_sha256", "tensor digest"), ("commit", "commit"),
                         ("config_source", "config source")):
        mixed = {r: dict(v) for r, v in recs.items()}
        mixed["odd6"][field] = "OTHER"
        bad = an.which_coherence_failures_2m("base", mixed)
        assert bad and f"2 different {label}s" in bad[0] and bad[0].startswith("endpoint smollm3_3b base")
    empty = {r: {"weight_sha256": None, "commit": "c" * 40, "config_source": "repo@c"}
             for r in bm.bt.RUNGS}
    assert any("empty" in b for b in an.which_coherence_failures_2m("stage3_final", empty))


def test_verdict_2m_discloses_a_reading_narrower_than_r_primary():
    """Freeze F-1: 3 <= |eligible| < |R_PRIMARY| carried no disclosure —
    2l F-4's guard speaks only below three. The two are mutually
    exclusive and both ride on the licence."""
    powered = {"A": {"declared_status": "POWERED"}, "B": {"declared_status": "POWERED"}}
    nine = tuple(sorted(bm.R_CAP_2K))
    eight = tuple(r for r in nine if r != "add3_mid")
    A = {**_prim(0.2, 0.001, True, eligible=eight), "thin": ["add3_mid"], "dropped_degenerate": []}
    B = {**_prim(0.02, 0.5, False, eligible=eight), "thin": ["add3_mid"], "dropped_degenerate": []}
    t = an.verdict_2m([], A, B, powered, nine)
    assert t["verdict"] == "PYTHIA-ONLY"
    assert not any(d.startswith(an.DISCLOSURE_THIN_ELIGIBLE_PREFIX_2M) for d in t["disclosures"])
    for test in ("A", "B"):
        hit = [d for d in t["disclosures"]
               if d.startswith(an.DISCLOSURE_PARTIAL_ELIGIBLE_PREFIX_2M + test)]
        assert hit and "add3_mid" in hit[0] and hit[0] in an._licensed_2m(t) and hit[0] in t["reason"]
    # the full reading discloses nothing; a sub-three reading takes 2l F-4's
    # wording and NOT this one (mutual exclusion)
    full = {**_prim(0.2, 0.001, True, eligible=nine), "thin": [], "dropped_degenerate": []}
    t_full = an.verdict_2m([], full, full, powered, nine)
    assert t_full["disclosures"] == []
    two = {**_prim(0.2, 0.001, True, eligible=nine[:2]), "thin": list(nine[2:]), "dropped_degenerate": []}
    t_two = an.verdict_2m([], two, two, powered, nine)
    assert all(d.startswith(an.DISCLOSURE_THIN_ELIGIBLE_PREFIX_2M) for d in t_two["disclosures"])
    assert an._partial_eligible_2m("A", two, nine) is None
    assert an._partial_eligible_2m("A", full, nine) is None


def _all_failure_labels(path):
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


def test_failure_labels_disjoint_from_2i_2j_2k_2l():
    mine = set(_all_failure_labels(bm.EXP2M / "analyze_2m.py"))
    assert mine and all(lab.startswith("2m") for lab in mine)
    for other in (bi.EXP2I / "analyze_2i.py", bg.REPO / "experiments/exp2j/analyze_2j.py",
                  bk.EXP2K / "analyze_2k.py", bl.EXP2L / "analyze_2l.py"):
        theirs = set(_all_failure_labels(other))
        for a in mine:
            for b in theirs:
                assert not a.startswith(b) and not b.startswith(a), (a, b)


def test_check_imports_2m_refuses_unpinned_and_covers_upstream(monkeypatch):
    monkeypatch.setattr(an, "IMPORTED_SHA256_2M", None)
    with pytest.raises(RuntimeError, match="not pinned"):
        an.check_imports_2m()
    monkeypatch.setattr(an, "IMPORTED_SHA256_2M", {})
    try:
        an.check_imports_2m()
    except RuntimeError as e:
        assert str(e).startswith("unpinned module")


def test_run_on_empty_tree_is_insufficient_never_raises(tmp_path):
    v = an.run(root_2m=tmp_path, root_2i=bi.EXP2I, root_2k=bk.EXP2K, n_perm=20, n_boot=5,
               referents_sha=False, imports_pinned=False, tag_exists=lambda t: True,
               blob_sha=lambda tag, rel: bg.sha256_file(bm.REPO / rel) if (bm.REPO / rel).is_file() else None,
               blobs_bound=lambda tag, paths, repo_root=None: [])
    assert v["verdict"] == "INSUFFICIENT_DATA" and v["tests"] is None and v["secondaries"] is None
    assert any("2m endpoint stage1_final" in f or "2m rung set" in f for f in v["referents"]["failures"])
    assert v["referents"]["pins_active"] == {"frozen_modules": True, "import_surface": False, "referent_manifest": False}
    assert v["known_inputs_caveat"] == an.KNOWN_INPUTS_CAVEAT_2M and v["model_contact"] == "none at analysis"
    assert v["calibration_note"] == an.CALIBRATION_SENTENCE_2M


# -------------------------------------------------------------- referents

def test_make_referents_2m_lists_2l_campaign_artifacts_and_2m_inputs(tmp_path, monkeypatch):
    files = mkr.referent_files()
    rel = {str(p.relative_to(bm.REPO)) for p in files}
    assert "experiments/exp2k/results/predictor_2k.json" in rel
    assert "experiments/exp2i/results/predictor/olmo1b/antonym.draws.jsonl.gz" in rel
    assert "experiments/exp2l/results/verdict.json" in rel
    assert "experiments/exp2l/results/endpoint/rung_set_2l.json" in rel
    assert "experiments/exp2l/results/endpoint/stage1_final/antonym.json" in rel
    assert "experiments/exp2l/results/sweep/olmo13b/step596057/antonym.json" in rel
    assert "experiments/exp2l/results/sweep/olmo13b/gate1.json" in rel
    for r in bl.INSTRUMENT_BLOBS_2L:
        assert r in rel
    assert "experiments/exp2m/checkpoints_2m.json" in rel and "experiments/exp2m/hub_inventory_smollm3.json" in rel
    assert "experiments/exp2m/power_2m.py" in rel
    assert len(files) == len(set(files))
    monkeypatch.setattr(mkr, "N_FILES_2M", None)
    p = tmp_path / "r.json"
    rec = mkr.build(p, n_files=len(files))
    assert rec["n_files"] == len(files)
    monkeypatch.setattr(mkr, "N_FILES_2M", len(files))
    assert mkr.check_referents(p, sha_pin=bg.sha256_file(p)) == []
    with pytest.raises(ValueError, match="hashes to"):
        mkr.check_referents(p, sha_pin="0" * 64)
