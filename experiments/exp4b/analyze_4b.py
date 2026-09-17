# experiments/exp4b/analyze_4b.py
"""Experiment 4b's analyzer (design `experiment-4b-design.md` §3.6-
§3.7, §5, §6; plan Task 5): the five known-answer gates against Exp
4's committed bytes, the placebo null and its calibration of T_4, S1-
S8, the tree, and `run()` -- the whole verdict path from Exp 4's
closed tree to a written `verdict.json`/`VERDICT.txt`.

Every measurement primitive is Exp 4's own or `placebo_4b`/
`power_ext_4b`/`levels_4b`'s (Tasks 2-4), called here, never
reimplemented: `analyze_4.collect_total_4/alignment_series_4/trend_4/
excess_4/cells_4/primary_4/eligibility_table_4/lambda_hat_4/gate0_4/
load_stage_tables_4/load_sweep_tables_4/_load_one_unit_4/_jsonify_4/
_compare_eligibility_4/_git_sha_4`; `battery_4b`'s Exp-4 record
loaders and binding; `placebo_4b`'s null/calibration/S3-S5/S8;
`power_ext_4b`'s gate (4) and S1's extension arms; `levels_4b`'s S6.
This module only wires and gates.

Zero model contact; no torch import. Failure messages here are
prefixed "4b "."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

EXP4B = Path(__file__).resolve().parent
EXPERIMENTS = EXP4B.parent
REPO = EXPERIMENTS.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

# Design §3.2 / build constraint: the BLAS thread pool is sized when
# numpy is first imported -- pinned before numpy (and before every
# `experiments.*` import that pulls numpy in transitively), exactly as
# `analyze_4.py` and every Task 2-4 module in this experiment do.
from experiments.exp4 import _threads_4  # noqa: E402,F401

import numpy as np  # noqa: E402

from experiments.exp2d import battery_2d as bt  # noqa: E402
from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp4 import analyze_4 as an  # noqa: E402
from experiments.exp4 import battery_4  # noqa: E402
from experiments.exp4 import collect_4  # noqa: E402
from experiments.exp4 import power_4 as pw4  # noqa: E402
from experiments.exp4b import battery_4b  # noqa: E402
from experiments.exp4b import levels_4b  # noqa: E402
from experiments.exp4b import placebo_4b  # noqa: E402
from experiments.exp4b import power_ext_4b  # noqa: E402

REFERENTS_PATH_4B = EXP4B / "referents_4b.json"
# Measured once against the real, closed exp4 tree (Task 5; see
# PROGRESS.md) -- the ONE hash walk this task performs before the tag,
# the exact analogue of `analyze_4.REFERENTS_4_SHA256`.
REFERENTS_4B_SHA256 = "6f83de15ffa13ec4e78c66b1c63a4abf24dc91392bf602ba30d5d2e85c621d36"
# Filled by Task 6 (`import_scan_4b.py`, run on the real closed exp4
# tree): the residual import surface -- every non-test module inside
# experiments/exp4b that is not one of the five INSTRUMENT_BLOBS_4B
# files (`__init__.py`, `make_referents_4b.py`, `verify_referents_4b.py`
# -- pulled in by `run()`'s own `make_referents_4b` import and
# `import_scan_4b.py`'s stage-tool pull-in) -- exactly `analyze_4.
# IMPORTED_SHA256_4`'s own pattern one experiment over.
IMPORTED_SHA256_4B = {
    REPO / "experiments/exp4b/__init__.py":
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    REPO / "experiments/exp4b/make_referents_4b.py":
        "043f793abf58290842b9c6a6f0383472430ae3b16dbfd77f6f58e90fb6199fec",
    # Re-pinned at the ADVERSARIAL FREEZE after cold check 13 (F-1's
    # gate-6 re-assertion) was added to `verify_referents_4b.py`; the
    # pin's own drift test caught the stale hash before the re-pin,
    # exactly as the fix wave's did.
    REPO / "experiments/exp4b/verify_referents_4b.py":
        "077a6382a58d2b1c8923ee129d073e7e8684049dffd0366e9aeae4bf450d5383",
}

# Design §2's disclosure paragraph, first sentence, quoted verbatim
# (checklist obligation: every licensed sentence carries it).
KNOWN_INPUT_CAVEAT_4B = "Every input is committed and known, INCLUDING TO THE DESIGNER."

# Ruled addition r1 (final review): design §6's licence sentence for
# each reached world, quoted (lightly normalized -- '§' kept, quote
# marks straightened, symbols spelled out) rather than paraphrased, so
# a reader of VERDICT.txt/verdict.json sees the SAME words the design
# doc licenses. `run()` selects one of these four by `tree["verdict"]`
# and prints it beside the CALIBRATED-only alpha_placebo sub-clause
# (`LICENCE_ALPHA_PLACEBO_CLAUSE_4B`) and the naming rule's outcome.
LICENCE_4B = {
    "CALIBRATED": (
        "design §6 CALIBRATED: the essay's convergence sentence loses its bound -- "
        "'bounded below rather than measured' and 'above the selection-inflated null' are "
        "replaced by 'above the null built from the flat tasks' own drift under the same "
        "selection, p = p_cal, a lead of T* (interval) beyond it' -- and the scoreboard "
        "sentence follows; the lens reading of Huh et al. is a measurement at task grain with "
        "a calibrated p."
    ),
    "MARGINAL": (
        "design §6 MARGINAL: the sentence reads 'above the drift null at p = p_cal, short of "
        "the program's alpha; the lead T* (interval)'; the bound is replaced by a measured "
        "margin, no more. The scoreboard says 'marginal'."
    ),
    "NOT-DISTINGUISHABLE": (
        "design §6 NOT-DISTINGUISHABLE: Exp 4's measurement is DEMOTED in the essay -- the "
        "convergence paragraph keeps the disclosure that the test ran and states that the "
        "task-specific lead did not separate from the flat tasks' drift under the same "
        "selection (p_cal, T* with its interval covering zero); the scoreboard sentence is "
        "rewritten to say so; the lens claim's task-grain measurement retreats to Huh et al.'s "
        "global result plus the disclosure; `experiments.md` records the demotion beside Exp 4's "
        "section. What survives in every world: the construction account's cell stays excluded "
        "by Exp 4's own sign-flip reading (T .61 at p+ 4.9e-4 against phi ~ 0), and the sentence "
        "says so -- 'the agreement did not arrive with performance; whether it led the general "
        "drift is not distinguishable at this resolution'."
    ),
    "INSUFFICIENT_DATA": "design §6: nothing changes in the essay; the reason is ledgered.",
}

# FREEZE NB-2 minor: design §6's LAST bullet ("Any world"), quoted --
# it applies whatever cell is reached and was missing from the licence
# block entirely.
LICENCE_ANY_WORLD_4B = (
    "design §6 Any world: S1-S8 in full in `experiments.md`; S6's site-0-excluded ladder "
    "replaces Exp 4's frozen S3 in the program record as the reading of the size axis, with the "
    "frozen number kept beside it as what the instrument printed; the known-input caveat "
    "verbatim in every sentence."
)

# FREEZE F-3: design §6's NOT-DISTINGUISHABLE sentence asserts "T* with
# its interval covering zero" as a matter of fact. It is not one: the
# interval is [T4 - Q.975, T4 - Q.025], so its UPPER end is negative
# whenever T4 sits below the placebo null's 2.5th percentile -- exactly
# the direction the construction account predicts -- and the world is
# still NOT-DISTINGUISHABLE (p_cal >= .05). The analyzer checks the
# clause instead of printing it unchecked, and names the cell §6 did
# not: the licence block carries `interval_covers_zero` and, when it is
# False, this sentence beside the quoted one.
LICENCE_INTERVAL_BELOW_NULL_4B = (
    "CELL NOT NAMED IN design §6: the quoted sentence's parenthetical does not hold on this "
    "reading -- T* 's placebo interval lies entirely BELOW zero (T_4 sits under the placebo "
    "null's 2.5th percentile, p_low printed beside p_cal), so the flat rungs' own drift EXCEEDS "
    "the task-specific lead at this resolution. The demotion §6 prescribes still governs; the "
    "'interval covering zero' clause must not be written, and which sentence the essay takes "
    "instead is Michael's call (a freeze disclosure, not a licence this analyzer grants)."
)

# design §6 CALIBRATED's own alpha_placebo sub-branch: keyed by
# `alpha_placebo < LICENCE_TRAJ_ALPHA_4b's own .05 bar` (an.
# LICENCE_TRAJ_ALPHA_4, m4's own constant -- the same bar the naming
# rule uses, design §6 never names a second one).
LICENCE_ALPHA_PLACEBO_CLAUSE_4B = {
    True: "alpha_placebo < .05: the Exp 4 licence is claimed in full.",
    False: ("alpha_placebo >= .05: the sentence adds that the preregistered decision rule's own "
           "false-positive rate at this scatter was alpha_placebo, and rests on p_cal."),
}

# FREEZE NB-2: design §5 S1's reading is one-sided; these are the two
# names §5 gives plus the two cells it does not license. The rule is in
# `run()._s1`; the S3 conjunct's own rule is
# `placebo_4b.s3_pooled_rising_4b`'s.
S1_READINGS_4B = ("same shape", "drift-like", "above-iid", "below-iid, S3 not rising")

_LITERAL = object()


def _scipy_version_4b():
    """scipy's version, for `pins_active`'s stack disclosure -- read
    through `levels_4b`'s own already-imported `scipy.stats` rather
    than a fresh import, `None` if it is somehow absent (never a
    raise: this is a disclosure field, not a gate)."""
    try:
        import scipy
        return scipy.__version__
    except Exception:  # noqa: BLE001
        return None


def collect_total_4b(thunk, label):
    """= `analyze_4.collect_total_4` (2h's widened surface plus
    `zipfile.BadZipFile`/`KeyError`/`OSError`) -- exp4b reads the exact
    same committed-file shapes (npz set tables, JSON records) exp4
    reads, so the same totality surface applies unchanged."""
    return an.collect_total_4(thunk, label)


def check_imports_4b() -> None:
    """2j F-1 / `analyze_4.check_imports_4`'s shape, widened to cover
    BOTH instruments' residual surfaces (ambiguity resolution 1):
    every module under `experiments/` this process has imported
    (excluding `tests/`) must be covered by `battery_4.
    FROZEN_SHA256_4` (everything outside exp4/exp4b), `battery_4.
    INSTRUMENT_BLOBS_4` (exp4's own instrument, tag-bound at
    `exp4-closed`), `battery_4b.EXP4_CLOSED_SHA256_4B` (exp4's seven
    files, re-pinned here too since exp4b imports them as modules),
    `analyze_4.IMPORTED_SHA256_4` (exp4's own residual -- DRIFT-CHECKED
    here too, not merely membership-covered: final review Important 1
    found that a drifted file among exp4's five residual pins, e.g.
    `_threads_4.py`, the BLAS thread pin, would have passed silently,
    since membership in `covered` never compares a file's current hash
    against its pin), `battery_4b.
    INSTRUMENT_BLOBS_4B` (exp4b's own instrument, tag-bound at
    `exp4b-preregistered`), or `IMPORTED_SHA256_4B` (exp4b's own
    residual, below -- filled by Task 6's `import_scan_4b.py`;
    `run()` only calls this function when `imports_pinned` is
    truthy)."""
    if IMPORTED_SHA256_4B is None:
        raise RuntimeError("4b: IMPORTED_SHA256_4B is None -- the import surface is not pinned "
                           "(build incomplete)")
    covered = {str(Path(p).resolve()) for p in battery_4.FROZEN_SHA256_4}
    covered |= {str((battery_4.REPO / rel).resolve()) for rel in battery_4.INSTRUMENT_BLOBS_4}
    covered |= {str((battery_4b.REPO / rel).resolve()) for rel in battery_4b.EXP4_CLOSED_SHA256_4B}
    covered |= {str((battery_4b.REPO / rel).resolve()) for rel in battery_4b.INSTRUMENT_BLOBS_4B}
    pinned = {str(Path(p).resolve()): v for p, v in IMPORTED_SHA256_4B.items()}
    # Important 1: fold exp4's own residual pins into `pinned` too, so
    # they are drift-checked exactly like exp4b's own -- previously
    # only added to `covered` (membership only, no hash comparison).
    pinned |= {str(Path(p).resolve()): v for p, v in (an.IMPORTED_SHA256_4 or {}).items()}
    drifted, unpinned = [], []
    for p, want in sorted(pinned.items()):
        pp = Path(p)
        if not pp.is_file() or bg.sha256_file(pp) != want:
            drifted.append(f"(pin) -> {p}")
    exp_root = str((battery_4b.REPO / "experiments").resolve())
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
        raise RuntimeError("4b: unpinned module on the import surface: " + "; ".join(sorted(unpinned)))
    if drifted:
        raise RuntimeError("4b: imported module drifted from its pin: " + "; ".join(sorted(drifted)))


# ------------------------------------------------------------------ gates
#
# Each function below is a COLD, standalone re-derivation -- it raises
# naturally on a bad input (no `collect_total_4b` wrapping inside); the
# wrapping happens once at each of `run()`'s two call sites (production)
# and `verify_referents_4b.py` calls these SAME functions directly on
# the real, closed tree (a cold re-assertion, exp4's own verify_
# referents_4.py check 12 pattern) rather than running the whole
# pipeline a second time.


def gate1_rederive_4b(series_by_traj, rung_sets, elig4, cells4, T4) -> dict:
    """design §3.6 gate (1): T_4 and the 26 cells re-derived through
    `alignment_series_4 -> trend_4 -> excess_4 -> cells_4` (with the
    COMMITTED eligibility table) `-> primary_4` at `n_boot=N_BOOT_4`,
    seed 0, equal `verdict.json`'s `primary.T` bit for bit and the
    cells equal on (traj, rung, phi, t_clear)."""
    rs_avail = {t: rung_sets[t] for t in series_by_traj if rung_sets.get(t) is not None}
    got_cells = an.cells_4(series_by_traj, rs_avail, elig4)
    primary1 = an.primary_4(got_cells, n_boot=an.N_BOOT_4, seed=0)
    t_match = primary1["T"] == T4
    got_norm = sorted((c["traj"], c["rung"], c["phi"], c["t_clear"]) for c in got_cells)
    want_norm = sorted((c["traj"], c["rung"], c["phi"], c["t_clear"]) for c in cells4)
    cells_match = got_norm == want_norm
    return {"pass": t_match and cells_match, "T_rederived": primary1["T"], "T_committed": T4,
           "t_match": t_match, "cells_match": cells_match,
           "n_cells_rederived": len(got_cells), "n_cells_committed": len(cells4)}


def gate2_rederive_4b(root4, elig4) -> dict:
    """gate (2): the eligibility table re-derived through
    `eligibility_table_4` equals the committed `eligibility_4.json`
    (Exp 4's own check, `_compare_eligibility_4`, repeated)."""
    recomputed = an.eligibility_table_4(root4)
    diffs = an._compare_eligibility_4(elig4, recomputed)
    return {"pass": not diffs, "diffs": diffs[:5]}


def gate3_rederive_4b(series_by_traj, rung_sets, elig4, v4) -> dict:
    """gate (3): lambda_hat per trajectory re-derived through
    `lambda_hat_4` equals the committed
    `calibration.per_traj[*].lambda_hat` (exact)."""
    cal_re = an.lambda_hat_4(series_by_traj, rung_sets, elig4)
    committed_cal = (v4.get("calibration") or {}).get("per_traj") or {}
    diffs, lambda_by_traj = [], {}
    for traj, block in cal_re["per_traj"].items():
        want = (committed_cal.get(traj) or {}).get("lambda_hat")
        got = block.get("lambda_hat")
        lambda_by_traj[traj] = got
        if got != want:
            diffs.append(f"{traj}: {got!r} != {want!r}")
    return {"pass": not diffs and bool(cal_re["per_traj"]), "diffs": diffs,
           "lambda_by_traj": lambda_by_traj}


def interval_covers_zero_4b(interval):
    """FREEZE F-3: design §6's NOT-DISTINGUISHABLE sentence asserts
    that T*'s placebo interval covers zero. `None` when there is no
    interval; otherwise the checked fact. The interval is
    `[T4 - Q.975(T_b), T4 - Q.025(T_b)]`, so its UPPER end is negative
    exactly when T_4 sits below the placebo null's 2.5th percentile --
    the construction account's own direction, and a world that is
    still NOT-DISTINGUISHABLE."""
    if interval is None:
        return None
    return bool(interval[0] <= 0.0 <= interval[1])


def s1_reading_4b(placebo_null_mean, iid_null_mean, s3) -> dict:
    """FREEZE NB-2 (supersedes the fix wave's r2, which was
    two-sided): design §5 S1's reading rule, exactly as §5 writes it --
    "same shape (means within .05) or drift-like (placebo mean BELOW
    the iid mean by more than .05, WITH the per-index table S3
    rising)".

    r2 labelled every |difference| > .05 "drift-like", which would
    have read a placebo mean ABOVE the iid mean -- the opposite
    direction, no accumulating drift at all -- as drift, and dropped
    the S3 conjunct entirely. Four labels (`S1_READINGS_4B`): §5's two,
    plus the two cells §5 does not license, named rather than folded
    into one of its own ("above-iid"; "below-iid, S3 not rising").
    `None` only when a null mean is unavailable. The S3 conjunct's own
    rule is `placebo_4b.s3_pooled_rising_4b`'s, stated in its
    docstring; `S1_SHAPE_TOL_4B` (.05) is §5's own tolerance, which §5
    uses for both halves and names no second one for."""
    rising = placebo_4b.s3_pooled_rising_4b(s3)
    tol = placebo_4b.S1_SHAPE_TOL_4B
    if placebo_null_mean is None or iid_null_mean is None:
        reading = None
    elif abs(placebo_null_mean - iid_null_mean) <= tol:
        reading = "same shape"
    elif placebo_null_mean > iid_null_mean + tol:
        reading = "above-iid"
    elif rising.get("rising"):
        reading = "drift-like"
    else:
        reading = "below-iid, S3 not rising"
    return {"reading": reading, "readings": list(S1_READINGS_4B), "shape_tol": tol,
            "s3_rising": rising}


def gate6_endpoint_identity_4b(root4) -> dict:
    """FREEZE F-1 (design §3.6's "the exact analogue of Exp 4's rule",
    attacked): the placebo screen's ENDPOINT input is a DIFFERENT FILE
    from the real rule's.

    `eligibility_table_4` -- the rule 4b's placebo eligibility claims
    to be the analogue of -- reads its endpoint per-item alignments
    from the REFERENCE-stage unit `reference/endpoint_<traj>/`. The
    placebo pool reads them from the SWEEP unit `sweep/<traj>/
    step<endpoint>/`, because `run()` feeds `placebo_pool_4b` the
    alignment series' OWN `per_item` arrays (the Task 2 note: the
    series/pia consistency refusal requires it). The two units are the
    same checkpoint computed twice, and their byte identity is what
    makes the placebo screen the analogue -- but nothing in exp4b ever
    measured it: `gate1.json` is sha-pinned in the manifest and never
    READ, and no exp4b gate compares the two directories to each
    other. Exp 4's own closed analyzer did measure it (`analyze_4.py`'s
    "4 gate 1 <traj> re-derivation", gating on all four agreements), so
    on the committed tree this is an INHERITED measurement over
    manifest-pinned bytes; re-asserted here so 4b's own placebo input
    provenance is measured rather than inherited (2i F-1 / 3d /
    exp4 F-1's attested-vs-measured lineage).

    `battery_4.gate1_rederive_4` is Exp 4's own frozen byte
    comparison, called unmodified: `sets_equal` per rung (npz bytes),
    `activation_sha_equal`/`attested_sha_equal` per rung (the two
    records' own shas), `tensor_digest` equal. All four required, as
    Exp 4 required them. ~0.01 s warm for 4 x 34 x 2 files."""
    detail, bad = {}, []
    for traj in battery_4.TRAJECTORIES_4:
        g = battery_4.gate1_rederive_4(root4, traj)
        sets_ok = all(g["sets_equal"].values())
        act_ok = all(g["activation_sha_equal"].values())
        att_ok = all(g["attested_sha_equal"].values())
        detail[traj] = {"sets_equal": bool(sets_ok), "activation_sha_equal": bool(act_ok),
                        "attested_sha_equal": bool(att_ok),
                        "digest_equal": bool(g["digest_equal"]), "n_rungs": g["n_rungs"],
                        "n_sets_differ": sum(1 for v in g["sets_equal"].values() if not v)}
        if not (sets_ok and act_ok and att_ok and g["digest_equal"]):
            bad.append(f"{traj}: reference/endpoint_{traj} and sweep/{traj}/step<endpoint> "
                       f"disagree ({detail[traj]})")
    return {"pass": not bad, "per_traj": detail, "bad": bad,
            "n_rungs_checked": sum(d["n_rungs"] for d in detail.values())}


def gate5_rederive_4b(root4, stage_tables_4, v4) -> dict:
    """gate (5): `gate0_4` (site 0 already excluded, `GATE0_
    EXCLUDED_SITES_4`) re-run from the committed reference tables
    equals the committed `gate0[*].fraction_below` (exact), per
    trajectory."""
    detail, ok_all = {}, True
    for traj in battery_4.TRAJECTORIES_4:
        refs = battery_4.REFS_FOR_4[traj]
        ref_tables_raw = collect_4.load_ref_tables_4(root4, refs)
        ref_tables = {ref: rt["sets"] for ref, rt in ref_tables_raw.items()}
        g0 = an.gate0_4(root4, traj, ref_tables, stage_tables_4)
        want = ((v4.get("gate0") or {}).get(traj) or {}).get("fraction_below")
        got = g0["fraction_below"]
        detail[traj] = {"got": got, "want": want}
        if got != want:
            ok_all = False
    return {"pass": ok_all, "per_traj": detail}


# --------------------------------------------------------- S7 (clears-and-stays)
#
# Finding 5 (controller ruling): S7(a) must be calibrated against the
# MATCHED null, not the primary null -- the clears-and-stays cells ARE
# re-derivable (Exp 4's own `analyze_4.run()._clears_and_stays_primary`,
# `experiments/exp4/analyze_4.py` around line 2378, read and replicated
# here in three composable steps rather than copied as one block, never
# reimplementing `cells_4`/`primary_4` themselves).


def clears_and_stays_rung_sets_4b(rung_sets: dict) -> dict:
    """Exp 4's own `_clears_and_stays_primary`'s rung-set transform:
    for each trajectory, `t_clear` is replaced by `clears_and_stays`
    wherever the latter is not `None` (a rung whose significance
    reverted keeps its ordinary, first-rise `t_clear`)."""
    rs_cas = {}
    for traj, rs in rung_sets.items():
        if rs is None:
            continue
        cas = rs["clears_and_stays"]
        rs_cas[traj] = {**rs, "t_clear": {r: (cas[r] if cas.get(r) is not None else rs["t_clear"].get(r))
                                          for r in rs["t_clear"]}}
    return rs_cas


def clears_and_stays_eligibility_4b(elig4: dict, rs_cas: dict) -> dict:
    """Exp 4's own `_clears_and_stays_primary`'s eligibility re-keying:
    every rung's `t_clear`/`t_clear_index` swapped to the clears-and-
    stays position; every other eligibility field (`eligible`, `se`,
    `x_end`, `reason`) untouched -- eligibility is not recomputed for
    the new clear position, matching Exp 4's own sensitivity exactly."""
    elig_cas = {}
    for traj, block in elig4.items():
        rs2 = rs_cas.get(traj)
        if rs2 is None:
            continue
        newR = {}
        for r, e in (block.get("R") or {}).items():
            steps = list(battery_4.GRID_4[traj])
            tclear = rs2["t_clear"].get(r)
            tci = steps.index(tclear) if tclear is not None else None
            e2 = dict(e); e2["t_clear"] = tclear; e2["t_clear_index"] = tci
            newR[r] = e2
        elig_cas[traj] = {**block, "R": newR}
    return elig_cas


def clears_and_stays_cells_4b(series_by_traj: dict, rung_sets: dict, elig4: dict) -> list:
    """The clears-and-stays cells, via `analyze_4.cells_4` unchanged
    (never reimplemented) -- Exp 4's own `_clears_and_stays_primary`'s
    cell-building half, composed from the two functions above."""
    rs_cas = clears_and_stays_rung_sets_4b(rung_sets)
    elig_cas = clears_and_stays_eligibility_4b(elig4, rs_cas)
    series_cas = {t: series_by_traj[t] for t in series_by_traj if t in rs_cas}
    return an.cells_4(series_cas, rs_cas, elig_cas)


def clears_and_stays_design_4b(cas_cells: list) -> dict:
    """`battery_4b.real_design_4b`'s input needs `t_clear_index`,
    which `cells_4`'s own cell shape does not carry (it carries
    `t_clear`/`t_minus` instead) -- added here by the same grid lookup
    `cells_from_verdict_4b` uses, never retyped."""
    augmented = []
    for c in cas_cells:
        grid = list(battery_4.GRID_4[c["traj"]])
        augmented.append({**c, "t_clear_index": grid.index(c["t_clear"])})
    return battery_4b.real_design_4b(augmented)


def best_site_mean_phi_4b(v4: dict, cells4: list) -> dict:
    """S7(b)'s statistic, extracted standalone (`verify_referents_4b.
    py`'s free known-answer pin calls this directly on the real tree,
    finding 5's own note): the plain mean, over every real cell whose
    trajectory's `S5 <traj>` sensitivity carries a `best_site[rung]
    .phi`, of that phi -- Exp 4's own per-site-best excess reading
    (`s5_site_sensitivities_4`), pooled over cells the same way the
    primary pools phi. Returns `{"T": float | None, "n_cells": int,
    "phis": [...]}`."""
    phis = []
    for traj in battery_4.TRAJECTORIES_4:
        s5_rec = ((v4.get("sensitivities") or {}).get(f"S5 {traj}") or {})
        best_site = s5_rec.get("best_site") or {}
        for c in cells4:
            if c["traj"] != traj:
                continue
            entry = best_site.get(c["rung"])
            if entry and entry.get("phi") is not None:
                phis.append(entry["phi"])
    T = float(np.mean(phis)) if phis else None
    return {"T": T, "n_cells": len(phis), "phis": phis}


# ------------------------------------------------------------------ tree


def verdict_tree_4b(failures, feasibility_ok, p_cal) -> dict:
    """Ambiguity resolution 2: the tree cells are decided by `p_cal`
    only. `failures` (any gate/loader refusal) and the design §4
    feasibility floor (fewer than `MIN_PLACEBO_TOTAL_4B` eligible
    placebo rungs total) both refuse to `INSUFFICIENT_DATA` before
    `p_cal` is ever read."""
    if failures:
        return {"verdict": "INSUFFICIENT_DATA", "reason": "; ".join(failures[:5])}
    if not feasibility_ok:
        return {"verdict": "INSUFFICIENT_DATA",
               "reason": f"4b: fewer than {battery_4b.MIN_PLACEBO_TOTAL_4B} eligible placebo "
                         f"rungs in total across the four trajectories (design §4 floor)"}
    if p_cal is None:
        return {"verdict": "INSUFFICIENT_DATA", "reason": "4b: p_cal not computed"}
    if p_cal < battery_4b.ALPHA_4B:
        return {"verdict": "CALIBRATED", "reason": f"p_cal {p_cal:.4g} < {battery_4b.ALPHA_4B}"}
    if p_cal < battery_4b.MARGINAL_4B:
        return {"verdict": "MARGINAL",
               "reason": f"p_cal {p_cal:.4g} in [{battery_4b.ALPHA_4B}, {battery_4b.MARGINAL_4B})"}
    return {"verdict": "NOT-DISTINGUISHABLE",
           "reason": f"p_cal {p_cal:.4g} >= {battery_4b.MARGINAL_4B}"}


# --------------------------------------------------------------- verdict


def verdict_4b(*, tree, gates, exp4_block, pins_active, primary=None, feasibility=None,
              alpha_placebo=None,
              per_traj=None, per_type=None, licence_naming=None, construction_statement=None,
              licence=None,
              s1=None, s3=None, s4=None, s5=None, s6=None, s7=None, s8=None,
              placebo_record_sha256=None, power_ext_sha256=None) -> dict:
    return {
        "verdict": tree["verdict"],
        "reason": tree["reason"],
        "primary": primary,
        "feasibility": feasibility,
        "alpha_placebo": alpha_placebo,
        "per_traj": per_traj,
        "per_type": per_type,
        "licence_naming": licence_naming,
        "construction_statement": construction_statement,
        "licence": licence,
        "s1": s1, "s3": s3, "s4": s4, "s5": s5, "s6": s6, "s7": s7, "s8": s8,
        "gates": gates,
        "exp4": exp4_block,
        "pins_active": pins_active,
        "git_sha": an._git_sha_4(),
        "placebo_record_sha256": placebo_record_sha256,
        "power_ext_sha256": power_ext_sha256,
        "stack_note": "analysis-only, no model contact -- a calibration of experiment 4's own "
                      "committed bytes against a placebo null built from its own flat rungs",
    }


def _sort_key_4b(k):
    """Numeric-aware sort key for dict keys that may be ints (a fresh
    `v`, e.g. in a hand-built test record) or strings (a `v` that has
    already passed through `_jsonify_4`, which stringifies every dict
    key) -- `write_verdict_txt_4b` reads both."""
    try:
        return (0, int(k))
    except (TypeError, ValueError):
        return (1, str(k))


def write_verdict_txt_4b(v: dict) -> str:
    lines = [f"EXPERIMENT 4B VERDICT: {v['verdict']}", "", v.get("reason") or "", "",
            f"Caveat (design §2, verbatim): {KNOWN_INPUT_CAVEAT_4B}", ""]
    p = v.get("primary")
    if p:
        lines.append(f"Primary: T4={p['T4']} p_cal={p['p_cal']:.4g} p_low={p['p_low']:.4g} "
                    f"T*={p['T_star']:.4f} interval={p['interval']} "
                    f"null_mean={p['null_mean']:.4f} null_sd={p['null_sd']:.4f} "
                    f"q95={p['q95']:.4f} q99={p['q99']:.4f} B={p['B']} n_cells={p['n_cells']}")
        # F-2: p_cal's Monte Carlo resolution against the tree's bars.
        mc = p.get("mc_resolution") or {}
        if mc:
            lines.append(f"  p_cal Monte Carlo SE: {mc.get('p_cal_mc_se')}; "
                        f"bars within 2 SE: {mc.get('within_2_mc_se')}")
            for bar, rec in sorted((mc.get("per_bar") or {}).items()):
                lines.append(f"    bar {bar}: margin={rec.get('margin')} "
                            f"({rec.get('margin_in_mc_se')} MC SE)")
            lines.append(f"  {mc.get('note')}")
        lines.append("")
    feas = v.get("feasibility")
    if feas:
        lines.append(f"Feasibility (design §4): total_eligible={feas.get('total_eligible')} "
                    f"min_required={feas.get('min_required')} floor_ok={feas.get('floor_ok')}")
        for t, rec in sorted((feas.get("per_traj") or {}).items()):
            lines.append(f"  {t}: n_real={rec.get('n_real')} "
                        f"n_eligible_placebo={rec.get('n_eligible_placebo')} "
                        f"deficit={rec.get('deficit')}")
        lines.append("")
    # Finding 6: the calibration line -- alpha_placebo (Exp 4's own
    # LEADS rule's false-positive rate on the real flat-rung scatter)
    # beside S1's alpha_iid/p_iid and the two nulls' mean/SD, side by
    # side (design §3.5's own reading rule: "same shape" if the two
    # means agree within .05).
    ap = v.get("alpha_placebo")
    s1v = v.get("s1")
    if ap or s1v:
        parts = []
        if ap:
            parts.append(f"alpha_placebo={ap.get('alpha_placebo')} "
                        f"(n_batteries={ap.get('n_batteries')}, n_leads={ap.get('n_leads')})")
            # FREEZE disclosure: alpha_placebo's DENOMINATOR is every
            # scored battery, including any that Exp 4's own tree reads
            # NO-CONVERGENCE (fewer than MIN_RUNGS_4 distinct placebo
            # rungs drawn, or fewer than MIN_CELLS_4 cells) and which
            # therefore cannot read LEADS by construction; and the flip
            # regime a battery lands in (exact enumeration at <= 20
            # distinct rungs, sampled above) need not be the real
            # verdict's. Both printed, not assumed uniform.
            parts.append(f"world_counts={ap.get('world_counts')}")
            parts.append(f"flip regime: batteries={ap.get('flip_method_counts')} "
                        f"vs the real verdict's {ap.get('real_regime')}")
        if s1v:
            parts.append(f"alpha_iid={s1v.get('alpha_iid')} p_iid={s1v.get('p_iid')}")
            comp = s1v.get("comparison") or {}
            parts.append(f"placebo null mean/SD={comp.get('placebo_null_mean')}/"
                        f"{comp.get('placebo_null_sd')}")
            parts.append(f"iid null mean/SD={comp.get('iid_null_mean')}/{comp.get('iid_null_sd')}")
            # NB-2: the one-sided §5 S1 label, with its S3 conjunct.
            rising = comp.get("s3_rising") or {}
            parts.append(f"S1 reading (design §5, one-sided)={comp.get('reading')!r} "
                        f"[tol={comp.get('shape_tol')}; S3 rising={rising.get('rising')}, "
                        f"delta={rising.get('delta')} over bins {rising.get('first_bin')}"
                        f"->{rising.get('last_bin')}; one of {comp.get('readings')}]")
        lines.append("Calibration (Exp 4's LEADS rule vs the placebo null vs the iid arm):")
        for part in parts:
            lines.append(f"  {part}")
        lines.append("")
    cs = v.get("construction_statement")
    if cs:
        lines.append(f"Construction account: {cs.get('text')}")
        lines.append("")
    ln = v.get("licence_naming")
    if ln:
        lines.append(f"Licence naming: {ln.get('n')} trajectories at p_cal,M < .05: "
                    f"{ln.get('trajectories')}")
        lines.append(f"  rule: {ln.get('rule')}")
        lines.append("")
    lic = v.get("licence")
    if lic:
        lines.append(f"Licence (design §6, world={lic.get('world')}):")
        lines.append(f"  {lic.get('text')}")
        if lic.get("alpha_placebo_clause"):
            lines.append(f"  {lic['alpha_placebo_clause']}")
        if lic.get("naming_outcome"):
            lines.append(f"  naming: {lic['naming_outcome']}")
        if lic.get("any_world"):
            lines.append(f"  {lic['any_world']}")
        if "interval_covers_zero" in lic:
            lines.append(f"  T* interval covers zero: {lic.get('interval_covers_zero')}")
        if lic.get("unnamed_cell"):
            lines.append(f"  {lic['unnamed_cell']}")
        lines.append("")
    pt = v.get("per_traj") or {}
    if pt:
        lines.append("Per trajectory:")
        for t, rec in sorted(pt.items()):
            lines.append(f"  {t}: T_obs={rec.get('T_obs')} p_cal={rec.get('p_cal')} "
                        f"T*={rec.get('T_star')} n_cells={rec.get('n_cells')}")
        lines.append("")
    pty = v.get("per_type") or {}
    if pty:
        lines.append("Per type:")
        for typ, rec in sorted(pty.items()):
            if rec is None:
                lines.append(f"  {typ}: (no cells)")
            else:
                lines.append(f"  {typ}: T_obs={rec.get('T_obs')} p_cal={rec.get('p_cal')} "
                            f"n_cells={rec.get('n_cells')} reason={rec.get('reason')}")
        lines.append("")
    s3v = v.get("s3")
    if s3v:
        lines.append("S3 -- the null's shape, per (trajectory, clear index):")
        per_traj_c = s3v.get("per_traj_c") or {}
        for t in sorted(per_traj_c):
            for c in sorted(per_traj_c[t], key=_sort_key_4b):
                stat = per_traj_c[t][c]
                lines.append(f"  {t} c={c}: mean={stat.get('mean')} sd={stat.get('sd')} "
                            f"n={stat.get('n')}")
        lines.append("  pooled bins by clear-index fraction:")
        for label, stat in (s3v.get("pooled_bins") or {}).items():
            lines.append(f"    {label}: mean={stat.get('mean')} sd={stat.get('sd')} "
                        f"n={stat.get('n')}")
        lines.append("")
    s5v = v.get("s5")
    if s5v:
        lines.append("S5 -- lag-1 autocorrelation of the flat rungs' excess increments:")
        for t, rec in sorted(s5v.items()):
            lines.append(f"  {t}: mean_of_rungs={rec.get('mean_of_rungs')} pooled={rec.get('pooled')}")
        lines.append("")
    s4v = v.get("s4")
    if s4v:
        pooled = s4v.get("pooled") or {}
        lines.append(f"S4 -- the scatter ratio, pooled: {pooled.get('ratio')} "
                    f"(rising {pooled.get('rms_rising')} / flat {pooled.get('rms_flat')})")
        # NB-1: say WHAT is compared, and print the residual pool-size
        # expectation per trajectory -- the ratio is raw on both sides.
        lines.append(f"  compared: {s4v.get('compared')}")
        for t, rec in sorted((s4v.get("per_traj") or {}).items()):
            lines.append(f"    {t}: ratio={rec.get('ratio')} "
                        f"rms_rising={rec.get('rms_rising')} rms_flat={rec.get('rms_flat')} "
                        f"pool_size_expected_ratio={rec.get('pool_size_expected_ratio')} "
                        f"(n_flat factor {rec.get('loo_scale_factor')}, disclosure only)")
        lines.append("")
    s7v = v.get("s7")
    if s7v:
        # Important 2 (final review): the (b) line used to print
        # best-site phi's p_cal/interval as if it were a calibration --
        # it is read against the PRIMARY placebo null (flat rungs' own
        # best-site series is not available to build a matched one), so
        # only T is printed here, with the mismatch disclosed inline;
        # the record itself (v["s7"]["best_site"]) still carries every
        # field (p_cal/interval included) for anyone reading the JSON.
        lines.append(f"S7 -- clears-and-stays T={((s7v.get('clears_and_stays') or {}).get('T'))} "
                    f"p_cal={((s7v.get('clears_and_stays') or {}).get('p_cal'))}; "
                    f"best-site T={((s7v.get('best_site') or {}).get('T'))} "
                    f"[mismatched construction -- the best-site series is not available for "
                    f"flat rungs; not a calibration]")
        lines.append("")
    s6v = v.get("s6")
    if s6v:
        lines.append(f"S6 present: {sorted(k for k in s6v if s6v.get(k) is not None)}")
        lines.append("")
    lines.append("Gates:")
    for n in ("1", "2", "3", "4", "5", "6"):
        g = (v.get("gates") or {}).get(n) or {}
        # FREEZE F-4: `pass=True` is not the whole story for gate 4 --
        # `power_gate="skip"` (TEST-ONLY) also reads pass=True, and the
        # only record of it was `pins_active`, which this file never
        # printed. Every gate's own qualifying flags are printed now.
        extra = ", ".join(f"{k}={g[k]}" for k in ("skipped", "identical", "cells_match",
                                                  "t_match", "n_rungs_checked")
                          if k in g)
        lines.append(f"  gate {n}: pass={g.get('pass')}" + (f" [{extra}]" if extra else ""))
    lines.append("")
    # FREEZE F-4: the pins that were ACTIVE when this verdict was
    # written -- the frozen-module check, the import surface, the
    # referent manifest, the prereg binding, the power gate, the
    # injected n_sim, the thread pin. A stubbed pin leaves a verdict
    # that reads identically everywhere else; exp4's own VERDICT.txt
    # does not print them either (precedent noted, not followed).
    pa = v.get("pins_active") or {}
    if pa:
        lines.append("Pins active (design §3.6; anything False or True-for-skip is a "
                     "TEST-ONLY invocation, not the sanctioned run):")
        for k in sorted(pa):
            lines.append(f"  {k}={pa[k]}")
        lines.append("")
    exp4_blk = v.get("exp4") or {}
    lines.append(f"exp4: verdict={exp4_blk.get('verdict')} T={exp4_blk.get('T')}")
    lines.append("")
    lines.append(f"git_sha={v.get('git_sha')}")
    return "\n".join(lines) + "\n"


# ------------------------------------------------------------------- run


def run(root4b=battery_4b.EXP4B, root4=battery_4.EXP4, *, write=False, B=battery_4b.B_4B,
       tag_exists=None, blob_sha=None, referents_sha=_LITERAL, imports_pinned=_LITERAL,
       frozen_check=None, stop_before=None, power_gate="full", n_sim_ext=battery_4b.N_SIM_EXT_4B,
       expected_n_sim=None) -> dict:
    if power_gate not in ("full", "skip"):
        raise ValueError(f"4b: power_gate must be 'full' or 'skip', got {power_gate!r}")
    if stop_before not in (None, "placebo"):
        raise ValueError(f"4b: stop_before must be None or 'placebo', got {stop_before!r}")

    failures = []
    root4b = Path(root4b)
    root4 = Path(root4)

    if referents_sha is _LITERAL:
        referents_sha = REFERENTS_4B_SHA256
    if imports_pinned is _LITERAL:
        imports_pinned = None if IMPORTED_SHA256_4B is None else True

    # ---- frozen modules (exp2*/exp3* transitively, plus exp4-closed itself)
    _, f = collect_total_4b(frozen_check or battery_4b.check_exp4_closed_4b,
                            "4b frozen (exp4-closed)")
    failures += f

    if imports_pinned:
        _, f = collect_total_4b(check_imports_4b, "4b import surface (entry)"); failures += f
    elif imports_pinned is not False:
        failures.append("4b import surface: not pinned (build incomplete)")

    _, f = collect_total_4b(
        lambda: battery_4b.require_prereg_4b(tag_exists=tag_exists, blob_sha=blob_sha),
        "4b prereg tag")
    failures += f

    referent_manifest_ok = False
    if referents_sha is None:
        failures.append("4b referent manifest: not pinned (build incomplete)")
    elif referents_sha is not False:
        from experiments.exp4b import make_referents_4b as mkr4b
        mf, f = collect_total_4b(
            lambda: mkr4b.check_referents_4b(REFERENTS_PATH_4B, sha_pin=referents_sha),
            "4b referent manifest")
        failures += f + (mf or [])
        referent_manifest_ok = not f and not mf

    # ---- Exp 4's verdict/eligibility/power records (B-5)
    v4, f = collect_total_4b(lambda: battery_4b.load_exp4_verdict_4b(root4), "4b exp4 verdict")
    failures += f
    elig4, f = collect_total_4b(lambda: battery_4b.load_exp4_eligibility_4b(root4),
                                "4b exp4 eligibility")
    failures += f
    power4_pack, f = collect_total_4b(lambda: battery_4b.load_exp4_power_4b(root4),
                                      "4b exp4 power")
    failures += f
    power4, power4_sha = power4_pack if power4_pack else (None, None)

    power_n_sim_expected = pw4.N_SIM_4 if expected_n_sim is None else expected_n_sim
    power_n_sim_injected = expected_n_sim is not None
    if power4 is not None and power4.get("n_sim") != power_n_sim_expected:
        failures.append(f"4b power record: n_sim {power4.get('n_sim')!r} != expected "
                        f"{power_n_sim_expected!r}")

    T4 = cells4 = design4 = None
    if v4 is not None:
        T4, f = collect_total_4b(lambda: battery_4b.T_4_from_verdict_4b(v4),
                                 "4b T_4 from verdict")
        failures += f
        cells4, f = collect_total_4b(lambda: battery_4b.cells_from_verdict_4b(v4),
                                     "4b cells from verdict")
        failures += f
        if cells4 is not None:
            design4, f = collect_total_4b(lambda: battery_4b.real_design_4b(cells4),
                                          "4b real design")
            failures += f

    # ---- battery/floors/outcomes/rung sets (Exp 4's loaders, unconditional)
    battery, f = collect_total_4b(bt.load_battery, "4b battery items"); failures += f
    floors, f = collect_total_4b(bg.load_floors, "4b floors 2d"); failures += f

    outcomes, rung_sets = {}, {}
    if battery is not None and floors is not None:
        for traj in battery_4.TRAJECTORIES_4:
            oc, f = collect_total_4b(lambda traj=traj: battery_4.load_outcome_4(traj, battery=battery),
                                     f"4b outcome {traj}")
            failures += f
            outcomes[traj] = oc
            rs = None
            if oc is not None:
                rs, f = collect_total_4b(lambda oc=oc: battery_4.rung_sets_4(oc, floors),
                                         f"4b rung sets {traj}")
                failures += f
                if rs is not None:
                    bad = battery_4.check_rung_set_pins_4(traj, rs)
                    if bad:
                        failures += [f"4b {b}" for b in bad]
            rung_sets[traj] = rs
    else:
        for traj in battery_4.TRAJECTORIES_4:
            outcomes[traj] = None; rung_sets[traj] = None
        failures.append("4b outcomes: battery or floors missing")

    # ---- stage tables + sweep tables (Exp 4's loaders)
    grids = {traj: list(battery_4.GRID_4[traj]) for traj in battery_4.TRAJECTORIES_4}
    series_by_traj, stage_tables_4 = {}, None
    if not failures:
        stage_keys = list(battery_4.STAGE1_KEYS_4) + list(battery_4.STAGE1_FIRST_UNITS_4)
        stage_tables_4, f = collect_total_4b(lambda: an.load_stage_tables_4(root4, keys=stage_keys),
                                             "4b stage tables")
        failures += f
        for traj in battery_4.TRAJECTORIES_4:
            sweep_tables, f = collect_total_4b(lambda traj=traj: an.load_sweep_tables_4(root4, traj),
                                              f"4b sweep tables {traj}")
            failures += f
            if sweep_tables is None or rung_sets.get(traj) is None:
                continue
            refs = battery_4.REFS_FOR_4[traj]
            ref_tables_raw, f = collect_total_4b(
                lambda refs=refs: collect_4.load_ref_tables_4(root4, refs), f"4b ref tables {traj}")
            failures += f
            if ref_tables_raw is None:
                continue
            ref_tables = {ref: rt["sets"] for ref, rt in ref_tables_raw.items()}
            series, f = collect_total_4b(
                lambda traj=traj, ref_tables=ref_tables, sweep_tables=sweep_tables:
                    an.alignment_series_4(root4, traj, ref_tables, sweep_tables),
                f"4b alignment series {traj}")
            failures += f
            if series is not None:
                series_by_traj[traj] = series

    gates = {}

    # ---- gate (1): T_4 and the 26 cells re-derived
    gate1_ok, gate1_detail = False, {}
    if series_by_traj and elig4 is not None and cells4 is not None and T4 is not None:
        g1, f = collect_total_4b(
            lambda: gate1_rederive_4b(series_by_traj, rung_sets, elig4, cells4, T4), "4b gate 1")
        failures += f
        if g1 is not None:
            gate1_ok, gate1_detail = g1["pass"], g1
    gates["1"] = {"pass": gate1_ok, **{k: v for k, v in gate1_detail.items() if k != "pass"}}
    if not gate1_ok:
        failures.append(f"4b gate 1: T_4/cells re-derivation disagrees with the committed verdict "
                        f"({gate1_detail or 'inputs unavailable'})")

    # ---- gate (2): eligibility re-derived
    gate2_ok, gate2_detail = False, {}
    if elig4 is not None:
        g2, f = collect_total_4b(lambda: gate2_rederive_4b(root4, elig4), "4b gate 2")
        failures += f
        if g2 is not None:
            gate2_ok, gate2_detail = g2["pass"], g2
    gates["2"] = {"pass": gate2_ok, "diffs": gate2_detail.get("diffs", [])}
    if not gate2_ok:
        failures.append(f"4b gate 2: eligibility disagrees with re-derivation: "
                        f"{gate2_detail.get('diffs', [])[:3]}")

    # ---- gate (3): lambda_hat re-derived
    gate3_ok, gate3_detail, lambda_by_traj = False, {}, {}
    if series_by_traj and elig4 is not None and v4 is not None:
        g3, f = collect_total_4b(lambda: gate3_rederive_4b(series_by_traj, rung_sets, elig4, v4),
                                 "4b gate 3")
        failures += f
        if g3 is not None:
            gate3_ok, gate3_detail = g3["pass"], g3
            lambda_by_traj = g3.get("lambda_by_traj", {})
    gates["3"] = {"pass": gate3_ok, "diffs": gate3_detail.get("diffs", [])}
    if not gate3_ok:
        failures.append(f"4b gate 3: lambda_hat disagrees with the committed calibration: "
                        f"{gate3_detail.get('diffs', [])}")

    # ---- gate (5): gate 0 (site 0 excluded) fractions
    gate5_ok, gate5_detail = False, {}
    if stage_tables_4 is not None and v4 is not None:
        g5, f = collect_total_4b(lambda: gate5_rederive_4b(root4, stage_tables_4, v4), "4b gate 5")
        failures += f
        if g5 is not None:
            gate5_ok, gate5_detail = g5["pass"], g5.get("per_traj", {})
    gates["5"] = {"pass": gate5_ok, "per_traj": gate5_detail}
    if not gate5_ok:
        failures.append(f"4b gate 5: gate0 fractions disagree with the committed record: "
                        f"{gate5_detail}")

    # ---- gate (6): the endpoint units' byte identity (FREEZE F-1)
    #
    # Unconditional: it needs only `root4`. The placebo screen's
    # endpoint input (the SWEEP endpoint unit, through the series'
    # per_item arrays) and the real eligibility rule's (the REFERENCE
    # endpoint unit) are different files; the placebo is the analogue
    # of Exp 4's rule only if they are byte-identical.
    gate6_ok, gate6_detail = False, {}
    g6, f = collect_total_4b(lambda: gate6_endpoint_identity_4b(root4), "4b gate 6")
    failures += f
    if g6 is not None:
        gate6_ok, gate6_detail = g6["pass"], g6
    gates["6"] = {"pass": gate6_ok,
                  "per_traj": gate6_detail.get("per_traj", {}),
                  "n_rungs_checked": gate6_detail.get("n_rungs_checked")}
    if not gate6_ok:
        failures.append(f"4b gate 6: the endpoint units' bytes disagree, so the placebo "
                        f"eligibility screen is not the analogue of Exp 4's rule: "
                        f"{gate6_detail.get('bad') or 'inputs unavailable'}")

    # ---- gate (4): the power record reproduction
    if power_gate == "full":
        rep, f = collect_total_4b(lambda: power_ext_4b.reproduce_power_record_4b(root4),
                                  "4b gate 4 power reproduction")
        failures += f
        gate4_ok = bool(rep and rep.get("identical"))
        if rep is not None:
            # Promoted minor (finding 7): `seconds` is wall-clock, not a
            # verdict quantity -- it must not sit in the persisted
            # record (Task 6's cross-process determinism fixture needs
            # verdict.json byte-identical). Printed for the ledger
            # instead of carried.
            print(f"4b gate 4: power record reproduction took {rep['seconds']:.4f}s "
                 f"(identical={rep['identical']})", flush=True)
        rep_persisted = {k: v for k, v in (rep or {}).items() if k != "seconds"}
        gates["4"] = {"pass": gate4_ok, **rep_persisted}
        if not gate4_ok:
            failures.append(f"4b gate 4: power record not reproduced: "
                            f"{(rep or {}).get('first_diff')}")
    else:  # "skip", TEST-ONLY
        gates["4"] = {"pass": True, "skipped": True}

    exp4_block = {
        "verdict": v4.get("verdict") if v4 else None,
        "T": T4,
        "git_sha": v4.get("git_sha") if v4 else None,
        "tags": [battery_4.PREREG_TAG_4, battery_4.REFERENCE_SEAL_TAG_4, battery_4b.EXP4_CLOSED_TAG],
    }
    pins_active = {
        "frozen_modules": frozen_check is None,
        "import_surface": bool(imports_pinned),
        "referent_manifest": referent_manifest_ok,
        "prereg_binding": tag_exists is None and blob_sha is None,
        "power_gate_skipped": power_gate == "skip",
        "power_n_sim_expected": power_n_sim_expected,
        "power_n_sim_injected": power_n_sim_injected,
        "threads_pinned": _threads_4.threads_pinned_4(),
        "threads_pinned_before_numpy": bool(_threads_4.PINNED_BEFORE_NUMPY_4),
        # FREEZE F-4 (disclosure): the analysis stack. Nothing here
        # gates -- gate 1's bit-for-bit T re-derivation is the stack
        # check, since a numpy/BLAS reduction-order change would move
        # the series -- but "which numpy decided this" belongs in the
        # record, as every campaign experiment in this program records
        # its torch/transformers versions.
        "numpy_version": np.__version__,
        "scipy_version": _scipy_version_4b(),
    }

    if stop_before == "placebo":
        tree = {"verdict": "INSUFFICIENT_DATA",
               "reason": "4b: stopped before the placebo null (pre-tag tool run)"}
        v = verdict_4b(tree=tree, gates=gates, exp4_block=exp4_block, pins_active=pins_active)
        v = an._jsonify_4(v)
        if write:
            _write_verdict_only_4b(root4b, v)
        return v

    # ================================================== the placebo pipeline

    pools = {}
    if not failures:
        for traj in battery_4.TRAJECTORIES_4:
            series = series_by_traj.get(traj)
            rs = rung_sets.get(traj)
            if series is None or rs is None:
                pools[traj] = None
                continue
            steps = series["steps"]
            per_item = series.get("per_item") or {}
            pia_t1 = per_item.get(steps[0])
            pia_end = per_item.get(steps[-1])
            if pia_t1 is None or pia_end is None:
                failures.append(f"4b: {traj} alignment series carries no per_item t_1/endpoint "
                                f"arrays")
                pools[traj] = None
                continue
            flat = rs["flat"]
            pool, f = collect_total_4b(
                lambda series=series, pia_t1=pia_t1, pia_end=pia_end, flat=flat:
                    placebo_4b.placebo_pool_4b(series, pia_t1, pia_end, flat,
                                              n_boot=an.N_BOOT_ELIG_4, seed=battery_4b.SEED_4B),
                f"4b placebo pool {traj}")
            failures += f
            pools[traj] = pool

    # Finding 4: a top-level, UNCONDITIONAL feasibility block -- the
    # feasibility-floor refusal path previously left this reachable
    # only through `primary`, which stays `None` on exactly that path
    # (no per-trajectory deficits were ever surfaced when the floor
    # fired). `deficit` matches `draw_batteries_4b`'s own rule
    # (`n_real > 0 and n_eligible < MIN_PLACEBO_PER_TRAJ_4B`) so the
    # two constructions agree even before batteries are drawn.
    feasibility_block, feasibility_ok = None, False
    if not failures:
        per_traj_feas, total_eligible = {}, 0
        for traj in battery_4.TRAJECTORIES_4:
            pool = pools.get(traj)
            n_elig = sum(1 for d in (pool or {}).values() if d["eligible"]) if pool else 0
            n_real = (design4.get(traj, {}) if design4 else {}).get("n", 0)
            deficit = n_real > 0 and n_elig < battery_4b.MIN_PLACEBO_PER_TRAJ_4B
            per_traj_feas[traj] = {"n_real": n_real, "n_eligible_placebo": n_elig,
                                   "deficit": deficit}
            total_eligible += n_elig
        feasibility_ok = total_eligible >= battery_4b.MIN_PLACEBO_TOTAL_4B
        feasibility_block = {"per_traj": per_traj_feas, "total_eligible": total_eligible,
                             "min_required": battery_4b.MIN_PLACEBO_TOTAL_4B,
                             "floor_ok": feasibility_ok}
        if not feasibility_ok:
            failures.append(f"4b: {total_eligible} eligible placebo rungs total < "
                            f"{battery_4b.MIN_PLACEBO_TOTAL_4B} (design §4 floor)")

    batteries = None
    if not failures:
        batteries, f = collect_total_4b(
            lambda: placebo_4b.draw_batteries_4b(pools, design4, B=B, seed=battery_4b.SEED_4B),
            "4b draw batteries")
        failures += f
        # On the completing path, prefer the AUTHORITATIVE per-
        # trajectory feasibility `draw_batteries_4b` itself used over
        # the hand-rolled duplicate above (same shape, same rule;
        # this is the one that actually decided the batteries).
        if batteries is not None and feasibility_block is not None and batteries.get("feasibility"):
            feasibility_block = {**feasibility_block, "per_traj": batteries["feasibility"]}

    p_cal_block = t_star_block = alpha_block = per_traj_cal = per_type_cal = None
    s3 = s4 = s5 = s8 = None
    if not failures and batteries is not None:
        p_cal_block, f = collect_total_4b(lambda: placebo_4b.p_cal_4b(batteries["T"], T4),
                                          "4b p_cal")
        failures += f
        t_star_block, f = collect_total_4b(lambda: placebo_4b.t_star_4b(batteries["T"], T4),
                                           "4b t_star")
        failures += f
        # r3: the real verdict's own flip regime, read live off the
        # committed v4["primary"] -- never retyped (the design's own
        # literal, "exact, 15 rungs", is exactly what this reads).
        real_regime = {"flip_method": (v4.get("primary") or {}).get("flip_method"),
                       "n_rungs": (v4.get("primary") or {}).get("n_rungs")}
        alpha_block, f = collect_total_4b(
            lambda: placebo_4b.alpha_placebo_4b(batteries, seed=battery_4b.SEED_4B,
                                               b_alpha=battery_4b.B_ALPHA_4B,
                                               real_regime=real_regime),
            "4b alpha_placebo")
        failures += f
        per_traj_cal, f = collect_total_4b(
            lambda: placebo_4b.per_traj_4b(batteries, design4, (v4.get("primary") or {}).get("per_traj") or {}),
            "4b per_traj")
        failures += f
        per_type_cal, f = collect_total_4b(
            lambda: placebo_4b.per_type_4b(pools, cells4, B=B, seed=battery_4b.SEED_4B),
            "4b per_type")
        failures += f
        s3, f = collect_total_4b(lambda: placebo_4b.s3_shape_4b(batteries, design4, cells4), "4b S3")
        failures += f
        s4, f = collect_total_4b(
            lambda: placebo_4b.s4_scatter_ratio_4b(series_by_traj, rung_sets, cells4), "4b S4")
        failures += f
        s5, f = collect_total_4b(lambda: placebo_4b.s5_autocorr_4b(series_by_traj, rung_sets), "4b S5")
        failures += f
        s8, f = collect_total_4b(
            lambda: placebo_4b.s8_curves_4b(series_by_traj, rung_sets, cells4, pools, batteries),
            "4b S8")
        failures += f

    s1, power_ext_payload = None, None
    if not failures:
        def _s1():
            arms = power_ext_4b.extension_arms_4b(elig4, rung_sets, grids, lambda_by_traj,
                                                  n_sim=n_sim_ext)
            piid = power_ext_4b.p_iid_4b(arms["arms"]["observed_lambda"]["Ts"], T4)
            alpha_iid = arms["arms"]["observed_lambda"].get("P_LEADS")
            placebo_mean = (t_star_block or {}).get("null_mean")
            iid_mean = piid["null_mean"]
            # FREEZE NB-2 (supersedes r2, which was two-sided): design
            # §5 S1's reading is ONE-SIDED -- "same shape (means within
            # .05) or drift-like (placebo mean BELOW the iid mean by
            # more than .05, WITH the per-index table S3 rising)". r2
            # labelled every |difference| > .05 "drift-like", which
            # would have read a placebo mean ABOVE the iid mean as
            # evidence of accumulating drift (the opposite direction)
            # and dropped the S3 conjunct entirely. Four labels now,
            # `S1_READINGS_4B`: the two §5 names, plus the two cells §5
            # does not license -- "above-iid" and "below-iid, S3 not
            # rising". `None` only when a mean is unavailable. The rule
            # itself is `s1_reading_4b` (one fast test per label).
            comparison = {"placebo_null_mean": placebo_mean,
                         "placebo_null_sd": (t_star_block or {}).get("null_sd"),
                         "iid_null_mean": iid_mean, "iid_null_sd": piid["null_sd"]}
            comparison.update(s1_reading_4b(placebo_mean, iid_mean, s3))
            return {"arms": arms, "p_iid": piid["p_iid"], "alpha_iid": alpha_iid,
                    "comparison": comparison}
        s1, f = collect_total_4b(_s1, "4b S1")
        failures += f
        if s1 is not None:
            power_ext_payload = s1["arms"]

    s6 = None
    if not failures:
        def _s6():
            return {"ladder": levels_4b.ladder_4b(root4),
                   "twins": levels_4b.twins_4b(root4),
                   "ceiling": levels_4b.ceiling_4b(root4),
                   "within_family": levels_4b.within_family_4b(root4),
                   "max_over_pairs": levels_4b.max_over_pairs_4b(root4, cells4)}
        s6, f = collect_total_4b(_s6, "4b S6")
        failures += f

    s7 = None
    if not failures:
        def _s7():
            # Finding 5 (controller ruling): S7(a) against the MATCHED
            # (clears-and-stays) null, re-derived from the cells --
            # Exp 4's own `_clears_and_stays_primary` construction, via
            # `clears_and_stays_cells_4b` above. The re-derived T is
            # itself a known-answer gate against the committed
            # `sensitivities["primary_clears_and_stays"]["T"]`, bit for
            # bit -- a mismatch raises (caught by `collect_total_4b`
            # like every other totality site here).
            cas_cells = clears_and_stays_cells_4b(series_by_traj, rung_sets, elig4)
            committed_cas_T = ((v4.get("sensitivities") or {})
                              .get("primary_clears_and_stays") or {}).get("T")
            if cas_cells:
                cas_T = an.primary_4(cas_cells, n_boot=an.N_BOOT_4, seed=0)["T"]
                if committed_cas_T is not None and cas_T != committed_cas_T:
                    raise ValueError(
                        f"4b S7(a): re-derived clears-and-stays T {cas_T!r} != the committed "
                        f"sensitivities['primary_clears_and_stays']['T'] {committed_cas_T!r}")
                design_cas = clears_and_stays_design_4b(cas_cells)
                batteries_cas = placebo_4b.draw_batteries_4b(pools, design_cas, B=B,
                                                              seed=battery_4b.SEED_4B + 7)
                a_cas = {"T": cas_T, "clear_multiset_source": "clears-and-stays cells re-derived"}
                a_cas.update(placebo_4b.p_cal_4b(batteries_cas["T"], cas_T))
                a_cas.update(placebo_4b.t_star_4b(batteries_cas["T"], cas_T))
            else:
                a_cas = {"T": None, "clear_multiset_source": "clears-and-stays cells re-derived",
                        "reason": "no clears-and-stays cells re-derived"}

            # S7(b) stays against the PRIMARY null (mismatched
            # construction, disclosed): the flat rungs' best-site
            # series is not available, so there is no matched null to
            # build here.
            bs = best_site_mean_phi_4b(v4, cells4)
            if bs["T"] is not None:
                b_best = {"T": bs["T"], "n_cells": bs["n_cells"]}
                b_best.update(placebo_4b.p_cal_4b(batteries["T"], bs["T"]))
                b_best.update(placebo_4b.t_star_4b(batteries["T"], bs["T"]))
            else:
                b_best = {"T": None, "n_cells": 0}
            b_best["mismatch_disclosed"] = (
                "compared against the PRIMARY placebo null -- best-site phi has no matching "
                "placebo construction (flat rungs' best_site series is not available), so this "
                "is a mismatched-construction reading, not a calibration")
            return {"clears_and_stays": a_cas, "best_site": b_best}
        s7, f = collect_total_4b(_s7, "4b S7")
        failures += f

    # Mutation harness review finding 3 (2j F-1's lineage, exp4's own
    # analyze_4.run() pattern at its own entry/exit sites): the import
    # surface is itself a verdict input -- a read sweep sees what an
    # analyzer OPENS, not what the interpreter EXECUTES on its behalf.
    # Checked at ENTRY (`"4b import surface (entry)"`, above, before
    # `make_referents_4b` is even imported) and again at EXIT, after
    # S1/S6/S7 have each had the chance to import something the entry
    # check never saw. Gated by `if not failures:` (exp4's own rule) --
    # `imports_pinned` falsy uses a no-op thunk, so the wrapper site
    # itself is still exercised (and totality-testable) either way.
    if not failures:
        _, f = collect_total_4b(check_imports_4b if imports_pinned else (lambda: None),
                                "4b import surface (exit)")
        failures += f

    tree = verdict_tree_4b(failures, feasibility_ok, (p_cal_block or {}).get("p_cal"))

    primary_block = None
    if p_cal_block is not None and t_star_block is not None:
        primary_block = {
            "T4": T4, "p_cal": p_cal_block["p_cal"], "p_low": p_cal_block["p_low"],
            "T_star": t_star_block["T_star"], "interval": t_star_block["interval"],
            "null_mean": t_star_block["null_mean"], "null_sd": t_star_block["null_sd"],
            "q95": t_star_block["q95"], "q99": t_star_block["q99"],
            "B": p_cal_block["B"], "n_cells": len(cells4) if cells4 else None,
            "feasibility": feasibility_block,
            # FREEZE F-2: p_cal's own Monte Carlo resolution against the
            # tree's two bars, which carry no tolerance.
            "mc_resolution": placebo_4b.bar_margins_4b(p_cal_block["p_cal"], p_cal_block["B"]),
        }

    licence_naming = None
    if per_traj_cal is not None:
        # m4 (final review): the naming bar is exp4's own LICENCE_TRAJ_
        # ALPHA_4 (0.05), read off the frozen instrument rather than
        # retyped as a literal here.
        naming_trajs = sorted(t for t, pt in per_traj_cal.items()
                              if pt.get("p_cal") is not None
                              and pt["p_cal"] < an.LICENCE_TRAJ_ALPHA_4)
        licence_naming = {
            "trajectories": naming_trajs, "n": len(naming_trajs),
            "rule": "design §6/§10(l): the sentence names the trajectories at p_cal,M < .05; "
                    "unqualified at two or more.",
        }

    # r1 (final review): the design §6 licence sentence for the
    # reached world, the CALIBRATED-only alpha_placebo sub-clause, and
    # the naming rule's own outcome -- printed in VERDICT.txt beside
    # the primary reading, never computed twice (this block only reads
    # fields already built above).
    licence_block = None
    licence_text = LICENCE_4B.get(tree["verdict"])
    if licence_text is not None:
        alpha_clause = None
        if tree["verdict"] == "CALIBRATED" and alpha_block is not None:
            alpha_clause = LICENCE_ALPHA_PLACEBO_CLAUSE_4B[
                alpha_block["alpha_placebo"] < an.LICENCE_TRAJ_ALPHA_4]
        naming_outcome = None
        if licence_naming is not None:
            naming_outcome = (
                f"{licence_naming['n']} trajectories qualify at p_cal,M < .05: "
                f"{licence_naming['trajectories']}" if licence_naming["n"] >= 2 else
                f"fewer than two trajectories qualify ({licence_naming['trajectories']}); "
                f"the sentence names them")
        # FREEZE F-3: §6's NOT-DISTINGUISHABLE sentence asserts that
        # T*'s interval covers zero. Checked, not assumed.
        covers_zero = interval_covers_zero_4b((t_star_block or {}).get("interval"))
        unnamed_cell = (LICENCE_INTERVAL_BELOW_NULL_4B
                        if (tree["verdict"] == "NOT-DISTINGUISHABLE" and covers_zero is False)
                        else None)
        licence_block = {"world": tree["verdict"], "text": licence_text,
                         "alpha_placebo_clause": alpha_clause, "naming_outcome": naming_outcome,
                         "any_world": LICENCE_ANY_WORLD_4B,
                         "interval_covers_zero": covers_zero,
                         "unnamed_cell": unnamed_cell}

    construction_statement = None
    if v4 is not None and T4 is not None:
        exp4_primary = v4.get("primary") or {}
        p_plus = exp4_primary.get("p_plus")
        T_b = batteries["T"] if batteries is not None else None
        null_q01 = float(np.percentile(T_b, 1)) if T_b is not None and len(T_b) else None
        construction_statement = {
            "exp4_T": T4, "exp4_p_plus": p_plus, "null_q01": null_q01,
            "text": (f"Experiment 4's own sign-flip reading against the construction account "
                    f"(agreement arriving with performance, phi ~ 0) stands: T {T4}, "
                    f"p+ {p_plus}, T_bar {an.T_BAR_4}; the placebo null's own 1st percentile "
                    f"({null_q01}) is printed beside it."),
        }

    v = verdict_4b(tree=tree, gates=gates, exp4_block=exp4_block, pins_active=pins_active,
                  primary=primary_block, feasibility=feasibility_block,
                  alpha_placebo=alpha_block, per_traj=per_traj_cal,
                  per_type=per_type_cal, licence_naming=licence_naming,
                  construction_statement=construction_statement, licence=licence_block,
                  s1=s1, s3=s3, s4=s4, s5=s5, s6=s6, s7=s7, s8=s8)

    placebo_bytes = power_ext_bytes = None
    if batteries is not None:
        placebo_payload = {
            "T_b": batteries["T"].tolist(),
            "per_traj_mean": {t: arr.tolist() for t, arr in batteries["per_traj_mean"].items()},
            "n_distinct_rungs": batteries["n_distinct_rungs"].tolist(),
            "seed": battery_4b.SEED_4B, "B": B,
        }
        placebo_bytes = json.dumps(an._jsonify_4(placebo_payload), indent=1,
                                   allow_nan=False).encode("utf-8")
        v["placebo_record_sha256"] = hashlib.sha256(placebo_bytes).hexdigest()
    if power_ext_payload is not None:
        power_ext_bytes = json.dumps(an._jsonify_4(power_ext_payload), indent=1,
                                     allow_nan=False).encode("utf-8")
        v["power_ext_sha256"] = hashlib.sha256(power_ext_bytes).hexdigest()

    v = an._jsonify_4(v)

    if write:
        # FREEZE F-5: the two companions are written BEFORE
        # verdict.json, not after. verdict.json carries their sha256s
        # (B-6), so the old order left a window -- and, on a write
        # failure (a full disk, a `results` path that is a file, a
        # read-only tree), a PERMANENT state -- in which a committed
        # verdict attested two records that do not exist. The writes
        # are deliberately NOT wrapped in `collect_total_4b`: a write
        # failure must be loud, not a verdict. Ordering it this way
        # makes "verdict.json exists" imply "its attested companions
        # exist", whatever fails.
        root_out = Path(root4b)
        battery_4b.verdict_path_4b(root_out).parent.mkdir(parents=True, exist_ok=True)
        if placebo_bytes is not None:
            battery_4b.placebo_record_path_4b(root_out).write_bytes(placebo_bytes)
        if power_ext_bytes is not None:
            battery_4b.power_ext_path_4b(root_out).write_bytes(power_ext_bytes)
        _write_verdict_only_4b(root4b, v)

    return v


def _write_verdict_only_4b(root4b, v: dict) -> None:
    root4b = Path(root4b)
    out_v = battery_4b.verdict_path_4b(root4b)
    out_txt = battery_4b.verdict_txt_path_4b(root4b)
    out_v.parent.mkdir(parents=True, exist_ok=True)
    out_v.write_text(json.dumps(v, indent=1, allow_nan=False))
    out_txt.write_text(write_verdict_txt_4b(v))


if __name__ == "__main__":
    result = run(write=True)
    print(f"verdict: {result['verdict']}")
    print(result["reason"])
