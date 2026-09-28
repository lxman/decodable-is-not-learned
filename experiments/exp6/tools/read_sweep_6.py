# experiments/exp6/tools/read_sweep_6.py
"""The read sweep: every file the analyzer OPENS, classified by what
binds it. A file nothing binds is a verdict input nobody pinned (3a's
class defect, found again in 3c, 3d and 2i).

The analyzer runs with `open`, `gzip.open` and `Path.read_*` recording
every path; each path is then one of
  (a) bound by the preregistration tag (the instrument, the item files);
  (b) a pinned module or a pinned item/data file of the battery;
  (c) named in the referent manifest, whose own sha is a literal;
  (d) bound by the predictor seal's file table;
  (e) bound by the endpoint seal (the rung sets' file table, the rung
      sets, the power record);
  (f) a sweep artifact: measured against its load record, the seals'
      shas it carries and, through gate 1, against the sealed endpoint;
  (g) the manifest, the seal or the gate record ITSELF (each is checked
      against a literal, a tag or a re-derivation);
and anything else is UNPINNED. UNPINNED must be zero.

A sweep that runs the analyzer on a COMPLETE tree prints no statistic:
it reports paths and classes only, and the analyzer's verdict is
discarded unread (2k's process note: a tool that computes a statistic
runs after the projection is sealed; this one does not print one).

    python -m experiments.exp6.tools.read_sweep_6 [root]
"""
from __future__ import annotations

import builtins
import gzip
import io
import json
import os
import sys
from pathlib import Path

EXP6 = Path(__file__).resolve().parents[1]
REPO = EXP6.parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))


def record_reads(thunk) -> list:
    """Run `thunk` and return every path it opened for reading."""
    seen = []
    real_open, real_gz = builtins.open, gzip.open
    real_io = io.open
    real_rb, real_rt = Path.read_bytes, Path.read_text

    def note(p, mode="r"):
        if isinstance(p, (str, bytes, os.PathLike)) and not any(c in str(mode)
                                                                for c in "wax+"):
            seen.append(os.path.abspath(os.fspath(p)))

    def _open(file, mode="r", *a, **k):
        note(file, mode)
        return real_open(file, mode, *a, **k)

    def _gz(filename, mode="rb", *a, **k):
        note(filename, mode)
        return real_gz(filename, mode, *a, **k)

    def _rb(self):
        note(self)
        return real_rb(self)

    def _rt(self, *a, **k):
        note(self)
        return real_rt(self, *a, **k)
    builtins.open, io.open, gzip.open = _open, _open, _gz
    Path.read_bytes, Path.read_text = _rb, _rt
    try:
        thunk()
    finally:
        builtins.open, io.open, gzip.open = real_open, real_io, real_gz
        Path.read_bytes, Path.read_text = real_rb, real_rt
    return sorted(set(seen))


def classify(paths, root) -> dict:
    from experiments.exp6 import battery_6 as b6
    from experiments.exp6 import pins_6 as p6
    from experiments.exp6 import records_6 as r6
    from experiments.exp6 import referents_6 as rf
    from experiments.exp6 import make_referents_6 as mkr
    from experiments.exp6.run import _common_6 as cm
    root = Path(root).resolve()
    repo = b6.REPO

    # an experiment directory reached through a link is still that
    # experiment: a frozen loader resolves its own path before it opens
    linked = {c.resolve(): Path("experiments") / c.name
              for c in (Path(repo) / "experiments").iterdir() if c.is_symlink()}

    def rel(p, base):
        for q in (Path(p), Path(p).resolve()):
            for b in (Path(base), Path(base).resolve()):
                try:
                    return str(q.relative_to(b))
                except ValueError:
                    continue
        if Path(base) == Path(repo):
            for target, name in linked.items():
                try:
                    return str(name / Path(p).resolve().relative_to(target))
                except ValueError:
                    continue
        return None
    bound = set(p6.INSTRUMENT_BLOBS_6) | set(p6.ITEM_BLOBS_6)
    pinned = set(p6.FROZEN_SHA256_6 or {}) | set(p6.IMPORTED_SHA256_6 or {})
    battery_data = {"experiments/exp6/battery/data/bbkey_audit_6.json",
                    "experiments/exp6/battery/data/bbkey_known_6.json",
                    "experiments/exp6/battery/data/bigbench_index_6.json",
                    "experiments/exp6/battery/data/words_6.tsv",
                    "experiments/exp6/battery/token_lengths_6.json"}
    referents = {rel(p, repo) for p in rf.referent_files()}
    seal, sealed_e = {}, set()
    try:
        seal = r6.read_json(r6.seal_path(root)).get("files") or {}
    except Exception:  # noqa: BLE001 — an absent stage is an empty class
        pass
    try:
        sealed_e = set(r6.read_json(r6.rung_sets_path(root)).get("sealed_files") or [])
    except Exception:  # noqa: BLE001
        pass
    itself = {str(mkr.PATH.resolve()), str(r6.seal_path(root).resolve()),
              str(r6.gate1p_path(root).resolve())}
    out = {k: [] for k in "abcdefg"}
    out["UNPINNED"], out["outside"] = [], []
    for p in paths:
        r_repo, r_root = rel(p, repo), rel(p, root)
        if str(Path(p).resolve()) in itself:
            out["g"].append(p)
        elif r_root is not None and r_root in seal:
            out["d"].append(p)
        elif r_root is not None and (r_root in sealed_e or Path(p).resolve() in (
                r6.rung_sets_path(root).resolve(), r6.power_path(root).resolve())):
            out["e"].append(p)
        elif r_root is not None and (
                r_root.startswith("results/sweep/")
                or (r_root.startswith("results/hosts/") and r_root not in sealed_e)):
            out["f"].append(p)
        elif r_repo in bound:
            out["a"].append(p)
        elif r_repo in pinned or r_repo in battery_data:
            out["b"].append(p)
        elif r_repo in referents:
            out["c"].append(p)
        elif r_repo is None and r_root is None:
            out["outside"].append(p)        # the interpreter's own: site-packages
        else:
            out["UNPINNED"].append(p)
    return out


def sweep(root, **inject) -> dict:
    """The analyzer's READS. Its import check is switched off here: this
    process has loaded the sweep itself and whatever called it, which
    are on its import surface and in no pin, and the check would hash
    them. The import surface is the import scan's to measure, in a fresh
    interpreter; the verdict of this run is discarded unread."""
    from experiments.exp6 import analyze_6 as an
    inject.setdefault("imports_pinned", False)
    paths = record_reads(lambda: an.run(root, n_perm=20, n_boot=5, **inject))
    cls = classify(paths, root)
    outside = [p for p in cls["outside"] if "site-packages" not in p
               and "/lib/python" not in p and not p.endswith((".pyc", ".so"))]
    return {"n_reads": len(paths), "classes": {k: len(v) for k, v in cls.items()},
            "UNPINNED": cls["UNPINNED"], "outside_unexplained": outside}


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    root = Path(argv[0]) if argv else EXP6
    out = sweep(root)
    print(json.dumps(out, indent=1))
    return 1 if (out["UNPINNED"] or out["outside_unexplained"]) else 0


if __name__ == "__main__":
    raise SystemExit(main())
