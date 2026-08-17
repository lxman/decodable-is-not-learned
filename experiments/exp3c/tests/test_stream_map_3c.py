"""The seed-extended stream map (doc Open item 2): golden literals pin
the frozen formula at the new seeds, and the committed map's overlap
with exp3's committed map is asserted byte-equal — pooling continuity
as an executable fact, not a comment.
"""
import json

import pytest

from experiments.exp3 import analyze_3 as a3
from experiments.exp3 import sampler as sp
from experiments.exp3c import analyze_3c as c

EXP3_MAP = json.loads((a3.EXP3 / "stream_map.json").read_text())


def test_seed_sets_partition_the_pooled_set():
    assert c.NEW_SEEDS == tuple(range(4, 16))
    assert set(c.NEW_SEEDS) & set(a3.SEEDS) == set()
    assert sorted(set(c.NEW_SEEDS) | set(a3.SEEDS)) == list(range(16))
    assert c.K_NEW == 12 * 64 == 768
    assert c.K_POOLED == c.K_NEW + a3.K_TOTAL["rev_string7"] == 1024


def test_new_seed_golden_values_pin_the_formula():
    """Seeds 4 and 15 through the frozen formula: if these literals
    move, the new streams are not the preregistered streams."""
    assert sp.stream_seed("rev_string7", "410m", "trained", 4, 0) == \
        7196211080022732596
    assert sp.stream_seed("rev_string7", "1b", "trained", 4, 0) == \
        113126945194852702
    assert sp.stream_seed("reverse_string", "410m", "trained", 4, 0) == \
        6528994979253196112
    assert sp.stream_seed("reverse_string", "1b", "trained", 4, 0) == \
        3067787698119348157
    assert sp.stream_seed("ctrl_copy", "1b", "trained", 4, 0) == \
        1060328931079088457
    assert sp.stream_seed("reverse_string", "1b", "trained", 15, 499) == \
        168471428302040078
    assert sp.stream_seed("rev_string7", "410m", "trained", 15, 499) == \
        1947049211295900780


def test_committed_map_exists_and_checks_pass():
    m = c.check_stream_map()
    assert len(m["cells"]) == 80
    assert m["new_seeds"] == list(range(4, 16))
    assert m["chunk_rows"] == 16


def test_committed_map_s0_entries_equal_exp3s_committed_map():
    m = json.loads(c.STREAM_MAP_3C_PATH.read_text())
    for (rung, size, mode) in c.GATE1_CELLS:
        for sd in a3.SEEDS:
            k = f"{rung}/{size}/{mode}/s{sd}"
            assert m["cells"][k] == EXP3_MAP["cells"][k], k


def test_dump_roundtrips_through_the_checker(tmp_path):
    p = tmp_path / "map.json"
    c.dump_stream_map_3c(p)
    m = c.check_stream_map(p)
    assert m["formula"] == EXP3_MAP["formula"]


def test_checker_refuses_formula_drift(tmp_path):
    m = c.dump_stream_map_3c(tmp_path / "map.json")
    m["formula"] = "something else"
    (tmp_path / "map.json").write_text(json.dumps(m))
    with pytest.raises(ValueError, match="formula"):
        c.check_stream_map(tmp_path / "map.json")


def test_checker_refuses_a_doctored_entry(tmp_path):
    m = c.dump_stream_map_3c(tmp_path / "map.json")
    m["cells"]["reverse_string/1b/trained/s4"]["item0"] += 1
    (tmp_path / "map.json").write_text(json.dumps(m))
    with pytest.raises(ValueError, match="not the formula's output"):
        c.check_stream_map(tmp_path / "map.json")


def test_checker_refuses_missing_entries(tmp_path):
    m = c.dump_stream_map_3c(tmp_path / "map.json")
    del m["cells"]["ctrl_copy/1b/trained/s15"]
    (tmp_path / "map.json").write_text(json.dumps(m))
    with pytest.raises(ValueError, match="16 seeds"):
        c.check_stream_map(tmp_path / "map.json")


def test_checker_refuses_broken_pooling_continuity(tmp_path):
    """If exp3's committed map itself drifted, the formula check on
    3c's map still passes — only the continuity comparison catches
    the break."""
    c.dump_stream_map_3c(tmp_path / "map.json")
    e = json.loads((a3.EXP3 / "stream_map.json").read_text())
    e["cells"]["reverse_string/1b/trained/s0"]["item0"] += 1
    (tmp_path / "exp3_map.json").write_text(json.dumps(e))
    with pytest.raises(ValueError, match="continuity"):
        c.check_stream_map(tmp_path / "map.json",
                           exp3_map_path=tmp_path / "exp3_map.json")
