"""Fixtures for the runner's model-free provisions (doc Open items 5+7):
the dtype policy table, the results layout, per-seed tallies, and the
raw-draw storage round-trip. The model-facing glue stays thin around
the fixture-proven modules; the campaign preflight and gate checks
cover it on the real ladder.
"""
import json

import pytest

from experiments.exp3 import analyze_3 as a
from experiments.exp3.run import run_cell as rc


# ------------------------------------------------------- dtype policy

def test_dtype_policy_is_the_ledgered_table():
    """PROGRESS.md 2026-08-15: mass+sampling fp32; 12b mass is the
    fp16 depth-1 exception (fp32 does not fit); re-decode is 3b's
    fp16 generate path."""
    assert rc.cell_policy("mass", "410m") == ("float32", 2)
    assert rc.cell_policy("mass", "6.9b") == ("float32", 2)
    assert rc.cell_policy("mass", "12b") == ("float16", 1)
    assert rc.cell_policy("sampling", "410m") == ("float32", None)
    assert rc.cell_policy("sampling", "1b") == ("float32", None)
    assert rc.cell_policy("redecode", "410m") == ("float16", None)


def test_sampling_never_runs_at_eval_sizes():
    with pytest.raises(ValueError, match="probe sizes"):
        rc.cell_policy("sampling", "2.8b")


# ------------------------------------------------------------- layout

def test_record_paths_live_under_canonical_kind_roots(tmp_path):
    p = rc.record_path(tmp_path, "mass", "rev_string7", "410m", "trained")
    assert p == tmp_path / "results" / "mass" / "410m_trained" / "rev_string7.json"
    d = rc.draws_path(tmp_path, "reverse_string", "1b", "untrained")
    assert d.name == "reverse_string.draws.jsonl.gz"
    assert d.parent == tmp_path / "results" / "sampling" / "1b_untrained"


# ------------------------------------------------------------ tallies

def synth_draws():
    """Item 0: seed 0 has one exact hit; seed 1 none. Item 1: nothing."""
    return [
        {"item": 0, "draws": {"0": ["dyayp", " dya"], "1": ["zz", ""]}},
        {"item": 1, "draws": {"0": ["x", "y"], "1": ["dy", "q"]}},
    ]


def test_per_seed_tallies_verify_and_first_char():
    answers = ["dyayp", "dyayp"]
    labels = ["d", "d"]
    t = rc.per_seed_tallies(synth_draws(), answers, labels,
                            answer_type="word", seeds=(0, 1))
    assert t["0"]["full_string"] == 1     # 'dyayp' verifies
    assert t["1"]["full_string"] == 0
    assert t["0"]["first_char"] == 2      # 'dyayp' + ' dya'
    assert t["1"]["first_char"] == 1      # 'dy'
    assert t["0"]["n_draws"] == t["1"]["n_draws"] == 4


def test_tallies_refuse_a_missing_seed_stream():
    with pytest.raises(ValueError, match="seed 1"):
        rc.per_seed_tallies([{"item": 0, "draws": {"0": ["x"]}}],
                            ["a"], ["a"], answer_type="word", seeds=(0, 1))


# ------------------------------------------------- draws round-trip

def test_draws_roundtrip_through_gzip_jsonl(tmp_path):
    p = tmp_path / "x.draws.jsonl.gz"
    rows = synth_draws()
    rc.write_draws(p, rows)
    assert rc.read_draws(p) == rows


def test_read_draws_refuses_duplicate_items(tmp_path):
    p = tmp_path / "x.draws.jsonl.gz"
    rc.write_draws(p, [{"item": 0, "draws": {"0": ["a"]}},
                       {"item": 0, "draws": {"0": ["b"]}}])
    with pytest.raises(ValueError, match="duplicate"):
        rc.read_draws(p)


# ------------------------------------------------------- campaign plan

def test_campaign_plan_order_is_the_committed_sequence():
    """§10.3: re-decode -> mass ladder (twins first within a kind,
    sizes ascending) -> twin sampling -> trained sampling 410m before
    1b. Tier-per-process: the plan is a sequence of (kind, size, mode)
    tiers, each one process."""
    from experiments.exp3.run.campaign_3 import tier_plan
    tiers = tier_plan()
    kinds = [t[0] for t in tiers]
    assert kinds == (["redecode"] * 4 + ["mass"] * 7 + ["sampling"] * 4)
    m = tiers[4:11]
    assert m[0][2] == m[1][2] == "untrained"
    assert [t[1] for t in m[2:]] == ["410m", "1b", "2.8b", "6.9b", "12b"]
    s = tiers[11:]
    assert [(t[1], t[2]) for t in s] == [("410m", "untrained"),
                                         ("1b", "untrained"),
                                         ("410m", "trained"),
                                         ("1b", "trained")]
