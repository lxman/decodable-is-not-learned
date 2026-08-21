"""Gate-1 record shape and the subset coverage rule (design §10.3;
3d F2)."""
import pytest

from experiments.exp3d import rederive_3d
from experiments.exp3e import analyze_3e as e
from experiments.exp3e import rederive_3e as rd


def test_comparator_is_3d_s_frozen_one():
    assert rd.diff_seed is rederive_3d.diff_seed


def test_record_shape_on_the_real_subset():
    rec = rd.gate1_record_3e(
        "1b", items=e.SUBSET_ITEMS_PIN, diffs=[],
        fires_reproduced=[{"item": 430, "seed": 20, "draw": 43},
                          {"item": 348, "seed": 20, "draw": 14}],
        committed_gz_sha="a" * 64,
        committed_shard="reverse_string.s20-s23.draws.jsonl.gz",
        items_sha="b" * 64, model_sha="m", stack={})
    assert rec["draws_compared"] == e.GATE1_COVERAGE == 2880
    assert rec["seeds_rederived"] == [20]
    assert rec["n_items"] == 45 and rec["items"] == list(e.SUBSET_ITEMS_PIN)
    assert rec["fires_reproduced"] == e.GATE1_EXPECTED_FIRES["1b"]
    assert rec["subset_sha256"] == e.SUBSET_SHA256_PIN


def test_subset_rows_refuse_incomplete_coverage():
    rows = [{"item": i, "draws": {"20": [" x"] * 64}} for i in (9, 21, 46)]
    got = rd.subset_committed_rows(rows, (9, 21, 46))
    assert [r["item"] for r in got] == [9, 21, 46]
    with pytest.raises(ValueError, match="every subset item"):
        rd.subset_committed_rows(rows, (9, 21, 46, 51))


def test_gate1_shard_blocks():
    assert e.gate1_shard_block("1b") == (20, 21, 22, 23)
    assert e.gate1_shard_block("410m") == (24, 25, 26, 27)
