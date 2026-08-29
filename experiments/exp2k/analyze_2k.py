# experiments/exp2k/analyze_2k.py
"""Experiment 2k — the density question (design `experiment-2k-design.md`).
Every 2i-tree loader is 2i's (the block 2j's run() executes); the
statistic is 2i's `_run_test`; the block reading is 2j's; the outcome
is 2i's committed 7B sweep. 2k adds: the k=256 tier loader with the
gate-1 re-derivation, the seal cross-check, the comparison gates
(x_A^(64) from the sealed 2k rows == 2d's files == 2i's verdict), the
primary at 256, S1–S7, the tree DENSITY / NOT-DENSITY, and run()."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

EXP2K = Path(__file__).resolve().parent
if str(EXP2K.parent.parent) not in sys.path:
    sys.path.insert(0, str(EXP2K.parent.parent))

from experiments.exp2d import analyze_2d as a2d  # noqa: E402
from experiments.exp2d import battery_2d as bt  # noqa: E402
from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp2g import predictor_2g as pr  # noqa: E402
from experiments.exp2g import stats_2g as st  # noqa: E402
from experiments.exp2g import strata_2g as sg  # noqa: E402
from experiments.exp2h import battery_2h as bh  # noqa: E402
from experiments.exp2i import analyze_2i as an2i  # noqa: E402
from experiments.exp2i import battery_2i as bi  # noqa: E402
from experiments.exp2j import analyze_2j as an2j  # noqa: E402
from experiments.exp2j import functionals_2j as fn  # noqa: E402
from experiments.exp2k import battery_2k as bk  # noqa: E402

RESULTS = EXP2K / "results"
REFERENTS_PATH_2K = EXP2K / "referents_2k.json"
REFERENTS_2K_SHA256 = None        # Task 5: pinned literally
IMPORTED_SHA256_2K = None         # Task 5: pinned literally from tests/import_scan_2k.py
WORLDS_2K = ("INSUFFICIENT_DATA", "DENSITY", "NOT-DENSITY")
ANNOTATIONS_2K = ("structured", "null")
ALPHA, T_BAR, N_PERM, N_BOOT = st.ALPHA, st.T_BAR, st.N_PERM, st.N_BOOT
collect_total = an2i.collect_total
_run_test = an2i._run_test

VERDICT_2I_PIN_A = 0.09491251078607414                # 2i Test A, x_A^(64) 1b → OLMo-7B
# Step 3: 2i's verdict.json carries this at
# `secondaries["replication_410m_cross"]["stratified"]["T"]` (2i's
# VERDICT.txt names it "410m cross .1154" — a projection miss, above
# 1b's own T). `pin_a410_from_record_2i` reads that path as PRIMARY,
# falling back to `secondaries["cross_410m"]["stratified"]["T"]` only
# if the primary path is absent (disclosed in the function's docstring
# and PROGRESS.md; the fallback is inert on every committed record).
VERDICT_2I_PIN_A410 = 0.11537934925951784              # 2i secondaries.replication_410m_cross
VERDICT_2G_PIN_28 = 0.16722141085849532                # x_A^(64) 1b → 2.8b over R_28 (2g)

# design §2, first bullet, verbatim
KNOWN_INPUTS_CAVEAT_2K = (
    "The outcome. 2i's 7B stage-1 sweep — per-item bits at 21 grid points on all 34 "
    "rungs, y_i the count of points at which item i verifies — is committed under "
    "`exp2i-closed`. This is 2d's and 2e's situation, not 2g's or 2i's: 2k tests a "
    "zero-free-parameter predictor fixed before sampling against an outcome that is "
    "already on disk. It is not a sealed forecast. A DENSITY verdict licenses \"the "
    "cross-family predictor clears its preregistered bar at 256 draws on 2i's outcome\"; "
    "it does not license \"Prediction 2 supported across families\", which stays "
    "reserved for a sealed-outcome experiment (approach C).")

_L = {
    "INSUFFICIENT_DATA": "No world reached: a referent, loader, gate or pin refused; nothing "
                         "is licensed",
    "DENSITY": "At four times the draw budget Pythia-1b's counts clear the same bar on the "
               "same outcome — an outcome that was already on disk, so a bar cleared, not a "
               "forecast made; the essay's cross-family clause gains its qualification, the "
               "scoreboard's 'stopped short at .095' gains 'and clears it at 256 draws', "
               "Prediction 2 reads 'a lineage instrument at 64 draws; at 256, cross-family on "
               "a known outcome'; the sealed cross-family test is approach C with a 256-draw "
               "predictor; nothing about mechanism is licensed (S3 is descriptive)",
    "NOT-DENSITY": "The cross-family shortfall is not predictor density at four times the "
                   "budget: the lineage wording stands unchanged and the essay gains that one "
                   "sentence; under 'null' the sub-bar structure 2i reported did not replicate "
                   "at 256 and that is said; approach C needs a different reason to expect a "
                   "cross-family forecast",
    "NOT-DENSITY_UNDERPOWERED": "not detected at this resolution: the primary did not fire "
                                "under DECLARED UNDERPOWERED IN ADVANCE, so the shortfall is "
                                "neither confirmed as density nor ruled out; the lineage "
                                "wording stands; nothing else is licensed",
    "NOT-DENSITY_THIN": "Fewer than three rungs carried the primary: the density question is "
                        "untested at this resolution, not answered; the lineage wording stands",
    "NOT-DENSITY_UNDEFINED": "The primary was undefined (predictor constant inside every "
                             "stratum on every rung): untested, not absent",
}
LICENSED_2K = {k: f"{v}. Disclosure (design §2): {KNOWN_INPUTS_CAVEAT_2K}" for k, v in _L.items()}
DISCLOSURE_THIN_2K = ("fewer than three rungs were eligible for the primary — the reading is "
                      "THIN regardless of the power record's declaration")
DISCLOSURE_UNDEFINED_2K = ("the primary was undefined (x_A^(256) constant inside every stratum "
                           "on every eligible rung) — untested, not absent")


# ------------------------------------------------------------ pins

_EXPERIMENTS_ROOT_2K = str((bg.REPO / "experiments").resolve())


def check_imports_2k() -> None:
    """The eleventh lesson, from commit one: every module under
    `experiments/` this process has imported must be covered — by
    FROZEN_FILES_2K (the documented path list), battery_2g's
    FROZEN_IMPORT_SHA256_2G, the three tag-bound INSTRUMENT_BLOBS_2K,
    2j's own closed residual import-surface pin (`IMPORTED_SHA256_2J`,
    verified against disk here — not merely trusted, since 2k's run()
    never calls 2j's own `check_imports_2j`), or IMPORTED_SHA256_2K
    (every entry of both dicts verified against disk unconditionally).
    `None` = not pinned (build incomplete) is a refusal. Files under a
    `tests/` directory are excluded (disclosed, 2j's rule) — 2k's own
    `run/rehearse_2k.py` and `run/__init__.py`, pulled into
    `sys.modules` only when `test_tier_2k.py` is collected alongside
    this module, are a REAL gap this scan is meant to surface: neither
    is frozen, an instrument blob, or yet in `IMPORTED_SHA256_2K` —
    Task 5's scan is what closes it, not this function.

    fix round 1 / Finding 1: coverage via FROZEN_FILES_2K (paths) is
    trusted for import-surface purposes, but the actual byte-level
    hash-checking of those paths happens in a DIFFERENT function
    (`check_frozen_2k`, which iterates `FROZEN_SHA256_2K.items()` —
    the pinned dict, not the documented tuple). Nothing before this
    fix asserted the two agree, so once Task 5 pins `FROZEN_SHA256_2K`,
    a path present in `FROZEN_FILES_2K` but missing from that dict
    would be reported "covered" here and hash-verified by NO gate
    anywhere in 2k's pipeline. The equality check below makes that
    silent gap impossible: once `FROZEN_SHA256_2K` is non-empty, its
    keys must exactly equal `FROZEN_FILES_2K`'s paths, or this refuses
    before `covered` is even built. Before that pin lands (the current,
    empty-dict state), the check is inert by construction (`if
    FROZEN_SHA256_2K`) — path coverage via FROZEN_FILES_2K stays
    correct-but-momentarily-unverified, same as every other
    build-incomplete gap in this module, and becomes a live guarantee
    the moment the literal is pinned."""
    if IMPORTED_SHA256_2K is None:
        raise RuntimeError("IMPORTED_SHA256_2K is None — the import surface is not pinned "
                           "(build incomplete)")
    if bk.FROZEN_SHA256_2K:
        pinned_frozen = {str(Path(p).resolve()) for p in bk.FROZEN_SHA256_2K}
        documented_frozen = {str(Path(p).resolve()) for p in bk.FROZEN_FILES_2K}
        if pinned_frozen != documented_frozen:
            missing = sorted(documented_frozen - pinned_frozen)
            extra = sorted(pinned_frozen - documented_frozen)
            raise RuntimeError(f"FROZEN_SHA256_2K does not cover FROZEN_FILES_2K: missing "
                               f"{missing}; extra {extra}")
    covered = {str(Path(p).resolve()) for p in bk.FROZEN_FILES_2K}
    covered |= {str(Path(p).resolve()) for p in bg.FROZEN_IMPORT_SHA256_2G}
    covered |= {str((bg.REPO / rel).resolve()) for rel in bk.INSTRUMENT_BLOBS_2K}
    pinned = {str(Path(p).resolve()): v for p, v in IMPORTED_SHA256_2K.items()}
    # 2j's own residual import-surface pins (`IMPORTED_SHA256_2J`) cover
    # the package `__init__.py` chain and the 2c/2f/exp3 modules 2k
    # inherits unchanged through the same import graph, closed and
    # immutable since 2j tagged. Folded into the SAME verified-against-
    # disk dict as `IMPORTED_SHA256_2K`'s own entries (not merely
    # `covered`) so a hand-edit to one of 2j's residual files is still
    # caught as drift here, not silently trusted — 2k's run() never
    # calls 2j's own `check_imports_2j` (it would also flag 2k's own
    # files, which 2j's covered-set knows nothing about), so this is
    # the only place that verification happens for 2k. 2k's own Task-5
    # scan need only add what is genuinely NEW to 2k on top of this.
    pinned_upstream = {str(Path(p).resolve()): v for p, v in an2j.IMPORTED_SHA256_2J.items()}
    unpinned, drifted = [], []
    for p, want in sorted({**pinned_upstream, **pinned}.items()):
        pp = Path(p)
        if not pp.is_file() or bg.sha256_file(pp) != want:
            drifted.append(f"(pin) -> {p}")
    for name, mod in sorted(sys.modules.items()):
        f = getattr(mod, "__file__", None)
        if not f:
            continue
        rp = Path(f).resolve()
        s = str(rp)
        if not s.startswith(_EXPERIMENTS_ROOT_2K + "/") or "tests" in rp.parts:
            continue
        if s in covered or s in pinned or s in pinned_upstream:
            continue
        unpinned.append(f"{name} -> {s}")
    if unpinned:
        raise RuntimeError("unpinned module on the import surface: " + "; ".join(sorted(unpinned)))
    if drifted:
        raise RuntimeError("imported module drifted from its pin: " + "; ".join(sorted(drifted)))


def pin_a_from_record_2i(v: dict) -> dict:
    a = v["tests"]["A"]
    return {"A": a["stratified"]["T"], "per_rung": {r: x["d"] for r, x in a["per_rung"].items()}}


def pin_a410_from_record_2i(v: dict) -> float:
    """Step 3: 2i's verdict.json carries the 410m cross replication at
    exactly `secondaries["replication_410m_cross"]["stratified"]["T"]`
    (located by printing `list(v["secondaries"])` and matching the
    entry whose T ≈ .1154, 2i's VERDICT.txt names it). No fallback: a
    record without this exact key raises `KeyError` into the caller's
    `collect_total` rather than silently reading a different path —
    fix round 1 / Ruling 3. Task 4's world builder writes this real key."""
    return v["secondaries"]["replication_410m_cross"]["stratified"]["T"]


def ladder_b_from_record_2j(v: dict) -> dict:
    lad = v["a1"]["outcomes"]["olmo7b"]["ladder"]
    return {int(k): float(row["B"]["T"]) for k, row in lad.items()}


# ---------------------------------------------------------- 2i tree

def load_2i_tree(root_2i, *, tag_exists=None, blobs_bound=None) -> tuple:
    """2j's run() prefix, verbatim in substance, with 2k-prefixed labels:
    the frozen pins of 2g/2i/2j, battery, floors, verify, strata, 2i's
    manifest, both 2i seals, predictor provenance, rung set (and its
    re-derivation), endpoint, gate 1 re-derived, the sweep, x_B, and
    the Pythia outcomes for S5. Returns (failures, ctx)."""
    failures, ctx = [], {}
    root_2i = Path(root_2i)
    for thunk, label in ((bg.check_frozen_imports_2g, "2k upstream 2g frozen imports"),
                         (bi.check_frozen_2i, "2k upstream 2i frozen imports"),
                         (an2j.check_frozen_2j, "2k upstream 2j frozen imports"),
                         (bi.check_pythia_predictor_files, "2k x_A committed 2d files pinned")):
        _, f = collect_total(thunk, label); failures += f
    battery, f = collect_total(bg.load_battery, "2k battery items");           failures += f
    floors, f = collect_total(bg.load_floors, "2k floors 2d");                  failures += f
    verify_fn, f = collect_total(a2d.load_verify, "2k verify criterion 3c");    failures += f
    pred2g, f = collect_total(
        lambda: pr.load_predictor(bg.predictor_path(bg.EXP2G), sha_pin=bh.PREDICTOR_2G_SHA),
        "2k strata source 2g predictor");                                        failures += f
    strata = sg.from_json(pred2g["strata"]) if pred2g else None
    if strata is not None:
        _, f = collect_total(lambda: sg.check_strata_pins(strata), "2k strata pins 2g"); failures += f
    manifest, f = collect_total(
        lambda: bi.load_manifest(bi.CHECKPOINTS_PATH, sha_pin=bi.CHECKPOINTS_2I_SHA256),
        "2k/2i checkpoint manifest");                                            failures += f
    predictor_rec, f = collect_total(lambda: an2i._load_predictor_seal_content(root_2i),
                                     "2k/2i predictor seal content");            failures += f
    psl = an2i.require_seal_2i(bi.PREDICTOR_SEAL_TAG,
                               an2i._predictor_seal_paths(root_2i, predictor_rec),
                               tag_exists=tag_exists, blobs_bound=blobs_bound)
    failures += [f"2k/2i predictor seal binding: {m}" for m in psl["failures"]]
    rung_set, f = collect_total(lambda: an2i._load_rung_set(root_2i), "2k/2i rung set file"); failures += f
    esl = an2i.require_seal_2i(bi.ENDPOINT_SEAL_TAG, an2i._endpoint_seal_paths(root_2i),
                               tag_exists=tag_exists, blobs_bound=blobs_bound)
    failures += [f"2k/2i endpoint seal binding: {m}" for m in esl["failures"]]
    entry_stage1 = entry_1b = None
    if manifest is not None:
        entry_stage1, f = collect_total(lambda: bi.entry_7b(manifest, bi.ENDPOINT_STEP_7B),
                                        "2k/2i 7B endpoint entry");             failures += f
        entry_1b, f = collect_total(lambda: bi.entry_1b_endpoint(manifest),
                                    "2k/2i 1B endpoint entry");                 failures += f
    _prec = battery is not None and entry_1b is not None
    predictor_records, f = collect_total(
        lambda: an2i.load_predictor_records_2i(root_2i, battery, entry_1b=entry_1b) if _prec
        else (_ for _ in ()).throw(ValueError("battery or 1B entry missing")),
        "2k/2i predictor olmo1b records");                                       failures += f
    if predictor_rec is not None and predictor_records is not None:
        sbad, f = collect_total(lambda: an2i._check_predictor_seal_sampling(predictor_rec, predictor_records),
                                "2k/2i predictor seal sampling block");          failures += f + (sbad or [])
    _st1 = (battery is not None and verify_fn is not None and predictor_rec is not None
            and entry_stage1 is not None)
    stage1_final, f = collect_total(
        lambda: an2i.load_endpoint_which(root_2i, "stage1_final", battery, verify_fn,
                                         entry=entry_stage1, predictor_sha=predictor_rec["sha256"])
        if _st1 else (_ for _ in ()).throw(ValueError("battery, verify, seal or entry missing")),
        "2k/2i endpoint stage1_final");                                          failures += f
    if rung_set is not None and stage1_final is not None:
        rb, f = collect_total(lambda: an2i._check_rung_set_vs_endpoint(rung_set, stage1_final),
                              "2k/2i rung set vs endpoint");                     failures += f + (rb or [])
        if floors is not None:
            rb2, f = collect_total(lambda: an2i._check_rung_set_derivation(rung_set, stage1_final, floors),
                                   "2k/2i rung set re-derivation");              failures += f + (rb2 or [])
    if rung_set is not None and tuple(sorted(rung_set["R_CAP"])) != bk.R_CAP_DESIGN:
        failures.append(f"2k/2i rung set: R_CAP {sorted(rung_set['R_CAP'])} != design §3.4's "
                        f"{list(bk.R_CAP_DESIGN)}")
    if bi.halt_marker_path(root_2i).exists():
        failures.append("2k/2i sweep: HALTED marker present")
    g1p = bi.gate1_path(root_2i)
    gate1 = None
    if not g1p.is_file():
        failures.append(f"2k/2i gate 1: record missing ({g1p})")
    else:
        gate1, f = collect_total(lambda: json.loads(g1p.read_text()), "2k/2i gate 1 record"); failures += f
    _sw = manifest is not None and battery is not None and verify_fn is not None and predictor_rec is not None
    sweep, f = collect_total(
        lambda: an2i.load_sweep_7b(root_2i, battery, verify_fn, manifest=manifest,
                                   predictor_sha=predictor_rec["sha256"]) if _sw
        else (_ for _ in ()).throw(ValueError("manifest, battery, verify or seal missing")),
        "2k/2i sweep olmo7b");                                                   failures += f
    _g = sweep is not None and stage1_final is not None and gate1 is not None
    gb, f = collect_total(
        lambda: an2i.gate1_rederive_7b(sweep[bi.ENDPOINT_STEP_7B], stage1_final, gate1) if _g
        else (_ for _ in ()).throw(ValueError("sweep, endpoint or gate 1 record missing")),
        "2k/2i gate 1 byte identity re-derived");                                failures += f + (gb or [])
    r_cap = tuple(sorted(rung_set["R_CAP"])) if rung_set else ()
    _pr = rung_set is not None and battery is not None and verify_fn is not None
    x_b, f = collect_total(lambda: bi.sampler_counts_olmo(r_cap, root=root_2i, battery=battery,
                                                          verify_fn=verify_fn) if _pr
                           else (_ for _ in ()).throw(ValueError("rung set/battery/verify missing")),
                           "2k x_B counts olmo1b");                              failures += f
    if predictor_rec is not None and predictor_records is not None and x_b is not None:
        cb, f = collect_total(lambda: an2i._check_predictor_counts_2i(predictor_rec, predictor_records, x_b),
                              "2k x_B counts vs the sealed attestation");        failures += f + (cb or [])

    def _bits_b():
        out = {}
        for r in r_cap:
            rows = fn.draw_rows_2i(root_2i, r)
            out[r] = fn.verified_bits(rows, battery[r], verify_fn)
            if fn.counts_from_bits(out[r]) != x_b[r]:
                raise ValueError(f"x_B bits do not reproduce the count on {r}")
        return out
    bits_b, f = collect_total(lambda: _bits_b() if _pr and x_b else
                              (_ for _ in ()).throw(ValueError("x_B missing")), "2k bits x_B"); failures += f
    py, f = collect_total(lambda: an2j.load_pythia_outcomes(battery, verify_fn) if battery and verify_fn
                          else (_ for _ in ()).throw(ValueError("battery/verify missing")),
                          "2k pythia outcomes 2g 2h");                            failures += f
    out = None
    if not failures:
        out, f = collect_total(lambda: an2i.outcomes_7b(sweep, rungs=tuple(bt.RUNGS)),
                               "2k outcome olmo7b");                             failures += f
    ctx.update(battery=battery, floors=floors, verify_fn=verify_fn, strata=strata, manifest=manifest,
               predictor_rec=predictor_rec, psl=psl, esl=esl, rung_set=rung_set, r_cap=r_cap,
               stage1_final=stage1_final, gate1=gate1, sweep=sweep, x_b=x_b, bits_b=bits_b, py=py,
               out=out)
    return failures, ctx


# ---------------------------------------------------------- 2k tier

def load_tier_2k(root_2k, size, *, battery, verify_fn, rungs) -> tuple:
    """One size's nine cells: the record's provenance (with 2i's committed
    sha for the cell), the 4-seed rows, GATE 1 RE-DERIVED from 2d's
    committed file (zero diffs, coverage 500 × 64 on both sides), the
    tallies cross-checked against the re-derivation, bits and counts at
    every k. Returns (failures, cells)."""
    failures, cells = [], {}
    root_2k = Path(root_2k)
    for rung in rungs:
        label = f"2k tier {size}/{rung}"
        rp, dp = bk.tier_record_path(root_2k, size, rung), bk.tier_draws_path(root_2k, size, rung)
        if not rp.is_file() or not dp.is_file():
            failures.append(f"{label}: record or draws file missing")
            continue
        rec, f = collect_total(lambda: json.loads(rp.read_text()), f"2k tier {size}/{rung} record read")
        failures += f
        if rec is None:
            continue
        if not isinstance(rec, dict):
            failures.append(f"{label}: record is not a dict")
            continue
        cap = battery[rung]
        bad = bk.tier_record_failures_2k(rec, size=size, rung=rung, cap=cap,
                                         committed_sha=bi.PYTHIA_PREDICTOR_FILES[(size, rung)])
        failures += bad
        rows, f = collect_total(lambda: bk.read_rows_2k(dp), f"2k tier {size}/{rung} rows read")
        failures += f
        if rows is None:
            continue

        def _gate():
            committed = bk.committed_rows(size, rung)
            gz_sha = hashlib.sha256(bk.committed_draws_path(size, rung).read_bytes()).hexdigest()
            if gz_sha != bi.PYTHIA_PREDICTOR_FILES[(size, rung)]:
                raise ValueError(f"committed 2d draws for {size}/{rung} are not at 2i's pin")
            diffs = bk.diff_seed0(rows, committed)
            n_cmp = len(rows) * bk.DRAWS_PER_SEED
            if len(rows) != bk.N_ITEMS or len(committed) != bk.N_ITEMS:
                raise ValueError(f"gate 1 coverage {len(rows)} vs {len(committed)} items")
            if diffs:
                raise ValueError(f"gate 1: {len(diffs)} seed-0 draw(s) differ from 2d's "
                                 f"committed bytes (first {diffs[0]})")
            if rec["gate1"].get("draws_compared") != n_cmp:
                raise ValueError(f"gate 1 attested {rec['gate1'].get('draws_compared')} draws, "
                                 f"re-derived {n_cmp}")
            return {"n_diffs": 0, "draws_compared": n_cmp, "committed_draws_sha256": gz_sha}
        g, f = collect_total(_gate, f"2k tier {size}/{rung} gate 1 re-derived")
        failures += f

        def _bits():
            b = bk.bits_2k(rows, cap, verify_fn)
            t = bk.tallies_2k(rows, cap, verify_fn)
            if t != rec.get("per_seed_tallies"):
                raise ValueError(f"per_seed_tallies {rec.get('per_seed_tallies')} disagree with "
                                 f"the re-derivation {t}")
            return b
        bits, f = collect_total(_bits, f"2k tier {size}/{rung} bits and tallies")
        failures += f
        if bits is None or g is None:
            continue
        cells[rung] = {"bits": bits, "counts": bk.counts_by_k(bits), "record": rec,
                       "gate1_rederived": g}
    return failures, cells


def _seal_paths_2k(root_2k, seal=None) -> list:
    paths = [bk.seal_path(root_2k), bk.power_path(root_2k)]
    for size in bk.SIZES_2K:
        for r in bk.R_CAP_DESIGN:
            paths.append(bk.tier_record_path(root_2k, size, r))
            paths.append(bk.tier_draws_path(root_2k, size, r))
    if isinstance(seal, dict) and isinstance(seal.get("files"), dict):
        known = set(paths)
        for rel in sorted(seal["files"]):
            p = Path(root_2k) / rel
            if p not in known:
                paths.append(p)
                known.add(p)
    return paths


def seal_sha_of(files: dict) -> str:
    lines = "\n".join(f"{rel} {sha}" for rel, sha in sorted(files.items()))
    return hashlib.sha256(lines.encode()).hexdigest()


def seal_failures_2k(seal, cells_by_size, root_2k) -> list:
    """The seal's attestations against the re-derivation (2i F-1: the
    predictor's provenance is measured, never trusted): counts at 256
    and at every ladder k, the sampling block, every file's sha, the
    composite sha, the tag."""
    bad = []
    if not isinstance(seal, dict):
        return ["2k seal: not a dict"]
    if seal.get("tag") != bk.SEAL_TAG_2K:
        bad.append(f"2k seal: tag {seal.get('tag')!r}")
    want_sampling = {"sizes": list(bk.SIZES_2K), "seeds": list(bk.SEEDS_2K),
                     "draws_per_seed": bk.DRAWS_PER_SEED, "k_total": bk.K_TOTAL,
                     "temperature": 1.0, "truncation": "none", "dtype": a2d.SAMPLING_DTYPE,
                     "stream_namespace": a2d.STREAM_NAMESPACE,
                     "model_sha": {s: bk.pythia_sha(s) for s in bk.SIZES_2K}}
    if seal.get("sampling") != want_sampling:
        bad.append(f"2k seal: sampling block {seal.get('sampling')!r} != {want_sampling!r}")
    for size, cells in cells_by_size.items():
        for r, c in cells.items():
            got = (seal.get("counts") or {}).get(size, {}).get(r)
            if got != c["counts"][bk.K_TOTAL]:
                bad.append(f"2k seal: counts[{size}][{r}] != the re-derived 256-draw counts")
            for k in bk.LADDER_K:
                gk = (seal.get("counts_by_k") or {}).get(size, {}).get(str(k), {}).get(r)
                if gk != c["counts"][k]:
                    bad.append(f"2k seal: counts_by_k[{size}][{k}][{r}] != re-derived")
    files = seal.get("files")
    if not isinstance(files, dict):
        bad.append("2k seal: files missing")
    else:
        for rel, sha in files.items():
            p = Path(root_2k) / rel
            if not p.is_file() or bg.sha256_file(p) != sha:
                bad.append(f"2k seal: {rel} missing or changed since the seal")
        if seal.get("sha256") != seal_sha_of(files):
            bad.append("2k seal: sha256 is not the sha of its own files table")
    return bad


def load_power_2k(root_2k, r_cap, seal_sha) -> dict:
    p = bk.power_path(root_2k)
    rec = json.loads(p.read_text())
    if not isinstance(rec, dict) or "primary" not in rec:
        raise ValueError(f"{p}: not a 2k power record")
    prim = rec["primary"]
    if prim.get("declared_status") not in an2i.DECLARED_STATUSES_2I:
        raise ValueError(f"{p}: declared_status {prim.get('declared_status')!r}")
    if set(prim.get("rungs", [])) != set(r_cap):
        raise ValueError(f"{p}: power rungs {prim.get('rungs')} != R_CAP {list(r_cap)}")
    if prim.get("n_trained_steps") != len(bi.trained_steps_7b()):
        raise ValueError(f"{p}: n_trained_steps {prim.get('n_trained_steps')}")
    if rec.get("predictor_sha256") != seal_sha:
        raise ValueError(f"{p}: predictor_sha256 {rec.get('predictor_sha256')!r} is not the "
                         f"sealed predictor's {seal_sha!r} — the record is a claim about a "
                         f"different predictor")
    return rec


# ------------------------------------------------------------ tests

def ladder_2k(bits, out, strata, rungs, size_label, **kw) -> dict:
    return {k: _run_test({r: bk.counts_at_k(bits[r], k) for r in rungs}, f"{size_label}:k{k}",
                         out, strata, rungs, **kw) for k in bk.LADDER_K}


def s1_blocks(bits, out, strata, rungs, size_label, **kw) -> dict:
    per = {str(b): _run_test({r: bk.block_counts(bits[r], b) for r in rungs}, f"{size_label}:s{b}",
                             out, strata, rungs, **kw) for b in range(len(bk.SEEDS_2K))}
    Ts = [v["stratified"]["T"] for v in per.values()]
    finite = [t for t in Ts if t is not None]
    return {"per_seed": per, "T": Ts,
            "mean": float(np.mean(finite)) if finite else None,
            "min": min(finite) if finite else None, "max": max(finite) if finite else None,
            "sd": float(np.std(finite, ddof=1)) if len(finite) > 1 else None,
            "per_rung": {r: [per[str(b)]["per_rung"].get(r, {}).get("d") for b in range(4)]
                         for r in rungs}}


def placement_on_ladder(ladder_b: dict, t) -> dict:
    ks = sorted(ladder_b)
    if t is None:
        return {"k_equivalent": None, "bracket": None}
    if t >= ladder_b[ks[-1]]:
        return {"k_equivalent": None, "bracket": [ks[-1], None]}
    if t < ladder_b[ks[0]]:
        return {"k_equivalent": None, "bracket": [None, ks[0]]}
    for lo, hi in zip(ks, ks[1:]):
        tlo, thi = ladder_b[lo], ladder_b[hi]
        if t == tlo:
            return {"k_equivalent": float(lo), "bracket": [lo, lo]}
        if tlo < t < thi:
            frac = (t - tlo) / (thi - tlo)
            return {"k_equivalent": float(2 ** (np.log2(lo) + frac * (np.log2(hi) - np.log2(lo)))),
                    "bracket": [lo, hi]}
        if t == thi:
            return {"k_equivalent": float(hi), "bracket": [hi, hi]}
    return {"k_equivalent": None, "bracket": None}


def s3_matched(bits_b, x_a64, x_a256, out, strata, rungs, *, ladder_b) -> dict:
    """x_B thinned per rung to k_g = clip(round(256·r̄_A/r̄_B), 1, 64)
    (2j's block machinery, per-rung mean over 64 // k blocks) against
    x_A^(256) on the same outcome/strata (T without permutation, 2j's
    `t_only`); plus x_A^(256)'s placement on 2j's committed x_B ladder."""
    per, means = {}, []
    for r in rungs:
        ra = bk.mean_rate(x_a64[r], bk.DRAWS_PER_SEED)
        rb = bk.mean_rate(fn.counts_from_bits(bits_b[r]), bk.DRAWS_PER_SEED)
        m = bk.matched_k_256(ra, rb)
        reading = an2j._block_reading(r, bits_b[r], m["k"], m["n_blocks"], bi.SIZE_PRED, out, strata)
        per[r] = {**m, "rate_A64": ra, "rate_B64": rb, **reading}
        if reading["mean"] is not None:
            means.append(reading["mean"])
    t_a = an2j.t_only(x_a256, "1b:k256", out, strata, rungs)
    return {"per_rung": per, "thinned_B": {"T": float(np.mean(means)) if means else None},
            "T_A256": t_a["T"], "placement": placement_on_ladder(ladder_b, t_a["T"]),
            "ladder_B_2j": {str(k): v for k, v in ladder_b.items()}}


def s4_partials(x_a256, x_b, out, strata, rungs, **kw) -> dict:
    return {"cross_beyond_within_256": _run_test(
                x_a256, "1b:k256", out, an2i._composite_strata_median(strata, x_b, rungs), rungs, **kw),
            "within_beyond_cross_256": _run_test(
                x_b, bi.SIZE_PRED, out, an2i._composite_strata(strata, x_a256, rungs), rungs, **kw)}


def s5_within_lineage(x_a256, py, strata, rungs, **kw) -> dict:
    r28 = tuple(r for r in rungs if r in bg.R_28)
    r69 = tuple(r for r in rungs if r in bh.R_69)
    return {"to_2.8b": _run_test(x_a256, "1b:k256", py["2.8b"], strata, r28, **kw),
            "to_6.9b": _run_test(x_a256, "1b:k256", py["6.9b"], strata, r69, **kw),
            "rungs_2.8b": list(r28), "rungs_6.9b": list(r69)}


def s7_texture(primary, bits, out, strata, rungs, **kw) -> dict:
    six = tuple(r for r in rungs if r not in ("add3_mid", "sub3_mid", "sub4_mid"))
    pr_ = primary.get("per_rung", {})
    six_d = [pr_[r]["d"] for r in six if r in pr_]
    live = {r: {"k64": sum(1 for c in bk.counts_at_k(bits[r], 64) if c > 0),
                "k256": sum(1 for c in bk.counts_at_k(bits[r], 256) if c > 0)} for r in rungs}
    first = an2i._first_correct_outcome(out, rungs)
    return {"six_carried_rungs": list(six), "six_rung_mean_D": float(np.mean(six_d)) if six_d else None,
            "live_items": live,
            "first_correct": _run_test({r: bk.counts_at_k(bits[r], 256) for r in rungs}, "1b:k256",
                                       first, strata, rungs, **kw)}


# -------------------------------------------------------------- tree

def verdict_tree_2k(failures, primary, power) -> dict:
    if failures:
        return {"verdict": "INSUFFICIENT_DATA", "annotation": None, "declared_status": None,
                "reason": f"{len(failures)} referent/loader/gate failure(s): {list(failures)[:5]}",
                "disclosures": []}
    status = power["declared_status"]
    T, p = primary["stratified"]["T"], primary["stratified"]["p"]
    disclosures = []
    if an2i._is_undefined_2i(primary):
        disclosures.append(DISCLOSURE_UNDEFINED_2K)
    elif len(primary.get("eligible", [])) < 3:
        disclosures.append(DISCLOSURE_THIN_2K)
    if primary["fires"]:
        reason = f"primary fires: T={an2i._fmt_T(T)}, p={p:.4g}; {status}"
        return {"verdict": "DENSITY", "annotation": None, "declared_status": status,
                "reason": "; ".join([reason] + disclosures), "disclosures": disclosures}
    annotation = "structured" if (T is not None and p < ALPHA) else "null"
    reason = (f"primary does not fire: T={an2i._fmt_T(T)}, p={p:.4g} ({annotation})"
              f"{'; ' + primary['named_inside'] if primary.get('named_inside') else ''}; {status}")
    return {"verdict": "NOT-DENSITY", "annotation": annotation, "declared_status": status,
            "reason": "; ".join([reason] + disclosures), "disclosures": disclosures}


def _licensed(tree) -> str:
    v = tree["verdict"]
    if v != "NOT-DENSITY":
        licensed = LICENSED_2K[v]
    else:
        d = tree.get("disclosures") or []
        if DISCLOSURE_UNDEFINED_2K in d:
            licensed = LICENSED_2K["NOT-DENSITY_UNDEFINED"]
        elif DISCLOSURE_THIN_2K in d or tree["declared_status"] == "THIN":
            licensed = LICENSED_2K["NOT-DENSITY_THIN"]
        elif tree["declared_status"] == "POWERED":
            licensed = LICENSED_2K["NOT-DENSITY"]
        else:
            licensed = LICENSED_2K["NOT-DENSITY_UNDERPOWERED"]
    if tree.get("disclosures"):
        licensed = "; ".join([licensed] + list(tree["disclosures"]))
    return licensed


def _git_sha() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=bg.REPO,
                              capture_output=True, text=True).stdout.strip()
    except OSError:
        return ""


_LITERAL = object()


# ----------------------------------------------------------------- run

def run(root_2i=bi.EXP2I, root_2k=EXP2K, *, write=False, n_perm=N_PERM, n_boot=N_BOOT,
        tag_exists=None, blob_sha=None, blobs_bound=None, referents_sha=_LITERAL,
        imports_pinned=_LITERAL, pin_a=None, pin_a410=None, pin_28=None,
        verdict_2i_path=None, verdict_2j_path=None, out_path=None, frozen_check=None) -> dict:
    # `frozen_check` is a TEST-ONLY injection point (Ruling 3, Task 4 build):
    # `bk.check_frozen_2k` refuses unconditionally ("not pinned (build
    # incomplete)") until Task 5 pins `FROZEN_SHA256_2K`, so every world
    # would land INSUFFICIENT_DATA on that refusal alone without a bypass.
    # The worlds pass `lambda: None` through `run_world`'s `**seal`
    # expansion; the campaign never passes this kwarg. Task 5 drops the
    # bypass here once the real pin lands.
    failures = []
    root_2i, root_2k = Path(root_2i), Path(root_2k)
    pin_a = VERDICT_2I_PIN_A if pin_a is None else pin_a
    pin_a410 = VERDICT_2I_PIN_A410 if pin_a410 is None else pin_a410
    pin_28 = VERDICT_2G_PIN_28 if pin_28 is None else pin_28
    if referents_sha is _LITERAL:
        referents_sha = REFERENTS_2K_SHA256
    if imports_pinned is _LITERAL:
        # mirror referents_sha's tri-state: the sentinel reads the
        # module constant and preserves None (unpinned, a refusal)
        # rather than collapsing it to False (an explicit skip) —
        # collapsing early would make a caller who takes the default
        # indistinguishable from one who deliberately opted out.
        imports_pinned = None if IMPORTED_SHA256_2K is None else True

    # ---- the halt scan FIRST (2d F-1): a halted tree never reaches a loader
    for m in bk.halt_markers(root_2k):
        failures.append(f"2k tier HALTED marker present: {m.parent.name}/{m.name}")
    # ---- pins, import surface (entry), prereg, manifest
    _, f = collect_total(frozen_check or bk.check_frozen_2k, "2k frozen modules"); failures += f
    if imports_pinned:
        _, f = collect_total(check_imports_2k, "2k import surface (entry)");       failures += f
    elif imports_pinned is not False:
        failures.append("2k import surface: not pinned (build incomplete)")
    prereg, f = collect_total(lambda: bk.require_prereg_2k(tag_exists=tag_exists, blob_sha=blob_sha),
                              "2k prereg tag");                                     failures += f
    if referents_sha is None:
        failures.append("2k referent manifest: not pinned (build incomplete)")
    elif referents_sha is not False:
        from experiments.exp2k import make_referents_2k as mkr
        mf, f = collect_total(lambda: mkr.check_referents(REFERENTS_PATH_2K, sha_pin=referents_sha),
                              "2k referent manifest");                             failures += f + (mf or [])

    # ---- the 2i tree (2j's block)
    f2, ctx = load_2i_tree(root_2i, tag_exists=tag_exists, blobs_bound=blobs_bound)
    failures += f2
    battery, verify_fn, strata, r_cap, out, x_b, bits_b, py = (
        ctx.get("battery"), ctx.get("verify_fn"), ctx.get("strata"), ctx.get("r_cap"),
        ctx.get("out"), ctx.get("x_b"), ctx.get("bits_b"), ctx.get("py"))

    # ---- the 2k tiers, the seal, the power record
    cells = {}
    if battery is not None and verify_fn is not None and r_cap:
        for size in bk.SIZES_2K:
            f3, c = load_tier_2k(root_2k, size, battery=battery, verify_fn=verify_fn, rungs=r_cap)
            failures += f3
            cells[size] = c
    else:
        failures.append("2k tier: not loaded (battery, verify or rung set missing)")
    seal, f = collect_total(lambda: json.loads(bk.seal_path(root_2k).read_text()), "2k seal read")
    failures += f
    ssl = an2i.require_seal_2i(bk.SEAL_TAG_2K, _seal_paths_2k(root_2k, seal), tag_exists=tag_exists,
                               blobs_bound=blobs_bound)
    failures += [f"2k seal binding: {m}" for m in ssl["failures"]]
    if seal is not None and all(len(cells.get(s, {})) == len(r_cap) for s in bk.SIZES_2K) and r_cap:
        sb, f = collect_total(lambda: seal_failures_2k(seal, cells, root_2k), "2k seal vs re-derivation")
        failures += f + (sb or [])
    power, f = collect_total(
        lambda: load_power_2k(root_2k, r_cap, seal["sha256"]) if (seal and r_cap)
        else (_ for _ in ()).throw(ValueError("seal or rung set missing")), "2k power record")
    failures += f

    # ---- comparison gates (three-way), behind every refusal above
    comparison = None
    if not failures:
        def _cmp():
            v2i = json.loads((Path(verdict_2i_path) if verdict_2i_path
                              else root_2i / "results" / "verdict.json").read_text())
            v2g = json.loads((bg.EXP2G / "results" / "verdict.json").read_text())
            bad = []
            x64 = {s: {r: cells[s][r]["counts"][64] for r in r_cap} for s in bk.SIZES_2K}
            for s in bk.SIZES_2K:
                from_2d = bi.sampler_counts_pythia(s, r_cap)
                for r in r_cap:
                    if x64[s][r] != list(from_2d[r]):
                        bad.append(f"comparison gate 2k counts: x_A^(64) from the sealed 2k rows != "
                                   f"2d's committed count on {s}/{r}")
            kw = dict(n_perm=n_perm, n_boot=n_boot)
            a = _run_test(x64["1b"], "1b", out, strata, r_cap, **kw)
            on_disk = pin_a_from_record_2i(v2i)
            bad += an2j.check_pin({"A": a["stratified"]["T"]}, {"A": on_disk["A"]}, {"A": pin_a},
                                  "comparison gate 2k A64")
            for r in r_cap:
                if a["per_rung"].get(r, {}).get("d") != on_disk["per_rung"].get(r):
                    bad.append(f"comparison gate 2k A per-rung: {r} d differs from 2i's record")
            a410 = _run_test(x64["410m"], "410m", out, strata, r_cap, **kw)
            bad += an2j.check_pin({"A410": a410["stratified"]["T"]}, {"A410": pin_a410_from_record_2i(v2i)},
                                  {"A410": pin_a410}, "comparison gate 2k A410")
            g28 = _run_test(x64["1b"], "1b", py["2.8b"], strata, tuple(bg.R_28), **kw)
            bad += an2j.check_pin({"g28": g28["stratified"]["T"]},
                                  {"g28": an2j.pin_from_record_2g(v2g)["sampler_competitor"]},
                                  {"g28": pin_28}, "comparison gate 2k 2g")
            return {"A64": a, "A64_410m": a410, "A64_to_2.8b": g28, "failures": bad}
        comparison, f = collect_total(_cmp, "2k comparison gate re-derivation");   failures += f
        if comparison:
            failures += comparison["failures"]

    core = None
    if not failures:
        def _core():
            x256 = {r: cells["1b"][r]["counts"][256] for r in r_cap}
            prim = _run_test(x256, "1b:k256", out, strata, r_cap, n_perm=n_perm, n_boot=n_boot)
            # the block gate: the ladder's k=64 point must equal the comparison gate's A exactly
            t64 = _run_test({r: cells["1b"][r]["counts"][64] for r in r_cap}, "1b", out, strata, r_cap,
                            n_perm=n_perm, n_boot=n_boot)["stratified"]["T"]
            if t64 != comparison["A64"]["stratified"]["T"]:
                raise ValueError(f"block gate: k=64 T {t64!r} != comparison gate A "
                                 f"{comparison['A64']['stratified']['T']!r}")
            return prim, x256
        core, f = collect_total(_core, "2k primary");                               failures += f
    if not failures and core is not None:
        _, f = collect_total(check_imports_2k if imports_pinned else (lambda: None),
                             "2k import surface (exit)");                            failures += f

    referents = {"failures": list(failures), "prereg": prereg, "predictor_seal_2i": ctx.get("psl"),
                 "endpoint_seal_2i": ctx.get("esl"), "seal_2k": ssl, "rung_set": ctx.get("rung_set"),
                 "gate1_2k": {s: {r: c["gate1_rederived"] for r, c in cells.get(s, {}).items()}
                              for s in bk.SIZES_2K},
                 "comparison": None if comparison is None else
                     {"A64": comparison["A64"]["stratified"]["T"],
                      "A64_410m": comparison["A64_410m"]["stratified"]["T"],
                      "A64_to_2.8b": comparison["A64_to_2.8b"]["stratified"]["T"],
                      "gate": "PASS" if not comparison["failures"] else "FAIL"},
                 "power": power}
    if failures:
        tree = verdict_tree_2k(failures, None, None)
        v = {"verdict": tree["verdict"], "annotation": None, "reason": tree["reason"],
             "declared_status": None, "known_inputs_caveat": KNOWN_INPUTS_CAVEAT_2K,
             "licensed_sentence": LICENSED_2K["INSUFFICIENT_DATA"], "referents": referents,
             "primary": None, "secondaries": None, "n_perm": n_perm, "git_sha": _git_sha(),
             "model_contact": "none at analysis; predictor-side only at the tier"}
    else:
        prim, x256 = core
        tree = verdict_tree_2k([], prim, power["primary"])
        sec, sec_failures = {}, []

        def _sec(name, thunk):
            val, f = collect_total(thunk, name)
            if f:
                sec[name] = {"failed": f[0]}
                sec_failures.extend(f)
            else:
                sec[name] = val

        kw = dict(n_perm=n_perm, n_boot=n_boot)
        bits1b = {r: cells["1b"][r]["bits"] for r in r_cap}
        x64 = {r: cells["1b"][r]["counts"][64] for r in r_cap}
        def _ladder_b():
            v2j = json.loads((Path(verdict_2j_path) if verdict_2j_path
                              else bg.REPO / "experiments/exp2j/results/verdict.json").read_text())
            return ladder_b_from_record_2j(v2j)
        _sec("S1 block replication 1b", lambda: s1_blocks(bits1b, out, strata, r_cap, "1b", **kw))
        _sec("S2 nested ladder 1b", lambda: ladder_2k(bits1b, out, strata, r_cap, "1b", **kw))
        _sec("S3 matched density 1b", lambda: s3_matched(bits_b, x64, x256, out, strata, r_cap,
                                                        ladder_b=_ladder_b()))
        _sec("S4 partials 1b", lambda: s4_partials(x256, x_b, out, strata, r_cap, **kw))
        _sec("S5 within lineage 1b", lambda: s5_within_lineage(x256, py, strata, r_cap, **kw))

        def _s6():
            b410 = {r: cells["410m"][r]["bits"] for r in r_cap}
            x64_410 = {r: cells["410m"][r]["counts"][64] for r in r_cap}
            x256_410 = {r: cells["410m"][r]["counts"][256] for r in r_cap}
            return {"primary_form": _run_test(x256_410, "410m:k256", out, strata, r_cap, **kw),
                    "S1": s1_blocks(b410, out, strata, r_cap, "410m", **kw),
                    "S2": ladder_2k(b410, out, strata, r_cap, "410m", **kw),
                    "S3": s3_matched(bits_b, x64_410, x256_410, out, strata, r_cap, ladder_b=_ladder_b()),
                    "S4": s4_partials(x256_410, x_b, out, strata, r_cap, **kw),
                    "S5": s5_within_lineage(x256_410, py, strata, r_cap, **kw)}
        _sec("S6 410m replicate", _s6)
        _sec("S7 texture 1b", lambda: s7_texture(prim, bits1b, out, strata, r_cap, **kw))

        def _sens():
            zf = {r: fn.zero_fraction_k(bits_b[r], x256[r]) for r in r_cap}
            six = tuple(r for r in r_cap if r not in ("add3_mid", "sub3_mid", "sub4_mid"))
            return {"zero_fraction_k_B": zf,
                    "thinned_B_zero_fraction_T": an2j.t_only(
                        {r: fn.thinned_counts(bits_b[r], zf[r], 0) for r in r_cap}, bi.SIZE_PRED,
                        out, strata, r_cap)["T"],
                    "primary_six_carried": _run_test({r: x256[r] for r in six}, "1b:k256", out,
                                                     strata, six, **kw)}
        _sec("sensitivities 1b", _sens)
        sec["failures"] = sec_failures
        v = {"verdict": tree["verdict"], "annotation": tree["annotation"], "reason": tree["reason"],
             "declared_status": tree["declared_status"],
             "known_inputs_caveat": KNOWN_INPUTS_CAVEAT_2K, "licensed_sentence": _licensed(tree),
             "referents": referents, "primary": prim, "secondaries": sec, "n_perm": n_perm,
             "git_sha": _git_sha(), "model_contact": "none at analysis; predictor-side only at the tier"}
    if write:
        outp = Path(out_path or RESULTS / "verdict.json")
        outp.parent.mkdir(parents=True, exist_ok=True)
        outp.write_text(json.dumps(an2i._json_safe(v), indent=1, default=an2i._jsonable,
                                   allow_nan=False))
    return v


if __name__ == "__main__":
    v = run(write="--write" in sys.argv)
    print(json.dumps({k: v[k] for k in ("verdict", "annotation", "reason")}, indent=1))
