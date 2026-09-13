# experiments/exp4/tests/import_scan_4.py
"""One-shot import-surface scan for `FROZEN_SHA256_4` (`battery_4.
check_frozen_4`'s pin — every module `experiments/exp4` imports
transitively OUTSIDE `experiments/exp4`) and `IMPORTED_SHA256_4`
(`analyze_4.check_imports_4`'s residual pin — every non-test module
INSIDE `experiments/exp4` that isn't one of the six blob-bound
`INSTRUMENT_BLOBS_4` files; 2j's F-1 lineage). Unlike 2n (which merges
four PRIOR sibling experiments' own residual import pins), exp4 is a
fresh experiment with no upstream residual pins to fold in — the split
is exactly frozen-outside-exp4 vs the-rest-of-exp4.

Runs `analyze_4.run()` ONCE on the REAL pre-campaign tree (no exp4
results tree exists yet, so it refuses early — see `read_sweep_4.py`'s
docstring for exactly where), then imports every exp4 stage tool by
hand (`run/reference_4.py`, `run/sweep_4.py`, `run/preflight_4.py`,
`power_4.py`, `make_referents_4.py`, `verify_referents_4.py`) so their
own import chains land in `sys.modules` too — none of them run on the
verdict path, but `check_frozen_4`/`check_imports_4` have no way to
know a module was imported for a STAGE TOOL and not the analyzer, so
both pins cover the whole surface a build session touches (2j's/2k's/
2n's own precedent).

Walks `sys.modules` afterward and keeps every module whose resolved
file is under `experiments/` and not under a `tests/` directory (2j's
disclosed exclusion). Splits by whether the file is under
`experiments/exp4/`: OUTSIDE -> `FROZEN_SHA256_4`; INSIDE and not one
of `INSTRUMENT_BLOBS_4` -> `IMPORTED_SHA256_4`.

Run: `PYTHONDONTWRITEBYTECODE=1 ~/emergence-lab/.venv/bin/python -m
experiments.exp4.tests.import_scan_4` from the repo root."""
from __future__ import annotations

import sys
from pathlib import Path

EXP4 = Path(__file__).resolve().parents[1]
REPO = EXP4.parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp4 import analyze_4 as an  # noqa: E402
from experiments.exp4 import battery_4  # noqa: E402


def _pull_in_every_stage_tool() -> None:
    import experiments.exp4.make_referents_4     # noqa: F401
    import experiments.exp4.power_4               # noqa: F401
    import experiments.exp4.run.preflight_4        # noqa: F401
    import experiments.exp4.run.reference_4        # noqa: F401
    import experiments.exp4.run.sweep_4            # noqa: F401
    import experiments.exp4.verify_referents_4     # noqa: F401


def scan() -> tuple:
    v = an.run(root=battery_4.EXP4, referents_sha=False, imports_pinned=False, n_boot=10)
    print(f"pre-campaign run: {v['verdict']} — {v['reason'][:200]}", file=sys.stderr)
    _pull_in_every_stage_tool()

    exp_root = str((battery_4.REPO / "experiments").resolve())
    exp4_root = str(battery_4.EXP4.resolve()) + "/"
    instrument = {str((battery_4.REPO / rel).resolve()) for rel in battery_4.INSTRUMENT_BLOBS_4}

    frozen_out, imported_out = {}, {}
    for name, mod in sorted(sys.modules.items()):
        f = getattr(mod, "__file__", None)
        if not f:
            continue
        rp = Path(f).resolve()
        s = str(rp)
        if not s.startswith(exp_root + "/") or "tests" in rp.parts:
            continue
        if s.startswith(exp4_root):
            if s in instrument:
                continue
            imported_out[rp] = bg.sha256_file(rp)
        else:
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
    _print_literal("FROZEN_SHA256_4", frozen)
    print()
    _print_literal("IMPORTED_SHA256_4", imported)
    print(f"# {len(frozen)} frozen modules, {len(imported)} exp4-own residual modules",
         file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
