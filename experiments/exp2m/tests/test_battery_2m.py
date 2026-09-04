# experiments/exp2m/tests/test_battery_2m.py
"""battery_2m: constants, the grid and its log-head subset; the manifest
builder on a hand-built two-repo inventory (candidate rule on a
weightless `main`, duplicate refusal, pinned endpoint, the stage-3 and
base entries, the twin entry); load_manifest's sha pin; the rung-set
rule's partition on the real floors; paths incl. the twin's; the record
stamps incl. the dtype override; the gate-1 checkers on hand records;
the endpoint composite sha over 104 files; the loader family's pure
parts (clean dir writes config.json; the cache key; the tokenizer pins
on stubs); the pins and the prereg binding with fakes and in a real
temp git repo. No torch, no network."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import types
from pathlib import Path

import pytest

from experiments.exp2d import battery_2d as bt
from experiments.exp2g import battery_2g as bg
from experiments.exp2g import checkpoints_2g as ck
from experiments.exp2i import battery_2i as bi
from experiments.exp2k import battery_2k as bk
from experiments.exp2l import battery_2l as bl
from experiments.exp2m import battery_2m as bm


# ------------------------------------------------------------ constants

def test_constants_and_grid():
    assert bm.REPO_CKPT == "HuggingFaceTB/SmolLM3-3B-checkpoints"
    assert bm.REPO_BASE == "HuggingFaceTB/SmolLM3-3B-Base"
    assert bm.SIZE_OUT == "smollm3_3b" and bm.FAMILY == "smollm3"
    assert bm.REV_ENDPOINT_2M == "stage1-step-3440000" and bm.ENDPOINT_STEP_2M == 3440000
    assert bm.REV_STAGE3_FINAL_2M == "stage3-step-4720000" and bm.STAGE3_STEP_2M == 4720000
    assert bm.REV_BASE_2M == "main" and bm.REV_CKPT_MAIN == "main"
    assert bm.TOKENS_PER_STEP_2M == 2_359_296
    assert bm.TWIN == bi.TWIN == "twin" and bm.TWIN_SEED == 0
    assert bm.GRID_3B == (40000, 80000, 120000, 160000, 200000, 240000, 280000, 320000, 360000, 400000,
                          600000, 800000, 1000000, 1200000, 1400000, 1600000, 1800000, 2000000, 2200000,
                          2400000, 2600000, 2800000, 3000000, 3200000, 3400000, 3440000)
    assert len(bm.GRID_3B) == 26 and bm.trained_steps_3b() == bm.GRID_3B and bm.n_trained_3b() == 26
    assert bm.GRID_3B[-1] == bm.ENDPOINT_STEP_2M and bm.TWIN not in bm.GRID_3B
    assert all(s % 40000 == 0 for s in bm.GRID_3B)          # the branch's 40k lattice
    assert bm.LOG_HEAD_SUBSET_2M == (40000, 80000, 160000, 320000, 400000, 600000, 800000, 1000000,
                                     1200000, 1400000, 1600000, 1800000, 2000000, 2200000, 2400000,
                                     2600000, 2800000, 3000000, 3200000, 3400000, 3440000)
    assert len(bm.LOG_HEAD_SUBSET_2M) == 21 and set(bm.LOG_HEAD_SUBSET_2M) < set(bm.GRID_3B)
    assert bm.PREREG_TAG_2M == "exp2m-preregistered"
    assert bm.ENDPOINT_SEAL_TAG_2M == "exp2m-endpoint-sealed"
    assert bm.INSTRUMENT_BLOBS_2M == ("experiments/exp2m/analyze_2m.py",
                                      "experiments/exp2m/battery_2m.py",
                                      "experiments/exp2m/run/endpoint_2m.py",
                                      "experiments/exp2m/run/sweep_2m.py")
    assert bm.R_CAP_2K == bk.R_CAP_DESIGN and len(bm.R_CAP_2K) == 9
    assert set(bm.R_CAP_2K) < set(bm.STRATA_RUNGS) and len(bm.STRATA_RUNGS) == 11
    assert bm.BATCH_SIZE_2M == 16 and bm.DTYPE_2M == "float16"
    assert bm.N_ITEMS == 500
    assert bm.ENDPOINT_WHICH_2M == ("stage1_final", "stage3_final", "base")


def test_tokenizer_constants():
    assert bm.PAD_TOKEN_2M == "<|finetune_right_pad_id|>" and bm.PAD_TOKEN_ID_2M == 128004
    assert bm.EOS_TOKEN_ID_2M == 128001
    assert bm.BOS_TOKEN_2M == "<|begin_of_text|>" and bm.BOS_TOKEN_ID_2M == 128000
    assert bm.PAD_TOKEN_ID_2M != bi.PAD_TOKEN_ID                # not OLMo-2's pad


def test_seal_literals_match_the_committed_seals_and_2l():
    s2k = json.loads(bk.seal_path(bk.EXP2K).read_text())["sha256"]
    s2i = json.loads(bi.predictor_seal_path(bi.EXP2I).read_text())["sha256"]
    assert bm.SEAL_2K_SHA256 == s2k == bl.SEAL_2K_SHA256
    assert bm.SEAL_2I_SHA256 == s2i == bl.SEAL_2I_SHA256
    assert bm.PREDICTOR_SHA_2M == bm.predictor_sha_2m(s2k, s2i)
    assert bm.PREDICTOR_SHA_2M == hashlib.sha256(f"2m|{s2k}|{s2i}".encode()).hexdigest()
    assert bm.PREDICTOR_SHA_2M != bl.PREDICTOR_SHA_2L          # a 2l record can never pass as 2m's
    assert bm.PREDICTOR_TAGS_2M == "exp2k-predictor-sealed+exp2i-predictor-sealed"


# ------------------------------------------------------------- manifest

def _files(tag, n_shards=2, size=4_966_315_264):
    """A SmolLM3-like revision file table: 2 safetensors shards (+ the
    index is not LFS, so it is absent from the table as on the Hub)."""
    return {f"model-{i:05d}-of-{n_shards:05d}.safetensors": [f"{tag}{i:02d}" * 4, size]
            for i in range(1, n_shards + 1)}


def _inventory(*, dup_step=None, drop_endpoint=False, drop_stage3=False, drop_base=False,
               dup_stage3=False):
    table = {}
    for step in bm.GRID_3B:
        table[f"stage1-step-{step}"] = {"commit": f"c{step:07d}" + "0" * 32, "files": _files(f"s{step}")}
    table["stage1-step-1080000"] = {"commit": "n" * 40, "files": _files("nongrid")}   # a non-grid stage-1 point
    table["stage2-step-3480000"] = {"commit": "t" * 40, "files": _files("s2")}
    table[bm.REV_STAGE3_FINAL_2M] = {"commit": "u" * 40, "files": _files("s3end")}
    table["main"] = {"commit": "m" * 40, "files": {}}                               # weightless README branch
    if dup_step is not None:
        table["stage1-step-9999999"] = {"commit": "d" * 40, "files": dict(table[f"stage1-step-{dup_step}"]["files"])}
    if dup_stage3:
        table["stage3-step-9999999"] = {"commit": "e" * 40, "files": dict(table[bm.REV_STAGE3_FINAL_2M]["files"])}
    if drop_endpoint:
        del table[bm.REV_ENDPOINT_2M]
    if drop_stage3:
        del table[bm.REV_STAGE3_FINAL_2M]
    base = {"main": {"commit": "b" * 40, "files": _files("base")}}
    if drop_base:
        base = {}
    return {bm.REPO_CKPT: table, bm.REPO_BASE: base}


def test_build_manifest_3b_shape():
    m = bm.build_manifest_3b(_inventory())
    assert m["repo_ckpt"] == bm.REPO_CKPT and m["repo_base"] == bm.REPO_BASE
    assert m["grid_3b"] == list(bm.GRID_3B) and m["trained_steps_3b"] == list(bm.GRID_3B)
    assert m["log_head_subset"] == list(bm.LOG_HEAD_SUBSET_2M) and m["tokens_per_step"] == bm.TOKENS_PER_STEP_2M
    assert set(m["entries_3b"]) == {str(s) for s in bm.GRID_3B}
    e = m["entries_3b"][str(bm.ENDPOINT_STEP_2M)]
    assert e["repo"] == bm.REPO_CKPT and e["revision"] == bm.REV_ENDPOINT_2M and e["kind"] == "safetensors-shards"
    assert e["files"] == ["model-00001-of-00002.safetensors", "model-00002-of-00002.safetensors",
                          "model.safetensors.index.json"]
    assert len(e["lfs_sha256"]) == 2 and all(isinstance(v, int) for v in e["lfs_size"].values())
    t = m["twin"]
    assert t == {"repo": bm.REPO_CKPT, "revision": bm.TWIN, "commit": None, "files": [], "kind": "from_config",
                 "seed": bm.TWIN_SEED, "config_commit": e["commit"]}
    s3 = m["stage3_final"]
    assert s3["repo"] == bm.REPO_CKPT and s3["revision"] == bm.REV_STAGE3_FINAL_2M and s3["commit"] == "u" * 40
    b = m["base"]
    assert b["repo"] == bm.REPO_BASE and b["revision"] == "main" and b["commit"] == "b" * 40 and len(b["lfs_sha256"]) == 2
    assert m["endpoint_duplicates"] == []
    assert m["n_revisions"] == {bm.REPO_CKPT: len(_inventory()[bm.REPO_CKPT]), bm.REPO_BASE: 1}


def test_build_manifest_3b_refusals():
    with pytest.raises(ValueError, match="duplicate"):
        bm.build_manifest_3b(_inventory(dup_step=600000))
    with pytest.raises(ValueError, match="exactly one stage1 branch"):
        bm.build_manifest_3b(_inventory(drop_endpoint=True))
    with pytest.raises(ValueError, match="stage-3 endpoint"):
        bm.build_manifest_3b(_inventory(drop_stage3=True))
    with pytest.raises(ValueError, match="stage-3 endpoint.*duplicate"):
        bm.build_manifest_3b(_inventory(dup_stage3=True))
    with pytest.raises(ValueError, match="base"):
        bm.build_manifest_3b(_inventory(drop_base=True))
    inv = _inventory()
    wrong_rev = f"stage1-step-{bm.ENDPOINT_STEP_2M}"          # rename the endpoint branch off the literal
    inv[bm.REPO_CKPT]["stage1-step-03440000"] = inv[bm.REPO_CKPT].pop(wrong_rev)
    with pytest.raises(ValueError, match="exactly one stage1 branch|endpoint revision"):
        bm.build_manifest_3b(inv)


def test_build_manifest_3b_endpoint_may_duplicate_and_is_recorded():
    inv = _inventory()
    inv[bm.REPO_CKPT]["stage2-copy"] = {"commit": "e" * 40,
                                        "files": dict(inv[bm.REPO_CKPT][bm.REV_ENDPOINT_2M]["files"])}
    m = bm.build_manifest_3b(inv)
    assert m["endpoint_duplicates"] == ["stage2-copy"]


def test_candidate_rule_accepts_two_shard_naming_and_a_weightless_main():
    files = _files("x")
    c = ck.candidate("stage1-step-40000", files, {})
    assert c["kind"] == "safetensors-shards" and c["lfs"] == sorted(files)
    assert c["files"][-1] == "model.safetensors.index.json"
    assert ck.candidate("main", {}, {}) is None                 # the checkpoints repo's main carries no weights
    assert bm._STAGE1_RE_2M.fullmatch("stage1-step-40000").group(1) == "40000"
    assert bm._STAGE1_RE_2M.fullmatch("stage1-step40000") is None
    assert bm._STAGE1_RE_2M.fullmatch("stage2-step-3480000") is None


def test_load_manifest_3b_pins_sha_grid_and_subset(tmp_path):
    m = bm.build_manifest_3b(_inventory())
    p = tmp_path / "m.json"
    bm.write_manifest(p, m)
    sha = bg.sha256_file(p)
    got = bm.load_manifest_3b(p, sha_pin=sha)
    assert got["grid_3b"] == list(bm.GRID_3B)
    with pytest.raises(ValueError, match="hashes to"):
        bm.load_manifest_3b(p, sha_pin="0" * 64)
    for bad in (dict(m, grid_3b=[1, 2, 3]), dict(m, log_head_subset=[40000]),
                dict(m, twin=dict(m["twin"], kind="thin"))):
        bm.write_manifest(p, bad)
        with pytest.raises(ValueError, match="frozen SmolLM3 grid"):
            bm.load_manifest_3b(p, sha_pin=None)


def test_entry_accessors():
    m = bm.build_manifest_3b(_inventory())
    assert bm.entry_3b(m, 600000)["revision"] == "stage1-step-600000"
    assert bm.entry_3b(m, "600000")["revision"] == "stage1-step-600000"
    assert bm.entry_3b(m, bm.TWIN)["kind"] == "from_config"
    assert bm.entry_stage3_3b(m)["revision"] == bm.REV_STAGE3_FINAL_2M
    assert bm.entry_base_3b(m)["repo"] == bm.REPO_BASE
    assert bm.entry_which_3b(m, "stage1_final") == bm.entry_3b(m, bm.ENDPOINT_STEP_2M)
    assert bm.entry_which_3b(m, "stage3_final") == bm.entry_stage3_3b(m)
    assert bm.entry_which_3b(m, "base") == bm.entry_base_3b(m)
    with pytest.raises(ValueError, match="not a grid entry"):
        bm.entry_3b(m, 1080000)                                  # on the branch, not on the grid
    with pytest.raises(ValueError):
        bm.entry_which_3b(m, "main")


def test_committed_manifest_is_pinned_and_consistent():
    """Live after Step 4 of this task (the real scan + manifest)."""
    if bm.CHECKPOINTS_2M_SHA256 is None:
        pytest.skip("manifest not yet built/pinned (Task 1 Step 4)")
    m = bm.load_manifest_3b(bm.CHECKPOINTS_PATH, sha_pin=bm.CHECKPOINTS_2M_SHA256)
    assert bm.entry_3b(m, bm.ENDPOINT_STEP_2M)["revision"] == bm.REV_ENDPOINT_2M
    assert bm.entry_3b(m, bm.ENDPOINT_STEP_2M)["commit"] == "d07a5a83dd011f3f084e9d2f1b47f51e524ca8d4"
    for step in bm.GRID_3B:
        e = bm.entry_3b(m, step)
        assert e["repo"] == bm.REPO_CKPT and e["kind"] == "safetensors-shards" and len(e["lfs_sha256"]) == 2
    assert bm.entry_3b(m, bm.TWIN)["config_commit"] == bm.entry_3b(m, bm.ENDPOINT_STEP_2M)["commit"]
    assert bm.entry_stage3_3b(m)["kind"] == "safetensors-shards"
    assert bm.entry_base_3b(m)["kind"] == "safetensors-shards" and bm.entry_base_3b(m)["repo"] == bm.REPO_BASE
    assert m["endpoint_duplicates"] == []


# ---------------------------------------------------------------- paths

def test_paths(tmp_path):
    r = tmp_path
    assert bm.sweep_dir(r) == r / "results" / "sweep" / "smollm3_3b"
    assert bm.record_path(r, 600000, "antonym") == bm.sweep_dir(r) / "step600000" / "antonym.json"
    assert bm.record_path(r, bm.TWIN, "antonym") == bm.sweep_dir(r) / "twin" / "antonym.json"
    assert bm.checkpoint_record_path(r, "40000") == bm.sweep_dir(r) / "step40000" / "_checkpoint.json"
    assert bm.checkpoint_record_path(r, bm.TWIN) == bm.sweep_dir(r) / "twin" / "_checkpoint.json"
    assert bm.gate1_path(r) == bm.sweep_dir(r) / "gate1.json"
    assert bm.halt_marker_path(r) == bm.sweep_dir(r) / "HALTED"
    for which in bm.ENDPOINT_WHICH_2M:
        assert bm.endpoint_record_path(r, which, "odd6") == r / "results" / "endpoint" / which / "odd6.json"
    with pytest.raises(ValueError):
        bm.endpoint_record_path(r, "main", "odd6")
    assert bm.rung_set_path(r) == r / "results" / "endpoint" / "rung_set_2m.json"
    assert bm.power_path(r) == r / "results" / "endpoint" / "power_2m.json"


# ------------------------------------------------------------ rung set

def test_rung_set_from_counts_2m_partition_on_real_floors():
    floors = bg.load_floors()
    counts = {r: 0 for r in bt.RUNGS}
    for r in ("antonym", "add_base8", "sub3_mid"):
        counts[r] = 480
    counts["count_div13"] = 480
    counts["reverse_string"] = 480
    rs = bm.rung_set_from_counts_2m(counts, floors)
    assert rs["R_PRIMARY"] == ["add_base8", "antonym", "sub3_mid"]
    assert rs["R_ELEVEN_EXTRA"] == ["count_div13"] and rs["R_EXTRA"] == ["reverse_string"]
    assert set(rs["R_3B"]) == set(rs["R_PRIMARY"]) | set(rs["R_ELEVEN_EXTRA"]) | set(rs["R_EXTRA"])
    assert set(rs["per_rung"]) == set(bt.RUNGS)
    assert rs["per_rung"]["antonym"]["significant"] is True and rs["per_rung"]["odd6"]["significant"] is False
    assert rs["primary_is_the_nine"] is False
    counts2 = {r: (480 if r in bm.R_CAP_2K else 0) for r in bt.RUNGS}
    rs2 = bm.rung_set_from_counts_2m(counts2, floors)
    assert rs2["R_PRIMARY"] == sorted(bm.R_CAP_2K) and rs2["primary_is_the_nine"] is True


# --------------------------------------------------------- record stamps

def _cap(rung="antonym"):
    return bg.load_battery()[rung]


def _ev0(cap):
    return {"bits": [0] * bt.N_ITEMS, "correct": 0, "continuations": [" zzz"] * bt.N_ITEMS}


def test_item_record_2m_overrides_dtype_and_handles_the_twin(monkeypatch):
    cap = _cap()
    ckpt = {"revision": "stage1-step-40000", "commit": "c" * 40, "kind": "safetensors-shards",
            "files": ["a"], "weight_sha256": "D", "config_source": "cs", "tokenizer_source": "ts"}
    rec = bm.item_record_2m(rung="antonym", cap=cap, ev=_ev0(cap), ckpt=ckpt, step=40000,
                            endpoint_sha="E" * 64, t_s=1.0)
    assert rec["family"] == bm.FAMILY and rec["size"] == bm.SIZE_OUT and rec["step"] == 40000
    assert rec["seal_tag"] == bm.ENDPOINT_SEAL_TAG_2M and rec["predictor_sha"] == bm.PREDICTOR_SHA_2M
    assert rec["endpoint_sha256"] == "E" * 64 and rec["n"] == bt.N_ITEMS and "which" not in rec
    assert rec["dtype"] == bm.DTYPE_2M
    monkeypatch.setattr(bm, "DTYPE_2M", "float32")
    rec32 = bm.item_record_2m(rung="antonym", cap=cap, ev=_ev0(cap), ckpt=ckpt, step=40000,
                              endpoint_sha="E" * 64, t_s=1.0)
    assert rec32["dtype"] == "float32"                          # item_record_2i's literal is overridden
    twin_ckpt = {"revision": bm.TWIN, "commit": None, "kind": "from_config", "files": [], "weight_sha256": "T",
                 "config_source": f"{bm.REPO_CKPT}@{'c' * 40}", "tokenizer_source": f"{bm.REPO_CKPT}@{'c' * 40}"}
    rt = bm.item_record_2m(rung="antonym", cap=cap, ev=_ev0(cap), ckpt=twin_ckpt, step=bm.TWIN,
                           endpoint_sha="E" * 64, t_s=0.0)
    assert rt["step"] == bm.TWIN and rt["commit"] is None and rt["kind"] == "from_config"


def test_endpoint_item_record_2m_and_checkpoint_records():
    cap = _cap()
    ckpt = {"revision": bm.REV_ENDPOINT_2M, "commit": "c" * 40, "kind": "safetensors-shards",
            "files": ["a"], "weight_sha256": "D", "config_source": "cs", "tokenizer_source": "ts"}
    seal = {"tag": bm.PREDICTOR_TAGS_2M, "sha256": bm.PREDICTOR_SHA_2M}
    rec = bm.endpoint_item_record_2m(rung="antonym", cap=cap, ev=_ev0(cap), ckpt=ckpt, which="base", seal=seal, t_s=0.0)
    assert rec["which"] == "base" and "step" not in rec and rec["dtype"] == bm.DTYPE_2M
    assert rec["seal_tag"] == bm.PREDICTOR_TAGS_2M and rec["size"] == bm.SIZE_OUT
    info = {"repo": bm.REPO_CKPT, "sha256": {"a": "1"},
            "loading_info": {"missing_keys": 0, "unexpected_keys": 0, "mismatched_keys": 0}}
    cr = bm.checkpoint_record_2m(step=40000, ckpt=ckpt, info=info, seconds=12.34)
    assert cr == {"family": bm.FAMILY, "size": bm.SIZE_OUT, "step": 40000, "repo": bm.REPO_CKPT,
                  "revision": ckpt["revision"], "commit": ckpt["commit"], "sha256": {"a": "1"},
                  "loading_info": info["loading_info"], "digest": "D", "download_seconds": 12.3}
    tinfo = {"repo": bm.REPO_CKPT, "revision": bm.TWIN, "seed": 0, "config_source": f"{bm.REPO_CKPT}@{'c' * 40}",
             "tensor_digest": "T"}
    tr = bm.twin_checkpoint_record_2m(info=tinfo)
    assert tr == {"family": bm.FAMILY, "size": bm.SIZE_OUT, "step": bm.TWIN, "repo": bm.REPO_CKPT,
                  "revision": bm.TWIN, "commit": None, "kind": "from_config", "seed": 0, "digest": "T",
                  "config_source": f"{bm.REPO_CKPT}@{'c' * 40}"}


# ------------------------------------------------------ endpoint sha

def test_composite_sha_and_endpoint_sha256(tmp_path):
    files = {"b": "2", "a": "1"}
    assert bm.composite_sha(files) == hashlib.sha256("a 1\nb 2".encode()).hexdigest()
    for which in bm.ENDPOINT_WHICH_2M:
        for r in bt.RUNGS:
            p = bm.endpoint_record_path(tmp_path, which, r)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps({"rung": r, "which": which}))
    bm.rung_set_path(tmp_path).write_text("{}")
    bm.power_path(tmp_path).write_text("{}")
    files = bm.endpoint_files(tmp_path)
    assert len(files) == 104
    assert "results/endpoint/rung_set_2m.json" in files and "results/endpoint/power_2m.json" in files
    assert "results/endpoint/base/odd6.json" in files
    s1 = bm.endpoint_sha256(tmp_path)
    assert s1 == bm.composite_sha(files) and len(s1) == 64
    bm.power_path(tmp_path).write_text('{"x": 1}')
    assert bm.endpoint_sha256(tmp_path) != s1
    bm.endpoint_record_path(tmp_path, "stage3_final", "odd6").unlink()
    with pytest.raises(FileNotFoundError):
        bm.endpoint_files(tmp_path)
    bm.endpoint_record_path(tmp_path, "stage3_final", "odd6").mkdir(parents=True)
    with pytest.raises(FileNotFoundError):
        bm.endpoint_files(tmp_path)


# -------------------------------------------------------------- gate 1

def _gate_rec(**over):
    g = {"rungs": list(bt.RUNGS), "bit_diffs": {r: 0 for r in bt.RUNGS},
         "continuation_diffs": {r: 0 for r in bt.RUNGS},
         "continuations_compared": {r: bt.N_ITEMS for r in bt.RUNGS},
         "digest_sweep": "D", "digest_endpoint": "D", "commit_sweep": "c" * 40,
         "commit_endpoint": "c" * 40, "prereg_tag": bm.PREREG_TAG_2M}
    g.update(over)
    return g


def _endpoint_records(bits_by_rung=None):
    out = {}
    for r in bt.RUNGS:
        bits = (bits_by_rung or {}).get(r, [0] * bt.N_ITEMS)
        out[r] = {"bits": list(bits), "continuations": [" zzz" if not b else " ok" for b in bits]}
    return out


def test_gate1_failures_3b():
    ep = _endpoint_records()
    assert bm.gate1_failures_3b(_gate_rec(), ep) == []
    assert bm.GATE1_FIELDS_2M == ("rungs", "bit_diffs", "continuation_diffs", "continuations_compared",
                                  "digest_sweep", "digest_endpoint", "commit_sweep", "commit_endpoint",
                                  "prereg_tag")
    bad = bm.gate1_failures_3b(_gate_rec(bit_diffs={**{r: 0 for r in bt.RUNGS}, "odd6": 2}), ep)
    assert any("odd6" in b and "2 bit diffs" in b for b in bad)
    for n in (499, bt.N_ITEMS + 1):
        bad = bm.gate1_failures_3b(_gate_rec(continuations_compared={**{r: bt.N_ITEMS for r in bt.RUNGS}, "odd6": n}), ep)
        assert any(f"{n} continuation pairs" in b for b in bad)
    assert any("tensor digest" in b for b in bm.gate1_failures_3b(_gate_rec(digest_sweep="X"), ep))
    assert any("commit" in b for b in bm.gate1_failures_3b(_gate_rec(commit_sweep="0" * 40), ep))
    assert any("prereg_tag" in b for b in bm.gate1_failures_3b(_gate_rec(prereg_tag="exp2l-preregistered"), ep))
    assert any("34-rung" in b for b in bm.gate1_failures_3b(_gate_rec(rungs=list(bt.RUNGS)[:-1]), ep))
    ep2 = dict(ep)
    del ep2["odd6"]
    assert any("no stage1_final endpoint record" in b for b in bm.gate1_failures_3b(_gate_rec(), ep2))
    for b in bm.gate1_failures_3b(_gate_rec(digest_sweep="X"), ep):
        assert b.startswith("gate 1 smollm3_3b")


def test_gate1_rederive_3b():
    ep = _endpoint_records({"antonym": [1] * 10 + [0] * 490})
    sw = _endpoint_records({"antonym": [1] * 10 + [0] * 490})
    assert bm.gate1_rederive_3b(sw, ep, _gate_rec()) == []
    sw2 = _endpoint_records({"antonym": [1] * 11 + [0] * 489})
    bad = bm.gate1_rederive_3b(sw2, ep, _gate_rec())
    assert any("antonym" in b and "1 bit diff" in b for b in bad)
    assert any("attested bit_diffs 0 disagrees with the re-derived 1" in b for b in bad)
    g = _gate_rec(bit_diffs={**{r: 0 for r in bt.RUNGS}, "antonym": 1})
    assert any("attested bit_diffs 1 disagrees with the re-derived 0" in b for b in bm.gate1_rederive_3b(sw, ep, g))
    short = dict(sw)
    short["odd6"] = {"bits": [0] * 10, "continuations": [" zzz"] * 10}
    assert any("odd6" in b and "coverage failure" in b for b in bm.gate1_rederive_3b(short, ep, _gate_rec()))
    g2 = _gate_rec(continuations_compared={**{r: bt.N_ITEMS for r in bt.RUNGS}, "odd6": 400})
    assert any("odd6" in b and "400" in b for b in bm.gate1_rederive_3b(sw, ep, g2))
    over = dict(sw)
    over["odd6"] = {"bits": sw["odd6"]["bits"] + [0], "continuations": sw["odd6"]["continuations"]}
    bad2 = bm.gate1_rederive_3b(over, ep, _gate_rec())
    assert any("odd6" in b and "coverage failure" in b for b in bad2)
    assert all(b.startswith("gate 1 smollm3_3b re-derive") for b in bad + bad2)


# -------------------------------------------------------------- loaders

def test_cache_key_and_clean_dir_writes_config(tmp_path):
    d = bm._cache_dir_3b("stage1-step-40000", tmp_path)
    assert d == tmp_path / "smollm3_3b" / "stage1-step-40000"
    src = tmp_path / "raw" / "model-00001-of-00002.safetensors"
    src.parent.mkdir(parents=True)
    src.write_bytes(b"weights")

    class Cfg:
        def to_json_file(self, path):
            Path(path).write_text('{"eos_token_id": 128001}')

    clean = bm.clean_dir_3b("stage1-step-40000", tmp_path, {src.name: src}, config=Cfg())
    assert clean == d / "clean" and (clean / src.name).read_bytes() == b"weights"
    assert json.loads((clean / "config.json").read_text())["eos_token_id"] == 128001
    with pytest.raises(TypeError):
        bm.clean_dir_3b("stage1-step-40000", tmp_path, {src.name: src})       # config REQUIRED
    bm.free_checkpoint_3b("stage1-step-40000", tmp_path)
    assert not d.exists()
    assert bm.CKPT_CACHE_2M == Path.home() / "emergence-lab" / "ckpt_cache_2m"


class _Tok:
    """A tokenizer stub for check_tokenizer_2m: a plain render of 'Q:'
    starts with a regular id unless `bos` is set."""
    def __init__(self, *, side="left", pad=bm.PAD_TOKEN_ID_2M, eos=bm.EOS_TOKEN_ID_2M, bos=False):
        self.padding_side, self.pad_token_id, self.eos_token_id = side, pad, eos
        self.all_special_ids = [bm.BOS_TOKEN_ID_2M, bm.EOS_TOKEN_ID_2M, bm.PAD_TOKEN_ID_2M]
        self._bos = bos

    def __call__(self, text):
        ids = [48, 25]
        return {"input_ids": ([bm.BOS_TOKEN_ID_2M] + ids) if self._bos else ids}


def test_check_tokenizer_2m_on_stubs():
    bm.check_tokenizer_2m(_Tok())
    with pytest.raises(RuntimeError, match="padding_side"):
        bm.check_tokenizer_2m(_Tok(side="right"))
    with pytest.raises(RuntimeError, match="pad_token_id"):
        bm.check_tokenizer_2m(_Tok(pad=None))
    with pytest.raises(RuntimeError, match="pad_token_id"):
        bm.check_tokenizer_2m(_Tok(pad=bi.PAD_TOKEN_ID))
    with pytest.raises(RuntimeError, match="eos_token_id"):
        bm.check_tokenizer_2m(_Tok(eos=2))
    with pytest.raises(RuntimeError, match="prepended"):
        bm.check_tokenizer_2m(_Tok(bos=True))


class _LoadTok(_Tok):
    """`load_tokenizer_3b`'s stub, in SmolLM3's REAL shape: right padding
    and NO pad token declared, so both of the loader's own assignments
    are observable. Setting `pad_token` sets `pad_token_id`, as a real
    tokenizer does."""
    def __init__(self):
        super().__init__(side="right", pad=None)
        self.set_pad = None

    @property
    def pad_token(self):
        return self.set_pad

    @pad_token.setter
    def pad_token(self, value):
        self.set_pad = value
        if value == bm.PAD_TOKEN_2M:
            self.pad_token_id = bm.PAD_TOKEN_ID_2M


def test_load_tokenizer_3b_sets_left_padding_and_the_pad_token(monkeypatch):
    """Mutation closure (Task 5, #35): `load_tokenizer_3b`'s own two
    assignments — left padding (dial n) and the vocabulary's own pad
    token — plus its `check_tokenizer_2m` call. No network: `transformers`
    is replaced by a stub module for the duration, so nothing is
    downloaded and no real tokenizer is built."""
    tok = _LoadTok()
    seen = {}

    def _from_pretrained(repo, revision=None):
        seen["args"] = (repo, revision)
        return tok

    fake = types.ModuleType("transformers")
    fake.AutoTokenizer = types.SimpleNamespace(from_pretrained=_from_pretrained)
    monkeypatch.setitem(sys.modules, "transformers", fake)
    got = bm.load_tokenizer_3b(bm.REPO_CKPT, "c" * 40)
    assert got is tok and seen["args"] == (bm.REPO_CKPT, "c" * 40)
    assert tok.padding_side == "left"
    assert tok.set_pad == bm.PAD_TOKEN_2M and tok.pad_token_id == bm.PAD_TOKEN_ID_2M


def test_loader_family_imports_torch_lazily():
    import ast
    src = (bm.EXP2M / "battery_2m.py").read_text()
    tree = ast.parse(src)
    top = [n for n in tree.body if isinstance(n, (ast.Import, ast.ImportFrom))]
    names = {a.name.split(".")[0] for n in top for a in n.names} | \
            {n.module.split(".")[0] for n in top if isinstance(n, ast.ImportFrom) and n.module}
    assert not names & {"torch", "transformers", "huggingface_hub"}


# ---------------------------------------------------------------- pins

def test_frozen_files_2m_list():
    assert set(bl.FROZEN_SHA256_2L) <= set(bm.FROZEN_FILES_2M)
    for rel in bl.INSTRUMENT_BLOBS_2L:
        assert (bm.REPO / rel) in bm.FROZEN_FILES_2M                # 2l's tag-bound blobs are frozen bytes to 2m
    assert (bm.EXP2M / "power_2m.py") in bm.FROZEN_FILES_2M
    assert (bm.EXP2M / "make_referents_2m.py") in bm.FROZEN_FILES_2M
    for rel in bm.INSTRUMENT_BLOBS_2M:
        assert (bm.REPO / rel) not in bm.FROZEN_FILES_2M            # tag-bound, never sha-pinned
    assert len(bm.FROZEN_FILES_2M) == len(set(bm.FROZEN_FILES_2M))


def test_check_frozen_2m_refuses_unpinned_and_drift(monkeypatch, tmp_path):
    monkeypatch.setattr(bm, "FROZEN_SHA256_2M", {})
    with pytest.raises(RuntimeError, match="not pinned"):
        bm.check_frozen_2m()
    p = tmp_path / "f.py"
    p.write_text("x = 1\n")
    monkeypatch.setattr(bm, "FROZEN_SHA256_2M", {p: bg.sha256_file(p)})
    bm.check_frozen_2m()
    p.write_text("x = 2\n")
    with pytest.raises(RuntimeError, match="drifted"):
        bm.check_frozen_2m()


def test_frozen_from_disk_strict_raises_on_missing(monkeypatch, tmp_path):
    monkeypatch.setattr(bm, "FROZEN_FILES_2M", (tmp_path / "missing.py",))
    with pytest.raises(FileNotFoundError):
        bm.frozen_from_disk()
    assert bm.frozen_from_disk(strict=False) == {}


def test_require_prereg_2m_with_fakes(monkeypatch):
    with pytest.raises(RuntimeError, match="does not exist"):
        bm.require_prereg_2m(tag_exists=lambda t: False, blob_sha=lambda t, r: None)
    present = tuple(r for r in bm.INSTRUMENT_BLOBS_2M if (bm.REPO / r).is_file())
    monkeypatch.setattr(bm, "INSTRUMENT_BLOBS_2M", present)
    ok = bm.require_prereg_2m(tag_exists=lambda t: t == bm.PREREG_TAG_2M,
                              blob_sha=lambda t, r: bg.sha256_file(bm.REPO / r))
    assert ok["tag"] == bm.PREREG_TAG_2M and set(ok["instrument_blobs"]) == set(present)
    with pytest.raises(RuntimeError, match="does not bind"):
        bm.require_prereg_2m(tag_exists=lambda t: True, blob_sha=lambda t, r: "0" * 64)


def _git(repo, *args):
    return subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, check=True)


def test_require_prereg_2m_binds_the_instrument_in_a_real_git_repo(tmp_path, monkeypatch):
    """2h F-3's lineage: the prereg tag must bind the INSTRUMENT, not a
    name. Real `git init`, a real annotated tag over the instrument
    blobs present on disk, `git show <tag>:<path>` as the comparison —
    then a post-tag edit to `battery_2m.py` is refused."""
    present = tuple(r for r in bm.INSTRUMENT_BLOBS_2M if (bm.REPO / r).is_file())
    monkeypatch.setattr(bm, "INSTRUMENT_BLOBS_2M", present)
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "freeze@example.invalid")
    _git(repo, "config", "user.name", "freeze")
    for rel in present:
        dst = repo / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes((bm.REPO / rel).read_bytes())
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "instrument")
    _git(repo, "tag", "-a", bm.PREREG_TAG_2M, "-m", "freeze probe")

    def tag_exists(tag):
        return tag in _git(repo, "tag", "--list", tag).stdout.split()

    def blob_sha(tag, rel):
        out = subprocess.run(["git", "show", f"{tag}:{rel}"], cwd=repo, capture_output=True)
        return None if out.returncode else hashlib.sha256(out.stdout).hexdigest()

    monkeypatch.setattr(bm, "REPO", repo)
    got = bm.require_prereg_2m(tag_exists=tag_exists, blob_sha=blob_sha)
    assert set(got["instrument_blobs"]) == set(present)
    bat = repo / "experiments/exp2m/battery_2m.py"
    bat.write_bytes(bat.read_bytes() + b"\n# a post-tag edit\n")
    with pytest.raises(RuntimeError, match="does not bind experiments/exp2m/battery_2m.py"):
        bm.require_prereg_2m(tag_exists=tag_exists, blob_sha=blob_sha)
