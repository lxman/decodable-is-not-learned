"""checkpoints_2g on the COMMITTED inventory (no network): the
candidate rule, finding A/B exclusions, the manifest, the loader's
pure parts."""
import json

import pytest

from experiments.exp2g import battery_2g as bg
from experiments.exp2g import checkpoints_2g as ck


@pytest.fixture(scope="module")
def inv():
    return ck.load_inventory()


def test_inventory_shape(inv):
    assert set(inv) == {"EleutherAI/pythia-2.8b", "EleutherAI/pythia-12b"}
    assert all(len(v) == 155 for v in inv.values())
    assert inv["EleutherAI/pythia-2.8b"]["main"]["commit"] == \
        "2a259cdd96a4beb1cdf467512e3904197345f6a9"


def test_candidate_rule():
    main = {"model.safetensors": ["AAA", 1], "pytorch_model.bin": ["BBB", 1]}
    # sharded branch with stale singles -> shards
    c = ck.candidate("step1000", {"model-00001-of-00002.safetensors": ["S1", 1],
                                  "model-00002-of-00002.safetensors": ["S2", 1],
                                  "model.safetensors": ["AAA", 1],
                                  "pytorch_model.bin": ["BBB", 1]}, main)
    assert c["kind"] == "safetensors-shards"
    assert c["files"] == ["model-00001-of-00002.safetensors",
                          "model-00002-of-00002.safetensors",
                          "model.safetensors.index.json"]
    # single safetensors == main's -> the bin
    c = ck.candidate("step30000", {"model.safetensors": ["AAA", 1],
                                   "pytorch_model.bin": ["CCC", 1]}, main)
    assert c["kind"] == "bin" and c["lfs"] == ["pytorch_model.bin"]
    # single safetensors with its own sha -> it
    c = ck.candidate("step143000", {"model.safetensors": ["DDD", 1],
                                    "pytorch_model.bin": ["EEE", 1]}, main)
    assert c["kind"] == "safetensors-single"
    # main itself keeps its safetensors
    assert ck.candidate("main", main, main)["kind"] == "safetensors-single"
    # 12b-style bin shards
    c = ck.candidate("step1000", {"pytorch_model-00001-of-00003.bin": ["a", 1],
                                  "pytorch_model-00002-of-00003.bin": ["b", 1],
                                  "pytorch_model-00003-of-00003.bin": ["c", 1]},
                     {"model-00001-of-00003.safetensors": ["x", 1]})
    assert c["kind"] == "bin-shards" and c["files"][-1] == "pytorch_model.bin.index.json"
    assert ck.candidate("stepX", {}, main) is None


def test_manifest_2_8b(inv):
    m = ck.build_manifest("2.8b", inv)
    assert m["main_commit"] == "2a259cdd96a4beb1cdf467512e3904197345f6a9"
    assert sorted(int(k) for k in m["entries"]) == sorted(bg.GRID["2.8b"])
    assert len(m["entries"]) == 22
    kinds = {int(k): v["kind"] for k, v in m["entries"].items()}
    assert all(kinds[s] == "safetensors-shards" for s in bg.GRID["2.8b"] if s <= 20000)
    assert all(kinds[s] == "bin" for s in bg.GRID["2.8b"] if 30000 <= s <= 140000)
    assert kinds[143000] == "safetensors-single"
    assert m["entries"]["143000"]["revision"] == "main"
    assert m["entries"]["1000"]["lfs_sha256"]["model-00001-of-00002.safetensors"].startswith("f6a6c2f8")
    assert m["excluded"] == {"64000": bg.EXCLUDED_GRID["2.8b"][64000]}
    assert m["exclusion_evidence"]["64000"]["duplicates"][:2] == ["step54000", "step56000"]
    assert m["hub_step143000"]["signature_equals_main"] is False
    assert m["stale_main_copies"]["model.safetensors"] == 76   # 77 incl. main itself
    assert m["stale_main_copies"]["pytorch_model.bin"] == 39


def test_manifest_12b(inv):
    m = ck.build_manifest("12b", inv)
    assert sorted(int(k) for k in m["entries"]) == sorted(bg.GRID["12b"])
    assert all(v["kind"] == "bin-shards" for k, v in m["entries"].items() if k != "143000")
    assert m["entries"]["143000"]["kind"] == "safetensors-shards"
    assert m["hub_step143000"]["signature_equals_main"] is True
    assert m["excluded"] == {}
    # main carries safetensors shards only (no plain model.safetensors or
    # pytorch_model.bin), so a stale-copy match against an absent file
    # must not be counted (M-3)
    assert m["stale_main_copies"] == {"model.safetensors": 0, "pytorch_model.bin": 0}


def test_manifest_refuses_a_duplicate_grid_point(inv):
    bad = json.loads(json.dumps(inv))
    repo = "EleutherAI/pythia-2.8b"
    bad[repo]["step30000"]["files"] = dict(bad[repo]["step40000"]["files"])
    with pytest.raises(ValueError, match="duplicate"):
        ck.build_manifest("2.8b", bad)


def test_manifest_refuses_an_unjustified_exclusion(inv, monkeypatch):
    monkeypatch.setattr(bg, "EXCLUDED_GRID", {"2.8b": {60000: "no reason"}, "12b": {}})
    monkeypatch.setattr(bg, "GRID", {"2.8b": tuple(s for s in bg.GRID["2.8b"] if s != 60000) + (60000,), "12b": bg.GRID["12b"]})
    with pytest.raises(ValueError, match="exclusion"):
        ck.build_manifest("2.8b", inv)


def test_write_and_load_roundtrip(inv, tmp_path):
    obj = ck.build_all(inv)
    p = tmp_path / "m.json"
    ck.write_manifest(p, obj)
    got = ck.load_manifest(p, sha_pin=bg.sha256_file(p))
    assert got == obj
    with pytest.raises(ValueError):
        ck.load_manifest(p, sha_pin="0" * 64)
    e = ck.entry_for(got, "2.8b", 1000)
    assert e["revision"] == "step1000" and e["files"][-1].endswith("index.json")


def test_load_manifest_refuses_a_stale_grid(inv, tmp_path):
    obj = ck.build_all(inv)
    obj = dict(obj)
    obj["2.8b"] = dict(obj["2.8b"])
    obj["2.8b"]["grid"] = list(obj["2.8b"]["grid"])[:-1]      # drop one step
    p = tmp_path / "m.json"
    ck.write_manifest(p, obj)
    # the sha_pin matches the file exactly written -- the failure has
    # to come from the grid check, not the hash check
    with pytest.raises(ValueError, match="frozen grid"):
        ck.load_manifest(p, sha_pin=bg.sha256_file(p))


def test_committed_manifest_matches_inventory(inv):
    obj = ck.load_manifest(bg.CHECKPOINTS_PATH, sha_pin=None)
    assert obj == ck.build_all(inv)


def test_tensor_digest_is_order_and_value_sensitive():
    import torch
    m = torch.nn.Linear(3, 2).half()
    a = ck.tensor_digest(m)
    assert a == ck.tensor_digest(m)
    with torch.no_grad():
        m.weight[0, 0] += 1
    assert ck.tensor_digest(m) != a
