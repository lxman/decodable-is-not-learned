"""Pytest face of the full-shape rule (doc Open item 4): every
terminal world asserts through the frozen loaders of both trees, and
every hard-error route — malformed batteries, moved referents, twin
fires, pin mismatches — refuses with the right error, never a verdict.
"""
import json

import pytest

from experiments.exp3 import analyze_3 as a3
from experiments.exp3c import analyze_3c as c
from experiments.exp3c.tests import full_shape as fs


@pytest.mark.parametrize("name", sorted(fs.BATTERIES))
def test_world_reaches_its_terminal(name, tmp_path):
    spec = fs.BATTERIES[name]
    out = fs.run_world(tmp_path, name, spec)
    assert out["verdict"] == spec["expect"]
    assert spec.get("expect_reason", "") in out["reason"]
    for i, chk in enumerate(spec.get("check", [])):
        assert chk(out), f"world {name} check {i} failed"


# ------------------------------------------------- hard-error routes

def test_empty_3c_tree_hard_errors(tmp_path):
    kw = fs.write_world(tmp_path / "w")
    import shutil
    shutil.rmtree(tmp_path / "w" / "exp3c" / "results" / "sampling")
    with pytest.raises(FileNotFoundError):
        fs.run_battery(**kw)


def test_missing_one_new_cell_hard_errors(tmp_path):
    kw = fs.write_world(tmp_path / "w")
    (tmp_path / "w" / "exp3c" / "results" / "sampling" / "1b_trained"
     / "reverse_string.json").unlink()
    with pytest.raises(FileNotFoundError):
        fs.run_battery(**kw)


def test_missing_gate1_record_hard_errors(tmp_path):
    kw = fs.write_world(tmp_path / "w")
    (tmp_path / "w" / "exp3c" / "results" / "gate1" / "1b_trained"
     / "ctrl_copy.json").unlink()
    with pytest.raises(FileNotFoundError):
        fs.run_battery(**kw)


def test_empty_exp3_tree_hard_errors(tmp_path):
    kw = fs.write_world(tmp_path / "w")
    import shutil
    shutil.rmtree(tmp_path / "w" / "exp3" / "results")
    with pytest.raises(FileNotFoundError):
        fs.run_battery(**kw)


def test_moved_fires_referent_hard_errors(tmp_path):
    kw = fs.write_world(tmp_path / "w")
    kw["referent"]["fires"]["reverse_string/1b/trained"] \
        ["full_string_total"] = 0
    with pytest.raises(ValueError, match="referent moved"):
        fs.run_battery(**kw)


def test_twin_fire_in_exp3_tree_hard_errors(tmp_path):
    kw = fs.write_world(
        tmp_path / "w",
        exp3_fires={("rev_string7", "410m", "untrained"): [(0, 0, 0)]})
    # the referent table matches the tree (both carry the twin fire),
    # so only the independent reading-4 assert can catch it
    with pytest.raises(ValueError, match="contamination referent"):
        fs.run_battery(**kw)


def test_address_pin_mismatch_hard_errors(tmp_path):
    kw = fs.write_world(tmp_path / "w")
    kw["referent"]["fire_addresses"]["reverse_string/1b/trained"] = \
        [{"item": 5, "seed": 0, "draw": 6}]
    with pytest.raises(ValueError, match="not where the referent says"):
        fs.run_battery(**kw)


def test_answer_length_pin_mismatch_hard_errors(tmp_path):
    kw = fs.write_world(tmp_path / "w")
    kw["referent"]["fire_answer_lengths"]["reverse_string/1b/trained"] \
        = [5]
    with pytest.raises(ValueError, match="lengths"):
        fs.run_battery(**kw)


def test_items_sha_pin_mismatch_hard_errors(tmp_path):
    kw = fs.write_world(tmp_path / "w")
    kw["sha_refs"]["reverse_string"] = "items-WRONG"
    with pytest.raises(ValueError, match="§4"):
        fs.run_battery(**kw)


def test_new_cell_sha_pin_binds_on_its_own(tmp_path):
    """Isolates the NEW-cell §4 pin arm: both trees carry the same
    drifted sha for one cell (so the cross-tree check agrees) and the
    gate-1 records still match the pin — only the new-cell arm can
    catch it."""
    kw = fs.write_world(tmp_path / "w")
    for tree in ("exp3", "exp3c"):
        p = (tmp_path / "w" / tree / "results" / "sampling"
             / "1b_trained" / "reverse_string.json")
        rec = json.loads(p.read_text())
        rec["items_sha256"] = "items-DRIFTED"
        p.write_text(json.dumps(rec))
    with pytest.raises(ValueError, match="single §4 pin"):
        fs.run_battery(**kw)


def test_answers_disagreeing_across_trees_hard_error(tmp_path):
    kw = fs.write_world(tmp_path / "w")
    p = (tmp_path / "w" / "exp3c" / "results" / "sampling"
         / "1b_trained" / "reverse_string.json")
    rec = json.loads(p.read_text())
    rec["answers"][0], rec["answers"][1] = \
        rec["answers"][1], rec["answers"][0]
    p.write_text(json.dumps(rec))
    with pytest.raises(ValueError,
                       match="not the same experiment's items"):
        fs.run_battery(**kw)


def test_untrained_dir_in_3c_tree_refused(tmp_path):
    kw = fs.write_world(tmp_path / "w")
    (tmp_path / "w" / "exp3c" / "results" / "sampling"
     / "410m_untrained").mkdir()
    with pytest.raises(ValueError, match="unexpected entry"):
        fs.run_battery(**kw)


def test_extractor_crosscheck_fires_on_loader_disagreement(tmp_path):
    kw = fs.write_world(tmp_path / "w")
    import harness
    cells = a3.load_sampling_cells(kw["root"] / "exp3",
                                   verify_fn=harness.verify)
    cells[c.FIRED_CELL]["recomputed"]["full_string_total"] += 1
    with pytest.raises(ValueError, match="two passes"):
        c.extract_fire_addresses(kw["root"] / "exp3", cells,
                                 verify_fn=harness.verify)


def test_gate1_committed_sha_mismatch_hard_errors(tmp_path):
    """FREEZE FINDING B executable: a gate-1 record whose
    committed_draws_sha256 does not hash-match the exp3 tree this
    analysis pools is a hard error — the continuity attestation and
    the pooled bytes must be about the same file."""
    kw = fs.write_world(tmp_path / "w")
    p = (tmp_path / "w" / "exp3c" / "results" / "gate1" / "1b_trained"
         / "reverse_string.json")
    rec = json.loads(p.read_text())
    rec["committed_draws_sha256"] = "0" * 64
    p.write_text(json.dumps(rec))
    with pytest.raises(ValueError, match="about the same file"):
        fs.run_battery(**kw)


def test_gate1_sha_check_needs_the_draws_file(tmp_path):
    """The loop closure refuses to run against a missing exp3 draws
    file rather than passing vacuously (isolated: the check itself,
    not the sampling loader, must raise)."""
    kw = fs.write_world(tmp_path / "w")
    gate1 = c.load_gate1_records(kw["root"] / "exp3c")
    (tmp_path / "w" / "exp3" / "results" / "sampling" / "1b_trained"
     / "ctrl_copy.draws.jsonl.gz").unlink()
    with pytest.raises(FileNotFoundError, match="gate-1"):
        c.check_gate1_committed_shas(gate1, kw["root"] / "exp3")


def test_gate1_seed_count_is_the_committed_volume(tmp_path):
    """PROGRESS.md reading 1 pinned: the gate-1 records' compared
    volumes are 64/item on scored cells and 8/item on ctrl_copy —
    132,000 on the real 500-item battery, 5,280 at n=20."""
    kw = fs.write_world(tmp_path / "w")
    recs = c.load_gate1_records(kw["root"] / "exp3c")
    assert recs[("ctrl_copy", "1b", "trained")]["draws_per_seed"] == 8
    assert recs[("ctrl_copy", "1b", "trained")]["draws_compared"] == 160
    assert recs[("reverse_string", "1b", "trained")]["draws_compared"] \
        == 1280
    scale = 500 // fs.N
    assert sum(r["draws_compared"] for r in recs.values()) * scale \
        == 132_000
