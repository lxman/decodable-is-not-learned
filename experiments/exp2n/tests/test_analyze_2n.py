# experiments/exp2n/tests/test_analyze_2n.py
"""analyze_2n: the record-failure functions on hand records (every
pinned field incl. dtype/render/eos_stop_id and the twin's shape, plus
the checkpoint record's generation_eos_token_id pin), the Comma loaders
on a short synthetic tree (three whichs, the twin), outcomes over the
grid only (the twin excluded) and over the every-40k subset, rung level
/ first-correct / collapses / non-monotone / ceiling fraction on hand
data, the power-record loader and claims check (B on base strata), S3's
paired difference, the generalised `paired_contrast_2n`, S4/S5 on real
committed rows, the thinned predictor and the annotation C's CI rule
and `covers_3b_increment`, S8 on synthetic committed outcomes (five
keys), S8c's Pile-vs-DCLM-class contrast, S9's sign ledger against the
committed literals and verdict.json readings, the 2n tree with its four
worlds, disclosures and the annotation carried in the reason, label-
prefix disjointness from 2i/2j/2k/2l/2m, the import-surface refusal,
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
from experiments.exp2l import analyze_2l as an2l
from experiments.exp2l import battery_2l as bl
from experiments.exp2m import analyze_2m as an2m
from experiments.exp2m import battery_2m as bm
from experiments.exp2n import analyze_2n as an
from experiments.exp2n import battery_2n as bn
from experiments.exp2n import make_referents_2n as mkr

SHORT_GRID = (10000, 20000, bn.ENDPOINT_STEP_2N)
SHORT_SUBSET = (20000, bn.ENDPOINT_STEP_2N)
R_SMALL = ("antonym", "antonym6")


@pytest.fixture(autouse=True)
def _frozen_pin(monkeypatch):
    monkeypatch.setattr(bn, "FROZEN_SHA256_2N", bn.frozen_from_disk(strict=False))


@lru_cache(maxsize=1)
def _manifest_raw():
    return bn.CHECKPOINTS_PATH.read_bytes()


def _manifest():
    return json.loads(_manifest_raw())


def _shrink(monkeypatch):
    monkeypatch.setattr(bn, "GRID_COMMA", SHORT_GRID)
    monkeypatch.setattr(bn, "EVERY40K_SUBSET_2N", SHORT_SUBSET)
    monkeypatch.setattr(bn, "load_manifest_comma", lambda path, sha_pin: _manifest())


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
    return {"revision": bn.TWIN, "commit": None, "kind": "from_config", "files": [], "weight_sha256": digest,
            "config_source": f"{bn.REPO_COMMA}@{entry['config_commit']}",
            "tokenizer_source": f"{bn.REPO_COMMA}@{entry['config_commit']}"}


def _endpoint_rec(which, rung, k, *, entry=None):
    entry = entry or bn.entry_which_comma(_manifest(), which)
    cap = _battery()[rung]
    return bn.endpoint_item_record_2n(rung=rung, cap=cap, ev=_ev(cap, k), ckpt=_ckpt(entry), which=which,
                                      seal={"tag": bn.PREDICTOR_TAGS_2N, "sha256": bn.PREDICTOR_SHA_2N}, t_s=0.0)


def _step_rec(step, rung, k, esha="E" * 64):
    entry = bn.entry_comma(_manifest(), step)
    cap = _battery()[rung]
    ckpt = _twin_ckpt(entry) if step == bn.TWIN else _ckpt(entry)
    return bn.item_record_2n(rung=rung, cap=cap, ev=_ev(cap, k), ckpt=ckpt, step=step, endpoint_sha=esha, t_s=0.0)


# --------------------------------------------------- record failures

def test_endpoint_record_failures_2n_pins_every_field_incl_dtype():
    verify = a2d.load_verify()
    cap = _battery()["antonym"]
    entry = bn.entry_which_comma(_manifest(), "main")
    rec = _endpoint_rec("main", "antonym", 10)
    assert an.endpoint_record_failures_2n(rec, which="main", rung="antonym", cap=cap, entry=entry, verify_fn=verify) == []
    for field, value, needle in (("size", "olmo13b", "size"), ("family", "olmo2", "family"),
                                 ("which", "stage1_final", "which"), ("rung", "odd6", "rung"),
                                 ("seal_tag", bi.PREDICTOR_SEAL_TAG, "seal_tag"),
                                 ("predictor_sha", bm.PREDICTOR_SHA_2M, "predictor_sha"),
                                 ("items_sha256", "x", "items_sha256"), ("commit", "0" * 40, "commit"),
                                 ("correct", 11, "correct"), ("n", 499, "n"), ("dtype", "bfloat16", "dtype"),
                                 ("render", "plain", "render"), ("eos_stop_id", 2, "eos_stop_id")):
        bad = an.endpoint_record_failures_2n(dict(rec, **{field: value}), which="main", rung="antonym",
                                             cap=cap, entry=entry, verify_fn=verify)
        assert any(needle in b for b in bad), (field, bad)
    r2 = dict(rec, bits=[1 - b for b in rec["bits"]], correct=bt.N_ITEMS - 10)
    bad = an.endpoint_record_failures_2n(r2, which="main", rung="antonym", cap=cap, entry=entry, verify_fn=verify)
    assert any("re-verification" in b for b in bad)
    assert all(b.startswith("endpoint comma_7b") for b in bad)


def test_step_record_failures_2n_pins_step_commit_endpoint_sha_and_the_twin():
    verify = a2d.load_verify()
    cap = _battery()["antonym"]
    man = _manifest()
    rec = _step_rec(40000, "antonym", 5)
    entry = bn.entry_comma(man, 40000)
    ok = an.step_record_failures_2n(rec, step=40000, rung="antonym", cap=cap, entry=entry, verify_fn=verify, endpoint_sha="E" * 64)
    assert ok == []
    assert any("endpoint_sha256" in b for b in an.step_record_failures_2n(rec, step=40000, rung="antonym", cap=cap, entry=entry, verify_fn=verify, endpoint_sha="F" * 64))
    assert any("step" in b for b in an.step_record_failures_2n(dict(rec, step=80000), step=40000, rung="antonym", cap=cap, entry=entry, verify_fn=verify, endpoint_sha="E" * 64))
    assert any("commit" in b for b in an.step_record_failures_2n(rec, step=40000, rung="antonym", cap=cap, entry=bn.entry_comma(man, 80000), verify_fn=verify, endpoint_sha="E" * 64))
    assert any("seal_tag" in b for b in an.step_record_failures_2n(dict(rec, seal_tag=bn.PREDICTOR_TAGS_2N), step=40000, rung="antonym", cap=cap, entry=entry, verify_fn=verify, endpoint_sha="E" * 64))
    assert any("dtype" in b for b in an.step_record_failures_2n(dict(rec, dtype="float32"), step=40000, rung="antonym", cap=cap, entry=entry, verify_fn=verify, endpoint_sha="E" * 64))
    assert any("render" in b for b in an.step_record_failures_2n(dict(rec, render="plain"), step=40000, rung="antonym", cap=cap, entry=entry, verify_fn=verify, endpoint_sha="E" * 64))
    assert any("eos_stop_id" in b for b in an.step_record_failures_2n(dict(rec, eos_stop_id=2), step=40000, rung="antonym", cap=cap, entry=entry, verify_fn=verify, endpoint_sha="E" * 64))
    tw = _step_rec(bn.TWIN, "antonym", 0)
    te = bn.entry_comma(man, bn.TWIN)
    assert an.step_record_failures_2n(tw, step=bn.TWIN, rung="antonym", cap=cap, entry=te, verify_fn=verify, endpoint_sha="E" * 64) == []
    assert any("commit" in b for b in an.step_record_failures_2n(dict(tw, commit="c" * 40), step=bn.TWIN, rung="antonym", cap=cap, entry=te, verify_fn=verify, endpoint_sha="E" * 64))
    assert any("kind" in b for b in an.step_record_failures_2n(dict(tw, kind="thin-loader"), step=bn.TWIN, rung="antonym", cap=cap, entry=te, verify_fn=verify, endpoint_sha="E" * 64))
    assert any("render" in b for b in an.step_record_failures_2n(dict(tw, render="plain"), step=bn.TWIN, rung="antonym", cap=cap, entry=te, verify_fn=verify, endpoint_sha="E" * 64))
    assert any("eos_stop_id" in b for b in an.step_record_failures_2n(dict(tw, eos_stop_id=2), step=bn.TWIN, rung="antonym", cap=cap, entry=te, verify_fn=verify, endpoint_sha="E" * 64))
    bad = an.step_record_failures_2n(dict(rec, step=80000), step=40000, rung="antonym", cap=cap, entry=entry, verify_fn=verify, endpoint_sha="E" * 64)
    assert all(b.startswith("comma_7b/step") for b in bad)


def test_checkpoint_record_failures_2n_pin_the_generation_eos():
    entry = bn.entry_comma(_manifest(), 20000)
    lfs = dict(entry["lfs_sha256"])
    good = {"revision": entry["revision"], "commit": entry["commit"], "digest": "D",
            "sha256": {n: lfs.get(n, "non-lfs") for n in entry["files"]},
            "config_eos_token_id": 2, "generation_eos_token_id": 3}
    recs = {r: {"weight_sha256": "D"} for r in R_SMALL}
    assert an.checkpoint_record_failures_2n(good, step=20000, entry=entry, step_records=recs) == []
    bad = an.checkpoint_record_failures_2n(dict(good, generation_eos_token_id=2), step=20000, entry=entry, step_records=recs)
    assert any("generation_eos_token_id" in b and "3" in b for b in bad)
    bad = an.checkpoint_record_failures_2n({k: v for k, v in good.items() if k != "generation_eos_token_id"}, step=20000, entry=entry, step_records=recs)
    assert any("generation_eos_token_id" in b for b in bad)
    te = bn.entry_comma(_manifest(), bn.TWIN)
    tgood = {"revision": bn.TWIN, "commit": None, "kind": "from_config", "seed": bn.TWIN_SEED, "digest": "T",
             "config_source": f"{bn.REPO_COMMA}@{te['config_commit']}", "generation_eos_token_id": 3}
    trecs = {r: {"weight_sha256": "T"} for r in R_SMALL}
    assert an.twin_checkpoint_record_failures_2n(tgood, entry=te, step_records=trecs) == []
    assert any("generation_eos_token_id" in b for b in an.twin_checkpoint_record_failures_2n(dict(tgood, generation_eos_token_id=2), entry=te, step_records=trecs))


def test_checkpoint_record_failures_2n_measure_provenance_coverage_and_the_twin():
    entry = bn.entry_comma(_manifest(), 40000)
    lfs = dict(entry["lfs_sha256"])
    assert len(entry["files"]) == 4 and len(lfs) == 3
    good = {"revision": entry["revision"], "commit": entry["commit"], "digest": "D",
            "sha256": {n: lfs.get(n, "non-lfs") for n in entry["files"]},
            "generation_eos_token_id": bn.EOS_STOP_ID_2N}
    recs = {r: {"weight_sha256": "D"} for r in R_SMALL}
    assert an.checkpoint_record_failures_2n(good, step=40000, entry=entry, step_records=recs) == []
    for k in ("revision", "commit"):
        bad = an.checkpoint_record_failures_2n(dict(good, **{k: "elsewhere"}), step=40000, entry=entry, step_records=recs)
        assert any(k in b and "is not the manifest's" in b for b in bad)
    assert any("attests no sha" in b and "index.json" in b
               for b in an.checkpoint_record_failures_2n(dict(good, sha256=lfs), step=40000, entry=entry, step_records=recs))
    assert any("not a table" in b for b in an.checkpoint_record_failures_2n(dict(good, sha256=[]), step=40000, entry=entry, step_records=recs))
    assert any("tensor digest" in b and R_SMALL[0] in b
               for b in an.checkpoint_record_failures_2n(dict(good, digest="OTHER"), step=40000, entry=entry, step_records=recs))
    te = bn.entry_comma(_manifest(), bn.TWIN)
    tgood = {"revision": bn.TWIN, "commit": None, "kind": "from_config", "seed": bn.TWIN_SEED, "digest": "T",
             "config_source": f"{bn.REPO_COMMA}@{te['config_commit']}", "generation_eos_token_id": bn.EOS_STOP_ID_2N}
    trecs = {r: {"weight_sha256": "T"} for r in R_SMALL}
    assert an.twin_checkpoint_record_failures_2n(tgood, entry=te, step_records=trecs) == []
    for mut, needle in ((dict(commit="c" * 40), "commit"), (dict(kind="thin-loader"), "kind"), (dict(seed=1), "seed"),
                        (dict(config_source="x@y"), "config_source"), (dict(digest="X"), "tensor digest")):
        bad = an.twin_checkpoint_record_failures_2n(dict(tgood, **mut), entry=te, step_records=trecs)
        assert any(needle in b for b in bad), (mut, bad)


# ----------------------------------------------------------- loaders

def _tree(root, *, k_by_step=None, twin_k=0, esha="E" * 64, which_k=None):
    man = _manifest()
    battery = _battery()
    k_by_step = k_by_step or {}
    which_k = which_k or {}
    for step in bn.GRID_COMMA:
        entry = bn.entry_comma(man, step)
        lfs = dict(entry["lfs_sha256"])
        _w(bn.checkpoint_record_path(root, step), {"family": bn.FAMILY, "size": bn.SIZE_OUT, "step": step,
                                                   "repo": entry["repo"], "revision": entry["revision"],
                                                   "commit": entry["commit"],
                                                   "sha256": {n: lfs.get(n, f"non-lfs:{n}") for n in entry["files"]},
                                                   "loading_info": {"missing_keys": 0, "unexpected_keys": 0, "mismatched_keys": 0},
                                                   "digest": "D", "download_seconds": 0.0,
                                                   "config_eos_token_id": 2, "generation_eos_token_id": 3})
        for r in bt.RUNGS:
            _w(bn.record_path(root, step, r), _step_rec(step, r, k_by_step.get(step, 0), esha))
    te = bn.entry_comma(man, bn.TWIN)
    _w(bn.checkpoint_record_path(root, bn.TWIN),
       bn.twin_checkpoint_record_2n(info={"repo": bn.REPO_COMMA, "revision": bn.TWIN, "seed": bn.TWIN_SEED,
                                          "config_source": f"{bn.REPO_COMMA}@{te['config_commit']}", "tensor_digest": "T",
                                          "config_eos_token_id": 2, "generation_eos_token_id": 3}))
    for r in bt.RUNGS:
        _w(bn.record_path(root, bn.TWIN, r), _step_rec(bn.TWIN, r, twin_k, esha))
    for which in bn.ENDPOINT_WHICH_2N:
        k = k_by_step.get(bn.ENDPOINT_STEP_2N, 0) if which == "stage1_final" else which_k.get(which, 0)
        for r in bt.RUNGS:
            _w(bn.endpoint_record_path(root, which, r), _endpoint_rec(which, r, k))
    return man, battery


def test_load_endpoint_and_sweep_comma(tmp_path, monkeypatch):
    _shrink(monkeypatch)
    man, battery = _tree(tmp_path, k_by_step={10000: 2, 20000: 5, bn.ENDPOINT_STEP_2N: 9}, twin_k=1,
                         which_k={"stage2_final": 3, "main": 4})
    verify = a2d.load_verify()
    for which, want in (("stage1_final", 9), ("stage2_final", 3), ("main", 4)):
        got = an.load_endpoint_which_2n(tmp_path, which, battery, verify, entry=bn.entry_which_comma(man, which))
        assert set(got) == set(bt.RUNGS) and got["antonym"]["correct"] == want
    # Freeze F-2: the which-coherence check is applied BY the loader, not
    # merely available beside it — one record from a second load refuses.
    p_odd = bn.endpoint_record_path(tmp_path, "main", "odd6")
    orig = p_odd.read_text()
    rec_odd = json.loads(orig)
    rec_odd["weight_sha256"] = "OTHER"
    p_odd.write_text(json.dumps(rec_odd))
    with pytest.raises(ValueError, match="did not come from one load"):
        an.load_endpoint_which_2n(tmp_path, "main", battery, verify, entry=bn.entry_which_comma(man, "main"))
    p_odd.write_text(orig)
    sweep = an.load_sweep_comma(tmp_path, battery, verify, manifest=man, endpoint_sha="E" * 64)
    assert set(sweep) == set(SHORT_GRID) | {bn.TWIN}
    assert sweep[bn.TWIN]["antonym"]["correct"] == 1
    with pytest.raises(ValueError, match="endpoint_sha256"):
        an.load_sweep_comma(tmp_path, battery, verify, manifest=man, endpoint_sha="F" * 64)
    bn.record_path(tmp_path, 20000, "odd6").unlink()
    with pytest.raises(FileNotFoundError):
        an.load_sweep_comma(tmp_path, battery, verify, manifest=man, endpoint_sha="E" * 64)
    _w(bn.record_path(tmp_path, 20000, "odd6"), _step_rec(20000, "odd6", 5))
    cp = bn.checkpoint_record_path(tmp_path, 10000)
    c = json.loads(cp.read_text())
    c["sha256"] = {k: "0" * 64 for k in c["sha256"]}
    cp.write_text(json.dumps(c))
    with pytest.raises(ValueError, match="downloaded .* sha"):
        an.load_sweep_comma(tmp_path, battery, verify, manifest=man, endpoint_sha="E" * 64)


def test_load_sweep_comma_carries_the_checkpoint_record_checks(tmp_path, monkeypatch):
    _shrink(monkeypatch)
    man, battery = _tree(tmp_path, k_by_step={10000: 2, 20000: 5, bn.ENDPOINT_STEP_2N: 9})
    verify = a2d.load_verify()
    cp = bn.checkpoint_record_path(tmp_path, 20000)
    rec = json.loads(cp.read_text())
    rec["sha256"] = {k: v for k, v in rec["sha256"].items() if not k.endswith("index.json")}
    cp.write_text(json.dumps(rec))
    with pytest.raises(ValueError, match="attests no sha"):
        an.load_sweep_comma(tmp_path, battery, verify, manifest=man, endpoint_sha="E" * 64)
    _tree(tmp_path, k_by_step={10000: 2, 20000: 5, bn.ENDPOINT_STEP_2N: 9})
    tp = bn.checkpoint_record_path(tmp_path, bn.TWIN)
    trec = json.loads(tp.read_text())
    trec["seed"] = 7
    tp.write_text(json.dumps(trec))
    with pytest.raises(ValueError, match="seed"):
        an.load_sweep_comma(tmp_path, battery, verify, manifest=man, endpoint_sha="E" * 64)


def test_outcomes_comma_excludes_the_twin_counts_grid_points_and_takes_a_subset(tmp_path, monkeypatch):
    _shrink(monkeypatch)
    man, battery = _tree(tmp_path, k_by_step={10000: 2, 20000: 5, bn.ENDPOINT_STEP_2N: 9}, twin_k=50)
    sweep = an.load_sweep_comma(tmp_path, battery, a2d.load_verify(), manifest=man, endpoint_sha="E" * 64)
    out = an.outcomes_comma(sweep, rungs=("antonym",))
    y = out["antonym"]["y"]
    assert y[0] == 3 and y[2] == 2 and y[5] == 1 and y[9] == 0 and max(y) == len(SHORT_GRID)
    assert out["antonym"]["first"][0] == 10000 and out["antonym"]["first"][5] == bn.ENDPOINT_STEP_2N
    assert out["antonym"]["n_pos"] == 9
    assert set(out["antonym"]["counts_by_step"]) == set(SHORT_GRID)          # the twin absent
    sub = an.outcomes_comma(sweep, rungs=("antonym",), steps=bn.EVERY40K_SUBSET_2N)
    assert max(sub["antonym"]["y"]) == len(SHORT_SUBSET) and sub["antonym"]["y"][0] == 2
    with pytest.raises(ValueError, match="grid"):
        an.outcomes_comma(sweep, rungs=("antonym",), steps=(10000, bn.TWIN))
    with pytest.raises(ValueError, match="grid"):
        an.outcomes_comma(sweep, rungs=("antonym",), steps=(10000, 120000))
    fc = an._first_correct_outcome_comma(out, ("antonym",))
    assert fc["antonym"]["y"][0] == bn.ENDPOINT_STEP_2N + 1 - 10000 and fc["antonym"]["y"][9] == 0
    rl = an.rung_level_comma(out, bg.load_floors(), rungs=("antonym",))
    assert set(rl["antonym"]) == {"s_star", "clears", "final_clears", "transient_clears"}
    cf = an.ceiling_fraction_comma(out, ("antonym",), n_steps=len(SHORT_GRID))
    assert cf["antonym"] == {"n_ceiling": 2, "fraction": 2 / bt.N_ITEMS, "n_pos": 9,
                             "fraction_of_positives": 2 / 9}


def test_collapses_and_non_monotone_on_hand_data():
    sweep = {s: {"antonym": {"correct": c, "continuations": [" 13"] * 480 + [" x"] * 20}}
             for s, c in ((40000, 0), (80000, 30), (460000, 20))}
    for s in (80000, 460000):
        sweep[s]["antonym"]["continuations"] = [f" {i}" for i in range(500)]
    col = an.collapses_comma(sweep, rungs=("antonym",))
    assert col == [{"rung": "antonym", "step": 40000, "continuation": " 13", "n_identical": 480, "correct": 0}]
    sweep2 = {40000: {"antonym": {"correct": 0, "continuations": [" 13"] * 450 + [f" x{i}" for i in range(50)]}}}
    assert an.collapses_comma(sweep2, rungs=("antonym",))[0]["n_identical"] == 450     # inclusive threshold
    out = {"antonym": {"counts_by_step": {40000: 0, 80000: 30, 460000: 20}}}
    assert an.non_monotone_comma(out, ("antonym",))["antonym"] == {"drops": [[80000, 460000, 30, 20]], "n_drops": 1, "max": 30}


# --------------------------------------------------------------- rung set

def test_rung_set_load_and_checks(tmp_path, monkeypatch):
    _shrink(monkeypatch)
    man, battery = _tree(tmp_path, k_by_step={bn.ENDPOINT_STEP_2N: 480})
    floors = bg.load_floors()
    st1 = an.load_endpoint_which_2n(tmp_path, "stage1_final", battery, a2d.load_verify(), entry=bn.entry_which_comma(man, "stage1_final"))
    rs = bn.rung_set_from_counts_2n({r: st1[r]["correct"] for r in bt.RUNGS}, floors)
    _w(bn.rung_set_path(tmp_path), {**rs, "endpoint_file_sha256": {}})
    got = an._load_rung_set_2n(tmp_path)
    assert got["R_PRIMARY"] == sorted(bn.R_CAP_2K)
    assert an._check_rung_set_vs_endpoint_2n(got, st1) == []
    assert an._check_rung_set_derivation_2n(got, st1, floors) == []
    assert any("R_PRIMARY" in b for b in an._check_rung_set_derivation_2n(dict(got, R_PRIMARY=got["R_PRIMARY"][:-1]), st1, floors))
    st1b = dict(st1, antonym=dict(st1["antonym"], correct=3))
    assert any("antonym" in b for b in an._check_rung_set_vs_endpoint_2n(got, st1b))
    _w(bn.rung_set_path(tmp_path), {**rs, "R_PRIMARY": rs["R_PRIMARY"] + ["count_div13"], "endpoint_file_sha256": {}})
    with pytest.raises(ValueError, match="subset of 2k's nine"):
        an._load_rung_set_2n(tmp_path)
    if rs["R_EXTRA"]:
        _w(bn.rung_set_path(tmp_path), {**rs, "R_EXTRA": rs["R_EXTRA"][:-1], "endpoint_file_sha256": {}})
        with pytest.raises(ValueError, match="do not partition"):
            an._load_rung_set_2n(tmp_path)
    shuffled = dict(got, R_PRIMARY=list(reversed(got["R_PRIMARY"])))
    assert any("R_PRIMARY" in b for b in an._check_rung_set_derivation_2n(shuffled, st1, floors))


def test_check_rung_set_endpoint_shas_2n_over_102(tmp_path, monkeypatch):
    _shrink(monkeypatch)
    _tree(tmp_path, k_by_step={bn.ENDPOINT_STEP_2N: 480})
    shas = {}
    for which in bn.ENDPOINT_WHICH_2N:
        for r in bt.RUNGS:
            p = bn.endpoint_record_path(tmp_path, which, r)
            shas[str(p.relative_to(tmp_path))] = bg.sha256_file(p)
    assert len(shas) == 102
    assert an._check_rung_set_endpoint_shas_2n({"endpoint_file_sha256": shas}, tmp_path) == []
    assert any("attests nothing" in b for b in an._check_rung_set_endpoint_shas_2n({"endpoint_file_sha256": {}}, tmp_path))
    one_rel = sorted(shas)[0]
    assert any(one_rel in b and "is not the committed record's" in b
               for b in an._check_rung_set_endpoint_shas_2n({"endpoint_file_sha256": {**shas, one_rel: "0" * 64}}, tmp_path))
    assert any("are not the endpoint records" in b
               for b in an._check_rung_set_endpoint_shas_2n({"endpoint_file_sha256": {**shas, "results/endpoint/stray.json": "0" * 64}}, tmp_path))
    assert any("not a table" in b for b in an._check_rung_set_endpoint_shas_2n({"endpoint_file_sha256": []}, tmp_path))
    bn.endpoint_record_path(tmp_path, "main", bt.RUNGS[0]).unlink()
    assert any("is missing" in b for b in an._check_rung_set_endpoint_shas_2n({"endpoint_file_sha256": shas}, tmp_path))
    assert len(an._endpoint_seal_paths_2n(tmp_path)) == 104


# ------------------------------------------------------------------ power

@lru_cache(maxsize=None)
def _bits_b_and_x64_for(r_primary):
    """The real committed 2i rows/bits and the real Pythia-1b 64-draw
    counts over `r_primary` — Ruling R-1's fixture inputs for the
    `delta_sd` block, cached since several tests share the same
    r_primary."""
    battery, verify = _battery(), a2d.load_verify()
    bits_b = {r: fn.verified_bits(fn.draw_rows_2i(bi.EXP2I, r), battery[r], verify) for r in r_primary}
    x_a64 = bi.sampler_counts_pythia("1b", r_primary)
    return bits_b, x_a64


def _power_rec(r_primary, *, status="POWERED", psha=bn.PREDICTOR_SHA_2N, x256=None, x_b=None, n_pos=None):
    strata = _strata()
    x256 = x256 or bi.sampler_counts_pythia("1b", r_primary)
    x_b = x_b or x256
    dropped_a = list(an2i._degenerate_rungs(x256, strata, r_primary))
    dropped_b = list(an2i._degenerate_rungs(x_b, strata, r_primary))          # B on BASE strata
    n_pos = n_pos or {r: 100 for r in r_primary}

    def one(dropped):
        keep = [r for r in r_primary if r not in dropped]
        return {"declared_status": status, "declaration": "x", "rungs": list(r_primary),
                "n_trained_steps": bn.n_trained_comma(), "dropped_degenerate": dropped,
                "rungs_simulated": keep, "n_pos_lower_bound": n_pos, "t_bar": an.T_BAR,
                "alpha": an.ALPHA, "thin": len(keep) < 3}

    bits_b_fix, x_a64_fix = _bits_b_and_x64_for(tuple(r_primary))
    dropped_both = set(dropped_a) | set(dropped_b)
    keep_both = [r for r in r_primary if r not in dropped_both]
    _, k_by_rung = an.thinned_x_b_2n(bits_b_fix, x_a64_fix, keep_both)
    delta_sd = {"n_sim": 3, "delta_null_sd": 0.01, "delta_sd_at_declare_A": 0.01,
                "delta_sd_at_declare_B": 0.01, "delta_boot_sd_null": 0.012,
                "min_detectable_delta": 2.63 * 0.012, "formula": an.DELTA_FORMULA_LITERAL_2N,
                "k_by_rung": {r: int(k) for r, k in k_by_rung.items()}, "rungs": keep_both}
    return {"A": one(dropped_a), "B": one(dropped_b),
            "block_sd_A": {"n_sim": 3, "mean_block_sd_at_declare": 0.01, "mean_block_sd_null": 0.005,
                           "per_block_mean_T_at_declare": [0.1, 0.1, 0.1, 0.1], "blocks": 4,
                           "rungs": [r for r in r_primary if r not in dropped_a]},
            "delta_sd": delta_sd,
            "r_primary": list(r_primary),
            "primary_is_the_nine": tuple(sorted(r_primary)) == tuple(sorted(bn.R_CAP_2K)),
            "predictor_sha256": psha, "calibration_note": an.CALIBRATION_SENTENCE_2N,
            "shape_note": "x", "note": "x"}


def test_load_power_2n_and_claims_on_base_strata(tmp_path):
    r_primary = tuple(sorted(bn.R_CAP_2K))
    rec = _power_rec(r_primary)
    _w(bn.power_path(tmp_path), rec)
    got = an.load_power_2n(tmp_path, r_primary, bn.PREDICTOR_SHA_2N)
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
                        (dict(block_sd_A={k: v for k, v in rec["block_sd_A"].items() if k != "rungs"}), "attests no rung set"),
                        # Ruling R-1: load_power_2n requires the delta_sd
                        # block and its pinned formula literal.
                        (dict(delta_sd=None), "delta_sd"),
                        (dict(delta_sd={**rec["delta_sd"], "formula": "wrong"}), "formula")):
        _w(bn.power_path(tmp_path), {**rec, **mut})
        with pytest.raises(ValueError, match=needle):
            an.load_power_2n(tmp_path, r_primary, bn.PREDICTOR_SHA_2N)
    strata = _strata()
    x256 = bi.sampler_counts_pythia("1b", r_primary)
    stage1 = {r: {"correct": 100} for r in r_primary}
    bits_b, x_a64 = _bits_b_and_x64_for(r_primary)
    assert an.check_power_claims_2n(rec, x256, x256, strata, r_primary, stage1,
                                    bits_b=bits_b, x_a64=x_a64) == []
    assert any("n_pos_lower_bound" in b and "A" in b for b in an.check_power_claims_2n(
        {**rec, "A": dict(rec["A"], n_pos_lower_bound={r: 0 for r in r_primary})}, x256, x256, strata, r_primary,
        stage1, bits_b=bits_b, x_a64=x_a64))
    assert any("rungs_simulated" in b and "B" in b for b in an.check_power_claims_2n(
        {**rec, "B": dict(rec["B"], rungs_simulated=[])}, x256, x256, strata, r_primary, stage1,
        bits_b=bits_b, x_a64=x_a64))
    assert any("t_bar" in b for b in an.check_power_claims_2n(
        {**rec, "A": dict(rec["A"], t_bar=0.0)}, x256, x256, strata, r_primary, stage1,
        bits_b=bits_b, x_a64=x_a64))
    assert any("block_sd_A" in b and "non-degenerate set" in b for b in an.check_power_claims_2n(
        {**rec, "block_sd_A": dict(rec["block_sd_A"], rungs=list(r_primary)[:-1])}, x256, x256, strata, r_primary,
        stage1, bits_b=bits_b, x_a64=x_a64))
    # Ruling R-1: check_power_claims_2n refuses a k_by_rung off by one on
    # one rung, and a rungs list missing one rung.
    one_rung = rec["delta_sd"]["rungs"][0]
    bad_k = {**rec["delta_sd"], "k_by_rung": {**rec["delta_sd"]["k_by_rung"],
                                              one_rung: rec["delta_sd"]["k_by_rung"][one_rung] + 1}}
    assert any("k_by_rung" in b for b in an.check_power_claims_2n(
        {**rec, "delta_sd": bad_k}, x256, x256, strata, r_primary, stage1, bits_b=bits_b, x_a64=x_a64))
    bad_rungs = {**rec["delta_sd"], "rungs": rec["delta_sd"]["rungs"][1:]}
    assert any("delta_sd" in b and "rungs" in b for b in an.check_power_claims_2n(
        {**rec, "delta_sd": bad_rungs}, x256, x256, strata, r_primary, stage1, bits_b=bits_b, x_a64=x_a64))
    assert an.POWER_CLAIM_FIELDS_2N == ("dropped_degenerate", "rungs_simulated", "n_pos_lower_bound", "t_bar", "alpha", "thin")


def test_check_power_claims_2n_reads_b_on_base_strata_not_a_composite():
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
    bits_b, x_a64 = _bits_b_and_x64_for(r_primary)
    assert an.check_power_claims_2n(rec, x256, x_b, strata, r_primary, stage1,
                                    bits_b=bits_b, x_a64=x_a64) == []
    bad = an.check_power_claims_2n({**rec, "B": dict(rec["B"], dropped_degenerate=[])}, x256, x_b, strata, r_primary,
                                   stage1, bits_b=bits_b, x_a64=x_a64)
    assert any("dropped_degenerate" in b and "B" in b for b in bad)


# ------------------------------------------------------------- secondaries

def _fake_out(rungs, seed=0, n_steps=None):
    n_steps = n_steps or bn.n_trained_comma()
    rng = np.random.default_rng(seed)
    out = {}
    for r in rungs:
        y = [int(v) for v in rng.integers(0, n_steps + 1, size=bt.N_ITEMS)]
        out[r] = {"y": y, "n_pos": sum(1 for v in y if v > 0), "first": [None if v == 0 else 40000 for v in y]}
    return out


def test_s3_paired_difference_2n_shape_sign_and_ci():
    strata = _strata()
    rungs = ("antonym", "add_base8")
    rng = np.random.default_rng(5)
    out = _fake_out(rungs, seed=6)
    x_a = {r: [int(v) for v in rng.integers(0, 257, size=bt.N_ITEMS)] for r in rungs}
    x_b = {r: list(out[r]["y"]) for r in rungs}                       # B tracks the outcome exactly
    s3 = an.s3_paired_difference_2n(x_a, x_b, out, strata, rungs, n_boot=40, seed=0)
    assert s3["rungs"] == list(rungs) and s3["n_boot"] == 40
    assert s3["T_B"] > s3["T_A"] and s3["diff_B_minus_A"] == s3["T_B"] - s3["T_A"]
    assert s3["ci95"][0] <= s3["diff_B_minus_A"] <= s3["ci95"][1] and s3["ci95"][0] > 0
    da = {r: st.somers_d_within(x_a[r], out[r]["y"], strata[r]["strata"])["d"] for r in rungs}
    assert abs(s3["T_A"] - float(np.mean(list(da.values())))) < 1e-12   # the full-data T is the plain mean of within-stratum D
    same = an.s3_paired_difference_2n(x_a, x_a, out, strata, rungs, n_boot=10, seed=0)
    assert same["diff_B_minus_A"] == 0.0 and same["ci95"] == [0.0, 0.0]
    empty = an.s3_paired_difference_2n(x_a, x_b, out, strata, (), n_boot=10, seed=0)
    assert empty["T_A"] is None and empty["diff_B_minus_A"] is None and empty["ci95"] is None


def test_s4_matched_2n_uses_2k_rule_and_2j_blocks():
    strata = _strata()
    rungs = ("antonym", "add_base8")
    battery, verify = _battery(), a2d.load_verify()
    bits_b = {r: fn.verified_bits(fn.draw_rows_2i(bi.EXP2I, r), battery[r], verify) for r in rungs}
    x_a64 = bi.sampler_counts_pythia("1b", rungs)
    x_a256 = {r: [min(64 * 4, c * 4) for c in x_a64[r]] for r in rungs}
    out = _fake_out(rungs)
    s4 = an.s4_matched_2n(bits_b, x_a64, x_a256, out, strata, rungs)
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
    s4 = an.s4_matched_2n(bits_b, x_a64, x_a256, _fake_out(rungs, seed=4), strata, rungs)
    assert s4["increment"] == s4["thinned_B"]["T"] - s4["T_A256"]


def test_thinned_x_b_2n_is_the_first_k_g_block():
    battery, verify = _battery(), a2d.load_verify()
    rungs = ("antonym", "add_base8")
    bits_b = {r: fn.verified_bits(fn.draw_rows_2i(bi.EXP2I, r), battery[r], verify) for r in rungs}
    x_a64 = bi.sampler_counts_pythia("1b", rungs)
    x_thin, k_by_rung = an.thinned_x_b_2n(bits_b, x_a64, rungs)
    for r in rungs:
        m = bk.matched_k_256(bk.mean_rate(x_a64[r], 64), bk.mean_rate(fn.counts_from_bits(bits_b[r]), 64))
        assert k_by_rung[r] == m["k"] and 1 <= m["k"] <= 64
        assert x_thin[r] == [sum(row[:m["k"]]) for row in bits_b[r]]          # the FIRST k_g draws, item by item


def test_paired_contrast_2n_generalises_s3_and_reads_a_and_b_on_one_index_draw():
    strata = _strata()
    rungs = ("antonym", "add_base8")
    rng = np.random.default_rng(5)
    out = _fake_out(rungs, seed=6)
    x_a = {r: [int(v) for v in rng.integers(0, 257, size=bt.N_ITEMS)] for r in rungs}
    x_b = {r: list(out[r]["y"]) for r in rungs}
    pc = an.paired_contrast_2n({"B": x_b}, {"A": x_a}, out, strata, rungs, n_boot=40, seed=0)
    s3 = an.s3_paired_difference_2n(x_a, x_b, out, strata, rungs, n_boot=40, seed=0)
    assert pc["T"]["A"] == s3["T_A"] and pc["T"]["B"] == s3["T_B"]
    assert pc["contrast"] == s3["diff_B_minus_A"] and pc["ci95"] == s3["ci95"] and pc["n_boot"] == 40
    two = an.paired_contrast_2n({"p1": x_b, "p2": x_b}, {"d1": x_a, "d2": x_a, "d3": x_a}, out, strata, rungs, n_boot=10, seed=1)
    assert abs(two["contrast"] - (pc["T"]["B"] - pc["T"]["A"])) < 1e-12          # means of identical members
    empty = an.paired_contrast_2n({"B": x_b}, {"A": x_a}, out, strata, (), n_boot=10, seed=0)
    assert empty["contrast"] is None and empty["ci95"] is None


def test_annotation_c_2n_readings_and_covers_flag():
    strata = _strata()
    rungs = ("antonym", "add_base8")
    battery, verify = _battery(), a2d.load_verify()
    bits_b = {r: fn.verified_bits(fn.draw_rows_2i(bi.EXP2I, r), battery[r], verify) for r in rungs}
    x_a64 = bi.sampler_counts_pythia("1b", rungs)
    x_a256 = {r: [min(256, c * 4) for c in x_a64[r]] for r in rungs}
    x_thin, _ = an.thinned_x_b_2n(bits_b, x_a64, rungs)
    out_b = {r: {"y": list(x_thin[r]), "n_pos": sum(1 for v in x_thin[r] if v > 0)} for r in rungs}   # B's thinned read IS the outcome
    c = an.annotation_c_2n(bits_b, x_a64, x_a256, out_b, strata, rungs, increment_3b=0.0659, n_boot=40, seed=0)
    assert c["reading"] == "B-LEADS" and c["delta"] > 0 and c["ci95"][0] > 0 and set(c["k_by_rung"]) == set(rungs)
    assert c["increment_3b"] == 0.0659 and isinstance(c["covers_3b_increment"], bool)
    assert c["committed_increments"] == {"olmo2_7b_known_2k": an.INCREMENT_7B_2K_2N, "olmo2_13b_2l": an.INCREMENT_13B_2L_2N, "smollm3_3b_2m": 0.0659}
    out_a = {r: {"y": list(x_a256[r]), "n_pos": sum(1 for v in x_a256[r] if v > 0)} for r in rungs}
    assert an.annotation_c_2n(bits_b, x_a64, x_a256, out_a, strata, rungs, increment_3b=0.0659, n_boot=40, seed=0)["reading"] == "A-LEADS"
    out_n = _fake_out(rungs, seed=11)
    cn = an.annotation_c_2n(bits_b, x_a64, x_a256, out_n, strata, rungs, increment_3b=0.0659, n_boot=40, seed=0)
    assert cn["reading"] in ("NO-LEAD", "A-LEADS", "B-LEADS") and cn["ci95"] is not None
    assert an.annotation_c_2n(bits_b, x_a64, x_a256, out_n, strata, (), increment_3b=0.0659, n_boot=10, seed=0)["reading"] == "UNDEFINED"
    assert an.C_READINGS_2N == ("B-LEADS", "A-LEADS", "NO-LEAD", "UNDEFINED")


def test_annotation_c_2n_ci_boundary_readings_and_covers_flag(monkeypatch):
    """Fix round 1, #125/#126/#128: the real bootstrap in
    `test_annotation_c_2n_readings_and_covers_flag` never lands a CI
    bound EXACTLY on zero or an increment EXACTLY on a CI bound, so it
    cannot distinguish `>` from `>=` (#125), `<` from `<=` (#126), or
    `covers` from `not covers` (#128). `paired_contrast_2n` mocked to
    return hand-picked boundary values instead."""
    strata = _strata()
    rungs = ("antonym",)
    battery, verify = _battery(), a2d.load_verify()
    bits_b = {r: fn.verified_bits(fn.draw_rows_2i(bi.EXP2I, r), battery[r], verify) for r in rungs}
    x_a64 = bi.sampler_counts_pythia("1b", rungs)
    x_a256 = {r: [min(256, c * 4) for c in x_a64[r]] for r in rungs}
    out = _fake_out(rungs, seed=1)

    def _pc(ci95, contrast):
        return lambda *a, **kw: {"rungs": list(rungs), "T": {"A256": 0.0, "B_thinned": 0.0},
                                 "contrast": contrast, "ci95": ci95, "n_boot": 10,
                                 "n_boot_requested": 10, "note": "mocked"}

    monkeypatch.setattr(an, "paired_contrast_2n", _pc([0.0, 0.05], 0.02))
    c = an.annotation_c_2n(bits_b, x_a64, x_a256, out, strata, rungs, increment_3b=0.0659, n_boot=5)
    assert c["reading"] == "NO-LEAD", c["reading"]     # ci[0] == 0 is NOT strictly > 0

    monkeypatch.setattr(an, "paired_contrast_2n", _pc([-0.05, 0.0], -0.02))
    c2 = an.annotation_c_2n(bits_b, x_a64, x_a256, out, strata, rungs, increment_3b=0.0659, n_boot=5)
    assert c2["reading"] == "NO-LEAD", c2["reading"]    # ci[1] == 0 is NOT strictly < 0

    monkeypatch.setattr(an, "paired_contrast_2n", _pc([0.01, 0.03], 0.02))
    c3 = an.annotation_c_2n(bits_b, x_a64, x_a256, out, strata, rungs, increment_3b=0.02, n_boot=5)
    assert c3["covers_3b_increment"] is True             # increment_3b sits inside [0.01, 0.03]
    c4 = an.annotation_c_2n(bits_b, x_a64, x_a256, out, strata, rungs, increment_3b=0.5, n_boot=5)
    assert c4["covers_3b_increment"] is False


def test_read_increment_3b_2n_matches_the_literal():
    got = an.read_increment_3b_2n(bm.EXP2M)
    assert round(got, 4) == round(an.INCREMENT_3B_2N, 4) == 0.0659
    with pytest.raises(ValueError, match="increment"):
        an.read_increment_3b_2n(Path("/nonexistent"))


def test_increment_reader_returns_the_files_own_value_not_a_hardcoded_literal(tmp_path):
    """Fix round 1, #129: `test_read_increment_3b_2n_matches_the_literal`
    is excluded from the mutation fast pass by name (`-k "... and not
    test_read_increment ..."`) — and the FIRST attempt at this closing
    test, named `test_read_increment_3b_2n_returns_...`, was ALSO
    excluded, because `-k`'s exclusion is a SUBSTRING match against the
    node id, not an exact name match (the file's own mutation_check.py
    docstring warns of exactly this trap re: test_s4/test_s5/real_tree,
    and it caught this test too — confirmed via `--only 129`: still
    SURVIVED with the first name, killed after this rename). A
    hand-built verdict.json carrying an increment far from
    INCREMENT_3B_2N must be read back exactly."""
    results = tmp_path / "results"
    results.mkdir()
    (results / "verdict.json").write_text(json.dumps(
        {"secondaries": {"S4 matched density": {"increment": 0.987654}}}))
    got = an.read_increment_3b_2n(tmp_path)
    assert got == 0.987654
    assert round(got, 4) != round(an.INCREMENT_3B_2N, 4)


def test_s5_answer_prior_2n_is_2j_functional_on_2i_rows():
    strata = _strata()
    rungs = ("antonym",)
    battery = _battery()
    rows = {r: fn.draw_rows_2i(bi.EXP2I, r) for r in rungs}
    s5 = an.s5_answer_prior_2n(rows, battery, _fake_out(rungs), strata, rungs, n_perm=20, n_boot=5)
    assert s5["pi"]["antonym"] == fn.wrong_target_propensity(rows["antonym"], battery["antonym"])
    assert s5["test"]["stratified"]["T"] is not None and s5["non_gating"] is True


def test_answer_prior_non_gating_is_a_hardcoded_literal(monkeypatch):
    monkeypatch.setattr(fn, "wrong_target_propensity", lambda rows, cap, **kw: 0.5)
    monkeypatch.setattr(an, "_run_test",
                        lambda *a, **kw: {"stratified": {"T": 0.0, "p": 1.0, "n_perm": 1, "n_ge": 1},
                                          "fires": False, "eligible": [], "per_rung": {}})
    assert an.s5_answer_prior_2n({"antonym": []}, {"antonym": {}}, {"antonym": {}}, {}, ("antonym",))["non_gating"] is True


def test_s8_outcome_order_2n_reads_each_committed_outcome_over_its_own_rungs():
    strata = _strata()
    r_primary = tuple(sorted(bn.R_CAP_2K))
    out_comma = _fake_out(r_primary, seed=8)
    tracks = {r: {"y": list(out_comma[r]["y"])} for r in ("antonym", "add_base8")}      # tracks Comma exactly
    indep = _fake_out(r_primary, seed=9, n_steps=16)                                    # independent
    committed = {"pythia_2.8b": tracks, "pythia_6.9b": tracks, "olmo2_7b": indep,
                 "olmo2_13b": indep, "smollm3_3b": indep}
    s8 = an.s8_outcome_order_2n(out_comma, strata, r_primary, committed, n_perm=30, n_boot=5)
    assert set(s8) == {"pythia_2.8b", "pythia_6.9b", "olmo2_7b", "olmo2_13b", "smollm3_3b"}
    assert s8["pythia_2.8b"]["rungs"] == ["add_base8", "antonym"]
    assert s8["olmo2_13b"]["rungs"] == list(r_primary)
    assert s8["pythia_2.8b"]["test"]["stratified"]["T"] > 0.5
    assert abs(s8["olmo2_13b"]["test"]["stratified"]["T"]) < 0.15
    assert all(v["descriptive"] is True for v in s8.values())


def test_load_committed_outcomes_2n_covers_all_five_sources(monkeypatch):
    """Fix round 1, #140: `load_committed_outcomes_2n`'s five loaders
    mocked to canned sentinels (no real 2i/2l/2m tree reads) — kills
    'the smollm3_3b key dropped' at unit-test speed."""
    monkeypatch.setattr(an2j, "load_pythia_outcomes", lambda battery, verify_fn: {"2.8b": "P28", "6.9b": "P69"})
    monkeypatch.setattr(bi, "load_manifest", lambda *a, **kw: "MAN2I")
    monkeypatch.setattr(an2i, "load_sweep_7b", lambda *a, **kw: "SWEEP7B")
    monkeypatch.setattr(an2i, "outcomes_7b", lambda *a, **kw: "OUT7B")
    monkeypatch.setattr(bl, "load_manifest_13b", lambda *a, **kw: "MAN2L")
    monkeypatch.setattr(bl, "endpoint_sha256", lambda *a, **kw: "ESHA13B")
    monkeypatch.setattr(an2l, "load_sweep_13b", lambda *a, **kw: "SWEEP13B")
    monkeypatch.setattr(an2l, "outcomes_13b", lambda *a, **kw: "OUT13B")
    monkeypatch.setattr(bm, "load_manifest_3b", lambda *a, **kw: "MAN2M")
    monkeypatch.setattr(bm, "endpoint_sha256", lambda *a, **kw: "ESHA3B")
    monkeypatch.setattr(an2m, "load_sweep_3b", lambda *a, **kw: "SWEEP3B")
    monkeypatch.setattr(an2m, "outcomes_3b", lambda *a, **kw: "OUT3B")
    out = an.load_committed_outcomes_2n({}, None, root_2i=bi.EXP2I, root_2l=bl.EXP2L, root_2m=bm.EXP2M)
    assert set(out) == {"pythia_2.8b", "pythia_6.9b", "olmo2_7b", "olmo2_13b", "smollm3_3b"}
    assert out == {"pythia_2.8b": "P28", "pythia_6.9b": "P69", "olmo2_7b": "OUT7B",
                   "olmo2_13b": "OUT13B", "smollm3_3b": "OUT3B"}


def test_s8c_corpus_contrast_2n_groups_and_direction():
    strata = _strata()
    r_primary = tuple(sorted(bn.R_CAP_2K))
    out = _fake_out(r_primary, seed=8)
    pile = {r: {"y": list(out[r]["y"])} for r in r_primary}                       # tracks Comma exactly
    dclm = _fake_out(r_primary, seed=9, n_steps=16)
    rows = {"pythia_2.8b": pile, "pythia_6.9b": pile, "olmo2_7b": dclm, "olmo2_13b": dclm, "smollm3_3b": dclm}
    s8c = an.s8c_corpus_contrast_2n(rows, out, strata, r_primary, n_boot=20, seed=0)
    assert s8c["pile_rows"] == ["pythia_2.8b", "pythia_6.9b"] and s8c["dclm_rows"] == ["olmo2_7b", "olmo2_13b", "smollm3_3b"]
    assert s8c["contrast"] > 0.5 and s8c["ci95"][0] > 0 and s8c["descriptive"] is True and s8c["no_alpha_claim"] is True
    assert s8c["rungs"] == list(r_primary)


def test_s9_sign_ledger_2n_reads_the_committed_option_rung_ds():
    A = {"per_rung": {r: {"d": 0.1} for r in bn.R_CAP_2K}}
    B = {"per_rung": {r: {"d": 0.2} for r in bn.R_CAP_2K}}
    led = an.s9_sign_ledger_2n(A, B, root_2l=bl.EXP2L, root_2m=bm.EXP2M)
    assert an.OPTION_RUNGS_2N == ("antonym", "antonym6", "odd6") and set(led["rows"]) == set(an.OPTION_RUNGS_2N)
    ant = led["rows"]["antonym"]
    assert round(ant["olmo2_13b_2l"]["A"], 3) == -0.066 and round(ant["olmo2_13b_2l"]["B"], 3) == 0.256
    assert round(ant["smollm3_3b_2m"]["A"], 3) == -0.041 and round(ant["smollm3_3b_2m"]["B"], 3) == 0.168
    assert ant["olmo2_7b_known"]["A"] == 0.024 and ant["olmo2_7b_known"]["B"] == 0.217 and ant["comma_7b"] == {"A": 0.1, "B": 0.2}
    assert led["rows"]["antonym6"]["olmo2_7b_known"]["A"] == 0.115
    assert led["rows"]["odd6"]["olmo2_7b_known"]["A"] == 0.096
    assert led["sources"]["olmo2_7b_known"].startswith("literals")


def test_sign_ledger_rows_are_exactly_the_three_option_rungs(tmp_path):
    """Fix round 1, #141: `test_s9_sign_ledger_2n_reads_the_committed_
    option_rung_ds` is excluded from the mutation fast pass by name
    (`-k "... and not test_s9_sign ..."`). Hand-built 2l/2m verdict.json
    stand-ins (no real committed trees) so this is fast and
    independently named. `OPTION_RUNGS_2N -> bn.R_CAP_2K` (the nine)
    would KeyError on `SIGN_LEDGER_LITERALS_2N["olmo2_7b_known"][r]`
    for any of the six non-option rungs it adds."""
    per_rung = {r: {"d": 0.3} for r in an.OPTION_RUNGS_2N}
    verdict = {"tests": {"A": {"per_rung": per_rung}, "B": {"per_rung": per_rung}}}
    for who in ("2l", "2m"):
        d = tmp_path / who / "results"
        d.mkdir(parents=True)
        (d / "verdict.json").write_text(json.dumps(verdict))
    A = {"per_rung": {r: {"d": 0.1} for r in an.OPTION_RUNGS_2N}}
    B = {"per_rung": {r: {"d": 0.2} for r in an.OPTION_RUNGS_2N}}
    led = an.s9_sign_ledger_2n(A, B, root_2l=tmp_path / "2l", root_2m=tmp_path / "2m")
    assert set(led["rows"]) == set(an.OPTION_RUNGS_2N) == {"antonym", "antonym6", "odd6"}
    assert led["option_rungs"] == list(an.OPTION_RUNGS_2N)


def test_extra_rungs_2n_shape():
    strata = _strata()
    out = _fake_out(("count_div13", "reverse_string"))
    x64 = bi.sampler_counts_pythia("1b", ("count_div13", "reverse_string"))
    x_b = {r: list(x64[r]) for r in x64}
    res = an._extra_rungs_2n(x64, x_b, out, strata, r_eleven_extra=("count_div13",), r_extra=("reverse_string",))
    assert set(res["eleven_extra"]["count_div13"]) == {"stratified_d_A64", "stratified_d_B", "n_pos"}
    assert set(res["extra"]["reverse_string"]) == {"raw_d_A64", "raw_d_B", "n_pos"}


# -------------------------------------------------------------- predictors

def test_load_predictors_2n_on_the_real_trees_is_clean():
    battery, verify = _battery(), a2d.load_verify()
    failures, ctx = an.load_predictors_2n(bi.EXP2I, bk.EXP2K, battery=battery, verify_fn=verify)
    assert failures == []
    assert set(ctx["cells_2k"]) == set(bk.SIZES_2K) and ctx["x_b"] and ctx["bits_b"] and ctx["rows_2i"]


@pytest.mark.parametrize("attr,needle", [("SEAL_2K_SHA256", "2n predictor 2k seal sha"),
                                         ("SEAL_2I_SHA256", "2n predictor 2i seal sha")])
def test_load_predictors_2n_refuses_seal_literal_drift(monkeypatch, attr, needle):
    battery, verify = _battery(), a2d.load_verify()
    monkeypatch.setattr(bn, attr, "0" * 64)
    failures, _ = an.load_predictors_2n(bi.EXP2I, bk.EXP2K, battery=battery, verify_fn=verify)
    assert any(needle in f and "is not the literal" in f for f in failures)


@pytest.mark.parametrize("mod,attr,needle", [
    (an2k, "seal_failures_2k", "injected 2k seal mismatch"),
    (an2i, "_check_predictor_counts_2i", "injected 2i counts mismatch"),
])
def test_load_predictors_2n_carries_the_upstream_checks(monkeypatch, mod, attr, needle):
    battery, verify = _battery(), a2d.load_verify()
    monkeypatch.setattr(mod, attr, lambda *a, **kw: [needle])
    failures, _ = an.load_predictors_2n(bi.EXP2I, bk.EXP2K, battery=battery, verify_fn=verify)
    assert any(needle in f for f in failures)


def test_load_predictors_2n_refuses_a_wrong_2i_rung_set_x_b_mismatch_and_a_halt(monkeypatch):
    battery, verify = _battery(), a2d.load_verify()
    monkeypatch.setattr(an2i, "_load_rung_set", lambda root: {"R_CAP": ["antonym"]})
    assert any("2n predictor 2i rung set: R_CAP" in f for f in an.load_predictors_2n(bi.EXP2I, bk.EXP2K, battery=battery, verify_fn=verify)[0])
    monkeypatch.undo()
    monkeypatch.setattr(bi, "sampler_counts_olmo",
                        lambda rungs, root=None, battery=None, verify_fn=None: {r: [0] * bt.N_ITEMS for r in rungs})
    assert any("x_B bits do not reproduce the count" in f for f in an.load_predictors_2n(bi.EXP2I, bk.EXP2K, battery=battery, verify_fn=verify)[0])
    monkeypatch.undo()
    monkeypatch.setattr(bk, "halt_markers", lambda root_2k: [Path("x/y.HALTED")])
    assert any("2n predictor 2k tier HALTED marker present" in f for f in an.load_predictors_2n(bi.EXP2I, bk.EXP2K, battery=battery, verify_fn=verify)[0])


_TOTALITY_FORCED_CASES_2N = [
    (an2i, "_load_predictor_seal_content", "2n predictor 2i seal content"),
    (an2i, "_load_rung_set", "2n predictor 2i rung set file"),
    (bi, "load_manifest", "2n predictor 2i manifest"),
    (bi, "entry_1b_endpoint", "2n predictor 2i 1B endpoint entry"),
    (an2i, "_check_predictor_seal_sampling", "2n predictor 2i seal sampling block"),
    (an2i, "_check_predictor_counts_2i", "2n predictor x_B counts vs the sealed attestation"),
    (an2k, "seal_failures_2k", "2n predictor 2k seal vs re-derivation"),
    (fn, "draw_rows_2i", "2n predictor x_B rows and bits"),
]


@pytest.mark.parametrize("mod,attr,label", _TOTALITY_FORCED_CASES_2N)
def test_load_predictors_2n_forced_exceptions_are_graceful(monkeypatch, mod, attr, label):
    battery, verify = _battery(), a2d.load_verify()

    def _raise(*a, **kw):
        raise ValueError("injected for a mutation-closure test")

    monkeypatch.setattr(mod, attr, _raise)
    failures, _ = an.load_predictors_2n(bi.EXP2I, bk.EXP2K, battery=battery, verify_fn=verify)
    assert any(label in f and "injected" in f for f in failures), (label, failures)


def test_load_predictors_2n_seal_read_forced_exception(monkeypatch):
    battery, verify = _battery(), a2d.load_verify()
    seal_file = bk.seal_path(bk.EXP2K)
    real_read_text = Path.read_text

    def _flaky_read_text(self, *a, **kw):
        if self == seal_file:
            raise ValueError("injected for a mutation-closure test")
        return real_read_text(self, *a, **kw)

    monkeypatch.setattr(Path, "read_text", _flaky_read_text)
    failures, _ = an.load_predictors_2n(bi.EXP2I, bk.EXP2K, battery=battery, verify_fn=verify)
    assert any("2n predictor 2k seal read" in f and "injected" in f for f in failures), failures


_RUN_FORCED_CASES_2N = [
    (bg, "load_battery", "2n battery items"),
    (bg, "load_floors", "2n floors 2d"),
    (a2d, "load_verify", "2n verify criterion 3c"),
    (pr, "load_predictor", "2n strata source 2g predictor"),
    (bg, "check_frozen_imports_2g", "2n upstream 2g frozen imports"),
    (bn, "entry_which_comma", "2n Comma endpoint entries"),
]


@pytest.mark.parametrize("mod,attr,label", _RUN_FORCED_CASES_2N)
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
    assert any("2n strata pins 2g" in f and "injected" in f for f in v["referents"]["failures"])


def test_run_frozen_check_forced_exception():
    def _raise():
        raise ValueError("injected for a mutation-closure test")

    v = an.run(n_perm=20, n_boot=5, frozen_check=_raise)
    assert v["verdict"] == "INSUFFICIENT_DATA"
    assert any("2n frozen modules" in f and "injected" in f for f in v["referents"]["failures"])


def test_run_import_surface_entry_forced_exception(monkeypatch):
    # `imports_pinned=True` is passed explicitly rather than left to the
    # default: it makes the branch under test independent of whether
    # IMPORTED_SHA256_2N happens to be pinned (it is not, yet), so the
    # injected exception is the only thing this case observes.
    monkeypatch.setattr(an, "check_imports_2n", lambda: (_ for _ in ()).throw(ValueError("injected")))
    v = an.run(n_perm=20, n_boot=5, imports_pinned=True)
    assert v["verdict"] == "INSUFFICIENT_DATA"
    assert any("2n import surface (entry)" in f and "injected" in f for f in v["referents"]["failures"])


def test_run_referent_manifest_check_forced_exception(monkeypatch):
    monkeypatch.setattr(mkr, "check_referents", lambda *a, **kw: (_ for _ in ()).throw(ValueError("injected")))
    v = an.run(n_perm=20, n_boot=5, referents_sha="0" * 64)
    assert v["verdict"] == "INSUFFICIENT_DATA"
    assert any("2n referent manifest" in f and "injected" in f for f in v["referents"]["failures"])


def test_core_reads_both_tests_on_the_bare_base_strata_ast():
    """Dial b as a property of the SOURCE (mutation closure, 2m's Task 5
    fix round 1, #88), at zero cost: inside `run()`'s nested `_core`,
    BOTH `_run_test` calls pass `strata` — the bare base strata, an
    `ast.Name` — as their fourth positional argument, never a composite
    built by a call."""
    tree = ast.parse((an.EXP2N / "analyze_2n.py").read_text())
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


def test_core_x256_indexes_k_total_not_a_bare_literal():
    """Fix round 1, #116: `x256 = {r: cells_2k["1b"][r]["counts"][bk.K_TOTAL]
    for r in r_primary}` inside `_core` must subscript `counts` with the
    module constant `bk.K_TOTAL` (an ast.Attribute), never a bare int
    literal like `64` (a 4-block predictor read where a 256-draw read
    is required)."""
    tree = ast.parse((an.EXP2N / "analyze_2n.py").read_text())
    run_fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "run")
    core = next(n for n in ast.walk(run_fn) if isinstance(n, ast.FunctionDef) and n.name == "_core")
    assign = next(n for n in ast.walk(core) if isinstance(n, ast.Assign)
                 and any(isinstance(t, ast.Name) and t.id == "x256" for t in n.targets))
    dictcomp = assign.value
    assert isinstance(dictcomp, ast.DictComp), ast.dump(dictcomp)
    value_expr = dictcomp.value          # DictComp uses .key/.value, not .elt
    assert isinstance(value_expr, ast.Subscript), ast.dump(value_expr)
    idx = value_expr.slice
    if isinstance(idx, getattr(ast, "Index", ())):    # py<3.9 wraps the slice; harmless no-op on 3.9+
        idx = idx.value
    assert isinstance(idx, ast.Attribute) and idx.attr == "K_TOTAL", ast.dump(idx)


def test_check_imports_2n_real_rule_flags_a_module_outside_tests(monkeypatch):
    fake_path = str(bn.EXP2N / "PROGRESS.md")
    assert Path(fake_path).is_file()
    monkeypatch.setitem(sys.modules, "exp2n_fake_module_for_mutation_test", types.SimpleNamespace(__file__=fake_path))
    if an.IMPORTED_SHA256_2N is None:
        monkeypatch.setattr(an, "IMPORTED_SHA256_2N", {})
    with pytest.raises(RuntimeError, match="unpinned module"):
        an.check_imports_2n()


# ------------------------------------------------------------------- tree

def _prim(T, p, fires, eligible=("a", "b", "c"), named=None):
    return {"stratified": {"T": T, "p": p, "n_perm": 10000, "n_ge": 0}, "fires": fires,
            "named_inside": named, "eligible": list(eligible), "per_rung": {}}


def test_verdict_tree_2n_names_the_four_worlds():
    for a, b, want in ((True, False, "PYTHIA-ONLY"), (False, True, "OLMO-ONLY"), (True, True, "SHARED"),
                       (False, False, "NEITHER")):
        t = an.verdict_tree_2n([], _prim(0.2 if a else 0.02, 0.001, a), _prim(0.2 if b else 0.02, 0.001, b))
        assert t["verdict"] == want and "A: T=" in t["reason"] and "B: T=" in t["reason"]
    assert an.verdict_tree_2n(["x"], None, None)["verdict"] == "INSUFFICIENT_DATA"
    t = an.verdict_tree_2n([], _prim(0.2, 0.001, True), _prim(None, 1.0, False, eligible=(), named="undefined: no eligible rung"))
    assert an.DISCLOSURE_UNDEFINED_2N["B"] in t["disclosures"] and t["verdict"] == "PYTHIA-ONLY"
    assert an.WORLDS_2N == ("INSUFFICIENT_DATA", "SHARED", "PYTHIA-ONLY", "OLMO-ONLY", "NEITHER")
    assert "PYTHIA-ONLY" in an.CALIBRATION_SENTENCE_2N and "LINEAGE" not in an.CALIBRATION_SENTENCE_2N


def test_verdict_2n_worlds_disclosures_and_licences():
    powered = {"A": {"declared_status": "POWERED"}, "B": {"declared_status": "POWERED"}}
    under_b = {"A": {"declared_status": "POWERED"}, "B": {"declared_status": "DECLARED UNDERPOWERED IN ADVANCE"}}
    nine = tuple(sorted(bn.R_CAP_2K))
    ins = an.verdict_2n(["x"], None, None, None, nine)
    assert ins["verdict"] == "INSUFFICIENT_DATA" and an._licensed_2n(ins) == an.LICENSED_2N["INSUFFICIENT_DATA"]
    for a, b, want in ((True, False, "PYTHIA-ONLY"), (False, True, "OLMO-ONLY"), (True, True, "SHARED"), (False, False, "NEITHER")):
        t = an.verdict_2n([], _prim(0.2 if a else 0.02, 0.001, a), _prim(0.2 if b else 0.02, 0.001, b), powered, nine)
        assert t["verdict"] == want and an._licensed_2n(t).startswith(an.LICENSED_2N[want])
        assert an.KNOWN_INPUTS_CAVEAT_2N in an._licensed_2n(t)
    t = an.verdict_2n([], _prim(0.2, 0.001, True), _prim(0.02, 0.5, False), under_b, nine)
    assert an.DISCLOSURE_UNDERPOWERED_2N["B"] in t["disclosures"] and an.DISCLOSURE_UNDERPOWERED_2N["A"] not in t["disclosures"]
    assert an.DISCLOSURE_UNDERPOWERED_2N["B"] in an._licensed_2n(t)
    t = an.verdict_2n([], _prim(0.2, 0.001, True), _prim(0.02, 0.5, False), powered, nine[:2])
    assert an.DISCLOSURE_THIN_2N in t["disclosures"] and t["verdict"] == "PYTHIA-ONLY"
    assert set(an.LICENSED_2N) == set(an.WORLDS_2N)


def test_verdict_2n_reason_carries_the_annotation():
    powered = {"A": {"declared_status": "POWERED"}, "B": {"declared_status": "POWERED"}}
    nine = tuple(sorted(bn.R_CAP_2K))
    t = an.verdict_2n([], _prim(0.2, 0.001, True), _prim(0.2, 0.001, True), powered, nine,
                      annotation={"C": {"reading": "NO-LEAD", "delta": 0.01, "ci95": [-0.02, 0.04]}})
    assert "C: NO-LEAD (delta 0.0100, ci95 [-0.0200, 0.0400])" in t["reason"]
    assert t["verdict"] == "SHARED"
    t2 = an.verdict_2n([], _prim(0.2, 0.001, True), _prim(0.2, 0.001, True), powered, nine, annotation=None)
    assert "C:" not in t2["reason"]
    # Fix round 1, #71: `annotation` must be carried into verdict_2n's own
    # return dict, not just baked into the `reason` string.
    assert t["annotation"] == {"C": {"reading": "NO-LEAD", "delta": 0.01, "ci95": [-0.02, 0.04]}}
    assert t2["annotation"] is None


def test_licensed_2n_appends_the_c_modifier_keyed_by_reading_and_covers(monkeypatch):
    """Fix round 1, #71/#73/#74: no existing test exercised `_licensed_2n`
    with a tree carrying an `annotation`, so neither the "modifier
    dropped" mutant (#73) nor the "covers/excludes swapped" mutant
    (#74, `_c_modifier_key_2n`) nor #71 (annotation not returned by
    `verdict_2n`, which starves this code path entirely) had a covering
    test."""
    powered = {"A": {"declared_status": "POWERED"}, "B": {"declared_status": "POWERED"}}
    nine = tuple(sorted(bn.R_CAP_2K))

    def _t(annotation):
        return an.verdict_2n([], _prim(0.2, 0.001, True), _prim(0.2, 0.001, True), powered, nine,
                             annotation=annotation)

    t_covers = _t({"C": {"reading": "B-LEADS", "covers_3b_increment": True}})
    lic_covers = an._licensed_2n(t_covers)
    assert lic_covers.startswith(an.LICENSED_2N["SHARED"])
    assert an.C_MODIFIERS_2N["B-LEADS-covers"] in lic_covers

    t_excludes = _t({"C": {"reading": "B-LEADS", "covers_3b_increment": False}})
    lic_excludes = an._licensed_2n(t_excludes)
    assert an.C_MODIFIERS_2N["B-LEADS-excludes"] in lic_excludes
    assert an.C_MODIFIERS_2N["B-LEADS-covers"] not in lic_excludes

    t_a = _t({"C": {"reading": "A-LEADS"}})
    assert an.C_MODIFIERS_2N["A-LEADS"] in an._licensed_2n(t_a)

    # a tree with no annotation at all: the modifier block must not run
    t_none = _t(None)
    lic_none = an._licensed_2n(t_none)
    assert lic_none.startswith(an.LICENSED_2N["SHARED"])
    assert not any(m in lic_none for m in an.C_MODIFIERS_2N.values())


def test_verdict_2n_discloses_a_test_that_read_fewer_than_three_rungs():
    powered = {"A": {"declared_status": "POWERED"}, "B": {"declared_status": "POWERED"}}
    nine = tuple(sorted(bn.R_CAP_2K))
    A = {**_prim(0.2, 0.001, True, eligible=("add_base8",)), "thin": ["add3_mid", "sub3_mid", "sub4_mid"], "dropped_degenerate": []}
    t = an.verdict_2n([], A, _prim(0.02, 0.5, False), powered, nine[:4])
    assert t["verdict"] == "PYTHIA-ONLY" and an.DISCLOSURE_THIN_2N not in t["disclosures"]
    hit = [d for d in t["disclosures"] if d.startswith(an.DISCLOSURE_THIN_ELIGIBLE_PREFIX_2N + "A")]
    assert hit and "add_base8" in hit[0] and hit[0] in an._licensed_2n(t) and hit[0] in t["reason"]
    assert not any(d.startswith(an.DISCLOSURE_THIN_ELIGIBLE_PREFIX_2N + "B") for d in t["disclosures"])


def test_descriptive_rows_say_their_fires_key_is_not_a_rule():
    """Freeze F-3 (2m's lineage): `_run_test` stamps `fires` on every test
    it runs, descriptives included. S5, S8 and S8c make no alpha claim,
    so each row says so in words beside the flag."""
    assert "{name}" in an.NO_ALPHA_NOTE_2N
    for name in ("S5", "S8", "S8c"):
        note = an.NO_ALPHA_NOTE_2N.format(name=name)
        assert "not a firing rule" in note.lower() and "no alpha claim" in note
        assert "secondaries.failures" in note
    # the rows themselves, built through the production functions on an
    # empty rung set (`_run_test` short-circuits to the undefined result,
    # so no committed bytes are needed)
    s5 = an.s5_answer_prior_2n({}, {}, {}, {}, (), n_perm=10, n_boot=5)
    assert s5["non_gating"] is True and s5["no_alpha_claim"] is True
    assert s5["note"] == an.NO_ALPHA_NOTE_2N.format(name="S5")
    s8 = an.s8_outcome_order_2n({}, {}, (), {"olmo2_13b": {}, "pythia_2.8b": {}}, n_perm=10, n_boot=5)
    assert set(s8) == {"olmo2_13b", "pythia_2.8b"}
    for row in s8.values():
        assert row["descriptive"] is True and row["no_alpha_claim"] is True
        assert row["note"] == an.NO_ALPHA_NOTE_2N.format(name="S8")


def test_which_coherence_failures_2n():
    """Freeze F-2: a `which` has no checkpoint record, so nothing
    measured that its 34 records came from ONE load."""
    recs = {r: {"weight_sha256": "D", "commit": "c" * 40, "config_source": "repo@c"}
            for r in bn.bt.RUNGS}
    assert an.which_coherence_failures_2n("stage1_final", recs) == []
    for field, label in (("weight_sha256", "tensor digest"), ("commit", "commit"),
                         ("config_source", "config source")):
        mixed = {r: dict(v) for r, v in recs.items()}
        mixed["odd6"][field] = "OTHER"
        bad = an.which_coherence_failures_2n("main", mixed)
        assert bad and f"2 different {label}s" in bad[0] and bad[0].startswith("endpoint comma_7b main")
    empty = {r: {"weight_sha256": None, "commit": "c" * 40, "config_source": "repo@c"}
             for r in bn.bt.RUNGS}
    assert any("empty" in b for b in an.which_coherence_failures_2n("stage2_final", empty))


def test_verdict_2n_discloses_a_reading_narrower_than_r_primary():
    """Freeze F-1: 3 <= |eligible| < |R_PRIMARY| carried no disclosure —
    2l F-4's guard speaks only below three. The two are mutually
    exclusive and both ride on the licence."""
    powered = {"A": {"declared_status": "POWERED"}, "B": {"declared_status": "POWERED"}}
    nine = tuple(sorted(bn.R_CAP_2K))
    eight = tuple(r for r in nine if r != "add3_mid")
    A = {**_prim(0.2, 0.001, True, eligible=eight), "thin": ["add3_mid"], "dropped_degenerate": []}
    B = {**_prim(0.02, 0.5, False, eligible=eight), "thin": ["add3_mid"], "dropped_degenerate": []}
    t = an.verdict_2n([], A, B, powered, nine)
    assert t["verdict"] == "PYTHIA-ONLY"
    assert not any(d.startswith(an.DISCLOSURE_THIN_ELIGIBLE_PREFIX_2N) for d in t["disclosures"])
    for test in ("A", "B"):
        hit = [d for d in t["disclosures"]
               if d.startswith(an.DISCLOSURE_PARTIAL_ELIGIBLE_PREFIX_2N + test)]
        # the MISSED rungs, not the read ones: assert the exact clause, since
        # the rung also appears later inside the `thin` list either way
        assert hit and "— ['add3_mid'] did not carry it" in hit[0]
        assert "add_base8" not in hit[0].split("did not carry it")[0]
        assert hit[0] in an._licensed_2n(t) and hit[0] in t["reason"]
    # the full reading discloses nothing; a sub-three reading takes 2l F-4's
    # wording and NOT this one (mutual exclusion)
    full = {**_prim(0.2, 0.001, True, eligible=nine), "thin": [], "dropped_degenerate": []}
    t_full = an.verdict_2n([], full, full, powered, nine)
    assert t_full["disclosures"] == []
    two = {**_prim(0.2, 0.001, True, eligible=nine[:2]), "thin": list(nine[2:]), "dropped_degenerate": []}
    t_two = an.verdict_2n([], two, two, powered, nine)
    assert all(d.startswith(an.DISCLOSURE_THIN_ELIGIBLE_PREFIX_2N) for d in t_two["disclosures"])
    assert an._partial_eligible_2n("A", two, nine) is None
    assert an._partial_eligible_2n("A", full, nine) is None


def test_partial_eligible_2n_same_set_when_rungs_simulated_matches_eligible():
    """R-1 (2m, ratified): SAME/WIDER is decided against the power
    record's OWN `rungs_simulated` list, not re-derived from
    `res['dropped_degenerate']`. When the declared list equals the
    read set exactly, the two are the SAME set reached by a different
    route (every unread rung was itself dropped as predictor-
    degenerate). The disclosure still fires (the licence stays bounded
    to the rungs named as read) but must not overstate the gap between
    the reading and the declaration."""
    nine = tuple(sorted(bn.R_CAP_2K))
    eight = tuple(r for r in nine if r != "add3_mid")
    same = {"eligible": eight, "thin": [], "dropped_degenerate": ["add3_mid"]}
    msg = an._partial_eligible_2n("A", same, nine, rungs_simulated=eight)
    assert msg is not None
    assert "the SAME set" in msg
    assert "WIDER" not in msg
    assert "bounded to the rungs named as read" in msg


def test_partial_eligible_2n_wider_when_rungs_simulated_exceeds_eligible_despite_dropped_degenerate():
    """R-1: the discriminating case — every rung the test did not read
    (`missing`) is ITSELF listed in `res['dropped_degenerate']`
    (`_run_test`'s retry loop folds a 'no informative pair' rung into
    that same field), so a naive `all(r in dropped_degenerate for r in
    missing)` would read SAME. But the power record's own
    `rungs_simulated`, computed from the coarser `_degenerate_rungs`
    pre-check that never caught this rung, is WIDER than the reading by
    exactly that rung — the sentence must say so, naming it."""
    nine = tuple(sorted(bn.R_CAP_2K))
    eight = tuple(r for r in nine if r != "arith_next")
    wider = {"eligible": eight, "thin": [], "dropped_degenerate": ["arith_next"]}
    msg = an._partial_eligible_2n("A", wider, nine, rungs_simulated=nine)
    assert msg is not None
    assert "a WIDER set" in msg
    assert "arith_next" in msg.split("(also")[-1]
    assert "SAME" not in msg


def test_partial_eligible_2n_wider_set_when_a_missing_rung_is_thin():
    """A genuinely thin missing rung: the power record's coarse
    degenerate-only `rungs_simulated` never drops a thin rung at all,
    so it is wider than the reading for the ordinary reason."""
    nine = tuple(sorted(bn.R_CAP_2K))
    eight = tuple(r for r in nine if r != "add3_mid")
    wider = {"eligible": eight, "thin": ["add3_mid"], "dropped_degenerate": []}
    msg = an._partial_eligible_2n("A", wider, nine, rungs_simulated=nine)
    assert msg is not None
    assert "a WIDER set than the reading" in msg
    assert "add3_mid" in msg.split("(also")[-1]
    assert "the SAME set" not in msg


def test_verdict_2n_partial_eligible_wider_via_power_rungs_simulated():
    """R-1: the plumbing through `verdict_2n`, not only the helper —
    `verdict_2n` must pass the power record's `rungs_simulated` list
    through to `_partial_eligible_2n`, not leave the SAME/WIDER
    decision to the helper's default (unreadable) branch."""
    nine = tuple(sorted(bn.R_CAP_2K))
    eight = tuple(r for r in nine if r != "arith_next")
    A = {**_prim(0.2, 0.001, True, eligible=eight), "thin": [], "dropped_degenerate": ["arith_next"]}
    B = {**_prim(0.02, 0.5, False, eligible=nine), "thin": [], "dropped_degenerate": []}
    power = {"A": {"rungs_simulated": list(nine)}, "B": {"rungs_simulated": list(nine)}}
    t = an.verdict_2n([], A, B, power, nine)
    hit = [d for d in t["disclosures"]
           if d.startswith(an.DISCLOSURE_PARTIAL_ELIGIBLE_PREFIX_2N + "A")]
    assert hit and "a WIDER set" in hit[0] and "arith_next" in hit[0].split("(also")[-1]


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


def test_failure_labels_disjoint_from_2i_2j_2k_2l_2m():
    mine = set(_all_failure_labels(bn.EXP2N / "analyze_2n.py"))
    assert mine and all(lab.startswith("2n") for lab in mine)
    assert not any(lab.startswith("2m") for lab in mine)
    for other in (bi.EXP2I / "analyze_2i.py", bg.REPO / "experiments/exp2j/analyze_2j.py",
                  bk.EXP2K / "analyze_2k.py", bl.EXP2L / "analyze_2l.py", bm.EXP2M / "analyze_2m.py"):
        theirs = set(_all_failure_labels(other))
        for a in mine:
            for b in theirs:
                assert not a.startswith(b) and not b.startswith(a), (a, b)


def test_check_imports_2n_refuses_unpinned_and_covers_upstream(monkeypatch):
    monkeypatch.setattr(an, "IMPORTED_SHA256_2N", None)
    with pytest.raises(RuntimeError, match="not pinned"):
        an.check_imports_2n()
    monkeypatch.setattr(an, "IMPORTED_SHA256_2N", {})
    with pytest.raises(RuntimeError, match="unpinned module"):
        an.check_imports_2n()


def test_run_on_empty_tree_is_insufficient_never_raises(tmp_path):
    v = an.run(root_2n=tmp_path, root_2i=bi.EXP2I, root_2k=bk.EXP2K, n_perm=20, n_boot=5,
               referents_sha=False, imports_pinned=False, tag_exists=lambda t: True,
               blob_sha=lambda tag, rel: bg.sha256_file(bn.REPO / rel) if (bn.REPO / rel).is_file() else None,
               blobs_bound=lambda tag, paths, repo_root=None: [])
    assert v["verdict"] == "INSUFFICIENT_DATA" and v["tests"] is None and v["secondaries"] is None
    assert any("2n endpoint stage1_final" in f or "2n rung set" in f for f in v["referents"]["failures"])
    assert v["referents"]["pins_active"] == {"frozen_modules": True, "import_surface": False, "referent_manifest": False}
    assert v["known_inputs_caveat"] == an.KNOWN_INPUTS_CAVEAT_2N and v["model_contact"] == "none at analysis"
    assert v["calibration_note"] == an.CALIBRATION_SENTENCE_2N


# -------------------------------------------------------------- referents

def test_make_referents_2n_lists_2m_campaign_artifacts_and_2n_inputs(tmp_path, monkeypatch):
    files = mkr.referent_files()
    rel = {str(p.relative_to(bn.REPO)) for p in files}
    assert "experiments/exp2k/results/predictor_2k.json" in rel
    assert "experiments/exp2i/results/predictor/olmo1b/antonym.draws.jsonl.gz" in rel
    assert "experiments/exp2m/results/verdict.json" in rel
    assert "experiments/exp2m/results/endpoint/rung_set_2m.json" in rel
    assert "experiments/exp2m/results/endpoint/stage1_final/antonym.json" in rel
    assert "experiments/exp2m/results/sweep/smollm3_3b/step40000/antonym.json" in rel
    assert "experiments/exp2m/results/sweep/smollm3_3b/gate1.json" in rel
    for r in bm.INSTRUMENT_BLOBS_2M:
        assert r in rel
    assert "experiments/exp2n/checkpoints_2n.json" in rel and "experiments/exp2n/hub_inventory_comma.json" in rel
    assert "experiments/exp2n/power_2n.py" in rel
    assert len(files) == len(set(files))
    monkeypatch.setattr(mkr, "N_FILES_2N", None)
    p = tmp_path / "r.json"
    rec = mkr.build(p, n_files=len(files))
    assert rec["n_files"] == len(files)
    monkeypatch.setattr(mkr, "N_FILES_2N", len(files))
    assert mkr.check_referents(p, sha_pin=bg.sha256_file(p)) == []
    with pytest.raises(ValueError, match="hashes to"):
        mkr.check_referents(p, sha_pin="0" * 64)
