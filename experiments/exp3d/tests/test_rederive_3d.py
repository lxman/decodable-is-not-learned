"""Unit fixtures for the gate-1 comparator (doc Open item 7): the pure
diff over seed-8 streams misses nothing, refuses incomplete coverage,
and its record round-trips through the analyzer's loader."""
import json

import pytest

from experiments.exp3d import analyze_3d as d
from experiments.exp3d import rederive_3d as r


def rows(dps=3):
    return [{"item": 0, "draws": {"8": ["a", "b", "c"][:dps]}},
            {"item": 1, "draws": {"8": ["d", "e", "f"][:dps]}}]


def test_diff_seed_clean_and_dirty():
    assert r.diff_seed(rows(), {0: ["a", "b", "c"],
                                1: ["d", "e", "f"]}, dps=3,
                       seed=8) == []
    diffs = r.diff_seed(rows(), {0: ["a", "X", "c"],
                                 1: ["d", "e", "Y"]}, dps=3, seed=8)
    assert diffs == [
        {"item": 0, "seed": 8, "draw": 1, "got": "X", "committed": "b"},
        {"item": 1, "seed": 8, "draw": 2, "got": "Y", "committed": "f"}]


def test_diff_seed_refuses_incomplete():
    with pytest.raises(ValueError, match="incomplete"):
        r.diff_seed(rows(), {0: ["a", "b", "c"]}, dps=3, seed=8)
    with pytest.raises(ValueError, match="incomplete"):
        r.diff_seed(rows(), {0: ["a", "b"], 1: ["d", "e", "f"]},
                    dps=3, seed=8)


def test_diff_seed_refuses_extras_and_missing_stream():
    with pytest.raises(ValueError, match="does not carry"):
        r.diff_seed(rows(), {0: ["a", "b", "c"], 1: ["d", "e", "f"],
                             9: ["z", "z", "z"]}, dps=3, seed=8)
    bad = [{"item": 0, "draws": {"7": ["a", "b", "c"]}}]
    with pytest.raises(ValueError):
        r.diff_seed(bad, {0: ["a", "b", "c"]}, dps=3, seed=8)


def test_gate1_record_round_trips_through_loader(tmp_path):
    for size in d.SIZES_3D:
        rec = r.gate1_record_3d(
            size, n_items=20, diffs=[],
            committed_gz_sha="e" * 64, items_sha="items-x",
            model_sha="m", stack={"torch": "t"})
        p = (tmp_path / "results" / "gate1" / f"{size}_trained"
             / "reverse_string.json")
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(rec))
    out = d.load_gate1_3d(tmp_path)
    assert out["1b"]["draws_compared"] == 20 * 64
    assert out["410m"]["n_diffs"] == 0


def test_gate1_record_carries_the_frozen_seed():
    rec = r.gate1_record_3d("1b", n_items=1, diffs=[],
                            committed_gz_sha="e" * 64, items_sha="i",
                            model_sha="m", stack={})
    assert rec["seeds_rederived"] == [8]
    assert rec["dtype"] == "float32"
