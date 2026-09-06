# experiments/exp2n/tests/test_battery_2n.py
"""battery_2n: constants, the grid and its every-40k control; the
manifest builder on a hand-built ONE-repo inventory (candidate rule on
a WEIGHT-BEARING `main`, duplicate refusal against every scanned
revision incl. `main`, pinned endpoint, the stage-2 and main entries,
the twin entry); load_manifest's sha pin; the rung-set rule's partition
on the real floors; paths incl. the twin's; the record stamps incl. the
dtype override and the render/eos_stop_id pins; the gate-1 checkers on
hand records; the endpoint composite sha over 104 files; the loader
family's pure parts (clean dir writes config.json; the cache key; the
tokenizer pins on stubs — Comma's declared pad, the BOS render, the
EOS stop-id override); the pins and the prereg binding with fakes and
in a real temp git repo. No torch, no network."""
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
from experiments.exp2m import battery_2m as bm
from experiments.exp2n import battery_2n as bn


# ------------------------------------------------------------ constants

def test_constants_and_grid():
    assert bn.REPO_COMMA == "common-pile/comma-v0.1-1t"
    assert bn.SIZE_OUT == "comma_7b" and bn.FAMILY == "comma"
    assert bn.REV_ENDPOINT_2N == "stage1-step460000-tokens965B" and bn.ENDPOINT_STEP_2N == 460000
    assert bn.REV_STAGE2_FINAL_2N == "stage2-step018000-tokens1002B" and bn.STAGE2_STEP_2N == 18000
    assert bn.REV_MAIN_2N == "main"
    assert bn.TOKENS_PER_STEP_2N == 2_097_152
    assert bn.TWIN == bi.TWIN == "twin" and bn.TWIN_SEED == 0
    assert bn.GRID_COMMA == (10000, 20000, 40000, 60000, 80000, 100000, 120000, 140000, 160000, 180000,
                             200000, 220000, 240000, 260000, 280000, 300000, 320000, 340000, 360000, 380000,
                             400000, 420000, 440000, 460000)
    assert len(bn.GRID_COMMA) == 24 and bn.trained_steps_comma() == bn.GRID_COMMA and bn.n_trained_comma() == 24
    assert bn.GRID_COMMA[-1] == bn.ENDPOINT_STEP_2N and bn.TWIN not in bn.GRID_COMMA
    assert bn.GRID_COMMA[0] == 10000
    assert all(s % 10000 == 0 for s in bn.GRID_COMMA)          # the branch's 10k lattice
    assert bn.EVERY40K_SUBSET_2N == (40000, 80000, 120000, 160000, 200000, 240000, 280000, 320000, 360000,
                                     400000, 440000, 460000)
    assert len(bn.EVERY40K_SUBSET_2N) == 12 and set(bn.EVERY40K_SUBSET_2N) < set(bn.GRID_COMMA)
    assert bn.PREREG_TAG_2N == "exp2n-preregistered"
    assert bn.ENDPOINT_SEAL_TAG_2N == "exp2n-endpoint-sealed"
    assert bn.INSTRUMENT_BLOBS_2N == ("experiments/exp2n/analyze_2n.py",
                                      "experiments/exp2n/battery_2n.py",
                                      "experiments/exp2n/run/endpoint_2n.py",
                                      "experiments/exp2n/run/sweep_2n.py")
    assert bn.R_CAP_2K == bk.R_CAP_DESIGN and len(bn.R_CAP_2K) == 9
    assert set(bn.R_CAP_2K) < set(bn.STRATA_RUNGS) and len(bn.STRATA_RUNGS) == 11
    assert bn.BATCH_SIZE_2N == 16 and bn.DTYPE_2N == "float16"
    assert bn.N_ITEMS == 500
    assert bn.ENDPOINT_WHICH_2N == ("stage1_final", "stage2_final", "main")


def test_tokenizer_constants():
    assert bn.PAD_TOKEN_2N == "<pad>" and bn.PAD_TOKEN_ID_2N == 0
    assert bn.UNK_TOKEN_ID_2N == 1
    assert bn.BOS_TOKEN_2N == "<|begin_of_text|>" and bn.BOS_TOKEN_ID_2N == 2
    assert bn.EOS_TOKEN_2N == "<|end_of_text|>" and bn.EOS_TOKEN_ID_2N == 3
    assert bn.EOS_STOP_ID_2N == 3 and bn.CONFIG_EOS_TOKEN_ID_2N == 2
    assert bn.RENDER_2N == "bos"
    assert bn.VOCAB_LEN_2N == 64000 and bn.CONFIG_VOCAB_2N == 64256
    assert bn.PAD_TOKEN_ID_2N != bi.PAD_TOKEN_ID                # not OLMo-2's pad


def test_seal_literals_match_the_committed_seals_and_2m():
    s2k = json.loads(bk.seal_path(bk.EXP2K).read_text())["sha256"]
    s2i = json.loads(bi.predictor_seal_path(bi.EXP2I).read_text())["sha256"]
    assert bn.SEAL_2K_SHA256 == s2k == bm.SEAL_2K_SHA256
    assert bn.SEAL_2I_SHA256 == s2i == bm.SEAL_2I_SHA256
    assert bn.PREDICTOR_SHA_2N == bn.predictor_sha_2n(s2k, s2i)
    assert bn.PREDICTOR_SHA_2N == hashlib.sha256(f"2n|{s2k}|{s2i}".encode()).hexdigest()
    assert bn.PREDICTOR_SHA_2N != bm.PREDICTOR_SHA_2M           # a 2m record can never pass as 2n's
    assert bn.PREDICTOR_TAGS_2N == "exp2k-predictor-sealed+exp2i-predictor-sealed"


# ------------------------------------------------------------- manifest

def _files(tag, n_shards=3, size=4_670_000_000):
    """A Comma-like revision file table: 3 safetensors shards (+ the
    index is not LFS, so it is absent from the table as on the Hub)."""
    return {f"model-{i:05d}-of-{n_shards:05d}.safetensors": [f"{tag}{i:02d}" * 4, size]
            for i in range(1, n_shards + 1)}


def _stage1_tokens(step):
    return round(step * bn.TOKENS_PER_STEP_2N / 10 ** 9)


def _stage1_rev(step):
    return f"stage1-step{step:06d}-tokens{_stage1_tokens(step)}B"


def _stage2_tokens(step):
    # linear between the two published endpoints (969B @ 2000, 1002B @
    # 18000) — a fixture convenience; only the step018000 literal is
    # ever asserted against REV_STAGE2_FINAL_2N.
    return round(969 + 33 * (step - 2000) / 16000)


def _stage2_rev(step):
    return f"stage2-step{step:06d}-tokens{_stage2_tokens(step)}B"


def _inventory(*, dup_step=None, drop_endpoint=False, drop_stage2=False, drop_main=False,
               dup_stage2=False):
    table = {}
    for step in range(10000, 460001, 10000):
        table[_stage1_rev(step)] = {"commit": f"c{step:07d}" + "0" * 32, "files": _files(f"s{step}")}
    for step in range(2000, 18001, 2000):
        table[_stage2_rev(step)] = {"commit": f"t{step:07d}" + "0" * 32, "files": _files(f"s2_{step}")}
    table[bn.REV_MAIN_2N] = {"commit": "5af409118da3cbea94684c622c66ab8c2ea7f4fe", "files": _files("main")}
    if dup_step is not None:
        table["stage1-step999999-tokens999B"] = {"commit": "d" * 40,
            "files": dict(table[_stage1_rev(dup_step)]["files"])}
    if dup_stage2:
        table["stage2-step099999-tokens999B"] = {"commit": "e" * 40,
            "files": dict(table[bn.REV_STAGE2_FINAL_2N]["files"])}
    if drop_endpoint:
        del table[bn.REV_ENDPOINT_2N]
    if drop_stage2:
        del table[bn.REV_STAGE2_FINAL_2N]
    if drop_main:
        del table[bn.REV_MAIN_2N]
    return {bn.REPO_COMMA: table}


def test_build_manifest_comma_shape():
    m = bn.build_manifest_comma(_inventory())
    assert m["repo"] == bn.REPO_COMMA
    assert m["grid_comma"] == list(bn.GRID_COMMA) and m["trained_steps_comma"] == list(bn.GRID_COMMA)
    assert m["every40k_subset"] == list(bn.EVERY40K_SUBSET_2N) and m["tokens_per_step"] == bn.TOKENS_PER_STEP_2N
    assert set(m["entries_comma"]) == {str(s) for s in bn.GRID_COMMA}
    e = m["entries_comma"][str(bn.ENDPOINT_STEP_2N)]
    assert e["repo"] == bn.REPO_COMMA and e["revision"] == bn.REV_ENDPOINT_2N and e["kind"] == "safetensors-shards"
    assert e["files"] == ["model-00001-of-00003.safetensors", "model-00002-of-00003.safetensors",
                          "model-00003-of-00003.safetensors", "model.safetensors.index.json"]
    assert len(e["lfs_sha256"]) == 3 and all(isinstance(v, int) for v in e["lfs_size"].values())
    t = m["twin"]
    assert t == {"repo": bn.REPO_COMMA, "revision": bn.TWIN, "commit": None, "files": [], "kind": "from_config",
                 "seed": bn.TWIN_SEED, "config_commit": e["commit"]}
    s2 = m["stage2_final"]
    assert s2["repo"] == bn.REPO_COMMA and s2["revision"] == bn.REV_STAGE2_FINAL_2N and len(s2["lfs_sha256"]) == 3
    main = m["main"]
    assert main["repo"] == bn.REPO_COMMA and main["revision"] == bn.REV_MAIN_2N and len(main["lfs_sha256"]) == 3
    assert m["endpoint_duplicates"] == []
    assert m["n_revisions"] == len(_inventory()[bn.REPO_COMMA])


def test_build_manifest_comma_refusals():
    with pytest.raises(ValueError, match="duplicate"):
        bn.build_manifest_comma(_inventory(dup_step=80000))
    with pytest.raises(ValueError, match="exactly one stage1 branch"):
        bn.build_manifest_comma(_inventory(drop_endpoint=True))
    with pytest.raises(ValueError, match="stage2_final"):
        bn.build_manifest_comma(_inventory(drop_stage2=True))
    with pytest.raises(ValueError, match="stage2_final.*duplicate"):
        bn.build_manifest_comma(_inventory(dup_stage2=True))
    with pytest.raises(KeyError):
        # `main_files = table[REV_MAIN_2N]["files"]` is dereferenced before
        # any refusal path in build_manifest_comma (production never drops
        # main — it is the ONE repo's default branch, always present).
        bn.build_manifest_comma(_inventory(drop_main=True))
    inv = _inventory()
    bad_rev = bn.REV_ENDPOINT_2N.replace("965B", "999B")          # same step, wrong tokens label
    inv[bn.REPO_COMMA][bad_rev] = inv[bn.REPO_COMMA].pop(bn.REV_ENDPOINT_2N)
    with pytest.raises(ValueError, match="endpoint revision"):
        bn.build_manifest_comma(inv)


def test_build_manifest_comma_endpoint_may_duplicate_and_is_recorded():
    inv = _inventory()
    inv[bn.REPO_COMMA]["stage1-step-endpoint-copy"] = {"commit": "e" * 40,
        "files": dict(inv[bn.REPO_COMMA][bn.REV_ENDPOINT_2N]["files"])}
    m = bn.build_manifest_comma(inv)
    assert m["endpoint_duplicates"] == ["stage1-step-endpoint-copy"]


def test_candidate_rule_accepts_three_shard_naming_and_a_weight_bearing_main():
    files = _files("x")
    c = ck.candidate("stage1-step010000-tokens21B", files, {})
    assert c["kind"] == "safetensors-shards" and c["lfs"] == sorted(files)
    assert c["files"][-1] == "model.safetensors.index.json"
    main_files = _files("main")
    cm = ck.candidate(bn.REV_MAIN_2N, main_files, main_files)     # main carries its OWN weights
    assert cm["kind"] == "safetensors-shards" and cm["lfs"] == sorted(main_files)
    assert bn._STAGE1_RE_2N.fullmatch("stage1-step010000-tokens21B").group(1) == "010000"
    assert bn._STAGE1_RE_2N.fullmatch("stage1-step10000-tokens21B") is None       # not 6 digits
    assert bn._STAGE1_RE_2N.fullmatch("stage2-step002000-tokens969B") is None


def test_load_manifest_comma_pins_sha_grid_and_subset(tmp_path):
    m = bn.build_manifest_comma(_inventory())
    p = tmp_path / "m.json"
    bn.write_manifest(p, m)
    sha = bg.sha256_file(p)
    got = bn.load_manifest_comma(p, sha_pin=sha)
    assert got["grid_comma"] == list(bn.GRID_COMMA)
    with pytest.raises(ValueError, match="hashes to"):
        bn.load_manifest_comma(p, sha_pin="0" * 64)
    for bad in (dict(m, grid_comma=[1, 2, 3]), dict(m, every40k_subset=[40000]),
                dict(m, twin=dict(m["twin"], kind="thin"))):
        bn.write_manifest(p, bad)
        with pytest.raises(ValueError, match="frozen Comma grid"):
            bn.load_manifest_comma(p, sha_pin=None)


def test_entry_accessors():
    m = bn.build_manifest_comma(_inventory())
    assert bn.entry_comma(m, 80000)["revision"] == _stage1_rev(80000)
    assert bn.entry_comma(m, "80000")["revision"] == _stage1_rev(80000)
    assert bn.entry_comma(m, bn.TWIN)["kind"] == "from_config"
    assert bn.entry_stage2_comma(m)["revision"] == bn.REV_STAGE2_FINAL_2N
    assert bn.entry_main_comma(m)["revision"] == bn.REV_MAIN_2N
    assert bn.entry_which_comma(m, "stage1_final") == bn.entry_comma(m, bn.ENDPOINT_STEP_2N)
    assert bn.entry_which_comma(m, "stage2_final") == bn.entry_stage2_comma(m)
    assert bn.entry_which_comma(m, "main") == bn.entry_main_comma(m)
    with pytest.raises(ValueError, match="not a grid entry"):
        bn.entry_comma(m, 30000)                                  # on the branch, not on the grid
    with pytest.raises(ValueError):
        bn.entry_which_comma(m, "base")


def test_committed_manifest_is_pinned_and_consistent():
    """Live after Step 5 of this task (the real scan + manifest)."""
    if not bn.CHECKPOINTS_2N_SHA256:
        pytest.skip("manifest not yet built/pinned (Task 1 Step 5)")
    m = bn.load_manifest_comma(bn.CHECKPOINTS_PATH, sha_pin=bn.CHECKPOINTS_2N_SHA256)
    assert bn.entry_comma(m, bn.ENDPOINT_STEP_2N)["revision"] == bn.REV_ENDPOINT_2N
    assert bn.entry_comma(m, bn.ENDPOINT_STEP_2N)["commit"] == "e295235994f32d763c359d324265a176e591f632"
    for step in bn.GRID_COMMA:
        e = bn.entry_comma(m, step)
        assert e["repo"] == bn.REPO_COMMA and e["kind"] == "safetensors-shards" and len(e["lfs_sha256"]) == 3
    assert bn.entry_comma(m, bn.TWIN)["config_commit"] == bn.entry_comma(m, bn.ENDPOINT_STEP_2N)["commit"]
    assert bn.entry_stage2_comma(m)["kind"] == "safetensors-shards"
    assert bn.entry_stage2_comma(m)["commit"] == "0d77335ff4b7219b1766ceb7103d4f2d780fccad"
    assert bn.entry_main_comma(m)["kind"] == "safetensors-shards"
    assert bn.entry_main_comma(m)["commit"] == "5af409118da3cbea94684c622c66ab8c2ea7f4fe"
    assert m["endpoint_duplicates"] == []


# ---------------------------------------------------------------- paths

def test_paths(tmp_path):
    r = tmp_path
    assert bn.sweep_dir(r) == r / "results" / "sweep" / "comma_7b"
    assert bn.record_path(r, 80000, "antonym") == bn.sweep_dir(r) / "step80000" / "antonym.json"
    assert bn.record_path(r, bn.TWIN, "antonym") == bn.sweep_dir(r) / "twin" / "antonym.json"
    assert bn.checkpoint_record_path(r, "40000") == bn.sweep_dir(r) / "step40000" / "_checkpoint.json"
    assert bn.checkpoint_record_path(r, bn.TWIN) == bn.sweep_dir(r) / "twin" / "_checkpoint.json"
    assert bn.gate1_path(r) == bn.sweep_dir(r) / "gate1.json"
    assert bn.halt_marker_path(r) == bn.sweep_dir(r) / "HALTED"
    for which in bn.ENDPOINT_WHICH_2N:
        assert bn.endpoint_record_path(r, which, "odd6") == r / "results" / "endpoint" / which / "odd6.json"
    with pytest.raises(ValueError):
        bn.endpoint_record_path(r, "stage3_final", "odd6")        # 2m's name, not a 2n which
    assert bn.rung_set_path(r) == r / "results" / "endpoint" / "rung_set_2n.json"
    assert bn.power_path(r) == r / "results" / "endpoint" / "power_2n.json"


# ------------------------------------------------------------ rung set

def test_rung_set_from_counts_2n_partition_on_real_floors():
    floors = bg.load_floors()
    counts = {r: 0 for r in bt.RUNGS}
    for r in ("antonym", "add_base8", "sub3_mid"):
        counts[r] = 480
    counts["count_div13"] = 480
    counts["reverse_string"] = 480
    rs = bn.rung_set_from_counts_2n(counts, floors)
    assert rs["R_PRIMARY"] == ["add_base8", "antonym", "sub3_mid"]
    assert rs["R_ELEVEN_EXTRA"] == ["count_div13"] and rs["R_EXTRA"] == ["reverse_string"]
    assert set(rs["R_COMMA"]) == set(rs["R_PRIMARY"]) | set(rs["R_ELEVEN_EXTRA"]) | set(rs["R_EXTRA"])
    assert set(rs["per_rung"]) == set(bt.RUNGS)
    assert rs["per_rung"]["antonym"]["significant"] is True and rs["per_rung"]["odd6"]["significant"] is False
    assert rs["primary_is_the_nine"] is False
    counts2 = {r: (480 if r in bn.R_CAP_2K else 0) for r in bt.RUNGS}
    rs2 = bn.rung_set_from_counts_2n(counts2, floors)
    assert rs2["R_PRIMARY"] == sorted(bn.R_CAP_2K) and rs2["primary_is_the_nine"] is True


# --------------------------------------------------------- record stamps

def _cap(rung="antonym"):
    return bg.load_battery()[rung]


def _ev0(cap):
    return {"bits": [0] * bt.N_ITEMS, "correct": 0, "continuations": [" zzz"] * bt.N_ITEMS}


def test_item_record_2n_overrides_dtype_and_handles_the_twin(monkeypatch):
    cap = _cap()
    ckpt = {"revision": "stage1-step040000-tokens84B", "commit": "c" * 40, "kind": "safetensors-shards",
            "files": ["a"], "weight_sha256": "D", "config_source": "cs", "tokenizer_source": "ts"}
    rec = bn.item_record_2n(rung="antonym", cap=cap, ev=_ev0(cap), ckpt=ckpt, step=40000,
                            endpoint_sha="E" * 64, t_s=1.0)
    assert rec["family"] == bn.FAMILY and rec["size"] == bn.SIZE_OUT and rec["step"] == 40000
    assert rec["seal_tag"] == bn.ENDPOINT_SEAL_TAG_2N and rec["predictor_sha"] == bn.PREDICTOR_SHA_2N
    assert rec["endpoint_sha256"] == "E" * 64 and rec["n"] == bt.N_ITEMS and "which" not in rec
    assert rec["dtype"] == bn.DTYPE_2N
    assert rec["render"] == bn.RENDER_2N and rec["eos_stop_id"] == bn.EOS_STOP_ID_2N
    monkeypatch.setattr(bn, "DTYPE_2N", "float32")
    rec32 = bn.item_record_2n(rung="antonym", cap=cap, ev=_ev0(cap), ckpt=ckpt, step=40000,
                              endpoint_sha="E" * 64, t_s=1.0)
    assert rec32["dtype"] == "float32"                          # item_record_2i's literal is overridden
    twin_ckpt = {"revision": bn.TWIN, "commit": None, "kind": "from_config", "files": [], "weight_sha256": "T",
                 "config_source": f"{bn.REPO_COMMA}@{'c' * 40}", "tokenizer_source": f"{bn.REPO_COMMA}@{'c' * 40}"}
    rt = bn.item_record_2n(rung="antonym", cap=cap, ev=_ev0(cap), ckpt=twin_ckpt, step=bn.TWIN,
                           endpoint_sha="E" * 64, t_s=0.0)
    assert rt["step"] == bn.TWIN and rt["commit"] is None and rt["kind"] == "from_config"
    assert rt["render"] == bn.RENDER_2N and rt["eos_stop_id"] == bn.EOS_STOP_ID_2N


def test_endpoint_item_record_2n_and_checkpoint_records():
    cap = _cap()
    ckpt = {"revision": bn.REV_ENDPOINT_2N, "commit": "c" * 40, "kind": "safetensors-shards",
            "files": ["a"], "weight_sha256": "D", "config_source": "cs", "tokenizer_source": "ts"}
    seal = {"tag": bn.PREDICTOR_TAGS_2N, "sha256": bn.PREDICTOR_SHA_2N}
    rec = bn.endpoint_item_record_2n(rung="antonym", cap=cap, ev=_ev0(cap), ckpt=ckpt, which="main",
                                     seal=seal, t_s=0.0)
    assert rec["which"] == "main" and "step" not in rec and rec["dtype"] == bn.DTYPE_2N
    assert rec["seal_tag"] == bn.PREDICTOR_TAGS_2N and rec["size"] == bn.SIZE_OUT
    assert rec["render"] == bn.RENDER_2N and rec["eos_stop_id"] == bn.EOS_STOP_ID_2N
    info = {"repo": bn.REPO_COMMA, "sha256": {"a": "1"},
            "loading_info": {"missing_keys": 0, "unexpected_keys": 0, "mismatched_keys": 0},
            "config_eos_token_id": 2, "generation_eos_token_id": 3}
    cr = bn.checkpoint_record_2n(step=40000, ckpt=ckpt, info=info, seconds=12.34)
    assert cr == {"family": bn.FAMILY, "size": bn.SIZE_OUT, "step": 40000, "repo": bn.REPO_COMMA,
                  "revision": ckpt["revision"], "commit": ckpt["commit"], "sha256": {"a": "1"},
                  "loading_info": info["loading_info"], "digest": "D", "download_seconds": 12.3,
                  "config_eos_token_id": 2, "generation_eos_token_id": 3}
    tinfo = {"repo": bn.REPO_COMMA, "revision": bn.TWIN, "seed": 0, "config_source": f"{bn.REPO_COMMA}@{'c' * 40}",
             "tensor_digest": "T", "config_eos_token_id": 2, "generation_eos_token_id": 3}
    tr = bn.twin_checkpoint_record_2n(info=tinfo)
    assert tr == {"family": bn.FAMILY, "size": bn.SIZE_OUT, "step": bn.TWIN, "repo": bn.REPO_COMMA,
                  "revision": bn.TWIN, "commit": None, "kind": "from_config", "seed": 0, "digest": "T",
                  "config_source": f"{bn.REPO_COMMA}@{'c' * 40}",
                  "config_eos_token_id": 2, "generation_eos_token_id": 3}


# ------------------------------------------------------ endpoint sha

def test_composite_sha_and_endpoint_sha256(tmp_path):
    files = {"b": "2", "a": "1"}
    assert bn.composite_sha(files) == hashlib.sha256("a 1\nb 2".encode()).hexdigest()
    for which in bn.ENDPOINT_WHICH_2N:
        for r in bt.RUNGS:
            p = bn.endpoint_record_path(tmp_path, which, r)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps({"rung": r, "which": which}))
    bn.rung_set_path(tmp_path).write_text("{}")
    bn.power_path(tmp_path).write_text("{}")
    files = bn.endpoint_files(tmp_path)
    assert len(files) == 104
    assert "results/endpoint/rung_set_2n.json" in files and "results/endpoint/power_2n.json" in files
    assert "results/endpoint/main/odd6.json" in files
    s1 = bn.endpoint_sha256(tmp_path)
    assert s1 == bn.composite_sha(files) and len(s1) == 64
    bn.power_path(tmp_path).write_text('{"x": 1}')
    assert bn.endpoint_sha256(tmp_path) != s1
    bn.endpoint_record_path(tmp_path, "stage2_final", "odd6").unlink()
    with pytest.raises(FileNotFoundError):
        bn.endpoint_files(tmp_path)
    bn.endpoint_record_path(tmp_path, "stage2_final", "odd6").mkdir(parents=True)
    with pytest.raises(FileNotFoundError):
        bn.endpoint_files(tmp_path)


# -------------------------------------------------------------- gate 1

def _gate_rec(**over):
    g = {"rungs": list(bt.RUNGS), "bit_diffs": {r: 0 for r in bt.RUNGS},
         "continuation_diffs": {r: 0 for r in bt.RUNGS},
         "continuations_compared": {r: bt.N_ITEMS for r in bt.RUNGS},
         "digest_sweep": "D", "digest_endpoint": "D", "commit_sweep": "c" * 40,
         "commit_endpoint": "c" * 40, "prereg_tag": bn.PREREG_TAG_2N}
    g.update(over)
    return g


def _endpoint_records(bits_by_rung=None, *, digest="D", commit="c" * 40, odd_rung=None,
                      odd_digest="OTHER", odd_commit=None):
    """Freeze F-2 (2m's lineage): a real endpoint record carries
    `weight_sha256` and `commit`, and gate 1 measures both across all
    34 — the fixture carries them. `odd_rung` gives one rung a
    different digest/commit."""
    out = {}
    for r in bt.RUNGS:
        bits = (bits_by_rung or {}).get(r, [0] * bt.N_ITEMS)
        out[r] = {"bits": list(bits), "continuations": [" zzz" if not b else " ok" for b in bits],
                  "weight_sha256": odd_digest if r == odd_rung else digest,
                  "commit": (odd_commit or commit) if r == odd_rung else commit}
    return out


def test_gate1_failures_comma():
    ep = _endpoint_records()
    assert bn.gate1_failures_comma(_gate_rec(), ep) == []
    assert bn.GATE1_FIELDS_2N == ("rungs", "bit_diffs", "continuation_diffs", "continuations_compared",
                                  "digest_sweep", "digest_endpoint", "commit_sweep", "commit_endpoint",
                                  "prereg_tag")
    bad = bn.gate1_failures_comma(_gate_rec(bit_diffs={**{r: 0 for r in bt.RUNGS}, "odd6": 2}), ep)
    assert any("odd6" in b and "2 bit diffs" in b for b in bad)
    for n in (499, bt.N_ITEMS + 1):
        bad = bn.gate1_failures_comma(_gate_rec(continuations_compared={**{r: bt.N_ITEMS for r in bt.RUNGS}, "odd6": n}), ep)
        assert any(f"{n} continuation pairs" in b for b in bad)
    assert any("tensor digest" in b for b in bn.gate1_failures_comma(_gate_rec(digest_sweep="X"), ep))
    assert any("commit" in b for b in bn.gate1_failures_comma(_gate_rec(commit_sweep="0" * 40), ep))
    assert any("prereg_tag" in b for b in bn.gate1_failures_comma(_gate_rec(prereg_tag="exp2m-preregistered"), ep))
    assert any("34-rung" in b for b in bn.gate1_failures_comma(_gate_rec(rungs=list(bt.RUNGS)[:-1]), ep))
    ep2 = dict(ep)
    del ep2["odd6"]
    assert any("no stage1_final endpoint record" in b for b in bn.gate1_failures_comma(_gate_rec(), ep2))
    for b in bn.gate1_failures_comma(_gate_rec(digest_sweep="X"), ep):
        assert b.startswith("gate 1 comma_7b")
    # Freeze F-2: `digest_endpoint`/`commit_endpoint` are attested by the
    # runner from ONE rung's record; both are now measured over all 34.
    mixed = _endpoint_records(odd_rung="odd6")
    bad = bn.gate1_failures_comma(_gate_rec(), mixed)
    assert any("2 different tensor digests" in b and "one load" in b for b in bad)
    mixed_c = _endpoint_records(odd_rung="odd6", odd_digest="D", odd_commit="d" * 40)
    assert any("2 different commits" in b for b in bn.gate1_failures_comma(_gate_rec(), mixed_c))
    coherent_but_other = _endpoint_records(digest="E")
    bad = bn.gate1_failures_comma(_gate_rec(digest_sweep="E", digest_endpoint="E"), coherent_but_other)
    assert bad == []
    bad = bn.gate1_failures_comma(_gate_rec(), coherent_but_other)      # attested "D", records all "E"
    assert any("is not the tensor digest every stage1_final record carries" in b for b in bad)
    bad = bn.gate1_failures_comma(_gate_rec(), _endpoint_records(commit="e" * 40))
    assert any("is not the commit every stage1_final record carries" in b for b in bad)


def test_gate1_rederive_comma():
    ep = _endpoint_records({"antonym": [1] * 10 + [0] * 490})
    sw = _endpoint_records({"antonym": [1] * 10 + [0] * 490})
    assert bn.gate1_rederive_comma(sw, ep, _gate_rec()) == []
    sw2 = _endpoint_records({"antonym": [1] * 11 + [0] * 489})
    bad = bn.gate1_rederive_comma(sw2, ep, _gate_rec())
    assert any("antonym" in b and "1 bit diff" in b for b in bad)
    assert any("attested bit_diffs 0 disagrees with the re-derived 1" in b for b in bad)
    g = _gate_rec(bit_diffs={**{r: 0 for r in bt.RUNGS}, "antonym": 1})
    assert any("attested bit_diffs 1 disagrees with the re-derived 0" in b for b in bn.gate1_rederive_comma(sw, ep, g))
    # Freeze F-2 (the sweep side): digest_sweep/commit_sweep measured over
    # all 34 sweep step-ENDPOINT records, not merely against digest_endpoint.
    mixed_sw = _endpoint_records({"antonym": [1] * 10 + [0] * 490}, odd_rung="odd6")
    assert any("re-derive" in b and "2 different tensor digests" in b
               for b in bn.gate1_rederive_comma(mixed_sw, ep, _gate_rec()))
    other_sw = _endpoint_records({"antonym": [1] * 10 + [0] * 490}, digest="E")
    assert any("is not the tensor digest every step" in b
               for b in bn.gate1_rederive_comma(other_sw, ep, _gate_rec()))
    other_c = _endpoint_records({"antonym": [1] * 10 + [0] * 490}, commit="e" * 40)
    assert any("is not the commit every step" in b
               for b in bn.gate1_rederive_comma(other_c, ep, _gate_rec()))
    short = dict(sw)
    short["odd6"] = {"bits": [0] * 10, "continuations": [" zzz"] * 10}
    assert any("odd6" in b and "coverage failure" in b for b in bn.gate1_rederive_comma(short, ep, _gate_rec()))
    g2 = _gate_rec(continuations_compared={**{r: bt.N_ITEMS for r in bt.RUNGS}, "odd6": 400})
    assert any("odd6" in b and "400" in b for b in bn.gate1_rederive_comma(sw, ep, g2))
    over = dict(sw)
    over["odd6"] = {"bits": sw["odd6"]["bits"] + [0], "continuations": sw["odd6"]["continuations"]}
    bad2 = bn.gate1_rederive_comma(over, ep, _gate_rec())
    assert any("odd6" in b and "coverage failure" in b for b in bad2)
    assert all(b.startswith("gate 1 comma_7b re-derive") for b in bad + bad2)


# -------------------------------------------------------------- loaders

def test_cache_key_and_clean_dir_writes_config(tmp_path):
    d = bn._cache_dir_comma("stage1-step040000-tokens84B", tmp_path)
    assert d == tmp_path / "comma_7b" / "stage1-step040000-tokens84B"
    src = tmp_path / "raw" / "model-00001-of-00003.safetensors"
    src.parent.mkdir(parents=True)
    src.write_bytes(b"weights")

    class Cfg:
        def to_json_file(self, path):
            Path(path).write_text('{"eos_token_id": 2}')

    clean = bn.clean_dir_comma("stage1-step040000-tokens84B", tmp_path, {src.name: src}, config=Cfg())
    assert clean == d / "clean" and (clean / src.name).read_bytes() == b"weights"
    assert json.loads((clean / "config.json").read_text())["eos_token_id"] == 2
    with pytest.raises(TypeError):
        bn.clean_dir_comma("stage1-step040000-tokens84B", tmp_path, {src.name: src})       # config REQUIRED
    bn.free_checkpoint_comma("stage1-step040000-tokens84B", tmp_path)
    assert not d.exists()
    assert bn.CKPT_CACHE_2N == Path.home() / "emergence-lab" / "ckpt_cache_2n"


def test_loader_family_imports_torch_lazily():
    import ast
    src = (bn.EXP2N / "battery_2n.py").read_text()
    tree = ast.parse(src)
    top = [n for n in tree.body if isinstance(n, (ast.Import, ast.ImportFrom))]
    names = {a.name.split(".")[0] for n in top for a in n.names} | \
            {n.module.split(".")[0] for n in top if isinstance(n, ast.ImportFrom) and n.module}
    assert not names & {"torch", "transformers", "huggingface_hub"}


# ---------------------------------------------------------------- pins

def test_frozen_files_2n_list():
    assert set(bm.FROZEN_SHA256_2M) <= set(bn.FROZEN_FILES_2N)
    for rel in bm.INSTRUMENT_BLOBS_2M:
        assert (bn.REPO / rel) in bn.FROZEN_FILES_2N                # 2m's tag-bound blobs are frozen bytes to 2n
    assert (bn.EXP2N / "power_2n.py") in bn.FROZEN_FILES_2N
    assert (bn.EXP2N / "make_referents_2n.py") in bn.FROZEN_FILES_2N
    for rel in bn.INSTRUMENT_BLOBS_2N:
        assert (bn.REPO / rel) not in bn.FROZEN_FILES_2N            # tag-bound, never sha-pinned
    assert len(bn.FROZEN_FILES_2N) == len(set(bn.FROZEN_FILES_2N))
    assert len(bn.FROZEN_FILES_2N) == 54


def test_check_frozen_2n_refuses_unpinned_and_drift(monkeypatch, tmp_path):
    monkeypatch.setattr(bn, "FROZEN_SHA256_2N", {})
    with pytest.raises(RuntimeError, match="not pinned"):
        bn.check_frozen_2n()
    p = tmp_path / "f.py"
    p.write_text("x = 1\n")
    monkeypatch.setattr(bn, "FROZEN_SHA256_2N", {p: bg.sha256_file(p)})
    bn.check_frozen_2n()
    p.write_text("x = 2\n")
    with pytest.raises(RuntimeError, match="drifted"):
        bn.check_frozen_2n()


def test_frozen_from_disk_strict_raises_on_missing(monkeypatch, tmp_path):
    monkeypatch.setattr(bn, "FROZEN_FILES_2N", (tmp_path / "missing.py",))
    with pytest.raises(FileNotFoundError):
        bn.frozen_from_disk()
    assert bn.frozen_from_disk(strict=False) == {}


def test_require_prereg_2n_with_fakes(monkeypatch):
    with pytest.raises(RuntimeError, match="does not exist"):
        bn.require_prereg_2n(tag_exists=lambda t: False, blob_sha=lambda t, r: None)
    present = tuple(r for r in bn.INSTRUMENT_BLOBS_2N if (bn.REPO / r).is_file())
    monkeypatch.setattr(bn, "INSTRUMENT_BLOBS_2N", present)
    ok = bn.require_prereg_2n(tag_exists=lambda t: t == bn.PREREG_TAG_2N,
                              blob_sha=lambda t, r: bg.sha256_file(bn.REPO / r))
    assert ok["tag"] == bn.PREREG_TAG_2N and set(ok["instrument_blobs"]) == set(present)
    with pytest.raises(RuntimeError, match="does not bind"):
        bn.require_prereg_2n(tag_exists=lambda t: True, blob_sha=lambda t, r: "0" * 64)


def _git(repo, *args):
    return subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, check=True)


def test_require_prereg_2n_binds_the_instrument_in_a_real_git_repo(tmp_path, monkeypatch):
    """2h F-3's lineage: the prereg tag must bind the INSTRUMENT, not a
    name. Real `git init`, a real annotated tag over the instrument
    blobs present on disk, `git show <tag>:<path>` as the comparison —
    then a post-tag edit to `battery_2n.py` is refused."""
    present = tuple(r for r in bn.INSTRUMENT_BLOBS_2N if (bn.REPO / r).is_file())
    monkeypatch.setattr(bn, "INSTRUMENT_BLOBS_2N", present)
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "freeze@example.invalid")
    _git(repo, "config", "user.name", "freeze")
    for rel in present:
        dst = repo / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes((bn.REPO / rel).read_bytes())
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "instrument")
    _git(repo, "tag", "-a", bn.PREREG_TAG_2N, "-m", "freeze probe")

    def tag_exists(tag):
        return tag in _git(repo, "tag", "--list", tag).stdout.split()

    def blob_sha(tag, rel):
        out = subprocess.run(["git", "show", f"{tag}:{rel}"], cwd=repo, capture_output=True)
        return None if out.returncode else hashlib.sha256(out.stdout).hexdigest()

    monkeypatch.setattr(bn, "REPO", repo)
    got = bn.require_prereg_2n(tag_exists=tag_exists, blob_sha=blob_sha)
    assert set(got["instrument_blobs"]) == set(present)
    bat = repo / "experiments/exp2n/battery_2n.py"
    bat.write_bytes(bat.read_bytes() + b"\n# a post-tag edit\n")
    with pytest.raises(RuntimeError, match="does not bind experiments/exp2n/battery_2n.py"):
        bn.require_prereg_2n(tag_exists=tag_exists, blob_sha=blob_sha)


# ------------------------------------------------------- new: tokenizer,
# render, stop id, and the weight-bearing-main manifest refusal

class _Tok:
    """A stub with Comma's real facts: pad 0 declared, unk 1, bos 2, eos 3,
    64,000 entries; `__call__` renders 'Q:' -> [52, 29], prepends 2 when the
    text starts with BOS_TOKEN_2N, and (when `bos_on_plain`) prepends 2 on a
    plain render too (the fact this stack does NOT exhibit)."""
    def __init__(self, *, side="left", pad=0, eos=3, bos=2, unk=1, n=64000, bos_on_plain=False):
        self.padding_side, self.pad_token_id, self.eos_token_id, self.bos_token_id = side, pad, eos, bos
        self.unk_token_id, self._n, self._bos_on_plain = unk, n, bos_on_plain
        self.all_special_ids = [bos, eos, unk, pad]

    def __len__(self):
        return self._n

    def __call__(self, text):
        ids = [52, 29] if text.endswith("Q:") else [52]
        if text.startswith(bn.BOS_TOKEN_2N) or self._bos_on_plain:
            ids = [self.bos_token_id] + ids
        return {"input_ids": ids}


def test_check_tokenizer_2n_on_stubs():
    bn.check_tokenizer_2n(_Tok())
    for kw, needle in ((dict(side="right"), "padding_side"), (dict(pad=None), "pad_token_id"),
                       (dict(pad=128004), "pad_token_id"), (dict(eos=2), "eos_token_id"),
                       (dict(bos=1), "bos_token_id"), (dict(n=64256), "64000"),
                       (dict(bos_on_plain=True), "plain render")):
        with pytest.raises(RuntimeError, match=needle):
            bn.check_tokenizer_2n(_Tok(**kw))

    class _NoBosRender(_Tok):
        def __call__(self, text):
            return {"input_ids": [52, 29]}          # the BOS prefix is swallowed
    with pytest.raises(RuntimeError, match="BOS render"):
        bn.check_tokenizer_2n(_NoBosRender())


def test_load_tokenizer_comma_sets_left_padding_and_refuses_a_foreign_pad(monkeypatch):
    import types
    calls = []

    class _Loaded(_Tok):
        def __init__(self):
            super().__init__(side="right")
    fake = types.SimpleNamespace(from_pretrained=lambda repo, revision=None: (calls.append((repo, revision)), _Loaded())[1])
    monkeypatch.setitem(sys.modules, "transformers", types.SimpleNamespace(AutoTokenizer=fake))
    tok = bn.load_tokenizer_comma(bn.REPO_COMMA, "c" * 40)
    assert calls == [(bn.REPO_COMMA, "c" * 40)] and tok.padding_side == "left" and tok.pad_token_id == 0

    class _ForeignPad(_Tok):
        def __init__(self):
            super().__init__(pad=7)
    fake.from_pretrained = lambda repo, revision=None: _ForeignPad()
    with pytest.raises(RuntimeError, match="pad_token_id is 7"):
        bn.load_tokenizer_comma(bn.REPO_COMMA, "c" * 40)


def test_render_2n_and_bos_runner_prefix_every_prompt():
    assert bn.RENDER_2N == "bos"
    assert bn.render_2n(["Q: a\nA:", "x"]) == [bn.BOS_TOKEN_2N + "Q: a\nA:", bn.BOS_TOKEN_2N + "x"]
    seen = {}

    class _Inner:
        def generate(self, prompts, max_new_tokens):
            seen["prompts"], seen["k"] = list(prompts), max_new_tokens
            return [" ok"] * len(prompts)
    r = bn.BosRunner(_Inner())
    assert r.generate(["p1", "p2"], 5) == [" ok", " ok"]
    assert seen == {"prompts": [bn.BOS_TOKEN_2N + "p1", bn.BOS_TOKEN_2N + "p2"], "k": 5}
    assert r.batch_size == getattr(_Inner(), "batch_size", None)


def test_set_eos_stop_2n_overrides_and_asserts():
    import types

    class _GC:
        eos_token_id = 2
    m = types.SimpleNamespace(generation_config=_GC(), config=types.SimpleNamespace(eos_token_id=2, bos_token_id=1))
    facts = bn.set_eos_stop_2n(m)
    assert m.generation_config.eos_token_id == bn.EOS_STOP_ID_2N == 3
    assert facts == {"config_eos_token_id": 2, "config_bos_token_id": 1, "generation_eos_token_id": 3}

    class _Stuck:
        @property
        def eos_token_id(self):
            return 2

        @eos_token_id.setter
        def eos_token_id(self, v):
            pass
    m2 = types.SimpleNamespace(generation_config=_Stuck(), config=types.SimpleNamespace(eos_token_id=2, bos_token_id=1))
    with pytest.raises(RuntimeError, match="generation_config.eos_token_id"):
        bn.set_eos_stop_2n(m2)


def test_build_manifest_comma_main_is_a_weight_bearing_entry_and_grid_dups_against_it_refuse():
    inv = _inventory()
    man = bn.build_manifest_comma(inv)
    assert man["main"]["revision"] == "main" and len(man["main"]["lfs_sha256"]) == 3
    assert man["stage2_final"]["revision"] == bn.REV_STAGE2_FINAL_2N
    assert man["twin"]["config_commit"] == man["entries_comma"][str(bn.ENDPOINT_STEP_2N)]["commit"]
    assert man["every40k_subset"] == list(bn.EVERY40K_SUBSET_2N) and man["grid_comma"] == list(bn.GRID_COMMA)
    inv2 = _inventory()
    rev = bn.REV_ENDPOINT_2N.replace("460000", "020000").replace("965B", "42B")
    inv2[bn.REPO_COMMA][rev]["files"] = dict(inv2[bn.REPO_COMMA]["main"]["files"])   # a stale copy of main
    with pytest.raises(ValueError, match="duplicate"):
        bn.build_manifest_comma(inv2)
