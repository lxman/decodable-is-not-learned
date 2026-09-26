# experiments/exp5b/battery_5b.py
"""The Exp 5b battery (design `experiment-5b-design.md` §3, §10 as ruled):
every input a committed value or a pin over Experiment 5's closed record.
Nothing here is a dial. Zero network: the checkpoint manifest is
Experiment 5's (`battery_5.load_manifest_5`, sha-pinned)."""
from __future__ import annotations

import hashlib
import json
import math
import subprocess
import sys
from pathlib import Path

EXP5B = Path(__file__).resolve().parent
EXPERIMENTS = EXP5B.parent
REPO = EXPERIMENTS.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp5 import _threads_5  # noqa: E402,F401 — the BLAS pin, before numpy
from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp2g import predictor_2g as pr  # noqa: E402
from experiments.exp5 import battery_5 as b5  # noqa: E402

EXP5 = b5.EXP5
RESULTS_5B = EXP5B / "results"
PROJECTION_PATH_5B = EXP5B / "projection.md"

PREREG_TAG_5B = "exp5b-preregistered"
CLOSED_TAG_5B = "exp5b-closed"
INSTRUMENT_BLOBS_5B = (
    "experiments/exp5b/battery_5b.py", "experiments/exp5b/stats_5b.py",
    "experiments/exp5b/collect_5b.py", "experiments/exp5b/analyze_5b.py",
    "experiments/exp5b/power_5b.py", "experiments/exp5b/run/units_5b.py",
    "experiments/exp5b/results/power_5b.json",
)
EXP5_CLOSED_TAG_5B = "exp5-closed"
EXP5_VERDICT_REL_5B = "experiments/exp5/results/verdict.json"
# `shasum -a 256 experiments/exp5/results/verdict.json` at the build (Task 1, step 4)
EXP5_VERDICT_SHA256_5B = "50a6f57e8e4b204adf83d84890fb19cb78eec495a977861e0f6a4cca26d61f11"
# design §3.6 gate 2: the literal subset of Experiment 5's verdict
EXP5_VERDICT_PIN_5B = {
    "verdict": "NOT-MATCHED", "modifier": "MIXED", "T": 0.05349206349206348,
    "n_cells": 63, "n_rungs": 13, "rung_block_p": 0.0006103515625,
    "n_nonzero_blocks": 13, "pairs_kept": 21,
}

# ------------------------------------------------------- the small-side window
WINDOW_STEPS_5B = (142000, 141000, 140000)             # dial b
SIZE_ORDER_5B = ("6.9b", "2.8b", "1.4b", "1b", "410m", "160m")   # dial n
WHYS_5B = ("final", "member")


def small_sides_5b() -> tuple:
    """Read at call time — the synthetic worlds shrink `battery_5.SMALL_SIDES_5`."""
    return tuple(b5.SMALL_SIDES_5)


def unit_steps_5b() -> tuple:
    return (b5.FINAL_STEP_5,) + tuple(WINDOW_STEPS_5B)


def reread_steps_5b() -> tuple:
    """Gate 1's twelve: the final and the first member (Experiment 5's S11 step)."""
    return (b5.FINAL_STEP_5, WINDOW_STEPS_5B[0])


def expected_units_5b() -> set:
    return {(s, st) for s in small_sides_5b() for st in unit_steps_5b()}


# ------------------------------------------------------------ the statistic
PLACEBO_SIGN_5B = 1                                    # dial e: the two moves ADDED
SQRT2_5B = math.sqrt(2.0)
SIGMA_GRID_5B = (5, 10, 15, 20, 30, 45)                # dial h, items per read
SIGMA_BELIEF_5B = 15
ALPHA_CAL_5B = 0.05
LOSS_TOL_5B = 1e-4                                      # gate 1: |Δℓ| on a re-read
SPIKE_PAIR_5B = ("2.8b", "12b")                         # S9
T_BAR_5B = b5.T_BAR_5
ALPHA_5B = b5.ALPHA_5
MIN_LIVE_CELLS_5B = b5.MIN_LIVE_CELLS_5
MIN_NONZERO_BLOCKS_5B = b5.MIN_NONZERO_BLOCKS_5
WORLDS_5B = ("INSUFFICIENT_DATA", "UNDETERMINED", "SURVIVES", "NOT-SURVIVED")
SURVIVES_CELLS_5B = ("CALIBRATED", "INFLATED", "OFF-GRID")
NOT_SURVIVED_CELLS_5B = ("INSIDE", "SIGN-ONLY", "SIZE-ONLY")
# Experiment 5's post-verdict descriptives (results/retrospective.md), printed beside S1/S3/S9
EXP5_REFERENTS_5B = {"row_2p8b_mean_c": 0.117, "outside_2p8b_and_antonyms_T": 0.0112,
                     "outside_2p8b_and_antonyms_p": 0.084, "spike_excluded_T": 0.0417,
                     "spike_excluded_p": 0.00037, "P_mean_items": 12.4, "P_sd_items": 13.6,
                     "mean_R_items": 39.1, "T_exp5_items": 26.7}


# ------------------------------------------------------------------- paths

def units_root_5b(root) -> Path:
    return Path(root) / "results" / "units"


def unit_dir_5b(root, size: str, step: int) -> Path:
    return b5.unit_dir_5(root, size, step)


def unit5b_record_path_5b(root, size, step) -> Path:
    return unit_dir_5b(root, size, step) / "_unit_5b.json"


def host_record_path_5b(root) -> Path:
    return Path(root) / "results" / "host_5b.json"


def gate1_path_5b(root) -> Path:
    return Path(root) / "results" / "gate1_5b.json"


def power_path_5b(root) -> Path:
    return Path(root) / "results" / "power_5b.json"


def halt_marker_path_5b(root, size) -> Path:
    return b5.halt_marker_path_5(root, size)


def unit_complete_5b(root, size, step) -> bool:
    """Experiment 5's completeness (`_unit.json` present and every named
    file at its sha) AND 5b's attestation file, written after it."""
    return b5.unit_complete_5(root, size, step) and unit5b_record_path_5b(root, size, step).is_file()


REREAD_KEYS_5B = ("digest_equal", "digest_here", "digest_committed", "loss_here", "loss_committed",
                  "loss_delta", "per_doc_diffs", "count_abs_diff_sum", "count_abs_diff_max",
                  "continuation_diffs_sum", "byte_identical", "tolerance_failures", "loss_within_tol")


def unit5b_record_failures_5b(rec: dict, *, size, step, host) -> list:
    bad = []
    label = f"{size}/step{int(step)}/_unit_5b"
    for k, v in (("size", size), ("step", int(step)), ("prereg_tag", PREREG_TAG_5B),
                 ("exp5_closed_tag", EXP5_CLOSED_TAG_5B)):
        if rec.get(k) != v:
            bad.append(f"{label}: {k} = {rec.get(k)!r}, expected {v!r}")
    if rec.get("why") not in WHYS_5B:
        bad.append(f"{label}: why {rec.get('why')!r} not in {WHYS_5B}")
    want_reread = int(step) in reread_steps_5b()
    if rec.get("reread") is not want_reread:
        bad.append(f"{label}: reread {rec.get('reread')!r}, expected {want_reread}")
    rr = rec.get("reread_record")
    if want_reread:
        if not isinstance(rr, dict) or any(k not in rr for k in REREAD_KEYS_5B):
            bad.append(f"{label}: reread_record missing or lacks {REREAD_KEYS_5B}")
    elif rr is not None:
        bad.append(f"{label}: reread_record present on a non-re-read unit")
    if rec.get("host_sha256") != host.get("sha256"):
        bad.append(f"{label}: host_sha256 is not the host record's")
    if not isinstance(rec.get("git_sha"), str) or not rec.get("git_sha"):
        bad.append(f"{label}: git_sha missing")
    return bad


def exp5_unit_record_5b(exp5_root, size, step, name: str) -> dict:
    """One of Experiment 5's committed unit files, read-only."""
    p = b5.unit_dir_5(exp5_root, size, step) / name
    if not p.is_file():
        raise FileNotFoundError(p)
    return json.loads(p.read_text())


# ---------------------------------------------------------------- bindings

def require_prereg_5b(*, tag_exists=None, blob_sha=None, blobs=INSTRUMENT_BLOBS_5B) -> dict:
    tag_exists = tag_exists or pr.git_tag_exists
    blob_sha = blob_sha or pr.git_blob_sha256
    if not tag_exists(PREREG_TAG_5B):
        raise RuntimeError(f"preregistration tag {PREREG_TAG_5B} does not exist")
    bound = {}
    for rel in blobs:
        p = REPO / rel
        if not p.is_file():
            raise RuntimeError(f"{rel} not on disk")
        want, got = blob_sha(PREREG_TAG_5B, rel), bg.sha256_file(p)
        if want != got:
            raise RuntimeError(f"tag {PREREG_TAG_5B} does not bind {rel}: tag "
                               f"{str(want)[:12]} vs disk {got[:12]}")
        bound[rel] = got
    return {"tag": PREREG_TAG_5B, "instrument_blobs": bound}


def require_exp5_closed_5b(*, tag_exists=None, blob_sha=None, verdict_sha=None,
                           exp5_root=None) -> dict:
    """Design §3.6 gate 2: `exp5-closed` present, Experiment 5's thirteen
    instrument blobs at that tag equal to disk, and the committed
    verdict.json at its pin (`verdict_sha=False` skips the sha — the
    synthetic worlds' Experiment 5 tree)."""
    tag_exists = tag_exists or pr.git_tag_exists
    blob_sha = blob_sha or pr.git_blob_sha256
    if not tag_exists(EXP5_CLOSED_TAG_5B):
        raise RuntimeError(f"tag {EXP5_CLOSED_TAG_5B} does not exist")
    bound = {}
    for rel in b5.INSTRUMENT_BLOBS_5:
        p = REPO / rel
        if not p.is_file():
            raise RuntimeError(f"{rel} not on disk")
        want, got = blob_sha(EXP5_CLOSED_TAG_5B, rel), bg.sha256_file(p)
        if want != got:
            raise RuntimeError(f"tag {EXP5_CLOSED_TAG_5B} does not bind {rel}: tag "
                               f"{str(want)[:12]} vs disk {got[:12]}")
        bound[rel] = got
    got_v = None
    if verdict_sha is not False:
        want_v = EXP5_VERDICT_SHA256_5B if verdict_sha is None else verdict_sha
        vp = (Path(exp5_root) / "results" / "verdict.json") if exp5_root is not None \
            else REPO / EXP5_VERDICT_REL_5B
        if not vp.is_file():
            raise RuntimeError(f"{vp}: Experiment 5's verdict.json is missing")
        got_v = hashlib.sha256(vp.read_bytes()).hexdigest()
        if got_v != want_v:
            raise RuntimeError(f"verdict.json hashes to {got_v[:12]}, pinned {str(want_v)[:12]}")
    return {"tag": EXP5_CLOSED_TAG_5B, "blobs": bound, "verdict_sha256": got_v}


def exp5_verdict_pin_failures_5b(v5: dict, pin=None) -> list:
    """The literal subset (design §3.6 gate 2); `pin=None` → the module's;
    the worlds pass their own or skip by setting the module pin to None."""
    pin = EXP5_VERDICT_PIN_5B if pin is None else pin
    if pin is None:
        return []
    bad = []
    prim = v5.get("primary") or {}
    rb = prim.get("rung_block") or {}
    checks = (("verdict", v5.get("verdict"), pin["verdict"]),
              ("modifier", (v5.get("tree") or {}).get("modifier"), pin["modifier"]),
              ("T", repr(prim.get("T")), repr(pin["T"])),
              ("n_cells", prim.get("n_cells"), pin["n_cells"]),
              ("n_rungs", prim.get("n_rungs"), pin["n_rungs"]),
              ("rung-block p", repr(rb.get("p")), repr(pin["rung_block_p"])),
              ("n_nonzero_blocks", prim.get("n_nonzero_blocks"), pin["n_nonzero_blocks"]),
              ("pairs_kept", (v5.get("gate4") or {}).get("pairs_kept"), pin["pairs_kept"]))
    for name, got, want in checks:
        if got != want:
            bad.append(f"exp5 verdict pin: {name} = {got!r}, pinned {want!r}")
    return bad


def _strip_volatile(v: dict) -> dict:
    out = dict(v)
    out.pop("meta", None)
    out.pop("pins_active", None)
    return out


def exp5_verdict_equal_failures_5b(rederived: dict, committed: dict) -> list:
    a, b = _strip_volatile(rederived), _strip_volatile(committed)
    if json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True):
        return []
    for k in sorted(set(a) | set(b)):
        if json.dumps(a.get(k), sort_keys=True) != json.dumps(b.get(k), sort_keys=True):
            return [f"exp5 verdict: the re-derived record differs from the committed one at "
                    f"key {k!r} (meta and pins_active excluded)"]
    return ["exp5 verdict: the re-derived record differs from the committed one"]


# ------------------------------------------------------------ frozen pins
FROZEN_SHA256_5B = None          # Task 6: every experiments/ module outside exp5b on the surface
IMPORTED_SHA256_5B = None        # Task 6: exp5b's own non-blob residual


def check_frozen_5b() -> None:
    if FROZEN_SHA256_5B is None:
        raise RuntimeError("FROZEN_SHA256_5B is None — not pinned (build incomplete)")
    bad = [f"{p}" for p, want in FROZEN_SHA256_5B.items()
           if not Path(p).is_file() or bg.sha256_file(p) != want]
    if bad:
        raise RuntimeError("5b: a frozen module drifted from its pin: " + "; ".join(bad))


def check_imports_5b() -> None:
    """Lesson 11 (2j F-1): every module under `experiments/` this process
    has imported (tests excluded) is pinned — `FROZEN_SHA256_5B`
    (drift-checked), an `INSTRUMENT_BLOBS_5B` file, or `IMPORTED_SHA256_5B`
    (drift-checked). Experiment 5's modules are in FROZEN_SHA256_5B."""
    if IMPORTED_SHA256_5B is None or FROZEN_SHA256_5B is None:
        raise RuntimeError("the import surface is not pinned (build incomplete)")
    pinned = {str(Path(p).resolve()): v for p, v in FROZEN_SHA256_5B.items()}
    pinned |= {str(Path(p).resolve()): v for p, v in IMPORTED_SHA256_5B.items()}
    covered = {str((REPO / rel).resolve()) for rel in INSTRUMENT_BLOBS_5B}
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


# ------------------------------------------------------------------- git

def git_sha_5b() -> str:
    return b5.git_sha_5()


def is_ancestor_5b(a: str, b: str) -> bool:
    return b5.is_ancestor_5(a, b)


def projection_commit_5b():
    out = subprocess.run(["git", "log", "--diff-filter=A", "--format=%H", "--",
                          "experiments/exp5b/projection.md"], cwd=REPO,
                         capture_output=True, text=True)
    lines = [ln for ln in out.stdout.strip().splitlines() if ln]
    return lines[-1] if lines else None


def projection_edits_5b(adding_commit: str, *, repo=None) -> list:
    """Experiment 5's F-5, for 5b's projection: every commit after the
    adding commit that touches it, plus a working-tree drift."""
    repo = REPO if repo is None else Path(repo)
    rel = "experiments/exp5b/projection.md"
    out = []
    later = subprocess.run(["git", "log", "--format=%H", f"{adding_commit}..HEAD", "--", rel],
                           cwd=repo, capture_output=True, text=True)
    if later.returncode != 0:
        return [f"projection: git log {adding_commit}..HEAD failed: {later.stderr.strip()[:120]}"]
    out += [f"projection: commit {c} modifies {rel} after its adding commit {adding_commit}"
            for c in later.stdout.split() if c]
    want = subprocess.run(["git", "rev-parse", f"{adding_commit}:{rel}"], cwd=repo,
                          capture_output=True, text=True).stdout.strip()
    got = subprocess.run(["git", "hash-object", str(repo / rel)], cwd=repo,
                         capture_output=True, text=True)
    if got.returncode != 0 or not want or got.stdout.strip() != want:
        out.append(f"projection: the working-tree {rel} ({got.stdout.strip()[:12] or 'missing'}) "
                   f"is not the blob its adding commit added ({want[:12] or 'none'})")
    return out


def prereg_tag_commit_5b():
    out = subprocess.run(["git", "rev-list", "-n", "1", PREREG_TAG_5B], cwd=REPO,
                         capture_output=True, text=True)
    sha = out.stdout.strip()
    return sha or None
