"""Unit fixtures for analyze_3c (doc Open items 1, 2, 4): constants,
the frozen-file pins, the CP/rate helpers, the raw-draw readers, and
every loader's refusal paths — 3a's valueless-input class refused at
load, executable. The verdict tree's terminals live in full_shape;
this file owns the pieces.
"""
import gzip
import json

import pytest

from experiments.exp3 import analyze_3 as a3
from experiments.exp3c import analyze_3c as c
from experiments.exp3c.tests import full_shape as fs


# ------------------------------------------------------------ constants

def test_the_matrix_is_the_designs():
    assert c.SCORED_CELLS == (
        ("rev_string7", "410m", "trained"),
        ("rev_string7", "1b", "trained"),
        ("reverse_string", "410m", "trained"),
        ("reverse_string", "1b", "trained"))
    assert c.GATE1_CELLS == c.SCORED_CELLS + \
        (("ctrl_copy", "1b", "trained"),)
    assert c.FIRED_CELL == ("reverse_string", "1b", "trained")
    assert len(c.WALLED_CELLS) == 3
    assert c.FIRED_CELL not in c.WALLED_CELLS


def test_the_exp3_fire_pin_is_the_committed_one():
    assert c.EXP3_FIRE_ADDRESSES_PIN["reverse_string/1b/trained"] == \
        [{"item": 436, "seed": 0, "draw": 6}]
    assert all(v == [] for k, v in c.EXP3_FIRE_ADDRESSES_PIN.items()
               if k != "reverse_string/1b/trained")
    assert c.EXP3_FIRE_ANSWER_LENGTHS_PIN["reverse_string/1b/trained"] \
        == [4]


def test_twin_referent_constants():
    assert len(c.TWIN_CELLS) == 8
    assert all(m == "untrained" for (_r, _s, m) in c.TWIN_CELLS)
    assert c.TWIN_REVERSAL_DRAWS == 512_000
    assert c.TWIN_CONTROL_DRAWS == 64_000


# ---------------------------------------------------------- frozen pins

def test_frozen_imports_pass_on_the_committed_tree():
    c.check_frozen_imports()


def test_frozen_import_drift_is_refused(monkeypatch):
    key = a3.EXP3 / "sampler.py"
    monkeypatch.setitem(c.FROZEN_IMPORT_SHA256, key, "0" * 64)
    with pytest.raises(ValueError, match="frozen file"):
        c.check_frozen_imports()


# --------------------------------------------------------- pure helpers

def test_luck_floor_values():
    assert abs(c.luck_floor(4) - 2.1882987290360982e-06) < 1e-18
    assert abs(c.luck_floor(4) - 26.0 ** -4) < 1e-18
    assert abs(c.luck_floor(7) - 26.0 ** -7) < 1e-20
    for bad in (0, -3, "4", 2.5):
        with pytest.raises(ValueError):
            c.luck_floor(bad)


def test_rate_entry_zero_ships_as_a_bound():
    e = c.rate_entry(0, 384_000)
    assert e["rate"] == 0.0
    assert abs(e["cp95_upper"] - a3.cp_upper(0, 384_000)) < 1e-15
    assert "ci95" not in e


def test_rate_entry_nonzero_ships_a_two_sided_ci():
    e = c.rate_entry(1, 512_000)
    lo, hi = a3.clopper_pearson(1, 512_000)
    assert e["ci95"] == [lo, hi]
    assert "cp95_upper" not in e
    assert abs(e["rate"] - 1.953125e-6) < 1e-12


def test_rate_entry_refuses_impossible_counts():
    with pytest.raises(ValueError):
        c.rate_entry(2, 1)
    with pytest.raises(ValueError):
        c.rate_entry(0, 0)
    with pytest.raises(ValueError):
        c.rate_entry(-1, 10)


def test_strata_of_partitions_by_answer_length():
    s = c.strata_of(["abcd", "efghi", "jklm", "nopqrs"])
    assert s == {4: [0, 2], 5: [1], 6: [3]}


# ------------------------------------------------------ raw-draw reader

def _write_rows(path, rows):
    with gzip.open(path, "wt") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")


GOOD_ROWS = [{"item": i, "draws": {str(s): [" x"] * 2
                                   for s in (4, 5)}} for i in range(3)]


def test_read_rows_roundtrip(tmp_path):
    p = tmp_path / "d.jsonl.gz"
    _write_rows(p, GOOD_ROWS)
    rows = c._read_rows(p, 3, (4, 5), 2)
    assert [r["item"] for r in rows] == [0, 1, 2]


def test_read_rows_refuses_duplicates(tmp_path):
    p = tmp_path / "d.jsonl.gz"
    _write_rows(p, GOOD_ROWS + [GOOD_ROWS[0]])
    with pytest.raises(ValueError, match="duplicate"):
        c._read_rows(p, 4, (4, 5), 2)


def test_read_rows_refuses_wrong_seed_sets(tmp_path):
    p = tmp_path / "d.jsonl.gz"
    _write_rows(p, [{"item": 0, "draws": {"0": [" x"] * 2,
                                          "5": [" x"] * 2}}])
    with pytest.raises(ValueError, match="preregistered seeds"):
        c._read_rows(p, 1, (4, 5), 2)


def test_read_rows_refuses_short_streams(tmp_path):
    p = tmp_path / "d.jsonl.gz"
    _write_rows(p, [{"item": 0, "draws": {"4": [" x"],
                                          "5": [" x"] * 2}}])
    with pytest.raises(ValueError, match="draws against draws_per_seed"):
        c._read_rows(p, 1, (4, 5), 2)


def test_read_rows_refuses_nonstring_draws(tmp_path):
    p = tmp_path / "d.jsonl.gz"
    _write_rows(p, [{"item": 0, "draws": {"4": [" x", 7],
                                          "5": [" x"] * 2}}])
    with pytest.raises(ValueError):
        c._read_rows(p, 1, (4, 5), 2)


def test_read_rows_refuses_incomplete_coverage(tmp_path):
    p = tmp_path / "d.jsonl.gz"
    _write_rows(p, GOOD_ROWS[:2])
    with pytest.raises(ValueError, match="distinct items"):
        c._read_rows(p, 3, (4, 5), 2)


# ------------------------------------------------- tally with addresses

def test_tally_counts_fires_first_chars_and_addresses():
    import harness

    rows = [{"item": 0, "draws": {"4": [" qvux", " qzzz"],
                                  "5": [" ~z", " ~z"]}},
            {"item": 1, "draws": {"4": [" ~z", " ~z"],
                                  "5": [" ~z", " abcd"]}}]
    t = c.tally_with_addresses(rows, ["qvux", "abcd"], ["q", "a"],
                               (4, 5), answer_type="word",
                               verify_fn=harness.verify)
    assert t["per_seed"]["4"] == {"full_string": 1, "first_char": 2,
                                  "n_draws": 4}
    assert t["per_seed"]["5"] == {"full_string": 1, "first_char": 1,
                                  "n_draws": 4}
    assert t["addresses"] == [
        {"item": 0, "seed": 4, "draw": 0, "text": " qvux"},
        {"item": 1, "seed": 5, "draw": 1, "text": " abcd"}]
    assert t["per_item_full_string"] == [1, 1]
    assert t["total_draw_len"] == sum(
        len(d) for r in rows for s in ("4", "5") for d in r["draws"][s])


# ------------------------------------------------------- new-cell loader

def _new_tree(tmp_path, **kw):
    return fs.write_world(tmp_path / "w", **kw)["root"] / "exp3c"


def _doctor(root, rung="reverse_string", size="1b", **changes):
    p = root / "results" / "sampling" / f"{size}_trained" / f"{rung}.json"
    rec = json.loads(p.read_text())
    rec.update(changes)
    p.write_text(json.dumps(rec))


def test_load_new_cells_happy_path(tmp_path):
    import harness

    root = _new_tree(tmp_path,
                     new_fires={c.FIRED_CELL: [(0, 4, 0)]})
    cells = c.load_new_cells(root, verify_fn=harness.verify)
    assert set(cells) == set(c.SCORED_CELLS)
    rc = cells[c.FIRED_CELL]["recomputed"]
    assert rc["full_string_total"] == 1
    assert rc["n_draws_total"] == fs.N * c.K_NEW
    assert cells[c.FIRED_CELL]["addresses"][0]["item"] == 0
    assert cells[c.FIRED_CELL]["mean_draw_len"] > 0


def test_load_new_cells_refuses_wrong_seed_field(tmp_path):
    import harness

    root = _new_tree(tmp_path)
    _doctor(root, seeds=list(range(12)))
    with pytest.raises(ValueError, match="preregistered new seeds"):
        c.load_new_cells(root, verify_fn=harness.verify)


def test_load_new_cells_refuses_wrong_dps_field(tmp_path):
    import harness

    root = _new_tree(tmp_path)
    _doctor(root, draws_per_seed=32)
    with pytest.raises(ValueError, match="draws_per_seed"):
        c.load_new_cells(root, verify_fn=harness.verify)


def test_load_new_cells_refuses_wrong_k_total(tmp_path):
    import harness

    root = _new_tree(tmp_path)
    _doctor(root, k_total=512)
    with pytest.raises(ValueError, match="k_total"):
        c.load_new_cells(root, verify_fn=harness.verify)


def test_load_new_cells_refuses_wrong_dtype(tmp_path):
    import harness

    root = _new_tree(tmp_path)
    _doctor(root, dtype="float16")
    with pytest.raises(ValueError, match="float32"):
        c.load_new_cells(root, verify_fn=harness.verify)


def test_load_new_cells_refuses_twin_seed_on_trained(tmp_path):
    import harness

    root = _new_tree(tmp_path)
    _doctor(root, untrained_seed=0)
    with pytest.raises(ValueError, match="samples no twins"):
        c.load_new_cells(root, verify_fn=harness.verify)


def test_load_new_cells_refuses_stored_tally_disagreement(tmp_path):
    import harness

    root = _new_tree(tmp_path)
    p = (root / "results" / "sampling" / "1b_trained"
         / "reverse_string.json")
    rec = json.loads(p.read_text())
    rec["per_seed_tallies"]["7"]["full_string"] += 1
    p.write_text(json.dumps(rec))
    with pytest.raises(ValueError, match="disagree with the recompute"):
        c.load_new_cells(root, verify_fn=harness.verify)


def test_load_new_cells_refuses_stray_files(tmp_path):
    import harness

    root = _new_tree(tmp_path)
    (root / "results" / "sampling" / "1b_trained"
     / "extra.json").write_text("{}")
    with pytest.raises(ValueError, match="unexpected file"):
        c.load_new_cells(root, verify_fn=harness.verify)


def test_load_new_cells_refuses_missing_draws_file(tmp_path):
    import harness

    root = _new_tree(tmp_path)
    (root / "results" / "sampling" / "1b_trained"
     / "reverse_string.draws.jsonl.gz").unlink()
    with pytest.raises(FileNotFoundError, match="raw draws"):
        c.load_new_cells(root, verify_fn=harness.verify)


# ------------------------------------------------------ gate-1 loader

def _doctor_gate1(root, rung="reverse_string", size="1b", **changes):
    p = root / "results" / "gate1" / f"{size}_trained" / f"{rung}.json"
    rec = json.loads(p.read_text())
    rec.update(changes)
    p.write_text(json.dumps(rec))


def test_gate1_loader_happy_path(tmp_path):
    root = _new_tree(tmp_path)
    recs = c.load_gate1_records(root)
    assert set(recs) == set(c.GATE1_CELLS)
    assert all(r["n_diffs"] == 0 for r in recs.values())


def test_gate1_loader_refuses_wrong_rederive_seed(tmp_path):
    root = _new_tree(tmp_path)
    _doctor_gate1(root, seeds_rederived=[1])
    with pytest.raises(ValueError, match="seed 0 only"):
        c.load_gate1_records(root)


def test_gate1_loader_refuses_wrong_depth_for_the_control(tmp_path):
    """PROGRESS.md reading 1: a 64-draw ctrl_copy 're-derivation'
    compares against nothing committed and is refused."""
    root = _new_tree(tmp_path)
    _doctor_gate1(root, rung="ctrl_copy", size="1b",
                  draws_per_seed=64, draws_compared=64 * fs.N)
    with pytest.raises(ValueError, match="not byte-comparable"):
        c.load_gate1_records(root)


def test_gate1_loader_refuses_zero_or_mismatched_volume(tmp_path):
    root = _new_tree(tmp_path)
    _doctor_gate1(root, draws_compared=0)
    with pytest.raises(ValueError, match="compared nothing"):
        c.load_gate1_records(root)


def test_gate1_loader_refuses_undisclosed_diff_counts(tmp_path):
    root = _new_tree(tmp_path)
    _doctor_gate1(root, n_diffs=2)
    with pytest.raises(ValueError, match="disclosed diffs"):
        c.load_gate1_records(root)


def test_gate1_loader_refuses_malformed_diff_entries(tmp_path):
    root = _new_tree(tmp_path)
    _doctor_gate1(root, n_diffs=1,
                  diffs=[{"item": 0, "seed": 3, "draw": 1,
                          "got": "x", "committed": "y"}])
    with pytest.raises(ValueError, match="verbatim differing draw"):
        c.load_gate1_records(root)


def test_gate1_loader_refuses_missing_committed_sha(tmp_path):
    root = _new_tree(tmp_path)
    _doctor_gate1(root, committed_draws_sha256="")
    with pytest.raises(ValueError, match="compared against"):
        c.load_gate1_records(root)


def test_gate1_loader_refuses_wrong_dtype(tmp_path):
    root = _new_tree(tmp_path)
    _doctor_gate1(root, dtype="float16")
    with pytest.raises(ValueError, match="float32"):
        c.load_gate1_records(root)


# ------------------------------------------------- exp3-side referents

def test_load_exp3_referent_matches_the_committed_pins():
    ref = c.load_exp3_referent()
    assert ref["fires"]["reverse_string/1b/trained"] == \
        {"full_string_total": 1, "n_draws": 128_000}
    assert ref["fires"]["rev_string7/410m/trained"] == \
        {"full_string_total": 0, "n_draws": 128_000}
    for (r, s, m) in c.TWIN_CELLS:
        assert ref["fires"][f"{r}/{s}/{m}"]["full_string_total"] == 0
    assert sum(ref["fires"][f"{r}/{s}/untrained"]["n_draws"]
               for r in c.REVERSAL_RUNGS for s in c.PROBE_SIZES) \
        == c.TWIN_REVERSAL_DRAWS
    assert ref["fire_addresses"] == c.EXP3_FIRE_ADDRESSES_PIN


def test_load_exp3_referent_refuses_sha_drift():
    with pytest.raises(ValueError, match="changed after the pin"):
        c.load_exp3_referent(expected_sha="0" * 64)


def test_load_exp3_referent_refuses_valueless_tables(tmp_path):
    import hashlib

    p = tmp_path / "verdict.json"
    p.write_text(json.dumps({"fires": {"reverse_string/1b/trained":
                                       {"full_string_total": 1}}}))
    sha = hashlib.sha256(p.read_bytes()).hexdigest()
    with pytest.raises(ValueError, match="no usable entry"):
        c.load_exp3_referent(p, expected_sha=sha)


# ------------------------------------------------------------- prompts

def test_load_prompts_matches_the_runners_construction():
    """The leak check must read the runner's exact prompts: cross-check
    against exp3's own loader + 2c's render_prompt."""
    import harness

    from experiments.exp3.run.run_cell import load_capability

    got = c.load_prompts()
    for rung in c.REVERSAL_RUNGS:
        cap, _p = load_capability(rung)
        shots = [tuple(s) for s in cap["shots"]][:2]
        want = [harness.render_prompt(it["question"], shots)
                for it in cap["eval_items"]]
        assert got[rung] == want


def test_committed_prompts_never_contain_their_answers():
    """The by-construction guarantee the leak-void gate leans on,
    checked across all 1000 committed items (design §6.3)."""
    got = c.load_prompts()
    import harness  # noqa: F401

    from experiments.exp3.run.run_cell import load_capability
    for rung in c.REVERSAL_RUNGS:
        cap, _p = load_capability(rung)
        for it, prompt in zip(cap["eval_items"], got[rung]):
            assert str(it["answer"]).casefold() not in prompt.casefold()
