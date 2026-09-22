# experiments/exp5/tests/test_search_5.py
import random

import pytest

from experiments.exp5 import search_5 as se

SPINE = (1000, 2000, 4000, 8000, 16000, 32000, 64000, 100000, 143000)
AVAIL = tuple(range(1000, 144000, 1000))


def _curve(step, A=2.0, B=40.0):
    return A + B / (step ** 0.5)


def _full():
    return {s: _curve(s) for s in AVAIL}


def test_plan_needs_spine_first_in_order():
    p = se.plan_5({}, AVAIL, SPINE, 2.3)
    assert p == {"status": "need", "step": 1000, "why": "spine"}
    p = se.plan_5({1000: 3.0}, AVAIL, SPINE, 2.3)
    assert p["step"] == 2000 and p["why"] == "spine"


def test_plan_drops_when_no_interval_crosses():
    losses = {s: _curve(s) for s in SPINE}
    p = se.plan_5(losses, AVAIL, SPINE, _curve(143000) - 0.001)
    assert p["status"] == "dropped" and "no spine interval" in p["reason"]


def test_plan_bisects_to_an_adjacent_bracket_and_names_the_window():
    losses = {s: _curve(s) for s in SPINE}
    target = _curve(50500)            # crossing inside [32000, 64000]
    requested = []
    while True:
        p = se.plan_5(losses, AVAIL, SPINE, target)
        if p["status"] != "need":
            break
        if p["why"] == "window":
            assert p["bracket"] == [50000, 51000]
            assert p["window"] == [48000, 49000, 52000, 53000]
        requested.append((p["step"], p["why"]))
        losses[p["step"]] = _curve(p["step"])
    assert p["status"] == "done"
    lo, hi = p["bracket"]
    assert hi == lo + 1000 and losses[lo] >= target > losses[hi]
    assert (lo, hi) == (50000, 51000)
    assert p["b_minus"] == [48000, 49000] and p["b_plus"] == [52000, 53000]
    assert [w for _, w in requested].count("bisect") == len(p["bisected"]) <= 6
    assert p["bisected"][0] == 48000                     # nearest the midpoint of [32000, 64000]
    assert p["residual_lo"] >= 0 and p["residual_hi"] > 0 and p["width_steps"] == 1000


def test_plan_crossing_is_closed_at_the_low_end_exactly():
    """Task 6 mutation kill: the crossing rule is `losses[a] >= target >
    losses[b]` — closed at the LOW end, open at the high end. A target
    equal to the FIRST spine point's own loss must still be found (the
    max loss in a decreasing table can only ever equal, never exceed,
    its own first point) — a mutant swapping the operators finds no
    interval anywhere and drops instead."""
    losses = {s: _curve(s) for s in SPINE}
    target = losses[SPINE[0]]
    p = se.plan_5(losses, AVAIL, SPINE, target)
    assert p["status"] != "dropped"


def test_bisection_tie_breaks_toward_the_lower_step():
    assert se.bisect_step_5((1000, 2000, 3000, 4000), 1000, 4000) == 2000      # mid 2500: tie 2000/3000


def test_window_at_the_list_edges_is_shorter_and_printed():
    avail = (1000, 2000, 143000)
    spine = (1000, 2000, 143000)
    losses = {1000: 3.0, 2000: 2.5, 143000: 2.0}
    p = se.plan_5(losses, avail, spine, 2.2)
    assert p["status"] == "done" and p["bracket"] == [2000, 143000]
    assert p["b_minus"] == [1000] and p["b_plus"] == [] and p["edge"] == {"b_minus": 1, "b_plus": 0}


def test_plan_is_total_over_random_partial_tables():
    rng = random.Random(0)
    full = _full()
    for _ in range(300):
        keep = {s: v for s, v in full.items() if rng.random() < 0.5}
        target = rng.uniform(_curve(143000), _curve(1000))
        p = se.plan_5(keep, AVAIL, SPINE, target)
        assert p["status"] in ("need", "dropped", "done")
        if p["status"] == "need":
            assert p["step"] in AVAIL and p["step"] not in keep


def test_plan_refuses_a_spine_step_off_the_available_list():
    with pytest.raises(ValueError, match="available"):
        se.plan_5({}, (1000, 2000), (1000, 3000), 2.0)


def test_non_monotone_losses_still_terminate_with_a_straddling_bracket():
    losses = {s: _curve(s) for s in AVAIL}
    losses[40000] = 9.0                    # a spike inside the interval
    target = _curve(50500)
    p = se.plan_5(losses, AVAIL, SPINE, target)
    assert p["status"] == "done"
    lo, hi = p["bracket"]
    assert losses[lo] >= target > losses[hi] and hi == lo + 1000


def test_replay_lists_the_whole_request_sequence():
    losses = _full()
    r = se.replay_5(losses, AVAIL, SPINE, _curve(50500))
    assert r["status"] == "done"
    assert r["requested"][:9] == [(s, "spine") for s in SPINE]
    # the bisection trace for this target visits 48000 and 52000 (see the
    # "bisect"-tagged requests below), which coincide with b_minus[0] and
    # b_plus[0] of the final window — a step already known is never
    # re-requested (search_5's total-over-partial-tables invariant), so
    # only 2 of the 4 window steps (49000, 53000) are fresh "window" asks.
    assert [w for _, w in r["requested"]].count("window") == 2
    assert set(se.requested_steps_5(r)) >= set(SPINE)
