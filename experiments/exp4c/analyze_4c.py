# experiments/exp4c/analyze_4c.py
"""Experiment 4c's analyzer (design `experiment-4c-design.md` §3.3-§3.8,
§5, §6; plan Task 4): the pinned unit loaders, gates 0-7, the pre-clear
rank primary with its exact family-block sign flip, the rung-coupled
placebo and the rule's own measured false-positive rate, the type
modifier, the calibration read, the four-world tree, the named
secondaries S1-S10, the licence block, and `run()` — the whole verdict
path from committed bytes to a written `verdict.json` / `VERDICT.txt`.

No torch import anywhere in this module and no network: every number
is re-derived from committed k-NN set tables (`sets/<rung>.npz`,
git-tracked) and the committed 2h/2l outcome records. Everything under
`experiments/exp2*`, `experiments/exp3*`, `experiments/exp4/` and
`experiments/exp4b/` is FROZEN: imported by name, never edited.

Structure follows `experiments/exp4/analyze_4.py` in order — pins,
loaders, gates, primary, secondaries, verdict, run, main — so the two
read side by side.

Totality (lesson 8): every step of `run()` is a `collect_total_4c`
site. A refusal anywhere on the verdict path is COLLECTED and
delivered as INSUFFICIENT_DATA with its reason verbatim; nothing
raises out of `run()`. A refusal inside a secondary degrades that
secondary alone.

Build-stage constants: `REFERENTS_4C_SHA256` and `IMPORTED_SHA256_4C`
are `None` here — Task 5 writes the referent manifest and the import
pins. Until then `run()` records "not pinned (build incomplete)" as a
failure unless a test injects `referents_sha=False` /
`imports_pinned=False`, and `power_gate="skip"` bypasses the two power
checks that need `power_4c` (the live cell structure's sha and the
byte reproduction); the record's presence, tag, declaration and
`n_sim` are still checked, so the "power record missing" route is a
real refusal route before Task 5."""
from __future__ import annotations

import json
import subprocess
import sys
import zipfile
from pathlib import Path

EXP4C = Path(__file__).resolve().parent
EXPERIMENTS = EXP4C.parent
REPO = EXPERIMENTS.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

# The BLAS thread pool is sized when numpy is first imported and a
# multi-threaded reduction is not bit-reproducible across processes
# (Exp 4's Minor 7): pinned before numpy and before every
# `experiments.*` import that pulls numpy in transitively.
from experiments.exp4 import _threads_4  # noqa: E402

import numpy as np  # noqa: E402

from experiments.exp2d import battery_2d as bt  # noqa: E402
from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp2i import analyze_2i as an2i  # noqa: E402
from experiments.exp4 import analyze_4 as a4  # noqa: E402
from experiments.exp4 import battery_4  # noqa: E402
from experiments.exp4 import collect_4  # noqa: E402
from experiments.exp4 import metric_4  # noqa: E402
from experiments.exp4b import placebo_4b  # noqa: E402
from experiments.exp4c import battery_4c as bc  # noqa: E402
from experiments.exp4c import rank_4c as rk  # noqa: E402

EXP4 = battery_4.EXP4

# ------------------------------------------------------------- constants

ALPHA_4C = rk.ALPHA_4C
MARGINAL_4C = rk.MARGINAL_4C
N_BOOT_4C = rk.N_BOOT_4C
B_PLACEBO_4C = rk.B_PLACEBO_4C
SEED_4C = rk.SEED_4C
WORLDS_4C = rk.WORLDS_4C
MODIFIERS_4C = rk.MODIFIERS_4C
REFUSAL_WORLD_4C = "INSUFFICIENT_DATA"

# S4's continuity arm reuses Exp 4's own eligibility bootstrap size and
# 4b's own placebo pool bootstrap size.
N_BOOT_ELIG_4C = a4.N_BOOT_ELIG_4

# Task 5's referent manifest, pinned to the sha256 `make_referents_4c.
# build` printed for `referents_4c.json` (8,160 files — 4,940 plus the
# 92-unit upstream argmax-outcome finding, `_exp4_argmax_outcome_
# files`, the read sweep's own UNPINNED count before the fix).
REFERENTS_4C_SHA256 = "eb3546582b2a85fa2787880d0273d4b96ddbd54f30c8795128ea7398afef9ff9"
# Task 5's import scan (`tests/import_scan_4c.py`), pinned LAST (§8 of
# the plan) — 4c's own residual: the two package `__init__.py` files
# and the three stage tools no verdict path imports
# (`make_referents_4c.py`, `run/preflight_4c.py`,
# `verify_referents_4c.py`). Fix round 1a: re-cut after `make_
# referents_4c.py`'s post-pin edit (the argmax-outcome-files fix) had
# left the ORIGINAL scan's sha stale in the same commit. Fix round 2:
# re-cut again after `verify_referents_4c.py`'s edits (items 3 and 5 —
# the always-verifying frozen-pin check and the power-record key-set
# assertion); only that one file's sha moved.
IMPORTED_SHA256_4C = {
    REPO / "experiments/exp4c/__init__.py":
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    REPO / "experiments/exp4c/make_referents_4c.py":
        "ea97e4b0ba85acc623d25c9ca05cc56d331b065b5b684059f957d211a68d0652",
    REPO / "experiments/exp4c/run/__init__.py":
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    REPO / "experiments/exp4c/run/preflight_4c.py":
        "31cffdd3bfa49ef595c16cc1f337baf53d72071d43cf766bee7f06fb5104a924",
    REPO / "experiments/exp4c/verify_referents_4c.py":
        "52aced84251923f023fd85a0090d6a2b304b6ea39315c7960db243156aa0eca1",
}
REFERENTS_PATH_4C = EXP4C / "referents_4c.json"

POWER_DECLARATIONS_4C = ("POWERED", "DECLARED UNDERPOWERED IN ADVANCE")


def power_path_4c(root) -> Path:
    """`results/power_4c.json` — the path `run/sweep_4c.py` refuses
    without and the tag binds."""
    return Path(root) / "results" / "power_4c.json"


# ---------------------------------------------------------------- licences

# Design §6's first line, VERBATIM — the bounds that hold in EVERY
# world. Printed on every licence and carried in the verdict.
KNOWN_OUTCOME_CAVEAT_4C = (
    "Bounded in every world to: 2c's battery; two runs, one from each of two families; the "
    "prompt-end position; Exp 4's site family and references; a sealed representation read "
    "against a KNOWN outcome; a statistic, a null and an alternative fixed on four runs the "
    "designer had seen."
)
# Design §2's reading of the same fact, appended as its own sentence.
NOT_A_FORECAST_4C = (
    "whatever fires is a preregistered reading on a known outcome, not a forecast."
)

# Design §6: "The modifier governs the noun."
MODIFIER_NOUN_4C = {
    "TYPE-GENERAL": "tasks",
    "TYPE-BOUND": ("the option and string tasks — nine cells on six tasks — with the "
                   "type-matched arithmetic comparison showing nothing (U_arith)"),
    "NEITHER": ("neither noun: U_arith does not clear its bar and the non-arithmetic stratum "
                "does not sit above one-half, so the sentence must say that the pooled reading "
                "is carried by neither stratum"),
}

_LICENCE_BODY_4C = {
    "REPLICATES": (
        "on two training runs nobody had read, at the last checkpoint before each task first "
        "performed, the task's agreement with three unrelated released models had grown more "
        "than that of the tasks which never perform on the same run (U, its interval, p), a "
        "test whose statistic and null were fixed beforehand on four other runs where the same "
        "reading gave .62. The modifier governs the noun, and this world licenses {noun}. The "
        "scoreboard moves from \"still a citation\" to \"measured on two sealed runs\"."
    ),
    "MARGINAL": (
        "on two training runs nobody had read, the pre-clear growth of the tasks that go on to "
        "perform is ahead of the tasks that never do at p = p+, short of the program's alpha "
        "(U and its interval printed). The scoreboard says \"marginal\"; the lens claim stays a "
        "citation with this beside it. The modifier governs the noun, and this world licenses "
        "{noun}."
    ),
    "NOT-REPLICATED": (
        "on two training runs nobody had read, a sealed rank test did not detect the lead (U, "
        "its interval, p), at a resolution that would have missed an effect of the size seen on "
        "the first four runs two times in three. \"Still a citation\" stands, and this is not "
        "evidence of absence. The modifier's reading, for the record, is {noun}."
    ),
    "INSUFFICIENT_DATA": (
        "no licence: the run did not produce a verdict; the reason is ledgered."
    ),
}

# Design §6, REPLICATES' last clause and §3.6: the rule's own measured
# false-positive rate at the deciding bar.
BOUNDED_SENTENCE_4C = (
    "BOUNDED (design §3.6): the rule's measured false-positive rate at the deciding bar "
    "(alpha_placebo {alpha:.4g} against a bar of {bar:g}) exceeds twice that bar, so the "
    "sentence states it and rests on the placebo p."
)

# Design §3.4/§6: the NOT-REPLICATED sub-cell named in advance.
REVERSED_SENTENCE_4C = (
    "REVERSED: the rising tasks' pre-clear growth sat below the never-performing tasks' "
    "(p- < .05). Nothing about precedence is licensed, and Exp 4's sign-flip reading against "
    "the construction account is re-examined in `experiments.md` rather than left standing "
    "unremarked."
)

_POWER_MISSING_4C = (
    "§4's power statement cannot be quoted: the power record is not available to this run, so "
    "the resolution this NOT-REPLICATED is read at is not on the record."
)

# Design §6, every world: the battery's own limit, stated wherever a
# type is named.
BATTERY_LIMIT_4C = (
    "Battery limit (design §3.2): the flat pool contains no option task and only three string "
    "tasks, so no type-matched comparator pool exists for the nine non-arithmetic cells on "
    "either run."
)

LICENSED_4C = dict(_LICENCE_BODY_4C)


# ------------------------------------------------------------- totality

def collect_total_4c(thunk, label):
    """`analyze_4.collect_total_4`'s body — 2i's widened surface plus
    `zipfile.BadZipFile` (a corrupted npz), `KeyError` (a missing npz
    member) and `OSError` — with `ImportError` added. Returns
    `(value, failures)`; never raises.

    Why `ImportError`: three of this analyzer's inputs live in modules
    written later in the build (`power_4c`, `make_referents_4c`), and a
    module named on the verdict path that cannot be imported is a
    missing INPUT, which lesson 8 says must arrive as INSUFFICIENT_DATA
    naming it rather than as a traceback. The laundering risk 2i's own
    docstring warns about (a logic defect wearing a refusal's clothes)
    is bounded here by `check_imports_4c`, which runs at entry and exit
    and pins every module this process actually executed: an import
    that silently resolved to the wrong file, or a module that went
    missing on the sanctioned run, cannot pass that check."""
    try:
        return an2i.collect_total(thunk, label)
    except (zipfile.BadZipFile, KeyError, OSError, ImportError) as e:
        return None, [f"{label}: {type(e).__name__}: {e}"]


def check_imports_4c() -> None:
    """2j F-1 / lesson 11: the import surface is a verdict input. Every
    module under `experiments/` this process has imported (tests
    excluded) must be covered by one of the pinned tables —
    `battery_4.FROZEN_SHA256_4`, `battery_4c.FROZEN_SHA256_4C`,
    `EXP4_CLOSED_SHA256_4C`, `EXP4B_CLOSED_SHA256_4C`,
    `INSTRUMENT_BLOBS_4C` — or by `IMPORTED_SHA256_4C` (4c's own
    residual), each byte-identical to its pin. `run()` calls this at
    ENTRY and again at EXIT."""
    if IMPORTED_SHA256_4C is None:
        raise RuntimeError("IMPORTED_SHA256_4C is None — the import surface is not pinned "
                           "(build incomplete)")
    covered = {str(Path(p).resolve()) for p in battery_4.FROZEN_SHA256_4}
    covered |= {str(Path(p).resolve()) for p in (bc.FROZEN_SHA256_4C or {})}
    for table in (bc.EXP4_CLOSED_SHA256_4C, bc.EXP4B_CLOSED_SHA256_4C):
        covered |= {str((REPO / rel).resolve()) for rel in table}
    covered |= {str((REPO / rel).resolve()) for rel in bc.INSTRUMENT_BLOBS_4C}
    pinned = {str(Path(p).resolve()): v for p, v in IMPORTED_SHA256_4C.items()}
    drifted, unpinned = [], []
    for p, want in sorted(pinned.items()):
        pp = Path(p)
        if not pp.is_file() or bg.sha256_file(pp) != want:
            drifted.append(f"(pin) -> {p}")
    exp_root = str((REPO / "experiments").resolve())
    for name, mod in sorted(sys.modules.items()):
        f = getattr(mod, "__file__", None)
        if not f:
            continue
        rp = Path(f).resolve()
        s = str(rp)
        if not s.startswith(exp_root + "/") or "tests" in rp.parts:
            continue
        if s in covered or s in pinned:
            continue
        unpinned.append(f"{name} -> {s}")
    if unpinned:
        raise RuntimeError("unpinned module on the import surface: " + "; ".join(sorted(unpinned)))
    if drifted:
        raise RuntimeError("imported module drifted from its pin: " + "; ".join(sorted(drifted)))


def _git_sha_4c() -> str:
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO,
                          capture_output=True, text=True).stdout.strip()


# ----------------------------------------------------------- unit loaders

def _load_one_unit_4c(root, key) -> dict:
    """`{"record", "sets", "overlaps"}` for one 4c unit — a `(traj,
    step)` pair (step 0 included) or `THIN_ENDPOINT_KEY_4C` — with
    every pin `battery_4c.load_record_failures_4c` makes (family,
    render, batch, the committed digest AND the loader's own measured
    `tensor_digest`, refs, the 4c tag, the info contract, the on-disk
    sets shas) plus the four this analyzer owns: 34-rung coverage of
    `sets_sha256`, `n_hidden` against `N_HIDDEN_PIN_4C`, `sites`
    against `metric_4.sites_4`, and the depth pairing RE-DERIVED (Exp 4
    F-2: a record naming two of its three refs would silently average
    the alignment over the wrong reference set)."""
    d = battery_4.key_dir_4(root, key)
    rec_path = d / "_load.json"
    if not rec_path.is_file():
        raise ValueError(f"{key}: unit missing ({rec_path})")
    rec = json.loads(rec_path.read_text())
    bad = bc.load_record_failures_4c(rec, key=key, root=root)
    if bad:
        raise ValueError(f"{key}: {bad}")
    exp = bc.expected_fields_4c(key)
    if set(rec.get("sets_sha256") or {}) != set(bc.RUNGS):
        raise ValueError(f"{key}: sets_sha256 covers "
                         f"{sorted(set(rec.get('sets_sha256') or {}))} — unit short "
                         f"(need all {len(bc.RUNGS)} rungs)")
    if rec.get("n_hidden") != exp["n_hidden"]:
        raise ValueError(f"{key}: n_hidden {rec.get('n_hidden')!r} != pinned {exp['n_hidden']}")
    want_sites = metric_4.sites_4(exp["n_hidden"])
    if list(rec.get("sites") or []) != want_sites:
        raise ValueError(f"{key}: sites {rec.get('sites')!r} != {want_sites}")
    want_pairing = a4.expected_pairing_4(exp["n_hidden"], exp["refs"])
    got_pairing = rec.get("pairing")
    if not isinstance(got_pairing, dict) or sorted(got_pairing) != sorted(want_pairing):
        raise ValueError(
            f"{key}: pairing keys "
            f"{sorted(got_pairing) if isinstance(got_pairing, dict) else got_pairing!r} != the "
            f"record's own refs {sorted(want_pairing)} — the alignment would average over the "
            f"wrong reference set")
    for ref, want_p in want_pairing.items():
        got_p = got_pairing.get(ref)
        if not isinstance(got_p, (list, tuple)) or [int(j) for j in got_p] != want_p:
            raise ValueError(f"{key}/{ref}: pairing {got_p!r} != the depth pairing re-derived "
                             f"from the pinned site families {want_p!r} (design §3.1)")
    sets_by_rung, overlaps_by_ref = a4._read_sets_and_overlaps(d, rec)
    return {"record": rec, "sets": sets_by_rung, "overlaps": overlaps_by_ref}


def load_run_tables_4c(root, traj) -> dict:
    """`{step: unit}` over `GRID_4C[traj]`, each strictly pinned — a
    short unit raises and names itself."""
    return {step: _load_one_unit_4c(root, (traj, step)) for step in bc.GRID_4C[traj]}


def _attested_question_end_4c(root, key, rec) -> dict:
    """`{rung: uint16[n_sites, n, k]}` from `attested/<rung>.npz`'s
    `question_end` member — read only when the file is present AND its
    sha equals the record's own `attested_sha256[rung]`. Raises,
    naming the rung, otherwise; S9's caller collects that and prints
    `available: False` (the attested files are gitignored and may be
    absent on a fresh clone)."""
    d = battery_4.key_dir_4(root, key)
    att_sha = rec.get("attested_sha256") or {}
    out = {}
    for rung in bc.RUNGS:
        p = d / "attested" / f"{rung}.npz"
        if not p.is_file():
            raise ValueError(f"{key}/{rung}: attested/{rung}.npz absent (gitignored)")
        if bg.sha256_file(p) != att_sha.get(rung):
            raise ValueError(f"{key}/{rung}: attested sha != the record's")
        with np.load(p) as z:
            if "question_end" not in z.files:
                raise ValueError(f"{key}/{rung}: no question_end member")
            out[rung] = np.asarray(z["question_end"])
    return out


# ------------------------------------------------------------------ gates

def gate0_4c(root, traj, ref_tables, init_unit, endpoint_unit) -> dict:
    """Design §3.7 gate 3 — the instrument sees training, Exp 4's own
    gate 0 (`analyze_4.gate0_4`) with the two units passed in rather
    than looked up in a reference-stage table: 4c's referent is the
    run's REAL step 0, not a from_config twin, and both units live
    under `sweep/<traj>/`. Cells are per (rung, site, REFERENCE); the
    degenerate hidden state 0 is dropped on both sides (Exp 4 campaign
    stop #1). Passes iff the pooled `fraction_below` is at least
    `GATE0_MIN_FRACTION_4`."""
    sites, keep = a4._gate0_kept_positions_4(init_unit, endpoint_unit, traj)
    twin_site = a4._gate0_site_means_4(init_unit, ref_tables, init_unit["record"]["pairing"])
    endpoint_site = a4._gate0_site_means_4(endpoint_unit, ref_tables,
                                           endpoint_unit["record"]["pairing"])
    below, total, dropped = 0, 0, 0
    per_ref_below, per_ref_total, per_ref_dropped = {}, {}, {}
    for rung in bc.RUNGS:
        tw_by_ref, ep_by_ref = twin_site[rung], endpoint_site[rung]
        for ref in tw_by_ref:
            tw, ep = tw_by_ref[ref], ep_by_ref[ref]
            if tw.shape[0] != len(sites) or ep.shape[0] != len(sites):
                raise ValueError(f"gate0_4c {traj}/{rung}/{ref}: site means of length "
                                 f"{tw.shape[0]}/{ep.shape[0]} against a {len(sites)}-site "
                                 f"record {sites!r}")
            b = int(np.sum(tw[keep] < ep[keep]))
            n = len(keep)
            dr = len(sites) - n
            below += b
            total += n
            dropped += dr
            per_ref_below[ref] = per_ref_below.get(ref, 0) + b
            per_ref_total[ref] = per_ref_total.get(ref, 0) + n
            per_ref_dropped[ref] = per_ref_dropped.get(ref, 0) + dr
    fraction_below = (below / total) if total else 0.0
    per_reference = {
        ref: {"fraction_below": float(per_ref_below[ref] / per_ref_total[ref])
              if per_ref_total[ref] else 0.0,
              "n_cells": int(per_ref_total[ref]),
              "n_cells_excluded": int(per_ref_dropped[ref])}
        for ref in per_ref_total}
    return {"fraction_below": float(fraction_below), "n_cells": int(total),
            "excluded_sites": [int(s) for s in a4.GATE0_EXCLUDED_SITES_4],
            "n_cells_excluded": int(dropped), "per_reference": per_reference,
            "init_step": bc.INIT_STEP_4C, "endpoint_step": bc.ENDPOINT_STEP_4C[traj],
            "pass": bool(fraction_below >= a4.GATE0_MIN_FRACTION_4)}


def gate7_ties_4c(cells) -> dict:
    """Design §3.7 gate 7 — rank determinism: ties are counted at one
    half and their number is PRINTED per cell, never broken by an
    index. A nonzero count is a disclosure, not a refusal (float64
    means of 500 overlaps are expected to be distinct)."""
    per_cell = {f"{c['traj']}/{c['rung']}": int(c.get("n_ties") or 0) for c in cells}
    total = int(sum(per_cell.values()))
    return {"n_ties_total": total, "n_cells_with_ties": int(sum(1 for v in per_cell.values() if v)),
            "per_cell": per_cell, "tie_rule": "counted at one half", "gating": False}


# ------------------------------------------------------------- eligibility

def eligibility_4c(root, traj, ref_tables, unit_t1, unit_end, rung_sets, *,
                   n_boot=N_BOOT_ELIG_4C, seed=0) -> dict:
    """`analyze_4.eligibility_table_4`'s per-trajectory body on 4c's own
    units (S4's continuity arm needs Exp 4's instrument, not 4c's): the
    item bootstrap over the first grid point's and the endpoint's
    per-item alignments, the leave-nothing-out flat trend, each rising
    rung's endpoint excess with its SE and Exp 4's one-sided 2-SE
    eligibility bar, each flat rung's `se_at_end`.

    Hidden state 0 is INCLUDED here, unlike 4c's own statistic: this
    block exists to print phi, T, lambda-hat and 4b's placebo null on
    the two new runs through 4's and 4b's own frozen code (design §5
    S4), and `per_item_alignment_4` is that code."""
    n = battery_4.N_ITEMS
    R, flat = rung_sets["R"], rung_sets["flat"]
    steps = list(bc.GRID_4C[traj])
    first_step, endpoint_step = steps[0], steps[-1]

    pia_t1 = a4.per_item_alignment_4(unit_t1, ref_tables, unit_t1["record"]["pairing"])
    pia_end = a4.per_item_alignment_4(unit_end, ref_tables, unit_end["record"]["pairing"])

    rng = np.random.default_rng(seed)

    def boot(rung):
        idx = rng.integers(0, n, size=(n_boot, n))
        a_t1 = pia_t1[rung][idx].mean(axis=1)
        a_e = pia_end[rung][idx].mean(axis=1)
        return a_t1, a_e

    flat_boot_t1, flat_boot_e = [], []
    for r in flat:
        a_t1, a_e = boot(r)
        flat_boot_t1.append(a_t1)
        flat_boot_e.append(a_e)
    if flat:
        trend_boot_t1 = np.mean(flat_boot_t1, axis=0)
        trend_boot_e = np.mean(flat_boot_e, axis=0)
        trend_point_t1 = float(np.mean([pia_t1[r].mean() for r in flat]))
        trend_point_e = float(np.mean([pia_end[r].mean() for r in flat]))
    else:
        trend_boot_t1 = np.zeros(n_boot)
        trend_boot_e = np.zeros(n_boot)
        trend_point_t1 = trend_point_e = 0.0

    se_flat = {}
    for i, r in enumerate(flat):
        x_end_b = (flat_boot_e[i] - flat_boot_t1[i]) - (trend_boot_e - trend_boot_t1)
        se_flat[r] = float(np.std(x_end_b, ddof=1))

    per_rung_R = {}
    for r in R:
        a_t1_b, a_e_b = boot(r)
        x_end_b = (a_e_b - a_t1_b) - (trend_boot_e - trend_boot_t1)
        se = float(np.std(x_end_b, ddof=1))
        x_end_point = float((pia_end[r].mean() - pia_t1[r].mean())
                            - (trend_point_e - trend_point_t1))
        tclear = rung_sets["t_clear"][r]
        tci = steps.index(tclear) if tclear is not None else None
        below_se = not (x_end_point >= a4.SE_MULTIPLE_4 * se)
        no_window = tci is None or tci < a4.MIN_CLEAR_INDEX_4
        eligible = (not below_se) and (not no_window)
        if below_se:
            reason = "endpoint excess below 2 SE"
        elif no_window:
            reason = "no pre-clear window (t_clear at grid index < 2)"
        else:
            reason = "eligible"
        per_rung_R[r] = {"x_end": x_end_point, "se": se, "eligible": bool(eligible),
                         "reason": reason, "t_clear": tclear, "t_clear_index": tci}

    return {"R": per_rung_R, "flat": {r: {"se_at_end": se_flat[r]} for r in flat},
            "transient": list(rung_sets["transient"]), "trend_t1": trend_point_t1,
            "trend_end": trend_point_e, "n_boot": n_boot, "seed": seed,
            "steps_used": [first_step, endpoint_step]}


# ---------------------------------------------------------------- primary

def primary_4c(cells, *, n_boot=N_BOOT_4C, seed=SEED_4C) -> dict:
    """Design §3.4: U = the mean of q over the cells; the EXACT
    family-block sign flip of (q - 1/2) (nine families, 512 flips) as
    the primary null; the rung-level flip and the family-clustered
    percentile CI beside it. `p_plus`/`p_minus` are carried at the top
    level — `rank_4c.verdict_tree_4c` reads exactly those two."""
    fam = rk.block_flip_4c(cells, block="family")
    rung = rk.block_flip_4c(cells, block="rung")
    ci = rk.cluster_bootstrap_ci_4c(cells, block="family", n_boot=n_boot, seed=seed)
    return {"U": rk.U_4c(cells), "n_cells": len(cells),
            "n_rungs": len({c["rung"] for c in cells}),
            "n_families": fam["n_blocks"], "families": fam["blocks"],
            "p_plus": fam["p_plus"], "p_minus": fam["p_minus"], "n_flips": fam["n_flips"],
            "resolution": fam["resolution"], "observed": fam["observed"],
            "block_sums": fam["block_sums"], "family_flip": fam, "rung_flip": rung,
            "ci95": [ci["lo"], ci["hi"]], "n_boot": ci["n_boot"],
            # read live off `rank_4c`, never off this module's re-export:
            # the bars the TREE applies are that module's, so a record
            # that printed a different pair would be a lie about the
            # decision (and a world that moves a bar would go unrecorded).
            "alpha": rk.ALPHA_4C, "marginal": rk.MARGINAL_4C,
            "cells": [dict(c) for c in cells]}


# ------------------------------------------------------------ S4 continuity

def _clear_indices_4c(cells) -> list:
    """`battery_4b.cells_from_verdict_4b`'s rule over 4c's grids: each
    Exp-4-shaped cell's `t_clear` re-derived to its position on
    `GRID_4C[traj]`, never retyped, raising if it is not on that grid.
    The frozen function itself reads `battery_4.GRID_4`, which has no
    entry for either 4c trajectory."""
    out = []
    for c in cells:
        traj = c["traj"]
        grid = list(bc.GRID_4C[traj])
        try:
            idx = grid.index(c["t_clear"])
        except ValueError:
            raise ValueError(f"4c: t_clear {c['t_clear']} not on GRID_4C[{traj}]")
        out.append({"traj": traj, "rung": c["rung"], "phi": c["phi"], "t_clear": c["t_clear"],
                    "t_clear_index": idx})
    return out


def _design_4c(cells) -> dict:
    """`battery_4b.real_design_4b`'s rule over 4c's two trajectories.

    The frozen function itself cannot be called on 4c's cells: it
    builds its output dict over `battery_4.TRAJECTORIES_4` (Exp 4's
    four) and then indexes it by each cell's own `traj`, so a
    `pythia_6.9b` cell raises `KeyError`. The rule — per trajectory,
    the cell count, the sorted multiset of clear indices and the
    sorted rung names — is reproduced here verbatim over
    `TRAJECTORIES_4C`, and `test_design_4c_agrees_with_real_design_4b`
    proves the two agree on cells the frozen function CAN take."""
    out = {traj: {"n": 0, "clear_indices": [], "rungs": []} for traj in bc.TRAJECTORIES_4C}
    for c in cells:
        traj = c["traj"]
        out[traj]["n"] += 1
        out[traj]["clear_indices"].append(c["t_clear_index"])
        out[traj]["rungs"].append(c["rung"])
    for traj in out:
        out[traj]["clear_indices"] = sorted(out[traj]["clear_indices"])
        out[traj]["rungs"] = sorted(out[traj]["rungs"])
    return out


def s4_continuity_4c(series_by_traj, rung_sets_by_traj, eligibility_by_traj, pia_by_traj, *,
                     n_boot=N_BOOT_4C, B=B_PLACEBO_4C, seed=SEED_4C) -> dict:
    """Design §5 S4: phi, T, eligibility, lambda-hat and 4b's p_cal,
    T*, alpha_placebo and per-run nulls on the two new runs, through
    Exp 4's and 4b's own frozen code. DESCRIPTIVE — `no_alpha_claim`;
    every piece is collected separately, so a refusal degrades this
    block and never the verdict.

    `series_by_traj` here is the site-0-INCLUDED series (Exp 4's own
    `alignment_series_4` construction): 4b's `placebo_pool_4b` refuses
    unless each flat rung's first and last series values are exactly
    the means of `pia_t1`/`pia_end`, which holds only for that
    construction."""
    out = {"no_alpha_claim": True, "source": "re-derived",
           "note": ("Exp 4's phi/T and 4b's placebo null on the two new runs, site 0 included, "
                    "for continuity with the closed record; no alpha is claimed and no bar is "
                    "read against these numbers")}
    fails = []

    cells, f = collect_total_4c(
        lambda: a4.cells_4(series_by_traj, rung_sets_by_traj, eligibility_by_traj), "4c S4 cells")
    fails += f
    out["cells"] = cells or []
    out["n_cells"] = len(cells or [])

    primary = None
    if cells:
        primary, f = collect_total_4c(lambda: a4.primary_4(cells, n_boot=n_boot, seed=seed),
                                      "4c S4 primary_4")
        fails += f
    out["primary"] = ({"T": primary["T"], "p_plus": primary["p_plus"],
                       "p_minus": primary["p_minus"], "ci95": primary["ci95"],
                       "n_cells": primary["n_cells"], "n_rungs": primary["n_rungs"],
                       "per_traj": primary["per_traj"], "per_type": primary["per_type"]}
                      if primary else None)

    lam, f = collect_total_4c(
        lambda: a4.lambda_hat_4(series_by_traj, rung_sets_by_traj, eligibility_by_traj),
        "4c S4 lambda_hat")
    fails += f
    out["lambda_hat"] = lam

    out["eligibility"] = {traj: {"n_R": len((b or {}).get("R") or {}),
                                 "n_eligible": sum(1 for e in ((b or {}).get("R") or {}).values()
                                                   if e.get("eligible")),
                                 "n_flat": len((b or {}).get("flat") or {})}
                          for traj, b in (eligibility_by_traj or {}).items()}

    # ---- 4b's placebo, on the two new runs
    pools = {}
    for traj in sorted(series_by_traj):
        pia = (pia_by_traj or {}).get(traj) or {}
        pool, f = collect_total_4c(
            lambda traj=traj, pia=pia: placebo_4b.placebo_pool_4b(
                series_by_traj[traj], pia["t1"], pia["end"], rung_sets_by_traj[traj]["flat"],
                n_boot=N_BOOT_ELIG_4C, seed=seed),
            f"4c S4 placebo pool {traj}")
        fails += f
        if pool is not None:
            pools[traj] = pool
    out["placebo_pool"] = {t: {"n_flat": len(p),
                               "n_eligible": sum(1 for d in p.values() if d["eligible"])}
                           for t, p in pools.items()}

    design, f = collect_total_4c(lambda: _design_4c(_clear_indices_4c(cells or [])),
                                 "4c S4 placebo design")
    fails += f
    if cells and primary is not None and design is not None \
            and len(pools) == len(series_by_traj):
        batteries, f = collect_total_4c(
            lambda: placebo_4b.draw_batteries_4b(pools, design, B=B, seed=seed),
            "4c S4 placebo batteries")
        fails += f
        if batteries is not None:
            T4 = float(primary["T"])
            p_cal, f = collect_total_4c(lambda: placebo_4b.p_cal_4b(batteries["T"], T4),
                                        "4c S4 p_cal")
            fails += f
            t_star, f = collect_total_4c(lambda: placebo_4b.t_star_4b(batteries["T"], T4),
                                         "4c S4 t_star")
            fails += f
            alpha, f = collect_total_4c(
                lambda: placebo_4b.alpha_placebo_4b(
                    batteries, seed=seed,
                    real_regime={"flip_method": primary.get("flip_method"),
                                 "n_rungs": primary.get("n_rungs")}),
                "4c S4 alpha_placebo")
            fails += f
            out["p_cal"] = p_cal
            out["t_star"] = t_star
            out["alpha_placebo"] = alpha
            out["design"] = design
            out["feasibility"] = batteries.get("feasibility")
            out["B"] = int(B)

    if fails:
        out["degraded"] = fails
    return out


# ------------------------------------------------------------- secondaries

def s1_per_run_4c(cells, *, n_boot=N_BOOT_4C, seed=SEED_4C) -> dict:
    """S1: U, its family-block p and its cluster CI on each run
    separately (6.9b's 8 cells, 13B's 18)."""
    out = {}
    for traj in sorted({c["traj"] for c in cells}):
        sub = [c for c in cells if c["traj"] == traj]
        fl = rk.block_flip_4c(sub, block="family")
        ci = rk.cluster_bootstrap_ci_4c(sub, block="family", n_boot=n_boot, seed=seed)
        out[traj] = {"U": rk.U_4c(sub), "n_cells": len(sub), "n_families": fl["n_blocks"],
                     "p_plus": fl["p_plus"], "p_minus": fl["p_minus"],
                     "resolution": fl["resolution"], "ci95": [ci["lo"], ci["hi"]]}
    return {"per_traj": out, "no_alpha_claim": True}


def _binom_tail_4c(k, n, p=0.5) -> float:
    """P(X >= k) for X ~ Binomial(n, p), exact over the integers."""
    from math import comb
    return float(sum(comb(n, i) * (p ** i) * ((1 - p) ** (n - i)) for i in range(k, n + 1)))


def s2_strata_4c(cells, discovery) -> dict:
    """S2: the per-type and per-family readings, and the sign of each
    family's sum here against the same family's sum on the discovery
    set — nine signs, with the binomial tail, DESCRIPTIVE (the
    discovery set's signs are known to the designer, design §5)."""
    fl = rk.block_flip_4c(cells, block="family")
    per_family = {}
    for fam in fl["blocks"]:
        sub = [c for c in cells if c["family"] == fam]
        per_family[fam] = {"U": rk.U_4c(sub), "n_cells": len(sub), "sum": fl["block_sums"][fam]}
    per_type = {}
    for typ in sorted({c["type"] for c in cells}):
        sub = [c for c in cells if c["type"] == typ]
        per_type[typ] = {"U": rk.U_4c(sub), "n_cells": len(sub),
                         "n_rungs": len({c["rung"] for c in sub})}
    disc_sums = (discovery or {}).get("family_sums") or {}
    agree, compared = {}, []
    for fam, s in sorted(fl["block_sums"].items()):
        if fam not in disc_sums:
            continue
        compared.append(fam)
        agree[fam] = bool((s > 0) == (disc_sums[fam] > 0))
    n_agree = sum(1 for v in agree.values() if v)
    return {"per_family": per_family, "per_type": per_type,
            "family_sign_agreement": agree, "n_compared": len(compared),
            "n_agree": n_agree,
            "binomial_tail": _binom_tail_4c(n_agree, len(compared)) if compared else None,
            "families_only_here": sorted(set(fl["block_sums"]) - set(disc_sums)),
            "families_only_on_the_discovery_set": sorted(set(disc_sums) - set(fl["block_sums"])),
            "descriptive": True, "no_alpha_claim": True}


def s3_window_mean_4c(series_by_traj, rung_sets_by_traj) -> dict:
    """S3: q averaged over every pre-clear checkpoint (indices 1..c-1)
    instead of read at t- alone, with its own U and family flip."""
    cells = rk.window_mean_cells_4c(series_by_traj, rung_sets_by_traj)
    if not cells:
        return {"available": False, "reason": "no cells", "no_alpha_claim": True}
    fl = rk.block_flip_4c(cells, block="family")
    return {"available": True, "U": rk.U_4c(cells), "n_cells": len(cells),
            "p_plus": fl["p_plus"], "p_minus": fl["p_minus"], "n_families": fl["n_blocks"],
            "cells": cells, "descriptive": True, "no_alpha_claim": True}


def s6_pooled_4c(cells, discovery) -> dict:
    """S6: U over the discovery set's 42 cells and the confirmation
    set's 26 pooled, with the split printed and the known-outcome
    caveat verbatim. The essay may not quote the pooled number without
    the split (design §5)."""
    disc_cells = (discovery or {}).get("cells")
    if not disc_cells:
        return {"available": False,
                "reason": "the discovery record carries no per-cell table",
                "no_alpha_claim": True}
    q_disc = [float(c["q"]) for c in disc_cells]
    q_new = [float(c["q"]) for c in cells]
    pooled = q_disc + q_new
    return {"available": True, "U_pooled": float(np.mean(pooled)), "n_pooled": len(pooled),
            "U_discovery": float(np.mean(q_disc)), "n_discovery": len(q_disc),
            "U_confirmation": float(np.mean(q_new)), "n_confirmation": len(q_new),
            "split_required": True, "known_outcome_caveat": KNOWN_OUTCOME_CAVEAT_4C,
            "discovery_status": ("post hoc on four runs the designer had seen — motivation, "
                                 "never evidence (design §2)"),
            "descriptive": True, "no_alpha_claim": True}


def s8_levels_4c(root, series_by_traj, init_units, ref_tables_by_traj, ref_raw_by_traj) -> dict:
    """S8: the levels, hidden state 0 EXCLUDED — the real step 0, the
    endpoint, the references' own pairwise ceiling, and the per-
    reference series. Levels, not the statistic: nothing here enters
    the primary."""
    out = {"per_traj": {}, "excluded_sites": list(rk.EXCLUDED_SITES_4C),
           "source": "re-derived", "no_alpha_claim": True}
    for traj in sorted(series_by_traj):
        series = series_by_traj[traj]
        unit0 = (init_units or {}).get(traj)
        step0 = None
        if unit0 is not None:
            s0 = rk.alignment_series_4c({bc.INIT_STEP_4C: unit0}, ref_tables_by_traj[traj],
                                        steps=[bc.INIT_STEP_4C])
            step0 = {r: s0["a"][r][0] for r in bc.RUNGS}
        endpoint = {r: series["a"][r][-1] for r in bc.RUNGS}
        first = {r: series["a"][r][0] for r in bc.RUNGS}
        out["per_traj"][traj] = {
            "step0": step0,
            "step0_mean": (float(np.mean(list(step0.values()))) if step0 else None),
            "first_grid_point": first,
            "first_grid_point_mean": float(np.mean(list(first.values()))),
            "endpoint": endpoint, "endpoint_mean": float(np.mean(list(endpoint.values()))),
            # design §5 S8: "per-reference a_r(t)" — the SERIES over the
            # grid, per reference and per rung, not a single level.
            "a_by_ref": {ref: {rung: [float(x) for x in vals] for rung, vals in by_rung.items()}
                         for ref, by_rung in (series.get("a_by_ref") or {}).items()},
            "a_by_ref_endpoint_mean": {ref: float(np.mean([v[-1] for v in by_rung.values()]))
                                       for ref, by_rung in (series.get("a_by_ref") or {}).items()},
            "steps": list(series["steps"]),
            "ceiling": references_ceiling_4c(ref_raw_by_traj[traj]),
        }
    return out


def references_ceiling_4c(ref_raw) -> dict:
    """The references' own pairwise mutual k-NN, hidden state 0
    excluded: for each unordered pair of the trajectory's three
    references, the depth-paired overlap fraction per rung (mean over
    the first reference's kept sites and the 500 items), averaged over
    the rungs. The ceiling a trajectory's alignment is read against —
    committed bytes only, no reference is loaded."""
    keys = sorted(ref_raw)
    out = {}
    for i, a_key in enumerate(keys):
        for b_key in keys[i + 1:]:
            ra, rb = ref_raw[a_key], ref_raw[b_key]
            sites_a, sites_b = list(ra["sites"]), list(rb["sites"])
            pairing = collect_4._pairing_positions(sites_a, ra["n_hidden"], sites_b,
                                                   rb["n_hidden"])
            keep = [i_ for i_, s in enumerate(sites_a) if int(s) not in rk.EXCLUDED_SITES_4C]
            vals = []
            for rung in bc.RUNGS:
                ov = collect_4.overlap_table_4(ra["sets"][rung], rb["sets"][rung], pairing)
                vals.append(float((ov[keep].astype(np.float64) / metric_4.K_4).mean()))
            out[f"{a_key}|{b_key}"] = {"mean": float(np.mean(vals)),
                                       "per_rung": dict(zip(bc.RUNGS, vals))}
    return out


def _reference_attested_sha_ok_4c(root4, ref, rec) -> tuple:
    """True/None, or False/a reason — the REFERENCE side of S9's
    gitignored-and-hash-checked contract. `_attested_question_end_4c`
    already sha-checks the MODEL/unit side's `attested/<rung>.npz`
    against its own record before S9 ever sees it; `collect_4.
    load_ref_tables_4`'s reference loader reads a reference's
    `attested/<rung>.npz` with NO sha check at all (fix round 2
    finding 4b) — this closes that gap by re-hashing the file on disk
    against the reference's OWN `_load.json` record's
    `attested_sha256[rung]` before `s9_question_end_4c` reads
    `sets_question_end`."""
    att_sha = rec.get("attested_sha256") or {}
    for rung in bc.RUNGS:
        p = battery_4.attested_path(root4, ref, rung)
        if not p.is_file():
            return False, f"{ref}/{rung}: attested/{rung}.npz absent (gitignored)"
        if bg.sha256_file(p) != att_sha.get(rung):
            return False, f"{ref}/{rung}: attested sha != the reference record's"
    return True, None


def s9_question_end_4c(root, root4, run_tables_by_traj, ref_raw_by_traj,
                       rung_sets_by_traj) -> dict:
    """S9 (dial l): the identical statistic at the QUESTION-END
    position — M's own attested question-end set tables against the
    references' attested question-end tables. Both sides are
    GITIGNORED artifacts, absent on a fresh clone, and both are
    HASH-CHECKED against their own committed `_load.json` record
    before use (the model side by `_attested_question_end_4c`, the
    reference side by `_reference_attested_sha_ok_4c` above — fix
    round 2 finding 4b closed a real gap: `collect_4.load_ref_tables_4`
    itself never checks the reference's attested sha). Descriptive
    only: when either side is absent, or a sha does not match its
    record, the block reads `available: False` and says which."""
    qe_refs = {}
    for traj, raw in ref_raw_by_traj.items():
        block = {}
        for ref, rt in raw.items():
            ok, reason = _reference_attested_sha_ok_4c(root4, ref, rt.get("record") or {})
            if not ok:
                return {"available": False, "reason": reason, "no_alpha_claim": True}
            qe = rt.get("sets_question_end") or {}
            if set(qe) != set(bc.RUNGS):
                return {"available": False,
                        "reason": f"{ref}: the reference's question-end set tables are not "
                                  f"available (attested/*.npz is gitignored)",
                        "no_alpha_claim": True}
            block[ref] = qe
        qe_refs[traj] = block

    series_qe = {}
    for traj, tables in run_tables_by_traj.items():
        a = {r: [] for r in bc.RUNGS}
        steps = list(bc.GRID_4C[traj])
        for step in steps:
            unit = tables[step]
            rec = unit["record"]
            sites = rec["sites"]
            keep = [i for i, s in enumerate(sites) if int(s) not in rk.EXCLUDED_SITES_4C]
            qe_m = _attested_question_end_4c(root, (traj, step), rec)
            for rung in bc.RUNGS:
                per_ref = []
                for ref, pairing in rec["pairing"].items():
                    ov = collect_4.overlap_table_4(qe_m[rung], qe_refs[traj][ref][rung], pairing)
                    per_ref.append(ov[keep].astype(np.float64) / metric_4.K_4)
                pooled = np.stack(per_ref, axis=0).mean(axis=(0, 1))
                a[rung].append(float(pooled.mean()))
        series_qe[traj] = {"steps": steps, "a": a}

    cells = rk.cells_4c(series_qe, rung_sets_by_traj)
    if not cells:
        return {"available": False, "reason": "no cells at the question-end position",
                "no_alpha_claim": True}
    fl = rk.block_flip_4c(cells, block="family")
    mod = rk.type_modifier_4c(cells)
    return {"available": True, "U": rk.U_4c(cells), "n_cells": len(cells),
            "p_plus": fl["p_plus"], "p_minus": fl["p_minus"], "n_families": fl["n_blocks"],
            "modifier": mod["modifier"], "position": "question_end",
            "source": "attested (gitignored; absent on a fresh clone)",
            "descriptive": True, "no_alpha_claim": True}


def s10_texture_4c(s4, series_incl_by_traj, rung_sets_by_traj) -> dict:
    """S10: the flat pool's texture — lambda-hat (from S4's own block,
    Exp 4's own construction) and the lag-1 autocorrelation of the flat
    rungs' leave-one-out excess increments (4b's S5): is 13B a random
    walk like its 7B sibling?"""
    autocorr = placebo_4b.s5_autocorr_4b(series_incl_by_traj, rung_sets_by_traj)
    return {"lambda_hat": (s4 or {}).get("lambda_hat"), "autocorr": autocorr,
            "series": "site 0 included (4b's own construction)",
            "descriptive": True, "no_alpha_claim": True}


# ---------------------------------------------------------- licence block

def _power_quote_4c(power) -> str:
    """§4's declaration and blind region, quoted from the power record
    (never retyped). A missing record is named, not papered over."""
    if not power:
        return _POWER_MISSING_4C
    decl = power.get("declaration")
    blind = power.get("blind_region")
    if not decl:
        return _POWER_MISSING_4C
    tail = f" Blind region: {blind}." if blind else ""
    return f"Power, quoted from the record written before the tag: {decl}.{tail}"


def licence_block_4c(world, modifier, calibration, tree, power) -> dict:
    """Design §6, printed rather than left to the reader (2n note 1):
    the reached cell, its sentence with the modifier's noun
    substituted, the calibration read, the REVERSED check, the battery
    limit and the known-outcome caveat."""
    mod = (modifier or {}).get("modifier")
    body = LICENSED_4C.get(world, LICENSED_4C["INSUFFICIENT_DATA"])
    if world == REFUSAL_WORLD_4C:
        return {"world": world, "modifier": None, "bounded": None, "reversed": None,
                "sentence": body, "known_outcome_caveat": KNOWN_OUTCOME_CAVEAT_4C}
    noun = MODIFIER_NOUN_4C.get(mod, MODIFIER_NOUN_4C["NEITHER"])
    parts = [body.replace("{noun}", noun)]
    bounded = bool((calibration or {}).get("bounded"))
    if bounded:
        parts.append(BOUNDED_SENTENCE_4C.format(alpha=float(calibration.get("alpha_at_bar") or 0.0),
                                                bar=float(calibration.get("deciding_bar") or 0.0)))
    reversed_ = bool((tree or {}).get("reversed"))
    if reversed_:
        parts.append(REVERSED_SENTENCE_4C)
    if world == "NOT-REPLICATED":
        parts.append(_power_quote_4c(power))
    parts.append(BATTERY_LIMIT_4C)
    parts.append(f"Disclosure (design §6): {KNOWN_OUTCOME_CAVEAT_4C} {NOT_A_FORECAST_4C}")
    return {"world": world, "modifier": mod, "bounded": bounded, "reversed": reversed_,
            "sentence": " ".join(parts), "known_outcome_caveat": KNOWN_OUTCOME_CAVEAT_4C,
            "not_a_forecast": NOT_A_FORECAST_4C}


# ---------------------------------------------------------------- verdict

def _placebo_summary_4c(placebo) -> dict:
    """The placebo record without its two B-element arrays (`U_b`,
    `U_b_nonarith`): the verdict carries the summary, not 20,000
    floats."""
    if not placebo:
        return None
    return {"null_mean": placebo["null_mean"], "null_sd": placebo["null_sd"],
            "p_placebo": placebo["p_placebo"],
            "alpha_placebo_01": placebo["alpha_placebo_01"],
            "alpha_placebo_05": placebo["alpha_placebo_05"],
            "U_nonarith": placebo.get("U_nonarith"),
            "p_placebo_nonarith": placebo.get("p_placebo_nonarith"),
            "n_nonarith_cells": placebo.get("n_nonarith_cells"),
            "pool_common": list(placebo["pool_common"]), "n_pool": placebo["n_pool"],
            "B": placebo["B"], "seed": placebo["seed"],
            "no_alpha_claim": placebo["no_alpha_claim"]}


def _modifier_block_4c(modifier, placebo) -> dict:
    """The §3.5 modifier with the non-arithmetic stratum's two
    descriptives printed side by side and both labelled: its
    rung-level p and its placebo p. `p_family` stays `None` with its
    reason — a null that cannot resolve the bar prints no p (4b
    process note 3)."""
    if not modifier:
        return None
    out = {"modifier": modifier["modifier"], "arith": modifier.get("arith")}
    na = modifier.get("nonarith")
    if na is not None:
        out["nonarith"] = dict(na)
        out["nonarith"]["p_placebo_nonarith"] = (placebo or {}).get("p_placebo_nonarith")
        out["nonarith"]["descriptive"] = ("p_rung_descriptive and p_placebo_nonarith are "
                                          "descriptives; neither carries an alpha claim")
    else:
        out["nonarith"] = None
    out["battery_limit"] = BATTERY_LIMIT_4C
    return out


def _json_rung_sets_4c(rung_sets_by_traj) -> dict:
    return {t: {"R": list(rs["R"]), "flat": list(rs["flat"]),
                "transient": list(rs["transient"]), "t_clear": dict(rs["t_clear"]),
                "endpoint_step": rs["endpoint_step"]}
            for t, rs in (rung_sets_by_traj or {}).items() if rs is not None}


def _discovery_summary_4c(discovery) -> dict:
    if not discovery:
        return None
    return {k: v for k, v in discovery.items() if k != "cells"}


def _power_summary_4c(power) -> dict:
    if not power:
        return None
    arms = power.get("arms") or {}
    disc = arms.get("discovery_shape") if isinstance(arms, dict) else None
    return {"declaration": power.get("declaration"),
            "n_sim": power.get("n_sim"), "seed": power.get("seed"),
            "n_cells": power.get("n_cells"), "n_families": power.get("n_families"),
            "cells_sha256": power.get("cells_sha256"),
            "realized_alpha_01": power.get("realized_alpha_01"),
            "realized_alpha_05": power.get("realized_alpha_05"),
            "min_detectable_uniform_lead": power.get("min_detectable_uniform_lead"),
            "blind_region": power.get("blind_region"),
            "P_discovery_shape_01": (disc.get("P_01") if isinstance(disc, dict) else None),
            "P_discovery_shape_05": (disc.get("P_05") if isinstance(disc, dict) else None),
            "prereg_tag": power.get("prereg_tag")}


def verdict_4c(*, failures, tree, primary, placebo, modifier, calibration, cells,
               rung_sets_by_traj, gate0_records, gate1_records, gate7, discovery, power,
               secondaries, pins_active, n_boot, B) -> dict:
    world = tree["verdict"]
    failures = list(failures)
    licence, f = collect_total_4c(
        lambda: licence_block_4c(world, modifier, calibration, tree, power), "4c licence block")
    failures += f
    if licence is None:
        licence = {"world": world, "modifier": None, "bounded": None, "reversed": None,
                   "sentence": LICENSED_4C["INSUFFICIENT_DATA"],
                   "known_outcome_caveat": KNOWN_OUTCOME_CAVEAT_4C}
    return {
        "verdict": world,
        "tree": tree,
        "reason": tree["reason"],
        "known_outcome_caveat": KNOWN_OUTCOME_CAVEAT_4C,
        "licence": licence,
        "licensed_sentence": licence["sentence"],
        "primary": primary,
        "placebo": _placebo_summary_4c(placebo),
        "modifier": _modifier_block_4c(modifier, placebo),
        "calibration": calibration,
        "cells": [dict(c) for c in (cells or [])],
        "gate0": gate0_records,
        "gate1": gate1_records,
        "gate7_ties": gate7,
        "discovery": _discovery_summary_4c(discovery),
        "power": _power_summary_4c(power),
        "rung_sets": _json_rung_sets_4c(rung_sets_by_traj),
        "secondaries": secondaries or None,
        "pins_active": pins_active,
        "failures": list(failures),
        "referents": {"failures": list(failures)},
        "n_boot": n_boot,
        "B": B,
        "git_sha": _git_sha_4c(),
        "stack_note": "analysis-only, no model contact",
    }


def write_verdict_txt_4c(v: dict) -> str:
    lines = [f"EXPERIMENT 4c VERDICT: {v['verdict']}", "", v["reason"], "",
             f"Caveat: {v['known_outcome_caveat']}", ""]
    lic = v.get("licence") or {}
    lines.append(f"Licence cell: world={lic.get('world')} modifier={lic.get('modifier')} "
                 f"bounded={lic.get('bounded')} reversed={lic.get('reversed')}")
    lines.append(f"Licence: {lic.get('sentence')}")
    lines.append("")
    p = v.get("primary")
    if p:
        lines.append(f"Primary (design §3.4): U={p['U']:.4f} p+={p['p_plus']:.4g} "
                     f"p-={p['p_minus']:.4g} CI95=[{p['ci95'][0]:.4f}, {p['ci95'][1]:.4f}] "
                     f"n_cells={p['n_cells']} n_rungs={p['n_rungs']} "
                     f"n_families={p['n_families']} flips={p['n_flips']} "
                     f"resolution={p['resolution']:.6g}")
        rf = p.get("rung_flip") or {}
        lines.append(f"  rung-level flip: p+={rf.get('p_plus')} over {rf.get('n_blocks')} rungs")
        lines.append("")
        lines.append("Per-cell q:")
        for c in p.get("cells") or []:
            lines.append(f"  {c['traj']}/{c['rung']} ({c['type']}, {c['family']}): "
                         f"q={c['q']:.4f} c={c['c']} t-={c['t_minus_step']} "
                         f"n_flat={c['n_flat']} ties={c['n_ties']}"
                         + (f" q_arith={c['q_arith']:.4f}" if c.get("q_arith") is not None else ""))
        lines.append("")
    s1 = ((v.get("secondaries") or {}).get("S1") or {}).get("per_traj") or {}
    if s1:
        lines.append("Per-run U (S1):")
        for traj, b in sorted(s1.items()):
            lines.append(f"  {traj}: U={b['U']:.4f} p+={b['p_plus']:.4g} "
                         f"n_cells={b['n_cells']} n_families={b['n_families']} "
                         f"CI95=[{b['ci95'][0]:.4f}, {b['ci95'][1]:.4f}]")
        lines.append("")
    s2 = (v.get("secondaries") or {}).get("S2") or {}
    if s2.get("per_type"):
        lines.append("Per-type U (S2):")
        for typ, b in sorted(s2["per_type"].items()):
            lines.append(f"  {typ}: U={b['U']:.4f} n_cells={b['n_cells']}")
        lines.append("")
    mod = v.get("modifier")
    if mod:
        ar, na = mod.get("arith"), mod.get("nonarith")
        lines.append(f"Type modifier (design §3.5): {mod.get('modifier')}")
        if ar:
            lines.append(f"  arithmetic (matched pool): U={ar['U']:.4f} p+={ar['p_plus']:.4g} "
                         f"n_cells={ar['n_cells']} n_families={ar['n_families']}")
        if na:
            lines.append(f"  non-arithmetic (whole pool): U={na['U']:.4f} n_cells={na['n_cells']} "
                         f"p_family={na['p_family']} ({na.get('p_family_reason')}); "
                         f"p_rung_descriptive={na.get('p_rung_descriptive')}, "
                         f"p_placebo_nonarith={na.get('p_placebo_nonarith')}")
        lines.append(f"  {mod.get('battery_limit')}")
        lines.append("")
    pl = v.get("placebo")
    if pl:
        lines.append(f"Placebo null (design §3.4): mean={pl['null_mean']:.4f} "
                     f"sd={pl['null_sd']:.4f} p_placebo={pl['p_placebo']:.4g} "
                     f"B={pl['B']} pool={pl['n_pool']}")
    cal = v.get("calibration")
    if cal:
        lines.append(f"Calibration (design §3.6): deciding bar {cal.get('deciding_bar')}, "
                     f"alpha_placebo at the bar {cal.get('alpha_at_bar')}, "
                     f"bounded={cal.get('bounded')} "
                     f"(alpha_01={cal.get('alpha_placebo_01')}, "
                     f"alpha_05={cal.get('alpha_placebo_05')})")
    lines.append("")
    g7 = v.get("gate7_ties")
    if g7:
        lines.append(f"Gate 7 (ties): {g7['n_ties_total']} exact ties over "
                     f"{g7['n_cells_with_ties']} cells, {g7['tie_rule']}")
    for traj, g in sorted((v.get("gate0") or {}).items()):
        if g:
            lines.append(f"Gate 0 {traj}: pass={g['pass']} fraction_below="
                         f"{g['fraction_below']:.4f} on {g['n_cells']} cells "
                         f"({g['n_cells_excluded']} excluded at site 0)")
    for traj, g in sorted((v.get("gate1") or {}).items()):
        if g:
            lines.append(f"Gate 1 {traj}: {g.get('n_rungs')} rungs vs "
                         f"{g.get('reference_root')}/{g.get('reference_key')}, "
                         f"digest_equal={g.get('digest_equal')}")
    lines.append("")
    pw = v.get("power")
    if pw:
        lines.append(f"Power (§4, written before the tag): {pw.get('declaration')}; "
                     f"P(p+<.01 | discovery shape)={pw.get('P_discovery_shape_01')}; "
                     f"min detectable uniform lead={pw.get('min_detectable_uniform_lead')}")
        lines.append("")
    disc = v.get("discovery")
    if disc:
        lines.append(f"Discovery gate (design §3.7(1), KNOWN runs): U={disc.get('U')} over "
                     f"{disc.get('n_cells')} cells, family p={disc.get('p_family')}")
        lines.append("")
    lines.append(f"Secondaries present: {sorted((v.get('secondaries') or {}))}")
    lines.append("")
    lines.append("Pins active:")
    for k in sorted(v.get("pins_active") or {}):
        lines.append(f"  {k}={v['pins_active'][k]}")
    lines.append("")
    fails = v.get("failures") or []
    lines.append(f"Failures ({len(fails)}):")
    for m in fails:
        lines.append(f"  {m}")
    lines.append("")
    lines.append(f"git_sha={v.get('git_sha')}")
    return "\n".join(lines) + "\n"


# -------------------------------------------------------------------- run

_LITERAL = object()


def _import_power_4c():
    from experiments.exp4c import power_4c as pw4c
    return pw4c


def run(root=bc.EXP4C, root4=EXP4, *, write=False, n_boot=N_BOOT_4C, B=B_PLACEBO_4C,
        tag_exists=None, blob_sha=None, blobs_bound=None, referents_sha=_LITERAL,
        imports_pinned=_LITERAL, frozen_check=None, discovery_check=None, expected_n_sim=None,
        power_gate="full", out_path=None) -> dict:
    """The whole verdict path. Every step is a `collect_total_4c` site
    and every failure is delivered as INSUFFICIENT_DATA — nothing
    raises out of this function.

    Refusal order (design §3.7-§3.8): halt markers -> frozen modules ->
    the import surface (entry) -> the preregistration tag -> the 2h/2l
    manifests -> the referent manifest -> battery and floors -> the
    committed outcomes, rung sets and their §3.2 pins -> Exp 4's
    reference seal over the five reused keys -> the reference tables ->
    THE DISCOVERY GATE (§3.7(1)) -> the power record -> per trajectory
    (only with a clean slate): gate 1, the thin endpoint, step 0, the
    grid, gate 0, the alignment series, S4's eligibility inputs -> the
    cells, the primary, the placebo, the modifier, the tree, the
    calibration read, S1-S10 -> the import surface (exit) -> the
    licence block.

    `power_gate="skip"` (TEST-ONLY, disclosed in `pins_active`) bypasses
    the two power checks that need `power_4c` — the live cell
    structure's sha and the byte reproduction — and leaves the
    record's presence, tag, declaration and `n_sim` checked.
    `discovery_check` (TEST-ONLY) replaces `rank_4c.discovery_set_4c`,
    which reads Exp 4's committed sweep tree: a synthetic world has no
    such tree."""
    if power_gate not in ("full", "skip"):
        raise ValueError(f"4c: power_gate must be 'full' or 'skip', got {power_gate!r}")
    failures = []
    root = Path(root)
    root4 = Path(root4)

    if referents_sha is _LITERAL:
        referents_sha = REFERENTS_4C_SHA256
    if imports_pinned is _LITERAL:
        imports_pinned = None if IMPORTED_SHA256_4C is None else True

    power_n_sim_expected = expected_n_sim
    power_n_sim_injected = expected_n_sim is not None

    # ---- halt markers (both trajectories)
    for traj in bc.TRAJECTORIES_4C:
        p = battery_4.halt_marker_path(root, traj)
        if p.exists():
            halted, f = collect_total_4c(lambda p=p: p.read_text().strip()[:200],
                                         "4c halt marker read")
            failures += f
            if not f:
                failures.append(f"4c: the runner halted ({p}): {halted}")

    _, f = collect_total_4c(frozen_check or bc.check_frozen_4c, "4c frozen modules")
    failures += f

    if imports_pinned:
        _, f = collect_total_4c(check_imports_4c, "4c import surface (entry)")
        failures += f
    elif imports_pinned is not False:
        failures.append("4c import surface: not pinned (build incomplete)")

    _, f = collect_total_4c(
        lambda: bc.require_prereg_4c(tag_exists=tag_exists, blob_sha=blob_sha), "4c prereg tag")
    failures += f

    _, f = collect_total_4c(bc.manifests_4c, "4c checkpoint manifests")
    failures += f

    referent_manifest_ok = False
    if referents_sha is None:
        failures.append("4c referent manifest: not pinned (build incomplete)")
    elif referents_sha is not False:
        def _check_referents():
            from experiments.exp4c import make_referents_4c as mkr
            return mkr.check_referents_4c(REFERENTS_PATH_4C, sha_pin=referents_sha)
        mf, f = collect_total_4c(_check_referents, "4c referent manifest")
        failures += f + (mf or [])
        referent_manifest_ok = not f and not mf

    battery, f = collect_total_4c(bt.load_battery, "4c battery items")
    failures += f
    floors, f = collect_total_4c(bg.load_floors, "4c floors 2d")
    failures += f

    rung_sets = {}
    if battery is not None and floors is not None:
        for traj in bc.TRAJECTORIES_4C:
            oc, f = collect_total_4c(
                lambda traj=traj: bc.load_outcome_4c(traj, battery=battery), f"4c outcome {traj}")
            failures += f
            rs = None
            if oc is not None:
                rs, f = collect_total_4c(lambda oc=oc: bc.rung_sets_4c(oc, floors),
                                         f"4c rung sets {traj}")
                failures += f
                if rs is not None:
                    bad, f = collect_total_4c(
                        lambda traj=traj, rs=rs, oc=oc: bc.check_rung_set_pins_4c(
                            traj, rs, oc["steps"]), f"4c rung-set pins {traj}")
                    failures += f + [f"4c {b}" for b in (bad or [])]
            rung_sets[traj] = rs
    else:
        for traj in bc.TRAJECTORIES_4C:
            rung_sets[traj] = None
        failures.append("4c outcomes: battery or floors missing")

    seal, f = collect_total_4c(
        lambda: an2i.require_seal_2i(battery_4.REFERENCE_SEAL_TAG_4,
                                     bc.exp4_reference_paths_4c(root4),
                                     tag_exists=tag_exists, blobs_bound=blobs_bound,
                                     repo_root=REPO),
        "4c exp4 reference seal")
    failures += f
    if seal is not None and seal.get("failures"):
        failures += [f"4c exp4 reference seal: {m}" for m in seal["failures"]]

    ref_raw_by_traj, ref_tables_by_traj = {}, {}
    for traj in bc.TRAJECTORIES_4C:
        refs = bc.REFS_FOR_4C[traj]
        raw, f = collect_total_4c(lambda refs=refs: collect_4.load_ref_tables_4(root4, refs),
                                  f"4c ref tables {traj}")
        failures += f
        if raw is None:
            continue
        ref_raw_by_traj[traj] = raw
        ref_tables_by_traj[traj] = {ref: rt["sets"] for ref, rt in raw.items()}

    # ---- the discovery gate (design §3.7(1)): 4c's own code, run on
    # Exp 4's committed tables, reproduces the design session's numbers
    # exactly. A mismatch is a failure.
    disc_fn = discovery_check if discovery_check is not None else rk.discovery_set_4c
    discovery, f = collect_total_4c(lambda: disc_fn(root4), "4c discovery gate")
    failures += f
    if discovery is not None:
        bad, f = collect_total_4c(lambda: rk.check_discovery_pins_4c(discovery),
                                  "4c discovery pins")
        failures += f + [f"4c discovery gate: {b}" for b in (bad or [])]

    # ---- the power record (§4): written before the tag, bound by it
    power = None
    power_reproduced = False
    if power_n_sim_expected is None and power_gate == "full":
        # `power_4c` is Task 5's; a missing module is a collected
        # failure, never an ImportError out of `run()`.
        pw4c, f = collect_total_4c(_import_power_4c, "4c power module")
        failures += f
        if pw4c is not None:
            power_n_sim_expected = pw4c.N_SIM_4C
    power_p = power_path_4c(root)
    if not power_p.is_file():
        failures.append(f"4c power record missing ({power_p})")
    else:
        power, f = collect_total_4c(lambda: json.loads(power_p.read_text()), "4c power record")
        failures += f
        if power is not None:
            bad, f = collect_total_4c(
                lambda: _power_record_failures_4c(power, expected_n_sim=power_n_sim_expected,
                                                  power_gate=power_gate),
                "4c power record fields")
            failures += f + [f"4c power record: {b}" for b in (bad or [])]
            if power_gate == "full" and not bad and not f:
                rep, f = collect_total_4c(lambda: _reproduce_power_4c(power),
                                          "4c power record reproduction")
                failures += f
                power_reproduced = bool(rep and rep.get("identical"))
                if rep is not None and not power_reproduced:
                    failures.append(f"4c power record: not reproduced byte for byte "
                                    f"({rep.get('first_diff')})")

    # ---- per trajectory
    series_by_traj, series_incl_by_traj = {}, {}
    run_tables_by_traj, init_units = {}, {}
    gate1_records, gate0_records = {}, {}
    eligibility_by_traj, pia_by_traj = {}, {}
    if not failures:
        for traj in bc.TRAJECTORIES_4C:
            g1_path = battery_4.gate1_path(root, traj)
            g1 = None
            if not g1_path.is_file():
                failures.append(f"4c gate 1 {traj}: record missing ({g1_path})")
            else:
                g1, f = collect_total_4c(lambda p=g1_path: json.loads(p.read_text()),
                                         f"4c gate 1 {traj} record")
                failures += f
                if g1 is not None:
                    bad, f = collect_total_4c(
                        lambda g1=g1, traj=traj: bc.gate1_failures_4c(g1, traj=traj),
                        f"4c gate 1 {traj} failures check")
                    failures += f + [f"4c {b}" for b in (bad or [])]
            gate1_records[traj] = g1

            der, f = collect_total_4c(
                lambda traj=traj: bc.gate1_rederive_4c(root, root4, traj),
                f"4c gate 1 {traj} re-derivation")
            failures += f
            if der is not None:
                if (not all(der["sets_equal"].values())
                        or not all(der["attested_sha_equal"].values())
                        or not der["digest_equal"]):
                    failures.append(f"4c gate 1 {traj}: re-derived bytes disagree")

            if traj == "olmo2_13b":
                # loaded for its pins alone (2l built no 13B reference,
                # so this unit IS gate 1's comparator — B-1)
                _, f = collect_total_4c(
                    lambda: _load_one_unit_4c(root, bc.THIN_ENDPOINT_KEY_4C),
                    "4c thin endpoint unit")
                failures += f

            unit0, f = collect_total_4c(
                lambda traj=traj: _load_one_unit_4c(root, (traj, bc.INIT_STEP_4C)),
                f"4c step 0 unit {traj}")
            failures += f
            if unit0 is not None:
                init_units[traj] = unit0

            tables, f = collect_total_4c(lambda traj=traj: load_run_tables_4c(root, traj),
                                         f"4c run tables {traj}")
            failures += f
            if tables is None or rung_sets.get(traj) is None or traj not in ref_tables_by_traj:
                continue
            run_tables_by_traj[traj] = tables

            if unit0 is not None:
                g0, f = collect_total_4c(
                    lambda traj=traj, unit0=unit0, tables=tables: gate0_4c(
                        root, traj, ref_tables_by_traj[traj], unit0,
                        tables[bc.ENDPOINT_STEP_4C[traj]]),
                    f"4c gate 0 {traj}")
                failures += f
                gate0_records[traj] = g0
                if g0 is not None and not g0["pass"]:
                    failures.append(
                        f"4c gate 0 {traj}: the instrument does not see training (step 0 below "
                        f"the endpoint on {g0['fraction_below']:.3f} of cells, need "
                        f"≥ {a4.GATE0_MIN_FRACTION_4:.2f})")

            series, f = collect_total_4c(
                lambda traj=traj, tables=tables: rk.alignment_series_4c(
                    tables, ref_tables_by_traj[traj], steps=list(bc.GRID_4C[traj])),
                f"4c alignment series {traj}")
            failures += f
            if series is not None:
                series_by_traj[traj] = series

            # S4's inputs: Exp 4's own instrument (site 0 included).
            series_incl, f = collect_total_4c(
                lambda traj=traj, tables=tables: rk.alignment_series_4c(
                    tables, ref_tables_by_traj[traj], steps=list(bc.GRID_4C[traj]),
                    excluded_sites=()),
                f"4c alignment series (site 0 included) {traj}")
            failures += f
            if series_incl is not None:
                series_incl_by_traj[traj] = series_incl

            unit_t1 = tables[bc.FIRST_STEP_4C[traj]]
            unit_end = tables[bc.ENDPOINT_STEP_4C[traj]]
            elig, f = collect_total_4c(
                lambda traj=traj, unit_t1=unit_t1, unit_end=unit_end: eligibility_4c(
                    root, traj, ref_tables_by_traj[traj], unit_t1, unit_end, rung_sets[traj]),
                f"4c eligibility (S4) {traj}")
            failures += f
            if elig is not None:
                eligibility_by_traj[traj] = elig
            pia, f = collect_total_4c(
                lambda traj=traj, unit_t1=unit_t1, unit_end=unit_end: {
                    "t1": a4.per_item_alignment_4(unit_t1, ref_tables_by_traj[traj],
                                                  unit_t1["record"]["pairing"]),
                    "end": a4.per_item_alignment_4(unit_end, ref_tables_by_traj[traj],
                                                   unit_end["record"]["pairing"])},
                f"4c per-item alignment (S4) {traj}")
            failures += f
            if pia is not None:
                pia_by_traj[traj] = pia

    # ---- cells, primary, placebo, modifier, tree, calibration
    cells = []
    if not failures and len(series_by_traj) == len(bc.TRAJECTORIES_4C):
        got, f = collect_total_4c(lambda: rk.cells_4c(series_by_traj, rung_sets), "4c cells")
        failures += f
        cells = got or []
        if not cells:
            failures.append("4c cells: no rising task has a pre-clear window")

    primary, placebo, modifier, calibration, gate7 = None, None, None, None, None
    if not failures and cells:
        primary, f = collect_total_4c(lambda: primary_4c(cells, n_boot=n_boot, seed=SEED_4C),
                                      "4c primary")
        failures += f
        placebo, f = collect_total_4c(
            lambda: rk.placebo_4c(series_by_traj, rung_sets, cells, B=B, seed=SEED_4C),
            "4c placebo")
        failures += f
        modifier, f = collect_total_4c(lambda: rk.type_modifier_4c(cells), "4c type modifier")
        failures += f
        gate7, f = collect_total_4c(lambda: gate7_ties_4c(cells), "4c gate 7 ties")
        failures += f

    if not failures and primary is None:
        failures.append("4c primary: no primary statistic was produced")
    # A PROVISIONAL reading, used only to pick the calibration read's
    # deciding bar (§3.6: alpha for REPLICATES, the marginal bar
    # otherwise). The tree that DECIDES is recomputed below, after
    # every remaining step that can append to `failures` — I-1.
    tree = rk.verdict_tree_4c(failures, primary or {})

    if not failures and placebo is not None:
        cal, f = collect_total_4c(lambda: rk.calibration_read_4c(placebo, tree["verdict"]),
                                  "4c calibration read")
        failures += f
        calibration = {"failed": f[0]} if f else cal

    # ---- secondaries (a refusal degrades the block, never the verdict)
    secondaries = {}
    if not failures:
        def _sec(name, thunk):
            val, f_ = collect_total_4c(thunk, f"4c {name}")
            secondaries[name] = {"failed": f_[0]} if f_ else val

        _sec("S1", lambda: s1_per_run_4c(cells, n_boot=n_boot, seed=SEED_4C))
        _sec("S2", lambda: s2_strata_4c(cells, discovery))
        _sec("S3", lambda: s3_window_mean_4c(series_by_traj, rung_sets))
        s4 = None

        def _s4():
            nonlocal s4
            s4 = s4_continuity_4c(series_incl_by_traj, rung_sets, eligibility_by_traj,
                                  pia_by_traj, n_boot=n_boot, B=B, seed=SEED_4C)
            return s4
        _sec("S4", _s4)
        _sec("S5", lambda: rk.within_riser_4c(series_by_traj, rung_sets))
        _sec("S6", lambda: s6_pooled_4c(cells, discovery))
        _sec("S7", lambda: rk.never_performing_type_check_4c(series_by_traj, rung_sets))
        _sec("S8", lambda: s8_levels_4c(root, series_by_traj, init_units, ref_tables_by_traj,
                                        ref_raw_by_traj))
        _sec("S9", lambda: s9_question_end_4c(root, root4, run_tables_by_traj, ref_raw_by_traj,
                                              rung_sets))
        _sec("S10", lambda: s10_texture_4c(s4, series_incl_by_traj, rung_sets))

    # ---- the import surface again, at EXIT (2j F-1): a secondary may
    # have imported something the entry check never saw.
    if not failures:
        _, f = collect_total_4c(check_imports_4c if imports_pinned else (lambda: None),
                                "4c import surface (exit)")
        failures += f

    # I-1: the tree that decides is computed HERE, after the exit import
    # check and after every `_sec` block — the last steps that can append
    # to `failures`. Computed any earlier, a failing exit pin would land
    # in `failures` and in `referents.failures` while the verdict still
    # read REPLICATES, with `pins_active["import_surface"]` True beside
    # it: the one shape 2j's lesson exists to prevent. The calibration
    # read follows the same rule — a refusal produced no world, so it
    # carries no deciding bar. Exp 4's frozen analyzer has the earlier
    # ordering (`analyze_4.py:2322` against its exit check at `:2422`);
    # that is disclosed here, not edited.
    tree = rk.verdict_tree_4c(failures, primary or {})
    if tree["verdict"] == REFUSAL_WORLD_4C:
        calibration = None

    pins_active = {
        "frozen_modules": frozen_check is None,
        "import_surface": bool(imports_pinned),
        "referent_manifest": referent_manifest_ok,
        "prereg_binding": tag_exists is None and blob_sha is None,
        "seal_binding": blobs_bound is None,
        "discovery_gate": discovery_check is None,
        "power_gate": power_gate,
        "power_reproduced": bool(power_reproduced),
        "power_n_sim_expected": power_n_sim_expected,
        "power_n_sim_injected": power_n_sim_injected,
        "threads_pinned": _threads_4.threads_pinned_4(),
        "threads_pinned_before_numpy": bool(_threads_4.PINNED_BEFORE_NUMPY_4),
        "numpy_version": np.__version__,
    }

    v = verdict_4c(failures=failures, tree=tree, primary=primary, placebo=placebo,
                   modifier=modifier, calibration=calibration, cells=cells,
                   rung_sets_by_traj=rung_sets, gate0_records=gate0_records,
                   gate1_records=gate1_records, gate7=gate7, discovery=discovery, power=power,
                   secondaries=secondaries, pins_active=pins_active, n_boot=n_boot, B=B)
    v = a4._jsonify_4(v)

    if write:
        out_v = Path(out_path) if out_path else battery_4.verdict_path(root)
        out_txt = battery_4.verdict_txt_path(root)
        out_v.parent.mkdir(parents=True, exist_ok=True)
        out_v.write_text(json.dumps(v, indent=1, allow_nan=False))
        out_txt.write_text(write_verdict_txt_4c(v))
    return v


def _power_record_failures_4c(power, *, expected_n_sim, power_gate) -> list:
    """The power record's own fields (§4): the tag it was written
    under, the declaration (one of the two §4 admits), the simulation
    count, and — when `power_4c` is available — the cell structure's
    sha against the LIVE structure, so a structure that changed after
    the tag cannot pass unnoticed."""
    bad = []
    if not isinstance(power, dict):
        return [f"the record is a {type(power).__name__}, not an object"]
    if power.get("prereg_tag") != bc.PREREG_TAG_4C:
        bad.append(f"prereg_tag {power.get('prereg_tag')!r} != {bc.PREREG_TAG_4C!r}")
    if power.get("declaration") not in POWER_DECLARATIONS_4C:
        bad.append(f"declaration {power.get('declaration')!r} is not one of "
                   f"{list(POWER_DECLARATIONS_4C)}")
    if expected_n_sim is not None and int(power.get("n_sim", -1)) != int(expected_n_sim):
        bad.append(f"n_sim {power.get('n_sim')!r} != expected {expected_n_sim}")
    if power_gate == "full":
        from experiments.exp4c import power_4c as pw4c
        structure = pw4c.cell_structure_4c()
        want = pw4c.structure_sha256_4c(structure)
        if power.get("cells_sha256") != want:
            bad.append(f"cells_sha256 {power.get('cells_sha256')!r} != the live cell "
                       f"structure's {want}")
    return bad


def _reproduce_power_4c(power) -> dict:
    """Task 5's byte reproduction: `power_4c.compute` re-run at the
    record's own `n_sim`/`seed` must produce the same record. The key
    SETS are asserted equal first — fix round 2 finding 5: comparing
    only the keys `rec2` happens to have would let a key present in
    the committed record but absent from `compute`'s live output (or
    vice versa) pass silently."""
    from experiments.exp4c import power_4c as pw4c
    rec2 = pw4c.compute(pw4c.cell_structure_4c(), n_sim=int(power["n_sim"]),
                        seed=int(power["seed"]))
    rec2["prereg_tag"] = power.get("prereg_tag")
    extra = sorted(set(power) - set(rec2))
    missing = sorted(set(rec2) - set(power))
    assert not extra and not missing, (
        f"power record key set mismatch: extra in committed {extra}, missing from committed "
        f"{missing}")
    a_s = json.dumps(rec2, sort_keys=True)
    b_s = json.dumps(power, sort_keys=True)
    identical = a_s == b_s
    first_diff = None
    if not identical:
        for k in sorted(rec2):
            if json.dumps(rec2[k], sort_keys=True) != json.dumps(power.get(k), sort_keys=True):
                first_diff = k
                break
    return {"identical": identical, "first_diff": first_diff}


if __name__ == "__main__":
    result = run(write=True)
    print(f"verdict: {result['verdict']}")
    print(result["reason"])
