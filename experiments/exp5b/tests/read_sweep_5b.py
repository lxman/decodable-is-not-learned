# experiments/exp5b/tests/read_sweep_5b.py
"""Read-sweep: every path opened for READING during one `analyze_5b.run(
root=battery_5b.EXP5B, n_sample=10, n_boot=10, referents_sha=<pin>,
imports_pinned=True)` call on the REAL, pre-campaign exp5b tree
(Experiment 5's own `read_sweep_5.py` shape). No 5b campaign data exists
yet, so `run()` proceeds through the halt/frozen/imports/prereg/exp5-
closed/manifest/slice/referents/battery/floors/verify loads, then runs
Experiment 5's WHOLE analyzer in-process as gate 2 (≈ 90 s — Experiment
5's own closed record still reproduces, so gate 2 itself does not
refuse), and refuses at `"5b host record"` (no `results/host_5b.json`
on the real tree) — every such execution is a pre-tag disclosure event,
counted in `PROGRESS.md`.

Classifies every distinct read path into:
  (a) `referents_5b.json`'s own manifest (Experiment 5's referents plus
      its whole results tree, its thirteen instrument blobs and its own
      referents_5.json)
  (b) a pinned module (`battery_5b.FROZEN_SHA256_5B` /
      `battery_5b.IMPORTED_SHA256_5B`)
  (c) an `INSTRUMENT_BLOBS_5B` file (5b's own tag-bound instrument)
  (d) python/stdlib/venv/site-packages
  (e) UNPINNED verdict input — must be 0
  (f) sha-pinned AT LOAD, independent of (a)/(c): `checkpoints_5.json`
      (`battery_5.load_manifest_5`'s own `sha_pin=`), `slice_5.npz`
      (`slice_5.load_slice_5`'s own `sha_pin=`), 2d's `results/
      verdict.json` (`battery_2g.load_floors`'s own `sha_pin=`, read
      through `battery_5.load_floors_5`), `referents_5b.json` itself
      (`make_referents_5b.check_referents_5b`'s own `sha_pin=`), and
      Experiment 5's `results/verdict.json` (the `exp5-closed` binding's
      own sha check, `require_exp5_closed_5b`) — five items, one beyond
      Experiment 5's own four-item list, disclosed: 5b's verdict-sha
      binding is a second sha-pinned-at-load read of the SAME Experiment
      5 verdict.json that (a)'s manifest also lists by content — it
      belongs here because ITS OWN mechanism is a `sha_pin=` compare
      independent of the manifest, same reasoning as Experiment 5's own
      referents_5.json disclosure.

The sweep covers `open`/`io.open`/`Path.read_text`/`read_bytes`/
`numpy.load` — the DATA surface, not the IMPORT surface (closed
separately by `battery_5b.check_imports_5b`, `import_scan_5b.py`) —
this script pre-imports everything so import traffic stays out of the
table.

Run: `PYTHONDONTWRITEBYTECODE=1 ~/emergence-lab/.venv/bin/python -m
experiments.exp5b.tests.read_sweep_5b` from the repo root."""
from __future__ import annotations

import builtins
import io
import json
import pathlib
import sys
import sysconfig
from pathlib import Path

EXP5B = Path(__file__).resolve().parents[1]
REPO = EXP5B.parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

# Pre-import every module analyze_5b.run() (and the stage tools) touch
# BEFORE the wrappers go on, so Python's own import machinery never
# pollutes the sweep.
from experiments.exp2d import analyze_2d as a2d  # noqa: E402,F401
from experiments.exp2d import battery_2d as bt  # noqa: E402,F401
from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp2g import predictor_2g as pr  # noqa: E402,F401
from experiments.exp2i import analyze_2i as an2i  # noqa: E402,F401
from experiments.exp5 import analyze_5 as an5  # noqa: E402,F401
from experiments.exp5 import battery_5 as b5  # noqa: E402
from experiments.exp5 import make_referents_5 as mkr5  # noqa: E402,F401
from experiments.exp5 import power_5 as pw5  # noqa: E402,F401
from experiments.exp5 import search_5 as se5  # noqa: E402,F401
from experiments.exp5 import slice_5 as sl5  # noqa: E402,F401
from experiments.exp5b import analyze_5b as an  # noqa: E402
from experiments.exp5b import battery_5b as b5b  # noqa: E402
from experiments.exp5b import collect_5b as c5b  # noqa: E402,F401
from experiments.exp5b import make_referents_5b as mkr  # noqa: E402,F401
from experiments.exp5b import power_5b as pw5b  # noqa: E402,F401
from experiments.exp5b import stats_5b as st  # noqa: E402,F401


def _is_read_mode(mode) -> bool:
    if mode is None:
        return True
    m = str(mode)
    return "r" in m and not any(c in m for c in "wax+")


class _Sweep:
    def __init__(self):
        self.reads = []
        self.writes = []

    def record(self, path, mode, source):
        try:
            p = str(Path(path))
        except TypeError:
            return
        if _is_read_mode(mode):
            self.reads.append((p, source))
        else:
            self.writes.append((p, mode, source))


SWEEP = _Sweep()


def _install():
    import numpy as np
    orig_open = builtins.open
    orig_io_open = io.open
    orig_read_text = pathlib.Path.read_text
    orig_read_bytes = pathlib.Path.read_bytes
    orig_np_load = np.load

    def wrapped_open(file, mode="r", *a, **kw):
        SWEEP.record(file, mode, "open")
        return orig_open(file, mode, *a, **kw)

    def wrapped_io_open(file, mode="r", *a, **kw):
        SWEEP.record(file, mode, "io.open")
        return orig_io_open(file, mode, *a, **kw)

    def wrapped_read_text(self, *a, **kw):
        SWEEP.record(self, "r", "Path.read_text")
        return orig_read_text(self, *a, **kw)

    def wrapped_read_bytes(self):
        SWEEP.record(self, "rb", "Path.read_bytes")
        return orig_read_bytes(self)

    def wrapped_np_load(file, *a, **kw):
        SWEEP.record(file, "rb", "np.load")
        return orig_np_load(file, *a, **kw)

    builtins.open = wrapped_open
    io.open = wrapped_io_open
    pathlib.Path.read_text = wrapped_read_text
    pathlib.Path.read_bytes = wrapped_read_bytes
    np.load = wrapped_np_load

    def restore():
        builtins.open = orig_open
        io.open = orig_io_open
        pathlib.Path.read_text = orig_read_text
        pathlib.Path.read_bytes = orig_read_bytes
        np.load = orig_np_load

    return restore


SHA_PIN_AT_LOAD = {str(b5.CHECKPOINTS_PATH_5), str(b5.SLICE_PATH_5),
                   str(bg.EXP2D / "results" / "verdict.json"),
                   str(EXP5B / "referents_5b.json"),
                   str(b5b.EXP5 / "results" / "verdict.json")}


def _classify(paths: set, referents_files: set) -> dict:
    manifest = {str(REPO / rel) for rel in referents_files}
    pinned = {str(p) for p in (b5b.FROZEN_SHA256_5B or {})}
    pinned |= {str(p) for p in (b5b.IMPORTED_SHA256_5B or {})}
    instrument = {str((REPO / rel).resolve()) for rel in b5b.INSTRUMENT_BLOBS_5B}
    stdlib_dirs = tuple(str(Path(d).resolve()) + "/" for d in sysconfig.get_paths().values() if d)
    venv_prefix = str(Path(sys.prefix).resolve()) + "/"
    base_prefix = str(Path(sys.base_prefix).resolve()) + "/"

    buckets = {"referents_5b.json": [], "pinned_module": [], "instrument_blob": [],
              "python_stdlib_venv": [], "sha_pin_at_load": [], "UNPINNED": []}
    for p in sorted(paths):
        rp = str(Path(p).resolve())
        if rp in SHA_PIN_AT_LOAD:
            buckets["sha_pin_at_load"].append(rp)
        elif rp in manifest:
            buckets["referents_5b.json"].append(rp)
        elif rp in instrument:
            buckets["instrument_blob"].append(rp)
        elif rp in pinned:
            buckets["pinned_module"].append(rp)
        elif rp.startswith(venv_prefix) or any(rp.startswith(d) for d in stdlib_dirs) \
                or "/site-packages/" in rp or rp.startswith(base_prefix):
            buckets["python_stdlib_venv"].append(rp)
        else:
            buckets["UNPINNED"].append(rp)
    return buckets


def main() -> int:
    referents_path = EXP5B / "referents_5b.json"
    referents_rel = set(json.loads(referents_path.read_text())["files"]) \
        if referents_path.is_file() else set()

    def blob_sha(tag, rel):
        p = REPO / rel
        return bg.sha256_file(p) if p.is_file() else None

    restore = _install()
    try:
        # `frozen_check`/`referents_sha`/`imports_pinned` are all left at
        # their PRODUCTION defaults (real checks against the real
        # committed tree) — only the prereg tag and the exp5-closed
        # binding's tag/blob callables are stubbed, since 5b's own
        # `exp5b-preregistered` tag does not exist yet pre-tag (the real
        # `exp5-closed` tag DOES exist, but is checked through the same
        # stubbed callables for a deterministic, network-free sweep).
        v = an.run(root=b5b.EXP5B, tag_exists=lambda t: True, blob_sha=blob_sha,
                  exp5_kwargs=dict(tag_exists=lambda t: True, blob_sha=blob_sha,
                                   blobs_bound=lambda t, p, **k: []),
                  n_sample=10, n_boot=10)
    finally:
        restore()

    print(f"pre-campaign run (NOT the experiment's verdict): {v['verdict']} — "
         f"{(v['failures'] or [''])[0][:200]}")

    distinct_reads = {p for p, _src in SWEEP.reads}
    buckets = _classify(distinct_reads, referents_rel)

    print(f"\n{len(distinct_reads)} distinct paths opened for reading "
         f"({len(SWEEP.reads)} total open/read calls)")
    print(f"  writes observed (should be 0, run() called with write=False by default): "
         f"{len(SWEEP.writes)}")
    for w in SWEEP.writes[:10]:
        print("   - WRITE", w)
    print()
    print(f"{'category':<24}{'count':>8}")
    for k, v_ in buckets.items():
        print(f"{k:<24}{len(v_):>8}")
    if buckets["UNPINNED"]:
        print("\nUNPINNED VERDICT INPUTS (must be empty):")
        for p in buckets["UNPINNED"]:
            print("  -", p)
        return 1
    print("\n(e) unpinned verdict input: 0 — clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
