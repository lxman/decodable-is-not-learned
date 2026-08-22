"""Exp 2e frozen analysis (design §4–§6): the floor as a covariate.

ANALYSIS-ONLY. No model is loaded and nothing is sampled; every input
is a committed 2d or 2c artifact read through 2d's frozen loaders
(`experiments/exp2d/analyze_2d.py`, sha-pinned here together with the
rest of 2d's instrument). 2e adds: the §5.1 functionals
(`functionals_2e.py`), a 273-file referent manifest over 2d's tree,
the per-cell main tally pin (design §4's table, by literal), the 2d
COMPARISON GATE (2d's thresholded primary re-derived from the same
cells through 2d's own code must equal 2d's committed verdict.json
AND the literal pin), the §5.4/§5.5 secondaries and the §6 tree.

The §6 tree's first terminal is a VERDICT, not an exception (methods
paper lesson 8): every pinned-referent refusal the loaders raise is
collected into `referent_failures` and delivered as
INSUFFICIENT_DATA with the reasons verbatim. Non-refusal exceptions
(anything but ValueError / FileNotFoundError) still propagate — a bug
is not a verdict.

§2's disclosure — the predictor's inputs were known to the designer —
rides verbatim on every record (`known_inputs_caveat`) and inside the
licensed sentence (ruling g).
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

EXP2E = Path(__file__).resolve().parent
EXPERIMENTS = EXP2E.parent
REPO = EXPERIMENTS.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp2d import analyze_2d as a2d  # noqa: E402
from experiments.exp2d import battery_2d as bt  # noqa: E402
from experiments.exp2d import stats_2d as st  # noqa: E402
from experiments.exp2e import functionals_2e as fn  # noqa: E402

EXP2D = a2d.EXP2D
REFERENTS_PATH = EXP2E / "referents_2e.json"
RESULTS = EXP2E / "results"

RUNGS = bt.RUNGS
FAMILY_OF = bt.FAMILY_OF
FAMILY_SIZES = bt.FAMILY_SIZES
PROBE_SIZES = bt.PROBE_SIZES
EVAL_SIZES = bt.EVAL_SIZES
REPLICATION_SIZE = "1b"
OTHER_SIZE = "410m"
FIRST_DIGIT_RUN_RUNGS = ("base12_digitsum", "base13")   # 2d freeze F-3
PRIMARY_FUNCTIONAL = "F1"                                # ruling a
FUNCTIONALS = ("F1", "F2", "F3", "B0")

# §2, verbatim (ruling g: repeated on the record and in the sentence)
KNOWN_INPUTS_CAVEAT_2E = (
    "What 2e cannot be: a forecast, or even 2d's kind of test. 2d's "
    "outcome was known; 2e's predictor inputs are known too — every "
    "per-rung tally is in 2d's committed verdict record, and the "
    "designer of this document has read them alongside the outcome. The "
    "preregistration therefore protects against exactly one thing: "
    "picking the functional after computing its correlation. It does "
    "not protect against a functional chosen with the tallies in view, "
    "and the doc says so. Three guards are built in: the family of "
    "admissible functionals is small and enumerated here (§5.1), one is "
    "primary and the rest are printed; the pilot tier — a different "
    "seed, drawn before any of this was written — replicates the "
    "primary (independent in SEED, not in what the designer knew: its "
    "per-cell tallies were as visible as main's, in 2d's runner logs "
    "and in `power_2d.json`'s attested pilot predictor); and the "
    "dumbest baseline, rank-by-floor-alone, is reported beside every "
    "result (§8). A PASS licenses a sentence about 2d's rule, not about "
    "Prediction 2.")

# ----------------------------------------------------- frozen-file pins
#
# 2d's instrument, by literal: the loaders, the statistics, the
# battery/floor rule, the comparator, 2d's own referent manifest (whose
# 250 entries analyze_2d re-hashes at every run), the stream map and
# the power records. A changed byte in any of them means 2e is no
# longer reading 2d's tree through 2d's closed code.
FROZEN_IMPORT_SHA256_2E = {
    EXP2D / "analyze_2d.py":
        "01ee334db5fe273a8509cf4bf79757b52a40a123311acd42554ac1a82e40334a",
    EXP2D / "stats_2d.py":
        "86243932709013ea15b250e9bf15243ce6209e03e6bcf81af0f7ac3f92644b46",
    EXP2D / "battery_2d.py":
        "503a2c09ec320989223561291ff93c71d62d27ed20c5681f9b2d535b7708e81a",
    EXP2D / "rederive_2d.py":
        "d53f0cbdf5fee66446c17960eaf72c73828a415c0c5cd0160f45f5b743bbbf18",
    EXP2D / "referents_2d.json":
        "95eded96af9b9c7b52ab1d1eb457d9a4fd6af94749f040f2655859183a97ad59",
    EXP2D / "stream_map_2d.json":
        "7819b690253a3d1acde779f8db5dbe2d0ad0cb3d67efb513fa4bdb445a37250d",
    EXP2D / "power_2d.json":
        "7bfb5914721e8b4d8a51c4ec702a3767b9dfc7227a46671169f31ea23abb90d3",
    EXP2D / "power_envelope_2d.json":
        "a1f477eec1a253fd1146051b8d65d8b4319c10ccf79bcd880d0a6b6bb3a8795f",
}

# §4: the per-rung MAIN tallies (verified of 32,000; 410m | 1b), the
# outcome side's twin — known, disclosed, pinned by literal and
# compared to the re-tally of the committed bytes at every run.
_TALLY_DOC = {
    "arith_next": (831, 531), "sub_base8": (710, 723),
    "antonym": (5015, 4368), "odd_one_out": (5324, 5356),
    "median5": (3930, 4481), "antonym6": (3616, 3147), "odd6": (2804, 3195),
    "median7": (2714, 3370), "hamming12": (4322, 3977),
    "roman_sum7": (3033, 2461), "collatz_step2": (2820, 3145),
    "count_div13": (2250, 2795), "isqrt_gap": (1795, 2719),
    "mod13": (1668, 1709), "mod17": (1624, 1564), "mod19": (1230, 1203),
    "mod13_comp": (922, 1353), "clock24_d999": (1082, 931),
    "clock24": (933, 927), "count_div7": (652, 838), "add_base8": (242, 170),
    "base13": (147, 173), "quad_next": (145, 156),
    "base12_digitsum": (52, 85), "sub3_mid": (35, 34), "add3_mid": (17, 10),
    "sub4_mid": (12, 15), "oct2dec": (8, 13), "caesar": (7, 7),
    "base7": (6, 7), "caesar_len8": (1, 3), "add4_mid": (1, 1),
    "reverse_string": (0, 1), "rev_string7": (0, 0),
}
MAIN_TALLY_PIN = {(r, s): int(v[i]) for r, v in _TALLY_DOC.items()
                  for i, s in enumerate(PROBE_SIZES)}
if set(_TALLY_DOC) != set(RUNGS):
    raise RuntimeError("MAIN_TALLY_PIN does not cover the 34 rungs")

# §4: 2d's committed primary, by literal (results/verdict.json, tag
# exp2d-closed) — the known answer the comparison gate must reproduce
# from the same cells through 2d's own `predictor_from_tier` +
# `primary_test`.
VERDICT_2D_PIN = {"auc": 0.5454545454545454,
                  "block_p": 0.6674933250667493,
                  "ci": [0.5, 0.6666666666666666],
                  "bootstrap_n_dropped": 2,
                  "n_rising": 11, "n_flat": 23,
                  "verdict": "FAIL"}
# §5.4: 2c's probe predictor on the same label, as 2d's record printed
# it (.6008) and 2c's ρ (.368, `a2d.VERDICT_2C_PIN`).
PROBE_2C_AUC_PIN = 0.6007905138339921

# referents_2e.json: 272 tier files + 2d's verdict.json, by sha; the
# FILE's own sha is the literal here (set at build).
REFERENTS_FILE_SHA256 = \
    "51a3cc2abc6a9cac217db380f1de7f9a47edeaf4b2ff1b76a3eb72f1dde9eea5"


def check_frozen_imports_2e() -> None:
    for path, want in FROZEN_IMPORT_SHA256_2E.items():
        got = hashlib.sha256(Path(path).read_bytes()).hexdigest()
        if got != want:
            raise ValueError(
                f"frozen file {path} has sha256 {got}, expected {want} — "
                f"2d is closed and its instrument is 2e's loader; a "
                f"changed byte means 2e no longer reads 2d's tree through "
                f"2d's code")


def verdict_2d_pin_from_record(v: dict) -> dict:
    p = v["primary"]
    return {"auc": p["auc"], "block_p": p["block_p"], "ci": list(p["ci"]),
            "bootstrap_n_dropped": p["bootstrap_n_dropped"],
            "n_rising": p["n_rising"], "n_flat": p["n_flat"],
            "verdict": v["verdict"]}


# --------------------------------------------------------------- manifest

_LITERAL_PIN = object()


def load_manifest(path=REFERENTS_PATH, *, file_sha_pin=_LITERAL_PIN) -> dict:
    """The manifest, its own bytes pinned (the literal by default; a
    world's sha in tests; None skips — tests only). A pin mismatch is
    a HARD error: the instrument, not the tree, has changed."""
    raw = Path(path).read_bytes()
    got = hashlib.sha256(raw).hexdigest()
    pin = REFERENTS_FILE_SHA256 if file_sha_pin is _LITERAL_PIN else file_sha_pin
    if pin is not None and got != pin:
        raise ValueError(f"{path} has sha256 {got} against the pinned {pin}")
    rec = json.loads(raw)
    if rec.get("n_files") != len(rec.get("files", {})):
        raise ValueError(f"{path}: n_files {rec.get('n_files')} != "
                         f"{len(rec.get('files', {}))} entries")
    return rec


def check_manifest(root, rec) -> list:
    """Every entry re-hashed against the tree; a list of failures
    (VERDICT inputs), never an exception for a tree problem."""
    from experiments.exp2e import make_referents_2e as mk
    if rec["n_files"] != len(rec["files"]):
        raise ValueError("manifest n_files disagrees with its entries")
    if rec["n_files"] != mk.N_FILES:
        raise ValueError(f"manifest carries {rec['n_files']} files, the "
                         f"frozen layout has {mk.N_FILES}")
    root = Path(root)
    bad = []
    for rel, want in rec["files"].items():
        p = root / rel
        if not p.is_file():
            bad.append(f"manifest: {rel} missing")
            continue
        h = hashlib.sha256(p.read_bytes()).hexdigest()
        if h != want:
            bad.append(f"manifest: {rel} hashes to {h}, pinned {want}")
    return bad


# ----------------------------------------------------------- tally pin

def check_tally_pin(main_cells, pin) -> list:
    bad = []
    for (rung, size), want in pin.items():
        if (rung, size) not in main_cells:
            bad.append(f"tally pin: {rung}/{size} pinned but not loaded")
            continue
        got = main_cells[(rung, size)]["verified"]
        if got != want:
            bad.append(f"tally pin: {rung}/{size} re-tallies to {got}, "
                       f"pinned {want}")
    missing = [k for k in main_cells if k not in pin]
    if missing:
        bad.append(f"tally pin: {len(missing)} cell(s) unpinned, e.g. "
                   f"{missing[0]}")
    return bad


# ------------------------------------------------------ 2d comparison

def comparison_2d(main_cells, floors, outcome) -> dict:
    """2d's thresholded predictor and primary, re-derived from the same
    cells through 2d's own code — the known-answer gate for the
    inherited statistic, and the §5.4 comparison column."""
    fams = [FAMILY_OF[r] for r in RUNGS]
    pred = a2d.predictor_from_tier(main_cells, floors,
                                   n_draws_per_rung=a2d.MAIN_DRAWS_PER_RUNG)
    y = a2d._labels(outcome, "rising")
    x = a2d._family_contiguous({r: pred[r]["score"] for r in RUNGS})
    t = st.primary_test(x, y, FAMILY_SIZES, fams)
    return {"auc": t["auc"], "block_p": t["block"]["p"],
            "ci": list(t["bootstrap"]["ci"]),
            "bootstrap_n_dropped": t["bootstrap"]["n_dropped"],
            "n_rising": t["n_rising"], "n_flat": t["n_flat"],
            "predictor": {r: pred[r]["score"] for r in RUNGS}}


def check_comparison_2d(cmp, root, pin) -> list:
    """Re-derivation == the tree's results/verdict.json primary ==
    the literal pin, field by field; the file's verdict == the pin's."""
    p = Path(root) / "results" / "verdict.json"
    if not p.is_file():
        return [f"2d comparison: {p} missing"]
    v = json.loads(p.read_text())
    rec = verdict_2d_pin_from_record(v)
    bad = []
    for k in ("auc", "block_p", "ci", "bootstrap_n_dropped", "n_rising",
              "n_flat"):
        if cmp[k] != rec[k]:
            bad.append(f"2d comparison: re-derived {k} {cmp[k]!r} != 2d's "
                       f"verdict.json {rec[k]!r}")
    if rec != pin:
        bad.append(f"2d comparison: verdict.json {rec} != the literal pin "
                   f"{pin}")
    return bad


# -------------------------------------------------------------- collect

def collect(thunk, label):
    """Run a frozen loader; its REFUSALS (ValueError / FileNotFound)
    become referent failures. Anything else propagates."""
    try:
        return thunk(), []
    except (ValueError, FileNotFoundError) as e:
        return None, [f"{label}: {e}"]


# --------------------------------------------------------------- verdict

def probe_auc_matches(auc: float, pin: float = PROBE_2C_AUC_PIN) -> bool:
    """2c's probe on 2d's label, recomputed == 2d's record (a known
    answer; printed, non-gating)."""
    return bool(auc == pin)


def _ordering(x, y, label, group):
    return a2d._ordering_secondary(x, y, label, group)


def _licensed_sentence(b0_auc: float) -> str:
    return (f"a floor-adjusted sampled rate at 410m/1b, fixed before the "
            f"correlation was computed, separates the rungs that rise above "
            f"format-guessing from those that do not on 2c's battery; 2d's "
            f"null was its threshold's. B0 — the floor alone, −log c — "
            f"scores AUC {b0_auc:.4f} on the same label (a PASS that B0 "
            f"matches is a PASS about answer spaces). Disclosure: "
            f"{KNOWN_INPUTS_CAVEAT_2E}")


def _test(x, y, group, counts):
    fams = [FAMILY_OF[r] for r in RUNGS]
    return st.primary_test(x, y, FAMILY_SIZES, fams, group=group,
                           counts=counts)


def _flat(t):
    return {"auc": t["auc"], "block_p": t["block"]["p"],
            "block_method": t["block"]["method"],
            "n_perms": t["block"]["n_perms"], "ci": t["bootstrap"]["ci"],
            "bootstrap_n_valid": t["bootstrap"]["n_valid"],
            "bootstrap_n_dropped": t["bootstrap"]["n_dropped"],
            "n_rising": t["n_rising"], "n_flat": t["n_flat"]}


def verdict_2e(*, outcome, main_cells, pilot_cells, floors, probe, cmp2d,
               referents) -> dict:
    fams = [FAMILY_OF[r] for r in RUNGS]
    group = st.block_perm_group(FAMILY_SIZES)
    counts = st.bootstrap_counts_matrix(bt.N_FAMILIES)
    vec = a2d._family_contiguous

    y = a2d._labels(outcome, "rising")
    y12 = a2d._labels(outcome, "rising_12b")
    asc = vec({r: outcome["rungs"][r]["corrected_ascent"] for r in RUNGS})

    F1 = fn.f1_table(main_cells, floors)
    F2 = fn.f2_table(main_cells)
    F3 = fn.f3_table(main_cells, floors)
    B0 = fn.b0_table(floors)
    tables = {"F1": F1, "F2": F2, "F3": F3, "B0": B0}
    X = {k: vec({r: t[r]["score"] for r in RUNGS}) for k, t in tables.items()}
    x = X[PRIMARY_FUNCTIONAL]

    primary = _test(x, y, group, counts)
    tree = fn.verdict_tree_2e(referent_failures=[], auc_obs=primary["auc"],
                              block_p=primary["block"]["p"],
                              ci=primary["bootstrap"]["ci"])

    sec = {}
    sec["functionals"] = {k: _flat(_test(X[k], y, group, counts))
                          for k in FUNCTIONALS}
    sec["f1_minus_b0"] = fn.cluster_bootstrap_auc_paired(
        X["F1"], X["B0"], y, fams, counts=counts)
    sec["ordering_vs_corrected_ascent"] = {
        k: _ordering(X[k], asc, "corrected ascent (§5.2)", group)
        for k in FUNCTIONALS}

    # the independent-seed replication (ruling e: non-gating)
    P1 = fn.f1_table(pilot_cells, floors)
    xp1 = vec({r: P1[r]["score"] for r in RUNGS})
    rc = spearmanr(xp1, x).statistic if len(set(xp1)) > 1 and \
        len(set(x)) > 1 else None
    sec["pilot_replication"] = {
        **_flat(_test(xp1, y, group, counts)),
        "eps": P1[RUNGS[0]]["eps"],
        "n_draws_per_cell": a2d.PILOT_DRAWS_PER_RUNG,
        "rho_vs_corrected_ascent": _ordering(xp1, asc,
                                             "corrected ascent (§5.2)", group),
        "rank_corr_pilot_vs_main_f1": None if rc is None or np.isnan(rc)
        else float(rc),
        "zero_draw_cells": sum(1 for r in RUNGS for s in PROBE_SIZES
                               if pilot_cells[(r, s)]["verified"] == 0),
    }
    sec["replication_1b_only"] = _flat(_test(
        vec({r: F1[r]["per_size"][REPLICATION_SIZE] for r in RUNGS}), y,
        group, counts))
    sec["replication_410m_only"] = _flat(_test(
        vec({r: F1[r]["per_size"][OTHER_SIZE] for r in RUNGS}), y,
        group, counts))
    sec["sensitivity_12b_only_label"] = _flat(_test(x, y12, group, counts)) \
        if 0 < y12.sum() < len(y12) else None

    xp = vec(probe)
    pt = _test(xp, y, group, counts)
    sec["probe_predictor_2c"] = {
        **_flat(pt), "auc_pin_2d_record": PROBE_2C_AUC_PIN,
        "auc_matches_2d_record": probe_auc_matches(pt["auc"]),
        "rho_2c": a2d.VERDICT_2C_PIN["rho"],
        "verdict_2c": a2d.VERDICT_2C_PIN}

    # §5.5 sensitivities (printed, non-gating)
    eps_rows = []
    for e in fn.EPS_SENSITIVITY:
        t = fn.f1_table(main_cells, floors, eps=e)
        eps_rows.append({"eps": e, **_flat(_test(
            vec({r: t[r]["score"] for r in RUNGS}), y, group, counts))})
    Fm = fn.f1_table(main_cells, floors, floor_key="majority_floor")
    maj = _flat(_test(vec({r: Fm[r]["score"] for r in RUNGS}), y, group,
                      counts))
    kept, sizes_r, fams_r = fn.drop_rungs_layout(FIRST_DIGIT_RUN_RUNGS)
    y_r = np.asarray([int(outcome["rungs"][r]["rising"]) for r in kept])
    x_r = np.asarray([F1[r]["score"] for r in kept], dtype=float)
    drop = _flat(st.primary_test(x_r, y_r, sizes_r, fams_r))
    sec["sensitivity"] = {
        "eps": eps_rows,
        "majority_floor_only": {**maj, "rungs_affected":
                                sorted(bt.OPTION_LISTING_PIN)},
        "drop_first_digit_run_rungs": {**drop, "n_rungs": len(kept),
                                       "dropped": list(FIRST_DIGIT_RUN_RUNGS)},
    }
    sec["comparison_2d_thresholded"] = {
        k: cmp2d[k] for k in ("auc", "block_p", "ci", "bootstrap_n_dropped",
                              "n_rising", "n_flat")}

    per_rung = {}
    for i, r in enumerate(RUNGS):
        per_rung[r] = {
            "family": FAMILY_OF[r], "floor": floors[r]["floor"],
            "majority_floor": floors[r]["majority_floor"],
            "verified_410m": main_cells[(r, OTHER_SIZE)]["verified"],
            "verified_1b": main_cells[(r, REPLICATION_SIZE)]["verified"],
            "rate_410m": main_cells[(r, OTHER_SIZE)]["rate"],
            "rate_1b": main_cells[(r, REPLICATION_SIZE)]["rate"],
            "F1": float(X["F1"][i]),
            "F1_per_size": {s: F1[r]["per_size"][s] for s in PROBE_SIZES},
            "F2": float(X["F2"][i]), "F3": float(X["F3"][i]),
            "B0": float(X["B0"][i]),
            "rising": bool(y[i]), "rising_12b": bool(y12[i]),
            "corrected_ascent": float(asc[i]),
            "ascent_2c": outcome["rungs"][r]["ascent_2c"],
            "F1_pilot": float(xp1[i]),
            "pilot_verified": {s: pilot_cells[(r, s)]["verified"]
                               for s in PROBE_SIZES},
            "score_2d": cmp2d["predictor"][r],
            "probe_score": float(xp[i]),
            "criterion_exact": floors[r]["criterion"]["exact"],
        }

    b0_auc = sec["functionals"]["B0"]["auc"]
    return {
        "verdict": tree["verdict"], "reason": tree["reason"],
        "known_inputs_caveat": KNOWN_INPUTS_CAVEAT_2E,
        "licensed_sentence_if_pass": _licensed_sentence(b0_auc),
        "primary": {
            "functional": PRIMARY_FUNCTIONAL,
            "statistic": "AUC of F1 = mean over sizes of log((rate + ε) / "
                         "floor), rising vs flat (§5.3)",
            "eps": F1[RUNGS[0]]["eps"],
            **_flat(primary),
            "group_size": primary["block"]["group_size"],
            "alpha": fn.ALPHA, "auc_bar": fn.AUC_BAR,
        },
        "referents": referents,
        "outcome_summary": {
            "n_rising": outcome["n_rising"],
            "n_rising_12b": outcome["n_rising_12b"],
            "families_with_rising": outcome["families_with_rising"],
            "known_answer_gate": outcome["known_answer_gate"]},
        "secondaries": sec,
        "per_rung": per_rung,
        "n_rungs": len(RUNGS), "n_families": bt.N_FAMILIES,
        "model_contact": "none",
    }


def insufficient_data_record_2e(failures, *, referents, outcome) -> dict:
    tree = fn.verdict_tree_2e(referent_failures=failures, auc_obs=None,
                              block_p=None, ci=[None, None])
    return {
        "verdict": tree["verdict"], "reason": tree["reason"],
        "known_inputs_caveat": KNOWN_INPUTS_CAVEAT_2E,
        "referents": referents,
        "primary": None,
        "outcome_summary": None if outcome is None else {
            "n_rising": outcome["n_rising"],
            "n_rising_12b": outcome["n_rising_12b"],
            "families_with_rising": outcome["families_with_rising"],
            "known_answer_gate": outcome["known_answer_gate"]},
        "n_rungs": len(RUNGS), "n_families": bt.N_FAMILIES,
        "model_contact": "none",
    }


# ------------------------------------------------------------------ run

def run(root=EXP2D, *, manifest_path=REFERENTS_PATH,
        manifest_sha_pin=_LITERAL_PIN, tally_pin=None, verdict_2d_pin=None,
        write=False, out_path=None) -> dict:
    """The referent phase first — EVERY failure collected, none
    raised — then the verdict. `tally_pin` / `verdict_2d_pin` default
    to the literals (worlds pass their own)."""
    tally_pin = MAIN_TALLY_PIN if tally_pin is None else tally_pin
    verdict_2d_pin = VERDICT_2D_PIN if verdict_2d_pin is None \
        else verdict_2d_pin
    check_frozen_imports_2e()
    a2d.check_frozen_imports_2d()
    bt.check_order_against_2c()
    a2d.check_stream_map_2d()
    manifest = load_manifest(manifest_path, file_sha_pin=manifest_sha_pin)
    failures = check_manifest(root, manifest)
    # 2d's 250-file manifest (2c's m4 records, the item files, exp3's
    # shards): its own sha is 2d's literal (a mismatch there is a hard
    # error inside the loader); a TREE entry failing is a referent
    # failure here, delivered, not raised
    ref2d, f = collect(a2d.load_referents, "2d referents")
    failures += f
    battery = bt.load_battery()
    floors = bt.floor_table(battery)
    bt.check_floors_against_doc(floors)
    verify_fn = a2d.load_verify()
    outcome, f = collect(lambda: a2d.load_outcome(floors, referents=ref2d),
                         "outcome")
    failures += f
    probe = a2d.load_probe_predictor()
    pilot_cells, f = collect(
        lambda: a2d.load_sampling_tier(root, "pilot", battery, verify_fn),
        "pilot tier")
    failures += f
    main_cells, f = collect(
        lambda: a2d.load_sampling_tier(root, "main", battery, verify_fn),
        "main tier")
    failures += f
    cmp = None
    if main_cells is not None:
        failures += check_tally_pin(main_cells, tally_pin)
        if outcome is not None:
            cmp = comparison_2d(main_cells, floors, outcome)
            failures += check_comparison_2d(cmp, root, verdict_2d_pin)
    referents = {
        "failures": list(failures),
        "manifest": {"path": str(manifest_path), "n_files": manifest["n_files"],
                     "sha256": hashlib.sha256(
                         Path(manifest_path).read_bytes()).hexdigest()},
        "manifest_2d": None if ref2d is None else {"n_files": ref2d["n_files"]},
        "main_tally_pin": None if main_cells is None else (
            f"PASS ({len(tally_pin)}/{len(tally_pin)} cells)"
            if not any(s.startswith("tally pin") for s in failures)
            else "FAIL"),
        "comparison_2d": None if cmp is None else {
            **{k: cmp[k] for k in ("auc", "block_p", "ci",
                                   "bootstrap_n_dropped")},
            "gate": "PASS" if not any(s.startswith("2d comparison")
                                      for s in failures) else "FAIL"},
        "outcome_known_answer_gate": None if outcome is None
        else outcome["known_answer_gate"],
        "floors": "PASS (doc §4 table; six option-listing rungs at "
                  "max(majority, 1/n))",
        "frozen_imports_2e": len(FROZEN_IMPORT_SHA256_2E),
    }
    if failures:
        v = insufficient_data_record_2e(failures, referents=referents,
                                        outcome=outcome)
    else:
        v = verdict_2e(outcome=outcome, main_cells=main_cells,
                       pilot_cells=pilot_cells, floors=floors, probe=probe,
                       cmp2d=cmp, referents=referents)
    if write:
        out = Path(out_path or RESULTS / "verdict.json")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(v, indent=1, default=str))
    return v


if __name__ == "__main__":
    v = run(write="--write" in sys.argv)
    print(json.dumps({k: v[k] for k in ("verdict", "reason", "primary",
                                        "referents")}, indent=1, default=str))
