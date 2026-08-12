# experiments/exp2c/tests/test_campaign_m4.py
"""Tests for the M4 eval campaign (design §3 eval side).

M4 is the first time the program queries a 2.8b+ model. Two things the
runner must get right beyond the mechanics:

  * it must REFUSE to run before the Stage 1 tag exists — the two-stage
    lock enforced in code, not just in discipline; and
  * it must load the 12 carried survivors' items from exp2b's frozen
    tree, sha-verified against the reuse manifest, since they have no
    item file and no SPECS entry on the 2c side.

No test here loads a model.
"""

import json

import pytest

from experiments.exp2c import harness
from experiments.exp2c.battery.family_map import (REUSED_FAMILIES,
                                                  scored_battery_families)
from experiments.exp2c.run import campaign_m4 as m4


# --------------------------------------------------------------- scope

def test_eval_scope_is_the_whole_scored_battery():
    """Unlike M1 (new-pool only), M4 must evaluate every scored rung —
    survivors included, or they have no ascent score."""
    assert set(m4.eval_capability_names()) == set(scored_battery_families())
    assert len(m4.eval_capability_names()) == 34


def test_eval_sizes_are_the_locked_side_only():
    assert m4.EVAL_SIZES == ("2.8b", "6.9b", "12b")
    for probe_size in ("410m", "1b"):
        assert probe_size not in m4.EVAL_SIZES


# -------------------------------------------------------- the two-stage lock

def test_refuses_to_run_without_the_stage_1_tag():
    """The lock in code. If the tag is absent the eval side must not be
    reachable, whatever the caller asks for."""
    with pytest.raises(RuntimeError, match="Stage 1 tag"):
        m4.require_stage1_tag(tag_exists=lambda _: False)


def test_accepts_the_stage_1_tag_when_present():
    m4.require_stage1_tag(tag_exists=lambda _: True)  # must not raise


def test_rejects_a_probe_size():
    with pytest.raises(AssertionError, match="eval sizes"):
        m4.check_size("410m")


# ------------------------------------------------------ survivor loading

def test_survivor_items_load_from_the_frozen_2b_tree():
    """No 2c item file, no 2c SPECS entry — the manifest is the only
    route, and answer_type rides in the 2b file itself."""
    for name in sorted(REUSED_FAMILIES):
        cap = m4.load_capability(name)
        assert cap["name"] == name
        assert len(cap["eval_items"]) >= 500
        assert cap["answer_type"] in harness.MAX_NEW_TOKENS
        assert cap["shots"]


def test_survivor_load_verifies_the_manifest_hash(tmp_path):
    """A survivor item file that no longer matches the tagged 2b record
    must fail loudly: the reuse declaration is what makes their carried
    fits comparable."""
    bad = dict(m4._survivor_entry("antonym"))
    bad["sha256"] = "0" * 64
    with pytest.raises(RuntimeError, match="sha256"):
        m4._load_survivor("antonym", entry=bad)


def test_new_pool_items_load_through_the_2c_harness():
    cap = m4.load_capability("odd6")
    assert cap["name"] == "odd6"
    assert cap["answer_type"] in harness.MAX_NEW_TOKENS
    assert len(cap["eval_items"]) >= 500


def test_every_scored_rung_is_loadable_and_eval_ready():
    """Design §7 item 7 as an executable check: >=500 items, shots for
    the 2-shot primary, and an answer_type the harness can cap."""
    for name in m4.eval_capability_names():
        cap = m4.load_capability(name)
        assert len(cap["eval_items"]) >= 500, name
        assert len(cap["shots"]) >= harness.N_SHOTS_PRIMARY, name
        assert cap["answer_type"] in harness.MAX_NEW_TOKENS, name
        it = cap["eval_items"][0]
        assert "question" in it and "answer" in it, name


# ------------------------------------------------------------ durability

def test_result_path_is_the_durable_resumable_unit():
    p = m4.result_path_for("2.8b", "trained", "odd6")
    assert p.parent.name == "2.8b_trained"
    assert p.name == "odd6.json"
    assert "m4" in str(p)


def test_plan_covers_every_size_mode_capability_cell():
    """3 sizes x 2 modes x 34 rungs. The untrained arm is not optional:
    the ascent score normalizes against EMPIRICAL floors (design §3)."""
    plan = m4.campaign_plan()
    assert len(plan) == 3 * 2 * 34
    assert {s for s, _, _ in plan} == set(m4.EVAL_SIZES)
    assert {m for _, m, _ in plan} == {"trained", "untrained"}


def test_plan_runs_the_untrained_floor_before_the_trained_arm():
    """Within a size the floor goes first. It is cheap (random init, no
    download) and every trained number is normalized against it, so a
    size whose floor is missing yields no ascent score at all. The
    declared plan must match what campaign_m4.sh actually executes."""
    plan = m4.campaign_plan()
    first = {}
    for size, mode, _ in plan:
        first.setdefault(size, mode)
    assert set(first.values()) == {"untrained"}


def test_plan_orders_cheapest_size_first():
    """12b is the long pole; it must not block the 2.8b and 6.9b
    evidence from landing first."""
    plan = m4.campaign_plan()
    order = []
    for s, _, _ in plan:
        if s not in order:
            order.append(s)
    assert order == ["2.8b", "6.9b", "12b"]
