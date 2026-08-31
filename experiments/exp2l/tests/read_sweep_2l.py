# experiments/exp2l/tests/read_sweep_2l.py
"""Read-sweep: every path opened for READING during one
`analyze_2l.run(n_perm=30, n_boot=10)` call on the REAL committed
pre-campaign tree, classified as (a) on `referents_2l.json`'s manifest,
(b) a `FROZEN_SHA256_2L` / `battery_2g.FROZEN_IMPORT_SHA256_2G` /
`IMPORTED_SHA256_2L` / `an2j.IMPORTED_SHA256_2J` / `an2k.IMPORTED_SHA256_2K`
module, (c) an `INSTRUMENT_BLOBS_2L` file, (d) python/stdlib/venv/
site-packages, (e) unpinned verdict input — must be empty, (f) an
endpoint-seal-bound campaign artifact absent pre-campaign (the 68
endpoint records + rung set + power record via `_endpoint_seal_paths_2l`,
the 595-path sweep tree, `gate1.json`, the halt marker — attempted-but-
failed opens the wrapper still records, classified separately since
they are bound by `exp2l-endpoint-sealed` rather than the pre-campaign
manifest), or (g) sha-pinned at load (`checkpoints_2g.json`/
`checkpoints_2h.json` — 2k's own bucket, inherited — plus
`checkpoints_2i.json` via `CHECKPOINTS_2I_SHA256` in frozen
`battery_2i.py`, and `checkpoints_2l.json` via `CHECKPOINTS_2L_SHA256`
in the tag-bound `battery_2l.py`).

The prereg tag `exp2l-preregistered` does not exist yet at this build
task, so `tag_exists=lambda t: True` and `blob_sha` = a callable that
returns the CURRENT ON-DISK sha of whatever path it is asked about are
passed to `an.run()` — SWEEP-ONLY STAND-INS that make `require_prereg_2l`
compare a file against itself rather than against a real git tag (2j's/
2k's precedent). `blobs_bound` is left at its DEFAULT (real git), so
2k's `exp2k-predictor-sealed` and 2i's `exp2i-predictor-sealed` bind
against REAL git — both experiments are closed, their tags exist and
bind for real. `referents_sha`, `imports_pinned` and `frozen_check` are
all left at their real, pinned defaults: on this committed tree they
should PASS for real, not need a bypass.

The sweep covers `open`/`io.open`/`gzip.open`/`Path.read_text`/
`read_bytes` — the DATA surface. It does NOT and cannot cover the
IMPORT surface (closed separately by `analyze_2l.check_imports_2l`,
Task 5's `tests/import_scan_2l.py`) — this script pre-imports
everything so import traffic stays out of the table.

On the pre-campaign tree `run()` lands INSUFFICIENT_DATA once it
reaches the 13B endpoint/rung-set/power stage (no campaign has run) —
the sweep still enumerates every predictor-side read the tree reaches
(2k's tier, 2i's sealed OLMo-2 1B counts, both fully real and closed)
before refusing. That verdict is NOT the experiment's verdict
(n_perm=30 has none of the real campaign's power/alpha) and must never
be written under `results/`; this script only prints the read table and
never calls `an.run(write=True, ...)`.

Run: `PYTHONDONTWRITEBYTECODE=1 ~/emergence-lab/.venv/bin/python -m
experiments.exp2l.tests.read_sweep_2l` from the repo root. Re-run once
AFTER the endpoint seal tag exists (process tail) — (e) must still be
empty, and the campaign-side paths in (f) should then start resolving
for real."""
from __future__ import annotations

import builtins
import gzip
import io
import json
import pathlib
import sys
import sysconfig
from pathlib import Path

EXP2L = Path(__file__).resolve().parents[1]
if str(EXP2L.parent.parent) not in sys.path:
    sys.path.insert(0, str(EXP2L.parent.parent))

# Pre-import every module analyze_2l.run() touches (directly or via a
# local import inside run()/load_predictors_2l) BEFORE the wrappers go
# on, so Python's own import machinery (which also calls open()) never
# pollutes the sweep; once a module is in sys.modules a later import is
# a dict lookup, not a file read.
from experiments.exp2d import analyze_2d as a2d  # noqa: E402,F401
from experiments.exp2d import battery_2d as bt  # noqa: E402,F401
from experiments.exp2d import stats_2d as st2d  # noqa: E402,F401
from experiments.exp2g import battery_2g as bg  # noqa: E402,F401
from experiments.exp2g import predictor_2g as pr  # noqa: E402,F401
from experiments.exp2g import stats_2g as st  # noqa: E402,F401
from experiments.exp2g import strata_2g as sg  # noqa: E402,F401
from experiments.exp2h import battery_2h as bh  # noqa: E402,F401
from experiments.exp2i import analyze_2i as an2i  # noqa: E402,F401
from experiments.exp2i import battery_2i as bi  # noqa: E402,F401
from experiments.exp2j import analyze_2j as an2j  # noqa: E402,F401
from experiments.exp2j import functionals_2j as fn  # noqa: E402,F401
from experiments.exp2k import analyze_2k as an2k  # noqa: E402,F401
from experiments.exp2k import battery_2k as bk  # noqa: E402,F401
from experiments.exp2l import analyze_2l as an  # noqa: E402
from experiments.exp2l import battery_2l as bl  # noqa: E402,F401
from experiments.exp2l import make_referents_2l as mkr  # noqa: E402

READ_MODES = None  # sentinel — see _is_read_mode


def _is_read_mode(mode) -> bool:
    if mode is None:
        return True             # gzip.open/open default to a read mode
    m = str(mode)
    return "r" in m and not any(c in m for c in "wax+")


class _Sweep:
    def __init__(self):
        self.reads = []          # list of (path_str, source)
        self.writes = []

    def record(self, path, mode, source):
        try:
            p = str(Path(path))
        except TypeError:
            return               # a file descriptor (int) or file-like object, not a path
        if _is_read_mode(mode):
            self.reads.append((p, source))
        else:
            self.writes.append((p, mode, source))


SWEEP = _Sweep()


def _install():
    orig_open = builtins.open
    orig_io_open = io.open
    orig_gzip_open = gzip.open
    orig_read_text = pathlib.Path.read_text
    orig_read_bytes = pathlib.Path.read_bytes

    def wrapped_open(file, mode="r", *a, **kw):
        SWEEP.record(file, mode, "open")
        return orig_open(file, mode, *a, **kw)

    def wrapped_io_open(file, mode="r", *a, **kw):
        SWEEP.record(file, mode, "io.open")
        return orig_io_open(file, mode, *a, **kw)

    def wrapped_gzip_open(filename, mode="rb", *a, **kw):
        SWEEP.record(filename, mode, "gzip.open")
        return orig_gzip_open(filename, mode, *a, **kw)

    def wrapped_read_text(self, *a, **kw):
        SWEEP.record(self, "r", "Path.read_text")
        return orig_read_text(self, *a, **kw)

    def wrapped_read_bytes(self):
        SWEEP.record(self, "rb", "Path.read_bytes")
        return orig_read_bytes(self)

    builtins.open = wrapped_open
    io.open = wrapped_io_open
    gzip.open = wrapped_gzip_open
    pathlib.Path.read_text = wrapped_read_text
    pathlib.Path.read_bytes = wrapped_read_bytes

    def restore():
        builtins.open = orig_open
        io.open = orig_io_open
        gzip.open = orig_gzip_open
        pathlib.Path.read_text = orig_read_text
        pathlib.Path.read_bytes = orig_read_bytes

    return restore


# battery_2g's OWN frozen-imports pin: sha256-checked against
# `bg.FROZEN_IMPORT_SHA256_2G`, a DIFFERENT literal dict than 2l's own
# `FROZEN_SHA256_2L` — folded in here the same way 2j's/2k's sweeps did.
FROZEN_2G_UPSTREAM = {str(p) for p in bg.FROZEN_IMPORT_SHA256_2G}

# The campaign-side paths (2j's F-2/2i's F-1/2k's F-1 lineage: bound by
# the ENDPOINT SEAL TAG, not the pre-campaign manifest): the 68 endpoint
# records + rung set + power record, the 595-path sweep tree (17 steps
# incl. real step 0 x 34 rungs, plus one checkpoint record per step),
# `gate1.json`, and the halt marker. Attempted-but-failed opens the
# wrapper still records.
def _sweep_tree_paths_2l() -> set:
    paths = set()
    for step in bl.GRID_13B + (bl.STEP0,):
        for r in bt.RUNGS:
            paths.add(str(bl.record_path(bl.EXP2L, step, r)))
        paths.add(str(bl.checkpoint_record_path(bl.EXP2L, step)))
    return paths


SEAL_BOUND_CAMPAIGN_PATHS = {str(p) for p in an._endpoint_seal_paths_2l(bl.EXP2L)}
SEAL_BOUND_CAMPAIGN_PATHS |= _sweep_tree_paths_2l()
SEAL_BOUND_CAMPAIGN_PATHS |= {str(bl.gate1_path(bl.EXP2L)), str(bl.halt_marker_path(bl.EXP2L))}

# Checkpoint manifests read inside `an.load_predictors_2l` (2k's tier via
# `analyze_2k.load_tier_2k` -> `an2j.load_pythia_outcomes` ->
# `ck2g.load_manifest(..., sha_pin=an2g.CHECKPOINTS_SHA256)` /
# `an2h.load_manifest_69(..., sha_pin=an2h.CHECKPOINTS_2H_SHA256)`) and
# directly by `an.run()` (2i's OLMo-2 1B manifest via
# `bi.load_manifest(bi.CHECKPOINTS_PATH, sha_pin=bi.CHECKPOINTS_2I_SHA256)`,
# 2l's own 13B manifest via `bl.load_manifest_13b(..., sha_pin=
# bl.CHECKPOINTS_2L_SHA256)`): the loader itself sha256-checks the raw
# bytes against a literal constant carried inside analyze_2g.py /
# analyze_2h.py (both IN FROZEN_SHA256_2L, inherited via 2k's/2j's own
# pins) / battery_2i.py (IN FROZEN_SHA256_2L directly) / battery_2l.py
# (one of the four tag-bound INSTRUMENT_BLOBS_2L) — so the pin VALUE is
# protected transitively even though the checkpoint-manifest FILE itself
# is not a referents_2l.json entry (2j's/2k's finding, one experiment
# over — the SHA_PIN_AT_LOAD bucket).
SHA_PIN_AT_LOAD = {str(bg.EXP2G / "checkpoints_2g.json"), str(bh.EXP2H / "checkpoints_2h.json"),
                  str(bi.CHECKPOINTS_PATH), str(bl.CHECKPOINTS_PATH)}


def _classify(paths: set, referents_files: set) -> dict:
    frozen = {str(p) for p in bl.FROZEN_SHA256_2L} | FROZEN_2G_UPSTREAM
    frozen |= {str(p) for p in an.IMPORTED_SHA256_2L}          # Task 5's own residual pin
    frozen |= {str(p) for p in an2j.IMPORTED_SHA256_2J}        # folded into IMPORTED_SHA256_2L's check
    frozen |= {str(p) for p in an2k.IMPORTED_SHA256_2K}        # folded into IMPORTED_SHA256_2L's check
    instrument = {str(bg.REPO / rel) for rel in bl.INSTRUMENT_BLOBS_2L}
    manifest = {str(bg.REPO / rel) for rel in referents_files}
    manifest.add(str(an.REFERENTS_PATH_2L))    # the manifest file pins ITSELF (REFERENTS_2L_SHA256)
    stdlib_dirs = tuple(str(Path(d).resolve()) + "/" for d in sysconfig.get_paths().values() if d)
    venv_prefix = str(Path(sys.prefix).resolve()) + "/"
    base_prefix = str(Path(sys.base_prefix).resolve()) + "/"
    KNOWN_NONEXISTENT_PROBES = {"/proc/self/maps"}

    buckets = {"referents_2l.json": [], "frozen_module": [], "instrument_blob": [],
              "sha_pin_at_load": [], "seal_bound_campaign_absent": [],
              "python_stdlib_venv": [], "UNPINNED": []}
    for p in sorted(paths):
        if p in SEAL_BOUND_CAMPAIGN_PATHS:
            buckets["seal_bound_campaign_absent"].append(p)
            continue
        rp = str(Path(p).resolve()) if p not in KNOWN_NONEXISTENT_PROBES else p
        if rp in manifest:
            buckets["referents_2l.json"].append(rp)
        elif rp in frozen:
            buckets["frozen_module"].append(rp)
        elif rp in instrument:
            buckets["instrument_blob"].append(rp)
        elif rp in SHA_PIN_AT_LOAD:
            buckets["sha_pin_at_load"].append(rp)
        elif p in KNOWN_NONEXISTENT_PROBES or rp.startswith(venv_prefix) \
                or any(rp.startswith(d) for d in stdlib_dirs) \
                or "/site-packages/" in rp or rp.startswith(base_prefix):
            buckets["python_stdlib_venv"].append(rp)
        else:
            buckets["UNPINNED"].append(rp)
    return buckets


def main() -> int:
    referents_rel = set(json.loads(an.REFERENTS_PATH_2L.read_text())["files"])
    live_rel = {str(Path(p).resolve().relative_to(bg.REPO.resolve()))
                for p in mkr.referent_files()}
    if live_rel != referents_rel:
        print(f"NOTE: referent_files() lists {len(live_rel)} files, the committed manifest "
              f"{len(referents_rel)}; only-live={sorted(live_rel - referents_rel)[:5]}, "
              f"only-manifest={sorted(referents_rel - live_rel)[:5]}")

    def blob_sha(tag, rel):
        p = bg.REPO / rel
        return bg.sha256_file(p) if p.is_file() else None

    restore = _install()
    try:
        v = an.run(n_perm=30, n_boot=10, write=False, tag_exists=lambda t: True, blob_sha=blob_sha)
    finally:
        restore()

    print(f"verdict (n_perm=30, NOT the experiment's verdict): {v['verdict']} — {v['reason'][:160]}")
    if v["referents"]["failures"]:
        print(f"  ({len(v['referents']['failures'])} referent failure(s) — see below)")
        for f in v["referents"]["failures"][:10]:
            print("   -", f)

    distinct_reads = {p for p, _src in SWEEP.reads}
    buckets = _classify(distinct_reads, referents_rel)

    print(f"\n{len(distinct_reads)} distinct paths opened for reading "
         f"({len(SWEEP.reads)} total open/read calls)")
    print(f"  writes observed (should be 0, write=False): {len(SWEEP.writes)}")
    for w in SWEEP.writes[:10]:
        print("   - WRITE", w)
    print()
    print(f"{'category':<28}{'count':>8}")
    for k, v_ in buckets.items():
        print(f"{k:<28}{len(v_):>8}")
    if buckets["UNPINNED"]:
        print("\nUNPINNED VERDICT INPUTS (must be empty):")
        for p in buckets["UNPINNED"]:
            print("  -", p)
        return 1
    print("\n(e) unpinned verdict input: 0 — clean")
    print(f"(f) seal-bound campaign artifact, absent pre-campaign: "
         f"{len(buckets['seal_bound_campaign_absent'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
