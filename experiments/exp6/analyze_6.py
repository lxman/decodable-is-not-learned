# experiments/exp6/analyze_6.py
"""Exp 6 frozen analysis (design `experiment-6-design.md` §1-§6): the
second battery. Eight preregistered tests — two predictors (A: Pythia-1b
at 256 draws; B: OLMo-2 1B at 64) by four outcome families — each 2g's
test through 2i's `_run_test`, on the rungs of the new battery that the
family's stage-1 endpoint cleared (R_f). A test that reads fewer than
three rungs is not EVALUABLE. Per predictor a STATUS by the three-of-four
naming rule (U / H / S / F); the pair of statuses names the WORLD, all
sixteen pairs enumerated.

Tree: INSUFFICIENT_DATA (any gate, any refusal, any incomplete family,
any halt marker) -> the eight tests -> the two statuses -> GENERAL /
PYTHIA-ONLY / OLMO-ONLY / SPLIT / BATTERY-BOUND / UNDETERMINED.

Nothing is attested that can be measured. Every record is re-derived
from its bytes: the predictor tallies from the draws, the outcome bits
from the continuations, gate 1-P from the committed streams, gates 1(a)
(b) (c) from each sweep host's own two reads of the endpoint and the
Mac's committed counts, the rung sets from the endpoint counts and the
floors, the power record's declarations from its own numbers. Every
loader refusal is COLLECTED and delivered as INSUFFICIENT_DATA with the
reason verbatim; an unfinished campaign delivers no verdict (5b F-1).

The anchors (2c's base-8 pair) and the control are never in a verdict.
"""
from __future__ import annotations

import json
import os
import sys
from collections import Counter
from pathlib import Path

import numpy as np

EXP6 = Path(__file__).resolve().parent
REPO = EXP6.parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp2g import stats_2g as st  # noqa: E402
from experiments.exp2i import analyze_2i as an2i  # noqa: E402
from experiments.exp2k import analyze_2k as an2k  # noqa: E402
from experiments.exp2m import analyze_2m as an2m  # noqa: E402
from experiments.exp6 import battery_6 as b6  # noqa: E402
from experiments.exp6 import families_6 as fm  # noqa: E402
from experiments.exp6 import floors_6 as fl  # noqa: E402
from experiments.exp6 import make_referents_6 as mkr  # noqa: E402
from experiments.exp6 import pins_6 as p6  # noqa: E402
from experiments.exp6 import power_6 as pw6  # noqa: E402
from experiments.exp6 import records_6 as r6  # noqa: E402
from experiments.exp6 import referents_6 as rf  # noqa: E402
from experiments.exp6 import strata_6 as s6  # noqa: E402
from experiments.exp6 import verify_6 as v6  # noqa: E402
from experiments.exp6.run import _common_6 as cm  # noqa: E402
from experiments.exp6.run import seal_endpoint_6 as se  # noqa: E402
from experiments.exp6.run import seal_predictor_6 as sp  # noqa: E402
from experiments.exp6.run import sweep_6 as sw  # noqa: E402

RESULTS = EXP6 / "results"
REFERENTS_6_SHA256 = "09286d10937ac008a456977fc51ef8da4a9807639e570da0c2fa41cbef5373a9"

ALPHA, T_BAR = st.ALPHA, st.T_BAR
N_PERM, N_BOOT = st.N_PERM, st.N_BOOT
MIN_RUNGS = pw6.MIN_RUNGS
HOLDS_AT = pw6.HOLDS_AT
TESTS_6 = pw6.TESTS_6
LABEL_OF = {"A": "1b:k256", "B": "olmo1b"}
collect_total = an2i.collect_total
_run_test = an2i._run_test

WORLDS_6 = ("INSUFFICIENT_DATA", "GENERAL", "PYTHIA-ONLY", "OLMO-ONLY", "SPLIT",
            "BATTERY-BOUND", "UNDETERMINED")
# every pair (status of A, status of B) — sixteen, none left to a default
WORLD_OF_6 = {
    ("H", "H"): "GENERAL",
    ("H", "S"): "PYTHIA-ONLY", ("H", "F"): "PYTHIA-ONLY", ("H", "U"): "PYTHIA-ONLY",
    ("S", "H"): "OLMO-ONLY", ("F", "H"): "OLMO-ONLY", ("U", "H"): "OLMO-ONLY",
    ("S", "S"): "SPLIT", ("S", "F"): "SPLIT", ("F", "S"): "SPLIT",
    ("F", "F"): "BATTERY-BOUND",
    ("S", "U"): "UNDETERMINED", ("U", "S"): "UNDETERMINED",
    ("F", "U"): "UNDETERMINED", ("U", "F"): "UNDETERMINED",
    ("U", "U"): "UNDETERMINED",
}

CALIBRATION_SENTENCE_6 = (
    "Each of the eight tests runs at alpha .01 behind an effect bar of T >= .10. "
    "The tests share items and predictors and are not independent; no "
    "family-wise figure is claimed and the union of the worlds is not "
    "alpha-calibrated. The guard against a shared artifact firing all eight at "
    "once is the strata, not the count of tests.")
KNOWN_INPUTS_CAVEAT_6 = (
    "Known to the designer before any model contact: the whole record through "
    "Experiment 5b, including the eight sealed forecasts on 2c's battery and "
    "the general texture of all four outcome trajectories as read on 2c's "
    "items. Not known to anyone in this program before the predictor stage: "
    "any output of any model on any item of this battery. The predictors were "
    "sealed before any outcome weight loaded; the endpoints, rung sets and "
    "power record before any intermediate checkpoint; the projection before "
    "the sweeps. The items are this program's renderings of ten BIG-bench "
    "tasks that Wei et al. (2022) classify as emergent: two-shot prompts, "
    "option-listing rungs scored by exact match on the emitted option, IPA "
    "scored per word, one answer per unscrambling item, each task split into "
    "rungs by a difficulty parameter fixed here. A landing is a statement "
    "about these renderings, not about BIG-bench scores.")
BOUNDS_6 = (
    "Bounded to item grain, to the rungs named as read, to these renderings of "
    "the tasks, and to predictors at or below one billion parameters. Nothing "
    "here licenses the across-task ranking: which tasks a family clears is "
    "R_f, read at the endpoint, not forecast.")
_L = {
    "INSUFFICIENT_DATA": "No statement is licensed: the record did not pass its "
                         "own gates.",
    "GENERAL": "The order in which the field's own emergent tasks come into "
               "focus during training is forecast, at the level of single "
               "items, by the sampled outputs of one-billion-parameter models "
               "of two other families, on four outcome families.",
    "PYTHIA-ONLY": "The item-order forecast generalises off the battery it was "
                   "found on for Pythia-1b's sampled counts and the sentence is "
                   "bounded to that predictor. It is the cleaner of the two "
                   "single-predictor worlds: the predictor that cannot have "
                   "seen BIG-bench holds.",
    "OLMO-ONLY": "The item-order forecast generalises off the battery it was "
                 "found on for OLMo-2 1B's sampled counts and the sentence is "
                 "bounded to that predictor. OLMo-2's corpus can hold "
                 "BIG-bench-style text and Pythia's cannot: familiarity with "
                 "the tasks' format is the live alternative and the sentence "
                 "says so.",
    "SPLIT": "The forecast reaches some families and not others on the field's "
             "tasks. The table is reported and no generality is claimed; the "
             "one-line thesis is bounded to one battery and, on the field's "
             "tasks, to the families named.",
    "BATTERY-BOUND": "Neither predictor reached the naming rule's bar on the "
                     "field's tasks: each fired on at most one of its evaluable "
                     "families. Read under the power record.",
    "UNDETERMINED": "Too few rungs cleared or too few predictors were live for "
                    "the naming rule to apply. The full table is reported and "
                    "nothing about generality is licensed in either direction.",
}
BATTERY_BOUND_POWERED_6 = (
    "Every evaluable test was POWERED: this is a measured absence. The eight "
    "sealed forecasts are a property of 2c's battery; the forecast claim is "
    "demoted to one synthetic battery of this program's making and the "
    "one-line thesis is withdrawn. What remains is the within-task ladder and "
    "the methods paper.")
BATTERY_BOUND_UNDERPOWERED_6 = (
    "At least one evaluable test was declared underpowered in advance: the "
    "reading is 'not detected at this resolution', the blind region is the "
    "power record's, and the demotion is to 'not shown beyond one battery'.")
BATTERY_BOUND_UNCOVERED_6 = (
    "Every evaluable test was declared POWERED, and at least one read a rung "
    "set the power record did not simulate ({names}): its declaration does not "
    "cover its reading. The reading is 'not detected at this resolution' and "
    "the demotion is to 'not shown beyond one battery'.")
HEADLINE_UNQUALIFIED_6 = (
    "Headline condition MET: at least two of the three rung types each hold a "
    "rung whose per-rung interval excludes zero on at least three families for "
    "a holding predictor; 'the field's emergent tasks' stands without a type "
    "qualifier.")
HEADLINE_QUALIFIED_6 = (
    "Headline condition NOT met: the sentence names the rung type that carried "
    "it ({types}) in place of 'the field's emergent tasks'.")
DISCLOSURE_THIN_6 = ("Test {name} read {k} rung(s) {rungs} — fewer than three: "
                     "not EVALUABLE, counted toward neither E nor F.")
DISCLOSURE_PARTIAL_6 = ("Test {name} read {k} of R_f's {n} rungs (not read: "
                        "{missing}); against the power record's simulated set "
                        "this is {versus}.")
DISCLOSURE_UNDERPOWERED_6 = ("Test {name} did not fire and was DECLARED "
                             "UNDERPOWERED IN ADVANCE: not detected at this "
                             "resolution.")
DISCLOSURE_HOLDS_ON_6 = ("Predictor {t} holds by the naming rule on {n} of its "
                         "{e} evaluable families ({fired}). Evaluable and did not "
                         "fire: {quiet}. Not evaluable, counted toward nothing: "
                         "{unread}.")
NO_ALPHA_NOTE_6 = ("{name} is descriptive and non-gating (design §5): its "
                   "`fires` fields are the primary's rule applied to another "
                   "input, printed for comparison; no alpha claim rides on it.")
LICENSED_6 = {k: f"{v} {BOUNDS_6} Disclosure (design §2): {KNOWN_INPUTS_CAVEAT_6}"
              for k, v in _L.items()}


# ------------------------------------------------------ statuses, worlds
def evaluable(res: dict) -> bool:
    return len(res.get("eligible") or []) >= MIN_RUNGS


def status_of(results: dict, *, holds_at: int = HOLDS_AT) -> dict:
    """`results[family]` = one predictor's four test results."""
    ev = [f for f in fm.FAMILIES_6 if evaluable(results[f])]
    fired = [f for f in ev if results[f]["fires"]]
    e, n = len(ev), len(fired)
    if e < 3:
        s = "U"
    elif n >= holds_at:
        s = "H"
    elif n == holds_at - 1:
        s = "S"
    else:
        s = "F"
    return {"status": s, "E": e, "F": n, "evaluable": ev, "fired": fired,
            "holds_at": holds_at}


def world_of(status_a: str, status_b: str) -> str:
    return WORLD_OF_6[(status_a, status_b)]


def headline_condition(tests: dict, statuses: dict) -> dict:
    """Design §6: for a HOLDING predictor, the rung types that hold a
    rung whose per-rung interval excludes zero on at least three
    families."""
    out = {}
    for t in ("A", "B"):
        if statuses[t]["status"] != "H":
            continue
        by_type = {}
        for r in b6.RUNGS_6:
            n = 0
            for f in fm.FAMILIES_6:
                ci = (tests[(t, f)].get("per_rung") or {}).get(r, {}).get("ci") or {}
                lo = ci.get("lo")
                if lo is not None and np.isfinite(lo) and lo > 0:
                    n += 1
            if n >= 3:
                by_type.setdefault(b6.RUNG_TYPE_OF[r], []).append(r)
        out[t] = by_type
    types = sorted({ty for v in out.values() for ty in v})
    best = max((len(v) for v in out.values()), default=0)
    return {"by_predictor": out, "types": types, "met": best >= 2}


def shortfall(tests: dict, statuses: dict, rung_sets: dict) -> list:
    """UNDETERMINED names which shortfall it was (design §6): the two
    sides call for different successors. Outcome side: R_f is short, or
    a rung of R_f was too thin over the sweep to be read. Predictor
    side: a rung was degenerate for the predictor."""
    out = []
    small = [f for f in fm.FAMILIES_6 if len(rung_sets["families"][f]["R"]) < MIN_RUNGS]
    if small:
        out.append(f"outcome side: R_f holds fewer than {MIN_RUNGS} rungs on "
                   f"{small}")
    for t in ("A", "B"):
        if statuses[t]["status"] != "U":
            continue
        for f in fm.FAMILIES_6:
            res = tests[(t, f)]
            if f in small or evaluable(res):
                continue
            thin = [r for r in res.get("thin") or []
                    if r not in (res.get("dropped_degenerate") or [])]
            if res.get("dropped_degenerate"):
                out.append(f"predictor side: Test {t} on {f} lost "
                           f"{list(res['dropped_degenerate'])} to degeneracy")
            if thin:
                out.append(f"outcome side: Test {t} on {f} lost {thin} to thin "
                           f"outcomes over the sweep")
            if not thin and not res.get("dropped_degenerate"):
                out.append(f"Test {t} on {f} read {len(res.get('eligible') or [])} "
                           f"rung(s) and its result names no cause")
    return out


def disclosures_of(tests: dict, rung_sets: dict, power: dict) -> list:
    out = []
    for t, f in TESTS_6:
        res, name = tests[(t, f)], pw6.test_name(t, f)
        r_f = list(rung_sets["families"][f]["R"])
        read = list(res.get("eligible") or [])
        if not evaluable(res):
            out.append(DISCLOSURE_THIN_6.format(name=name, k=len(read), rungs=read))
        elif set(read) != set(r_f):
            sim = set(((power or {}).get("tests") or {}).get(name, {})
                      .get("rungs_simulated") or [])
            versus = ("the SAME set" if set(read) == sim else
                      "NARROWER than the set simulated (the power record "
                      "simulated a WIDER one)" if set(read) < sim else
                      "a DIFFERENT set")
            out.append(DISCLOSURE_PARTIAL_6.format(
                name=name, k=len(read), n=len(r_f),
                missing=[r for r in r_f if r not in read], versus=versus))
        status = ((power or {}).get("tests") or {}).get(name, {}).get("declared_status")
        if evaluable(res) and not res["fires"] and \
                status == "DECLARED UNDERPOWERED IN ADVANCE":
            out.append(DISCLOSURE_UNDERPOWERED_6.format(name=name))
    return out


def holds_on(statuses: dict) -> list:
    """A predictor holds on three of four: the licence's sentence says
    "on four outcome families", and the record says on which it held. A
    family on which the test was not EVALUABLE is named apart: it was
    not read, whether or not its test fired, and "did not fire" is said
    only of a family that was."""
    out = []
    for t in ("A", "B"):
        s = statuses[t]
        if s["status"] == "H" and len(s["fired"]) < len(fm.FAMILIES_6):
            quiet = [f for f in s["evaluable"] if f not in s["fired"]]
            unread = [f for f in fm.FAMILIES_6 if f not in s["evaluable"]]
            out.append(DISCLOSURE_HOLDS_ON_6.format(
                t=t, n=len(s["fired"]), e=s["E"], fired=", ".join(s["fired"]),
                quiet=", ".join(quiet) or "none", unread=", ".join(unread) or "none"))
    return out


def uncovered(tests: dict, power: dict) -> list:
    """The evaluable tests whose reading the power record's declaration
    does not cover: the set read is not the set simulated."""
    out = []
    for t, f in TESTS_6:
        res, name = tests[(t, f)], pw6.test_name(t, f)
        sim = ((power or {}).get("tests") or {}).get(name, {}).get("rungs_simulated")
        if evaluable(res) and set(res.get("eligible") or []) != set(sim or []):
            out.append(name)
    return out


def _fmt(res: dict) -> str:
    s = res["stratified"]
    return (f"T={an2i._fmt_T(s['T'])}, p={s['p']:.4g}, rungs={len(res['eligible'])}, "
            f"fires={bool(res['fires'])}")


def verdict_6(failures, tests, rung_sets, power) -> dict:
    if failures:
        return {"verdict": "INSUFFICIENT_DATA",
                "reason": f"{len(failures)} referent/loader failure(s): "
                          f"{list(failures)[:5]}",
                "statuses": None, "disclosures": [], "modifiers": []}
    statuses = {t: status_of({f: tests[(t, f)] for f in fm.FAMILIES_6})
                for t in ("A", "B")}
    world = world_of(statuses["A"]["status"], statuses["B"]["status"])
    parts = [f"A is {statuses['A']['status']} (E={statuses['A']['E']}, "
             f"F={statuses['A']['F']}); B is {statuses['B']['status']} "
             f"(E={statuses['B']['E']}, F={statuses['B']['F']})"]
    parts += [f"{pw6.test_name(t, f)}: {_fmt(tests[(t, f)])}" for t, f in TESTS_6]
    mods = []
    if world in ("GENERAL", "PYTHIA-ONLY", "OLMO-ONLY"):
        hc = headline_condition(tests, statuses)
        mods.append(HEADLINE_UNQUALIFIED_6 if hc["met"] else
                    HEADLINE_QUALIFIED_6.format(types=", ".join(hc["types"]) or
                                                "none cleared the condition"))
    if world == "BATTERY-BOUND":
        ev = [(t, f) for t, f in TESTS_6 if evaluable(tests[(t, f)])]
        powered = all(((power or {}).get("tests") or {}).get(pw6.test_name(t, f), {})
                      .get("declared_status") == "POWERED" for t, f in ev)
        narrow = uncovered(tests, power)
        mods.append(BATTERY_BOUND_UNDERPOWERED_6 if not powered else
                    BATTERY_BOUND_UNCOVERED_6.format(names=", ".join(narrow))
                    if narrow else BATTERY_BOUND_POWERED_6)
    if world == "UNDETERMINED":
        mods += shortfall(tests, statuses, rung_sets)
    disc = disclosures_of(tests, rung_sets, power) + holds_on(statuses)
    return {"verdict": world, "reason": "; ".join(parts + mods + disc),
            "statuses": statuses, "disclosures": disc, "modifiers": mods}


def licensed_6(tree: dict) -> str:
    return " ".join([LICENSED_6[tree["verdict"]]] + list(tree.get("modifiers") or [])
                    + list(tree.get("disclosures") or []))


# ------------------------------------------------------ the sealed stages
def _raise(msg):
    raise ValueError(msg)


def load_predictor_stage(root, battery, *, tag_exists=None, blobs_bound=None) -> tuple:
    """(failures, ctx): the seal, its binding, every unit measured,
    gate 1-P re-derived, the seal's counts re-derived from the draws."""
    bad, ctx = [], {}
    seal, f = collect_total(lambda: r6.read_json(r6.seal_path(root)),
                            "6 predictor seal")
    bad += f
    got, f = collect_total(lambda: sp.collect(root), "6 predictor units")
    bad += f
    if got is None:
        return bad, ctx
    ub, units = got
    bad += ub
    gp, f = collect_total(lambda: sp.gate1p(root, units), "6 gate 1-P re-derivation")
    bad += f
    if gp is not None:
        bad += gp[0]
        rec, f = collect_total(lambda: r6.read_json(r6.gate1p_path(root)),
                               "6 gate 1-P record")
        bad += f
        if rec is not None and rec.get("units") != gp[1]:
            bad.append("6 gate 1-P: the record does not re-derive from the draws")
        if rec is not None and rec.get("prereg_tag") != r6.PREREG_TAG_6:
            bad.append("6 gate 1-P: prereg_tag")
        ctx["gate1p"] = gp[1]
    if seal is not None:
        files, f = collect_total(lambda: sp.file_table(root), "6 predictor file table")
        bad += f
        if files is not None and (seal.get("files") != files or
                                  seal.get("sha256") != r6.composite_sha(files)):
            bad.append("6 predictor seal: it does not describe the files on disk")
        paths = [Path(root) / rel for rel in (seal.get("files") or {})]
        b = p6.seal_failures(r6.PREDICTOR_SEAL_TAG_6, paths + [r6.seal_path(root)],
                             tag_exists=tag_exists, blobs_bound=blobs_bound)
        bad += [f"6 predictor seal binding: {m}" for m in b]
        ctx["seal_binding"] = {"tag": r6.PREDICTOR_SEAL_TAG_6,
                               "n_paths": len(paths) + 1, "failures": b}
        want = {p: {r: r6.counts_of(units[(p, "main", r)]["bits"])
                    for r in r6.tier_shape(p, "main")["rungs"]
                    if (p, "main", r) in units} for p in r6.PREDICTORS_6}
        if seal.get("counts") != want:
            bad.append("6 predictor seal: its counts do not re-derive from the draws")
        if seal.get("models") != {p: rf.model_pin(p) for p in r6.PREDICTORS_6}:
            bad.append("6 predictor seal: its models are not the pins")
        if seal.get("n_units") != len(r6.predictor_units()):
            bad.append("6 predictor seal: n_units")
        if seal.get("tag") != r6.PREDICTOR_SEAL_TAG_6:
            bad.append("6 predictor seal: tag")
    ctx.update({"seal": seal, "units": units})
    return bad, ctx


def predictor_counts(units: dict) -> dict:
    """x per test and the bits behind it: every rung the main tier
    sampled (the new battery and the two anchors)."""
    out = {}
    for t, p in r6.TEST_PREDICTOR.items():
        rungs = r6.tier_shape(p, "main")["rungs"]
        bits = {r: units[(p, "main", r)]["bits"] for r in rungs}
        out[t] = {"bits": bits, "x": {r: r6.counts_of(bits[r]) for r in rungs}}
    rungs = r6.tier_shape("pythia_410m", "main")["rungs"]
    bits = {r: units[("pythia_410m", "main", r)]["bits"] for r in rungs}
    out["410m"] = {"bits": bits, "x": {r: r6.counts_of(bits[r]) for r in rungs}}
    return out


def load_sealed_stages(root, *, tag_exists=None, blobs_bound=None) -> tuple:
    """(ctx, failures) for everything sealed BEFORE the sweeps: the
    battery and its tables, the predictor stage, the hosts, the endpoint
    stage, gate 1(b), the rung sets. `power_6` reads its inputs here."""
    bad, ctx = [], {}
    battery, f = collect_total(b6.load_battery_6, "6 battery items")
    bad += f
    floors = strata = None
    if battery is not None:
        floors, f = collect_total(lambda: fl.floor_table_6(battery), "6 floors")
        bad += f
        strata, f = collect_total(lambda: s6.build_table_6(battery), "6 strata")
        bad += f
    if floors is not None:
        _, f = collect_total(lambda: fl.check_floor_pins_6(floors), "6 floor pins")
        bad += f
    structure = heuristics = None
    if strata is not None:
        _, f = collect_total(lambda: s6.check_strata_pins_6(strata), "6 strata pins")
        bad += f
        structure, f = collect_total(lambda: s6.structure_table_6(battery, strata),
                                     "6 structure levels")
        bad += f
    if structure is not None:
        _, f = collect_total(lambda: s6.check_structure_pins_6(structure),
                             "6 structure pins")
        bad += f
    if battery is not None:
        heuristics, f = collect_total(lambda: fl.heuristic_table_6(battery),
                                      "6 heuristic floors")
        bad += f
    if heuristics is not None:
        _, f = collect_total(lambda: fl.check_heuristic_pins_6(heuristics),
                             "6 heuristic pins")
        bad += f
    ctx.update({"battery": battery, "floors": floors, "strata": strata,
                "structure": structure, "heuristics": heuristics})
    if battery is None:
        return ctx, bad
    pb, pctx = load_predictor_stage(root, battery, tag_exists=tag_exists,
                                    blobs_bound=blobs_bound)
    bad += pb
    ctx.update(pctx)
    seal_sha = (pctx.get("seal") or {}).get("sha256")
    if pctx.get("units") is not None and not pb:
        ctx["pred"], f = collect_total(lambda: predictor_counts(pctx["units"]),
                                       "6 predictor counts")
        bad += f
    got, f = collect_total(
        lambda: se.collect(root, battery=battery, seal_sha256=seal_sha),
        "6 endpoint stage")
    bad += f
    if got is None:
        return ctx, bad
    eb, ep, hosts = got
    bad += eb
    ctx.update({"endpoint": ep, "hosts": hosts})
    complete = all(set(ep.get(fam, {})) == set(r6.ENDPOINT_WHICH_6)
                   for fam in fm.FAMILIES_6)
    gb, f = collect_total(lambda: se.gate1b_failures(root, ep, hosts), "6 gate 1(b)")
    bad += f + (gb or [])
    rs, f = collect_total(lambda: r6.read_json(r6.rung_sets_path(root)),
                          "6 rung sets")
    bad += f
    if rs is not None and complete and floors is not None and heuristics is not None:
        rb, f = collect_total(
            lambda: se.rung_sets_failures(rs, ep, floors, heuristics, root),
            "6 rung sets re-derivation")
        bad += f + (rb or [])
        if rs.get("predictor_sha256") != seal_sha:
            bad.append("6 rung sets: predictor_sha256 is not the predictor seal's")
    ctx["rung_sets"] = rs
    return ctx, bad


def test_inputs(ctx: dict) -> dict:
    """The eight tests' inputs as the power record and the analyzer
    both read them: the real predictor, the battery's strata, R_f, the
    endpoint's count as the lower bound on n_pos, the grid's length."""
    out = {}
    for t, f in TESTS_6:
        rungs = list(ctx["rung_sets"]["families"][f]["R"])
        recs = ctx["endpoint"][f]["stage1_final"]["records"]
        out[(t, f)] = {
            "x": {r: list(ctx["pred"][t]["x"][r]) for r in rungs},
            "bits": {r: ctx["pred"][t]["bits"][r] for r in rungs},
            "strata": {r: {"strata": list(ctx["strata"][r]["strata"])} for r in rungs},
            "n_pos": {r: int(recs[r]["correct"]) for r in rungs},
            "rungs": rungs, "n_steps": len(fm.grid(f))}
    return out


# --------------------------------------------------------------- the sweep
GATE1_FIELDS_6 = ("family", "rungs", "rungs_compared", "items_per_rung",
                  "digest_thin", "digest_candidate", "digest_sealed", "commit",
                  "tolerance_per_rung", "failures", "pass")


def _load_gate_read(root, family, host, which, *, battery, man, seal_sha,
                    endpoint_sha) -> tuple:
    label = f"6 gate 1 {family}/{host[:12]}/{r6.GATE_READS_6[which]}"
    lp = r6.gate_load_path(root, family, host, which)
    if not lp.is_file():
        return [f"{label}: load record missing"], None
    load = r6.read_json(lp)
    entry = dict(fm.entry(family, man, fm.endpoint_step(family)))
    if which == r6.SWEEP_THIN:
        entry["kind"] = "thin-loader"
    bad = r6.load_record_failures(load, family=family, key=which, entry=entry,
                                  host_sha256=host)
    bad += rf.digest_failures(load, family, which, label=label.replace(
        "6 gate 1 ", "6 gate 1(d) "))
    recs = {}
    for rung in b6.ALL_RUNGS_6:
        p = r6.gate_record_path(root, family, host, which, rung)
        if not p.is_file():
            bad.append(f"{label}/{rung}: record missing")
            continue
        rec = r6.read_json(p)
        bad += r6.unit_record_failures(
            rec, family=family, rung=rung, cap=battery[rung], load=load,
            seal_sha256=seal_sha, host_sha256=host, which=which,
            endpoint_sha256=endpoint_sha)
        recs[rung] = rec
    if len(recs) != len(b6.ALL_RUNGS_6):
        return bad, None
    return bad, {"load": load, "records": recs}


def gate1_failures(root, family, host, *, battery, man, seal_sha, endpoint_sha,
                   sealed, sealed_load) -> tuple:
    """Gate 1 on one sweep host RE-DERIVED from that host's two reads
    of the endpoint, the sealed endpoint records and the Mac's counts;
    then the runner's record against the re-derivation."""
    label = f"6 gate 1 {family}/{host[:12]}"
    bad, reads = [], {}
    for which in (r6.SWEEP_THIN, r6.SWEEP_CAND):
        b, got = _load_gate_read(root, family, host, which, battery=battery, man=man,
                                 seal_sha=seal_sha, endpoint_sha=endpoint_sha)
        bad += b
        reads[which] = got
    gp = r6.gate1_path(root, family, host)
    if not gp.is_file():
        return bad + [f"{label}: gate record missing"], reads
    rec = r6.read_json(gp)
    if any(v is None for v in reads.values()):
        return bad + [f"{label}: the gate's reads are incomplete"], reads
    thin, cand = reads[r6.SWEEP_THIN], reads[r6.SWEEP_CAND]
    end = fm.endpoint_step(family)
    counts = {r: int(cand["records"][r]["correct"]) for r in b6.ANCHORS_6}
    redo = sw.gate1_record(
        family, thin=thin["records"], cand=cand["records"], sealed=sealed,
        thin_load=thin["load"], cand_load=cand["load"], sealed_load=sealed_load,
        anchor_bad=sw.anchor_failures(counts, family, end,
                                      label=f"6 gate 1(c) {family}/step{end}"))
    bad += redo["failures"]
    for k in GATE1_FIELDS_6:
        if rec.get(k) != redo[k]:
            bad.append(f"{label}: the record's {k} does not re-derive from the bytes")
    for k, v in (("host_sha256", host), ("prereg_tag", r6.PREREG_TAG_6),
                 ("endpoint_sha256", endpoint_sha)):
        if rec.get(k) != v:
            bad.append(f"{label}: {k}")
    return bad, reads


def load_sweep_family(root, family, *, battery, seal_sha, endpoint_sha, hosts,
                      sealed, sealed_load) -> tuple:
    """(failures, sweep). WINDOW COMPLETENESS first: every grid step of
    the family present and whole, or no verdict (5b F-1)."""
    man = fm.manifest(family)
    bad, steps, loads = [], {}, {}
    for step in fm.grid(family):
        label = f"6 sweep {family}/step{step}"
        cp = r6.checkpoint_path(root, family, step)
        if not cp.is_file():
            bad.append(f"{label}: not complete — an unfinished campaign delivers "
                       f"no verdict")
            continue
        load = r6.read_json(cp)
        bad += r6.load_record_failures(load, family=family, key=int(step),
                                       entry=fm.entry(family, man, step))
        bad += rf.digest_failures(load, family, step,
                                  label=f"6 gate 1(d) {family}/step{step}")
        h = load.get("host_sha256")
        if h not in hosts:
            bad.append(f"{label}: host {str(h)[:12]} has no host record")
        recs = {}
        for rung in b6.ALL_RUNGS_6:
            p = r6.sweep_record_path(root, family, step, rung)
            if not p.is_file():
                bad.append(f"{label}/{rung}: record missing")
                continue
            rec = r6.read_json(p)
            bad += r6.unit_record_failures(
                rec, family=family, rung=rung, cap=battery[rung], load=load,
                seal_sha256=seal_sha, host_sha256=h, step=step,
                endpoint_sha256=endpoint_sha)
            recs[rung] = rec
        if len(recs) != len(b6.ALL_RUNGS_6):
            continue
        counts = {r: int(recs[r]["correct"]) for r in b6.ANCHORS_6}
        bad += sw.anchor_failures(counts, family, step,
                                  label=f"6 gate 1(c) {family}/step{step}")
        steps[int(step)], loads[int(step)] = recs, load
    gate_hosts = {str(h) for h in (ld.get("host_sha256") for ld in loads.values())
                  if h}
    # a gate record on disk that did not pass refuses, whoever wrote it
    for gp in sorted(r6.sweep_dir(root, family).glob("gate1_*.json")):
        rec = r6.read_json(gp)
        if rec.get("pass") is not True:
            bad.append(f"6 gate 1 {family}/{gp.name}: the gate did not pass")
        if rec.get("host_sha256"):
            gate_hosts.add(str(rec["host_sha256"]))
    gates = {}
    for h in sorted(gate_hosts):
        if h not in hosts:
            bad.append(f"6 gate 1 {family}: host {h[:12]} has no host record")
        gb, reads = gate1_failures(root, family, h, battery=battery, man=man,
                                   seal_sha=seal_sha, endpoint_sha=endpoint_sha,
                                   sealed=sealed, sealed_load=sealed_load)
        bad += gb
        gates[h] = reads
    end = fm.endpoint_step(family)
    if end in steps:
        h = loads[end].get("host_sha256")
        cand = (gates.get(h) or {}).get(r6.SWEEP_CAND)
        if cand is None:
            bad.append(f"6 sweep {family}/step{end}: its host's candidate read is "
                       f"missing")
        else:
            for rung in b6.ALL_RUNGS_6:
                a, b = steps[end][rung], cand["records"][rung]
                if a["bits"] != b["bits"] or a["continuations"] != b["continuations"]:
                    bad.append(f"6 sweep {family}/step{end}/{rung}: not its host's "
                               f"candidate read of the endpoint")
            if loads[end].get("digest") != cand["load"].get("digest"):
                bad.append(f"6 sweep {family}/step{end}: tensor digest is not the "
                           f"candidate read's")
    return bad, {"steps": steps, "loads": loads,
                 "hosts": sorted(gate_hosts), "complete": len(steps) == len(fm.grid(family))}


# ----------------------------------------------------------------- outcomes
def outcomes_6(steps_recs: dict, family: str, *, rungs=b6.ALL_RUNGS_6,
               steps=None) -> dict:
    """y_i = the number of the family's grid points at which item i
    verifies; first-correct beside it. The init referent is never in an
    outcome: a step off the grid is refused."""
    grid = tuple(int(s) for s in fm.grid(family))
    steps = tuple(int(s) for s in steps) if steps is not None else grid
    if any(s not in grid for s in steps):
        raise ValueError(f"outcomes_6: steps {steps} are not all on {family}'s grid")
    out = {}
    for rung in rungs:
        bits = {s: [int(b) for b in steps_recs[s][rung]["bits"]] for s in steps}
        y, first = [], []
        for i in range(b6.N_ITEMS):
            hits = [s for s in steps if bits[s][i]]
            y.append(len(hits))
            first.append(hits[0] if hits else None)
        out[rung] = {"y": y, "first": first,
                     "n_pos": int(sum(1 for v in y if v > 0)),
                     "counts_by_step": {int(s): int(steps_recs[s][rung]["correct"])
                                        for s in steps}}
    return out


def first_correct_outcome(out: dict, family: str, rungs) -> dict:
    """First-correct as y (the sensitivity): earlier is larger."""
    last = max(int(s) for s in fm.grid(family))
    return {r: {"y": [0 if fc is None else (last + 1 - fc) for fc in out[r]["first"]],
                "n_pos": out[r]["n_pos"]} for r in rungs}


def rung_level(out: dict, floors: dict, heuristics: dict, family: str, rungs) -> dict:
    """Per rung: the steps at which the count clears the rule's floor,
    and beside the endpoint's count whether it also clears the
    HEURISTIC floor — what a guesser that solves nothing can score (plan
    delta B-22). A rung that clears the first and not the second may
    have been cleared by a shortcut; the record says so and decides
    nothing by it."""
    end = fm.endpoint_step(family)
    res = {}
    for rung in rungs:
        c = out[rung]["counts_by_step"]
        clears = [s for s in sorted(c)
                  if fl.clears(c[s], b6.N_ITEMS, floors[rung]["floor"])["significant"]]
        final = end in clears
        h = heuristics[rung]
        over = se.clears_heuristic(c[end], h)
        res[rung] = {"s_star": clears[0] if clears else None, "clears": clears,
                     "final_clears": final,
                     "transient_clears": [] if final else clears,
                     "ever": int(out[rung]["n_pos"]), "final": int(c[end]),
                     "floor": floors[rung]["floor"],
                     "heuristic": h["heuristic"],
                     "heuristic_floor": h["heuristic_floor"],
                     "final_clears_heuristic_floor": over,
                     "counts_by_step": c}
    return res


def collapses(steps_recs: dict, rungs, *, threshold: int = 450) -> list:
    """A (step, rung) where `threshold` of the 500 continuations are one
    identical string: a checkpoint-local pathology, descriptive."""
    res = []
    for step in sorted(steps_recs):
        for r in rungs:
            rec = steps_recs[step][r]
            top, n = Counter(rec["continuations"]).most_common(1)[0]
            if n >= threshold:
                res.append({"rung": r, "step": int(step), "continuation": top,
                            "n_identical": int(n), "correct": int(rec["correct"])})
    return res


def ceiling_fraction(out: dict, rungs, *, n_steps: int) -> dict:
    res = {}
    for r in rungs:
        y = out[r]["y"]
        n_c = int(sum(1 for v in y if v == n_steps))
        n_pos = int(out[r]["n_pos"])
        res[r] = {"n_ceiling": n_c, "fraction": n_c / b6.N_ITEMS, "n_pos": n_pos,
                  "fraction_of_positives": (n_c / n_pos) if n_pos else None,
                  "definition": "items verifying at EVERY grid point of the family"}
    return res


# -------------------------------------------------------------- secondaries
def answer_prior_6(rows, cap, *, seeds) -> list:
    """2j's wrong-target propensity under Exp 6's criterion: among all
    draws on items whose normalized answer differs from a_i, the
    fraction whose normalized output equals a_i."""
    at = cap["answer_type"]
    ans = [v6.normalize_answer_side(str(it["answer"]), at) for it in cap["eval_items"]]

    def norm(d):
        try:
            return v6.normalize_6(d, at)
        except IndexError:
            return ""
    per_item = [None] * b6.N_ITEMS
    n_each = None
    for row in rows:
        draws = [d for s in seeds for d in row["draws"][str(s)]]
        n_each = len(draws)
        per_item[row["item"]] = Counter(norm(d) for d in draws)
    if any(c is None for c in per_item):
        raise ValueError("answer_prior_6: coverage incomplete")
    total, by_answer = Counter(), {}
    for i, c in enumerate(per_item):
        total.update(c)
        acc = by_answer.setdefault(ans[i], [Counter(), 0])
        acc[0].update(c)
        acc[1] += n_each
    n_total = b6.N_ITEMS * n_each
    out = []
    for i in range(b6.N_ITEMS):
        a = ans[i]
        num, den = total[a] - by_answer[a][0][a], n_total - by_answer[a][1]
        out.append(float(num) / den if den > 0 else 0.0)
    return out


# S12: `ipa_word` is scored by exact match against ONE transcription
# convention (plan delta B-27). The relaxed form removes what conventions
# differ on and nothing else; the table is fixed here, before any model
# wrote a transcription: stress and length marks, the syllable dot, the
# enclosing slashes or brackets, the two affricate ligatures, and three
# letters that eng_to_ipa writes its own way.
IPA_RUNG_6 = "ipa_word"
RELAXED_IPA_6 = (("ˈ", ""), ("ˌ", ""), ("ː", ""), (".", ""), ("ʧ", "tʃ"), ("ʤ", "dʒ"),
                 ("ʌ", "ə"), ("ɹ", "r"), ("ɡ", "g"))


def relaxed_ipa(text) -> str:
    """The strict criterion's token, relaxed. Total on the draw side."""
    s = v6.normalize_6(str(text), "ipa").strip("/[]")
    for a, b in RELAXED_IPA_6:
        s = s.replace(a, b)
    return s


def ipa_relaxed_6(ctx, sweeps, outs, *, n_perm, n_boot) -> dict:
    """Every test re-read with `ipa_word` scored under the relaxed
    criterion on BOTH sides — the predictor's draws and the outcome's
    continuations — and admitted to a family's rungs by the ruled rule
    applied to the relaxed count of the SEALED endpoint read."""
    kw = dict(n_perm=n_perm, n_boot=n_boot)
    rung, strata = IPA_RUNG_6, ctx["strata"]
    items = ctx["battery"][rung]["eval_items"]
    strict = [v6.normalize_answer_side(str(it["answer"]), "ipa") for it in items]
    want = [relaxed_ipa(it["answer"]) for it in items]
    if not all(want):
        raise ValueError("ipa_relaxed_6: an answer relaxes to the empty string")
    floor = Counter(want).most_common(1)[0][1] / b6.N_ITEMS
    x = {}
    for t, tier in (("A", "pythia_1b"), ("B", "olmo2_1b")):
        seeds = r6.tier_shape(tier, "main")["seeds"]
        counts = [None] * b6.N_ITEMS
        for row in ctx["units"][(tier, "main", rung)]["rows"]:
            i = int(row["item"])
            counts[i] = sum(1 for s in seeds for d in row["draws"][str(s)]
                            if relaxed_ipa(d) == want[i])
        if any(c is None for c in counts):
            raise ValueError(f"ipa_relaxed_6: {tier} coverage incomplete")
        if any(c < a for c, a in zip(counts, ctx["pred"][t]["x"][rung])):
            raise ValueError("ipa_relaxed_6: a relaxed count below the strict one")
        x[t] = counts
    res, keyed = {}, {}
    for f in fm.FAMILIES_6:
        grid = tuple(int(s) for s in fm.grid(f))
        steps = sweeps[f]["steps"]
        bits = {s: [int(relaxed_ipa(c) == w)
                    for c, w in zip(steps[s][rung]["continuations"], want)]
                for s in grid}
        y = [sum(bits[s][i] for s in grid) for i in range(b6.N_ITEMS)]
        sealed = ctx["endpoint"][f]["stage1_final"]["records"][rung]
        k = sum(1 for c, w in zip(sealed["continuations"], want)
                if relaxed_ipa(c) == w)
        if k < int(sealed["correct"]):
            raise ValueError("ipa_relaxed_6: a relaxed count below the strict one")
        bar = fl.clears(k, b6.N_ITEMS, floor)
        R = tuple(ctx["rung_sets"]["families"][f]["R"])
        R2 = tuple(r for r in b6.RUNGS_6
                   if (r != rung and r in R) or (r == rung and bar["significant"]))
        out2 = dict(outs[f])
        out2[rung] = {"y": y, "n_pos": int(sum(1 for v in y if v > 0))}
        per = {}
        for t in ("A", "B"):
            x2 = dict(ctx["pred"][t]["x"])
            x2[rung] = x[t]
            keyed[(t, f)] = _run_test(x2, LABEL_OF[t], out2, strata, R2, **kw)
            d = {}
            for name, xs, ys in (("strict", ctx["pred"][t]["x"][rung], outs[f][rung]["y"]),
                                 ("relaxed", x[t], y)):
                v = st.somers_d_within(xs, ys, strata[rung]["strata"])["d"]
                d[name] = float(v) if np.isfinite(v) else None
            per[t] = {"test": keyed[(t, f)], "d_ipa_word": d,
                      "live_items": {"strict": int(sum(
                          1 for c in ctx["pred"][t]["x"][rung] if c > 0)),
                          "relaxed": int(sum(1 for c in x[t] if c > 0))}}
        res[f] = {"endpoint_count": {"strict": int(sealed["correct"]), "relaxed": int(k)},
                  "relaxed_floor": floor, "relaxed_clears": bool(bar["significant"]),
                  "strict_in_R": rung in R, "rungs": list(R2),
                  "ever": {"strict": int(outs[f][rung]["n_pos"]),
                           "relaxed": int(out2[rung]["n_pos"])},
                  "predictors": per}
    stt = {t: status_of({f: keyed[(t, f)] for f in fm.FAMILIES_6}) for t in ("A", "B")}
    return {"relaxed": [list(p) for p in RELAXED_IPA_6],
            "n_answers_changed": int(sum(1 for a, b in zip(strict, want) if a != b)),
            "n_distinct_relaxed_answers": len(set(want)),
            "families": res, "statuses": stt,
            "world": world_of(stt["A"]["status"], stt["B"]["status"]),
            "note": "proposed at the build (plan delta B-27), non-gating: exact match "
                    "rewards one transcription convention; this reading removes the "
                    "convention from both sides. The primary's criterion is the "
                    "design's."}


def beyond_heuristic_6(ctx, outs, heuristics, *, n_perm, n_boot) -> dict:
    """S13: every test re-read over R_heuristic — the rungs of R_f whose
    sealed endpoint count also clears the HEURISTIC floor."""
    kw = dict(n_perm=n_perm, n_boot=n_boot)
    fams = ctx["rung_sets"]["families"]
    keyed = {(t, f): _run_test(ctx["pred"][t]["x"], LABEL_OF[t], outs[f],
                               ctx["strata"], tuple(fams[f]["R_heuristic"]), **kw)
             for t, f in TESTS_6}
    stt = {t: status_of({f: keyed[(t, f)] for f in fm.FAMILIES_6}) for t in ("A", "B")}
    return {"rungs": {f: {"R": list(fams[f]["R"]),
                          "R_heuristic": list(fams[f]["R_heuristic"]),
                          "not_beyond": [r for r in fams[f]["R"]
                                         if r not in fams[f]["R_heuristic"]]}
                      for f in fm.FAMILIES_6},
            "heuristic_floors": {r: {"heuristic": heuristics[r]["heuristic"],
                                     "heuristic_floor": heuristics[r]["heuristic_floor"]}
                                 for r in b6.RUNGS_6},
            "tests": {pw6.test_name(t, f): keyed[(t, f)] for t, f in TESTS_6},
            "statuses": stt,
            "world": world_of(stt["A"]["status"], stt["B"]["status"]),
            "note": "proposed at the build (plan deltas B-22, B-31), non-gating: a "
                    "rung a surface guesser can clear is read by the primary and "
                    "left out here. On `temporal` a string match scores every item, "
                    "so the rung is in no R_heuristic."}


def _subset_tests(x, label, out, strata, rungs, groups: dict, **kw) -> dict:
    return {g: _run_test({r: x[r] for r in rungs if r in members}, label, out,
                         strata, tuple(r for r in rungs if r in members), **kw)
            for g, members in groups.items()}


TYPE_GROUPS_6 = {t: tuple(r for r in b6.RUNGS_6 if b6.RUNG_TYPE_OF[r] == t)
                 for t in ("arithmetic", "string", "choice")}
CLASS_GROUPS_6 = {c: tuple(r for r in b6.RUNGS_6 if b6.WEI_CLASS_OF[r] == c)
                  for c in ("E.2", "E.3")}


def anchors_side_by_side(test, family, x, out, strata) -> dict:
    """S10: per-rung D on the base-8 pair through the NEW pipeline
    beside the committed per-rung D, against the declared tolerance."""
    com = rf.committed_test(test, family)
    rows = {}
    for r in b6.ANCHORS_6:
        d = st.somers_d_within(x[r], out[r]["y"], strata[r]["strata"])["d"]
        ref = com["per_rung_d"].get(r)
        diff = None if (ref is None or not np.isfinite(d)) else float(d) - float(ref)
        rows[r] = {"d_new": float(d) if np.isfinite(d) else None, "d_committed": ref,
                   "diff": diff, "within": (None if diff is None
                                            else abs(diff) <= rf.D_TOLERANCE_6)}
    return {"rungs": rows, "tolerance": rf.D_TOLERANCE_6,
            "committed": {k: com[k] for k in ("experiment", "path", "conditioning")}}


def secondaries_6(ctx, sweeps, outs, tests, *, n_perm, n_boot) -> dict:
    kw = dict(n_perm=n_perm, n_boot=n_boot)
    strata, battery, floors = ctx["strata"], ctx["battery"], ctx["floors"]
    structure, heuristics = ctx["structure"], ctx["heuristics"]
    pred, rsets = ctx["pred"], ctx["rung_sets"]["families"]
    xa, xb, x410 = pred["A"]["x"], pred["B"]["x"], pred["410m"]["x"]
    sec, sec_failures = {}, []

    def _sec(name, thunk):
        val, f = collect_total(thunk, name)
        if f:
            sec[name] = {"failed": f[0]}
            sec_failures.extend(f)
        else:
            sec[name] = val

    def per_family(fn):
        return {f: fn(f, tuple(rsets[f]["R"])) for f in fm.FAMILIES_6}

    _sec("S1 ladder", lambda: per_family(lambda f, R: {
        "ladder": an2k.ladder_2k(pred["A"]["bits"], outs[f], strata, R, "1b", **kw),
        "blocks": an2k.s1_blocks(pred["A"]["bits"], outs[f], strata, R, "1b", **kw)}))
    _sec("S2 410m at 256", lambda: per_family(lambda f, R: _run_test(
        x410, "410m:k256", outs[f], strata, R, **kw)))

    def _s3(f, R):
        both = [r for r in tests[("A", f)]["eligible"]
                if r in tests[("B", f)]["eligible"]]
        return {"B_beyond_A": _run_test(
                    xb, LABEL_OF["B"], outs[f],
                    an2i._composite_strata_median(strata, xa, R), R, **kw),
                "A_beyond_B": _run_test(
                    xa, LABEL_OF["A"], outs[f],
                    an2i._composite_strata_median(strata, xb, R), R, **kw),
                "paired_difference": an2m.s3_paired_difference_2m(
                    xa, xb, outs[f], strata, both, n_boot=n_boot)}
    _sec("S3 the two predictors", lambda: per_family(_s3))

    def _s4(f, R):
        return {t: {"by_type": _subset_tests(pred[t]["x"], LABEL_OF[t], outs[f],
                                             strata, R, TYPE_GROUPS_6, **kw),
                    "by_class": _subset_tests(pred[t]["x"], LABEL_OF[t], outs[f],
                                              strata, R, CLASS_GROUPS_6, **kw)}
                for t in ("A", "B")}
    _sec("S4 by type and class", lambda: per_family(_s4))

    def _s5():
        t = r6.tier_shape("olmo2_1b", "main")
        rows = ctx["units"]
        pi = {r: answer_prior_6(rows[("olmo2_1b", "main", r)]["rows"], battery[r],
                                seeds=t["seeds"]) for r in b6.RUNGS_6}
        return {"test": per_family(lambda f, R: _run_test(
                    pi, "olmo1b:pi", outs[f], strata, R, **kw)),
                "non_gating": True,
                "source": "wrong-target propensity on the sealed OLMo-2 1B draws"}
    _sec("S5 answer prior", _s5)

    def _s6():
        twin = ctx["units"]
        out = {"init": {f: {r: {"count": int(ctx["endpoint"][f]["init"]["records"][r]
                                             ["correct"]),
                                "floor": floors[r]["floor"],
                                "clears": bool(fl.clears(
                                    ctx["endpoint"][f]["init"]["records"][r]["correct"],
                                    b6.N_ITEMS, floors[r]["floor"])["significant"])}
                            for r in b6.RUNGS_6} for f in fm.FAMILIES_6},
               "predictor_twin": {}}
        t = r6.tier_shape("pythia_1b", "twin")
        for r in t["rungs"]:
            c = r6.counts_of(twin[("pythia_1b", "twin", r)]["bits"])
            out["predictor_twin"][r] = {"verified": int(sum(c)),
                                        "n_draws": b6.N_ITEMS * t["k"],
                                        "live_items": int(sum(1 for v in c if v > 0))}
        # the pilot MEASURED liveness before the main tier ran; what it
        # showed is printed beside what the main tier then showed. It
        # feeds nothing: the power record reads the sealed main tier.
        t = r6.tier_shape("pythia_1b", "pilot")
        out["pilot"] = {}
        for r in t["rungs"]:
            c = r6.counts_of(twin[("pythia_1b", "pilot", r)]["bits"])
            out["pilot"][r] = {
                "verified": int(sum(c)), "n_draws": b6.N_ITEMS * t["k"],
                "live_items": int(sum(1 for v in c if v > 0)),
                "live_items_main": int(sum(1 for v in xa[r] if v > 0))}
        return out
    _sec("S6 referents", _s6)

    def _s7(f, R):
        rl = rung_level(outs[f], floors, heuristics, f, b6.RUNGS_6)
        flat = [r for r in b6.RUNGS_6 if r not in R]
        return {"rung_level": rl, "flat_rungs": flat,
                "transient_clears_on_flat": {r: rl[r]["transient_clears"] for r in flat
                                             if rl[r]["transient_clears"]},
                "collapses": collapses(sweeps[f]["steps"], b6.ALL_RUNGS_6),
                "ceiling_fraction": ceiling_fraction(outs[f], b6.RUNGS_6,
                                                     n_steps=len(fm.grid(f))),
                "nonfinite_units": {int(s): int(ld["n_nonfinite_logits"])
                                    for s, ld in sweeps[f]["loads"].items()
                                    if ld["n_nonfinite_logits"]},
                "live_items": {t: {r: int(sum(1 for c in pred[t]["x"][r] if c > 0))
                                   for r in b6.RUNGS_6} for t in ("A", "B")},
                "control": {int(s): int(sweeps[f]["steps"][s][b6.CONTROL_6]["correct"])
                            for s in sorted(sweeps[f]["steps"])}}
    _sec("S7 textures", lambda: per_family(_s7))

    def _s8():
        res = {}
        for f in fm.FAMILIES_6:
            for g in fm.FAMILIES_6:
                if f == g:
                    continue
                R = tuple(r for r in rsets[f]["R"] if r in rsets[g]["R"])
                x = {r: [int(v) for v in outs[g][r]["y"]] for r in R}
                res[f"{g}->{f}"] = {"rungs": list(R), "test": _run_test(
                    x, f"{g}:count", outs[f], strata, R, **kw)}
        return {"pairs": res, "descriptive": True}
    _sec("S8 outcome order", _s8)

    _sec("S9 two batteries", lambda: {
        pw6.test_name(t, f): {
            "new_battery": {"T": tests[(t, f)]["stratified"]["T"],
                            "p": tests[(t, f)]["stratified"]["p"],
                            "rungs": list(tests[(t, f)]["eligible"]),
                            "fires": bool(tests[(t, f)]["fires"])},
            "battery_2c": {k: v for k, v in rf.committed_test(t, f).items()
                           if k != "per_rung_d"}}
        for t, f in TESTS_6})
    _sec("S10 anchors", lambda: {
        pw6.test_name(t, f): anchors_side_by_side(t, f, pred[t]["x"], outs[f], strata)
        for t, f in TESTS_6})

    def _s11():
        res = {pw6.test_name(t, f): _run_test(
            pred[t]["x"], LABEL_OF[t], outs[f], structure, tuple(rsets[f]["R"]), **kw)
            for t, f in TESTS_6}
        keyed = {(t, f): res[pw6.test_name(t, f)] for t, f in TESTS_6}
        st = {t: status_of({f: keyed[(t, f)] for f in fm.FAMILIES_6})
              for t in ("A", "B")}
        return {"structure_of": dict(s6.STRUCTURE_OF_6),
                "structure_counts": {r: structure[r]["structure_counts"]
                                     for r in b6.RUNGS_6},
                "tests": res, "statuses": st,
                "world": world_of(st["A"]["status"], st["B"]["status"]),
                "note": "proposed at the build (plan delta B-21), non-gating: every "
                        "test re-read with the item's structure level crossed into "
                        "its stratum. A forecast that is only 'both models get the "
                        "read-off items first' loses its T here."}
    _sec("S11 structure-conditioned", _s11)
    _sec("S12 ipa relaxed", lambda: ipa_relaxed_6(ctx, sweeps, outs, **kw))
    _sec("S13 beyond the heuristic floor",
         lambda: beyond_heuristic_6(ctx, outs, heuristics, **kw))

    def _sens():
        first = {f: first_correct_outcome(outs[f], f, rsets[f]["R"])
                 for f in fm.FAMILIES_6}
        fc = {(t, f): _run_test(pred[t]["x"], LABEL_OF[t], first[f], strata,
                                tuple(rsets[f]["R"]), **kw) for t, f in TESTS_6}
        two = {t: status_of({f: tests[(t, f)] for f in fm.FAMILIES_6}, holds_at=2)
               for t in ("A", "B")}
        fcs = {t: status_of({f: fc[(t, f)] for f in fm.FAMILIES_6})
               for t in ("A", "B")}
        return {
            "first_correct": {
                "tests": {pw6.test_name(t, f): fc[(t, f)] for t, f in TESTS_6},
                "statuses": fcs,
                "world": world_of(fcs["A"]["status"], fcs["B"]["status"])},
            "B_conditioned_on_A": per_family(lambda f, R: {
                "zero_cut": _run_test(xb, LABEL_OF["B"], outs[f],
                                      an2i._composite_strata(strata, xa, R), R, **kw),
                "median": _run_test(xb, LABEL_OF["B"], outs[f],
                                    an2i._composite_strata_median(strata, xa, R),
                                    R, **kw)}),
            "naming_rule_two_of_four": {
                "statuses": two,
                "world": world_of(two["A"]["status"], two["B"]["status"])}}
    _sec("sensitivities", _sens)
    sec["note"] = NO_ALPHA_NOTE_6.format(name="Every secondary")
    sec["failures"] = sec_failures
    return sec


# ---------------------------------------------------------------------- run
_LITERAL = object()


def _keyed(tests: dict) -> dict:
    return {pw6.test_name(t, f): v for (t, f), v in tests.items()}


def run(root=EXP6, *, write=False, n_perm=N_PERM, n_boot=N_BOOT, tag_exists=None,
        blob_sha=None, blobs_bound=None, referents_sha=_LITERAL,
        imports_pinned=_LITERAL, frozen_check=None, out_path=None) -> dict:
    # `frozen_check`, `referents_sha=False` and `imports_pinned=False`
    # are TEST-ONLY injections; the campaign passes none of them, and
    # `pins_active` records which pins really ran.
    root = Path(root)
    failures = []
    if referents_sha is _LITERAL:
        referents_sha = REFERENTS_6_SHA256
    if imports_pinned is _LITERAL:
        imports_pinned = None if p6.IMPORTED_SHA256_6 is None else True

    # ---- the halt scan FIRST (2d F-1; both artifacts refuse, 2k F-1)
    marks, f = collect_total(lambda: r6.halt_markers(root), "6 halt scan")
    failures += f
    for m in marks or []:
        failures.append(f"6 halt marker: {os.path.relpath(str(m), str(root))} — a "
                        f"runner halted")
    # ---- pins
    _, f = collect_total(frozen_check or p6.check_frozen_6, "6 frozen modules")
    failures += f
    if imports_pinned:
        _, f = collect_total(p6.check_imports_6, "6 import surface (entry)")
        failures += f
    elif imports_pinned is not False:
        failures.append("6 import surface: not pinned (build incomplete)")
    prereg, f = collect_total(
        lambda: p6.require_prereg_6(tag_exists=tag_exists, blob_sha=blob_sha),
        "6 prereg tag")
    failures += f
    if referents_sha is None:
        failures.append("6 referent manifest: not pinned (build incomplete)")
    elif referents_sha is not False:
        mf, f = collect_total(
            lambda: mkr.check_referents(mkr.PATH, sha_pin=referents_sha),
            "6 referent manifest")
        failures += f + (mf or [])

    # ---- everything sealed before the sweeps
    got, f = collect_total(
        lambda: load_sealed_stages(root, tag_exists=tag_exists,
                                   blobs_bound=blobs_bound), "6 sealed stages")
    failures += f
    ctx, sb = got if got is not None else ({}, [])
    failures += sb
    rung_sets = ctx.get("rung_sets")

    # ---- the endpoint seal, the power record
    esl = {"tag": r6.ENDPOINT_SEAL_TAG_6, "failures": ["rung sets missing"]}
    endpoint_sha = None
    if rung_sets is not None:
        paths, f = collect_total(lambda: se.seal_paths(root), "6 endpoint seal paths")
        failures += f
        if paths is not None:
            esl = {"tag": r6.ENDPOINT_SEAL_TAG_6, "n_paths": len(paths),
                   "failures": p6.seal_failures(
                       r6.ENDPOINT_SEAL_TAG_6, paths, tag_exists=tag_exists,
                       blobs_bound=blobs_bound)}
            endpoint_sha, f = collect_total(lambda: se.endpoint_sha256(root),
                                            "6 endpoint composite sha")
            failures += f
    failures += [f"6 endpoint seal binding: {m}" for m in esl["failures"]]
    power, f = collect_total(lambda: r6.read_json(r6.power_path(root)),
                             "6 power record")
    failures += f
    inputs = None
    if not failures:
        inputs, f = collect_total(lambda: test_inputs(ctx), "6 test inputs")
        failures += f
    if inputs is not None and power is not None:
        def _power():
            bad = pw6.claim_failures(power, inputs)
            if power.get("predictor_sha256") != ctx["seal"]["sha256"]:
                bad.append("6 power: predictor_sha256 is not the predictor seal's")
            if power.get("rung_sets_sha256") != \
                    r6.sha256_file(r6.rung_sets_path(root)):
                bad.append("6 power: rung_sets_sha256 is not the rung sets'")
            return bad
        pf, f = collect_total(_power, "6 power claims")
        failures += f + (pf or [])

    # ---- the four sweeps
    sweeps = {}
    ready = (ctx.get("battery") is not None and ctx.get("endpoint") is not None
             and endpoint_sha is not None and isinstance(ctx.get("seal"), dict))
    for fam in fm.FAMILIES_6:
        def _load(fam=fam):
            if not ready or set(ctx["endpoint"].get(fam, {})) != \
                    set(r6.ENDPOINT_WHICH_6):
                _raise("the sealed stages are incomplete")
            return load_sweep_family(
                root, fam, battery=ctx["battery"], seal_sha=ctx["seal"]["sha256"],
                endpoint_sha=endpoint_sha, hosts=ctx["hosts"],
                sealed=ctx["endpoint"][fam]["stage1_final"]["records"],
                sealed_load=ctx["endpoint"][fam]["stage1_final"]["load"])
        got, f = collect_total(_load, f"6 sweep {fam}")
        failures += f
        if got is not None:
            failures += got[0]
            sweeps[fam] = got[1]

    # ---- the gating core: outcomes and the eight tests, one unit
    core = None
    if not failures:
        def _core():
            outs = {fam: outcomes_6(sweeps[fam]["steps"], fam)
                    for fam in fm.FAMILIES_6}
            tests = {}
            for t, fam in TESTS_6:
                R = tuple(rung_sets["families"][fam]["R"])
                tests[(t, fam)] = _run_test(ctx["pred"][t]["x"], LABEL_OF[t],
                                            outs[fam], ctx["strata"], R,
                                            n_perm=n_perm, n_boot=n_boot)
            return outs, tests
        core, f = collect_total(_core, "6 primary")
        failures += f
    if not failures and imports_pinned:
        _, f = collect_total(p6.check_imports_6, "6 import surface (exit)")
        failures += f

    seal = ctx.get("seal")
    referents = {
        "failures": list(failures), "prereg": prereg,
        "predictor_seal": ctx.get("seal_binding"),
        "predictor_sha256": seal.get("sha256") if isinstance(seal, dict) else None,
        "endpoint_seal": esl, "endpoint_sha256": endpoint_sha,
        "rung_sets": rung_sets, "gate1p": ctx.get("gate1p"),
        "hosts": sorted(str(h) for h in (ctx.get("hosts") or {})),
        "sweep_hosts": {fam: s["hosts"] for fam, s in sweeps.items()},
        "referent_manifest_sha256": REFERENTS_6_SHA256,
        "pins_active": {"frozen_modules": frozen_check is None,
                        "import_surface": bool(imports_pinned),
                        "referent_manifest": referents_sha not in (False, None),
                        "prereg_tag": tag_exists is None and blob_sha is None,
                        "seal_tags": tag_exists is None and blobs_bound is None},
        "dtype": fm.DTYPE_6, "batch_size": fm.BATCH_SIZE_6,
        "tolerance_per_rung": rf.TOL_PER_RUNG_6, "power": power}
    common = {"known_inputs_caveat": KNOWN_INPUTS_CAVEAT_6,
              "calibration_note": CALIBRATION_SENTENCE_6, "bounds": BOUNDS_6,
              "n_perm": n_perm, "n_boot": n_boot, "git_sha": p6.git_sha(),
              "model_contact": "none at analysis"}

    def _insufficient():
        tree = verdict_6(failures, None, None, None)
        return {"verdict": tree["verdict"], "reason": tree["reason"], **common,
                "licensed_sentence": LICENSED_6["INSUFFICIENT_DATA"],
                "statuses": None, "referents": referents, "tests": None,
                "secondaries": None}

    if failures or core is None:
        v = _insufficient()
    else:
        outs, tests = core
        tree = verdict_6([], tests, rung_sets, power)
        sec = secondaries_6(ctx, sweeps, outs, tests, n_perm=n_perm, n_boot=n_boot)
        v = {"verdict": tree["verdict"], "reason": tree["reason"], **common,
             "licensed_sentence": licensed_6(tree), "statuses": tree["statuses"],
             "modifiers": tree["modifiers"], "disclosures": tree["disclosures"],
             "referents": referents, "tests": _keyed(tests), "secondaries": sec}
        if imports_pinned:
            _, f = collect_total(p6.check_imports_6,
                                 "6 import surface (post-secondaries)")
            if f:
                failures += f
                referents["failures"] = list(failures)
                v = _insufficient()
    if write:
        outp = Path(out_path or r6.verdict_path(root))
        outp.parent.mkdir(parents=True, exist_ok=True)
        outp.write_text(json.dumps(an2i._json_safe(v), indent=1,
                                   default=an2i._jsonable, allow_nan=False))
    return v


if __name__ == "__main__":
    out = run(write="--write" in sys.argv)
    print(json.dumps({k: out[k] for k in ("verdict", "reason")}, indent=1))
