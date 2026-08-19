"""Unit fixtures for the committed seed-extension map (doc Open item
6): the golden formula literal, the dump/check round trip, and both
overlap continuity laws (exp3 seeds 0–3, 3c seeds 4–15)."""
import hashlib
import json

import pytest

from experiments.exp3.sampler import stream_seed
from experiments.exp3d import analyze_3d as d


def test_formula_golden_literal():
    tag = "exp3|reverse_string|1b|trained|s16|i0"
    want = int.from_bytes(hashlib.sha256(tag.encode()).digest()[:8],
                          "big") & ((1 << 63) - 1)
    assert stream_seed("reverse_string", "1b", "trained", 16, 0) == want


def test_committed_map_checks_clean():
    d.check_stream_map_3d()


def test_dump_check_round_trip_and_tamper(tmp_path):
    p = tmp_path / "map.json"
    d.dump_stream_map_3d(p)
    d.check_stream_map_3d(p)
    m = json.loads(p.read_text())
    m["cells"]["reverse_string/1b/trained/s16"]["item0"] += 1
    p.write_text(json.dumps(m))
    with pytest.raises(ValueError, match="not the formula's output"):
        d.check_stream_map_3d(p)


def test_overlap_law_enforced(tmp_path):
    p = tmp_path / "map.json"
    d.dump_stream_map_3d(p)
    m = json.loads(p.read_text())
    # coverage tamper: drop a cell
    del m["cells"]["reverse_string/410m/trained/s0"]
    p.write_text(json.dumps(m))
    with pytest.raises(ValueError, match="covers"):
        d.check_stream_map_3d(p)


def test_committed_map_covers_both_pooled_ranges():
    m = json.loads(d.STREAM_MAP_3D_PATH.read_text())
    assert len(m["cells"]) == 40 + 28
    assert m["new_seeds"] == {"410m": list(range(16, 28)),
                              "1b": list(range(16, 40))}
    assert m["seed_blocks"]["1b"][0] == [16, 17, 18, 19]
