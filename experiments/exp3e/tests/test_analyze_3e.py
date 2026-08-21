"""Loader refusals and pin self-consistency for analyze_3e (design §4,
§2): every verdict input is a committed value re-derived at load and
refused on disagreement."""
import gzip
import json

import pytest

from experiments.exp3 import analyze_3 as a3
from experiments.exp3c import analyze_3c as c
from experiments.exp3d import analyze_3d as d
from experiments.exp3e import analyze_3e as e
from experiments.exp3e import scorer_3e as sc
from experiments.exp3e.tests import full_shape as fs


# ------------------------------------------------------------ constants

def test_matrix_literals():
    assert e.NEW_SEEDS_3E["1b"] == tuple(range(40, 168))
    assert e.NEW_SEEDS_3E["410m"] == tuple(range(28, 92))
    assert e.K_NEW_3E == {"410m": 4096, "1b": 8192}
    assert e.K_BLOCK == 1024 and e.BLOCK_DRAWS == 46080
    assert len(e.SEED_BLOCKS["1b"]) == 8 and len(e.SEED_BLOCKS["410m"]) == 4
    assert all(len(b) == 16 for s in e.SIZES_3E for b in e.SEED_BLOCKS[s])
    assert e.COMMITTED_SEEDS["1b"] == tuple(range(40))
    assert e.COMMITTED_SEEDS["410m"] == tuple(range(28))
    assert e.K_COMMITTED == {"410m": 1792, "1b": 2560}
    assert e.GATE1_SEED_3E == {"1b": 20, "410m": 24}
    assert e.GATE1_COVERAGE == 2880


def test_committed_fire_pins_are_self_consistent():
    assert sum(len(v) for v in e.COMMITTED_FIRES_PIN.values()) == 26
    assert {s: len(v) for s, v in e.REPEAT_CLASS_FIRES_PIN.items()} == \
        {"1b": 14, "410m": 5}
    # the 3d-inherited 13 are a subset by value
    for size in e.SIZES_3E:
        got = {(a["item"], a["seed"], a["draw"])
               for a in e.COMMITTED_FIRES_PIN[size]}
        for a in d.COMMITTED_FIRES_PIN[size]:
            assert (a["item"], a["seed"], a["draw"]) in got
    assert e.COMMITTED_FIRE_COUNTS_SUBSET["1b"] == {
        123: 5, 447: 3, 320: 1, 153: 1, 179: 1, 283: 1, 348: 1, 430: 1}
    assert e.COMMITTED_FIRE_COUNTS_SUBSET["410m"] == {
        123: 2, 174: 1, 226: 1, 283: 1}


def test_subset_literal_and_sha():
    assert len(e.SUBSET_ITEMS_PIN) == 45
    assert e.subset_sha256(e.SUBSET_ITEMS_PIN) == e.SUBSET_SHA256_PIN
    assert set(e.NON_REACHABLE_PIN) == {9, 46, 78, 143, 148, 154, 361,
                                        367, 415, 435, 439, 463, 489}
    for a in e.REPEAT_CLASS_FIRES_PIN["1b"] + \
            e.REPEAT_CLASS_FIRES_PIN["410m"]:
        assert a["item"] in e.SUBSET_ITEMS_PIN
        assert a["item"] not in e.NON_REACHABLE_PIN


def test_gate1_expected_fires_are_committed_subset_fires():
    for size in e.SIZES_3E:
        seed = e.GATE1_SEED_3E[size]
        want = sorted(
            [{"item": a["item"], "seed": a["seed"], "draw": a["draw"]}
             for a in e.COMMITTED_FIRES_PIN[size]
             if a["seed"] == seed and a["item"] in e.SUBSET_ITEMS_PIN],
            key=lambda a: (a["item"], a["seed"], a["draw"]))
        assert e.GATE1_EXPECTED_FIRES[size] == want
    assert [a["item"] for a in e.GATE1_EXPECTED_FIRES["1b"]] == [348, 430]
    assert [a["item"] for a in e.GATE1_EXPECTED_FIRES["410m"]] == [123]


# ----------------------------------------------------- shard ingestion

def _world_trees(tmp, new_fires=None, **kw):
    new_fires = new_fires or {"1b": [(0, 40, 0)], "410m": []}
    e3 = fs.write_exp3_tree(tmp / "exp3")
    c3 = fs.write_3c_tree(tmp / "exp3c")
    d3 = fs.write_3d_tree(tmp / "exp3d")
    shas = fs.write_3e_tree(tmp / "exp3e", d3, new_fires=new_fires, **kw)
    return e3, c3, d3, shas


def _load_new(tmp):
    labels, answers = fs.rung_items("reverse_string")
    return e.load_new_cells_3e(tmp / "exp3e", verify_fn=c.load_verify_3c(),
                               items=fs.SUBSET, answers=answers,
                               labels=labels, answer_type_pin="word")


def test_new_cells_load_and_recompute(tmp_path):
    _world_trees(tmp_path)
    cells = _load_new(tmp_path)
    assert cells["1b"]["recomputed"]["n_draws_total"] == 16 * 8192
    assert cells["410m"]["recomputed"]["n_draws_total"] == 16 * 4096
    assert cells["1b"]["recomputed"]["full_string_total"] == 1
    assert cells["1b"]["addresses"][0]["item"] == 0
    assert cells["1b"]["items"] == fs.SUBSET


def test_new_cells_refuse_stray_file(tmp_path):
    _world_trees(tmp_path)
    (tmp_path / "exp3e/results/sampling/1b_trained/extra.json").write_text(
        "{}")
    with pytest.raises(ValueError, match="unexpected"):
        _load_new(tmp_path)


def test_new_cells_refuse_missing_block(tmp_path):
    _world_trees(tmp_path)
    p = tmp_path / "exp3e/results/sampling/410m_trained"
    (p / f"{e.shard_name(e.SEED_BLOCKS['410m'][1])}.json").unlink()
    with pytest.raises(FileNotFoundError):
        _load_new(tmp_path)


def test_new_cells_refuse_tally_disagreement(tmp_path):
    _world_trees(tmp_path)
    p = (tmp_path / "exp3e/results/sampling/1b_trained"
         / f"{e.shard_name(e.SEED_BLOCKS['1b'][0])}.json")
    rec = json.loads(p.read_text())
    rec["per_seed_tallies"]["40"]["full_string"] += 1
    p.write_text(json.dumps(rec))
    with pytest.raises(ValueError, match="disagree with the recompute"):
        _load_new(tmp_path)


def test_new_cells_refuse_wrong_items(tmp_path):
    _world_trees(tmp_path)
    p = (tmp_path / "exp3e/results/sampling/1b_trained"
         / f"{e.shard_name(e.SEED_BLOCKS['1b'][0])}.json")
    rec = json.loads(p.read_text())
    rec["items"] = rec["items"][:-1] + [17]
    p.write_text(json.dumps(rec))
    with pytest.raises(ValueError, match="items"):
        _load_new(tmp_path)


def test_new_cells_refuse_row_outside_subset(tmp_path):
    _world_trees(tmp_path)
    gz = (tmp_path / "exp3e/results/sampling/1b_trained"
          / f"{e.shard_name(e.SEED_BLOCKS['1b'][0])}.draws.jsonl.gz")
    with gzip.open(gz, "rt") as f:
        rows = [json.loads(l) for l in f]
    rows[0]["item"] = 17
    with gzip.open(gz, "wt") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    with pytest.raises(ValueError, match="not in the preregistered"):
        _load_new(tmp_path)


def test_frozen_import_pins_refuse_a_changed_byte(monkeypatch):
    e.check_frozen_imports_3e()          # the real pins, clean
    bad = dict(e.FROZEN_IMPORT_SHA256_3E)
    first = next(iter(bad))
    bad[first] = "0" * 64
    monkeypatch.setattr(e, "FROZEN_IMPORT_SHA256_3E", bad)
    with pytest.raises(ValueError, match="frozen file"):
        e.check_frozen_imports_3e()


def test_new_cells_refuse_answer_type_drift(tmp_path):
    _world_trees(tmp_path)
    labels, answers = fs.rung_items("reverse_string")
    with pytest.raises(ValueError, match="answer_type"):
        e.load_new_cells_3e(tmp_path / "exp3e",
                            verify_fn=c.load_verify_3c(),
                            items=fs.SUBSET, answers=answers,
                            labels=labels, answer_type_pin="letters")


def test_new_cells_refuse_twin_shard(tmp_path):
    _world_trees(tmp_path)
    p = (tmp_path / "exp3e/results/sampling/1b_trained"
         / f"{e.shard_name(e.SEED_BLOCKS['1b'][0])}.json")
    rec = json.loads(p.read_text())
    rec["untrained_seed"] = 0
    p.write_text(json.dumps(rec))
    with pytest.raises(ValueError, match="twin"):
        _load_new(tmp_path)


# ----------------------------------------------------- gate-1 records

def _load_gate1(tmp, **kw):
    return e.load_gate1_3e(tmp / "exp3e", items=fs.SUBSET,
                           expected_fires={s: fs.e_expected_gate1_fires(s)
                                           for s in e.SIZES_3E}, **kw)


def test_gate1_loads_clean(tmp_path):
    _e3, _c3, _d3, shas = _world_trees(tmp_path)
    g = _load_gate1(tmp_path)
    assert g["1b"]["n_diffs"] == 0
    assert g["1b"]["draws_compared"] == 16 * 64
    e.check_gate1_committed_shas_3e(g, tmp_path / "exp3d", expected=shas)


def test_gate1_refuses_coverage_not_pinned(tmp_path):
    _world_trees(tmp_path)
    p = tmp_path / "exp3e/results/gate1/1b_trained/reverse_string.json"
    rec = json.loads(p.read_text())
    rec["n_items"] = 15
    rec["items"] = rec["items"][:15]
    rec["draws_compared"] = 15 * 64
    p.write_text(json.dumps(rec))
    with pytest.raises(ValueError, match="subset"):
        _load_gate1(tmp_path)


def test_gate1_refuses_wrong_seed(tmp_path):
    _world_trees(tmp_path)
    p = tmp_path / "exp3e/results/gate1/410m_trained/reverse_string.json"
    rec = json.loads(p.read_text())
    rec["seeds_rederived"] = [8]
    p.write_text(json.dumps(rec))
    with pytest.raises(ValueError, match="seed"):
        _load_gate1(tmp_path)


def test_gate1_refuses_unreproduced_fires(tmp_path):
    _world_trees(tmp_path)
    p = tmp_path / "exp3e/results/gate1/1b_trained/reverse_string.json"
    rec = json.loads(p.read_text())
    rec["fires_reproduced"] = []
    p.write_text(json.dumps(rec))
    with pytest.raises(ValueError, match="fires_reproduced"):
        _load_gate1(tmp_path)


def test_gate1_attested_sha_checked_against_disk_and_literal(tmp_path):
    _e3, _c3, _d3, shas = _world_trees(tmp_path)
    g = _load_gate1(tmp_path)
    bad = dict(shas)
    bad["1b"] = "0" * 64
    with pytest.raises(ValueError, match="literal"):
        e.check_gate1_committed_shas_3e(g, tmp_path / "exp3d",
                                        expected=bad)
    p = tmp_path / "exp3e/results/gate1/1b_trained/reverse_string.json"
    rec = json.loads(p.read_text())
    rec["committed_draws_sha256"] = "1" * 64
    p.write_text(json.dumps(rec))
    g2 = _load_gate1(tmp_path)
    with pytest.raises(ValueError, match="attest"):
        e.check_gate1_committed_shas_3e(g2, tmp_path / "exp3d",
                                        expected=shas)


# ------------------------------------------------- scorer-gate record

def test_scorer_gates_record_loads_and_refuses_failure(tmp_path):
    _world_trees(tmp_path)
    rec = e.load_scorer_gates_3e(tmp_path / "exp3e",
                                 fires_pin=fs.syn_repeat_class_fires(),
                                 ctrl_pin=fs.SYN_CTRL_RATE)
    assert rec["passed"] is True
    p = tmp_path / "exp3e/results/scorer_gates.json"
    r = json.loads(p.read_text())
    r["gate_a"]["passed"] = False
    r["passed"] = False
    p.write_text(json.dumps(r))
    with pytest.raises(ValueError, match="did not pass"):
        e.load_scorer_gates_3e(tmp_path / "exp3e",
                               fires_pin=fs.syn_repeat_class_fires(),
                               ctrl_pin=fs.SYN_CTRL_RATE)


def test_scorer_gates_record_refuses_wrong_referent(tmp_path):
    _world_trees(tmp_path)
    p = tmp_path / "exp3e/results/scorer_gates.json"
    r = json.loads(p.read_text())
    r["gate_a"]["addresses"]["1b"] = r["gate_a"]["addresses"]["1b"][:-1]
    p.write_text(json.dumps(r))
    with pytest.raises(ValueError, match="pin"):
        e.load_scorer_gates_3e(tmp_path / "exp3e",
                               fires_pin=fs.syn_repeat_class_fires(),
                               ctrl_pin=fs.SYN_CTRL_RATE)


def test_scorer_gates_record_missing(tmp_path):
    with pytest.raises(FileNotFoundError):
        e.load_scorer_gates_3e(tmp_path, fires_pin={}, ctrl_pin={})


# ------------------------------------------------ committed rows + base

def _draws_pins(e3, c3, d3):
    return {
        "reverse_string": {
            size: {"exp3": e3[("reverse_string", size, "trained")],
                   "3c": c3[("reverse_string", size, "trained")],
                   "3d": {d.shard_name(b): d3[(size, b)]
                          for b in d.SEED_BLOCKS[size]}}
            for size in e.SIZES_3E},
        "ctrl_copy": {size: e3[(a3.POSITIVE_CONTROL, size, "trained")]
                      for size in e.SIZES_3E},
    }


def test_committed_rows_load_and_refuse_sha_drift(tmp_path):
    e3, c3, d3, _ = _world_trees(tmp_path)
    roots = {"exp3": tmp_path / "exp3", "3c": tmp_path / "exp3c",
             "3d": tmp_path / "exp3d"}
    rows = e.load_committed_rows(roots=roots, n_items=fs.N,
                                 draws_pins=_draws_pins(e3, c3, d3))
    assert set(rows["reverse_string"]["1b"]) == set(range(fs.N))
    assert set(rows["reverse_string"]["1b"][0]) == \
        {str(s) for s in range(40)}
    assert len(rows["reverse_string"]["410m"][0]["0"]) == 64
    assert len(rows["ctrl_copy"]["1b"][0]["0"]) == 8
    pins = _draws_pins(e3, c3, d3)
    pins["reverse_string"]["1b"]["3c"] = "0" * 64
    with pytest.raises(ValueError, match="sha256"):
        e.load_committed_rows(roots=roots, n_items=fs.N, draws_pins=pins)


def test_committed_base_reproduces_pin_and_refuses_drift(tmp_path):
    e3, c3, d3, _ = _world_trees(tmp_path)
    roots = {"exp3": tmp_path / "exp3", "3c": tmp_path / "exp3c",
             "3d": tmp_path / "exp3d"}
    rows = e.load_committed_rows(roots=roots, n_items=fs.N,
                                 draws_pins=_draws_pins(e3, c3, d3))
    _l, answers = fs.rung_items("reverse_string")
    ctrl = fs.rung_items(a3.POSITIVE_CONTROL)[1]
    base = e.committed_base_3e(rows, answers, "word", sc.load_scorer(),
                               fires_pin=fs.SYN_COMMITTED_FIRES,
                               subset=fs.SUBSET, ctrl_answers=ctrl)
    assert base["1b"]["per_item"][0] == 3
    assert base["1b"]["n_draws_per_item"] == 2560
    assert base["410m"]["n_draws_per_item"] == 1792
    assert base["1b"]["subset_addresses"] == \
        fs.syn_repeat_class_fires()["1b"]
    assert base["ctrl_gate_b"]["1b"] == {"count": 19 * fs.N,
                                         "n_draws": 32 * fs.N}
    bad = {s: tuple(list(v)[:-1]) for s, v in
           fs.SYN_COMMITTED_FIRES.items()}
    with pytest.raises(ValueError, match="pin"):
        e.committed_base_3e(rows, answers, "word", sc.load_scorer(),
                            fires_pin=bad, subset=fs.SUBSET,
                            ctrl_answers=ctrl)


def test_twin_record_from_exp3_loader(tmp_path):
    _world_trees(tmp_path)
    t = e.load_twin_record(tmp_path / "exp3", verify_fn=c.load_verify_3c(),
                           pins={"reversal": 4 * fs.N * 256,
                                 "control": 4 * fs.N * 32})
    assert t["fires"] == 0 and t["cells"] == 8
    with pytest.raises(ValueError, match="twin"):
        e.load_twin_record(tmp_path / "exp3", verify_fn=c.load_verify_3c(),
                           pins={"reversal": 1, "control": 1})


# ------------------------------------------------- partition + power

def test_partition_loader_pins_subset_and_file_sha(tmp_path):
    _l, answers = fs.rung_items("reverse_string")
    part_path, power_path = fs.write_partition_and_power(tmp_path)
    p = e.load_partition_3e(answers, part_path, subset_pin=fs.SUBSET,
                            file_sha_pin=None)
    assert p["reachable"] == fs.REACHABLE
    assert p["arm_items"] == fs.ARM_ITEMS
    with pytest.raises(ValueError, match="subset"):
        e.load_partition_3e(answers, part_path, subset_pin=fs.SUBSET[:-1],
                            file_sha_pin=None)
    with pytest.raises(ValueError, match="sha256"):
        e.load_partition_3e(answers, part_path, subset_pin=fs.SUBSET,
                            file_sha_pin="0" * 64)
    pin = e.load_power_pin_3e(p, power_path)
    assert pin["m_min"] == 7 and pin["m_s_min"] == 3
    rec = json.loads(power_path.read_text())
    rec["m_min"] = 6
    power_path.write_text(json.dumps(rec))
    with pytest.raises(ValueError, match="m_min"):
        e.load_power_pin_3e(p, power_path)


# -------------------------------------------------------- stream map

def test_stream_map_round_trip_and_continuity(tmp_path):
    p = tmp_path / "map.json"
    e.dump_stream_map_3e(p)
    m = e.check_stream_map_3e(p)
    assert m["new_seeds"]["1b"] == list(range(40, 168))
    assert len(m["subset_streams"]["1b"]) == 168
    assert len(m["subset_streams"]["1b"]["s20"]) == 45
    rec = json.loads(p.read_text())
    rec["subset_streams"]["1b"]["s20"]["123"] += 1
    p.write_text(json.dumps(rec))
    with pytest.raises(ValueError, match="formula"):
        e.check_stream_map_3e(p)


def test_committed_stream_map_checks_clean():
    e.check_stream_map_3e()
