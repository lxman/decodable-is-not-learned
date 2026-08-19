"""Unit fixtures for analyze_3d (doc Open item 7): frozen constants
against the design, the §4 pin tables' internal consistency, and every
loader's refusal paths — 3a's valueless-input class refused at load,
executable. The verdict tree's terminals live in full_shape; this
file owns the pieces."""
import gzip
import json

import pytest

from experiments.exp3 import analyze_3 as a3
from experiments.exp3c import analyze_3c as c
from experiments.exp3d import analyze_3d as d
from experiments.exp3d import rank_test_3d as rt
from experiments.exp3d.tests import full_shape as fs


# ------------------------------------------------------------ constants

def test_the_matrix_is_the_designs():
    assert d.RUNG == "reverse_string"
    assert d.SIZES_3D == ("410m", "1b")
    assert d.ADJUDICATING_SIZE == "1b"
    assert d.NEW_SEEDS_3D["1b"] == tuple(range(16, 40))
    assert d.NEW_SEEDS_3D["410m"] == tuple(range(16, 28))
    assert d.DRAWS_PER_SEED_3D == 64
    assert d.K_NEW_3D == {"410m": 768, "1b": 1536}
    assert d.K_BLOCK == 256
    assert d.GATE1_SEED_3D == 8
    assert d.SCORING_RUNGS == ("reverse_string", "ctrl_copy")


def test_seed_blocks_partition_the_seed_sets():
    for size in d.SIZES_3D:
        flat = [s for b in d.SEED_BLOCKS[size] for s in b]
        assert tuple(flat) == d.NEW_SEEDS_3D[size]
        assert all(len(b) == 4 for b in d.SEED_BLOCKS[size])


def test_committed_fire_counts_derive_from_addresses():
    for size in d.SIZES_3D:
        derived = {}
        for ad in d.COMMITTED_FIRES_PIN[size]:
            derived[ad["item"]] = derived.get(ad["item"], 0) + 1
        assert derived == d.COMMITTED_FIRE_COUNTS[size]
    assert sum(d.COMMITTED_FIRE_COUNTS["1b"].values()) == 10
    assert sum(d.COMMITTED_FIRE_COUNTS["410m"].values()) == 3


def test_exp3_fire_is_item_436():
    exp3 = [ad for ad in d.COMMITTED_FIRES_PIN["1b"]
            if ad["source"] == "exp3"]
    assert exp3 == [{"item": 436, "seed": 0, "draw": 6,
                     "source": "exp3"}]
    # and it matches 3c's own frozen pin
    assert c.EXP3_FIRE_ADDRESSES_PIN["reverse_string/1b/trained"] == \
        [{"item": 436, "seed": 0, "draw": 6}]


def test_pins_are_hex_shas():
    for table in (d.FROZEN_IMPORT_SHA256_3D, d.COMMITTED_3C_DRAWS_SHA256,
                  d.ITEMS_SHA_PIN):
        for k, v in table.items():
            assert isinstance(v, str) and len(v) == 64, (k, v)
            int(v, 16)


def test_3c_pins_inherit_exp3_pins_verbatim():
    for path, sha in c.FROZEN_IMPORT_SHA256.items():
        assert d.FROZEN_IMPORT_SHA256_3D[path] == sha


def test_ctrl_gate_band_constants():
    assert d.CTRL_GATE_LOWER_FACTOR == 0.5
    assert d.CTRL_GATE_UPPER_MARGIN == 0.02
    assert d.CTRL_SAMPLED_RATE_PIN["410m"] == {"count": 12787,
                                               "n_draws": 16000}
    assert d.CTRL_SAMPLED_RATE_PIN["1b"] == {"count": 13460,
                                             "n_draws": 16000}


def test_strata_pin():
    assert d.STRATA_PIN == {4: 194, 5: 155, 6: 151}


# --------------------------------------------------------- item loader

def test_load_item_file_refuses_unknown_rung():
    with pytest.raises(ValueError):
        d.load_item_file("clock24_d999")


def test_load_item_file_refuses_wrong_sha(monkeypatch):
    monkeypatch.setitem(d.ITEMS_SHA_PIN, "reverse_string", "0" * 64)
    with pytest.raises(ValueError, match="§4 pin"):
        d.load_item_file("reverse_string")


# ----------------------------------------------------- shard ingestion

@pytest.fixture()
def tree_3d(tmp_path):
    c3 = tmp_path / "exp3c"
    fs.write_3c_tree(c3)
    root = tmp_path / "exp3d"
    fs.write_3d_tree(root, c3, new_fires={"1b": [(0, 16, 0)],
                                          "410m": []})
    return root


def _load(root):
    return d.load_new_cells_3d(root, verify_fn=c.load_verify_3c(),
                               n_items=fs.N)


def test_shards_load_clean(tree_3d):
    out = _load(tree_3d)
    assert out["1b"]["recomputed"]["full_string_total"] == 1
    assert out["1b"]["seeds"] == list(range(16, 40))


def test_missing_shard_refused(tree_3d):
    (tree_3d / "results" / "sampling" / "1b_trained"
     / "reverse_string.s36-s39.json").unlink()
    with pytest.raises(FileNotFoundError):
        _load(tree_3d)


def test_stray_file_refused(tree_3d):
    (tree_3d / "results" / "sampling" / "1b_trained"
     / "reverse_string.s40-s43.json").write_text("{}")
    with pytest.raises(ValueError, match="unexpected file"):
        _load(tree_3d)


def test_untrained_dir_refused(tree_3d):
    p = tree_3d / "results" / "sampling" / "1b_untrained"
    p.mkdir()
    with pytest.raises(ValueError, match="unexpected entry"):
        _load(tree_3d)


def _edit_record(root, size, block, **changes):
    p = (root / "results" / "sampling" / f"{size}_trained"
         / f"{d.shard_name(block)}.json")
    rec = json.loads(p.read_text())
    rec.update(changes)
    p.write_text(json.dumps(rec))


def test_wrong_dtype_refused(tree_3d):
    _edit_record(tree_3d, "1b", (16, 17, 18, 19), dtype="float16")
    with pytest.raises(ValueError, match="float32"):
        _load(tree_3d)


def test_twin_field_refused(tree_3d):
    _edit_record(tree_3d, "1b", (16, 17, 18, 19), untrained_seed=0)
    with pytest.raises(ValueError, match="no twins"):
        _load(tree_3d)


def test_wrong_seeds_refused(tree_3d):
    _edit_record(tree_3d, "1b", (16, 17, 18, 19),
                 seeds=[12, 13, 14, 15])
    with pytest.raises(ValueError, match="preregistered block"):
        _load(tree_3d)


def test_wrong_k_total_refused(tree_3d):
    _edit_record(tree_3d, "1b", (16, 17, 18, 19), k_total=999)
    with pytest.raises(ValueError, match="k_total"):
        _load(tree_3d)


def test_tampered_tally_refused(tree_3d):
    p = (tree_3d / "results" / "sampling" / "1b_trained"
         / "reverse_string.s16-s19.json")
    rec = json.loads(p.read_text())
    rec["per_seed_tallies"]["16"]["full_string"] += 1
    p.write_text(json.dumps(rec))
    with pytest.raises(ValueError, match="disagree with the recompute"):
        _load(tree_3d)


def test_answers_must_agree_across_shards(tree_3d):
    p = (tree_3d / "results" / "sampling" / "1b_trained"
         / "reverse_string.s20-s23.json")
    rec = json.loads(p.read_text())
    rec["answers"] = list(rec["answers"])
    rec["answers"][0] = "zzzz"
    p.write_text(json.dumps(rec))
    with pytest.raises(ValueError, match="other shards"):
        _load(tree_3d)


def test_items_sha_presence_required(tree_3d):
    _edit_record(tree_3d, "410m", (16, 17, 18, 19), items_sha256="")
    with pytest.raises(ValueError, match="items_sha256"):
        _load(tree_3d)


# ------------------------------------------------------- gate-1 loader

def test_gate1_loads_and_refuses(tree_3d):
    recs = d.load_gate1_3d(tree_3d)
    assert recs["1b"]["n_diffs"] == 0
    p = tree_3d / "results" / "gate1" / "1b_trained" \
        / "reverse_string.json"
    rec = json.loads(p.read_text())

    bad = dict(rec, seeds_rederived=[0])
    p.write_text(json.dumps(bad))
    with pytest.raises(ValueError, match="seed 8"):
        d.load_gate1_3d(tree_3d)

    bad = dict(rec, n_diffs=3)
    p.write_text(json.dumps(bad))
    with pytest.raises(ValueError, match="disclosed diffs"):
        d.load_gate1_3d(tree_3d)

    bad = dict(rec, committed_draws_sha256="")
    p.write_text(json.dumps(bad))
    with pytest.raises(ValueError, match="compared against"):
        d.load_gate1_3d(tree_3d)

    bad = dict(rec, draws_compared=7)
    p.write_text(json.dumps(bad))
    with pytest.raises(ValueError, match="compared nothing|against "
                                         "n_items"):
        d.load_gate1_3d(tree_3d)

    bad = dict(rec, diffs=[{"item": 1, "seed": 0, "draw": 2,
                            "got": "x", "committed": "y"}],
               n_diffs=1)
    p.write_text(json.dumps(bad))
    with pytest.raises(ValueError, match="verbatim differing"):
        d.load_gate1_3d(tree_3d)


def test_gate1_committed_sha_loop(tmp_path):
    c3 = tmp_path / "exp3c"
    fs.write_3c_tree(c3)
    root = tmp_path / "exp3d"
    true_shas = fs.write_3d_tree(root, c3, new_fires={"1b": [],
                                                      "410m": []})
    recs = d.load_gate1_3d(root)
    d.check_gate1_committed_shas_3d(recs, c3, expected=true_shas)
    # attestation != disk
    p = root / "results" / "gate1" / "1b_trained" \
        / "reverse_string.json"
    rec = json.loads(p.read_text())
    rec["committed_draws_sha256"] = "f" * 64
    p.write_text(json.dumps(rec))
    with pytest.raises(ValueError, match="finding B"):
        d.check_gate1_committed_shas_3d(d.load_gate1_3d(root), c3,
                                        expected=true_shas)
    # disk != §4 pin
    rec["committed_draws_sha256"] = true_shas["1b"]
    p.write_text(json.dumps(rec))
    with pytest.raises(ValueError, match="literal pin"):
        d.check_gate1_committed_shas_3d(
            d.load_gate1_3d(root), c3,
            expected={"410m": true_shas["410m"], "1b": "f" * 64})


# ------------------------------------------------------ scoring loader

def _scoring_load(root):
    return d.load_scoring_3d(root, items_sha_pin=fs.SYN_ITEMS_SHA,
                             ctrl_rate_pin=fs.SYN_CTRL_RATE,
                             n_items=fs.N)


def test_scoring_loads_clean(tree_3d):
    out = _scoring_load(tree_3d)
    assert out[("ctrl_copy", "1b")]["known_answer_gate"]["passed"]


def test_scoring_missing_record_refused(tree_3d):
    (tree_3d / "results" / "scoring" / "1b_trained"
     / "ctrl_copy.json").unlink()
    with pytest.raises(FileNotFoundError, match="§10 order"):
        _scoring_load(tree_3d)


def _edit_scoring(root, rung, size, **changes):
    p = (root / "results" / "scoring" / f"{size}_trained"
         / f"{rung}.json")
    rec = json.loads(p.read_text())
    rec.update(changes)
    p.write_text(json.dumps(rec))


def test_scoring_gate_fail_is_hard_error(tmp_path):
    c3 = tmp_path / "exp3c"
    fs.write_3c_tree(c3)
    root = tmp_path / "exp3d"
    fs.write_3d_tree(root, c3, new_fires={"1b": [], "410m": []},
                     ctrl_gate_passed=False)
    with pytest.raises(ValueError, match="did not pass"):
        _scoring_load(root)


def test_scoring_span_failures_refused(tree_3d):
    _edit_scoring(tree_3d, "reverse_string", "1b",
                  span_round_trip_failures=2)
    with pytest.raises(ValueError, match="span_round_trip_failures"):
        _scoring_load(tree_3d)


def test_scoring_ell_shape_refused(tree_3d):
    _edit_scoring(tree_3d, "reverse_string", "1b", ell=[-0.1] * 3)
    with pytest.raises(ValueError, match="3a's class"):
        _scoring_load(tree_3d)


def test_scoring_ell_type_refused(tree_3d):
    bad = [-0.1] * fs.N
    bad[4] = "cheap"
    _edit_scoring(tree_3d, "reverse_string", "1b", ell=bad)
    with pytest.raises(ValueError, match="neither a float"):
        _scoring_load(tree_3d)


def test_scoring_wrong_items_sha_refused(tree_3d):
    _edit_scoring(tree_3d, "reverse_string", "1b",
                  items_sha256="not-the-pin")
    with pytest.raises(ValueError, match="§4 pin"):
        _scoring_load(tree_3d)


def test_scoring_gate_referent_mismatch_refused(tree_3d):
    p = (tree_3d / "results" / "scoring" / "1b_trained"
         / "ctrl_copy.json")
    rec = json.loads(p.read_text())
    rec["known_answer_gate"]["committed_count"] = 12345
    p.write_text(json.dumps(rec))
    with pytest.raises(ValueError, match="wrong committed rate"):
        _scoring_load(tree_3d)


# --------------------------------------------- selection + power pins

def test_selection_and_power_pins_refuse_tampering(tmp_path):
    sel_path, power_path = fs.write_selection_and_power(tmp_path)
    _labels, answers = fs.rung_items("reverse_string")
    sel = d.load_selection(answers, sel_path,
                           fired_sets=fs.SYN_FIRED_SETS)
    d.load_power_pin(sel, power_path)

    with pytest.raises(FileNotFoundError):
        d.load_selection(answers, tmp_path / "nope.json",
                         fired_sets=fs.SYN_FIRED_SETS)
    with pytest.raises(FileNotFoundError):
        d.load_power_pin(sel, tmp_path / "nope.json")

    rec = json.loads(sel_path.read_text())
    tam = dict(rec, winner="C4_lz78_phrases")
    sel_path.write_text(json.dumps(tam))
    with pytest.raises(ValueError, match="winner"):
        d.load_selection(answers, sel_path,
                         fired_sets=fs.SYN_FIRED_SETS)

    tam = dict(rec)
    tam["winner_values"] = list(tam["winner_values"])
    tam["winner_values"][0] += 0.5
    sel_path.write_text(json.dumps(tam))
    with pytest.raises(ValueError, match="values disagree"):
        d.load_selection(answers, sel_path,
                         fired_sets=fs.SYN_FIRED_SETS)

    tam = dict(rec)
    tam["decile_bucket"] = list(tam["decile_bucket"])[:-1]
    sel_path.write_text(json.dumps(tam))
    with pytest.raises(ValueError, match="bucket"):
        d.load_selection(answers, sel_path,
                         fired_sets=fs.SYN_FIRED_SETS)

    sel_path.write_text(json.dumps(rec))
    power_path.write_text(json.dumps({"m_min": 7}))
    with pytest.raises(ValueError, match="m_min"):
        d.load_power_pin(sel, power_path)


# ----------------------------------------------------- committed base

def test_committed_base_refuses_pin_mismatch(tmp_path):
    exp3_root = tmp_path / "exp3"
    c3_root = tmp_path / "exp3c"
    fs.write_exp3_tree(exp3_root)
    fs.write_3c_tree(c3_root)
    verify_fn = c.load_verify_3c()
    exp3_cells = a3.load_sampling_cells(exp3_root, verify_fn=verify_fn)
    addresses = c.extract_fire_addresses(exp3_root, exp3_cells,
                                         verify_fn=verify_fn)
    c3_cells = c.load_new_cells(c3_root, verify_fn=verify_fn)
    ref = fs.c3_referent_fires(c3_root)
    base = d.build_committed_base(exp3_cells, c3_cells, addresses,
                                  c3_referent_fires=ref,
                                  fires_pin=fs.SYN_FIRES_PIN,
                                  base_draws_pin=fs.SYN_BASE_DRAWS)
    assert base["1b"]["fires"] == 3
    assert base["twin"]["fires"] == 0

    wrong_pin = {"1b": fs.SYN_FIRES_PIN["1b"][:-1],
                 "410m": fs.SYN_FIRES_PIN["410m"]}
    with pytest.raises(ValueError, match="§4 pin"):
        d.build_committed_base(exp3_cells, c3_cells, addresses,
                               c3_referent_fires=ref,
                               fires_pin=wrong_pin,
                               base_draws_pin=fs.SYN_BASE_DRAWS)

    with pytest.raises(ValueError, match="base draws"):
        d.build_committed_base(exp3_cells, c3_cells, addresses,
                               c3_referent_fires=ref,
                               fires_pin=fs.SYN_FIRES_PIN,
                               base_draws_pin={"1b": 1, "410m": 1})

    bad_ref = {k: dict(v, new={"count": 9, "n_draws": 1})
               for k, v in ref.items()}
    with pytest.raises(ValueError, match="sha-pinned verdict record"):
        d.build_committed_base(exp3_cells, c3_cells, addresses,
                               c3_referent_fires=bad_ref,
                               fires_pin=fs.SYN_FIRES_PIN,
                               base_draws_pin=fs.SYN_BASE_DRAWS)


def test_frozen_imports_refuse_drift(monkeypatch):
    key = next(iter(d.FROZEN_IMPORT_SHA256_3D))
    monkeypatch.setitem(d.FROZEN_IMPORT_SHA256_3D, key, "0" * 64)
    with pytest.raises(ValueError, match="frozen file"):
        d.check_frozen_imports_3d()


def test_committed_base_refuses_twin_fire(tmp_path):
    exp3_root = tmp_path / "exp3"
    c3_root = tmp_path / "exp3c"
    fs.write_exp3_tree(exp3_root, twin_fires={
        ("reverse_string", "410m", "untrained"): [(4, 2, 10)]})
    fs.write_3c_tree(c3_root)
    verify_fn = c.load_verify_3c()
    exp3_cells = a3.load_sampling_cells(exp3_root, verify_fn=verify_fn)
    addresses = c.extract_fire_addresses(exp3_root, exp3_cells,
                                         verify_fn=verify_fn)
    c3_cells = c.load_new_cells(c3_root, verify_fn=verify_fn)
    with pytest.raises(ValueError, match="twin"):
        d.build_committed_base(exp3_cells, c3_cells, addresses,
                               c3_referent_fires=fs.c3_referent_fires(
                                   c3_root),
                               fires_pin=fs.SYN_FIRES_PIN,
                               base_draws_pin=fs.SYN_BASE_DRAWS)


# --------------------------------------------------------- small pieces

def test_ell_cost_values():
    assert d.ell_cost_values([-1.0, None, -3.0]) == \
        [1.0, float("inf"), 3.0]


def test_spearman_directions():
    assert d._spearman([1, 2, 3, 4], [2, 4, 6, 8]) == pytest.approx(1.0)
    assert d._spearman([1, 2, 3, 4], [8, 6, 4, 2]) == \
        pytest.approx(-1.0)


def test_shard_name():
    assert d.shard_name((16, 17, 18, 19)) == "reverse_string.s16-s19"
