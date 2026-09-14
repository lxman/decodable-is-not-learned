# experiments/exp4/tests/read_sweep_4.py
"""Read-sweep: every path opened for READING during one `analyze_4.run
(n_boot=10)` call on the REAL pre-campaign tree (nothing under
`experiments/exp4/results/`), classified as (a) on `referents_4.json`'s
manifest, (b) a `FROZEN_SHA256_4` / `battery_2g.FROZEN_IMPORT_SHA256_2G`
/ `IMPORTED_SHA256_4` module, (c) an `INSTRUMENT_BLOBS_4` file, (d)
python/stdlib/venv/site-packages, (e) unpinned verdict input — must be
empty, (f) a `REFERENCE_SEAL_TAG_4`-bound campaign artifact (the 849
`reference_seal_paths_4` paths — absent before the reference stage
ran, read for real from the stage tables on), or (g) sha-pinned at load: the
four upstream checkpoint manifests (`checkpoints_2g.json` via
`analyze_2g.CHECKPOINTS_SHA256`, `checkpoints_2i.json` via
`battery_2i.CHECKPOINTS_2I_SHA256`, `checkpoints_2m.json` via
`battery_2m.CHECKPOINTS_2M_SHA256`, `checkpoints_2n.json` via
`battery_2n.CHECKPOINTS_2N_SHA256`) plus `hub_inventory_pythia_4.json`
(its three scanned commits cross-checked against `PYTHIA_COMMITS_4` at
import time).

`analyze_4.run()` lands INSUFFICIENT_DATA on the real tree at "4
prereg tag" first (`exp4-preregistered` does not exist) UNLESS
`tag_exists`/`blob_sha` stand-ins are supplied (2j's/2k's/2n's
precedent) -- this sweep supplies them so the run reaches as far as
the tree allows: through the frozen/import/referent/manifest/outcome
checks, then refuses at "4 reference seal" (`exp4-reference-sealed`
does not exist and the 849 sealed paths are absent) before any stage-
table load is attempted. That verdict is NOT the experiment's verdict
and must never be written under `results/`; this script only prints
the read table.

The sweep covers `open`/`io.open`/`Path.read_text`/`read_bytes` — the
DATA surface. It does NOT cover the IMPORT surface (closed separately
by `analyze_4.check_imports_4`, `import_scan_4.py`) — this script
pre-imports everything so import traffic stays out of the table.

Run: `PYTHONDONTWRITEBYTECODE=1 ~/emergence-lab/.venv/bin/python -m
experiments.exp4.tests.read_sweep_4` from the repo root. Re-run once
`exp4-preregistered`/`exp4-reference-sealed` exist and the reference
stage has run — (e) must still be empty, and (f) should then start
resolving for real."""
from __future__ import annotations

import builtins
import io
import json
import pathlib
import sys
import sysconfig
from pathlib import Path

EXP4 = Path(__file__).resolve().parents[1]
if str(EXP4.parent.parent) not in sys.path:
    sys.path.insert(0, str(EXP4.parent.parent))

# Pre-import every module analyze_4.run() touches BEFORE the wrappers
# go on, so Python's own import machinery (which also calls open())
# never pollutes the sweep.
from experiments.exp2d import analyze_2d as a2d  # noqa: E402,F401
from experiments.exp2d import battery_2d as bt  # noqa: E402,F401
from experiments.exp2d import stats_2d as st2d  # noqa: E402,F401
from experiments.exp2g import analyze_2g as an2g  # noqa: E402,F401
from experiments.exp2g import battery_2g as bg  # noqa: E402,F401
from experiments.exp2g import checkpoints_2g as ck  # noqa: E402,F401
from experiments.exp2g import predictor_2g as pr  # noqa: E402,F401
from experiments.exp2g import stats_2g as sg2  # noqa: E402,F401
from experiments.exp2g import strata_2g as sg  # noqa: E402,F401
from experiments.exp2h import battery_2h as bh  # noqa: E402,F401
from experiments.exp2i import analyze_2i as an2i  # noqa: E402,F401
from experiments.exp2i import battery_2i as bi  # noqa: E402,F401
from experiments.exp2m import battery_2m as bm  # noqa: E402,F401
from experiments.exp2n import battery_2n as bn  # noqa: E402,F401
from experiments.exp4 import analyze_4 as an  # noqa: E402
from experiments.exp4 import battery_4  # noqa: E402,F401
from experiments.exp4 import collect_4  # noqa: E402,F401
from experiments.exp4 import make_referents_4 as mkr  # noqa: E402
from experiments.exp4 import metric_4  # noqa: E402,F401


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


SHA_PIN_AT_LOAD = {str(bg.CHECKPOINTS_PATH), str(bi.CHECKPOINTS_PATH), str(bm.CHECKPOINTS_PATH),
                  str(bn.CHECKPOINTS_PATH), str(battery_4.HUB_INVENTORY_PYTHIA_PATH)}

# `reference_seal_paths_4` returns paths RELATIVE to its root (run()'s
# own caller rejoins them); bucketing the sweep's ABSOLUTE reads against
# relative strings matched nothing. Invisible before the reference stage
# ran — the run refused at the seal and never opened a campaign file —
# and every one of them would have landed in (e) UNPINNED afterwards.
# Stale premise in a cold tool, fixed at campaign stop #1's closure.
SEAL_BOUND_CAMPAIGN_PATHS = {str((battery_4.EXP4 / p).resolve())
                            for p in battery_4.reference_seal_paths_4(battery_4.EXP4)}


def _classify(paths: set, referents_files: set, *, root=None) -> dict:
    """FREEZE, attack item 19: with `root` given (a synthetic POST-SEAL
    world), every path under `<root>/results/` is a campaign artifact —
    on the real tree those are the seal-bound files of bucket (f). They
    are bucketed as such here so that (e) UNPINNED answers the question
    the pre-campaign sweep structurally cannot: once the run gets PAST
    the reference seal, does it open any non-campaign file that no pin
    covers? (The secondaries' reads — 2d's and 2e's verdicts, 2d's
    argmax records, 2c's m4 files, 2g's predictor/strata — happen only
    on that side of the refusal.)"""
    world_prefix = (str((Path(root) / "results").resolve()) + "/") if root is not None else None
    frozen = {str(p) for p in battery_4.FROZEN_SHA256_4}
    frozen |= {str(p) for p in bg.FROZEN_IMPORT_SHA256_2G}
    frozen |= {str(p) for p in an.IMPORTED_SHA256_4} if an.IMPORTED_SHA256_4 else set()
    instrument = {str(bg.REPO / rel) for rel in battery_4.INSTRUMENT_BLOBS_4}
    manifest = {str(bg.REPO / rel) for rel in referents_files}
    manifest.add(str(an.REFERENTS_PATH_4))
    stdlib_dirs = tuple(str(Path(d).resolve()) + "/" for d in sysconfig.get_paths().values() if d)
    venv_prefix = str(Path(sys.prefix).resolve()) + "/"
    base_prefix = str(Path(sys.base_prefix).resolve()) + "/"
    KNOWN_NONEXISTENT_PROBES = {"/proc/self/maps"}

    buckets = {"referents_4.json": [], "frozen_module": [], "instrument_blob": [],
              "sha_pin_at_load": [], "seal_bound_campaign_absent": [],
              "world_campaign_artifact": [],
              "python_stdlib_venv": [], "UNPINNED": []}
    for p in sorted(paths):
        if world_prefix is not None and str(Path(p).resolve()).startswith(world_prefix):
            buckets["world_campaign_artifact"].append(str(Path(p).resolve()))
            continue
        if str(Path(p).resolve()) in SEAL_BOUND_CAMPAIGN_PATHS:
            buckets["seal_bound_campaign_absent"].append(p)
            continue
        rp = str(Path(p).resolve()) if p not in KNOWN_NONEXISTENT_PROBES else p
        # The four upstream manifests + hub_inventory_pythia_4.json are
        # BOTH in referents_4.json (disclosure/completeness, per the
        # referent-manifest brief) AND individually sha-pinned at load
        # by their own frozen readers -- bucket (g) is checked FIRST so
        # these five files land there specifically, matching the read-
        # sweep brief's explicit "(g) = the four manifests at their
        # pins + hub_inventory_pythia_4.json".
        if rp in SHA_PIN_AT_LOAD:
            buckets["sha_pin_at_load"].append(rp)
        elif rp in manifest:
            buckets["referents_4.json"].append(rp)
        elif rp in frozen:
            buckets["frozen_module"].append(rp)
        elif rp in instrument:
            buckets["instrument_blob"].append(rp)
        elif p in KNOWN_NONEXISTENT_PROBES or rp.startswith(venv_prefix) \
                or any(rp.startswith(d) for d in stdlib_dirs) \
                or "/site-packages/" in rp or rp.startswith(base_prefix):
            buckets["python_stdlib_venv"].append(rp)
        else:
            buckets["UNPINNED"].append(rp)
    return buckets


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    world_root = None
    for a in argv:
        if a.startswith("--root="):
            world_root = Path(a[len("--root="):]).resolve()
    referents_rel = set(json.loads(an.REFERENTS_PATH_4.read_text())["files"])
    live_rel = {str(Path(p).resolve().relative_to(bg.REPO.resolve())) for p in mkr.referent_files()}
    if live_rel != referents_rel:
        print(f"NOTE: referent_files() lists {len(live_rel)} files, the committed manifest "
             f"{len(referents_rel)}; only-live={sorted(live_rel - referents_rel)[:5]}, "
             f"only-manifest={sorted(referents_rel - live_rel)[:5]}")

    def blob_sha(tag, rel):
        p = bg.REPO / rel
        return bg.sha256_file(p) if p.is_file() else None

    run_kw = dict(n_boot=10, write=False, tag_exists=lambda t: True, blob_sha=blob_sha)
    if world_root is not None:
        # A synthetic world's campaign artifacts are not in git, so the
        # seal's blob binding cannot apply; its power record is written
        # at the world's own n_sim. Everything else — the frozen pins,
        # the import surface, the referent manifest — stays REAL.
        from experiments.exp4.tests import full_shape as fs
        run_kw.update(blobs_bound=lambda tag, paths, repo_root=None: [],
                      expected_n_sim=fs.WORLD_POWER_N_SIM_4)
    restore = _install()
    try:
        v = an.run(root=(world_root or battery_4.EXP4), **run_kw)
    finally:
        restore()

    print(f"verdict (n_boot=10, NOT the experiment's verdict): {v['verdict']} — {v['reason'][:200]}")
    if v["referents"]["failures"]:
        print(f"  ({len(v['referents']['failures'])} referent failure(s) — see below)")
        for f in v["referents"]["failures"][:10]:
            print("   -", f)

    distinct_reads = {p for p, _src in SWEEP.reads}
    buckets = _classify(distinct_reads, referents_rel, root=world_root)
    if world_root is not None:
        print(f"POST-SEAL sweep against the synthetic world {world_root}")

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
    print(f"(f) seal-bound campaign artifact (absent pre-campaign, read from the "
         f"reference stage on): {len(buckets['seal_bound_campaign_absent'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
