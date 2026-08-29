# experiments/exp2k/tests/read_sweep_2k.py
"""Read-sweep: every path opened for READING during one
`analyze_2k.run(n_perm=30, n_boot=10)` call on the REAL committed
pre-campaign tree, classified as (a) on `referents_2k.json`'s manifest,
(b) a `FROZEN_SHA256_2K` / `battery_2g.FROZEN_IMPORT_SHA256_2G` /
`IMPORTED_SHA256_2K` module, (c) an `INSTRUMENT_BLOBS_2K` file, (d)
python/stdlib/venv/site-packages, (e) unpinned verdict input — must be
empty, or (f) seal-bound campaign artifact, absent pre-campaign (the
2k tier records/draws, the seal, and the power record: attempted-but-
failed opens the wrapper still records, classified separately since
they are bound by the seal tag rather than the pre-campaign manifest).

The prereg tag `exp2k-preregistered` does not exist yet at this build
task, so `tag_exists=lambda t: True` and `blob_sha` = a callable that
returns the CURRENT ON-DISK sha of whatever path it is asked about are
passed to `an.run()` — SWEEP-ONLY STAND-INS that make `require_prereg_2k`
compare a file against itself rather than against a real git tag (2j's
precedent). The two 2i seal checks (`predictor_seal_2i`,
`endpoint_seal_2i`) take `tag_exists`/`blobs_bound`, and `blobs_bound`
is left at its default, so those two run against REAL git — 2i is
closed, its tags exist and bind for real. `referents_sha`, `imports_pinned`
and `frozen_check` are all left at their real, pinned defaults: on this
committed tree they should PASS for real, not need a bypass.

The sweep covers `open`/`io.open`/`gzip.open`/`Path.read_text`/
`read_bytes` — the DATA surface. It does NOT and cannot cover the
IMPORT surface (closed separately by `analyze_2k.check_imports_2k`,
Task 5's `tests/import_scan_2k.py`) — this script pre-imports
everything so import traffic stays out of the table.

On the pre-campaign tree `run()` lands INSUFFICIENT_DATA at the 2k
tier (no campaign has run) — the sweep still enumerates every 2i-side
read the tree reaches before refusing, plus the 2k-side halt scan and
the attempted (failing) reads of the campaign artifacts. That verdict
is NOT the experiment's verdict (n_perm=30 has none of the real
campaign's power/alpha) and must never be written under `results/`;
this script only prints the read table and never calls
`an.run(write=True, ...)`.

Run: `PYTHONDONTWRITEBYTECODE=1 ~/emergence-lab/.venv/bin/python -m
experiments.exp2k.tests.read_sweep_2k` from the repo root. Re-run once
AFTER the seal tag exists (process tail) — (e) must still be empty,
and the campaign-side paths in (f) should then resolve for real."""
from __future__ import annotations

import builtins
import gzip
import io
import json
import pathlib
import sys
import sysconfig
from pathlib import Path

EXP2K = Path(__file__).resolve().parents[1]
if str(EXP2K.parent.parent) not in sys.path:
    sys.path.insert(0, str(EXP2K.parent.parent))

# Pre-import every module analyze_2k.run() touches (directly or via a
# local import inside run()/load_2i_tree/load_tier_2k) BEFORE the
# wrappers go on, so Python's own import machinery (which also calls
# open()) never pollutes the sweep; once a module is in sys.modules a
# later import is a dict lookup, not a file read.
from experiments.exp2d import analyze_2d as a2d  # noqa: E402,F401
from experiments.exp2d import battery_2d as bt  # noqa: E402,F401
from experiments.exp2g import battery_2g as bg  # noqa: E402,F401
from experiments.exp2g import predictor_2g as pr  # noqa: E402,F401
from experiments.exp2g import stats_2g as st  # noqa: E402,F401
from experiments.exp2g import strata_2g as sg  # noqa: E402,F401
from experiments.exp2h import battery_2h as bh  # noqa: E402,F401
from experiments.exp2i import analyze_2i as an2i  # noqa: E402,F401
from experiments.exp2i import battery_2i as bi  # noqa: E402,F401
from experiments.exp2j import analyze_2j as an2j  # noqa: E402,F401
from experiments.exp2j import functionals_2j as fn  # noqa: E402,F401
from experiments.exp2k import analyze_2k as an  # noqa: E402
from experiments.exp2k import battery_2k as bk  # noqa: E402,F401
from experiments.exp2k import make_referents_2k as mkr  # noqa: E402

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
# `bg.FROZEN_IMPORT_SHA256_2G`, a DIFFERENT literal dict than 2k's own
# `FROZEN_SHA256_2K` — 2j's sweep found these show up UNPINNED if the
# classifier only knows about 2k's own pin; folded in here the same way.
FROZEN_2G_UPSTREAM = {str(p) for p in bg.FROZEN_IMPORT_SHA256_2G}

# The campaign-side paths (2j's F-2/2i's F-1 lineage: bound by the SEAL
# TAG, not the pre-campaign manifest) — `_seal_paths_2k`'s own base list
# before any seal `files` dict is merged in (that dict does not exist
# pre-campaign). Attempted-but-failed opens the wrapper still records.
SEAL_BOUND_CAMPAIGN_PATHS = {str(p) for p in an._seal_paths_2k(bk.EXP2K)}

# Two checkpoint manifests read inside `an2j.load_pythia_outcomes` ->
# `ck2g.load_manifest(..., sha_pin=an2g.CHECKPOINTS_SHA256)` /
# `an2h.load_manifest_69(..., sha_pin=an2h.CHECKPOINTS_2H_SHA256)`: the
# loader itself sha256-checks the raw bytes against a literal constant
# carried inside analyze_2g.py / analyze_2h.py — both of which ARE in
# FROZEN_SHA256_2K (inherited via an2j.FROZEN_SHA256_2J) — so the pin
# VALUE is protected transitively even though the checkpoint-manifest
# FILE itself is not a referents_2k.json entry (2j's read_sweep_2j.py
# finding, one experiment over — its own `SHA_PIN_AT_LOAD` bucket).
SHA_PIN_AT_LOAD = {str(bg.EXP2G / "checkpoints_2g.json"), str(bh.EXP2H / "checkpoints_2h.json")}


def _classify(paths: set, referents_files: set) -> dict:
    frozen = {str(p) for p in bk.FROZEN_SHA256_2K} | FROZEN_2G_UPSTREAM
    frozen |= {str(p) for p in an.IMPORTED_SHA256_2K}          # Task 5's own residual pin
    frozen |= {str(p) for p in an2j.IMPORTED_SHA256_2J}        # folded into IMPORTED_SHA256_2K's check
    instrument = {str(bg.REPO / rel) for rel in bk.INSTRUMENT_BLOBS_2K}
    manifest = {str(bg.REPO / rel) for rel in referents_files}
    manifest.add(str(an.REFERENTS_PATH_2K))    # the manifest file pins ITSELF (REFERENTS_2K_SHA256)
    stdlib_dirs = tuple(str(Path(d).resolve()) + "/" for d in sysconfig.get_paths().values() if d)
    venv_prefix = str(Path(sys.prefix).resolve()) + "/"
    base_prefix = str(Path(sys.base_prefix).resolve()) + "/"
    KNOWN_NONEXISTENT_PROBES = {"/proc/self/maps"}

    buckets = {"referents_2k.json": [], "frozen_module": [], "instrument_blob": [],
              "sha_pin_at_load": [], "seal_bound_campaign_absent": [],
              "python_stdlib_venv": [], "UNPINNED": []}
    for p in sorted(paths):
        if p in SEAL_BOUND_CAMPAIGN_PATHS:
            buckets["seal_bound_campaign_absent"].append(p)
            continue
        rp = str(Path(p).resolve()) if p not in KNOWN_NONEXISTENT_PROBES else p
        if rp in manifest:
            buckets["referents_2k.json"].append(rp)
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
    referents_rel = set(json.loads(an.REFERENTS_PATH_2K.read_text())["files"])
    live_rel = {str(Path(p).resolve().relative_to(bg.REPO.resolve()))
                for p in mkr.referent_files(with_campaign=False)}
    if live_rel != referents_rel:
        print(f"NOTE: referent_files(with_campaign=False) lists {len(live_rel)} files, the "
              f"committed manifest {len(referents_rel)}; only-live={sorted(live_rel - referents_rel)[:5]}, "
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
