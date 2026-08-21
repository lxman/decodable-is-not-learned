"""Fixtures for the frozen partition (design §5.1; doc Open item 1):
N(x), reachability, M(x), the two rejected variants, the 45-item
subset, the palindrome assertion, and the committed partition
record's reproduce-or-refuse load."""
import json

import pytest

from experiments.exp3e import partition_3e as pt


# ------------------------------------------------------------- N(x)

def test_neighbour_set_of_single_repeat_len4_has_seven_members():
    assert len(pt.neighbours("aabc")) == 7


def test_neighbour_set_excludes_the_source_and_equal_char_swaps():
    n = pt.neighbours("aabc")
    assert "aabc" not in n
    # the (0,1) swap of equal chars is the identity and is not counted
    assert n == {"baac", "abac", "caba", "acba", "aacb", "abca", "caab"}


def test_transpositions_skip_equal_characters():
    tr = pt.transpositions("aabc")
    assert "aabc" not in tr
    assert set(tr.values()) == {(0, 2), (0, 3), (1, 2), (1, 3), (2, 3)}


def test_neighbour_set_of_all_distinct_len4_has_eight_members():
    # 6 transpositions + 2 rotations, all distinct from x and each other
    assert len(pt.neighbours("abcd")) == 8


def test_rotations():
    assert pt.rotate_left("pmhm") == "mhmp"
    assert pt.rotate_right("abaq") == "qaba"


# ------------------------------------------------------- reachability

@pytest.mark.parametrize("x, want", [
    ("edce", ("transposition", (1, 2))),   # mirror (0,3): swap middle
    ("pffq", ("transposition", (0, 3))),   # mirror (1,2): swap outer
    ("abaq", ("rotation", "right")),       # (0,2)
    ("pmhm", ("rotation", "left")),        # (1,3)
])
def test_reachable_items_name_their_one_edit(x, want):
    r = pt.reach(x)
    assert r["reachable"] is True
    assert (r["mechanism"], r["edit"]) == want


@pytest.mark.parametrize("x", ["aabc", "abcc", "abcd"])
def test_non_reachable_items(x):
    r = pt.reach(x)
    assert r["reachable"] is False
    assert r["mechanism"] is None


def test_repeat_pattern():
    assert pt.repeat_pattern("aabc") == (0, 1)
    assert pt.repeat_pattern("abaq") == (0, 2)
    assert pt.repeat_pattern("pffq") == (1, 2)
    assert pt.repeat_pattern("abcd") is None


def test_repeat_pattern_refuses_more_than_one_repeat():
    with pytest.raises(ValueError, match="exactly one"):
        pt.repeat_pattern("aabb")


# -------------------------------------------------------------- M(x)

def test_overlap():
    assert pt.overlap("qbaa", "abaq") == 2
    assert pt.overlap("qaba", "abaq") == 0


@pytest.mark.parametrize("x, want", [
    ("abaq", {"qbaa"}),                       # (0,2): |M| = 1
    ("edce", {"edec", "eecd"}),               # (0,3): |M| = 2, 'eedc' dropped
    ("pmhm", {"mphm", "mmhp", "mpmh"}),       # (1,3): |M| = 3
    ("pffq", set()),                          # (1,2): |M| = 0 ('qpff' dropped)
    ("abcd", {"dabc", "dbca"}),               # all-distinct S2 set
    ("aabc", {"caba", "caab"}),               # non-reachable (0,1)
])
def test_matched_competitors(x, want):
    assert set(pt.matched_competitors(x)) == want


def test_matched_competitors_is_sorted_and_excludes_reverse():
    m = pt.matched_competitors("edce")
    assert m == sorted(m)
    assert "ecde" not in m


# ------------------------------------------------------------ variants

def test_variant_adjacent_only_drops_the_outer_swap():
    assert pt.reach("pffq", variant="adjacent").get("reachable") is False
    assert pt.reach("edce", variant="adjacent")["reachable"] is True


def test_variant_rotations_only_drops_all_mirrors():
    assert pt.reach("edce", variant="rotations")["reachable"] is False
    assert pt.reach("abaq", variant="rotations")["reachable"] is True


def test_unknown_variant_refused():
    with pytest.raises(ValueError, match="variant"):
        pt.reach("abaq", variant="hamming")


# ------------------------------------------------------- entropy (C1)

def test_unigram_bits_of_single_repeat_and_all_distinct():
    assert pt.unigram_bits("aabc") == 6.0
    assert pt.unigram_bits("abcd") == 8.0


# ----------------------------------------------- the subset + partition

def test_repeat_class_subset_and_palindrome_refusal():
    answers = ["ecde", "abcd", "qqab", "abba", "abcde"]
    assert pt.repeat_class_len4(answers) == [0, 2, 3]
    with pytest.raises(ValueError, match="palindrom"):
        pt.build_partition(answers)


def test_build_partition_on_a_small_synthetic_battery():
    answers = ["ecde", "abcd", "cbaa", "qaba", "xyzzy"]
    p = pt.build_partition(answers)
    assert p["items"] == [0, 2, 3]
    by = {e["item"]: e for e in p["entries"]}
    assert by[0]["input"] == "edce" and by[0]["reachable"] is True
    assert by[2]["input"] == "aabc" and by[2]["reachable"] is False
    assert by[3]["reachable"] is True and by[3]["sub_class"] == "rotation"
    assert p["reachable"] == [0, 3] and p["non_reachable"] == [2]
    assert p["variants"]["adjacent"]["reachable"] == [0, 3]
    assert p["variants"]["rotations"]["reachable"] == [3]
    assert by[0]["matched_competitors"] == ["edec", "eecd"]
    assert by[0]["entropy_bits"] == 6.0
    # the repeat pattern is stated on the INPUT (design §1/§3 tables):
    # input 'edce' is mirror (0,3); input 'aabc' is (0,1)
    assert by[0]["repeat_pattern"] == [0, 3]
    assert by[2]["repeat_pattern"] == [0, 1]
    assert p["pattern_counts"] == {"0,3": 1, "0,1": 1, "0,2": 1}


def test_dump_and_check_round_trip_and_tamper(tmp_path):
    answers = ["ecde", "abcd", "cbaa", "qaba"]
    p = tmp_path / "partition.json"
    pt.dump_partition(answers, p)
    rec = pt.check_partition(answers, p)
    assert rec["reachable"] == [0, 3]
    m = json.loads(p.read_text())
    m["non_reachable"] = []
    p.write_text(json.dumps(m))
    with pytest.raises(ValueError, match="not the frozen partition"):
        pt.check_partition(answers, p)


def test_check_partition_refuses_a_missing_record(tmp_path):
    with pytest.raises(FileNotFoundError):
        pt.check_partition(["ecde"], tmp_path / "nope.json")
