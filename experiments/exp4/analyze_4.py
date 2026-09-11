# experiments/exp4/analyze_4.py
"""Experiment 4's analyzer (design `experiment-4-design.md` §3.5-§3.9,
§4, §5, §6; Task 4 brief + resolutions): the excess and its pre-clear
fraction phi, the rung-level sign-flip primary with its cluster-
bootstrap CI, the eligibility bootstrap (reference stage only), the
six-world tree, S1-S11 named secondaries (no alpha claim), the
sensitivities, and run() — the whole verdict path from committed bytes
to a written verdict.json / VERDICT.txt.

No torch import anywhere in this module; no model contact. Every
number the primary needs is re-derived from committed sets
(`sets/<rung>.npz`, git-tracked); the sensitivities that need
activations or a fixed pairing scalar (question-end, pooled, CKA, the
Huh max-over-pairs reading) are read from the committed `align.json`
and labelled ATTESTED, since the underlying activation files are
gitignored and may not exist at analysis time.

Task 4 resolutions applied here (see the task brief for the numbered
list): (1) `per_item_alignment_4`/`eligibility_table_4` re-derive
every overlap from committed set tables via `metric_4.overlap_counts`
and refuse on any disagreement with a stored `overlap_<ref>` array;
(4) `load_stage_tables_4`/`load_sweep_tables_4` apply STRICT pins
(n_hidden, sites, 34 rungs, 500 items, k, render, batch, committed
digest, prereg tag) via `battery_4.load_record_failures_4` plus the
extra n_hidden/sites/coverage checks that function does not itself
make; (6) `run()`'s refusal order is exactly the brief's list, every
step wrapped by `collect_total_4`; `REFERENTS_4_SHA256 = None` and
`IMPORTED_SHA256_4 = None` in this task (Task 5 fills)."""
from __future__ import annotations

import json
import subprocess
import sys
import zipfile
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

EXP4 = Path(__file__).resolve().parent
EXPERIMENTS = EXP4.parent
REPO = EXPERIMENTS.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp2d import analyze_2d as a2d  # noqa: E402
from experiments.exp2d import battery_2d as bt  # noqa: E402
from experiments.exp2d import stats_2d as st  # noqa: E402
from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp2g import predictor_2g as pr  # noqa: E402
from experiments.exp2g import stats_2g as sg2  # noqa: E402
from experiments.exp2g import strata_2g as sg  # noqa: E402
from experiments.exp2h import battery_2h as bh  # noqa: E402
from experiments.exp2i import analyze_2i as an2i  # noqa: E402
from experiments.exp4 import battery_4  # noqa: E402
from experiments.exp4 import collect_4  # noqa: E402
from experiments.exp4 import metric_4  # noqa: E402

# ---------------------------------------------------------------- worlds

WORLDS_4 = ("INSUFFICIENT_DATA", "NO-CONVERGENCE", "LEADS", "PARTIAL", "FOLLOWS", "UNDETERMINED")

T_BAR_4 = 0.25
ALPHA_4 = 0.01
N_BOOT_4 = 10_000
N_FLIP_SAMPLE_4 = 10_000
MAX_ENUMERATE_4 = 20
N_BOOT_ELIG_4 = 2000
MIN_CELLS_4 = 3
MIN_RUNGS_4 = 3
SE_MULTIPLE_4 = 2.0
MIN_CLEAR_INDEX_4 = 2
GATE0_MIN_FRACTION_4 = 0.90

REFERENTS_4_SHA256 = "432f645a9adb24bdec636d210f8dccebec0a0e636dd8466f6465fa82ea2c7e91"
# Task 5: exp4's OWN residual import surface -- every non-test module
# inside experiments/exp4 that is not one of the four blob-bound
# INSTRUMENT_BLOBS_4 files, from tests/import_scan_4.py's scan.
IMPORTED_SHA256_4 = {
    battery_4.REPO / "experiments/exp4/__init__.py":
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    battery_4.REPO / "experiments/exp4/make_referents_4.py":
        "e8b9cff34a34c830e2e07302eae6bcd811fe22fe978f77c0ea32ff07d4491b7e",
    battery_4.REPO / "experiments/exp4/power_4.py":
        "33b4ff53900d436a1353256b4d854787d59a29e0f9e49fde44d7c19d838b6419",
    battery_4.REPO / "experiments/exp4/run/__init__.py":
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    battery_4.REPO / "experiments/exp4/run/preflight_4.py":
        "865d4f8c08b66cb5be708af4e46f728b660fd5accb4b19c394142856a2a33057",
    battery_4.REPO / "experiments/exp4/verify_referents_4.py":
        "4e59bdfbb3ff1c8510324f80b2d1265300c0dd1c782d3559a09cb1a572d5d1b6",
}
REFERENTS_PATH_4 = EXP4 / "referents_4.json"   # Task 5 writes this file

KNOWN_OUTCOME_CAVEAT_4 = (
    "whatever fires is a preregistered reading on a known outcome, not a forecast"
)

_LICENSE_BODY_4 = {
    "LEADS": (
        "on N tasks across four families' training runs, the agreement between a model's "
        "representation of a task's items and three unrelated released models' ran ahead of "
        "the general convergence trend before the task first performed, by a preregistered "
        "margin, and the lens reading of Huh et al. is upgraded from a citation to a "
        "measurement at task grain in the scoreboard. Condition: LEADS on at least two of the "
        "four per-model readings (each at its own p < .05 and T >= .25); otherwise the sentence "
        "names the trajectories on which it held."
    ),
    "PARTIAL": (
        "a measurable part of the task-specific agreement precedes performance, below the "
        "preregistered quarter; the lens reading is supported in direction and bounded in size; "
        "the bar and T are printed."
    ),
    "FOLLOWS": (
        "the convergence paragraph is bounded: Huh et al.'s result stands as a statement about "
        "global representation, and on this battery the task-specific part of the agreement "
        "arrived with performance, not before -- the construction account's prediction, and the "
        "first place in the program where it is the one that held. 'There would be no reason for "
        "independent constructions to agree' is struck or qualified: the agreement that follows "
        "performance is exactly what agreeing on the answer produces."
    ),
    "UNDETERMINED": (
        "the blind region is the CI95 of T; nothing about precedence is licensed; the essay's "
        "paragraph gains only the disclosure that the test ran and where it stopped."
    ),
    "NO-CONVERGENCE": (
        "task-specific agreement above the flat pool is not measurable at the endpoint on fewer "
        "than three cells: the lens claim's premise -- that resolving a task makes independent "
        "lenses agree about its items -- does not show at this resolution; the paragraph is "
        "bounded to the global claim, with the endpoint excess table as the record."
    ),
    "INSUFFICIENT_DATA": "no licence: the run did not produce a verdict.",
}
LICENSED_4 = {w: f"{v} Disclosure (design §2): {KNOWN_OUTCOME_CAVEAT_4}." for w, v in _LICENSE_BODY_4.items()}

# ------------------------------------------------------------- rung types

_ARITHMETIC_4 = ("add3_mid", "sub3_mid", "add4_mid", "sub4_mid", "add_base8", "sub_base8",
                 "arith_next", "quad_next", "count_div13", "count_div7", "median5", "median7",
                 "oct2dec", "base7", "base12_digitsum", "base13", "mod13", "mod13_comp", "mod17",
                 "mod19", "isqrt_gap", "collatz_step2", "roman_sum7", "clock24", "clock24_d999")
_OPTION_4 = ("antonym", "antonym6", "odd6", "odd_one_out")
_STRING_4 = ("reverse_string", "rev_string7", "caesar", "caesar_len8", "hamming12")

RUNG_TYPE_4 = {}
for _r in _ARITHMETIC_4:
    RUNG_TYPE_4[_r] = "arithmetic"
for _r in _OPTION_4:
    RUNG_TYPE_4[_r] = "option"
for _r in _STRING_4:
    RUNG_TYPE_4[_r] = "string"
del _r
if set(RUNG_TYPE_4) != set(bt.RUNGS):
    raise RuntimeError(f"RUNG_TYPE_4 does not cover bt.RUNGS exactly: "
                       f"missing {sorted(set(bt.RUNGS) - set(RUNG_TYPE_4))}, "
                       f"extra {sorted(set(RUNG_TYPE_4) - set(bt.RUNGS))}")


def collect_total_4(thunk, label):
    """`an2i.collect_total` (2h's widened surface) plus `zipfile.
    BadZipFile` (a corrupted npz), `KeyError` (a missing npz member —
    already caught inside `an2i.collect_total`, re-declared here per
    the brief for clarity) and `OSError` (also already caught inside)."""
    try:
        return an2i.collect_total(thunk, label)
    except (zipfile.BadZipFile, KeyError, OSError) as e:
        return None, [f"{label}: {type(e).__name__}: {e}"]


def check_imports_4() -> None:
    """2j F-1 (2n's `check_imports_2n` shape, no upstream residual pins
    to fold in — exp4 is a fresh experiment): every module under
    `experiments/` this process has imported (excluding `tests/`) must
    be covered by `FROZEN_SHA256_4` (everything outside `experiments/
    exp4/`), `INSTRUMENT_BLOBS_4`, or `IMPORTED_SHA256_4` (exp4's own
    residual — everything inside `experiments/exp4/` that isn't one of
    the four instrument blobs), each byte-identical to its pin. `run()`
    only calls this when `imports_pinned` is truthy."""
    if IMPORTED_SHA256_4 is None:
        raise RuntimeError("IMPORTED_SHA256_4 is None — the import surface is not pinned "
                           "(build incomplete)")
    covered = {str(Path(p).resolve()) for p in battery_4.FROZEN_SHA256_4}
    covered |= {str((battery_4.REPO / rel).resolve()) for rel in battery_4.INSTRUMENT_BLOBS_4}
    pinned = {str(Path(p).resolve()): v for p, v in IMPORTED_SHA256_4.items()}
    drifted, unpinned = [], []
    for p, want in sorted(pinned.items()):
        pp = Path(p)
        if not pp.is_file() or bg.sha256_file(pp) != want:
            drifted.append(f"(pin) -> {p}")
    exp_root = str((battery_4.REPO / "experiments").resolve())
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


def _git_sha_4() -> str:
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=battery_4.REPO,
                          capture_output=True, text=True).stdout.strip()


# ---------------------------------------------------------- stage tables

def _traj_of_init_key(key: str) -> str:
    for traj, k in battery_4.INIT_KEY_4.items():
        if k == key:
            return traj
    raise ValueError(f"{key!r} is not an exp4 init key")


def _expected_fields_4(key) -> dict:
    """`{family, render, batch, refs, n_hidden, committed_digest}` for
    a reference-stage str key or a `(traj, step)` sweep unit — the
    SAME values every real runner call site used to write the unit,
    read fresh from `battery_4` (never from the record itself)."""
    if isinstance(key, (tuple, list)):
        traj, step = key
        family = collect_4.family_of_traj_4(traj)
        return dict(family=family, render=battery_4.RENDER_4[family],
                    batch=battery_4.BATCH_4[traj], refs=battery_4.REFS_FOR_4[traj],
                    n_hidden=battery_4.N_HIDDEN_PIN_4[traj],
                    committed_digest=battery_4.committed_step_digest_4(traj, step))
    if key in battery_4.REFERENCES_4:
        family = battery_4.FAMILY_OF_KEY_4[key]
        return dict(family=family, render=battery_4.RENDER_4[family],
                    batch=battery_4.BATCH_4[key], refs=(), n_hidden=battery_4.N_HIDDEN_PIN_4[key],
                    committed_digest=None)
    if key.startswith("endpoint_"):
        traj = key[len("endpoint_"):]
        family = battery_4.FAMILY_OF_KEY_4[key]
        return dict(family=family, render=battery_4.RENDER_4[family],
                    batch=battery_4.BATCH_4[key], refs=battery_4.REFS_FOR_4[traj],
                    n_hidden=battery_4.N_HIDDEN_PIN_4[key],
                    committed_digest=battery_4.committed_step_digest_4(
                        traj, battery_4.ENDPOINT_STEP_4[traj]))
    if key in battery_4.INIT_KEY_4.values():
        traj = _traj_of_init_key(key)
        family = battery_4.FAMILY_OF_KEY_4[key]
        return dict(family=family, render=battery_4.RENDER_4[family],
                    batch=battery_4.BATCH_4[key], refs=battery_4.REFS_FOR_4[traj],
                    n_hidden=battery_4.N_HIDDEN_PIN_4[key],
                    committed_digest=battery_4.committed_init_digest_4(traj))
    if key.startswith("ladder_pythia_"):
        family = "pythia"
        return dict(family=family, render=battery_4.RENDER_4[family],
                    batch=battery_4.BATCH_4[key], refs=collect_4.non_pythia_refs_4(),
                    n_hidden=battery_4.N_HIDDEN_PIN_4[key], committed_digest=None)
    raise ValueError(f"{key!r} is not a recognised exp4 key")


def _read_sets_and_overlaps(d: Path, rec: dict):
    """`{rung: uint16[n_sites,500,k]}`, `{ref: {rung: uint8[n_sites,500]}}`
    for every one of the 34 rungs — a short unit (any rung's `sets/
    <rung>.npz` missing, or fewer than 34 present) raises `ValueError`
    naming it."""
    sites = rec.get("sites") or []
    n_sites = len(sites)
    refs = rec.get("refs") or []
    sets_by_rung = {}
    overlaps_by_ref = {r: {} for r in refs}
    for rung in battery_4.RUNGS:
        p = d / "sets" / f"{rung}.npz"
        if not p.is_file():
            raise ValueError(f"{d}: sets/{rung}.npz missing — unit short "
                             f"({len(sets_by_rung)} of {len(battery_4.RUNGS)} rungs present)")
        with np.load(p) as z:
            sets = np.asarray(z["sets"])
            want_shape = (n_sites, battery_4.N_ITEMS, metric_4.K_4)
            if sets.shape != want_shape:
                raise ValueError(f"{d}/{rung}: sets shape {sets.shape} != {want_shape}")
            sets_by_rung[rung] = sets
            for ref in refs:
                name = f"overlap_{ref}"
                if name not in z.files:
                    raise ValueError(f"{d}/{rung}: {name} missing — a unit whose record "
                                     f"lists refs {refs!r} must carry one overlap_<ref> "
                                     f"array per (ref, rung)")
                overlaps_by_ref[ref][rung] = np.asarray(z[name])
    if set(sets_by_rung) != set(battery_4.RUNGS):
        raise ValueError(f"{d}: unit short — missing "
                         f"{sorted(set(battery_4.RUNGS) - set(sets_by_rung))}")
    return sets_by_rung, overlaps_by_ref


def _load_one_unit_4(root, key) -> dict:
    d = battery_4.key_dir_4(root, key)
    rec_path = d / "_load.json"
    if not rec_path.is_file():
        raise ValueError(f"{key}: unit missing ({rec_path})")
    rec = json.loads(rec_path.read_text())
    exp = _expected_fields_4(key)
    bad = battery_4.load_record_failures_4(
        rec, key=key, expected_family=exp["family"], expected_render=exp["render"],
        expected_batch=exp["batch"], expected_committed_digest=exp["committed_digest"],
        expected_refs=exp["refs"], root=root)
    if bad:
        raise ValueError(f"{key}: {bad}")
    if set(rec.get("sets_sha256") or {}) != set(battery_4.RUNGS):
        raise ValueError(f"{key}: sets_sha256 covers "
                         f"{sorted(set(rec.get('sets_sha256') or {}))} — unit short "
                         f"(need all {len(battery_4.RUNGS)} rungs)")
    if rec.get("n_hidden") != exp["n_hidden"]:
        raise ValueError(f"{key}: n_hidden {rec.get('n_hidden')!r} != pinned {exp['n_hidden']}")
    want_sites = metric_4.sites_4(exp["n_hidden"])
    if list(rec.get("sites") or []) != want_sites:
        raise ValueError(f"{key}: sites {rec.get('sites')!r} != {want_sites}")
    sets_by_rung, overlaps_by_ref = _read_sets_and_overlaps(d, rec)
    return {"record": rec, "sets": sets_by_rung, "overlaps": overlaps_by_ref}


def load_stage_tables_4(root, *, keys) -> dict:
    """`{key: {"record", "sets", "overlaps"}}` for every key in `keys`
    (a reference-stage str or a `(traj, step)` tuple), each strictly
    pinned via `_load_one_unit_4`."""
    return {key: _load_one_unit_4(root, key) for key in keys}


def load_sweep_tables_4(root, traj: str) -> dict:
    """`{step: {"record", "sets", "overlaps"}}` for every step of
    `GRID_4[traj]` (the first step and the endpoint both live under
    `unit_dir`, written by the reference stage and the sweep
    respectively — read uniformly here)."""
    return {step: _load_one_unit_4(root, (traj, step)) for step in battery_4.GRID_4[traj]}


# ------------------------------------------------------------- alignment

def per_item_alignment_4(tables_m: dict, ref_tables: dict, pairing_by_ref: dict) -> dict:
    """`{rung: float64[500]}` = mean over refs and M's sites of
    overlap/k, RE-DERIVED from the two set tables via `metric_4.
    overlap_counts` (through `collect_4.overlap_table_4`); asserts
    equality with the stored `overlap_<ref>` array when present,
    naming the rung/ref/site on disagreement."""
    sets_m = tables_m["sets"]
    stored = tables_m.get("overlaps") or {}
    out = {}
    for rung in battery_4.RUNGS:
        sm = sets_m[rung]
        per_ref = []
        for ref, pairing in pairing_by_ref.items():
            sq = ref_tables[ref][rung]
            ov = collect_4.overlap_table_4(sm, sq, pairing)
            stored_ov = (stored.get(ref) or {}).get(rung)
            if stored_ov is not None and not np.array_equal(stored_ov, ov):
                diff_sites = np.flatnonzero(~np.all(stored_ov == ov, axis=1))
                site0 = int(diff_sites[0]) if len(diff_sites) else -1
                raise ValueError(f"per_item_alignment_4: {rung}/{ref}/site{site0}: stored "
                                 f"overlap disagrees with the re-derived value")
            per_ref.append(ov.astype(np.float64) / metric_4.K_4)
        stacked = np.stack(per_ref, axis=0)          # [n_refs, n_sites, 500]
        out[rung] = stacked.mean(axis=(0, 1))
    return out


def _gate0_site_means_4(tables: dict, ref_tables: dict, pairing_by_ref: dict) -> dict:
    """`{rung: {ref: float64[n_sites]}}` = mean over items ONLY (sites
    AND references KEPT separate) of overlap/k, re-derived via
    `metric_4.overlap_counts` — the per-(rung, site, reference)
    granularity gate 0 needs (Task 5 finding 1: cells are per
    REFERENCE, not averaged over references first), at the prompt-end
    position (the committed `sets` are always prompt-end, per Task 3's
    storage convention)."""
    sets_m = tables["sets"]
    out = {}
    for rung in battery_4.RUNGS:
        sm = sets_m[rung]
        per_ref = {}
        for ref, pairing in pairing_by_ref.items():
            sq = ref_tables[ref][rung]
            ov = collect_4.overlap_table_4(sm, sq, pairing)      # [n_sites, 500] uint8
            per_ref[ref] = (ov.astype(np.float64) / metric_4.K_4).mean(axis=1)   # -> [n_sites]
        out[rung] = per_ref
    return out


def gate0_4(root, traj: str, ref_tables: dict, stage_tables: dict) -> dict:
    """Design §3.7 gate 0 — the instrument sees training: re-derived
    from the committed set tables of `INIT_KEY_4[traj]` (the seeded
    twin) and `endpoint_<traj>` (both already loaded in `stage_tables`
    — both are `STAGE1_KEYS_4` members). Task 5 finding 1: cells are
    per (rung, site, REFERENCE) — the twin's mean-over-items overlap
    with reference Q at site s must be below the endpoint's for the
    SAME (rung, s, Q), never averaged over references first. Passes
    iff the pooled `fraction_below` over all 34 x n_sites x n_refs
    cells is >= `GATE0_MIN_FRACTION_4` (0.90); a per-reference
    breakdown is also returned."""
    twin_key = battery_4.INIT_KEY_4[traj]
    endpoint_key = f"endpoint_{traj}"
    twin_tables = stage_tables[twin_key]
    endpoint_tables = stage_tables[endpoint_key]
    twin_site = _gate0_site_means_4(twin_tables, ref_tables, twin_tables["record"]["pairing"])
    endpoint_site = _gate0_site_means_4(endpoint_tables, ref_tables,
                                        endpoint_tables["record"]["pairing"])
    below, total = 0, 0
    per_ref_below: dict = {}
    per_ref_total: dict = {}
    for rung in battery_4.RUNGS:
        tw_by_ref, ep_by_ref = twin_site[rung], endpoint_site[rung]
        for ref in tw_by_ref:
            tw, ep = tw_by_ref[ref], ep_by_ref[ref]
            b = int(np.sum(tw < ep))
            n = int(tw.shape[0])
            below += b; total += n
            per_ref_below[ref] = per_ref_below.get(ref, 0) + b
            per_ref_total[ref] = per_ref_total.get(ref, 0) + n
    fraction_below = (below / total) if total else 0.0
    per_reference = {
        ref: {"fraction_below": float(per_ref_below[ref] / per_ref_total[ref])
             if per_ref_total[ref] else 0.0, "n_cells": int(per_ref_total[ref])}
        for ref in per_ref_total
    }
    return {"fraction_below": float(fraction_below), "n_cells": int(total),
           "per_reference": per_reference,
           "pass": bool(fraction_below >= GATE0_MIN_FRACTION_4)}


def alignment_series_4(root, traj: str, ref_tables: dict, stage_tables: dict) -> dict:
    """`{"steps", "a": {rung: [per step]}, "per_item": {step: {rung:
    float64[500]}}}` over `GRID_4[traj]`, from `stage_tables` (a
    pre-loaded `load_sweep_tables_4` result) — the first step's and
    the endpoint's tables are exactly those the reference stage / gate
    1 wrote, read uniformly with every other grid step."""
    steps = list(battery_4.GRID_4[traj])
    per_item, a = {}, {r: [] for r in battery_4.RUNGS}
    for step in steps:
        unit = stage_tables[step]
        pairing_by_ref = unit["record"]["pairing"]
        pia = per_item_alignment_4(unit, ref_tables, pairing_by_ref)
        per_item[step] = pia
        for r in battery_4.RUNGS:
            a[r].append(float(pia[r].mean()))
    return {"steps": steps, "a": a, "per_item": per_item}


# --------------------------------------------------- primary code (exact)

def trend_4(a, flat, steps):
    if not flat:
        raise ValueError("trend_4: no flat rungs")
    return [float(np.mean([a[r][i] for r in flat])) for i in range(len(steps))]


def excess_4(a, trend, steps):
    out = {}
    for r, series in a.items():
        out[r] = [float((series[i] - series[0]) - (trend[i] - trend[0])) for i in range(len(steps))]
    return out


def phi_4(x, t_clear_index):
    if t_clear_index is None or t_clear_index < MIN_CLEAR_INDEX_4:
        return None
    if x[-1] == 0.0:
        return None
    return float(x[t_clear_index - 1] / x[-1])


def _flip_signs(n_rungs, *, seed):
    if n_rungs <= MAX_ENUMERATE_4:
        m = 1 << n_rungs
        bits = ((np.arange(m)[:, None] >> np.arange(n_rungs)[None, :]) & 1)
        return (1 - 2 * bits).astype(np.int8), "exact"
    rng = np.random.default_rng(seed)
    return rng.choice(np.array([-1, 1], dtype=np.int8), size=(N_FLIP_SAMPLE_4, n_rungs)), "sampled"


def _per_type(cells):
    out = {}
    for typ in ("arithmetic", "option", "string"):
        sub = [c for c in cells if RUNG_TYPE_4.get(c["rung"]) == typ]
        if not sub:
            out[typ] = None
            continue
        rungs_t = sorted({c["rung"] for c in sub})
        idx_t = {r: i for i, r in enumerate(rungs_t)}
        phi_t = np.array([c["phi"] for c in sub], dtype=np.float64)
        rid_t = np.array([idx_t[c["rung"]] for c in sub])
        S_t, method_t = _flip_signs(len(rungs_t), seed=0)
        sums_t = np.zeros(len(rungs_t)); np.add.at(sums_t, rid_t, phi_t)
        T_t = float(phi_t.mean())
        flips_t = (S_t @ sums_t) / len(sub)
        out[typ] = {"T": T_t, "n_cells": len(sub), "n_rungs": len(rungs_t),
                    "p_plus": float(np.mean(flips_t >= T_t - 1e-15)), "flip_method": method_t}
    return out


def primary_4(cells, *, n_boot=N_BOOT_4, seed=0):
    if not cells:
        raise ValueError("primary_4: no cells")
    rungs = sorted({c["rung"] for c in cells})
    idx = {r: i for i, r in enumerate(rungs)}
    phi = np.array([c["phi"] for c in cells], dtype=np.float64)
    rid = np.array([idx[c["rung"]] for c in cells])
    T = float(phi.mean())
    S, method = _flip_signs(len(rungs), seed=seed)
    per_rung_sum = np.zeros(len(rungs)); np.add.at(per_rung_sum, rid, phi)
    T_flip = (S @ per_rung_sum) / len(cells)
    p_plus = float(np.mean(T_flip >= T - 1e-15)); p_minus = float(np.mean(T_flip <= T + 1e-15))
    rng = np.random.default_rng(seed + 1)
    boots = []
    for _ in range(n_boot):
        pick = rng.integers(0, len(rungs), size=len(rungs))
        vals = np.concatenate([phi[rid == j] for j in pick])
        boots.append(vals.mean())
    lo, hi = np.percentile(boots, [2.5, 97.5])
    per_traj = {}
    for t in sorted({c["traj"] for c in cells}):
        sub = [c for c in cells if c["traj"] == t]
        rungs_t = sorted({c["rung"] for c in sub})
        idx_t = {r: i for i, r in enumerate(rungs_t)}
        phi_t = np.array([c["phi"] for c in sub], dtype=np.float64)
        rid_t = np.array([idx_t[c["rung"]] for c in sub])
        S_t, method_t = _flip_signs(len(rungs_t), seed=seed)
        sums_t = np.zeros(len(rungs_t)); np.add.at(sums_t, rid_t, phi_t)
        T_t = float(phi_t.mean()); flips_t = (S_t @ sums_t) / len(sub)
        per_traj[t] = {"T": T_t, "n_cells": len(sub), "n_rungs": len(rungs_t),
                       "p_plus": float(np.mean(flips_t >= T_t - 1e-15)), "flip_method": method_t}
    return {"T": T, "n_cells": len(cells), "n_rungs": len(rungs), "rungs": rungs, "p_plus": p_plus,
            "p_minus": p_minus, "flip_method": method, "n_flips": int(S.shape[0]), "ci95": [float(lo), float(hi)],
            "n_boot": n_boot, "per_traj": per_traj, "per_type": _per_type(cells), "t_bar": T_BAR_4, "alpha": ALPHA_4}


def verdict_tree_4(failures, n_eligible_cells, n_eligible_rungs, primary):
    if failures:
        return {"verdict": "INSUFFICIENT_DATA", "reason": "; ".join(failures[:5])}
    if n_eligible_cells < MIN_CELLS_4 or n_eligible_rungs < MIN_RUNGS_4:
        return {"verdict": "NO-CONVERGENCE", "reason": f"{n_eligible_cells} eligible cells on {n_eligible_rungs} rungs (need {MIN_CELLS_4}/{MIN_RUNGS_4})"}
    T, p, ci = primary["T"], primary["p_plus"], primary["ci95"]
    if p < ALPHA_4 and T >= T_BAR_4:
        return {"verdict": "LEADS", "reason": f"T {T:.4f} ≥ {T_BAR_4}, p+ {p:.4g} < {ALPHA_4}"}
    if p < ALPHA_4 and 0 < T < T_BAR_4:
        return {"verdict": "PARTIAL", "reason": f"T {T:.4f} in (0, {T_BAR_4}), p+ {p:.4g} < {ALPHA_4} — real, below the bar"}
    if p >= ALPHA_4 and ci[1] < T_BAR_4:
        return {"verdict": "FOLLOWS", "reason": f"p+ {p:.4g} ≥ {ALPHA_4} and CI95 upper {ci[1]:.4f} < {T_BAR_4}"}
    return {"verdict": "UNDETERMINED", "reason": f"T {T:.4f}, p+ {p:.4g}, p− {primary['p_minus']:.4g}, CI95 {ci}"}


# --------------------------------------------------------------- eligibility

def eligibility_table_4(root, *, n_boot=N_BOOT_ELIG_4, seed=0) -> dict:
    """Per trajectory, from `reference/endpoint_<M>/` and the first
    unit ONLY (no other sweep unit is read): per rung in R_M `{x_end,
    se, eligible, reason, t_clear, t_clear_index}`, per rung in flat_M
    `{se_at_end}`, the trend at t_1/t_end, flat/transient, n_boot,
    seed, steps_used."""
    battery = bt.load_battery()
    floors = bg.load_floors()
    n = battery_4.N_ITEMS
    out = {}
    for traj in battery_4.TRAJECTORIES_4:
        outcome = battery_4.load_outcome_4(traj, battery=battery)
        rs = battery_4.rung_sets_4(outcome, floors)
        R, flat = rs["R"], rs["flat"]
        steps = list(battery_4.GRID_4[traj])
        first_step, endpoint_step = steps[0], steps[-1]

        refs = battery_4.REFS_FOR_4[traj]
        ref_tables_raw = collect_4.load_ref_tables_4(root, refs)
        ref_tables = {ref: rt["sets"] for ref, rt in ref_tables_raw.items()}

        unit_t1 = _load_one_unit_4(root, (traj, first_step))
        unit_end = _load_one_unit_4(root, f"endpoint_{traj}")
        pia_t1 = per_item_alignment_4(unit_t1, ref_tables, unit_t1["record"]["pairing"])
        pia_end = per_item_alignment_4(unit_end, ref_tables, unit_end["record"]["pairing"])

        rng = np.random.default_rng(seed)

        def boot(rung):
            idx = rng.integers(0, n, size=(n_boot, n))
            a_t1 = pia_t1[rung][idx].mean(axis=1)
            a_e = pia_end[rung][idx].mean(axis=1)
            return a_t1, a_e

        flat_boot_t1, flat_boot_e = [], []
        for r in flat:
            a_t1, a_e = boot(r)
            flat_boot_t1.append(a_t1); flat_boot_e.append(a_e)
        if flat:
            trend_boot_t1 = np.mean(flat_boot_t1, axis=0)
            trend_boot_e = np.mean(flat_boot_e, axis=0)
            trend_point_t1 = float(np.mean([pia_t1[r].mean() for r in flat]))
            trend_point_e = float(np.mean([pia_end[r].mean() for r in flat]))
        else:
            trend_boot_t1 = np.zeros(n_boot); trend_boot_e = np.zeros(n_boot)
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
            tclear = rs["t_clear"][r]
            tci = steps.index(tclear) if tclear is not None else None
            below_se = not (x_end_point >= SE_MULTIPLE_4 * se)
            no_window = tci is None or tci < MIN_CLEAR_INDEX_4
            eligible = (not below_se) and (not no_window)
            if below_se:
                reason = "endpoint excess below 2 SE"
            elif no_window:
                reason = "no pre-clear window (t_clear at grid index < 2)"
            else:
                reason = "eligible"
            per_rung_R[r] = {"x_end": x_end_point, "se": se, "eligible": bool(eligible),
                             "reason": reason, "t_clear": tclear, "t_clear_index": tci}

        out[traj] = {"R": per_rung_R, "flat": {r: {"se_at_end": se_flat[r]} for r in flat},
                    "transient": list(rs["transient"]), "trend_t1": trend_point_t1,
                    "trend_end": trend_point_e, "n_boot": n_boot, "seed": seed,
                    "steps_used": [first_step, endpoint_step]}
    return out


def cells_4(series_by_traj, rung_sets_by_traj, eligibility) -> list:
    out = []
    for traj, series in series_by_traj.items():
        rs = rung_sets_by_traj[traj]
        elig = (eligibility.get(traj) or {}).get("R") or {}
        trend = trend_4(series["a"], rs["flat"], series["steps"])
        excess = excess_4(series["a"], trend, series["steps"])
        for rung in rs["R"]:
            e = elig.get(rung)
            if not e or not e.get("eligible"):
                continue
            tci = e["t_clear_index"]
            x = excess[rung]
            phi = phi_4(x, tci)
            if phi is None:
                continue
            steps = series["steps"]
            out.append({"traj": traj, "rung": rung, "phi": phi, "t_clear": e["t_clear"],
                       "t_minus": steps[tci - 1], "x_end": x[-1], "x_pre": x[tci - 1]})
    return out


# ---------------------------------------------------------- S2 known-answer

def s2_known_answer_gates_4() -> dict:
    """Reproduces 2d's AUC .5454545454545454 from `exp2d/results/
    verdict.json` `per_rung[r]["predictor_score"]` and 2e's
    .6126482213438735 from `exp2e/results/verdict.json`
    `per_rung[r]["F1"]`, both against `per_rung[r]["rising"]`, through
    `stats_2d.primary_test` in `analyze_2d._family_contiguous` layout."""
    fams = [bt.FAMILY_OF[r] for r in bt.RUNGS]

    v2d = json.loads((a2d.EXP2D / "results" / "verdict.json").read_bytes())
    pr2d = v2d["per_rung"]
    y2d = a2d._family_contiguous({r: int(pr2d[r]["rising"]) for r in bt.RUNGS})
    x2d = a2d._family_contiguous({r: pr2d[r]["predictor_score"] for r in bt.RUNGS})
    res2d = st.primary_test(x2d, y2d, bt.FAMILY_SIZES, fams)

    exp2e = EXPERIMENTS / "exp2e"
    v2e = json.loads((exp2e / "results" / "verdict.json").read_bytes())
    pr2e = v2e["per_rung"]
    y2e = a2d._family_contiguous({r: int(pr2e[r]["rising"]) for r in bt.RUNGS})
    x2e = a2d._family_contiguous({r: pr2e[r]["F1"] for r in bt.RUNGS})
    res2e = st.primary_test(x2e, y2e, bt.FAMILY_SIZES, fams)

    auc_2d, auc_2e = res2d["auc"], res2e["auc"]
    if abs(auc_2d - 0.5454545454545454) >= 1e-12:
        raise ValueError(f"s2_known_answer_gates_4: 2d's AUC reproduced as {auc_2d!r}")
    if abs(auc_2e - 0.6126482213438735) >= 1e-12:
        raise ValueError(f"s2_known_answer_gates_4: 2e's AUC reproduced as {auc_2e!r}")
    return {"auc_2d": auc_2d, "auc_2e": auc_2e, "no_alpha_claim": True}


# ------------------------------------------------------------- secondaries

def _align_by_step_4(root, traj, steps=None):
    steps = steps or battery_4.GRID_4[traj]
    return {s: json.loads((battery_4.unit_dir(root, traj, s) / "align.json").read_text())
           for s in steps}


def s1_order_4(series_by_traj, rung_sets_by_traj, *, frac=0.5) -> dict:
    """Somers' D (concordant-discordant, ties in either excluded)
    between the excess's frac-rise grid index and t_clear(r)'s grid
    index, per traj over R_M, pooled = mean over trajs; the
    descriptive block p via `stats_2d.spearman_block_p` in
    `analyze_2d._restricted_layout`'s family-contiguous subset."""
    per_traj, ds = {}, []
    for traj, rs in rung_sets_by_traj.items():
        series = series_by_traj.get(traj)
        if series is None:
            continue
        steps = series["steps"]
        trend = trend_4(series["a"], rs["flat"], steps)
        excess = excess_4(series["a"], trend, steps)
        half_idx, clear_idx, rungs_used = [], [], []
        for r in rs["R"]:
            x = excess[r]
            xe = x[-1]
            if xe == 0:
                continue
            target = frac * xe
            hi = next((i for i, v in enumerate(x)
                      if (v >= target if xe > 0 else v <= target)), None)
            ci = steps.index(rs["t_clear"][r]) if rs["t_clear"][r] is not None else None
            if hi is None or ci is None:
                continue
            half_idx.append(hi); clear_idx.append(ci); rungs_used.append(r)
        c = d = 0
        for i in range(len(rungs_used)):
            for j in range(i + 1, len(rungs_used)):
                dx, dy = half_idx[i] - half_idx[j], clear_idx[i] - clear_idx[j]
                if dx == 0 or dy == 0:
                    continue
                if (dx > 0) == (dy > 0):
                    c += 1
                else:
                    d += 1
        d_val = None if (c + d) == 0 else (c - d) / (c + d)
        block = None
        if len(rungs_used) >= 2 and len(set(half_idx)) > 1 and len(set(clear_idx)) > 1:
            keep_mask = [r in rungs_used for r in bt.RUNGS]
            kept, sizes, _fams = a2d._restricted_layout(keep_mask)
            order_idx = {r: k for k, r in enumerate(rungs_used)}
            xarr = [half_idx[order_idx[r]] for r in kept]
            yarr = [clear_idx[order_idx[r]] for r in kept]
            block = st.spearman_block_p(xarr, yarr, sizes)
        per_traj[traj] = {"d": d_val, "n_concordant": c, "n_discordant": d,
                          "n_rungs": len(rungs_used), "block": block}
        if d_val is not None:
            ds.append(d_val)
    pooled = float(np.mean(ds)) if ds else None
    return {"pooled_d": pooled, "per_traj": per_traj, "source": "re-derived", "no_alpha_claim": True}


def s2_from_below_4(root) -> dict:
    """The design §3.5 two-point excess: x_r(1b) = (a_r(1b) -
    a_r(70m)) - (trend(1b) - trend(70m)), trend = the Pythia ladder's
    23 flat rungs (2d's own flat rungs), a_r at Pythia's 1b/70m `main`
    against the three non-Pythia references — as the predictor in 2d's
    rung-level primary — AUC rising vs flat over the 34 rungs; 2d's
    bars printed for comparison, not applied."""
    non_pythia = collect_4.non_pythia_refs_4()
    ref_tables = {ref: rt["sets"] for ref, rt in
                 collect_4.load_ref_tables_4(root, non_pythia).items()}
    unit_1b = _load_one_unit_4(root, "ladder_pythia_1b")
    unit_70m = _load_one_unit_4(root, "ladder_pythia_70m")
    pia_1b = per_item_alignment_4(unit_1b, ref_tables, unit_1b["record"]["pairing"])
    pia_70m = per_item_alignment_4(unit_70m, ref_tables, unit_70m["record"]["pairing"])
    a_1b = {r: float(pia_1b[r].mean()) for r in bt.RUNGS}
    a_70m = {r: float(pia_70m[r].mean()) for r in bt.RUNGS}

    v2d = json.loads((a2d.EXP2D / "results" / "verdict.json").read_bytes())
    rising = {r: bool(v2d["per_rung"][r]["rising"]) for r in bt.RUNGS}
    flat_rungs = [r for r in bt.RUNGS if not rising[r]]
    trend_1b = float(np.mean([a_1b[r] for r in flat_rungs])) if flat_rungs else 0.0
    trend_70m = float(np.mean([a_70m[r] for r in flat_rungs])) if flat_rungs else 0.0
    x_r = {r: (a_1b[r] - a_70m[r]) - (trend_1b - trend_70m) for r in bt.RUNGS}
    x = a2d._family_contiguous(x_r)
    y = a2d._family_contiguous({r: int(rising[r]) for r in bt.RUNGS})
    fams = [bt.FAMILY_OF[r] for r in bt.RUNGS]
    res = st.primary_test(x, y, bt.FAMILY_SIZES, fams)
    return {"auc": res["auc"], "block_p": res["block"]["p"], "ci95": res["bootstrap"]["ci"],
           "bar_2d_sampled": 0.5454545454545454, "bar_2d_floor_adjusted": 0.6126482213438735,
           "source": "re-derived", "no_alpha_claim": True}


def s2_per_trajectory_4(series_by_traj, rung_sets_by_traj) -> dict:
    """The design §3.5 two-point excess at each trajectory's own first
    two grid points: x_r(t2) = (a_r(t2) - a_r(t1)) - (trend(t2) -
    trend(t1)), trend = M's own flat rungs, against rising-vs-flat at
    M's own endpoint (rs["R"])."""
    out = {}
    for traj, rs in rung_sets_by_traj.items():
        series = series_by_traj.get(traj)
        if series is None or len(series["steps"]) < 2:
            out[traj] = None
            continue
        a_t1 = {r: series["a"][r][0] for r in bt.RUNGS}
        a_t2 = {r: series["a"][r][1] for r in bt.RUNGS}
        flat = rs["flat"]
        if not flat:
            out[traj] = None
            continue
        trend_t1 = float(np.mean([a_t1[r] for r in flat]))
        trend_t2 = float(np.mean([a_t2[r] for r in flat]))
        elig_rungs = sorted(set(rs["R"]) | set(flat))
        x = np.array([(a_t2[r] - a_t1[r]) - (trend_t2 - trend_t1) for r in elig_rungs])
        y = np.array([1 if r in rs["R"] else 0 for r in elig_rungs])
        auc = None
        if (y == 1).any() and (y == 0).any():
            try:
                auc = st.auc(x, y)
            except ValueError:
                auc = None
        out[traj] = {"auc": auc, "n_rising": int((y == 1).sum()), "n_flat": int((y == 0).sum()),
                    "source": "re-derived", "no_alpha_claim": True}
    return out


def _load_global(root, key):
    p = battery_4.global_sets_path(root, key)
    with np.load(p) as z:
        return np.asarray(z["sets"])


def s3_scale_4(root) -> dict:
    """Alignment as a function of scale: Pythia 70m..12b at `main`,
    each against the three non-Pythia references, per rung: Spearman
    of a_r with log parameters; the largest single-step share of the
    total rise; the global-bank reading (S3's global-bank part is
    'not available' when `global.npz` was not committed for a key —
    disclosed rather than silently omitted)."""
    non_pythia = collect_4.non_pythia_refs_4()
    ref_tables_raw = collect_4.load_ref_tables_4(root, non_pythia)
    ref_tables = {ref: rt["sets"] for ref, rt in ref_tables_raw.items()}
    sizes = battery_4.LADDER_SIZES_4
    a_by_size = {}
    units = {}
    pairings = {}
    for size in sizes:
        key = "ref_pythia_12b" if size == "12b" else f"ladder_pythia_{size}"
        unit = _load_one_unit_4(root, key)
        units[size] = (key, unit)
        pairing_by_ref = unit["record"]["pairing"]
        if not pairing_by_ref:
            # A reference-stage key (e.g. ref_pythia_12b, "12b" on
            # this axis) is written with refs=() -- its OWN record
            # carries no pairing against the non-Pythia references.
            # Re-derive it directly, the same way S8's within-family
            # reading does; without this, `per_item_alignment_4` was
            # handed an empty pairing dict and `np.stack([])` on zero
            # per-ref arrays raised "need at least one array to
            # stack" -- a real, pre-existing crash on ANY tree (not
            # only synthetic worlds), never caught before because no
            # test checked S3's actual VALUE, only that the key
            # existed in `secondaries`.
            sites_u, n_hidden_u = unit["record"]["sites"], unit["record"]["n_hidden"]
            pairing_by_ref = {
                ref: collect_4._pairing_positions(sites_u, n_hidden_u,
                                                  ref_tables_raw[ref]["sites"],
                                                  ref_tables_raw[ref]["n_hidden"])
                for ref in non_pythia
            }
        pairings[size] = pairing_by_ref
        pia = per_item_alignment_4(unit, ref_tables, pairing_by_ref)
        a_by_size[size] = {r: float(pia[r].mean()) for r in bt.RUNGS}
    logp = np.array([np.log(battery_4.PYTHIA_PARAMS_4[s]) for s in sizes])
    per_rung = {}
    for r in bt.RUNGS:
        vals = np.array([a_by_size[s][r] for s in sizes])
        rho = float(spearmanr(vals, logp).statistic) if len(set(vals.tolist())) > 1 else None
        rise = vals[-1] - vals[0]
        share = float(np.max(np.diff(vals)) / rise) if rise > 0 else None
        per_rung[r] = {"a_by_size": {s: a_by_size[s][r] for s in sizes},
                       "rho_log_params": rho, "max_single_step_share": share}
    global_reading = None
    try:
        refs_global = {ref: _load_global(root, ref) for ref in non_pythia}
        means = {}
        for size in sizes:
            key, unit = units[size]
            g = _load_global(root, key)
            pairing = pairings[size]
            vals = []
            for ref in non_pythia:
                ov = collect_4.overlap_table_4(g, refs_global[ref], pairing[ref])
                vals.append(float((ov.astype(np.float64) / metric_4.K_4).mean()))
            means[size] = float(np.mean(vals))
        vals = np.array([means[s] for s in sizes])
        rho = float(spearmanr(vals, logp).statistic) if len(set(vals.tolist())) > 1 else None
        global_reading = {"a_by_size": means, "rho_log_params": rho, "available": True}
    except (FileNotFoundError, OSError, zipfile.BadZipFile, ValueError):
        global_reading = {"available": False,
                          "note": "global.npz not committed for one or more ladder keys"}
    return {"per_rung": per_rung, "sizes": list(sizes), "global": global_reading,
           "source": "re-derived", "no_alpha_claim": True}


def _argmax_correct_4(root_2d, size, rung):
    p = a2d.argmax_record_path(root_2d, size, rung)
    rec = json.loads(p.read_text())
    if rec.get("rung") != rung or rec.get("size") != size:
        raise ValueError(f"argmax record {p}: shape mismatch")
    return int(rec["correct"])


def _m4_count_4(size, rung):
    if size == "6.9b":
        return bh.load_m4_counts_69(rungs=(rung,))[rung]
    return bg.load_m4_counts(size, rungs=(rung,))[rung]


AXIS_SIZES_4 = ("70m", "410m", "1b", "2.8b", "6.9b", "12b")   # I-3: the outcome axis only


def s4_size_axis_4(s3_result) -> dict:
    """The size-axis pre-clear fraction over the 11 rising Pythia-
    ladder rungs, on the six-point OUTCOME axis {70m, 410m, 1b, 2.8b,
    6.9b, 12b} (t_1 = 70m; 160m and 1.4b are S3-curve-only points, not
    part of this axis, so a rung first clearing at 410m has index 1
    and is excluded by MIN_CLEAR_INDEX_4, and a rung first clearing at
    2.8b reads t_minus = 1b), the 23 flat rungs as trend."""
    v2d = json.loads((a2d.EXP2D / "results" / "verdict.json").read_bytes())
    rising_2d = [r for r in bt.RUNGS if v2d["per_rung"][r]["rising"]]
    flat_2d = [r for r in bt.RUNGS if not v2d["per_rung"][r]["rising"]]
    sizes = list(AXIS_SIZES_4)
    a = {r: [s3_result["per_rung"][r]["a_by_size"][s] for s in sizes] for r in bt.RUNGS}
    trend = trend_4(a, flat_2d, sizes)
    excess = excess_4(a, trend, sizes)
    outcome_sizes = ("410m", "1b", "2.8b", "6.9b", "12b")
    floors = bg.load_floors()
    per_rung = {}
    for r in rising_2d:
        first_clear_size = None
        for size in outcome_sizes:
            correct = (_argmax_correct_4(a2d.EXP2D, size, r) if size in ("410m", "1b")
                      else _m4_count_4(size, r))
            if st.binomial_bar(correct, bt.N_ITEMS, floors[r])["significant"]:
                first_clear_size = size
                break
        if first_clear_size is None:
            per_rung[r] = {"phi": None, "first_clear_size": None}
            continue
        tci = sizes.index(first_clear_size)
        per_rung[r] = {"phi": phi_4(excess[r], tci), "first_clear_size": first_clear_size,
                       "t_clear_index": tci, "x_end": excess[r][-1]}
    return {"per_rung": per_rung, "sizes": sizes, "source": "re-derived", "no_alpha_claim": True}


def s5_site_sensitivities_4(root, traj, rung_sets, eligibility_R) -> dict:
    """(a) max over all site pairs, (b) the single site with the
    largest endpoint excess read along the trajectory, (c) the final
    layer only — all from the per-site data `align.json` already
    carries. The three parts are computed INDEPENDENTLY (I-5): (a)'s
    attested `knn_max_over_pairs_prompt_end` reading is `None` on any
    unit built with `compute_max_pairs=False` (most sweep units, per
    the worlds' own construction) — that degrades ONLY part (a) to
    `{"available": False}`, never the whole function to a `failed`
    entry; (b)/(c) read `knn_prompt_end`, which is always populated."""
    steps = list(battery_4.GRID_4[traj])
    refs = battery_4.REFS_FOR_4[traj]
    align_by_step = _align_by_step_4(root, traj, steps)
    n_sites = len(json.loads((battery_4.unit_dir(root, traj, steps[0]) / "_load.json")
                             .read_text())["sites"])

    def series_per_site(rung):
        out = np.zeros((n_sites, len(steps)))
        for j, s in enumerate(steps):
            entry = align_by_step[s][rung]
            vals = np.mean([entry[ref]["knn_prompt_end"] for ref in refs], axis=0)
            out[:, j] = vals
        return out

    def series_max_pairs(rung):
        vals = []
        for s in steps:
            per_ref = [align_by_step[s][rung][ref].get("knn_max_over_pairs_prompt_end")
                      for ref in refs]
            if any(v is None for v in per_ref):
                return None
            vals.append(float(np.mean(per_ref)))
        return vals

    flat = rung_sets["flat"]
    flat_site = {r: series_per_site(r) for r in flat}
    trend_final = (trend_4({r: flat_site[r][-1, :].tolist() for r in flat}, flat, steps)
                  if flat else [0.0] * len(steps))
    trend_site_arr = (np.mean([flat_site[r] for r in flat], axis=0) if flat
                      else np.zeros((n_sites, len(steps))))

    flat_max = {r: series_max_pairs(r) for r in flat} if flat else {}
    max_pairs_available = bool(flat) and all(v is not None for v in flat_max.values())
    trend_max = trend_4(flat_max, flat, steps) if max_pairs_available else None

    out = {"max_over_pairs": {}, "best_site": {}, "final_layer": {},
          "source": "attested", "no_alpha_claim": True}
    for rung in rung_sets["R"]:
        e = eligibility_R.get(rung)
        if not e or not e.get("eligible"):
            continue
        tci = e["t_clear_index"]

        if max_pairs_available:
            a_max_r = series_max_pairs(rung)
            if a_max_r is None:
                out["max_over_pairs"][rung] = {"available": False}
            else:
                x_max = excess_4({rung: a_max_r}, trend_max, steps)[rung]
                out["max_over_pairs"][rung] = {"available": True, "phi": phi_4(x_max, tci),
                                               "x_end": x_max[-1]}
        else:
            out["max_over_pairs"][rung] = {"available": False}

        site_r = series_per_site(rung)
        a_final_r = site_r[-1, :].tolist()
        x_final = excess_4({rung: a_final_r}, trend_final, steps)[rung]
        out["final_layer"][rung] = {"phi": phi_4(x_final, tci), "x_end": x_final[-1]}

        excess_site = (site_r - site_r[:, [0]]) - (trend_site_arr - trend_site_arr[:, [0]])
        best = int(np.argmax(excess_site[:, -1]))
        x_best = excess_site[best, :].tolist()
        out["best_site"][rung] = {"site_index": best, "phi": phi_4(x_best, tci), "x_end": x_best[-1]}
    return out


def s6_question_end_4(root, traj, rung_sets, eligibility_R) -> dict:
    steps = list(battery_4.GRID_4[traj])
    refs = battery_4.REFS_FOR_4[traj]
    align_by_step = _align_by_step_4(root, traj, steps)

    def series(r):
        vals = []
        for s in steps:
            per_ref = [align_by_step[s][r][ref]["knn_question_end"] for ref in refs]
            if any(v is None for v in per_ref):
                return None
            vals.append(float(np.mean([np.mean(v) for v in per_ref])))
        return vals

    flat = rung_sets["flat"]
    a_flat = {r: v for r, v in ((r, series(r)) for r in flat) if v is not None}
    if not a_flat:
        return {"available": False, "source": "attested", "no_alpha_claim": True}
    trend = trend_4(a_flat, list(a_flat), steps)
    out = {}
    for rung in rung_sets["R"]:
        e = eligibility_R.get(rung)
        if not e or not e.get("eligible"):
            continue
        a_r = series(rung)
        if a_r is None:
            out[rung] = None
            continue
        x = excess_4({rung: a_r}, trend, steps)[rung]
        out[rung] = {"phi": phi_4(x, e["t_clear_index"]), "x_end": x[-1]}
    return {"available": True, "per_rung": out, "source": "attested", "no_alpha_claim": True}


def s7_huh_construction_4(root, traj, rung_sets, eligibility_R) -> dict:
    """Huh et al.'s own construction reproduced: pooled, max over
    block pairs, k=10, per rung; the global-bank pooled reading is not
    computed by this build (disclosed) since only the prompt-end
    global bank was committed."""
    steps = list(battery_4.GRID_4[traj])
    refs = battery_4.REFS_FOR_4[traj]
    align_by_step = _align_by_step_4(root, traj, steps)

    def series_pooled_max(rung):
        vals = []
        for s in steps:
            per_ref = [align_by_step[s][rung][ref]["knn_max_over_pairs_pooled"] for ref in refs]
            if any(v is None for v in per_ref):
                return None
            vals.append(float(np.mean(per_ref)))
        return vals

    flat = rung_sets["flat"]
    a_flat = {r: v for r, v in ((r, series_pooled_max(r)) for r in flat) if v is not None}
    per_rung = {}
    if a_flat:
        trend = trend_4(a_flat, list(a_flat), steps)
        for rung in rung_sets["R"]:
            e = eligibility_R.get(rung)
            if not e or not e.get("eligible"):
                continue
            a_r = series_pooled_max(rung)
            if a_r is None:
                per_rung[rung] = None
                continue
            x = excess_4({rung: a_r}, trend, steps)[rung]
            per_rung[rung] = {"phi": phi_4(x, e["t_clear_index"]), "x_end": x[-1]}
    return {"per_rung": per_rung, "global_bank": None,
           "note": "pooled global bank not committed by this build (Task 3 stores the "
                   "prompt-end position's global bank only)",
           "source": "attested", "no_alpha_claim": True}


def s8_referents_4(root, series_by_traj) -> dict:
    """The twins' alignments per rung; Pythia 2.8b's real step 0
    beside them (`init_pythia_2.8b` IS the real step-0 weights, not a
    from_config twin); the references' mutual alignments (the
    ceiling); the within-family reading (Pythia 2.8b's trajectory
    against Pythia-12b), re-derived from committed sets only."""
    twins = {}
    for traj in battery_4.TRAJECTORIES_4:
        key = battery_4.INIT_KEY_4[traj]
        unit = _load_one_unit_4(root, key)
        refs = battery_4.REFS_FOR_4[traj]
        ref_tables = {ref: rt["sets"] for ref, rt in
                     collect_4.load_ref_tables_4(root, refs).items()}
        pia = per_item_alignment_4(unit, ref_tables, unit["record"]["pairing"])
        twins[traj] = {r: float(pia[r].mean()) for r in bt.RUNGS}

    ceiling = {}
    for ref in battery_4.REFERENCES_4:
        align = json.loads((battery_4.reference_dir(root, ref) / "align.json").read_text())
        ceiling[ref] = {r: {o: float(np.mean(align[r][o]["knn_prompt_end"]))
                            for o in align[r]} for r in bt.RUNGS}

    # M-6: one `_load_one_unit_4` per STEP (it reads all 34 rungs'
    # sets in one call), not one per (rung, step) -- the original
    # rung-outer loop called it 34x per step, redundantly reloading
    # the same unit's bytes 34 times.
    within = {r: [] for r in bt.RUNGS}
    traj, ref = "pythia_2.8b", "ref_pythia_12b"
    ref_tables_pyt = collect_4.load_ref_tables_4(root, (ref,))[ref]
    ref_sets = ref_tables_pyt["sets"]
    ref_rec = json.loads((battery_4.reference_dir(root, ref) / "_load.json").read_text())
    steps = battery_4.GRID_4[traj]
    for s in steps:
        unit = _load_one_unit_4(root, (traj, s))
        sites, n_hidden = unit["record"]["sites"], unit["record"]["n_hidden"]
        pairing = collect_4._pairing_positions(sites, n_hidden, ref_rec["sites"],
                                               ref_rec["n_hidden"])
        for r in bt.RUNGS:
            ov = collect_4.overlap_table_4(unit["sets"][r], ref_sets[r], pairing)
            within[r].append(float((ov.astype(np.float64) / metric_4.K_4).mean()))
    return {"twins": twins, "twins_source": "re-derived",
           "ceiling": ceiling, "ceiling_source": "attested",
           "within_family": {"steps": list(steps), "a": within}, "within_family_source": "re-derived",
           "no_alpha_claim": True}


def s9_cka_4(root) -> dict:
    """Linear CKA at every site pair, ATTESTED from `align.json`; the
    primary re-read with CKA in place of k-NN on the endpoints and
    references only (activations exist there, and only there)."""
    out = {}
    for traj in battery_4.TRAJECTORIES_4:
        key = f"endpoint_{traj}"
        align = json.loads((battery_4.reference_dir(root, key) / "align.json").read_text())
        refs = battery_4.REFS_FOR_4[traj]
        per_rung = {}
        for r in bt.RUNGS:
            vals = {}
            for ref in refs:
                cka = align[r][ref].get("cka_prompt_end")
                vals[ref] = (None if cka is None
                            else [c for c in cka if c is not None] or None)
            per_rung[r] = vals
        out[traj] = per_rung
    return {"per_traj": out, "scope": "endpoints and references only",
           "source": "attested", "no_alpha_claim": True}


def k_sensitivity_4(root, k) -> dict:
    """Sensitivity: k = 5 / k = 20 in place of K_4 = 10. Computed on
    REFERENCE-STAGE keys only (the four endpoints and their
    references) where activations are kept (`keep_activations=True`)
    -- 'endpoints and references only', per the brief; degrades to
    unavailable per trajectory when a (gitignored) activations file is
    not present on disk (real analysis on a fresh checkout, or a world
    that never kept them). Each reference's k-NN sets are computed
    ONCE per rung and cached (`_ref_cache`) -- with 4 trajectories
    sharing 4 references 3-of-4 ways, a naive per-trajectory loop
    redoes the same reference ~3x."""
    _ref_cache: dict = {}

    def ref_sets(ref, rung):
        ck = (ref, rung)
        if ck not in _ref_cache:
            rp = battery_4.activations_path(root, ref, rung)
            if not rp.is_file():
                _ref_cache[ck] = None
            else:
                with np.load(rp) as zq:
                    Xq = np.asarray(zq["X"])[:, :, -1, :].astype(np.float32)
                _ref_cache[ck] = np.stack(
                    [metric_4.knn_sets(Xq[:, s, :], k=k) for s in range(Xq.shape[1])])
        return _ref_cache[ck]

    out = {}
    for traj in battery_4.TRAJECTORIES_4:
        key = f"endpoint_{traj}"
        d = battery_4.reference_dir(root, key)
        rec = json.loads((d / "_load.json").read_text())
        refs = rec.get("refs") or []
        pairing_by_ref = rec.get("pairing") or {}
        per_rung = {}
        for rung in bt.RUNGS:
            p = d / "activations" / f"{rung}.npz"
            if not p.is_file():
                per_rung = None
                break
            with np.load(p) as z:
                X = np.asarray(z["X"])[:, :, -1, :].astype(np.float32)   # prompt-end
            n_sites = X.shape[1]
            sets_m = np.stack([metric_4.knn_sets(X[:, s, :], k=k) for s in range(n_sites)])
            vals = []
            for ref in refs:
                sets_q = ref_sets(ref, rung)
                if sets_q is None:
                    continue
                ov = collect_4.overlap_table_4(sets_m, sets_q, pairing_by_ref[ref])
                vals.append(float((ov.astype(np.float64) / k).mean()))
            if vals:
                per_rung[rung] = float(np.mean(vals))
        out[traj] = per_rung if per_rung else None
    return {"per_traj_endpoint": out, "k": k, "scope": "endpoints and references only",
           "source": "re-derived", "no_alpha_claim": True}


def s10_item_grain_4(root, cells, series_by_traj, rung_sets_by_traj) -> dict:
    """The per-item pre-clear excess overlap against the committed
    per-item emission order, within rung x 2g's strata (11 strata
    rungs), `stats_2g.somers_d_within`."""
    battery = bt.load_battery()
    pred2g = pr.load_predictor(bg.predictor_path(bg.EXP2G), sha_pin=bh.PREDICTOR_2G_SHA)
    strata_table = sg.from_json(pred2g["strata"])
    outcome_cache: dict = {}   # M-6: one load_outcome_4 per trajectory, not per cell
    out = {}
    for c in cells:
        traj, rung, t_minus = c["traj"], c["rung"], c["t_minus"]
        if traj not in outcome_cache:
            outcome_cache[traj] = battery_4.load_outcome_4(traj, battery=battery)
        outcome = outcome_cache[traj]
        per_item = series_by_traj[traj]["per_item"][t_minus]
        flat_rungs = rung_sets_by_traj[traj]["flat"]
        # M-4 (ruling): the flat-pool expectation is the SCALAR mean
        # over ALL flat rungs and ALL their items of o_i(t_minus) --
        # not a position-wise (per-item) vector -- subtracted from
        # every one of rung r's per-item overlaps alike.
        flat_vals = (float(np.mean([per_item[fr] for fr in flat_rungs])) if flat_rungs
                    else 0.0)
        x = per_item[rung] - flat_vals
        y = np.array([sum(outcome["per_step"][s]["rungs"][rung]["bits"][i]
                          for s in outcome["steps"]) for i in range(bt.N_ITEMS)], dtype=float)
        if rung in strata_table:
            strata = strata_table[rung]["strata"]
        else:
            strata = ["0"] * bt.N_ITEMS
        res = sg2.somers_d_within(x, y, strata)
        out[f"{traj}/{rung}"] = {"d": res["d"], "n_pairs": res["n_pairs"], "n": res["n"]}
    return {"per_cell": out, "source": "re-derived", "no_alpha_claim": True}


def s11_textures_4(root, cells, series_by_traj, rung_sets_by_traj) -> dict:
    battery = bt.load_battery()
    floors = bg.load_floors()
    bar_count_cache: dict = {}

    def bar_count(rung, floor):
        # M-5 (ruling): the bar COUNT is the smallest k in 0..500 for
        # which `stats_2d.binomial_bar(k, 500, floor)["significant"]`
        # -- a linear search, memoised per rung. Task 5 finding 3: when
        # NO k in 0..500 clears the bar, this must report `None` (not
        # clamp to 500 -- 500 is itself never checked for significance
        # by the loop below once k > N_ITEMS, so clamping silently
        # manufactured a bar count that was never verified significant).
        if rung not in bar_count_cache:
            k = 0
            found = None
            while k <= bt.N_ITEMS:
                if st.binomial_bar(k, bt.N_ITEMS, floor)["significant"]:
                    found = k
                    break
                k += 1
            bar_count_cache[rung] = found
        return bar_count_cache[rung]

    outcome_cache: dict = {}   # M-6: one load_outcome_4 per trajectory, not per cell
    per_cell = {}
    for c in cells:
        traj, rung = c["traj"], c["rung"]
        steps = series_by_traj[traj]["steps"]
        rs = rung_sets_by_traj[traj]
        trend = trend_4(series_by_traj[traj]["a"], rs["flat"], steps)
        excess = excess_4(series_by_traj[traj]["a"], trend, steps)[rung]
        diffs = np.diff(excess)
        largest_i = int(np.argmax(diffs)) if len(diffs) else None
        largest_step = steps[largest_i + 1] if largest_i is not None else None
        non_monotone = int(np.sum(diffs < -1e-12))
        if traj not in outcome_cache:
            outcome_cache[traj] = battery_4.load_outcome_4(traj, battery=battery)
        outcome = outcome_cache[traj]
        rec = outcome["per_step"][c["t_minus"]]["rungs"][rung]
        rate = rec["correct"] / rec["n"]
        floor = floors[rung]
        bc = bar_count(rung, floor)
        per_cell[f"{traj}/{rung}"] = {
            "largest_step": largest_step, "coincides_with_t_clear": largest_step == c["t_clear"],
            "non_monotone_count": non_monotone, "excess_series": excess,
            "rate_at_t_minus": rate, "floor": floor,
            "correct_at_t_minus": rec["correct"], "bar_count": bc,
            "bar_count_available": bc is not None,
            "count_fraction_of_bar_at_t_minus": (rec["correct"] / bc) if bc else None,
        }
    transient_series, trend_shapes, steps_by_traj = {}, {}, {}
    for traj, rs in rung_sets_by_traj.items():
        series = series_by_traj.get(traj)
        if series is None:
            continue
        steps = series["steps"]
        trend = trend_4(series["a"], rs["flat"], steps)
        excess = excess_4(series["a"], trend, steps)
        transient_series[traj] = {r: excess[r] for r in rs["transient"]}
        trend_shapes[traj] = trend
        steps_by_traj[traj] = steps
    return {"per_cell": per_cell, "transient_series": transient_series,
           "trend_shapes": trend_shapes, "steps_by_traj": steps_by_traj,
           "note": "grid values are training steps, not token counts (a token-per-step "
                   "conversion was not built)", "source": "re-derived", "no_alpha_claim": True}


# ---------------------------------------------------------------- verdict

def _eligibility_summary_4(eligibility) -> dict:
    out = {}
    for traj, block in eligibility.items():
        r = block.get("R") or {}
        n_eligible = sum(1 for e in r.values() if e.get("eligible"))
        out[traj] = {"n_R": len(r), "n_eligible": n_eligible, "n_flat": len(block.get("flat") or {}),
                    "n_transient": len(block.get("transient") or [])}
    return out


def _compare_eligibility_4(a, b, path="") -> list:
    bad = []
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a or k not in b:
                bad.append(f"{path}.{k}: present in only one"); continue
            bad += _compare_eligibility_4(a[k], b[k], f"{path}.{k}")
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            bad.append(f"{path}: length {len(a)} != {len(b)}")
        else:
            for i, (x, y) in enumerate(zip(a, b)):
                bad += _compare_eligibility_4(x, y, f"{path}[{i}]")
    elif (isinstance(a, (int, float)) and not isinstance(a, bool)
         and isinstance(b, (int, float)) and not isinstance(b, bool)):
        if a is None or b is None:
            if a != b:
                bad.append(f"{path}: {a!r} != {b!r}")
        elif abs(float(a) - float(b)) > 1e-12:
            bad.append(f"{path}: {a!r} != {b!r}")
    else:
        if a != b:
            bad.append(f"{path}: {a!r} != {b!r}")
    return bad


def _check_power_matches_eligibility_4(power, eligibility, eligibility_sha) -> list:
    bad = []
    for field in ("cells", "rungs", "eligibility_sha256", "declaration", "n_sim", "arms"):
        if field not in power:
            bad.append(f"power record missing {field!r}")
    elig_pairs = set()
    for traj, block in eligibility.items():
        for rung, e in (block.get("R") or {}).items():
            if e.get("eligible"):
                elig_pairs.add((traj, rung))
    if "cells" in power:
        got = {(c[0], c[1]) if isinstance(c, (list, tuple)) else tuple(c) for c in power["cells"]}
        if got != elig_pairs:
            bad.append("power record cells != eligibility's eligible set")
    if "rungs" in power:
        want_rungs = {r for _, r in elig_pairs}
        if set(power["rungs"]) != want_rungs:
            bad.append("power record rungs != eligibility's eligible rung set")
    if "eligibility_sha256" in power and power["eligibility_sha256"] != eligibility_sha:
        bad.append("power record eligibility_sha256 != the eligibility file's sha")
    return bad


def _jsonify_4(obj):
    if isinstance(obj, dict):
        return {str(k): _jsonify_4(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_jsonify_4(v) for v in obj]
    if isinstance(obj, np.ndarray):
        return _jsonify_4(obj.tolist())
    if isinstance(obj, (np.floating,)):
        v = float(obj)
        return None if (v != v or v in (float("inf"), float("-inf"))) else v
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, np.bool_):
        return bool(obj)
    if isinstance(obj, float):
        return None if (obj != obj or obj in (float("inf"), float("-inf"))) else obj
    return obj


def _json_rung_sets_4(rung_sets_by_traj) -> dict:
    return {t: {"R": list(rs["R"]), "flat": list(rs["flat"]), "transient": list(rs["transient"]),
               "t_clear": dict(rs["t_clear"]), "endpoint_step": rs["endpoint_step"]}
           for t, rs in rung_sets_by_traj.items() if rs is not None}


def verdict_4(*, failures, tree, primary, cells, eligibility, rung_sets_by_traj, gate1_records,
             gate0_records=None, secondaries, sensitivities, pins_active, n_boot) -> dict:
    world = tree["verdict"]
    failures = list(failures)
    # I-1: a malformed eligibility file (e.g. a list, not a dict) must
    # not crash the whole packaging step and throw away a verdict the
    # tree already correctly decided (e.g. INSUFFICIENT_DATA from an
    # earlier comparison failure) — `tree`/`reason` above are already
    # fixed from the caller's own `failures` snapshot, so a late
    # failure here only ever reaches `referents.failures`.
    elig_summary = None
    if eligibility:
        elig_summary, f = collect_total_4(lambda: _eligibility_summary_4(eligibility),
                                          "4 eligibility summary")
        failures += f
    gate0_summary = None
    if gate0_records:
        gate0_summary = {t: ({"fraction_below": g["fraction_below"], "n_cells": g["n_cells"],
                             "per_reference": g.get("per_reference"), "pass": g["pass"]} if g else None)
                         for t, g in gate0_records.items()}
    return {
        "verdict": world,
        "reason": tree["reason"],
        "known_outcome_caveat": KNOWN_OUTCOME_CAVEAT_4,
        "licensed_sentence": LICENSED_4[world],
        "primary": primary,
        "cells": cells,
        "eligibility_summary": elig_summary,
        "rung_sets": _json_rung_sets_4(rung_sets_by_traj) if rung_sets_by_traj else None,
        "gate1": gate1_records,
        "gate0": gate0_summary,
        "secondaries": secondaries or None,
        "sensitivities": sensitivities or None,
        "referents": {"failures": list(failures)},
        "pins_active": pins_active,
        "n_boot": n_boot,
        "git_sha": _git_sha_4(),
        "stack_note": "analysis-only, no model contact",
    }


def write_verdict_txt_4(v: dict) -> str:
    lines = [f"EXPERIMENT 4 VERDICT: {v['verdict']}", "", v["reason"], "",
            f"Caveat: {v['known_outcome_caveat']}", "", f"Licence: {v['licensed_sentence']}", ""]
    p = v.get("primary")
    if p:
        lines.append(f"Primary: T={p['T']:.4f} p+={p['p_plus']:.4g} p-={p['p_minus']:.4g} "
                    f"CI95=[{p['ci95'][0]:.4f}, {p['ci95'][1]:.4f}] "
                    f"n_cells={p['n_cells']} n_rungs={p['n_rungs']} flip_method={p['flip_method']}")
        lines.append("")
        lines.append("Per-trajectory T:")
        for t, pt in (p.get("per_traj") or {}).items():
            lines.append(f"  {t}: T={pt['T']:.4f} p+={pt['p_plus']:.4g} n_cells={pt['n_cells']}")
        lines.append("")
        lines.append("Per-type T:")
        for typ, pt in (p.get("per_type") or {}).items():
            if pt is None:
                lines.append(f"  {typ}: (no cells)")
            else:
                lines.append(f"  {typ}: T={pt['T']:.4f} p+={pt['p_plus']:.4g} n_cells={pt['n_cells']}")
        lines.append("")
    lines.append("Per-cell phi:")
    for c in (v.get("cells") or []):
        lines.append(f"  {c['traj']}/{c['rung']}: phi={c['phi']:.4f} t_clear={c['t_clear']} "
                    f"x_end={c['x_end']:.4f}")
    lines.append("")
    sec = v.get("secondaries") or {}
    lines.append(f"Secondaries present: {sorted(sec)}")
    sens = v.get("sensitivities") or {}
    lines.append(f"Sensitivities present: {sorted(sens)}")
    lines.append("")
    lines.append(f"git_sha={v.get('git_sha')}")
    return "\n".join(lines) + "\n"


# -------------------------------------------------------------------- run

_LITERAL = object()


def run(root=battery_4.EXP4, *, write=False, n_boot=N_BOOT_4, tag_exists=None, blob_sha=None,
       blobs_bound=None, referents_sha=_LITERAL, imports_pinned=_LITERAL, out_path=None,
       frozen_check=None) -> dict:
    failures = []
    root = Path(root)
    if referents_sha is _LITERAL:
        referents_sha = REFERENTS_4_SHA256
    if imports_pinned is _LITERAL:
        imports_pinned = None if IMPORTED_SHA256_4 is None else True

    # ---- halt markers first (every trajectory + the reference stage)
    halt_paths = [collect_4.reference_halt_marker_path(root)] + \
                [battery_4.halt_marker_path(root, traj) for traj in battery_4.TRAJECTORIES_4]
    for p in halt_paths:
        if p.exists():
            halted, f = collect_total_4(lambda p=p: p.read_text().strip()[:200], "4 halt marker read")
            failures += f
            if not f:
                failures.append(f"4: the runner halted ({p}): {halted}")

    _, f = collect_total_4(frozen_check or battery_4.check_frozen_4, "4 frozen modules"); failures += f

    if imports_pinned:
        _, f = collect_total_4(check_imports_4, "4 import surface (entry)"); failures += f
    elif imports_pinned is not False:
        failures.append("4 import surface: not pinned (build incomplete)")

    prereg, f = collect_total_4(
        lambda: battery_4.require_prereg_4(tag_exists=tag_exists, blob_sha=blob_sha),
        "4 prereg tag"); failures += f

    _, f = collect_total_4(battery_4.manifests_4, "4 checkpoint manifests"); failures += f

    # I-8: referents_sha is False in tests that deliberately skip this
    # (no referent tool yet); a string means the manifest must
    # actually be re-checked, not merely assumed pinned.
    referent_manifest_ok = False
    if referents_sha is None:
        failures.append("4 referent manifest: not pinned (build incomplete)")
    elif referents_sha is not False:
        # Task 5 finding 2: `check_referents` returns a LIST of per-
        # file drift failures (raising only on the sha-pin mismatch
        # itself) — the returned list must be CONSUMED, not discarded,
        # else a non-empty drift list from an otherwise-non-raising
        # check would silently mark `pins_active["referent_manifest"]`
        # True.
        from experiments.exp4 import make_referents_4 as mkr
        mf, f = collect_total_4(
            lambda: mkr.check_referents(REFERENTS_PATH_4, sha_pin=referents_sha),
            "4 referent manifest")
        failures += f + (mf or [])
        referent_manifest_ok = not f and not mf

    battery, f = collect_total_4(bt.load_battery, "4 battery items"); failures += f
    floors, f = collect_total_4(bg.load_floors, "4 floors 2d"); failures += f

    outcomes, rung_sets = {}, {}
    if battery is not None and floors is not None:
        for traj in battery_4.TRAJECTORIES_4:
            oc, f = collect_total_4(lambda traj=traj: battery_4.load_outcome_4(traj, battery=battery),
                                    f"4 outcome {traj}"); failures += f
            outcomes[traj] = oc
            rs = None
            if oc is not None:
                rs, f = collect_total_4(lambda oc=oc: battery_4.rung_sets_4(oc, floors),
                                        f"4 rung sets {traj}"); failures += f
                if rs is not None:
                    bad = battery_4.check_rung_set_pins_4(traj, rs)
                    if bad:
                        failures += [f"4 {b}" for b in bad]
            rung_sets[traj] = rs
    else:
        for traj in battery_4.TRAJECTORIES_4:
            outcomes[traj] = None; rung_sets[traj] = None
        failures.append("4 outcomes: battery or floors missing")

    seal, f = collect_total_4(
        lambda: an2i.require_seal_2i(battery_4.REFERENCE_SEAL_TAG_4,
                                     [root / p for p in battery_4.reference_seal_paths_4(root)],
                                     tag_exists=tag_exists, blobs_bound=blobs_bound,
                                     repo_root=battery_4.REPO),
        "4 reference seal")
    failures += f
    if seal is not None and seal.get("failures"):
        failures += [f"4 reference seal: {m}" for m in seal["failures"]]

    stage_keys = list(battery_4.STAGE1_KEYS_4) + list(battery_4.STAGE1_FIRST_UNITS_4)
    stage_tables_4, f = collect_total_4(lambda: load_stage_tables_4(root, keys=stage_keys),
                                        "4 stage tables")
    failures += f

    # C-1 (design §3.7): gate 0, right after the stage tables load and
    # before gate 1 — for every trajectory, unconditionally (not
    # gated behind `if not failures`, so a gate-0 failure is always
    # collected, matching eligibility/power's own unconditional checks
    # just below).
    gate0_records = {}
    for traj in battery_4.TRAJECTORIES_4:
        if stage_tables_4 is None:
            gate0_records[traj] = None
            continue
        refs = battery_4.REFS_FOR_4[traj]
        ref_tables_raw_g0, f = collect_total_4(
            lambda refs=refs: collect_4.load_ref_tables_4(root, refs), f"4 gate 0 {traj} ref tables")
        failures += f
        if ref_tables_raw_g0 is None:
            gate0_records[traj] = None
            continue
        ref_tables_g0 = {ref: rt["sets"] for ref, rt in ref_tables_raw_g0.items()}
        g0, f = collect_total_4(
            lambda traj=traj, ref_tables_g0=ref_tables_g0:
                gate0_4(root, traj, ref_tables_g0, stage_tables_4),
            f"4 gate 0 {traj}")
        failures += f
        gate0_records[traj] = g0
        if g0 is not None and not g0["pass"]:
            failures.append(f"4 gate 0 {traj}: the instrument does not see training (twin "
                            f"below endpoint on {g0['fraction_below']:.3f} of cells, need "
                            f"≥ {GATE0_MIN_FRACTION_4:.2f})")

    elig_path = battery_4.eligibility_path(root)
    eligibility, elig_sha = None, None
    if not elig_path.is_file():
        failures.append(f"4 eligibility record missing ({elig_path})")
    else:
        elig_sha = bg.sha256_file(elig_path)
        eligibility, f = collect_total_4(lambda: json.loads(elig_path.read_text()),
                                        "4 eligibility record"); failures += f
        if eligibility is not None:
            recomputed, f = collect_total_4(lambda: eligibility_table_4(root),
                                            "4 eligibility re-derivation"); failures += f
            if recomputed is not None:
                bad = _compare_eligibility_4(eligibility, recomputed)
                if bad:
                    failures.append(f"4 eligibility record disagrees with re-derivation: {bad[:3]}")

    power_path = battery_4.power_path(root)
    power = None
    if not power_path.is_file():
        failures.append(f"4 power record missing ({power_path})")
    else:
        power, f = collect_total_4(lambda: json.loads(power_path.read_text()),
                                  "4 power record"); failures += f
        if power is not None and eligibility is not None:
            bad, f = collect_total_4(
                lambda: _check_power_matches_eligibility_4(power, eligibility, elig_sha),
                "4 power vs eligibility check")
            failures += f
            if bad:
                failures += [f"4 power record: {b}" for b in bad]

    series_by_traj, gate1_records = {}, {}
    if not failures:
        for traj in battery_4.TRAJECTORIES_4:
            g1_path = battery_4.gate1_path(root, traj)
            g1_att = None
            if not g1_path.is_file():
                failures.append(f"4 gate 1 {traj}: record missing ({g1_path})")
            else:
                g1_att, f = collect_total_4(lambda p=g1_path: json.loads(p.read_text()),
                                           f"4 gate 1 {traj} record"); failures += f
                if g1_att is not None:
                    bad, f = collect_total_4(
                        lambda g1_att=g1_att, traj=traj: battery_4.gate1_failures_4(g1_att, traj=traj),
                        f"4 gate 1 {traj} failures check")
                    failures += f
                    if bad:
                        failures += [f"4 {b}" for b in bad]
            gate1_records[traj] = g1_att

            g1_der, f = collect_total_4(lambda traj=traj: battery_4.gate1_rederive_4(root, traj),
                                       f"4 gate 1 {traj} re-derivation"); failures += f
            if g1_der is not None:
                # I-6: require ALL FOUR re-derived agreements, not
                # just sets_equal/digest_equal -- activation_sha_equal
                # was already computed by gate1_rederive_4 and
                # silently discarded; attested_sha_equal (design §3.7:
                # identity on every (rung, site, position)) is new.
                if (not all(g1_der["sets_equal"].values())
                    or not all(g1_der["activation_sha_equal"].values())
                    or not all(g1_der["attested_sha_equal"].values())
                    or not g1_der["digest_equal"]):
                    failures.append(f"4 gate 1 {traj}: re-derived bytes disagree")

            sweep_tables, f = collect_total_4(lambda traj=traj: load_sweep_tables_4(root, traj),
                                             f"4 sweep tables {traj}"); failures += f
            if sweep_tables is None or rung_sets.get(traj) is None:
                continue
            refs = battery_4.REFS_FOR_4[traj]
            ref_tables_raw, f = collect_total_4(lambda refs=refs: collect_4.load_ref_tables_4(root, refs),
                                               f"4 ref tables {traj}"); failures += f
            if ref_tables_raw is None:
                continue
            ref_tables = {ref: rt["sets"] for ref, rt in ref_tables_raw.items()}
            series, f = collect_total_4(
                lambda traj=traj, ref_tables=ref_tables, sweep_tables=sweep_tables:
                    alignment_series_4(root, traj, ref_tables, sweep_tables),
                f"4 alignment series {traj}")
            failures += f
            if series is not None:
                series_by_traj[traj] = series

    cells = []
    if not failures and series_by_traj and eligibility is not None:
        rs_available = {t: rung_sets[t] for t in series_by_traj if rung_sets.get(t) is not None}
        got_cells, f = collect_total_4(lambda: cells_4(series_by_traj, rs_available, eligibility),
                                      "4 cells")
        failures += f
        cells = got_cells or []

    primary = None
    if not failures and cells:
        primary, f = collect_total_4(lambda: primary_4(cells, n_boot=n_boot, seed=0), "4 primary")
        failures += f

    n_eligible_cells = len(cells)
    n_eligible_rungs = len({c["rung"] for c in cells}) if cells else 0
    tree = verdict_tree_4(failures, n_eligible_cells, n_eligible_rungs, primary or {})

    secondaries, sensitivities = {}, {}
    if not failures:
        def _sec(name, thunk, store):
            # M-3: the collect_total_4 label starts "4 " like every
            # other refusal label in run(); the dict key (`name`, what
            # callers/tests look up under `secondaries`/
            # `sensitivities`) is untouched.
            val, f = collect_total_4(thunk, f"4 {name}")
            store[name] = {"failed": f[0]} if f else val

        _sec("S1", lambda: s1_order_4(series_by_traj, rung_sets), secondaries)
        _sec("S2 from-below (1b)", lambda: s2_from_below_4(root), secondaries)
        _sec("S2 per-trajectory", lambda: s2_per_trajectory_4(series_by_traj, rung_sets), secondaries)
        _sec("S2 known-answer gates", s2_known_answer_gates_4, secondaries)
        s3 = None

        def _s3():
            nonlocal s3
            s3 = s3_scale_4(root)
            return s3
        _sec("S3", _s3, secondaries)
        _sec("S4", lambda: s4_size_axis_4(s3) if s3 is not None
             else (_ for _ in ()).throw(ValueError("S3 not available")), secondaries)
        for traj in battery_4.TRAJECTORIES_4:
            elig_R = ((eligibility or {}).get(traj) or {}).get("R") or {}
            rs = rung_sets.get(traj)
            if rs is None or traj not in series_by_traj:
                continue
            _sec(f"S5 {traj}", lambda traj=traj, rs=rs, elig_R=elig_R:
                s5_site_sensitivities_4(root, traj, rs, elig_R), sensitivities)
            _sec(f"S6 {traj}", lambda traj=traj, rs=rs, elig_R=elig_R:
                s6_question_end_4(root, traj, rs, elig_R), sensitivities)
            _sec(f"S7 {traj}", lambda traj=traj, rs=rs, elig_R=elig_R:
                s7_huh_construction_4(root, traj, rs, elig_R), sensitivities)
        _sec("S8", lambda: s8_referents_4(root, series_by_traj), secondaries)
        _sec("S9", lambda: s9_cka_4(root), sensitivities)
        _sec("S10", lambda: s10_item_grain_4(root, cells, series_by_traj, rung_sets), secondaries)
        _sec("S11", lambda: s11_textures_4(root, cells, series_by_traj, rung_sets), secondaries)
        _sec("S1 quarter/three-quarter", lambda: {
            "q1": s1_order_4(series_by_traj, rung_sets, frac=0.25),
            "q3": s1_order_4(series_by_traj, rung_sets, frac=0.75),
        }, sensitivities)

        def _clears_and_stays_primary():
            rs_cas = {}
            for traj, rs in rung_sets.items():
                if rs is None:
                    continue
                rs2 = dict(rs)
                cas = rs["clears_and_stays"]
                rs2 = {**rs, "t_clear": {r: (cas[r] if cas.get(r) is not None else rs["t_clear"].get(r))
                                        for r in rs["t_clear"]}}
                rs_cas[traj] = rs2
            if not eligibility:
                raise ValueError("eligibility not available")
            elig_cas = {}
            for traj, block in eligibility.items():
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
            cells_cas = cells_4({t: series_by_traj[t] for t in series_by_traj if t in rs_cas},
                                rs_cas, elig_cas)
            if not cells_cas:
                return None
            return primary_4(cells_cas, n_boot=n_boot, seed=0)
        _sec("primary_clears_and_stays", _clears_and_stays_primary, sensitivities)
        _sec("k=5", lambda: k_sensitivity_4(root, 5), sensitivities)
        _sec("k=20", lambda: k_sensitivity_4(root, 20), sensitivities)

    # 2j F-1, Task 5: the import surface is itself a verdict input — a
    # read sweep sees what an analyzer opens, not what the interpreter
    # executes on its behalf (2j's own lesson). Checked at ENTRY
    # (above) and again at EXIT, after every secondary/sensitivity has
    # had the chance to import something the entry check never saw.
    if not failures:
        _, f = collect_total_4(check_imports_4 if imports_pinned else (lambda: None),
                               "4 import surface (exit)")
        failures += f

    pins_active = {
        "frozen_modules": frozen_check is None,
        "import_surface": bool(imports_pinned),
        "referent_manifest": referent_manifest_ok,
        "prereg_binding": tag_exists is None and blob_sha is None,
        "seal_binding": blobs_bound is None,
    }

    v = verdict_4(failures=failures, tree=tree, primary=primary, cells=cells,
                 eligibility=eligibility or {}, rung_sets_by_traj=rung_sets,
                 gate1_records=gate1_records, gate0_records=gate0_records,
                 secondaries=secondaries, sensitivities=sensitivities,
                 pins_active=pins_active, n_boot=n_boot)
    # Sanitised (no numpy scalars/arrays, no NaN/Inf) unconditionally,
    # not only when writing: `run()`'s return value must itself be
    # strict-JSON-able (brief Step 3), and a numpy type left in
    # `cells`/`secondaries`/`sensitivities` should fail loudly via
    # `allow_nan=False`/plain `json.dumps` on the CALLER's own check,
    # not silently pass because only the on-disk copy was cleaned.
    v = _jsonify_4(v)

    if write:
        out_v = out_path or battery_4.verdict_path(root)
        out_txt = battery_4.verdict_txt_path(root)
        out_v.parent.mkdir(parents=True, exist_ok=True)
        out_v.write_text(json.dumps(v, indent=1, allow_nan=False))
        out_txt.write_text(write_verdict_txt_4(v))

    return v


if __name__ == "__main__":
    result = run(write=True)
    print(f"verdict: {result['verdict']}")
    print(result["reason"])
