# experiments/exp4c/tests/read_sweep_4c.py
"""Read-sweep: every path opened for READING during one `analyze_4c.
run(root=battery_4c.EXP4C, root4=battery_4.EXP4, n_boot=10, B=10)` call
on the REAL, pre-campaign exp4c tree (2n's/4b's shape). No exp4c
campaign data exists yet beyond the committed `power_4c.json` and the
design session's `series_known4.json`, so `run()` reaches the
DISCOVERY GATE (design §3.7(1) — it re-derives U on Exp 4's committed,
closed 92-unit sweep tree, printing the known U .6224, a DISCLOSURE
event, counted in `experiments-4c-design.md` §2's running tally), then
the power record's byte reproduction, then refuses at "4c gate 1
pythia_6.9b: record missing" — the first thing the per-trajectory loop
needs that a pre-campaign tree does not have.

Classifies every distinct read path into one of:
  (a) referents_4c.json's own manifest
  (b) a pinned module (`battery_4.FROZEN_SHA256_4` / `battery_4c.
      FROZEN_SHA256_4C` / `EXP4_CLOSED_SHA256_4C` / `EXP4B_CLOSED_
      SHA256_4C` / `analyze_4c.IMPORTED_SHA256_4C`)
  (c) an `INSTRUMENT_BLOBS_4C` file (exp4c's own tag-bound instrument,
      incl. `results/power_4c.json`)
  (d) python/stdlib/venv/site-packages
  (e) UNPINNED verdict input — must be 0
  (f) an Exp 4 campaign artifact under `battery_4.EXP4` not already
      classified above — the discovery gate's own inputs (the 92 sweep
      units' `_load.json`/`sets/*.npz`/`align.json`, the five reference
      keys, `eligibility_4.json`, `power_4.json`) all land here
  (g) sha-pinned at load — the 2h/2l upstream checkpoint manifests,
      read through `load_manifest_69`/`load_manifest_13b`'s own
      `sha_pin=` argument rather than this module's classifier

The sweep covers `open`/`io.open`/`Path.read_text`/`read_bytes` — the
DATA surface, not the IMPORT surface (closed separately by
`analyze_4c.check_imports_4c`, `import_scan_4c.py`) — this script
pre-imports everything so import traffic stays out of the table.

Run: `PYTHONDONTWRITEBYTECODE=1 ~/emergence-lab/.venv/bin/python -m
experiments.exp4c.tests.read_sweep_4c` from the repo root."""
from __future__ import annotations

import builtins
import io
import json
import pathlib
import sys
import sysconfig
from pathlib import Path

EXP4C = Path(__file__).resolve().parents[1]
REPO = EXP4C.parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

# Pre-import every module analyze_4c.run() touches BEFORE the wrappers
# go on, so Python's own import machinery never pollutes the sweep.
from experiments.exp2d import battery_2d as bt  # noqa: E402,F401
from experiments.exp2g import battery_2g as bg  # noqa: E402,F401
from experiments.exp2g import predictor_2g as pr  # noqa: E402,F401
from experiments.exp2h import battery_2h as bh  # noqa: E402,F401
from experiments.exp2i import analyze_2i as an2i  # noqa: E402,F401
from experiments.exp2l import battery_2l as bl  # noqa: E402,F401
from experiments.exp4 import analyze_4 as a4  # noqa: E402,F401
from experiments.exp4 import battery_4  # noqa: E402
from experiments.exp4 import collect_4  # noqa: E402,F401
from experiments.exp4 import metric_4  # noqa: E402,F401
from experiments.exp4b import placebo_4b  # noqa: E402,F401
from experiments.exp4c import analyze_4c as an  # noqa: E402
from experiments.exp4c import battery_4c as bc  # noqa: E402
from experiments.exp4c import make_referents_4c as mkr  # noqa: E402
from experiments.exp4c import power_4c as pw4c  # noqa: E402,F401
from experiments.exp4c import rank_4c as rk  # noqa: E402,F401


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
    orig_open = builtins.open
    orig_io_open = io.open
    orig_read_text = pathlib.Path.read_text
    orig_read_bytes = pathlib.Path.read_bytes

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

    builtins.open = wrapped_open
    io.open = wrapped_io_open
    pathlib.Path.read_text = wrapped_read_text
    pathlib.Path.read_bytes = wrapped_read_bytes

    def restore():
        builtins.open = orig_open
        io.open = orig_io_open
        pathlib.Path.read_text = orig_read_text
        pathlib.Path.read_bytes = orig_read_bytes

    return restore


SHA_PIN_AT_LOAD = {str(bh.CHECKPOINTS_PATH_69), str(bl.CHECKPOINTS_PATH)}


def _classify(paths: set, referents_files: set) -> dict:
    manifest = {str(REPO / rel) for rel in referents_files}
    pinned = {str(p) for p in battery_4.FROZEN_SHA256_4}
    pinned |= {str(p) for p in (bc.FROZEN_SHA256_4C or {})}
    for table in (bc.EXP4_CLOSED_SHA256_4C, bc.EXP4B_CLOSED_SHA256_4C):
        pinned |= {str((REPO / rel).resolve()) for rel in table}
    pinned |= {str(Path(p).resolve()) for p in (an.IMPORTED_SHA256_4C or {})}
    instrument = {str((REPO / rel).resolve()) for rel in bc.INSTRUMENT_BLOBS_4C}
    stdlib_dirs = tuple(str(Path(d).resolve()) + "/" for d in sysconfig.get_paths().values() if d)
    venv_prefix = str(Path(sys.prefix).resolve()) + "/"
    base_prefix = str(Path(sys.base_prefix).resolve()) + "/"
    exp4_root_prefix = str(battery_4.EXP4.resolve()) + "/"

    exp4c_results_prefix = str((bc.EXP4C / "results").resolve()) + "/"

    buckets = {"referents_4c.json": [], "pinned_module": [], "instrument_blob": [],
              "python_stdlib_venv": [], "sha_pin_at_load": [],
              "exp4_campaign_artifact": [], "exp4c_own_future_campaign_artifact": [],
              "UNPINNED": []}
    for p in sorted(paths):
        rp = str(Path(p).resolve())
        if rp in SHA_PIN_AT_LOAD:
            buckets["sha_pin_at_load"].append(rp)
        elif rp in manifest:
            buckets["referents_4c.json"].append(rp)
        elif rp in instrument:
            buckets["instrument_blob"].append(rp)
        elif rp in pinned:
            buckets["pinned_module"].append(rp)
        elif rp.startswith(venv_prefix) or any(rp.startswith(d) for d in stdlib_dirs) \
                or "/site-packages/" in rp or rp.startswith(base_prefix):
            buckets["python_stdlib_venv"].append(rp)
        elif rp.startswith(exp4_root_prefix):
            buckets["exp4_campaign_artifact"].append(rp)
        elif rp.startswith(exp4c_results_prefix):
            # 4c's OWN future campaign artifacts (gate 1's byte
            # rederivation attempts to read the sweep endpoint's own
            # sets/*.npz and the 13B thin endpoint's, which do not
            # exist pre-campaign — the FileNotFoundError is caught and
            # collected as a failure, but `_install()`'s wrapper
            # records the attempted path before the underlying `open`
            # call raises).
            buckets["exp4c_own_future_campaign_artifact"].append(rp)
        else:
            buckets["UNPINNED"].append(rp)
    return buckets


def main() -> int:
    referents_path = bc.EXP4C / "referents_4c.json"
    referents_rel = set(json.loads(referents_path.read_text())["files"]) \
        if referents_path.is_file() else set()

    def blob_sha(tag, rel):
        p = REPO / rel
        return bg.sha256_file(p) if p.is_file() else None

    restore = _install()
    try:
        # `frozen_check` stubbed for the same build-stage reason
        # `import_scan_4c.py` stubs it: this sweep can run BEFORE
        # `FROZEN_SHA256_4C` is pinned.
        v = an.run(root=bc.EXP4C, root4=battery_4.EXP4, frozen_check=lambda: None,
                  referents_sha=False, imports_pinned=False, tag_exists=lambda t: True,
                  blob_sha=blob_sha, n_boot=10, B=10)
    finally:
        restore()

    print(f"pre-campaign run (NOT the experiment's verdict): {v['verdict']} — "
         f"{(v['reason'] or '')[:200]}")

    distinct_reads = {p for p, _src in SWEEP.reads}
    buckets = _classify(distinct_reads, referents_rel)

    print(f"\n{len(distinct_reads)} distinct paths opened for reading "
         f"({len(SWEEP.reads)} total open/read calls)")
    print(f"  writes observed (should be 0, run() called with write=False by default): "
         f"{len(SWEEP.writes)}")
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
    return 0


if __name__ == "__main__":
    sys.exit(main())
