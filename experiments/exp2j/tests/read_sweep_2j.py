# experiments/exp2j/tests/read_sweep_2j.py
"""Read-sweep: every path opened for READING during one
`analyze_2j.run(n_perm=30, n_boot=10)` call on the REAL committed tree,
classified as (a) on `referents_2j.json`'s manifest, (b) a
`FROZEN_SHA256_2J` module, (c) an `INSTRUMENT_BLOBS_2J` file, (d)
python/stdlib/venv/site-packages, or (e) unpinned verdict input — (e)
must be empty.

The prereg tag `exp2j-preregistered` does not exist yet at this build
task, so `tag_exists=lambda t: True` and `blob_sha` = a callable that
returns the CURRENT ON-DISK sha of whatever path it is asked about are
passed to `an.run()` — SWEEP-ONLY STAND-INS that make `require_prereg_2j`
and the two 2i seal checks compare a file against itself rather than
against a real git tag. This is deliberate and documented: the sweep's
purpose is to enumerate every file `run()` touches on its way to a
verdict, not to exercise tag binding (`verify_referents_2j` check 2
already does that against real git). `blobs_bound` is left at its
default (real git) — 2i's own `PREDICTOR_SEAL_TAG`/`ENDPOINT_SEAL_TAG`
tags DO already exist and bind, since 2i is closed.

At n_perm=30 the comparison gates compare T only (2i's own convention),
so they PASS on the real tree, and the run reaches a real verdict — but
that verdict is NOT the experiment's verdict (n_perm=30 has nothing
like the power/alpha the real campaign will use) and must not be
written anywhere under `results/`. This script only prints the read
table; it never calls `an.run(write=True, ...)`.

Run: `PYTHONDONTWRITEBYTECODE=1 ~/emergence-lab/.venv/bin/python -m
experiments.exp2j.tests.read_sweep_2j` from the repo root."""
from __future__ import annotations

import builtins
import gzip
import io
import pathlib
import sys
import sysconfig
from pathlib import Path

EXP2J = Path(__file__).resolve().parents[1]
if str(EXP2J.parent.parent) not in sys.path:
    sys.path.insert(0, str(EXP2J.parent.parent))

# Pre-import every module analyze_2j.run() touches (directly or via a
# local import inside run()) BEFORE the wrappers go on, so Python's own
# import machinery (which also calls open()) never pollutes the sweep;
# once a module is in sys.modules a later `import`/`from … import` is a
# dict lookup, not a file read.
from experiments.exp2d import analyze_2d as a2d  # noqa: E402,F401
from experiments.exp2d import battery_2d as bt  # noqa: E402,F401
from experiments.exp2g import analyze_2g as an2g  # noqa: E402,F401
from experiments.exp2g import battery_2g as bg  # noqa: E402,F401
from experiments.exp2g import checkpoints_2g as ck2g  # noqa: E402,F401
from experiments.exp2g import predictor_2g as pr  # noqa: E402,F401
from experiments.exp2g import stats_2g as st  # noqa: E402,F401
from experiments.exp2g import strata_2g as sg  # noqa: E402,F401
from experiments.exp2h import analyze_2h as an2h  # noqa: E402,F401
from experiments.exp2h import battery_2h as bh  # noqa: E402,F401
from experiments.exp2i import analyze_2i as an2i  # noqa: E402,F401
from experiments.exp2i import battery_2i as bi  # noqa: E402,F401
from experiments.exp2j import analyze_2j as an  # noqa: E402
from experiments.exp2j import functionals_2j as fn  # noqa: E402,F401
from experiments.exp2j import make_referents_2j as mkr  # noqa: E402

READ_MODES = None  # sentinel — see _is_read_mode


def _is_read_mode(mode) -> bool:
    if mode is None:
        return True             # gzip.open/open default to a read mode
    m = str(mode)
    return "r" in m and not any(c in m for c in "wax+")


class _Sweep:
    def __init__(self):
        self.reads = []          # list of (path_str, source) — source in {open, io.open, gzip, read_text, read_bytes}
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


# battery_2g's OWN frozen-imports pin (`bg.check_frozen_imports_2g`,
# one of the four checks the "frozen imports loop" — Step 4 mutant
# label "2g upstream frozen imports" — runs unconditionally): 14 files
# (exp2b x3, exp2c harness+run/screen, exp2d x3, exp2f x4, exp3c,
# exp1/signatures/stats.py) sha256-checked against `bg.
# FROZEN_IMPORT_SHA256_2G`, a DIFFERENT literal dict than 2j's own
# FROZEN_SHA256_2J — found by this sweep's first run (they showed up
# UNPINNED because the classifier only knew about 2j's own 26-file
# pin); confirmed by a stack-trace probe: the read originates inside
# `bg.check_frozen_imports_2g` -> `bg.sha256_file`, not a plain import.
FROZEN_2G_UPSTREAM = {str(p) for p in bg.FROZEN_IMPORT_SHA256_2G}

# Two checkpoint manifests (`checkpoints_2g.json`, `checkpoints_2h.json`)
# are read inside `load_pythia_outcomes` -> `ck2g.load_manifest(...,
# sha_pin=an2g.CHECKPOINTS_SHA256)` / `an2h.load_manifest_69(...,
# sha_pin=an2h.CHECKPOINTS_2H_SHA256)`: the loader itself sha256-checks
# the raw bytes against a literal constant carried inside analyze_2g.py
# / analyze_2h.py — both of which ARE in FROZEN_SHA256_2J, so the pin
# VALUE is protected transitively even though the checkpoint-manifest
# FILE itself is not a referents_2j.json entry (found by this sweep's
# first run; confirmed by reading `ck2g.load_manifest`'s source, which
# raises ValueError on a hash mismatch before ever returning).
SHA_PIN_AT_LOAD = {str(bg.EXP2G / "checkpoints_2g.json"), str(bh.EXP2H / "checkpoints_2h.json")}


def _classify(paths: set, referents_files: set) -> dict:
    frozen = {str(p) for p in an.FROZEN_SHA256_2J} | FROZEN_2G_UPSTREAM
    instrument = {str(bg.REPO / rel) for rel in an.INSTRUMENT_BLOBS_2J}
    manifest = {str(bg.REPO / rel) for rel in referents_files}
    manifest.add(str(an.REFERENTS_PATH_2J))     # the manifest file pins ITSELF (REFERENTS_2J_SHA256)
    stdlib_dirs = tuple(str(Path(d).resolve()) for d in sysconfig.get_paths().values() if d)
    venv_prefix = str(Path(sys.prefix).resolve())
    base_prefix = str(Path(sys.base_prefix).resolve())
    # library/interpreter probes of a path that doesn't exist on this OS
    # (e.g. a Linux-style /proc/self/maps probed defensively by a C
    # extension's thread-count detection) carry no data either way.
    KNOWN_NONEXISTENT_PROBES = {"/proc/self/maps"}

    buckets = {"referents_2j.json": [], "frozen_module": [], "instrument_blob": [],
              "sha_pin_at_load": [], "python_stdlib_venv": [], "UNPINNED": []}
    for p in sorted(paths):
        rp = str(Path(p).resolve()) if p not in KNOWN_NONEXISTENT_PROBES else p
        if rp in manifest:
            buckets["referents_2j.json"].append(rp)
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
    referents_files = set(mkr.referent_files())
    referents_rel = {str(Path(p).resolve().relative_to(bg.REPO.resolve())) for p in referents_files}

    def blob_sha(tag, rel):
        p = bg.REPO / rel
        return bg.sha256_file(p) if p.is_file() else None

    restore = _install()
    try:
        v = an.run(n_perm=30, n_boot=10, write=False,
                  tag_exists=lambda t: True, blob_sha=blob_sha)
    finally:
        restore()

    print(f"verdict (n_perm=30, NOT the experiment's verdict): {v['verdict']} — {v['reason'][:120]}")
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
    print(f"{'category':<22}{'count':>8}")
    for k, v_ in buckets.items():
        print(f"{k:<22}{len(v_):>8}")
    if buckets["UNPINNED"]:
        print("\nUNPINNED VERDICT INPUTS (must be empty):")
        for p in buckets["UNPINNED"]:
            print("  -", p)
        return 1
    print("\n(e) unpinned verdict input: 0 — clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
