# experiments/exp5/tests/read_sweep_5.py
"""Read-sweep: every path opened for READING during one `analyze_5.run(
root=battery_5.EXP5, n_sample=10, n_boot=10)` call on the REAL,
pre-campaign exp5 tree (exp4c's/2n's own shape). No exp5 campaign data
exists yet, so `run()` proceeds through the referents/battery/floors/
verify loads and refuses early, at `"5 host record"` (no `results/
host_5.json` on the real tree) — see `import_scan_5.py`'s docstring for
the exact refusal text and the pre-tag disclosure count.

Classifies every distinct read path into:
  (a) `referents_5.json`'s own manifest (the ≈1,786 committed files it lists)
  (b) a pinned module (`battery_5.FROZEN_SHA256_5` / `battery_5.
      IMPORTED_SHA256_5`)
  (c) an `INSTRUMENT_BLOBS_5` file (exp5's own tag-bound instrument)
  (d) python/stdlib/venv/site-packages
  (e) UNPINNED verdict input — must be 0
  (f) sha-pinned AT LOAD, independent of (a)/(c): `checkpoints_5.json`
      (`battery_5.load_manifest_5`'s own `sha_pin=`), `slice_5.npz`
      (`slice_5.load_slice_5`'s own `sha_pin=`), 2d's `results/
      verdict.json` (`battery_2g.load_floors`'s own `sha_pin=`, read
      through `battery_5.load_floors_5`), and `referents_5.json`
      itself (`make_referents_5.check_referents_5`'s own `sha_pin=` —
      a fourth item beyond the brief's literal three, disclosed: its
      bytes are ALSO sha-pinned, by `analyze_5.REFERENTS_5_SHA256`,
      the same mechanism as the other three, so it belongs in this
      bucket rather than (a), which is about files referents_5.json
      itself LISTS)

The sweep covers `open`/`io.open`/`Path.read_text`/`read_bytes`/
`numpy.load` — the DATA surface, not the IMPORT surface (closed
separately by `battery_5.check_imports_5`, `import_scan_5.py`) — this
script pre-imports everything so import traffic stays out of the
table.

Run: `PYTHONDONTWRITEBYTECODE=1 ~/emergence-lab/.venv/bin/python -m
experiments.exp5.tests.read_sweep_5` from the repo root."""
from __future__ import annotations

import builtins
import io
import json
import pathlib
import sys
import sysconfig
from pathlib import Path

EXP5 = Path(__file__).resolve().parents[1]
REPO = EXP5.parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

# Pre-import every module analyze_5.run() (and the stage tools) touch
# BEFORE the wrappers go on, so Python's own import machinery never
# pollutes the sweep.
from experiments.exp2d import analyze_2d as a2d  # noqa: E402,F401
from experiments.exp2d import battery_2d as bt  # noqa: E402,F401
from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp2g import predictor_2g as pr  # noqa: E402,F401
from experiments.exp2h import battery_2h as bh  # noqa: E402,F401
from experiments.exp2i import analyze_2i as an2i  # noqa: E402,F401
from experiments.exp5 import analyze_5 as an  # noqa: E402
from experiments.exp5 import battery_5 as b5  # noqa: E402
from experiments.exp5 import make_referents_5 as mkr  # noqa: E402,F401
from experiments.exp5 import power_5 as pw  # noqa: E402,F401
from experiments.exp5 import search_5 as se5  # noqa: E402,F401
from experiments.exp5 import slice_5 as sl5  # noqa: E402,F401


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
                   str(EXP5 / "referents_5.json")}


def _classify(paths: set, referents_files: set) -> dict:
    manifest = {str(REPO / rel) for rel in referents_files}
    pinned = {str(p) for p in (b5.FROZEN_SHA256_5 or {})}
    pinned |= {str(p) for p in (b5.IMPORTED_SHA256_5 or {})}
    instrument = {str((REPO / rel).resolve()) for rel in b5.INSTRUMENT_BLOBS_5}
    stdlib_dirs = tuple(str(Path(d).resolve()) + "/" for d in sysconfig.get_paths().values() if d)
    venv_prefix = str(Path(sys.prefix).resolve()) + "/"
    base_prefix = str(Path(sys.base_prefix).resolve()) + "/"

    buckets = {"referents_5.json": [], "pinned_module": [], "instrument_blob": [],
              "python_stdlib_venv": [], "sha_pin_at_load": [], "UNPINNED": []}
    for p in sorted(paths):
        rp = str(Path(p).resolve())
        if rp in SHA_PIN_AT_LOAD:
            buckets["sha_pin_at_load"].append(rp)
        elif rp in manifest:
            buckets["referents_5.json"].append(rp)
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
    referents_path = EXP5 / "referents_5.json"
    referents_rel = set(json.loads(referents_path.read_text())["files"]) \
        if referents_path.is_file() else set()

    def blob_sha(tag, rel):
        p = REPO / rel
        return bg.sha256_file(p) if p.is_file() else None

    restore = _install()
    try:
        # `frozen_check`/`referents_sha`/`imports_pinned` are all left
        # at their PRODUCTION defaults (real checks against the real
        # committed tree, independent of the tag) — only the prereg
        # tag and the targets seal are stubbed, since neither exists
        # yet pre-tag.
        v = an.run(root=b5.EXP5, tag_exists=lambda t: True, blob_sha=blob_sha,
                  blobs_bound=lambda t, p, **k: [], n_sample=10, n_boot=10)
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
