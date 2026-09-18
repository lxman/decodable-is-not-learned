# experiments/exp4c/tests/import_scan_4c.py
"""One-shot import-surface scan for `FROZEN_SHA256_4C` (`battery_4c.
check_frozen_4c`'s pin — every module `experiments/exp4c` imports
transitively OUTSIDE `experiments/exp4c`, that is not already covered
by `battery_4.FROZEN_SHA256_4`, `battery_4c.EXP4_CLOSED_SHA256_4C` or
`battery_4c.EXP4B_CLOSED_SHA256_4C`) and `IMPORTED_SHA256_4C`
(`analyze_4c.check_imports_4c`'s residual pin — every non-test module
INSIDE `experiments/exp4c` that is not one of the seven blob-bound
`INSTRUMENT_BLOBS_4C` files; 2j's F-1 lineage, exp4's own
`import_scan_4.py`/exp4b's `import_scan_4b.py` one experiment over).

Runs `analyze_4c.run()` ONCE on the REAL pre-campaign tree (root=
`battery_4c.EXP4C`, root4=`battery_4.EXP4` — no exp4c results tree
exists yet beyond the committed `power_4c.json`, so it refuses at "4c
gate 1 pythia_6.9b: record missing", AFTER the discovery gate and the
power record's byte reproduction have both run — see `read_sweep_4c.
py`'s docstring for exactly where and the pre-tag disclosure count),
then imports every exp4c stage tool by hand (`make_referents_4c.py`,
`verify_referents_4c.py`, `run/preflight_4c.py`) so their own import
chains land in `sys.modules` too — none of them run on the verdict
path, but `check_frozen_4c`/`check_imports_4c` have no way to know a
module was imported for a STAGE TOOL and not the analyzer, so both
pins cover the whole surface a build session touches (2j's/2k's/2n's/
exp4's own precedent). `run/sweep_4c.py` and `power_4c.py` are already
blob-bound (`INSTRUMENT_BLOBS_4C`) — pulling them in again is harmless,
the instrument-blob check excludes them from `IMPORTED_SHA256_4C`.

Walks `sys.modules` afterward and keeps every module whose resolved
file is under `experiments/` and not under a `tests/` directory.
Splits by whether the file is under `experiments/exp4c/`: OUTSIDE and
not already covered by exp4's/exp4b's own closed pins -> `FROZEN_
SHA256_4C`; INSIDE and not one of `INSTRUMENT_BLOBS_4C` -> `IMPORTED_
SHA256_4C`.

Run: `PYTHONDONTWRITEBYTECODE=1 ~/emergence-lab/.venv/bin/python -m
experiments.exp4c.tests.import_scan_4c` from the repo root."""
from __future__ import annotations

import sys
from pathlib import Path

EXP4C = Path(__file__).resolve().parents[1]
REPO = EXP4C.parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp4 import battery_4  # noqa: E402
from experiments.exp4c import analyze_4c as an  # noqa: E402
from experiments.exp4c import battery_4c as bc  # noqa: E402


def _pull_in_every_stage_tool() -> None:
    import experiments.exp4c.make_referents_4c      # noqa: F401
    import experiments.exp4c.run.preflight_4c        # noqa: F401
    import experiments.exp4c.verify_referents_4c     # noqa: F401


def _blob_sha(tag, rel):
    p = battery_4.REPO / rel
    return bg.sha256_file(p) if p.is_file() else None


def scan() -> tuple:
    # `frozen_check` stubbed: this scan runs BEFORE `FROZEN_SHA256_4C`
    # is pinned (it is what BUILDS that pin), and `check_frozen_4c`
    # raises "not pinned" rather than passing trivially on an empty
    # table (battery_4c's own build-stage sentinel; `full_shape_4c.
    # world_run_kwargs_4c` makes the identical injection). `tag_exists`/
    # `blob_sha` stubbed too, so the run proceeds as deep as the REAL
    # pre-campaign tree allows (through the discovery gate and the
    # power record's byte reproduction, refusing at "4c gate 1
    # pythia_6.9b: record missing") rather than stopping early at the
    # prereg-tag check — every module the per-trajectory loop's own
    # loaders would touch (2h's/2l's manifest/entry functions) is
    # pulled in this way too, not just what the two rung-set/outcome
    # reads earlier in run() already cover.
    v = an.run(root=bc.EXP4C, root4=battery_4.EXP4, frozen_check=lambda: None,
              referents_sha=False, imports_pinned=False, tag_exists=lambda t: True,
              blob_sha=_blob_sha, n_boot=10)
    print(f"pre-campaign run: {v['verdict']} — {v['reason'][:200]}", file=sys.stderr)
    _pull_in_every_stage_tool()

    exp_root = str((battery_4.REPO / "experiments").resolve())
    exp4c_root = str(bc.EXP4C.resolve()) + "/"
    already_covered = {str(p) for p in battery_4.FROZEN_SHA256_4}
    for table in (bc.EXP4_CLOSED_SHA256_4C, bc.EXP4B_CLOSED_SHA256_4C):
        already_covered |= {str((battery_4.REPO / rel).resolve()) for rel in table}
    instrument = {str((battery_4.REPO / rel).resolve()) for rel in bc.INSTRUMENT_BLOBS_4C}

    frozen_out, imported_out = {}, {}
    for name, mod in sorted(sys.modules.items()):
        f = getattr(mod, "__file__", None)
        if not f:
            continue
        rp = Path(f).resolve()
        s = str(rp)
        if not s.startswith(exp_root + "/") or "tests" in rp.parts:
            continue
        if s.startswith(exp4c_root):
            if s in instrument:
                continue
            imported_out[rp] = bg.sha256_file(rp)
        else:
            if s in already_covered:
                continue
            frozen_out[rp] = bg.sha256_file(rp)
    return frozen_out, imported_out


def _print_literal(name: str, mapping: dict) -> None:
    print(f"{name} = {{")
    for p in sorted(mapping, key=lambda p: str(p.relative_to(bg.REPO))):
        rel = p.relative_to(bg.REPO)
        print(f'    REPO / "{rel}":')
        print(f'        "{mapping[p]}",')
    print("}")


def main() -> int:
    frozen, imported = scan()
    _print_literal("FROZEN_SHA256_4C", frozen)
    print()
    _print_literal("IMPORTED_SHA256_4C", imported)
    print(f"# {len(frozen)} frozen (non-exp4/exp4b) modules, {len(imported)} exp4c-own residual "
         f"module(s)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
