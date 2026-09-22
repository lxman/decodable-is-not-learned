# experiments/exp5/analyze_5.py
"""Exp 5 frozen analysis (design `experiment-5-design.md` §3.7-§3.8, §5,
§6): loaders with contracts, gates 0-7 (host attestation, the two-path
identity gate, the finals' known-answer tolerance, the slice, every
unit's contract, the search's own deterministic replay, the power
record, the projection's ancestry, the tags), the primary statistic,
the direction modifier, the tree, eleven named secondaries and the
licence block.

Everything not defined here is frozen and re-asserted by sha256
(`battery_5.FROZEN_SHA256_5`/`check_frozen_5`, `battery_5.IMPORTED_
SHA256_5`/`check_imports_5`): 2d's argmax harness and floors, 2g's/2h's
committed interior referents, exp3c's total verify wrapper by way of
2d's `load_verify`, 2i's `collect_total`/`require_seal_2i`. Every
loader refusal is COLLECTED and delivered as INSUFFICIENT_DATA with
the reason verbatim (lesson 8): `collect_total_5` widens 2i's already-
widened exception surface by exactly `zipfile.BadZipFile`, `KeyError`,
`OSError`, `ImportError`, `EOFError` — a DATA problem is a refusal,
never a traceback; any OTHER exception is a logic defect and CRASHES
`run()` (the totality contract protects data, not bugs), while a
wrong-shaped call site (a label not prefixed `"5 "`) is a programming
error and is RAISED, never laundered.

Tree (design §3.8): INSUFFICIENT_DATA (any gate) -> UNDETERMINED (fewer
than 20 live cells with a defined P, or fewer than 5 rungs carrying
them) -> NOT-MATCHED (rung-block p < .01 and T >= .01), with the
modifier LARGE-AHEAD / SMALL-AHEAD / MIXED / THIN -> MATCHED
(otherwise), read under the power declaration."""
from __future__ import annotations

import bisect as _bisect
import json
import math
import subprocess
import sys
import zipfile
from pathlib import Path

EXP5 = Path(__file__).resolve().parent
EXPERIMENTS = EXP5.parent
REPO = EXPERIMENTS.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp5 import _threads_5  # noqa: E402,F401 — before numpy (transitively)
import numpy as np  # noqa: E402
from scipy.stats import spearmanr  # noqa: E402

from experiments.exp2d import analyze_2d as a2d  # noqa: E402
from experiments.exp2d import battery_2d as bt  # noqa: E402
from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp2h import battery_2h as bh  # noqa: E402
from experiments.exp2i import analyze_2i as an2i  # noqa: E402
from experiments.exp5 import battery_5 as b5  # noqa: E402
from experiments.exp5 import power_5 as pw  # noqa: E402
from experiments.exp5 import search_5 as se5  # noqa: E402
from experiments.exp5 import slice_5 as sl5  # noqa: E402
from experiments.exp5 import stats_5 as ss  # noqa: E402

RESULTS_5 = EXP5 / "results"
REFERENTS_PATH_5 = EXP5 / "referents_5.json"

# Task 6 pins these; a plain None means "not pinned yet — build incomplete"
# and is read by `run()`'s `_LITERAL` default resolution (4c's convention).
REFERENTS_5_SHA256 = "e7a1ea3b65d915bc0f6ba7711a938b07ff4e267dc9f2a190798f3135991070e0"

_LITERAL = object()

CAVEAT_5 = ("one family, one battery of 34 synthetic tasks, sizes to 12b, loss matched on a "
            "2M-token validation slice")

# design §6, one body per licence CELL (world, or world x modifier for NOT-MATCHED).
_LICENCE_BODY_5 = {
    "MATCHED-POWERED": (
        "on Pythia, across the size pairs read to date, a larger model read at the checkpoint "
        "where its held-out loss equals a smaller model's final loss has the smaller model's "
        "profile on this battery to within the larger model's own wobble between neighbouring "
        "checkpoints; the scoreboard states the resolution this reading was bought at: an "
        "average excess of five items per 500 detectable, two or three not"),
    "MATCHED-UNDERPOWERED": (
        "not distinguishable at this resolution — under DECLARED UNDERPOWERED IN ADVANCE nothing "
        "more is claimed; S1's ledger is quoted only for the named cells it contains"),
    "NOT-MATCHED-LARGE-AHEAD": (
        "at equal loss the larger Pythia models are ahead of what the smaller ones ever become "
        "on these tasks; loss is not sufficient for the profile on this battery — the "
        "prediction's own falsifier at lab scale. The lens framing's 'bits bought with loss' "
        "loses its cleanest quantitative form; the essay keeps the framing and loses the claim "
        "that loss is the whole currency. S3's composition reading is printed beside it."),
    "NOT-MATCHED-SMALL-AHEAD": (
        "the annealed smaller model is ahead at equal loss; the prediction as written fails in "
        "the other direction. The licensed sentence names the candidates the design cannot "
        "separate — exposure, annealing, optimizer state, loss composition (S3, S6) — and says "
        "aggregate loss under-describes fidelity, without choosing among them. Not licensed: "
        "size-dependent emergence."),
    "NOT-MATCHED-MIXED": (
        "the discrepancy is real and has no direction the design can read; the essay reports the "
        "excess and the performability ledger, no mechanism sentence"),
    "NOT-MATCHED-THIN": (
        "the discrepancy is real (rung-block p < .01 and T >= the bar) but fewer than 8 cells "
        "carry R > P, so the sign test has no direction to read; the essay reports the excess "
        "and the ledger, no mechanism sentence"),
    "UNDETERMINED": (
        "the battery did not supply the cells; the essay's paragraph is unchanged and "
        "experiments.md records the resolution reached"),
    "INSUFFICIENT_DATA": "nothing; the record states which gate failed, verbatim",
}


# ------------------------------------------------------------- totality

def collect_total_5(thunk, label):
    """`analyze_2i.collect_total` (itself 2h's/2g's chain — `ValueError`,
    `FileNotFoundError`, `KeyError`, `RuntimeError`, `TypeError`,
    `AttributeError`, `OSError`, `EOFError`, `zlib.error`) widened by
    `zipfile.BadZipFile`, `KeyError`, `OSError`, `ImportError`,
    `EOFError`; any OTHER exception is a logic defect and CRASHES —
    the totality contract protects DATA problems only (2i's own
    docstring: a reachable exception outside the named set "would be a
    logic defect in the instrument, which must surface as a crash
    rather than be laundered into a refusal"). `label` MUST start with
    `"5 "` (a call-site programming error, raised, not laundered)."""
    if not isinstance(label, str) or not label.startswith("5 "):
        raise ValueError(f"collect_total_5: label {label!r} must start with the '5 ' prefix")
    try:
        return an2i.collect_total(thunk, label)
    except (zipfile.BadZipFile, KeyError, OSError, ImportError, EOFError) as e:
        return None, [f"{label}: {type(e).__name__}: {e}"]


# --------------------------------------------------------------- gate 1

def gate1a_failures_5(rec: dict) -> list:
    bad = []
    if rec.get("digests_equal") is not True:
        bad.append(f"gate 1(a): digests_equal {rec.get('digests_equal')!r} is not True")
    conts_compared = rec.get("continuations_compared") or {}
    for r in b5.RUNGS:
        if conts_compared.get(r) != b5.N_ITEMS:
            bad.append(f"gate 1(a)/{r}: continuations_compared {conts_compared.get(r)!r} != "
                       f"{b5.N_ITEMS}")
    diffs = rec.get("continuation_diffs") or {}
    for r in b5.RUNGS:
        if diffs.get(r):
            bad.append(f"gate 1(a)/{r}: {diffs.get(r)} continuation diffs between the two loader "
                       f"paths")
    if rec.get("loss_equal") is not True:
        bad.append(f"gate 1(a): loss_equal {rec.get('loss_equal')!r} is not True")
    if rec.get("prereg_tag") != b5.PREREG_TAG_5:
        bad.append(f"gate 1(a): prereg_tag {rec.get('prereg_tag')!r} != {b5.PREREG_TAG_5!r}")
    if rec.get("pass") is not True:
        bad.append(f"gate 1(a): pass {rec.get('pass')!r} is not True")
    # Freeze F-2: the three flags above are the runner's ATTESTATIONS; the
    # record also carries what they were computed from, so re-derive them
    # (measured, not attested — 2i F-1 / Exp 4 F-1's form).
    da, db = rec.get("digest_2c_path"), rec.get("digest_candidate_path")
    if not (isinstance(da, str) and len(da) == 64 and da == db):
        bad.append(f"gate 1(a): digest_2c_path {da!r} != digest_candidate_path {db!r} "
                   f"(re-derived; digests_equal is attested)")
    la, lb = rec.get("loss_2c_path"), rec.get("loss_candidate_path")
    if not (isinstance(la, float) and isinstance(lb, float) and repr(la) == repr(lb)):
        bad.append(f"gate 1(a): loss_2c_path {la!r} != loss_candidate_path {lb!r} to the bit "
                   f"(re-derived; loss_equal is attested)")
    if rec.get("per_doc_diffs") != 0:
        bad.append(f"gate 1(a): per_doc_diffs {rec.get('per_doc_diffs')!r} != 0 "
                   f"(re-derived; loss_equal is attested)")
    return bad


def gate1a_unit_failures_5(rec: dict, final_2p8b: dict) -> list:
    """Freeze F-2: gate 1(a)'s candidate-path side IS the 2.8b final unit
    (`finals_5.gate1a` runs it through `run_unit_5`), so the record's
    candidate-path loss must equal that unit's committed `_loss.json` loss
    to the bit, and — continuations being identical on every rung — the
    2c-path counts must equal the unit's committed counts. `final_2p8b` is
    `{"loss": float, "counts": {rung: int}, "digest": str}` from
    `load_units_5`."""
    bad = []
    if rec.get("digest_candidate_path") != final_2p8b.get("digest"):
        bad.append(f"gate 1(a): digest_candidate_path {rec.get('digest_candidate_path')!r} != the "
                   f"2.8b final unit's digest {final_2p8b.get('digest')!r}")
    if repr(rec.get("loss_candidate_path")) != repr(final_2p8b.get("loss")):
        bad.append(f"gate 1(a): loss_candidate_path {rec.get('loss_candidate_path')!r} != the 2.8b "
                   f"final unit's committed loss {final_2p8b.get('loss')!r}")
    counts_a = rec.get("counts_2c_path") or {}
    unit_counts = final_2p8b.get("counts") or {}
    diff = sorted(r for r in b5.RUNGS if counts_a.get(r) != unit_counts.get(r))
    if diff:
        bad.append(f"gate 1(a): counts_2c_path differs from the 2.8b final unit's committed counts "
                   f"on {diff[:6]}{'…' if len(diff) > 6 else ''} ({len(diff)} rung(s)) although the "
                   f"continuations are attested identical")
    return bad


def gate1b_failures_5(root, rec: dict) -> list:
    """Re-derived from the referent files (never trusts the record's
    own `per_size`/`counts`): every size's FINAL rung records, read
    fresh from `root`, against `battery_5.mac_final_counts_5`."""
    bad = []
    if rec.get("pass") is not True:
        bad.append(f"gate 1(b): pass {rec.get('pass')!r} is not True")
    expected_no_ref = sorted(s for s in b5.SIZES_5 if b5.GATE1_REFERENT_SOURCE_5.get(s) is None)
    got_no_ref = sorted(rec.get("no_referent") or [])
    if got_no_ref != expected_no_ref:
        bad.append(f"gate 1(b): no_referent {got_no_ref} != {expected_no_ref}")
    for size in b5.SIZES_5:
        ref = b5.mac_final_counts_5(size)
        if ref is None:
            continue
        counts = {r: int(json.loads(b5.rung_record_path_5(root, size, b5.FINAL_STEP_5, r)
                                    .read_text())["correct"]) for r in b5.RUNGS}
        bad += b5.tolerance_failures_5(counts, ref, label=f"gate 1(b) {size}")
    return bad


def gate1c_failures_5(root, size, rec: dict) -> list:
    """Re-derived: every interior step `battery_5.gate1_interior_steps_5`
    names for this size, read fresh from `root`, against
    `battery_5.mac_interior_counts_5`."""
    bad = []
    if rec.get("pass") is not True:
        bad.append(f"gate 1(c) {size}: pass {rec.get('pass')!r} is not True")
    steps = b5.gate1_interior_steps_5(size)
    rec_steps = set(rec.get("steps") or {})
    want_steps = {str(s) for s in steps}
    if rec_steps != want_steps:
        bad.append(f"gate 1(c) {size}: steps {sorted(rec_steps)} != {sorted(want_steps)}")
    for step in steps:
        ref = b5.mac_interior_counts_5(size, step)
        if ref is None:
            continue
        counts = {r: int(json.loads(b5.rung_record_path_5(root, size, step, r)
                                    .read_text())["correct"]) for r in b5.RUNGS}
        bad += b5.tolerance_failures_5(counts, ref, label=f"gate 1(c) {size}/step{step}")
    return bad


# -------------------------------------------------------------- loaders

def load_units_5(root, size, *, manifest, battery, verify_fn, host, slice_sha, n_scored=None) -> dict:
    """Every COMPLETE unit of `size` on disk (`battery_5.unit_complete_5`
    — an incomplete/torn unit directory is silently absent from every
    key here; gate 4's `units_unnamed` check is the one that catches an
    orphan directory, from the raw listing), gate 3 applied to each:
    the `_unit.json`, `_checkpoint.json`, `_loss.json` and 34 rung-
    record contracts, all-or-nothing (one bad unit raises for the
    whole size — 4c's/2i's per-size totality convention). Raises if
    the size's final is not among the complete units."""
    root = Path(root)
    n_scored = b5.SLICE_N_SCORED_5 if n_scored is None else n_scored
    d = b5.units_root_5(root) / size
    steps, counts, losses, loss_records = [], {}, {}, {}
    digests, git_shas, whys = {}, {}, {}
    n_params = None
    if d.exists():
        cand_steps = sorted(int(p.name[4:]) for p in d.iterdir()
                            if p.is_dir() and p.name.startswith("step") and p.name[4:].isdigit())
        for step in cand_steps:
            if not b5.unit_complete_5(root, size, step):
                continue
            unit_rec = json.loads(b5.unit_record_path_5(root, size, step).read_text())
            bad = b5.unit_record_failures_5(unit_rec, b5.unit_dir_5(root, size, step))
            ck_rec = json.loads(b5.checkpoint_record_path_5(root, size, step).read_text())
            entry = b5.entry_5(manifest, size, step)
            bad += b5.checkpoint_record_failures_5(ck_rec, size=size, step=step, entry=entry)
            # Freeze F-3: the checkpoint record and the unit record carry the
            # host attestation too; gate 0 compared only _loss and the rungs.
            bad += b5._same_host(ck_rec, host, f"{size}/step{step}/_checkpoint")
            if unit_rec.get("host_sha256") != host.get("sha256"):
                bad.append(f"{size}/step{step}/_unit.json: host_sha256 is not the host record's")
            ls_rec = json.loads(b5.loss_record_path_5(root, size, step).read_text())
            bad += b5.loss_record_failures_5(ls_rec, size=size, step=step, host=host,
                                             slice_sha=slice_sha, n_scored=n_scored)
            rung_counts = {}
            for rung in b5.RUNGS:
                rg_rec = json.loads(b5.rung_record_path_5(root, size, step, rung).read_text())
                bad += b5.rung_record_failures_5(rg_rec, size=size, step=step, rung=rung,
                                                 cap=battery[rung], entry=entry, verify_fn=verify_fn,
                                                 host=host)
                rung_counts[rung] = int(rg_rec.get("correct", -1))
            if not unit_rec.get("why"):
                bad.append(f"{size}/step{step}/_unit.json: why missing")
            if bad:
                raise ValueError(f"{size}/step{step}: gate 3 contract failure(s): {bad[:8]}")
            steps.append(step)
            counts[step] = rung_counts
            losses[step] = float(ls_rec["loss"])
            loss_records[step] = ls_rec
            digests[step] = ck_rec.get("digest")
            git_shas[step] = unit_rec.get("git_sha")
            whys[step] = unit_rec.get("why")
            if n_params is None:
                n_params = ck_rec.get("n_params")
    if b5.FINAL_STEP_5 not in steps:
        raise ValueError(f"{size}: the final (step{b5.FINAL_STEP_5}) is not among the complete units")
    return {"steps": sorted(steps), "counts": counts, "losses": losses, "loss_records": loss_records,
            "digests": digests, "n_params": n_params, "git_shas": git_shas, "whys": whys}


def _steps_on_disk_5(root, size) -> set:
    d = b5.units_root_5(root) / size
    if not d.exists():
        return set()
    return {int(p.name[4:]) for p in d.iterdir()
            if p.is_dir() and p.name.startswith("step") and p.name[4:].isdigit()}


def expected_steps_5(units_by_size: dict, manifest: dict, size: str) -> set:
    """Gate 4's "nothing else loaded" set for `size`, RE-DERIVED — never
    read from any search log's own attested field, so a stray or
    tampered `pairs` entry cannot manufacture legitimacy for an orphan
    unit. `{final}` always; `{S11_STEP_5}` when `size` is a small side
    (whether or not an S11 unit was actually ever written for it — the
    smallest size never gets swept as a large size, so it is always a
    strict subset regardless); for a LARGE size, additionally its own
    spine plus, for every LEGITIMATE (strictly smaller) partner with a
    known final loss, `search_5.replay_5`'s own `requested_steps_5`
    over `size`'s committed losses (the spine is already implied by
    every partner's replay, since `plan_5` always asks for the whole
    spine before any bisection — included explicitly here too, for a
    large size with no computable partner)."""
    expected = {b5.FINAL_STEP_5}
    if size in b5.SMALL_SIDES_5:
        expected.add(b5.S11_STEP_5)
    if size in b5.LARGE_SIDES_5:
        spine = b5.spine_5(manifest, size)
        expected |= set(spine)
        available = list(b5.available_5(manifest, size))
        large_losses = (units_by_size.get(size) or {}).get("losses") or {}
        for small in [s for s in b5.SIZES_5 if b5.SIZES_5.index(s) < b5.SIZES_5.index(size)]:
            small_units = units_by_size.get(small)
            if small_units is None:
                continue
            target = (small_units.get("losses") or {}).get(b5.FINAL_STEP_5)
            if target is None:
                continue
            rep = se5.replay_5(large_losses, available, spine, target)
            expected |= set(se5.requested_steps_5(rep))
    return expected


def _rebuilt_loss_table_5(units_by_size: dict) -> dict:
    table = {}
    for size, u in units_by_size.items():
        entries = {}
        for step in sorted(u["steps"]):
            rec = u["loss_records"][step]
            entries[str(step)] = {"loss": rec["loss"],
                                  "per_set": {k: v["loss"] for k, v in rec.get("per_set", {}).items()}}
        table[size] = entries
    return table


# ---------------------------------------------------------------- gate 4

def replay_pairs_5(units_by_size: dict, manifest: dict, search_log: dict) -> tuple:
    """ONE size's search log (`search_log["size"]` names it; its
    `"pairs"` dict carries one entry per small partner — the plural
    parameter name follows the log's own shape). For every DONE pair,
    `search_5.replay_5` is re-run over the size's own committed losses
    (never the log's in-memory trace) and checked against the logged
    `requested_all`/`plan`/`status`; a DROPPED pair is checked for
    status and target agreement only (nothing else was loaded for it).
    Returns `(pairs_data, failures)`; `pairs_data` holds only the KEPT
    (done) pairs, each `{"small","large","plan","f","counts"}` ready
    for `stats_5.cells_5`. Any `search_log["pairs"]` key that is not a
    legitimate (smaller) partner of `size` is refused outright — a
    stray pair entry naming an already-complete unit could otherwise
    hide an orphan from gate 4's `units_unnamed` check if that check
    trusted the log's own key set. Total over a malformed log entry
    (each problem is appended to `failures`, never raised)."""
    failures = []
    size = search_log.get("size")
    large_units = units_by_size.get(size)
    if large_units is None:
        return [], [f"gate 4 {size}: no unit data for the large size"]
    spine_expected = list(b5.spine_5(manifest, size))
    spine_logged = list(search_log.get("spine") or [])
    if spine_logged != spine_expected:
        failures.append(f"gate 4 {size}: search log spine {spine_logged} != {spine_expected}")
    available = list(b5.available_5(manifest, size))
    losses = large_units["losses"]
    pairs_data = []
    small_sides = [s for s in b5.SIZES_5 if b5.SIZES_5.index(s) < b5.SIZES_5.index(size)]
    log_pairs = search_log.get("pairs") or {}
    stray = sorted(set(log_pairs) - set(small_sides))
    if stray:
        failures += [f"gate 4 {size}: the search log names {s!r} as a pair, which is not a "
                    f"legitimate partner of {size}" for s in stray]
    for small in small_sides:
        plog = log_pairs.get(small)
        if plog is None:
            failures.append(f"gate 4 {size}/{small}: pair missing from the search log")
            continue
        small_units = units_by_size.get(small)
        if small_units is None:
            failures.append(f"gate 4 {size}/{small}: no unit data for the small size")
            continue
        target = small_units["losses"].get(b5.FINAL_STEP_5)
        if target is None:
            failures.append(f"gate 4 {size}/{small}: no final loss for the small size")
            continue
        logged_target = plog.get("target")
        if logged_target is None or abs(float(logged_target) - float(target)) > 1e-9:
            failures.append(f"gate 4 {size}/{small}: logged target {logged_target!r} != "
                            f"the committed small final {target!r}")
        rep = se5.replay_5(losses, available, spine_expected, target)
        rep_steps = se5.requested_steps_5(rep)
        if rep["status"] == "incomplete":
            failures.append(f"gate 4 {size}/{small}: the replay over the committed table is "
                            f"INCOMPLETE (missing step{rep.get('missing')}) — the size's units do "
                            f"not cover its own logged pair")
            continue
        logged_all = plog.get("requested_all")
        if logged_all is None:
            failures.append(f"gate 4 {size}/{small}: requested_all missing — the pair was never "
                            f"closed")
            continue
        logged_steps = [r["step"] for r in logged_all]
        if logged_steps != rep_steps:
            failures.append(f"gate 4 {size}/{small}: requested_all steps {logged_steps} != the "
                            f"replay's {rep_steps}")
        if plog.get("status") != rep["status"]:
            failures.append(f"gate 4 {size}/{small}: status {plog.get('status')!r} != the replay's "
                            f"{rep['status']!r}")
            continue
        if rep["status"] == "dropped":
            continue
        # done
        plan = rep["plan"]
        logged_plan = plog.get("plan") or {}
        if logged_plan.get("bisected") != plan["bisected"]:
            failures.append(f"gate 4 {size}/{small}: bisected order {logged_plan.get('bisected')} "
                            f"!= the replay's {plan['bisected']}")
        if logged_plan.get("bracket") != plan["bracket"]:
            failures.append(f"gate 4 {size}/{small}: bracket {logged_plan.get('bracket')} != the "
                            f"replay's {plan['bracket']}")
        if logged_plan.get("b_minus") != plan["b_minus"] or logged_plan.get("b_plus") != plan["b_plus"]:
            failures.append(f"gate 4 {size}/{small}: window "
                            f"{logged_plan.get('b_minus')}/{logged_plan.get('b_plus')} != the "
                            f"replay's {plan['b_minus']}/{plan['b_plus']}")
        lo, hi = plan["bracket"]
        try:
            i_lo, i_hi = available.index(lo), available.index(hi)
        except ValueError:
            failures.append(f"gate 4 {size}/{small}: bracket {plan['bracket']} not on the "
                            f"available list")
            continue
        if i_hi != i_lo + 1:
            failures.append(f"gate 4 {size}/{small}: bracket {plan['bracket']} not adjacent on "
                            f"the available list")
        window_steps = plan["b_minus"] + [lo, hi] + plan["b_plus"]
        missing = [s for s in window_steps if s not in large_units["counts"]]
        if missing:
            failures.append(f"gate 4 {size}/{small}: window step(s) {missing} are not complete "
                            f"units")
            continue
        f_counts = small_units["counts"].get(b5.FINAL_STEP_5)
        if f_counts is None:
            failures.append(f"gate 4 {size}/{small}: the small final's counts are missing")
            continue
        pairs_data.append({"small": small, "large": size, "plan": plan, "f": f_counts,
                           "counts": large_units["counts"]})
    return pairs_data, failures


# -------------------------------------------------------------- power/projection

def power_failures_5(root, rec: dict, finals_counts: dict, floors: dict, *,
                     power_gate="full") -> list:
    """The WHOLE of gate 5 (design §3.7.5) — every check `run()`'s "5
    power record" site needs, so the named gate function IS the gate:
    the record's provenance pins (prereg tag; `n_sim`/`seed` equal to
    `power_5.N_SIM_5`/`SEED_5` — a record written at a DIFFERENT
    n_sim/seed reproduces itself under `pw.compute`, so provenance
    must be MEASURED against the module's own committed constants,
    never merely self-consistent), `finals_sha256` against the
    committed finals, the declaration literal, and — unless
    `power_gate == "skip"` (test-only) — `power_5.compute` re-run at
    `finals_counts`/`floors` (this function's own arguments) with the
    record's `n_sim`/`seed` and compared byte-for-byte
    (`json.dumps(..., sort_keys=True)`) against the committed record."""
    bad = []
    if rec.get("prereg_tag") != b5.PREREG_TAG_5:
        bad.append(f"power record: prereg_tag {rec.get('prereg_tag')!r} != {b5.PREREG_TAG_5!r}")
    if rec.get("n_sim") != pw.N_SIM_5:
        bad.append(f"power record: n_sim {rec.get('n_sim')!r} != power_5.N_SIM_5 "
                   f"{pw.N_SIM_5!r} — provenance is measured, not attested")
    if rec.get("seed") != pw.SEED_5:
        bad.append(f"power record: seed {rec.get('seed')!r} != power_5.SEED_5 {pw.SEED_5!r} — "
                   f"provenance is measured, not attested")
    want_sha = pw.finals_sha256_5(root)
    if rec.get("finals_sha256") != want_sha:
        bad.append(f"power record: finals_sha256 {rec.get('finals_sha256')!r} != {want_sha!r}")
    if rec.get("declaration") not in ("POWERED", "DECLARED UNDERPOWERED IN ADVANCE"):
        bad.append(f"power record: declaration {rec.get('declaration')!r} is not one of the two "
                   f"literals")
    if power_gate == "full" and (finals_counts is None or floors is None):
        # Task 6 fix (flagged Task 5 minor): power_gate == "full" is the
        # caller's request that this gate be the WHOLE of gate 5 — a
        # missing finals_counts/floors must REFUSE, not silently skip
        # the reproduction the caller asked for.
        bad.append("power record: cannot reproduce — finals_counts or floors missing "
                   "(power_gate='full')")
    elif power_gate != "skip" and finals_counts is not None and floors is not None and \
            "n_sim" in rec and "seed" in rec:
        recomputed = pw.compute(finals_counts, floors, n_sim=rec["n_sim"], seed=rec["seed"])
        recomputed["finals_sha256"] = want_sha
        if json.dumps(recomputed, sort_keys=True) != json.dumps(rec, sort_keys=True):
            bad.append("power record: the recomputed record differs byte-for-byte from the "
                      "committed one")
    return bad


def projection_failures_5(units_by_size: dict, *, projection_commit, is_ancestor,
                          seal_tag_commit, edits=()) -> list:
    bad = list(edits)          # freeze F-5: `battery_5.projection_edits_5`'s lines
    if not projection_commit:
        bad.append("projection: no projection commit found "
                   "(experiments/exp5/projection.md was never added)")
        return bad
    if not seal_tag_commit:
        bad.append("projection: no targets-seal tag commit to check ancestry against")
        return bad
    if not is_ancestor(seal_tag_commit, projection_commit):
        bad.append(f"projection: the targets seal ({seal_tag_commit}) is not an ancestor of the "
                   f"projection commit ({projection_commit}) — the projection must be sealed "
                   f"before any window unit")
    for size, u in units_by_size.items():
        git_shas = u.get("git_shas") or {}
        whys = u.get("whys") or {}
        for step, sha in git_shas.items():
            if int(step) == b5.FINAL_STEP_5:
                continue
            if not is_ancestor(projection_commit, sha):
                bad.append(f"projection: {size}/step{step} (why {whys.get(step)!r}) was built at "
                           f"{sha}, which is not a descendant of the projection commit "
                           f"({projection_commit})")
    return bad


def _seal_tag_commit_5():
    out = subprocess.run(["git", "rev-list", "-n", "1", b5.TARGETS_SEAL_TAG_5], cwd=b5.REPO,
                         capture_output=True, text=True)
    sha = out.stdout.strip()
    return sha or None


# -------------------------------------------------------------- licence

def licence_block_5(world: str, modifier, power: dict) -> dict:
    power = power or {}
    if world == "MATCHED":
        key = "MATCHED-POWERED" if power.get("declaration") == "POWERED" else "MATCHED-UNDERPOWERED"
    elif world == "NOT-MATCHED":
        key = f"NOT-MATCHED-{modifier}" if modifier in ("LARGE-AHEAD", "SMALL-AHEAD", "MIXED", "THIN") \
            else "NOT-MATCHED-MIXED"
    else:
        key = world
    sentence = _LICENCE_BODY_5.get(key, _LICENCE_BODY_5["INSUFFICIENT_DATA"])
    return {"world": world, "modifier": modifier, "key": key, "sentence": sentence,
            "caveat": CAVEAT_5, "declaration": power.get("declaration"),
            "min_detectable_T": power.get("min_detectable_T")}


# ----------------------------------------------------------- secondaries

def _s2_overlay_5(units_by_size: dict) -> dict:
    return {size: [[step, u["losses"][step], u["counts"][step]] for step in sorted(u["steps"])
                  if step in u["losses"] and step in u["counts"]]
            for size, u in units_by_size.items()}


def _s3_composition_5(pairs_data: list, units_by_size: dict) -> dict:
    out = {}
    for pd in pairs_data:
        small, large = pd["small"], pd["large"]
        lo, hi = pd["plan"]["bracket"]
        small_rec = units_by_size[small]["loss_records"].get(b5.FINAL_STEP_5, {})
        lo_rec = units_by_size[large]["loss_records"].get(lo, {})
        hi_rec = units_by_size[large]["loss_records"].get(hi, {})
        small_ps = small_rec.get("per_set", {})
        gaps = {}
        for name, v in small_ps.items():
            lo_l = (lo_rec.get("per_set", {}).get(name) or {}).get("loss")
            hi_l = (hi_rec.get("per_set", {}).get(name) or {}).get("loss")
            if lo_l is None or hi_l is None or v.get("loss") is None:
                continue
            gaps[name] = float((lo_l + hi_l) / 2.0 - v["loss"])
        mean_abs = float(np.mean([abs(g) for g in gaps.values()])) if gaps else None
        largest = sorted(gaps.items(), key=lambda kv: -abs(kv[1]))[:3]
        out[f"{small}→{large}"] = {"mean_abs_gap": mean_abs,
                                        "largest": [{"set": k, "gap": v} for k, v in largest]}
    return out


def _s6_exposure_5(pairs_data: list, cells: list) -> dict:
    rows = {}
    xs, ys = [], []
    live = ss.analysed_5(cells)
    by_pair = {}
    for c in live:
        by_pair.setdefault((c["small"], c["large"]), []).append(c["c"])
    for pd in pairs_data:
        small, large = pd["small"], pd["large"]
        lo, hi = pd["plan"]["bracket"]
        tokens_lo = b5.tokens_seen_5(lo)
        exposure_ratio = tokens_lo / 300e9
        lr_ratio = b5.lr_at_5(large, lo) / b5.lr_at_5(small, b5.FINAL_STEP_5)
        rows[f"{small}→{large}"] = {"tokens_seen_lo": tokens_lo,
                                        "exposure_ratio": exposure_ratio, "lr_ratio": lr_ratio}
        cs = by_pair.get((small, large))
        if cs and exposure_ratio > 0:
            xs.append(math.log(exposure_ratio))
            ys.append(float(np.mean(cs)))
    rho = None
    if len(set(xs)) > 1 and len(set(ys)) > 1 and len(xs) > 2:
        r = spearmanr(xs, ys).statistic
        rho = float(r) if not math.isnan(r) else None
    return {"per_pair": rows, "spearman_c_vs_log_exposure": rho}


def _interp_loss_5(step, steps, losses):
    """Linear interpolation of the loss at `step` onto this experiment's
    own axis, in LOG-step between the two bracketing committed points;
    flat extrapolation at the ends. Descriptive (S8) — the
    interpolation is disclosed, never gating."""
    if not steps:
        return None
    if step in steps:
        return losses[steps.index(step)]
    i = _bisect.bisect_left(steps, step)
    if i == 0:
        return losses[0]
    if i >= len(steps):
        return losses[-1]
    s0, s1, l0, l1 = steps[i - 1], steps[i], losses[i - 1], losses[i]
    x0, x1, x = math.log(max(s0, 1)), math.log(max(s1, 1)), math.log(max(step, 1))
    if x1 == x0:
        return l0
    return l0 + (l1 - l0) * (x - x0) / (x1 - x0)


def _s8_grid_points_5(size, grid_steps, steps_avail, losses_avail):
    avail_set = set(steps_avail)
    pts = []
    for step in grid_steps:
        counts = {}
        for r in b5.RUNGS:
            p = b5.interior_record_path_5(size, step, r)
            if not p.is_file():
                counts = None
                break
            rec = json.loads(p.read_text())
            counts[r] = int(rec.get("correct", 0))
        if counts is None:
            continue
        pts.append({"step": step, "loss": _interp_loss_5(step, steps_avail, losses_avail),
                   "counts": counts, "interpolated": step not in avail_set})
    return pts


def _s8_known_trajectories_5(units_by_size: dict) -> dict:
    """2g's FULL committed 2.8b grid (`battery_2g.trained_steps("2.8b")`,
    21 points — `GRID["2.8b"]` already excludes 0 and the stale-copy
    step64000, so nothing further is excluded here) and 2h's full 6.9b
    grid (`battery_2h.trained_steps_69()`, 22 points), each record read
    directly via `battery_5.interior_record_path_5` (the same accessor
    gate 1(c) uses, unrestricted to its interior-steps subset), placed
    on THIS experiment's own loss axis: measured at every step that
    coincides with a unit this run actually loaded, log-step
    interpolated between them elsewhere (flat extrapolation past the
    ends — `interp_loss_5`), each point's `"interpolated"` flag saying
    which. Design choice, disclosed: read directly from 2g's/2h's own
    committed sweep trees rather than through `battery_4.load_outcome_4`
    (exp4's frozen accessor) — pulling from `experiments/exp4` would add
    an import outside 2g/2h/exp5's existing surface for no benefit,
    since `interior_record_path_5` already exists and is exp5's own
    established, sha-independent path to the same committed bytes."""
    out = {}
    grids = {"2.8b": bg.trained_steps("2.8b"), "6.9b": bh.trained_steps_69()}
    for size, grid_steps in grids.items():
        u = units_by_size.get(size)
        if u is None:
            continue
        steps_avail = sorted(u["steps"])
        losses_avail = [u["losses"][s] for s in steps_avail]
        pts = _s8_grid_points_5(size, grid_steps, steps_avail, losses_avail)
        out[size] = {"points": pts, "n_grid": len(grid_steps), "n_read": len(pts),
                    "disclosure": (f"{size}: {len(pts)} of {len(grid_steps)} committed grid "
                                   f"points read; loss is MEASURED at points coinciding with a "
                                   f"unit this experiment loaded ('interpolated': false) and "
                                   f"LOG-STEP INTERPOLATED between this experiment's own loaded "
                                   f"points elsewhere ('interpolated': true), flat past the ends")}
    return out


def _s9_cross_host_5(root) -> dict:
    """The Mac re-run's counts and loss for each `results/s9/<size>/
    step<k>/` unit against the box's own committed unit for the SAME
    (size, step) under `results/units/...` — `battery_5.tolerance_
    failures_5` (gate 1's own tolerance) plus the loss difference,
    per unit; `"not run"` when `results/s9/` doesn't exist. Non-gating:
    nothing here reaches `run()`'s own `failures`."""
    s9_root = Path(root) / "results" / "s9"
    if not s9_root.exists():
        return {"status": "not run"}
    units = []
    for size_dir in sorted(p for p in s9_root.iterdir() if p.is_dir()):
        size = size_dir.name
        step_dirs = sorted((p for p in size_dir.iterdir() if p.is_dir() and p.name.startswith("step")),
                           key=lambda p: int(p.name[4:]))
        for step_dir in step_dirs:
            step = int(step_dir.name[4:])
            mac_counts = {}
            for r in b5.RUNGS:
                p = step_dir / f"{r}.json"
                if p.is_file():
                    mac_counts[r] = int(json.loads(p.read_text()).get("correct"))
            mac_loss_p = step_dir / "_loss.json"
            mac_loss = json.loads(mac_loss_p.read_text()).get("loss") if mac_loss_p.is_file() else None
            box_counts = {}
            for r in b5.RUNGS:
                p = b5.rung_record_path_5(root, size, step, r)
                if p.is_file():
                    box_counts[r] = int(json.loads(p.read_text()).get("correct"))
            box_loss_p = b5.loss_record_path_5(root, size, step)
            box_loss = json.loads(box_loss_p.read_text()).get("loss") if box_loss_p.is_file() else None
            tol = (b5.tolerance_failures_5(mac_counts, box_counts, label=f"S9 {size}/step{step}")
                  if mac_counts and box_counts else None)
            loss_diff = (abs(mac_loss - box_loss) if mac_loss is not None and box_loss is not None
                        else None)
            units.append({"size": size, "step": step, "mac_counts": mac_counts,
                         "box_counts": box_counts, "mac_loss": mac_loss, "box_loss": box_loss,
                         "loss_diff": loss_diff, "tolerance_failures": tol})
    return {"status": "present", "units": units}


def _re_crossings_5(units_by_size: dict, manifest, size: str) -> dict:
    """Every spine interval `(t_i, t_{i+1})` with `loss(t_i) >= target >
    loss(t_{i+1})`, per legitimate (smaller) partner of `size` — the
    FIRST such interval is the one `plan_5` actually bisects; any
    interval beyond it is a RE-crossing (loss is not assumed
    monotone; §3.2's "a later re-crossing is texture, printed, never
    used"). Total: a missing spine/loss value is skipped, never
    raised."""
    u = units_by_size.get(size)
    if u is None or manifest is None:
        return {}
    spine = list(b5.spine_5(manifest, size))
    losses = u.get("losses") or {}
    spine_losses = [losses.get(s) for s in spine]
    out = {}
    for small in [s for s in b5.SIZES_5 if b5.SIZES_5.index(s) < b5.SIZES_5.index(size)]:
        small_units = units_by_size.get(small)
        if small_units is None:
            continue
        target = (small_units.get("losses") or {}).get(b5.FINAL_STEP_5)
        if target is None:
            continue
        intervals = []
        for i in range(len(spine) - 1):
            a, b_ = spine_losses[i], spine_losses[i + 1]
            if a is None or b_ is None:
                continue
            if a >= target > b_:
                intervals.append([spine[i], spine[i + 1]])
        out[small] = {"n_crossings": len(intervals), "intervals": intervals,
                     "re_crossings": intervals[1:]}
    return out


def _b6_12b_5(units_by_size: dict) -> list:
    """B-6: for every `GATE1_DESCRIPTIVE_12B_5` step present as a 12b
    unit, `tolerance_failures_5` against `mac_interior_counts_5` (2g's
    replication grid — B-6 ruling 2026-09-22: 11 `PREDICTOR_RUNGS`
    only, never all 34), compared over the INTERSECTION of the unit's
    rungs (34, every real collected unit) and the referent's rungs
    (11) — `n_rungs_compared` printed alongside max/sum |Δ| and the
    scaled `GATE1_TOL_SUM_5` bound the 11-rung comparison reads
    against. Non-gating throughout: into S10 only, never `run()`'s own
    `failures`."""
    u = units_by_size.get("12b")
    if u is None:
        return []
    rows = []
    for step in b5.GATE1_DESCRIPTIVE_12B_5:
        if step not in u["steps"]:
            continue
        ref = b5.mac_interior_counts_5("12b", step)
        if ref is None:
            continue
        counts = u["counts"].get(step) or {}
        rungs = tuple(sorted(set(counts) & set(ref)))
        bad = b5.tolerance_failures_5(counts, ref, label=f"S10 B-6 12b/step{step}", rungs=rungs)
        diffs = [abs(int(counts[r]) - int(ref[r])) for r in rungs]
        scaled_sum_bound = (b5.GATE1_TOL_SUM_5 * len(rungs) / len(b5.RUNGS)) if rungs else 0.0
        rows.append({"step": step, "failures": bad, "n_rungs_compared": len(rungs),
                    "sum_abs_diff": sum(diffs), "max_abs_diff": max(diffs) if diffs else 0,
                    "gate1_tol_per_rung": b5.GATE1_TOL_PER_RUNG_5,
                    "gate1_tol_sum_scaled": scaled_sum_bound})
    return rows


def _s10_texture_5(units_by_size: dict, pairs_data: list, root, manifest=None) -> dict:
    mono = {}
    for size, u in units_by_size.items():
        steps = sorted(u["steps"])
        losses = [u["losses"][s] for s in steps if s in u["losses"]]
        n_non_decreasing = sum(1 for i in range(1, len(losses)) if losses[i] >= losses[i - 1])
        mono[size] = {"n_points": len(steps), "n_non_decreasing_steps": n_non_decreasing}
    widths = [{"small": pd["small"], "large": pd["large"],
              "width_steps": pd["plan"]["bracket"][1] - pd["plan"]["bracket"][0]}
             for pd in pairs_data]
    pf = Path(root) / "results" / "preflight_5.json"
    preflight = json.loads(pf.read_text()) if pf.is_file() else None
    twelve_b = None
    if "12b" in units_by_size:
        steps12 = set(units_by_size["12b"]["steps"])
        twelve_b = {"coincide": sorted(steps12 & set(b5.GATE1_DESCRIPTIVE_12B_5))}
    re_crossings = {size: _re_crossings_5(units_by_size, manifest, size)
                    for size in units_by_size if size in b5.LARGE_SIDES_5}
    return {"loss_monotonicity": mono, "bracket_widths": widths, "preflight": preflight,
            "12b_descriptive_coincidence": twelve_b, "re_crossings": re_crossings,
            "b6_12b": _b6_12b_5(units_by_size)}


def _s11_stability_5(units_by_size: dict, cells: list) -> dict:
    out = {}
    for size in b5.SMALL_SIDES_5:
        u = units_by_size.get(size)
        if u is None or b5.S11_STEP_5 not in u.get("counts", {}):
            continue
        s11c = u["counts"][b5.S11_STEP_5]
        fin = u["counts"].get(b5.FINAL_STEP_5, {})
        rows = {}
        for r in b5.RUNGS:
            a, bb = s11c.get(r), fin.get(r)
            rows[r] = {"s11": a, "final": bb, "diff": (a - bb) if a is not None and bb is not None else None}
        out[size] = rows
    p_vals = [c["P"] for c in ss.analysed_5(cells) if c["P"] is not None]
    p_dist = {"n": len(p_vals), "mean": float(np.mean(p_vals)) if p_vals else None,
             "sd": float(np.std(p_vals)) if p_vals else None}
    return {"per_small_side": out, "P_distribution": p_dist}


def secondaries_5(cells, units_by_size, pairs_data, root, manifest=None) -> tuple:
    """S1-S11, each its own `collect_total_5` site: a refusal inside one
    secondary degrades that secondary alone (`secondaries[key] = None`)
    and is recorded in the returned `secondary_failures` dict, never in
    `run()`'s own `failures`."""
    cells = cells or []
    units_by_size = units_by_size or {}
    pairs_data = pairs_data or []
    secondaries, secondary_failures = {}, {}

    def _do(key, fn):
        val, f = collect_total_5(fn, f"5 {key}")
        secondaries[key] = val
        if f:
            secondary_failures[key] = f

    _do("S1", lambda: ss.ledger_5(cells))
    _do("S2", lambda: _s2_overlay_5(units_by_size))
    _do("S3", lambda: _s3_composition_5(pairs_data, units_by_size))
    _do("S4", lambda: ss.s4_size_ratio_5(cells, {s: u["n_params"] for s, u in units_by_size.items()}))
    _do("S5", lambda: ss.s5_by_type_5(cells))
    _do("S6", lambda: _s6_exposure_5(pairs_data, cells))
    _do("S7", lambda: ss.s7_by_pair_5(cells))
    _do("S8", lambda: _s8_known_trajectories_5(units_by_size))
    _do("S9", lambda: _s9_cross_host_5(root))
    _do("S10", lambda: _s10_texture_5(units_by_size, pairs_data, root, manifest))
    _do("S11", lambda: _s11_stability_5(units_by_size, cells))
    return secondaries, secondary_failures


# -------------------------------------------------------------- verdict

def verdict_5(*, failures, tree, primary, modifier, gate4, secondaries, secondary_failures,
             licence, power, signed_offset, pins_active, git_sha, gate1=None) -> dict:
    """`git_sha` (and any future timestamp) lives under `"meta"` —
    Task 6's determinism fixture drops that one key wholesale rather
    than enumerating volatile fields one at a time (the brief's own
    words: "put those under one `meta` key... if they are not
    already")."""
    return {"verdict": tree["verdict"], "tree": tree, "primary": primary, "modifier": modifier,
            "gate4": gate4, "gate1": gate1, "secondaries": secondaries, "failures": list(failures),
            "secondary_failures": secondary_failures, "pins_active": pins_active,
            "licence": licence, "power": power, "signed_offset": signed_offset,
            "meta": {"git_sha": git_sha}}


def _json_safe_5(o):
    if isinstance(o, float):
        return o if np.isfinite(o) else None
    if isinstance(o, np.floating):
        return float(o) if np.isfinite(o) else None
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, np.ndarray):
        return [_json_safe_5(x) for x in o.tolist()]
    if isinstance(o, dict):
        return {str(k): _json_safe_5(x) for k, x in o.items()}
    if isinstance(o, (list, tuple)):
        return [_json_safe_5(x) for x in o]
    return o


def write_verdict_txt_5(v: dict) -> str:
    lines = [f"EXPERIMENT 5 VERDICT: {v['tree']['verdict']}"
            + (f" · {v['tree']['modifier']}" if v['tree'].get('modifier') else ""),
            f"reason: {v['tree'].get('reason', '')}", "", f"caveat: {v['licence'].get('caveat', '')}",
            "", f"licence: {v['licence'].get('sentence', '')}", ""]
    p = v.get("primary") or {}
    rb = p.get("rung_block") or {}
    lines.append(f"primary: T={p.get('T')} n_cells={p.get('n_cells')} n_rungs={p.get('n_rungs')} "
                f"rung-block p={rb.get('p')} method={rb.get('method')} "
                f"n_blocks={rb.get('n_blocks')} resolution={rb.get('resolution')}")
    fb = p.get("family_block") or {}
    cl = p.get("cell_level") or {}
    lines.append(f"  family-block p={fb.get('p')}  cell-level p={cl.get('p')}")
    m = v.get("modifier") or {}
    lines.append(f"modifier: {m.get('modifier')} n={m.get('n')} n_pos={m.get('n_pos')} "
                f"n_neg={m.get('n_neg')} p={m.get('p_two_sided')}")
    so = v.get("signed_offset") or {}
    lines.append(f"signed mean offset: {so.get('mean')} CI95 {so.get('ci95')}")
    pw_rec = v.get("power") or {}
    lines.append(f"power: {pw_rec.get('declaration')}  min_detectable_T={pw_rec.get('min_detectable_T')}"
                f"  n_live_simulated={pw_rec.get('n_live_simulated')}"
                f"  n_live_realized={p.get('n_cells')}")
    lines.append("")
    sec = v.get("secondaries") or {}
    lines.append("S7 (by pair): " + json.dumps(sec.get("S7")))
    lines.append("S5 (by type): " + json.dumps(sec.get("S5")))
    lines.append("")
    lines.append("Performability ledger (S1):")
    s1 = sec.get("S1") or {}
    lines.append(f"  classes: {s1.get('classes')}  unstable_fraction={s1.get('unstable_fraction')}")
    for row in (s1.get("named") or []):
        lines.append(f"  {row.get('class')}: {row.get('small')}→{row.get('large')}/"
                    f"{row.get('rung')} f={row.get('f')} lo={row.get('lo')} hi={row.get('hi')} "
                    f"bracket={row.get('bracket')} residual_lo={row.get('residual_lo')} "
                    f"residual_hi={row.get('residual_hi')} "
                    f"b_minus_clears_both={row.get('b_minus_clears_both')}")
    lines.append("")
    g4 = v.get("gate4") or {}
    lines.append(f"gate 4: pairs_kept={g4.get('pairs_kept')} pairs_dropped={g4.get('pairs_dropped')} "
                f"units_unnamed={g4.get('units_unnamed')}")
    for d in (g4.get("dropped_detail") or []):
        lines.append(f"  dropped: {d.get('small')}→{d.get('large')} target={d.get('target')} "
                    f"reason={d.get('reason')} spine_losses={d.get('spine_losses')}")
    lines.append("")
    g1 = v.get("gate1") or {}
    g1a = g1.get("a") or {}
    lines.append(f"gate 1(a): pass={g1a.get('pass')} digests_equal={g1a.get('digests_equal')} "
                f"loss_equal={g1a.get('loss_equal')} "
                f"continuation_diffs_sum={sum((g1a.get('continuation_diffs') or {}).values()) if g1a.get('continuation_diffs') else None}")
    g1b = g1.get("b") or {}
    per_size_b = g1b.get("per_size") or {}
    lines.append(f"gate 1(b): pass={g1b.get('pass')} no_referent={g1b.get('no_referent')}")
    for size, row in per_size_b.items():
        if row.get("referent") is not None:
            lines.append(f"  {size}: max|Δ|={row.get('max_abs_diff')} sum|Δ|={row.get('sum_abs_diff')}")
    g1c_all = g1.get("c") or {}
    for size, g1c in g1c_all.items():
        for step, row in (g1c.get("steps") or {}).items():
            if row.get("referent") is not None:
                lines.append(f"gate 1(c) {size}/step{step}: max|Δ|={row.get('max_abs_diff')} "
                            f"sum|Δ|={row.get('sum_abs_diff')}")
    lines.append("")
    lines.append("S6 (exposure): " + json.dumps(sec.get("S6")))
    lines.append("")
    lines.append("S10 (texture): " + json.dumps(sec.get("S10")))
    lines.append("S9 (cross-host drift): " + json.dumps(sec.get("S9")))
    lines.append("S11 (small-side stability): " + json.dumps(sec.get("S11")))
    lines.append("")
    lines.append(f"failures: {v.get('failures')}")
    lines.append(f"secondary_failures: {v.get('secondary_failures')}")
    return "\n".join(lines) + "\n"


# ------------------------------------------------------------------ run

def run(root=None, *, write=False, n_sample=None, n_boot=None, manifest=None, sl=None,
       tag_exists=None, blob_sha=None, blobs_bound=None, projection_commit=None, is_ancestor=None,
       seal_tag_commit=None, referents_sha=_LITERAL, imports_pinned=_LITERAL, frozen_check=None,
       power_gate="full", projection_edits=None) -> dict:
    root = Path(root) if root is not None else EXP5
    n_sample = b5.N_PERM_SAMPLED_5 if n_sample is None else n_sample
    n_boot = b5.N_BOOT_5 if n_boot is None else n_boot
    if referents_sha is _LITERAL:
        referents_sha = REFERENTS_5_SHA256
    if imports_pinned is _LITERAL:
        imports_pinned = True
    sl_injected = sl is not None
    manifest_injected = manifest is not None

    failures = []

    # 1. halt markers
    def _check_halts():
        bad = []
        for size in b5.SIZES_5:
            p = b5.halt_marker_path_5(root, size)
            if p.exists():
                bad.append(f"{size} is halted: {p.read_text().strip()[:200]}")
        if bad:
            raise ValueError(f"halt marker(s): {bad}")
        return True
    _, f = collect_total_5(_check_halts, "5 halt marker")
    failures += f

    # 2. frozen modules
    _, f = collect_total_5(frozen_check or b5.check_frozen_5, "5 frozen modules")
    failures += f

    # 3. import surface (entry)
    if imports_pinned is not False:
        _, f = collect_total_5(b5.check_imports_5, "5 import surface (entry)")
        failures += f

    # 4. prereg tag
    prereg, f = collect_total_5(lambda: b5.require_prereg_5(tag_exists=tag_exists, blob_sha=blob_sha),
                                "5 prereg tag")
    failures += f

    # 5. targets seal
    seal, f = collect_total_5(
        lambda: b5.require_targets_seal_5(root, tag_exists=tag_exists, blobs_bound=blobs_bound),
        "5 targets seal")
    failures += f
    if seal is not None:
        failures += [f"5 targets seal: {m}" for m in seal.get("failures", [])]

    # 6. manifest / slice / referents / battery / floors / verify
    manifest, f = collect_total_5(
        lambda: manifest if manifest_injected else b5.load_manifest_5(sha_pin=b5.CHECKPOINTS_SHA256_5),
        "5 manifest")
    failures += f

    def _load_slice():
        if sl_injected:
            return sl
        loaded = sl5.load_slice_5(sha_pin=b5.SLICE_SHA256_5)
        if loaded["meta"]["n_scored"] != b5.SLICE_N_SCORED_5:
            raise ValueError(f"slice n_scored {loaded['meta']['n_scored']} != "
                             f"{b5.SLICE_N_SCORED_5}")
        return loaded
    sl, f = collect_total_5(_load_slice, "5 slice")
    failures += f

    if referents_sha is not False:
        if referents_sha is None:
            failures.append("5 referents: not pinned (build incomplete)")
        else:
            def _check_referents():
                from experiments.exp5 import make_referents_5 as mkr5
                return mkr5.check_referents_5(REFERENTS_PATH_5, sha_pin=referents_sha)
            mf, f = collect_total_5(_check_referents, "5 referents")
            failures += f + (mf or [])

    battery, f = collect_total_5(bt.load_battery, "5 battery")
    failures += f
    floors, f = collect_total_5(b5.load_floors_5, "5 floors")
    failures += f
    verify_fn, f = collect_total_5(a2d.load_verify, "5 verify")
    failures += f

    # 7. host record
    def _load_host():
        p = b5.host_record_path_5(root)
        if not p.is_file():
            raise ValueError("host record missing")
        rec = json.loads(p.read_text())
        bad = b5.host_record_failures_5(rec)
        if bad:
            raise ValueError(f"host record: {bad}")
        return rec
    host, f = collect_total_5(_load_host, "5 host record")
    failures += f

    # 8. finals (gate 3, every size) + gate 1(a)/(b)
    _finals_ready = all(x is not None for x in (manifest, battery, verify_fn, host, sl))

    def _load_all_units():
        if not _finals_ready:
            raise ValueError("manifest, battery, verify criterion, host record or slice missing")
        return {size: load_units_5(root, size, manifest=manifest, battery=battery,
                                   verify_fn=verify_fn, host=host, slice_sha=sl["sha256"],
                                   n_scored=sl["meta"]["n_scored"]) for size in b5.SIZES_5}
    units, f = collect_total_5(_load_all_units, "5 finals")
    failures += f

    if b5.gate1a_path_5(root).is_file():
        def _check_gate1a():
            rec = json.loads(b5.gate1a_path_5(root).read_text())
            bad = gate1a_failures_5(rec)
            if units is not None and "2.8b" in units:
                u28 = units["2.8b"]
                bad += gate1a_unit_failures_5(rec, {
                    "digest": u28["digests"].get(b5.FINAL_STEP_5),
                    "loss": u28["losses"].get(b5.FINAL_STEP_5),
                    "counts": u28["counts"].get(b5.FINAL_STEP_5)})
            if bad:
                raise ValueError(f"gate 1(a): {bad}")
            return rec
        gate1a_rec, f = collect_total_5(_check_gate1a, "5 gate 1(a)")
        failures += f
    else:
        gate1a_rec = None
        failures.append("5 gate 1(a): record missing")

    if b5.gate1b_path_5(root).is_file():
        def _check_gate1b():
            rec = json.loads(b5.gate1b_path_5(root).read_text())
            bad = gate1b_failures_5(root, rec)
            if bad:
                raise ValueError(f"gate 1(b): {bad}")
            return rec
        gate1b_rec, f = collect_total_5(_check_gate1b, "5 gate 1(b)")
        failures += f
    else:
        gate1b_rec = None
        failures.append("5 gate 1(b): record missing")

    # 9. loss table
    def _check_loss_table():
        if units is None:
            raise ValueError("units not loaded")
        p = b5.loss_table_path_5(root)
        if not p.is_file():
            raise ValueError("loss_table_5.json missing")
        committed = json.loads(p.read_text())
        rebuilt = _rebuilt_loss_table_5(units)
        if committed != rebuilt:
            raise ValueError("loss_table_5.json does not equal the table rebuilt from the "
                             "committed units")
        return rebuilt
    _, f = collect_total_5(_check_loss_table, "5 loss table")
    failures += f

    # 10. power record — power_failures_5 is the WHOLE of gate 5 (review finding 4)
    def _check_power():
        if floors is None:
            raise ValueError("floors missing")
        finals_counts = pw.load_finals_counts_5(root)
        p = b5.power_path_5(root)
        if not p.is_file():
            raise ValueError("power_5.json missing")
        rec = json.loads(p.read_text())
        bad = power_failures_5(root, rec, finals_counts, floors, power_gate=power_gate)
        if bad:
            raise ValueError(f"power record: {bad}")
        return rec, finals_counts
    power_result, f = collect_total_5(_check_power, "5 power record")
    failures += f
    power_rec, finals_counts = power_result if power_result else (None, None)

    # 11. projection
    resolved_seal_commit = seal_tag_commit if seal_tag_commit is not None else _seal_tag_commit_5()
    resolved_pc = projection_commit if projection_commit is not None else b5.projection_commit_5()
    anc = is_ancestor or b5.is_ancestor_5

    def _check_projection():
        if units is None:
            raise ValueError("units not loaded")
        # Freeze F-5: the projection must be exactly the blob its adding commit
        # added. Measured against the real repository whenever the projection
        # commit is resolved from it; an injected commit (the worlds) injects
        # its edits too (default: none).
        if projection_edits is not None:
            edits = list(projection_edits)
        elif projection_commit is None and resolved_pc:
            edits = b5.projection_edits_5(resolved_pc)
        else:
            edits = []
        bad = projection_failures_5(units, projection_commit=resolved_pc, is_ancestor=anc,
                                    seal_tag_commit=resolved_seal_commit, edits=edits)
        if bad:
            raise ValueError(f"projection: {bad}")
        return True
    _, f = collect_total_5(_check_projection, "5 projection")
    failures += f

    # 12/13. spine/gate 1(c)/search log for every LARGE size; gate 4's
    # "nothing else loaded" check for EVERY size (the smallest size is
    # never swept as large, so it never gets a search log, but a unit
    # can still be orphaned under it — Task 5 review finding 1).
    gate4_total = {"pairs_kept": 0, "pairs_dropped": 0, "units_unnamed": [], "dropped_detail": []}
    gate1c_recs = {}
    all_pairs_data = []
    for size in b5.SIZES_5:
        is_large = size in b5.LARGE_SIDES_5
        log = None

        if is_large:
            def _check_spine(size=size):
                if units is None or manifest is None:
                    raise ValueError("units or manifest missing")
                spine = b5.spine_5(manifest, size)
                u = units.get(size)
                if u is None:
                    raise ValueError(f"{size}: no unit data")
                missing = [s for s in spine if s not in u["steps"]]
                if missing:
                    raise ValueError(f"{size}: spine step(s) missing from the committed units: "
                                     f"{missing}")
                return spine
            _, f = collect_total_5(_check_spine, f"5 spine {size}")
            failures += f

            if b5.gate1_interior_steps_5(size):
                def _check_gate1c(size=size):
                    p = b5.gate1c_path_5(root, size)
                    if not p.is_file():
                        raise ValueError(f"{size}: gate1c.json missing")
                    rec = json.loads(p.read_text())
                    bad = gate1c_failures_5(root, size, rec)
                    if bad:
                        raise ValueError(f"gate 1(c) {size}: {bad}")
                    return rec
                g1c_rec, f = collect_total_5(_check_gate1c, f"5 gate 1(c) {size}")
                failures += f
                if g1c_rec is not None:
                    gate1c_recs[size] = g1c_rec

            def _load_search_log(size=size):
                p = b5.search_log_path_5(root, size)
                if not p.is_file():
                    raise ValueError(f"{size}: search_log.json missing")
                log = json.loads(p.read_text())
                if manifest is not None:
                    expected_spine = list(b5.spine_5(manifest, size))
                    if list(log.get("spine") or []) != expected_spine:
                        raise ValueError(f"{size}: search log spine {log.get('spine')} != "
                                         f"{expected_spine}")
                if units is not None and size in units:
                    usteps = set(units[size]["steps"])
                    for r in log.get("requests", []):
                        if r["step"] not in usteps:
                            raise ValueError(f"{size}: logged request step{r['step']} is not a "
                                             f"complete unit")
                    for small, plog in (log.get("pairs") or {}).items():
                        for r in plog.get("requests", []):
                            if r["step"] not in usteps:
                                raise ValueError(f"{size}/{small}: logged request "
                                                 f"step{r['step']} is not a complete unit")
                if not log.get("git_sha"):
                    raise ValueError(f"{size}: search log has no git_sha")
                return log
            log, f = collect_total_5(_load_search_log, f"5 search log {size}")
            failures += f

        def _gate4(size=size, log=log, is_large=is_large):
            if units is None or manifest is None:
                raise ValueError("units or manifest missing")
            if is_large:
                if log is None:
                    raise ValueError("search log missing")
                pairs_data, pf = replay_pairs_5(units, manifest, log)
            else:
                pairs_data, pf = [], []
            expected = expected_steps_5(units, manifest, size)
            on_disk = _steps_on_disk_5(root, size)
            unnamed = sorted(on_disk - expected)
            if unnamed:
                pf = pf + [f"gate 4 {size}: step{s} on disk but never requested (nothing else "
                          f"loaded)" for s in unnamed]
            # Freeze F-4: load_units_5 skips a step directory that is not a
            # complete unit; a torn/tampered unit nothing downstream needs
            # (the smallest size's S11 — its search log is never read) then
            # vanished silently. The puller copies complete units only, so
            # on the committed tree every step directory must be one.
            torn = sorted(s for s in on_disk if not b5.unit_complete_5(root, size, s))
            if torn:
                pf = pf + [f"gate 3 {size}: step{s} is on disk but is not a complete unit (torn, "
                          f"or a file's sha differs from its _unit.json)" for s in torn]
            dropped_detail = [{"small": small, "large": size, "target": plog["plan"].get("target"),
                              "reason": plog["plan"].get("reason"),
                              "spine_losses": plog["plan"].get("spine_losses")}
                             for small, plog in ((log or {}).get("pairs") or {}).items()
                             if plog.get("status") == "dropped"]
            return pairs_data, pf, unnamed, dropped_detail
        result, f = collect_total_5(_gate4, f"5 gate 4 {size}")
        failures += f
        if result is not None:
            pairs_data, pf, unnamed, dropped_detail = result
            failures += pf
            all_pairs_data += pairs_data
            gate4_total["pairs_kept"] += len(pairs_data)
            gate4_total["pairs_dropped"] += len(dropped_detail)
            gate4_total["units_unnamed"] += [f"{size}: step{s}" for s in unnamed]
            gate4_total["dropped_detail"] += dropped_detail

    # 14. cells / primary / modifier / signed offset
    def _make_cells():
        if floors is None:
            raise ValueError("floors missing")
        return ss.cells_5(all_pairs_data, floors)
    cells, f = collect_total_5(_make_cells, "5 cells")
    failures += f

    def _make_primary():
        if cells is None:
            raise ValueError("cells missing")
        return ss.primary_5(cells, n_sample=n_sample, seed=b5.PERM_SEED_5)
    primary, f = collect_total_5(_make_primary, "5 primary")
    failures += f

    def _make_modifier():
        if cells is None:
            raise ValueError("cells missing")
        return ss.modifier_5(cells)
    modifier, f = collect_total_5(_make_modifier, "5 modifier")
    failures += f

    def _make_signed_offset():
        if cells is None:
            raise ValueError("cells missing")
        return ss.signed_offset_ci_5(cells, n_boot=n_boot, seed=b5.BOOT_SEED_5)
    signed_offset, f = collect_total_5(_make_signed_offset, "5 signed offset")
    failures += f

    # 15. import surface (exit)
    if imports_pinned is not False:
        _, f = collect_total_5(b5.check_imports_5, "5 import surface (exit)")
        failures += f

    tree = ss.tree_5(failures=failures, primary=primary or {}, modifier=modifier or {})

    # 16. secondaries (never touch `failures`)
    secondaries, secondary_failures = secondaries_5(cells, units, all_pairs_data, root, manifest)

    licence = licence_block_5(tree["verdict"], tree.get("modifier"), power_rec)

    pins_active = {
        "frozen_modules": frozen_check is None,
        "import_surface": bool(imports_pinned),
        "referents_sha": referents_sha,
        "prereg_binding": tag_exists is None and blob_sha is None,
        "seal_binding": blobs_bound is None,
        "power_gate": power_gate,
        "slice_injected": sl_injected,
        "manifest_injected": manifest_injected,
        "projection_edits_measured": projection_edits is None and projection_commit is None,
    }

    git_sha = b5.git_sha_5()

    gate1 = {"a": gate1a_rec, "b": gate1b_rec, "c": gate1c_recs}
    v = verdict_5(failures=failures, tree=tree, primary=primary, modifier=modifier,
                 gate4=gate4_total, secondaries=secondaries, secondary_failures=secondary_failures,
                 licence=licence, power=power_rec, signed_offset=signed_offset,
                 pins_active=pins_active, git_sha=git_sha, gate1=gate1)
    v = _json_safe_5(v)

    if write:
        def _write_verdict():
            out_v = Path(root) / "results" / "verdict.json"
            out_txt = Path(root) / "results" / "VERDICT.txt"
            txt = write_verdict_txt_5(v)
            out_v.parent.mkdir(parents=True, exist_ok=True)
            out_v.write_text(json.dumps(v, indent=1, allow_nan=False))
            out_txt.write_text(txt)
            return True
        _, f = collect_total_5(_write_verdict, "5 verdict write")
        if f:
            v["write_failure"] = f[0]
    return v


if __name__ == "__main__":
    result = run(write="--write" in sys.argv)
    print(json.dumps({"verdict": result["verdict"], "git_sha": result["meta"]["git_sha"]}, indent=1))
