# experiments/exp4b/tests/read_sweep_4b.py
"""Read-sweep: every path opened for READING during one `analyze_4b.
run(root4b=<tmp>, root4=battery_4.EXP4, stop_before="placebo", B=10,
n_sim_ext=2)` call on the REAL, closed exp4 tree (design §2's B-4 rule:
no placebo quantity is ever computed against the real tree -- the run
stops before `placebo_4b.draw_batteries_4b` is ever called), classified
(a) on `referents_4b.json`'s manifest, (b) a `FROZEN_SHA256_4` /
`battery_2g.FROZEN_IMPORT_SHA256_2G` / `analyze_4.IMPORTED_SHA256_4`
module (exp4's own transitively-frozen surface, outside `experiments/
exp4/` itself), (c) an `INSTRUMENT_BLOBS_4B` file (exp4b's own
instrument), (d) python/stdlib/venv/site-packages, (e) UNPINNED verdict
input -- must be 0, (f) an exp4 campaign artifact NOT in exp4b's own
`referents_4b.json` manifest -- should be 0 (that manifest is built
from the closed, complete tree, so it already covers everything a
post-close analyzer run touches; unlike exp4's own read sweep, which
ran PRE-campaign and had a whole bucket of seal-bound paths that did
not exist yet), (g) sha-pinned at load (the upstream checkpoint
manifests exp4's OWN loaders would pin -- structurally kept for parity
with exp4's own sweep; exp4b's analyzer never loads a checkpoint or a
Hub inventory, so this bucket is expected to be empty), (h) an
`exp4-closed`-pinned exp4 module (`battery_4b.EXP4_CLOSED_SHA256_4B`
-- exp4's own seven files, re-pinned separately by exp4b since it
treats `experiments/exp4/` as its own special frozen dependency,
distinct from the "outside exp4" frozen set of bucket (b)).

A finding, not a defect: the first (f)-classified sweep found 136
`results/reference/<ref>/attested/<rung>.npz` reads (34 rungs x 4
references) -- `collect_4.load_ref_tables_4` (exp4's own frozen code,
`collect_4.py` line ~523) unconditionally attempts this read for every
rung when the file exists. `collect_4.py`'s own module docstring
already discloses these files as "sha-attested, gitignored" -- exp4's
OWN `referents_4.json` carries ZERO of them (verified directly), so
they were never part of exp4's committed-bytes reproducibility
contract either. `load_ref_tables_4` reads them UNCHECKED (no sha
comparison, unlike `sets`, which IS checked against `_load.json`'s
`sets_sha256`) into `sets_question_end`/`sets_pooled`, and every one
of exp4b's five call sites (`analyze_4b.run`'s two, `levels_4b.py`'s
three, `verify_referents_4b.py`'s one) immediately reduces the raw
dict to `{ref: rt["sets"] for ...}` or otherwise reads only `sets`/
`sites`/`n_hidden`/`record` -- `sets_question_end`/`sets_pooled` are
read from disk and then discarded, never touching a verdict quantity
(grepped exhaustively; see PROGRESS.md's Task 6 entry). Bucketed
separately as (i), not folded into (f): pinning a GITIGNORED file's
content would be incoherent (a fresh clone never has the file at all),
and the content is provably unused, so this bucket's count is a
disclosure, not a gap -- (f) itself is expected to be 0.

`analyze_4b.run(stop_before="placebo")` on the real tree reaches every
gate (1-5) and then returns the FIXED "stopped before the placebo
null" reason unconditionally -- that returned verdict is NOT the
experiment's verdict and is never written under `results/`; this
script only prints the read table (`write=False` throughout).

The sweep covers `open`/`io.open`/`Path.read_text`/`read_bytes` -- the
DATA surface. It does NOT cover the IMPORT surface (closed separately
by `analyze_4b.check_imports_4b`, `import_scan_4b.py`) -- this script
pre-imports everything so import traffic (module SOURCE reads driven
by Python's own import machinery, as opposed to this module's own
sha256-of-a-pinned-file reads) stays out of the table.

Run: `PYTHONDONTWRITEBYTECODE=1 ~/emergence-lab/.venv/bin/python -m
experiments.exp4b.tests.read_sweep_4b` from the repo root."""
from __future__ import annotations

import builtins
import io
import json
import pathlib
import sys
import sysconfig
import tempfile
from pathlib import Path

EXP4B = Path(__file__).resolve().parents[1]
REPO = EXP4B.parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

# Pre-import every module analyze_4b.run() touches BEFORE the wrappers
# go on, so Python's own import machinery never pollutes the sweep.
from experiments.exp2d import battery_2d as bt  # noqa: E402,F401
from experiments.exp2g import battery_2g as bg  # noqa: E402,F401
from experiments.exp2g import predictor_2g as pr  # noqa: E402,F401
from experiments.exp4 import analyze_4 as an  # noqa: E402
from experiments.exp4 import battery_4  # noqa: E402,F401
from experiments.exp4 import collect_4  # noqa: E402,F401
from experiments.exp4 import metric_4  # noqa: E402,F401
from experiments.exp4 import power_4 as pw4  # noqa: E402,F401
from experiments.exp4b import analyze_4b as an4b  # noqa: E402
from experiments.exp4b import battery_4b  # noqa: E402,F401
from experiments.exp4b import levels_4b  # noqa: E402,F401
from experiments.exp4b import make_referents_4b as mkr4b  # noqa: E402
from experiments.exp4b import placebo_4b  # noqa: E402,F401
from experiments.exp4b import power_ext_4b  # noqa: E402,F401


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


# Structural parity with exp4's own read_sweep_4.py's bucket (g) -- kept
# even though exp4b's analyzer never loads a checkpoint or Hub
# inventory, so this set is expected to contribute 0 reads here.
SHA_PIN_AT_LOAD = {str(battery_4.HUB_INVENTORY_PYTHIA_PATH)}


def _classify(paths: set, referents_files: set) -> dict:
    frozen = {str(p) for p in battery_4.FROZEN_SHA256_4}
    frozen |= {str(p) for p in bg.FROZEN_IMPORT_SHA256_2G}
    frozen |= {str(p) for p in (an.IMPORTED_SHA256_4 or {})}
    instrument = {str(battery_4b.REPO / rel) for rel in battery_4b.INSTRUMENT_BLOBS_4B}
    exp4_closed = {str(battery_4b.REPO / rel) for rel in battery_4b.EXP4_CLOSED_SHA256_4B}
    manifest = {str(battery_4b.REPO / rel) for rel in referents_files}
    manifest.add(str(an4b.REFERENTS_PATH_4B))
    stdlib_dirs = tuple(str(Path(d).resolve()) + "/" for d in sysconfig.get_paths().values() if d)
    venv_prefix = str(Path(sys.prefix).resolve()) + "/"
    base_prefix = str(Path(sys.base_prefix).resolve()) + "/"
    exp4_root_prefix = str(battery_4.EXP4.resolve()) + "/"

    buckets = {"referents_4b.json": [], "frozen_module": [], "instrument_blob": [],
              "exp4_closed_module": [], "sha_pin_at_load": [],
              "gitignored_attested_unused": [],
              "exp4_campaign_artifact_not_in_manifest": [],
              "python_stdlib_venv": [], "UNPINNED": []}
    for p in sorted(paths):
        rp = str(Path(p).resolve())
        if rp in SHA_PIN_AT_LOAD:
            buckets["sha_pin_at_load"].append(rp)
        elif rp in manifest:
            buckets["referents_4b.json"].append(rp)
        elif rp in exp4_closed:
            buckets["exp4_closed_module"].append(rp)
        elif rp in frozen:
            buckets["frozen_module"].append(rp)
        elif rp in instrument:
            buckets["instrument_blob"].append(rp)
        elif rp.startswith(venv_prefix) or any(rp.startswith(d) for d in stdlib_dirs) \
                or "/site-packages/" in rp or rp.startswith(base_prefix):
            buckets["python_stdlib_venv"].append(rp)
        elif "/reference/" in rp and rp.endswith(".npz") and "/attested/" in rp:
            # (i), disclosed above: `collect_4.load_ref_tables_4`
            # (exp4's own frozen code) unconditionally attempts this
            # read; the file is explicitly documented as "sha-attested,
            # gitignored" by collect_4.py's own module docstring, is
            # absent from exp4's OWN referents_4.json, is read with NO
            # sha check (unlike `sets`), and its content
            # (`sets_question_end`/`sets_pooled`) is discarded by every
            # one of exp4b's five call sites before any verdict
            # quantity is computed — grepped exhaustively, PROGRESS.md's
            # Task 6 entry carries the proof.
            buckets["gitignored_attested_unused"].append(rp)
        elif rp.startswith(exp4_root_prefix):
            # Anything ELSE under the real, closed exp4 tree not
            # already covered by referents_4b.json's manifest, the
            # exp4-closed pin, the frozen/instrument sets, or the
            # gitignored-attested finding above — should be empty
            # (bucket (f)'s own "should be 0").
            buckets["exp4_campaign_artifact_not_in_manifest"].append(rp)
        else:
            buckets["UNPINNED"].append(rp)
    return buckets


def main(argv=None) -> int:
    referents_rel = set(json.loads(an4b.REFERENTS_PATH_4B.read_text())["files"])
    live_rel = {str(Path(p).resolve().relative_to(bg.REPO.resolve()))
               for p in mkr4b.referent_files_4b()}
    if live_rel != referents_rel:
        print(f"NOTE: referent_files_4b() lists {len(live_rel)} files, the committed manifest "
             f"{len(referents_rel)}; only-live={sorted(live_rel - referents_rel)[:5]}, "
             f"only-manifest={sorted(referents_rel - live_rel)[:5]}")

    def blob_sha(tag, rel):
        p = battery_4b.REPO / rel
        return bg.sha256_file(p) if p.is_file() else None

    restore = _install()
    try:
        with tempfile.TemporaryDirectory() as tmp:
            run_kw = dict(root4b=Path(tmp) / "4b", root4=battery_4.EXP4, write=False,
                         stop_before="placebo", B=10, n_sim_ext=2, tag_exists=lambda t: True,
                         blob_sha=blob_sha, referents_sha=False, imports_pinned=False)
            v = an4b.run(**run_kw)
    finally:
        restore()

    print(f"verdict (stop_before='placebo', NOT the experiment's verdict): {v['verdict']} — "
         f"{v['reason'][:200]}")
    for n in ("1", "2", "3", "4", "5"):
        g = v["gates"].get(n) or {}
        print(f"  gate {n}: pass={g.get('pass')}")

    distinct_reads = {p for p, _src in SWEEP.reads}
    buckets = _classify(distinct_reads, referents_rel)

    print(f"\n{len(distinct_reads)} distinct paths opened for reading "
         f"({len(SWEEP.reads)} total open/read calls)")
    print(f"  writes observed (should be 0, write=False): {len(SWEEP.writes)}")
    for w in SWEEP.writes[:10]:
        print("   - WRITE", w)
    print()
    print(f"{'category':<40}{'count':>8}")
    for k, v_ in buckets.items():
        print(f"{k:<40}{len(v_):>8}")
    if buckets["UNPINNED"]:
        print("\nUNPINNED VERDICT INPUTS (must be empty):")
        for p in buckets["UNPINNED"]:
            print("  -", p)
        return 1
    print("\n(e) unpinned verdict input: 0 — clean")
    print(f"(f) exp4 campaign artifact not in exp4b's manifest: "
         f"{len(buckets['exp4_campaign_artifact_not_in_manifest'])} (should be 0)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
