# experiments/exp2l/tests/test_battery_2l.py
"""battery_2l: constants and the grid; the manifest builder on a
hand-built inventory (candidate rule, duplicate refusal, pinned
endpoint, step 0); load_manifest's sha pin; the rung-set rule's
partition on the real floors; paths; the record stamps; the gate-1
checkers on hand records; the endpoint composite sha; the loader
family's pure parts (clean dir writes config.json; the 13B cache key);
the pins and the prereg binding with fakes. No torch, no network."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from experiments.exp2d import battery_2d as bt
from experiments.exp2g import battery_2g as bg
from experiments.exp2g import checkpoints_2g as ck
from experiments.exp2i import battery_2i as bi
from experiments.exp2k import battery_2k as bk
from experiments.exp2l import battery_2l as bl


# ------------------------------------------------------------ constants

def test_constants_and_grid():
    assert bl.REPO_13B == "allenai/OLMo-2-1124-13B"
    assert bl.SIZE_OUT == "olmo13b" and bl.FAMILY == "olmo2"
    assert bl.REV_13B_ENDPOINT == "stage1-step596057-tokens5001B"
    assert bl.REV_13B_STEP0 == "stage1-step0-tokens0B"
    assert bl.ENDPOINT_STEP_13B == 596057 and bl.STEP0 == 0
    assert bl.GRID_13B == (1000, 2000, 4000, 8000, 16000, 32000, 64000, 128000, 192000,
                           256000, 320000, 384000, 448000, 512000, 576000, 596057)
    assert bl.trained_steps_13b() == bl.GRID_13B and bl.n_trained_13b() == 16
    assert bl.STEP0 not in bl.GRID_13B
    assert bl.GRID_13B[-1] == bl.ENDPOINT_STEP_13B
    assert bl.PREREG_TAG_2L == "exp2l-preregistered"
    assert bl.ENDPOINT_SEAL_TAG_2L == "exp2l-endpoint-sealed"
    assert bl.INSTRUMENT_BLOBS_2L == ("experiments/exp2l/analyze_2l.py",
                                      "experiments/exp2l/battery_2l.py",
                                      "experiments/exp2l/run/endpoint_2l.py",
                                      "experiments/exp2l/run/sweep_2l.py")
    assert bl.R_CAP_2K == bk.R_CAP_DESIGN and len(bl.R_CAP_2K) == 9
    assert set(bl.R_CAP_2K) < set(bl.STRATA_RUNGS) and len(bl.STRATA_RUNGS) == 11
    assert bl.BATCH_SIZE_2L == 16
    assert bl.N_ITEMS == 500


def test_seal_literals_match_the_committed_seals():
    s2k = json.loads(bk.seal_path(bk.EXP2K).read_text())["sha256"]
    s2i = json.loads(bi.predictor_seal_path(bi.EXP2I).read_text())["sha256"]
    assert bl.SEAL_2K_SHA256 == s2k
    assert bl.SEAL_2I_SHA256 == s2i
    assert bl.PREDICTOR_SHA_2L == bl.predictor_sha_2l(s2k, s2i)
    assert bl.PREDICTOR_SHA_2L == hashlib.sha256(f"{s2k}|{s2i}".encode()).hexdigest()
    assert bl.PREDICTOR_TAGS_2L == "exp2k-predictor-sealed+exp2i-predictor-sealed"


# ------------------------------------------------------------- manifest

def _files(tag, n_shards=12, size=4_500_000_000):
    """A 13B-like revision file table: 12 safetensors shards + index."""
    out = {f"model-{i:05d}-of-{n_shards:05d}.safetensors": [f"{tag}{i:02d}" * 4, size]
           for i in range(1, n_shards + 1)}
    return out


def _inventory(*, dup_step=None, drop_endpoint=False, drop_step0=False):
    table = {}
    for step in bl.GRID_13B + (bl.STEP0,):
        rev = (bl.REV_13B_ENDPOINT if step == bl.ENDPOINT_STEP_13B else
               bl.REV_13B_STEP0 if step == bl.STEP0 else f"stage1-step{step}-tokens{step // 100}B")
        table[rev] = {"commit": f"c{step:07d}" + "0" * 32, "files": _files(f"s{step}")}
    table["main"] = {"commit": "m" * 40, "files": _files("main")}
    table["stage2-ingredient1-step1000-tokens5B"] = {"commit": "i" * 40, "files": _files("ing")}
    if dup_step is not None:
        rev = f"stage1-step{dup_step}-tokens{dup_step // 100}B"
        table["stage1-step999999-tokens9999B"] = {"commit": "d" * 40,
                                                  "files": dict(table[rev]["files"])}
    if drop_endpoint:
        del table[bl.REV_13B_ENDPOINT]
    if drop_step0:
        del table[bl.REV_13B_STEP0]
    return {bl.REPO_13B: table}


def test_build_manifest_13b_shape():
    m = bl.build_manifest_13b(_inventory())
    assert m["repo_13b"] == bl.REPO_13B
    assert m["grid_13b"] == list(bl.GRID_13B) and m["trained_steps_13b"] == list(bl.GRID_13B)
    assert m["step0"] == bl.STEP0
    assert set(m["entries_13b"]) == {str(s) for s in bl.GRID_13B} | {str(bl.STEP0)}
    e = m["entries_13b"][str(bl.ENDPOINT_STEP_13B)]
    assert e["revision"] == bl.REV_13B_ENDPOINT and e["kind"] == "safetensors-shards"
    assert e["files"][-1] == "model.safetensors.index.json" and len(e["files"]) == 13
    assert len(e["lfs_sha256"]) == 12 and all(isinstance(v, int) for v in e["lfs_size"].values())
    z = m["entries_13b"][str(bl.STEP0)]
    assert z["revision"] == bl.REV_13B_STEP0 and z["commit"].startswith("c0000000")
    assert m["main"]["revision"] == "main"
    assert m["final_duplicates"] == [] and m["signature_equals_main"] is False
    assert m["n_revisions"] == len(_inventory()[bl.REPO_13B])


def test_build_manifest_13b_refuses_duplicate_grid_point_missing_endpoint_and_missing_step0():
    with pytest.raises(ValueError, match="duplicate"):
        bl.build_manifest_13b(_inventory(dup_step=64000))
    with pytest.raises(ValueError, match="exactly one stage1 branch"):
        bl.build_manifest_13b(_inventory(drop_endpoint=True))
    with pytest.raises(ValueError, match="exactly one stage1 branch"):
        bl.build_manifest_13b(_inventory(drop_step0=True))


def test_build_manifest_13b_endpoint_may_duplicate_and_is_recorded():
    inv = _inventory()
    inv[bl.REPO_13B]["stage2-copy"] = {"commit": "e" * 40,
                                       "files": dict(inv[bl.REPO_13B][bl.REV_13B_ENDPOINT]["files"])}
    m = bl.build_manifest_13b(inv)
    assert m["final_duplicates"] == ["stage2-copy"]


def test_build_manifest_13b_refuses_endpoint_and_step0_revision_drift():
    """Mutation gap (Task 5, #4/#5): the step-number match alone is not
    enough — the matched revision STRING must equal the pinned literal,
    or a same-step revision under a different token count (a Hub
    relabelling, or a same-numbered branch on a different lineage)
    would silently pass as the endpoint/step-0."""
    inv = _inventory()
    wrong_rev = f"stage1-step{bl.ENDPOINT_STEP_13B}-tokens1B"
    inv[bl.REPO_13B][wrong_rev] = inv[bl.REPO_13B].pop(bl.REV_13B_ENDPOINT)
    with pytest.raises(ValueError, match="endpoint revision"):
        bl.build_manifest_13b(inv)

    inv2 = _inventory()
    wrong_rev0 = f"stage1-step{bl.STEP0}-tokens1B"
    inv2[bl.REPO_13B][wrong_rev0] = inv2[bl.REPO_13B].pop(bl.REV_13B_STEP0)
    with pytest.raises(ValueError, match="step-0 revision"):
        bl.build_manifest_13b(inv2)


def test_candidate_rule_accepts_twelve_shard_naming():
    files = _files("x")
    c = ck.candidate("stage1-step1000-tokens1B", files, _files("main"))
    assert c["kind"] == "safetensors-shards" and len(c["lfs"]) == 12
    assert c["files"][0] == "model-00001-of-00012.safetensors"


def test_load_manifest_13b_pins_sha_and_grid(tmp_path):
    m = bl.build_manifest_13b(_inventory())
    p = tmp_path / "m.json"
    bl.write_manifest(p, m)
    sha = bg.sha256_file(p)
    got = bl.load_manifest_13b(p, sha_pin=sha)
    assert got["grid_13b"] == list(bl.GRID_13B)
    with pytest.raises(ValueError, match="hashes to"):
        bl.load_manifest_13b(p, sha_pin="0" * 64)
    m2 = dict(m, grid_13b=[1, 2, 3])
    bl.write_manifest(p, m2)
    with pytest.raises(ValueError, match="frozen 13B grid"):
        bl.load_manifest_13b(p, sha_pin=None)


def test_entry_accessors():
    m = bl.build_manifest_13b(_inventory())
    assert bl.entry_13b(m, 64000)["revision"] == "stage1-step64000-tokens640B"
    assert bl.entry_13b(m, "64000")["revision"] == "stage1-step64000-tokens640B"
    assert bl.entry_13b(m, bl.STEP0)["revision"] == bl.REV_13B_STEP0
    assert bl.entry_main_13b(m)["commit"] == "m" * 40
    with pytest.raises(ValueError, match="not a grid entry"):
        bl.entry_13b(m, 3000)


def test_committed_manifest_is_pinned_and_consistent():
    """Live after Step 4 of this task (the real scan + manifest)."""
    if bl.CHECKPOINTS_2L_SHA256 is None:
        pytest.skip("manifest not yet built/pinned (Task 1 Step 4)")
    m = bl.load_manifest_13b(bl.CHECKPOINTS_PATH, sha_pin=bl.CHECKPOINTS_2L_SHA256)
    assert bl.entry_13b(m, bl.ENDPOINT_STEP_13B)["revision"] == bl.REV_13B_ENDPOINT
    assert bl.entry_13b(m, bl.STEP0)["revision"] == bl.REV_13B_STEP0
    for step in bl.GRID_13B:
        e = bl.entry_13b(m, step)
        assert e["kind"] == "safetensors-shards" and len(e["lfs_sha256"]) == 12
    assert bl.entry_main_13b(m)["kind"] == "safetensors-shards"


# ---------------------------------------------------------------- paths

def test_paths(tmp_path):
    r = tmp_path
    assert bl.sweep_dir(r) == r / "results" / "sweep" / "olmo13b"
    assert bl.record_path(r, 64000, "antonym") == bl.sweep_dir(r) / "step64000" / "antonym.json"
    assert bl.record_path(r, bl.STEP0, "antonym") == bl.sweep_dir(r) / "step0" / "antonym.json"
    assert bl.checkpoint_record_path(r, "1000") == bl.sweep_dir(r) / "step1000" / "_checkpoint.json"
    assert bl.gate1_path(r) == bl.sweep_dir(r) / "gate1.json"
    assert bl.halt_marker_path(r) == bl.sweep_dir(r) / "HALTED"
    assert bl.endpoint_record_path(r, "stage1_final", "odd6") == r / "results" / "endpoint" / "stage1_final" / "odd6.json"
    assert bl.endpoint_record_path(r, "main", "odd6") == r / "results" / "endpoint" / "main" / "odd6.json"
    with pytest.raises(ValueError):
        bl.endpoint_record_path(r, "twin", "odd6")
    assert bl.rung_set_path(r) == r / "results" / "endpoint" / "rung_set_2l.json"
    assert bl.power_path(r) == r / "results" / "endpoint" / "power_2l.json"


# ------------------------------------------------------------ rung set

def test_rung_set_from_counts_2l_partition_on_real_floors():
    floors = bg.load_floors()
    counts = {r: 0 for r in bt.RUNGS}
    for r in ("antonym", "add_base8", "sub3_mid"):      # three of the nine
        counts[r] = 480
    counts["count_div13"] = 480                          # in the eleven, not the nine
    counts["reverse_string"] = 480                       # outside the eleven
    rs = bl.rung_set_from_counts_2l(counts, floors)
    assert rs["R_PRIMARY"] == ["add_base8", "antonym", "sub3_mid"]
    assert rs["R_ELEVEN_EXTRA"] == ["count_div13"]
    assert rs["R_EXTRA"] == ["reverse_string"]
    assert set(rs["R_13B"]) == set(rs["R_PRIMARY"]) | set(rs["R_ELEVEN_EXTRA"]) | set(rs["R_EXTRA"])
    assert set(rs["per_rung"]) == set(bt.RUNGS)
    assert rs["per_rung"]["antonym"]["significant"] is True
    assert rs["per_rung"]["odd6"]["significant"] is False
    assert rs["primary_is_the_nine"] is False
    counts2 = {r: (480 if r in bl.R_CAP_2K else 0) for r in bt.RUNGS}
    rs2 = bl.rung_set_from_counts_2l(counts2, floors)
    assert rs2["R_PRIMARY"] == sorted(bl.R_CAP_2K) and rs2["primary_is_the_nine"] is True


# --------------------------------------------------------- record stamps

def _cap(rung="antonym"):
    return bg.load_battery()[rung]


def test_item_record_2l_and_checkpoint_record_2l():
    cap = _cap()
    ev = {"bits": [0] * bt.N_ITEMS, "correct": 0, "continuations": [" zzz"] * bt.N_ITEMS}
    ckpt = {"revision": "stage1-step1000-tokens8B", "commit": "c" * 40, "kind": "safetensors-shards",
            "files": ["a"], "weight_sha256": "D", "config_source": "cs", "tokenizer_source": "ts"}
    rec = bl.item_record_2l(rung="antonym", cap=cap, ev=ev, ckpt=ckpt, step=1000,
                            endpoint_sha="E" * 64, t_s=1.0)
    assert rec["family"] == bl.FAMILY and rec["size"] == bl.SIZE_OUT and rec["step"] == 1000
    assert rec["seal_tag"] == bl.ENDPOINT_SEAL_TAG_2L
    assert rec["predictor_sha"] == bl.PREDICTOR_SHA_2L
    assert rec["endpoint_sha256"] == "E" * 64
    assert rec["n"] == bt.N_ITEMS and rec["dtype"] == "float16" and "which" not in rec
    rec0 = bl.item_record_2l(rung="antonym", cap=cap, ev=ev, ckpt=ckpt, step=bl.STEP0,
                             endpoint_sha="E" * 64, t_s=0.0)
    assert rec0["step"] == 0
    info = {"sha256": {"a": "1"}, "loading_info": {"missing_keys": 0, "unexpected_keys": 0,
                                                   "mismatched_keys": 0}}
    cr = bl.checkpoint_record_2l(step=1000, ckpt=ckpt, info=info, seconds=12.34)
    assert cr == {"family": bl.FAMILY, "size": bl.SIZE_OUT, "step": 1000,
                  "revision": ckpt["revision"], "commit": ckpt["commit"], "sha256": {"a": "1"},
                  "loading_info": info["loading_info"], "digest": "D", "download_seconds": 12.3}


# ------------------------------------------------------ endpoint sha

def test_composite_sha_and_endpoint_sha256(tmp_path):
    files = {"b": "2", "a": "1"}
    want = hashlib.sha256("a 1\nb 2".encode()).hexdigest()
    assert bl.composite_sha(files) == want
    for which in ("stage1_final", "main"):
        for r in bt.RUNGS:
            p = bl.endpoint_record_path(tmp_path, which, r)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps({"rung": r, "which": which}))
    bl.rung_set_path(tmp_path).write_text("{}")
    bl.power_path(tmp_path).write_text("{}")
    files = bl.endpoint_files(tmp_path)
    assert len(files) == 70
    assert "results/endpoint/rung_set_2l.json" in files and "results/endpoint/power_2l.json" in files
    s1 = bl.endpoint_sha256(tmp_path)
    assert s1 == bl.composite_sha(files) and len(s1) == 64
    bl.power_path(tmp_path).write_text('{"x": 1}')
    assert bl.endpoint_sha256(tmp_path) != s1
    bl.endpoint_record_path(tmp_path, "main", "odd6").unlink()
    with pytest.raises(FileNotFoundError):
        bl.endpoint_files(tmp_path)
    # Mutation gap (Task 5, #10): a plain-missing path already raises
    # FileNotFoundError via bg.sha256_file's own open() even with the
    # explicit is_file() guard stripped -- same exception class, so
    # that case alone cannot distinguish the guard from its absence. A
    # DIRECTORY at the path is not a file (is_file() is False, so the
    # guard is the only thing standing between it and an attempted
    # read), but reading it raises IsADirectoryError, not
    # FileNotFoundError -- exactly the guard's job.
    bl.endpoint_record_path(tmp_path, "main", "odd6").mkdir(parents=True)
    with pytest.raises(FileNotFoundError):
        bl.endpoint_files(tmp_path)


# -------------------------------------------------------------- gate 1

def _gate_rec(**over):
    g = {"rungs": list(bt.RUNGS), "bit_diffs": {r: 0 for r in bt.RUNGS},
         "continuation_diffs": {r: 0 for r in bt.RUNGS},
         "continuations_compared": {r: bt.N_ITEMS for r in bt.RUNGS},
         "digest_sweep": "D", "digest_endpoint": "D", "commit_sweep": "c" * 40,
         "commit_endpoint": "c" * 40, "prereg_tag": bl.PREREG_TAG_2L}
    g.update(over)
    return g


def _endpoint_records(bits_by_rung=None):
    out = {}
    for r in bt.RUNGS:
        bits = (bits_by_rung or {}).get(r, [0] * bt.N_ITEMS)
        out[r] = {"bits": list(bits), "continuations": [" zzz" if not b else " ok" for b in bits]}
    return out


def test_gate1_failures_13b():
    ep = _endpoint_records()
    assert bl.gate1_failures_13b(_gate_rec(), ep) == []
    assert bl.GATE1_FIELDS_2L == ("rungs", "bit_diffs", "continuation_diffs",
                                  "continuations_compared", "digest_sweep", "digest_endpoint",
                                  "commit_sweep", "commit_endpoint", "prereg_tag")
    bad = bl.gate1_failures_13b(_gate_rec(bit_diffs={**{r: 0 for r in bt.RUNGS}, "odd6": 2}), ep)
    assert any("odd6" in b and "2 bit diffs" in b for b in bad)
    bad = bl.gate1_failures_13b(_gate_rec(continuations_compared={**{r: bt.N_ITEMS for r in bt.RUNGS},
                                                                  "odd6": 499}), ep)
    assert any("499 continuation pairs" in b for b in bad)
    # Mutation gap (Task 5, #15): OVER-coverage (more pairs than N_ITEMS)
    # must fail too -- a `!=` loosened to `<` would silently accept it.
    bad = bl.gate1_failures_13b(_gate_rec(continuations_compared={**{r: bt.N_ITEMS for r in bt.RUNGS},
                                                                  "odd6": bt.N_ITEMS + 1}), ep)
    assert any("501 continuation pairs" in b for b in bad)
    bad = bl.gate1_failures_13b(_gate_rec(digest_sweep="X"), ep)
    assert any("tensor digest" in b for b in bad)
    bad = bl.gate1_failures_13b(_gate_rec(commit_sweep="0" * 40), ep)
    assert any("commit" in b for b in bad)
    bad = bl.gate1_failures_13b(_gate_rec(prereg_tag="exp2i-preregistered"), ep)
    assert any("prereg_tag" in b for b in bad)
    bad = bl.gate1_failures_13b(_gate_rec(rungs=list(bt.RUNGS)[:-1]), ep)
    assert any("34-rung" in b for b in bad)
    ep2 = dict(ep)
    del ep2["odd6"]
    assert any("no stage1_final endpoint record" in b for b in bl.gate1_failures_13b(_gate_rec(), ep2))
    for b in bad:
        assert b.startswith("gate 1 olmo13b")


def test_gate1_rederive_13b():
    ep = _endpoint_records({"antonym": [1] * 10 + [0] * 490})
    sw = _endpoint_records({"antonym": [1] * 10 + [0] * 490})
    assert bl.gate1_rederive_13b(sw, ep, _gate_rec()) == []
    sw2 = _endpoint_records({"antonym": [1] * 11 + [0] * 489})
    bad = bl.gate1_rederive_13b(sw2, ep, _gate_rec())
    assert any("antonym" in b and "1 bit diff" in b for b in bad)
    assert any("attested bit_diffs 0 disagrees with the re-derived 1" in b for b in bad)
    g = _gate_rec(bit_diffs={**{r: 0 for r in bt.RUNGS}, "antonym": 1})
    bad = bl.gate1_rederive_13b(sw, ep, g)          # bytes identical, attestation lies
    assert any("attested bit_diffs 1 disagrees with the re-derived 0" in b for b in bad)
    short = dict(sw)
    short["odd6"] = {"bits": [0] * 10, "continuations": [" zzz"] * 10}
    bad = bl.gate1_rederive_13b(short, ep, _gate_rec())
    assert any("odd6" in b and "coverage failure" in b for b in bad)
    g2 = _gate_rec(continuations_compared={**{r: bt.N_ITEMS for r in bt.RUNGS}, "odd6": 400})
    bad = bl.gate1_rederive_13b(sw, ep, g2)
    assert any("odd6" in b and "400" in b for b in bad)
    # Mutation gap (Task 5, #20): OVER-length bits/continuations (more
    # than N_ITEMS on one side) must be a coverage failure too -- a
    # `!=` loosened to `<` would let zip() silently truncate to the
    # shorter side instead.
    over = dict(sw)
    # ONLY bits over-length -- continuations stays at N_ITEMS so the
    # (unmutated) continuations coverage check cannot also catch this,
    # isolating mutant #20's exact branch.
    over["odd6"] = {"bits": sw["odd6"]["bits"] + [0], "continuations": sw["odd6"]["continuations"]}
    bad2 = bl.gate1_rederive_13b(over, ep, _gate_rec())
    assert any("odd6" in b and "coverage failure" in b for b in bad2)
    assert all(b.startswith("gate 1 olmo13b re-derive") for b in bad)
    assert all(b.startswith("gate 1 olmo13b re-derive") for b in bad2)


# -------------------------------------------------------------- loaders

def test_cache_key_and_clean_dir_writes_config(tmp_path):
    d = bl._cache_dir_13b("stage1-step1000-tokens8B", tmp_path)
    assert d == tmp_path / "olmo13b" / "stage1-step1000-tokens8B"
    src = tmp_path / "raw" / "model-00001-of-00012.safetensors"
    src.parent.mkdir(parents=True)
    src.write_bytes(b"weights")

    class Cfg:
        def to_json_file(self, path):
            Path(path).write_text('{"eos_token_id": 100257}')

    clean = bl.clean_dir_13b("stage1-step1000-tokens8B", tmp_path, {src.name: src}, config=Cfg())
    assert clean == d / "clean"
    assert (clean / src.name).read_bytes() == b"weights"
    assert json.loads((clean / "config.json").read_text())["eos_token_id"] == 100257
    with pytest.raises(TypeError):
        bl.clean_dir_13b("stage1-step1000-tokens8B", tmp_path, {src.name: src})   # config REQUIRED
    bl.free_checkpoint_13b("stage1-step1000-tokens8B", tmp_path)
    assert not d.exists()
    assert bl.CKPT_CACHE_2L == Path.home() / "emergence-lab" / "ckpt_cache_2l"


def test_loader_family_imports_torch_lazily():
    import ast
    src = (bl.EXP2L / "battery_2l.py").read_text()
    tree = ast.parse(src)
    top = [n for n in tree.body if isinstance(n, (ast.Import, ast.ImportFrom))]
    names = {a.name.split(".")[0] for n in top for a in n.names} | \
            {n.module.split(".")[0] for n in top if isinstance(n, ast.ImportFrom) and n.module}
    assert not names & {"torch", "transformers", "huggingface_hub"}


# ---------------------------------------------------------------- pins

def test_frozen_files_2l_list():
    assert set(bk.FROZEN_SHA256_2K) <= set(bl.FROZEN_FILES_2L)
    for rel in bk.INSTRUMENT_BLOBS_2K:
        assert (bl.REPO / rel) in bl.FROZEN_FILES_2L
    assert (bl.EXPERIMENTS / "exp2i" / "run" / "endpoint_2i.py") in bl.FROZEN_FILES_2L
    assert (bl.EXP2L / "power_2l.py") in bl.FROZEN_FILES_2L
    assert (bl.EXP2L / "make_referents_2l.py") in bl.FROZEN_FILES_2L
    for rel in bl.INSTRUMENT_BLOBS_2L:
        assert (bl.REPO / rel) not in bl.FROZEN_FILES_2L      # tag-bound, never sha-pinned
    assert len(bl.FROZEN_FILES_2L) == len(set(bl.FROZEN_FILES_2L))


def test_check_frozen_2l_refuses_unpinned_and_drift(monkeypatch, tmp_path):
    monkeypatch.setattr(bl, "FROZEN_SHA256_2L", {})
    with pytest.raises(RuntimeError, match="not pinned"):
        bl.check_frozen_2l()
    p = tmp_path / "f.py"
    p.write_text("x = 1\n")
    monkeypatch.setattr(bl, "FROZEN_SHA256_2L", {p: bg.sha256_file(p)})
    bl.check_frozen_2l()
    p.write_text("x = 2\n")
    with pytest.raises(RuntimeError, match="drifted"):
        bl.check_frozen_2l()


def test_frozen_from_disk_strict_raises_on_missing(monkeypatch, tmp_path):
    monkeypatch.setattr(bl, "FROZEN_FILES_2L", (tmp_path / "missing.py",))
    with pytest.raises(FileNotFoundError):
        bl.frozen_from_disk()
    assert bl.frozen_from_disk(strict=False) == {}


def test_require_prereg_2l_with_fakes(monkeypatch):
    with pytest.raises(RuntimeError, match="does not exist"):
        bl.require_prereg_2l(tag_exists=lambda t: False, blob_sha=lambda t, r: None)
    present = tuple(r for r in bl.INSTRUMENT_BLOBS_2L if (bl.REPO / r).is_file())
    monkeypatch.setattr(bl, "INSTRUMENT_BLOBS_2L", present)
    ok = bl.require_prereg_2l(tag_exists=lambda t: t == bl.PREREG_TAG_2L,
                              blob_sha=lambda t, r: bg.sha256_file(bl.REPO / r))
    assert ok["tag"] == bl.PREREG_TAG_2L and set(ok["instrument_blobs"]) == set(present)
    with pytest.raises(RuntimeError, match="does not bind"):
        bl.require_prereg_2l(tag_exists=lambda t: True, blob_sha=lambda t, r: "0" * 64)
