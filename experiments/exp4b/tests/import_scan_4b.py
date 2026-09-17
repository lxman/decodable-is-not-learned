# experiments/exp4b/tests/import_scan_4b.py
"""One-shot import-surface scan for `IMPORTED_SHA256_4B` (`analyze_4b.
check_imports_4b`'s residual pin -- every non-test module INSIDE
`experiments/exp4b` that is not one of the five blob-bound
`INSTRUMENT_BLOBS_4B` files; 2j's F-1 lineage, exp4's own
`import_scan_4.py` one experiment over). Everything OUTSIDE
`experiments/exp4b` (exp2*/exp3*, and `experiments/exp4/` itself) is
already covered by `battery_4.FROZEN_SHA256_4`, `battery_4.
INSTRUMENT_BLOBS_4`, `battery_4b.EXP4_CLOSED_SHA256_4B`, and
`analyze_4.IMPORTED_SHA256_4` -- `check_imports_4b`'s own covered set
(see `analyze_4b.py`'s docstring) -- so this scan only needs to find
exp4b's OWN residual.

Runs `analyze_4b.run(stop_before="placebo")` ONCE on the REAL, closed
exp4 tree (B-4: no placebo quantity computed), then imports every
exp4b tool by hand (`make_referents_4b.py`, `verify_referents_4b.py`)
so their own import chains land in `sys.modules` too -- neither runs
on the verdict path, but `check_imports_4b` has no way to know a
module was imported for a STAGE TOOL and not the analyzer, so the pin
covers the whole surface a build session touches (2j's/2k's/2n's/
exp4's own precedent).

Walks `sys.modules` afterward and keeps every module whose resolved
file is under `experiments/exp4b/` and not under a `tests/` directory,
excluding the five `INSTRUMENT_BLOBS_4B` files themselves.

Run: `PYTHONDONTWRITEBYTECODE=1 ~/emergence-lab/.venv/bin/python -m
experiments.exp4b.tests.import_scan_4b` from the repo root."""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

EXP4B = Path(__file__).resolve().parents[1]
REPO = EXP4B.parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp4 import battery_4  # noqa: E402
from experiments.exp4b import analyze_4b as an4b  # noqa: E402
from experiments.exp4b import battery_4b  # noqa: E402


def _pull_in_every_stage_tool() -> None:
    import experiments.exp4b.make_referents_4b     # noqa: F401
    import experiments.exp4b.verify_referents_4b    # noqa: F401


def scan() -> dict:
    def blob_sha(tag, rel):
        p = battery_4b.REPO / rel
        return bg.sha256_file(p) if p.is_file() else None

    with tempfile.TemporaryDirectory() as tmp:
        v = an4b.run(root4b=Path(tmp) / "4b", root4=battery_4.EXP4, write=False,
                    stop_before="placebo", tag_exists=lambda t: True, blob_sha=blob_sha,
                    referents_sha=False, imports_pinned=False)
    print(f"pre-pin run: {v['verdict']} — {v['reason'][:200]}", file=sys.stderr)
    _pull_in_every_stage_tool()

    exp4b_root = str(EXP4B.resolve()) + "/"
    instrument = {str((battery_4b.REPO / rel).resolve()) for rel in battery_4b.INSTRUMENT_BLOBS_4B}

    imported_out = {}
    for name, mod in sorted(sys.modules.items()):
        f = getattr(mod, "__file__", None)
        if not f:
            continue
        rp = Path(f).resolve()
        s = str(rp)
        if not s.startswith(exp4b_root) or "tests" in rp.parts:
            continue
        if s in instrument:
            continue
        imported_out[rp] = bg.sha256_file(rp)
    return imported_out


def _print_literal(name: str, mapping: dict) -> None:
    print(f"{name} = {{")
    for p in sorted(mapping, key=lambda p: str(p.relative_to(bg.REPO))):
        rel = p.relative_to(bg.REPO)
        print(f'    REPO / "{rel}":')
        print(f'        "{mapping[p]}",')
    print("}")


def main() -> int:
    imported = scan()
    _print_literal("IMPORTED_SHA256_4B", imported)
    print(f"# {len(imported)} exp4b-own residual module(s)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
