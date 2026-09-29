# experiments/exp6/tests/test_analyze_unit_6.py
"""The analyzer's pure parts: the statuses, all sixteen worlds, the
modifiers, the disclosures, the outcome, the secondaries' inputs."""
import itertools

import numpy as np
import pytest

from experiments.exp6 import analyze_6 as an
from experiments.exp6 import battery_6 as b6
from experiments.exp6 import families_6 as fm
from experiments.exp6 import power_6 as pw6

F = fm.FAMILIES_6


def res(fires, n_rungs=9, T=0.2, p=1e-4, lo=0.05, rungs=None):
    rungs = list(rungs if rungs is not None else b6.RUNGS_6[:n_rungs])
    return {"fires": fires, "eligible": rungs,
            "stratified": {"T": T if fires else 0.01, "p": p if fires else 0.4,
                           "n_perm": 100, "n_ge": 0},
            "per_rung": {r: {"d": 0.2, "ci": {"lo": lo, "hi": 0.4}} for r in rungs},
            "named_inside": None}


def four(*fires, n_rungs=9):
    return {f: res(x, n_rungs=n_rungs) for f, x in zip(F, fires)}


# ------------------------------------------------------------------ statuses
@pytest.mark.parametrize("fires,want", [
    ((1, 1, 1, 1), "H"), ((1, 1, 1, 0), "H"), ((1, 0, 1, 1), "H"),
    ((1, 1, 0, 0), "S"), ((0, 1, 0, 1), "S"),
    ((1, 0, 0, 0), "F"), ((0, 0, 0, 0), "F"),
])
def test_the_naming_rule_at_three_of_four(fires, want):
    s = an.status_of(four(*fires))
    assert s["status"] == want and s["E"] == 4 and s["F"] == sum(fires)


def test_a_test_that_reads_two_rungs_counts_toward_nothing():
    r = four(1, 1, 1, 1)
    r["olmo7b"] = res(True, n_rungs=2)               # fires, but is not EVALUABLE
    s = an.status_of(r)
    assert s["E"] == 3 and s["F"] == 3 and s["status"] == "H"
    assert "olmo7b" not in s["evaluable"] and "olmo7b" not in s["fired"]
    r["olmo13b"] = res(True, n_rungs=0)
    s = an.status_of(r)
    assert s["E"] == 2 and s["status"] == "U"         # two evaluable: undetermined
    assert an.evaluable(res(True, n_rungs=3)) and not an.evaluable(res(True, n_rungs=2))


def test_the_rule_at_two_of_four_is_the_sensitivity():
    assert an.status_of(four(1, 1, 0, 0), holds_at=2)["status"] == "H"
    assert an.status_of(four(1, 0, 0, 0), holds_at=2)["status"] == "S"
    assert an.status_of(four(0, 0, 0, 0), holds_at=2)["status"] == "F"
    assert an.status_of(four(1, 1, 0, 0))["status"] == "S"


def test_all_sixteen_pairs_name_a_world():
    pairs = set(itertools.product("HSFU", repeat=2))
    assert set(an.WORLD_OF_6) == pairs and len(pairs) == 16
    assert set(an.WORLD_OF_6.values()) == set(an.WORLDS_6) - {"INSUFFICIENT_DATA"}
    want = {"GENERAL": {("H", "H")},
            "PYTHIA-ONLY": {("H", "S"), ("H", "F"), ("H", "U")},
            "OLMO-ONLY": {("S", "H"), ("F", "H"), ("U", "H")},
            "SPLIT": {("S", "S"), ("S", "F"), ("F", "S")},
            "BATTERY-BOUND": {("F", "F")},
            "UNDETERMINED": {("S", "U"), ("U", "S"), ("F", "U"), ("U", "F"), ("U", "U")}}
    for world, cells in want.items():
        assert {k for k, v in an.WORLD_OF_6.items() if v == world} == cells
        for a, b in cells:
            assert an.world_of(a, b) == world
    assert set(an.LICENSED_6) == set(an.WORLDS_6)
    for text in an.LICENSED_6.values():
        assert an.BOUNDS_6 in text and an.KNOWN_INPUTS_CAVEAT_6 in text


# -------------------------------------------------------------------- verdict
def _tests(a, b, **kw):
    out = {}
    for t, fires in (("A", a), ("B", b)):
        for f, x in zip(F, fires):
            out[(t, f)] = res(x, **kw)
    return out


def _rsets(n=9):
    return {"families": {f: {"R": list(b6.RUNGS_6[:n]),
                             "R_heuristic": list(b6.RUNGS_6[:n])} for f in F}}


def _power(status="POWERED", sim=9, **over):
    return {"tests": {pw6.test_name(t, f): {
        "declared_status": over.get(pw6.test_name(t, f), status),
        "rungs_simulated": list(b6.RUNGS_6[:sim])} for t, f in pw6.TESTS_6}}


@pytest.mark.parametrize("a,b,world", [
    ((1, 1, 1, 1), (1, 1, 1, 0), "GENERAL"),
    ((1, 1, 1, 0), (1, 1, 0, 0), "PYTHIA-ONLY"),
    ((1, 1, 1, 0), (0, 0, 0, 0), "PYTHIA-ONLY"),
    ((0, 0, 0, 1), (1, 1, 1, 1), "OLMO-ONLY"),
    ((1, 1, 0, 0), (1, 0, 1, 0), "SPLIT"),
    ((1, 1, 0, 0), (0, 0, 0, 0), "SPLIT"),
    ((0, 0, 0, 0), (0, 1, 0, 0), "BATTERY-BOUND"),
])
def test_the_tree(a, b, world):
    v = an.verdict_6([], _tests(a, b), _rsets(), _power())
    assert v["verdict"] == world
    assert v["statuses"]["A"]["F"] == sum(a) and v["statuses"]["B"]["F"] == sum(b)
    for t, f in pw6.TESTS_6:
        assert pw6.test_name(t, f) in v["reason"]
    assert an.licensed_6(v).startswith(an.LICENSED_6[world])


def test_failures_come_first():
    v = an.verdict_6(["x failed"], None, None, None)
    assert v["verdict"] == "INSUFFICIENT_DATA" and "x failed" in v["reason"]
    assert v["statuses"] is None
    assert an.licensed_6(v) == an.LICENSED_6["INSUFFICIENT_DATA"]


def test_battery_bound_is_read_under_the_power_record():
    t = _tests((0, 0, 0, 0), (0, 0, 0, 0))
    v = an.verdict_6([], t, _rsets(), _power())
    assert v["modifiers"] == [an.BATTERY_BOUND_POWERED_6]
    assert "measured absence" in an.licensed_6(v) and "withdrawn" in an.licensed_6(v)
    v = an.verdict_6([], t, _rsets(), _power(
        **{"B:olmo7b": "DECLARED UNDERPOWERED IN ADVANCE"}))
    assert v["modifiers"] == [an.BATTERY_BOUND_UNDERPOWERED_6]
    assert "withdrawn" not in an.licensed_6(v)
    assert an.DISCLOSURE_UNDERPOWERED_6.format(name="B:olmo7b") in v["disclosures"]
    # a test that is not evaluable does not decide the modifier
    t[("B", "olmo7b")] = res(False, n_rungs=2)
    v = an.verdict_6([], t, _rsets(), _power(
        **{"B:olmo7b": "DECLARED UNDERPOWERED IN ADVANCE"}))
    assert v["verdict"] == "BATTERY-BOUND"
    assert v["modifiers"] == [an.BATTERY_BOUND_POWERED_6]


def test_the_headline_condition():
    rungs = ("modarith_add1", "lcs", "sort3", "ascii_basic", "deduction3", "temporal")
    t = {(p, f): res(True, rungs=rungs) for p, f in pw6.TESTS_6}
    st = {p: an.status_of({f: t[(p, f)] for f in F}) for p in "AB"}
    h = an.headline_condition(t, st)
    assert h["met"] and h["types"] == ["arithmetic", "choice", "string"]
    v = an.verdict_6([], t, _rsets(), _power())
    assert v["modifiers"] == [an.HEADLINE_UNQUALIFIED_6]
    # only the arithmetic rungs' intervals exclude zero
    for k in t:
        for r in t[k]["per_rung"]:
            if b6.RUNG_TYPE_OF[r] != "arithmetic":
                t[k]["per_rung"][r]["ci"]["lo"] = -0.01
    h = an.headline_condition(t, st)
    assert not h["met"] and h["types"] == ["arithmetic"]
    v = an.verdict_6([], t, _rsets(), _power())
    assert "arithmetic" in v["modifiers"][0] and "NOT met" in v["modifiers"][0]
    # on two families only: no rung counts
    for f in F[:2]:
        for p in "AB":
            for r in t[(p, f)]["per_rung"]:
                t[(p, f)]["per_rung"][r]["ci"]["lo"] = -0.01
    assert an.headline_condition(t, st)["types"] == []
    # an interval that TOUCHES zero does not exclude it
    t0 = {(p, f): res(True, rungs=rungs, lo=0.0) for p, f in pw6.TESTS_6}
    h = an.headline_condition(t0, st)
    assert not h["met"] and h["types"] == []
    # a predictor that does not hold is not read
    t2 = _tests((1, 1, 1, 1), (0, 0, 0, 0))
    st2 = {p: an.status_of({f: t2[(p, f)] for f in F}) for p in "AB"}
    assert set(an.headline_condition(t2, st2)["by_predictor"]) == {"A"}


def test_undetermined_names_its_shortfall():
    """Design §6: the record names which shortfall it was, because the
    two sides call for different successors. R_f short, or a rung too
    thin over the sweep: the outcome side. A rung degenerate for the
    predictor: the predictor side."""
    t = _tests((1, 1, 1, 1), (1, 1, 1, 1), n_rungs=2)
    v = an.verdict_6([], t, _rsets(2), _power(sim=2))
    assert v["verdict"] == "UNDETERMINED"
    assert v["modifiers"] == [f"outcome side: R_f holds fewer than 3 rungs on {list(F)}"]
    R9 = list(b6.RUNGS_6[:9])
    t = _tests((1, 1, 1, 1), (1, 1, 1, 1))
    for f in F[:2]:
        t[("A", f)] = dict(res(False, rungs=R9[:2]), dropped_degenerate=R9[2:], thin=[])
        t[("B", f)] = dict(res(False, rungs=R9[:2]), dropped_degenerate=[], thin=R9[2:])
    v = an.verdict_6([], t, _rsets(9), _power())
    assert v["verdict"] == "UNDETERMINED"
    assert v["modifiers"] == [
        f"predictor side: Test A on {f} lost {R9[2:]} to degeneracy" for f in F[:2]] + [
        f"outcome side: Test B on {f} lost {R9[2:]} to thin outcomes over the sweep"
        for f in F[:2]]
    assert sum("fewer than three" in d for d in v["disclosures"]) == 4
    # an undefined test lists every rung as thin; the degenerate ones are not counted twice
    t[("A", F[0])] = dict(res(False, rungs=[]), dropped_degenerate=R9[:5], thin=R9)
    mods = an.verdict_6([], t, _rsets(9), _power())["modifiers"]
    assert f"predictor side: Test A on {F[0]} lost {R9[:5]} to degeneracy" in mods
    assert f"outcome side: Test A on {F[0]} lost {R9[5:]} to thin outcomes over the sweep" \
        in mods
    # one family short of rungs is named, not only two
    rs = _rsets(9)
    rs["families"][F[3]]["R"] = R9[:2]
    assert an.shortfall(t, {p: {"status": "F"} for p in "AB"}, rs) == [
        f"outcome side: R_f holds fewer than 3 rungs on {[F[3]]}"]
    # a loss the result does not explain is said, not dropped
    t = _tests((1, 1, 1, 1), (1, 1, 1, 1), n_rungs=2)
    mods = an.verdict_6([], t, _rsets(9), _power())["modifiers"]
    assert len(mods) == 8 and all("names no cause" in m for m in mods)


# --------------------------------------- fix wave 3 (final review C-1, I-4, M-1)
SEAL_ORDER_6 = (
    "The predictors were sealed before any outcome model was handed an item of "
    "this battery; the endpoints, rung sets and power record before any "
    "intermediate checkpoint was scored into a record; the projection before the "
    "sweeps. Outcome weights were loaded before the predictor seal once, by a "
    "test on 2026-09-28 (no tokenizer, no forward pass, no item read; the ledger "
    "has the account). The outcome preflight runs after the predictor seal and "
    "loads each family's endpoint and first grid step. It stores nothing. Of what "
    "a model writes on an item of this battery it reports shape, timing and "
    "identity, and no score; it holds 2c's two anchors to their committed counts.")


def test_the_known_inputs_caveat_states_the_seal_order_as_run():
    """Final review C-1 (ruling I-19): the sentence that travels into
    every licence said the predictors were sealed before any outcome
    weight loaded; a test loaded one on 2026-09-28 and the run plan's
    outcome preflight loads each family's endpoint and first grid step.
    The sentence now states what the seal order is."""
    assert SEAL_ORDER_6 in an.KNOWN_INPUTS_CAVEAT_6
    assert "before any outcome weight loaded" not in an.KNOWN_INPUTS_CAVEAT_6
    for world, text in an.LICENSED_6.items():
        assert SEAL_ORDER_6 in text, world
        assert "before any outcome weight loaded" not in text, world
        assert "scores nothing" not in text, world          # ruling I-24


def test_the_headline_counts_evaluable_families_only():
    """Freeze §D 1 / final review I-4 (ruling I-20): a family on which
    the test read fewer than three rungs is counted toward nothing by the
    naming rule, and toward nothing by the headline condition either."""
    rungs = ("modarith_add1", "lcs", "sort3", "ascii_basic", "deduction3", "temporal")
    t = {(p, f): res(p == "A", rungs=rungs) for p, f in pw6.TESTS_6}
    t[("A", F[3])] = res(True, rungs=(rungs[0], rungs[2]))   # two rungs: not EVALUABLE
    for r in t[("A", F[2])]["per_rung"]:
        t[("A", F[2])]["per_rung"][r]["ci"]["lo"] = -0.01
    st = {p: an.status_of({f: t[(p, f)] for f in F}) for p in "AB"}
    assert st["A"]["status"] == "H" and st["A"]["evaluable"] == list(F[:3])
    assert st["B"]["status"] != "H"
    # modarith_add1 (arithmetic) and sort3 (string) exclude zero on F0, F1
    # (evaluable) and F3 (not): two types on "three families" as built
    h = an.headline_condition(t, st)
    assert not h["met"] and h["types"] == [] and h["by_predictor"] == {"A": {}}
    v = an.verdict_6([], t, _rsets(), _power())
    assert v["verdict"] == "PYTHIA-ONLY" and "NOT met" in v["modifiers"][0]
    # the same intervals on an evaluable third family: met
    t[("A", F[3])] = res(True, rungs=rungs)
    st = {p: an.status_of({f: t[(p, f)] for f in F}) for p in "AB"}
    assert an.headline_condition(t, st)["met"]


def test_the_shortfall_names_the_side_that_lost_the_rung():
    """Final review M-1 (ruling I-22): `_run_test` also drops a rung whose
    OUTCOME is constant inside every stratum (2g's `perm_test`: no
    informative pair). `dropped_predictor` is what was degenerate on the
    predictor's side before any retry; the rest of `dropped_degenerate`
    is named on the outcome side."""
    R9 = list(b6.RUNGS_6[:9])

    def one(**over):
        t = _tests((1, 1, 1, 1), (1, 1, 1, 1))
        t[("A", F[0])] = dict(res(False, rungs=R9[:2]), **over)
        st2 = {"A": {"status": "U"}, "B": {"status": "H"}}
        return an.shortfall(t, st2, _rsets(9))
    # the predictor side: degenerate before any retry
    assert one(dropped_degenerate=R9[2:5], dropped_predictor=R9[2:5], thin=[]) == [
        f"predictor side: Test A on {F[0]} lost {R9[2:5]} to degeneracy"]
    # the outcome side: dropped on the retry, not degenerate for the predictor
    assert one(dropped_degenerate=R9[2:5], dropped_predictor=[], thin=[]) == [
        f"outcome side: Test A on {F[0]} lost {R9[2:5]} to an outcome that is "
        f"constant inside every stratum"]
    # both, and the thin ones beside them
    assert one(dropped_degenerate=R9[2:5], dropped_predictor=R9[2:3],
               thin=R9[2:]) == [
        f"predictor side: Test A on {F[0]} lost {R9[2:3]} to degeneracy",
        f"outcome side: Test A on {F[0]} lost {R9[3:5]} to an outcome that is "
        f"constant inside every stratum",
        f"outcome side: Test A on {F[0]} lost {R9[5:]} to thin outcomes over the sweep"]
    # thin alone
    assert one(dropped_degenerate=[], dropped_predictor=[], thin=R9[2:]) == [
        f"outcome side: Test A on {F[0]} lost {R9[2:]} to thin outcomes over the sweep"]
    # a result with no `dropped_predictor` (a stub) is read as before
    assert one(dropped_degenerate=R9[2:5], thin=[]) == [
        f"predictor side: Test A on {F[0]} lost {R9[2:5]} to degeneracy"]


def test_the_licence_of_battery_bound_claims_no_absence():
    """Status F allows one firing family, so BATTERY-BOUND can hold two
    tests that fired. Its sentence states the naming rule's count and
    leaves the reading to the power record (design §6 wrote no other)."""
    base = an._L["BATTERY-BOUND"]
    assert base == ("Neither predictor reached the naming rule's bar on the field's "
                    "tasks: each fired on at most one of its evaluable families. Read "
                    "under the power record.")
    for word in ("forecasts", "absence", "withdrawn", "no forecast", "does not"):
        assert word not in base, word
    t = _tests((1, 0, 0, 0), (0, 0, 1, 0))
    under = _power(status="DECLARED UNDERPOWERED IN ADVANCE")
    v = an.verdict_6([], t, _rsets(), under)
    assert v["verdict"] == "BATTERY-BOUND"
    assert (v["statuses"]["A"]["fired"], v["statuses"]["B"]["fired"]) == ([F[0]], [F[2]])
    said = an.licensed_6(v)
    assert said.startswith(base) and "withdrawn" not in said
    assert v["modifiers"] == [an.BATTERY_BOUND_UNDERPOWERED_6]


def test_withdrawn_is_printed_only_where_the_power_record_covers_the_reading():
    """POWERED was declared for the set the record simulated. A test
    that read another set is not covered by it (2m F-1's lineage)."""
    t = _tests((0, 0, 0, 0), (0, 0, 0, 0))
    v = an.verdict_6([], t, _rsets(), _power())
    assert v["modifiers"] == [an.BATTERY_BOUND_POWERED_6]
    assert "withdrawn" in an.licensed_6(v) and an.uncovered(t, _power()) == []
    wide = _power(sim=9)
    t[("B", F[1])] = res(False, n_rungs=7)                # read seven of the nine simulated
    assert an.uncovered(t, wide) == ["B:" + F[1]]
    v = an.verdict_6([], t, _rsets(), wide)
    assert v["verdict"] == "BATTERY-BOUND"
    assert v["modifiers"] == [an.BATTERY_BOUND_UNCOVERED_6.format(names="B:" + F[1])]
    assert "withdrawn" not in an.licensed_6(v)
    assert "not detected at this resolution" in an.licensed_6(v)
    # underpowered is said first, whatever the sets
    mixed = _power(**{"A:" + F[0]: "DECLARED UNDERPOWERED IN ADVANCE"})
    assert an.verdict_6([], t, _rsets(), mixed)["modifiers"] == [
        an.BATTERY_BOUND_UNDERPOWERED_6]
    # a test that is not evaluable is not asked whether it is covered
    t[("B", F[1])] = res(False, n_rungs=2)
    assert an.uncovered(t, wide) == []
    # nor is a reading WIDER than the set simulated covered by the declaration
    t = _tests((0, 0, 0, 0), (0, 0, 0, 0))
    assert an.uncovered(t, _power(sim=7)) == [pw6.test_name(a, f) for a, f in pw6.TESTS_6]
    assert an.verdict_6([], t, _rsets(), _power(sim=7))["modifiers"][0].startswith(
        "Every evaluable test was declared POWERED, and at least one read a rung set")


def test_a_predictor_that_holds_on_three_says_on_which():
    t = _tests((1, 1, 1, 0), (1, 1, 1, 1))
    v = an.verdict_6([], t, _rsets(), _power())
    assert v["verdict"] == "GENERAL"
    line = an.DISCLOSURE_HOLDS_ON_6.format(t="A", n=3, e=4, fired=", ".join(F[:3]),
                                           quiet=F[3], unread="none")
    assert line.endswith(f"Evaluable and did not fire: {F[3]}. Not evaluable, counted "
                         f"toward nothing: none.")
    assert v["disclosures"] == [line] and an.licensed_6(v).endswith(line)
    # a family whose test FIRED on two rungs was not read: it is not said not to have fired
    t = _tests((1, 1, 1, 1), (1, 1, 1, 1))
    t[("A", F[1])] = res(True, n_rungs=2)
    v = an.verdict_6([], t, _rsets(), _power())
    assert v["verdict"] == "GENERAL" and v["statuses"]["A"]["E"] == 3
    said = [d for d in v["disclosures"] if d.startswith("Predictor A holds")]
    assert said == [an.DISCLOSURE_HOLDS_ON_6.format(
        t="A", n=3, e=3, fired=", ".join(f for f in F if f != F[1]), quiet="none",
        unread=F[1])]
    assert "did not fire: none" in said[0] and f"toward nothing: {F[1]}." in said[0]
    full = an.verdict_6([], _tests((1, 1, 1, 1), (1, 1, 1, 1)), _rsets(), _power())
    assert full["disclosures"] == []
    assert an.holds_on({"A": {"status": "S", "fired": F[:2], "E": 4},
                        "B": {"status": "F", "fired": [], "E": 4}}) == []


def test_a_test_that_reads_less_than_R_f_says_so_against_the_power_record():
    t = _tests((1, 1, 1, 1), (1, 1, 1, 1), n_rungs=7)
    v = an.verdict_6([], t, _rsets(9), _power(sim=7))
    assert sum("the SAME set" in d for d in v["disclosures"]) == 8
    v = an.verdict_6([], t, _rsets(9), _power(sim=9))
    assert sum("NARROWER" in d for d in v["disclosures"]) == 8
    v = an.verdict_6([], t, _rsets(9), _power(sim=3))
    assert sum("a DIFFERENT set" in d for d in v["disclosures"]) == 8
    v = an.verdict_6([], _tests((1, 1, 1, 1), (1, 1, 1, 1)), _rsets(9), _power())
    assert v["disclosures"] == []


# ------------------------------------------------------------------- outcomes
def _steps(family, first):
    grid = [int(s) for s in fm.grid(family)]
    recs = {}
    for k, s in enumerate(grid):
        bits = [int(f is not None and k >= f) for f in first]
        recs[s] = {"lcs": {"bits": bits, "correct": sum(bits),
                           "continuations": ["x"] * len(bits)}}
    return recs


def test_the_outcome_is_the_count_of_grid_points():
    first = [0, 3, None, 20] + [None] * 496
    out = an.outcomes_6(_steps("olmo7b", first), "olmo7b", rungs=("lcs",))["lcs"]
    assert out["y"][:4] == [21, 18, 0, 1] and out["n_pos"] == 3
    g = [int(s) for s in fm.grid("olmo7b")]
    assert out["first"][:4] == [g[0], g[3], None, g[20]]
    assert out["counts_by_step"][g[-1]] == 3 and out["counts_by_step"][g[0]] == 1
    fc = an.first_correct_outcome({"lcs": out}, "olmo7b", ("lcs",))["lcs"]["y"]
    assert fc[0] > fc[1] > fc[3] > fc[2] == 0          # earlier is larger
    with pytest.raises(ValueError, match="grid"):
        an.outcomes_6(_steps("olmo7b", first), "olmo7b", rungs=("lcs",), steps=(7,))


def test_the_outcome_counts_a_transient_item():
    recs = _steps("olmo13b", [None] * 500)
    g = sorted(recs)
    for s in (g[2], g[5]):                             # right twice, not at the end
        recs[s]["lcs"]["bits"][9] = 1
    out = an.outcomes_6(recs, "olmo13b", rungs=("lcs",))["lcs"]
    assert out["y"][9] == 2 and out["first"][9] == g[2] and out["n_pos"] == 1


def test_rung_level_prints_both_floors():
    first = [0] * 60 + [None] * 440
    out = an.outcomes_6(_steps("olmo7b", first), "olmo7b", rungs=("lcs",))
    floors = {"lcs": {"floor": 0.1}}
    h = {"lcs": {"heuristic": "a rule", "heuristic_floor": 0.42}}
    rl = an.rung_level(out, floors, h, "olmo7b", ("lcs",))["lcs"]
    assert rl["final"] == 60 and rl["final_clears"] is False       # 60 of 500 at .10
    first = [0] * 120 + [None] * 380
    out = an.outcomes_6(_steps("olmo7b", first), "olmo7b", rungs=("lcs",))
    rl = an.rung_level(out, floors, h, "olmo7b", ("lcs",))["lcs"]
    assert rl["final_clears"] is True
    assert rl["final_clears_heuristic_floor"] is False     # a length rule scores more
    rl = an.rung_level(out, floors, {"lcs": {"heuristic": None,
                                             "heuristic_floor": None}},
                       "olmo7b", ("lcs",))["lcs"]
    assert rl["final_clears_heuristic_floor"] is None
    rl = an.rung_level(out, floors, {"lcs": {"heuristic": "x", "heuristic_floor": 1.0}},
                       "olmo7b", ("lcs",))["lcs"]
    assert rl["final_clears_heuristic_floor"] is False     # nothing beats a full score


def test_a_rung_that_cleared_and_fell_back_is_a_transient_clear():
    """The steps at which a rung cleared are TRANSIENT clears only where
    it does not clear at the endpoint."""
    floors = {"lcs": {"floor": 0.1}}
    h = {"lcs": {"heuristic": None, "heuristic_floor": None}}
    recs = _steps("olmo7b", [None] * 500)
    g = sorted(recs)
    for s in (g[3], g[4]):                  # 120 right at two steps, none at the end
        recs[s]["lcs"]["bits"] = [1] * 120 + [0] * 380
        recs[s]["lcs"]["correct"] = 120
    out = an.outcomes_6(recs, "olmo7b", rungs=("lcs",))
    rl = an.rung_level(out, floors, h, "olmo7b", ("lcs",))["lcs"]
    assert rl["clears"] == [g[3], g[4]] and rl["s_star"] == g[3]
    assert rl["final_clears"] is False and rl["transient_clears"] == [g[3], g[4]]
    assert rl["ever"] == 120 and rl["final"] == 0
    out = an.outcomes_6(_steps("olmo7b", [0] * 120 + [None] * 380), "olmo7b",
                        rungs=("lcs",))
    rl = an.rung_level(out, floors, h, "olmo7b", ("lcs",))["lcs"]
    assert rl["final_clears"] is True and rl["clears"] == g
    assert rl["transient_clears"] == []


def test_collapses_and_ceiling():
    recs = _steps("olmo13b", [0] * 500)
    g = sorted(recs)
    recs[g[1]]["lcs"]["continuations"] = ["!"] * 460 + ["x"] * 40
    for s in g:                                        # no two items say the same
        recs[s]["lcs"]["continuations"] = [f" {i}" for i in range(500)]
    recs[g[1]]["lcs"]["continuations"] = ["!"] * 460 + [f" {i}" for i in range(40)]
    recs[g[2]]["lcs"]["continuations"] = ["!"] * 449 + [f" {i}" for i in range(51)]
    assert an.collapses(recs, ("lcs",)) == [
        {"rung": "lcs", "step": g[1], "continuation": "!", "n_identical": 460,
         "correct": 500}]                              # 449 of 500 is not a collapse
    assert [c["step"] for c in an.collapses(recs, ("lcs",), threshold=449)] == g[1:3]
    out = an.outcomes_6(_steps("olmo13b", [0] * 10 + [1] * 5 + [None] * 485),
                        "olmo13b", rungs=("lcs",))
    c = an.ceiling_fraction(out, ("lcs",), n_steps=16)["lcs"]
    assert c["n_ceiling"] == 10 and c["n_pos"] == 15
    assert c["fraction_of_positives"] == pytest.approx(10 / 15)


def test_the_answer_prior():
    cap = b6.load_item_file_6("lcs")
    ans = [it["answer"] for it in cap["eval_items"]]
    rows = [{"item": i, "draws": {"0": [" 7"] * 16 + [" " + ans[i]] * 48}}
            for i in range(500)]
    pi = an.answer_prior_6(rows, cap, seeds=(0,))
    seven = [p for p, a in zip(pi, ans) if a == "7"]
    other = [p for p, a in zip(pi, ans) if a != "7"]
    # "7" is said on a quarter of the draws of every item whose answer is not 7
    assert all(p == pytest.approx(0.25) for p in seven)
    assert all(p < 0.12 for p in other) and len(seven) == 50
    rows[3]["draws"]["0"][0] = " \r"                  # the draw side is total here too
    an.answer_prior_6(rows, cap, seeds=(0,))
    with pytest.raises(ValueError, match="coverage"):
        an.answer_prior_6(rows[:499], cap, seeds=(0,))


def test_the_groups_of_the_by_type_secondary():
    assert sorted(sum(map(list, an.TYPE_GROUPS_6.values()), [])) == sorted(b6.RUNGS_6)
    assert sorted(sum(map(list, an.CLASS_GROUPS_6.values()), [])) == sorted(b6.RUNGS_6)
    assert {k: len(v) for k, v in an.TYPE_GROUPS_6.items()} == \
        {"arithmetic": 4, "string": 8, "choice": 5}
    assert {k: len(v) for k, v in an.CLASS_GROUPS_6.items()} == {"E.2": 10, "E.3": 7}


# ------------------------------------------------- S12, S13: the two floors
def test_the_relaxed_transcription():
    assert an.relaxed_ipa(" ˈbətən\n\nQ: next") == "bətən"
    assert an.relaxed_ipa("/ˈbʌt.ən/") == "bətən"           # slashes, a dot, ʌ
    assert an.relaxed_ipa("[ʧɛr]") == "tʃɛr" and an.relaxed_ipa("ʤəʤ") == "dʒədʒ"
    assert an.relaxed_ipa("ɹɛd ɡoʊ") == "rɛd"                # the first token, as strict
    assert an.relaxed_ipa("siː") == "si"
    for blank in ("", " ", " \r", "\n\n", "//"):
        assert an.relaxed_ipa(blank) == ""                   # total, and empty is empty
    assert an.relaxed_ipa("Bətən") == "Bətən"                # no case folding, as strict


def test_the_relaxed_criterion_only_loosens():
    items = b6.load_item_file_6("ipa_word")["eval_items"]
    marked = 0
    for it in items:
        a = str(it["answer"])
        r = an.relaxed_ipa(a)
        assert r and an.relaxed_ipa(r) == r                  # idempotent, never empty
        assert not any(c in r for c, _ in an.RELAXED_IPA_6)
        marked += r != a
    assert marked >= 312          # every stress-marked answer changes, and some others
    assert len({an.relaxed_ipa(it["answer"]) for it in items}) >= 490


def test_a_count_against_the_heuristic_floor():
    from experiments.exp6.run import seal_endpoint_6 as se
    assert se.clears_heuristic(300, {"heuristic_floor": None}) is None
    assert se.clears_heuristic(500, {"heuristic_floor": 1.0}) is False
    assert se.clears_heuristic(150, {"heuristic_floor": 0.23}) is True
    assert se.clears_heuristic(120, {"heuristic_floor": 0.23}) is False   # .24: not beyond
    assert se.clears_heuristic(115, {"heuristic_floor": 0.23}) is False


def test_the_rung_sets_hold_both_sets():
    from experiments.exp6 import floors_6 as fl
    from experiments.exp6.run import seal_endpoint_6 as se
    battery = b6.load_battery_6()
    floors, heur = fl.floor_table_6(battery), fl.heuristic_table_6(battery)
    count = {r: 0 for r in b6.ALL_RUNGS_6}
    count.update({"temporal": 500, "lcs": 100, "unit_interp2": 300, "sort3": 40,
                  "deduction3": 190})
    ep = {f: {"stage1_final": {"records": {r: {"correct": k} for r, k in count.items()}},
              "init": {"records": {r: {"correct": 0} for r in b6.ALL_RUNGS_6}}}
          for f in F}
    got = se.derive_rung_sets(ep, floors, heur)
    for f in F:
        row = got[f]
        # lcs: 100 of 500 clears .10 and not the length rule's .23;
        # temporal: a string match scores every item; deduction3: 190 of
        # 500 does not clear one third, so it is in neither
        assert row["R"] == ["sort3", "temporal", "lcs", "unit_interp2"]
        assert row["R_heuristic"] == ["sort3", "unit_interp2"]
        assert row["rungs"]["sort3"]["clears_heuristic"] is None
        assert row["rungs"]["temporal"]["clears_heuristic"] is False
        assert row["rungs"]["temporal"]["heuristic_floor"] == 1.0
        assert row["rungs"]["lcs"]["clears_heuristic"] is False
        assert row["rungs"]["deduction3"]["clears"] is False
        assert set(row["R_heuristic"]) <= set(row["R"])
