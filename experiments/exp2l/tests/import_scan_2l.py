# experiments/exp2l/tests/import_scan_2l.py
"""One-shot import-surface scan for `IMPORTED_SHA256_2L` (analyze_2l.
check_imports_2l's own residual pin — 2j's F-1 lineage, closed on 2l's
own files at pin time rather than discovered at the freeze).

Runs `analyze_2l.run()` ONCE on the REAL pre-campaign tree — no OLMo-2
13B endpoint/sweep/power/rung-set records exist yet, so the run lands
INSUFFICIENT_DATA, but it still executes every predictor-side loader
first: 2k's tier (`analyze_2k.load_tier_2k`, real and closed, so its
own gate-1 re-derivation runs to completion — including its lazily
imported `experiments.exp3d.rederive_3d` chain) and 2i's sealed OLMo-2
1B counts (`load_predictor_records_2i`, `sampler_counts_olmo`), plus
the 2l-side halt scan and both predictor-seal reads, before refusing on
the missing 13B endpoint/rung-set/power records — then imports every 2l
stage tool by hand (`run/endpoint_2l.py`, `run/sweep_2l.py`,
`run/preflight_2l.py`, `power_2l.py`, `make_referents_2l.py`,
`verify_referents_2l.py`) so their own import chains land in
`sys.modules` too — none of them run on the verdict path, but
`check_imports_2l` has no way to know that a module was imported for a
STAGE TOOL and not the analyzer, so the residual pin covers the whole
surface a build session touches, matching 2j's/2k's own precedent.

Walks `sys.modules` afterward and keeps every module whose resolved
file is under `experiments/` and not under a `tests/` directory (2j's
disclosed exclusion: world fixtures and this scan itself live there,
the campaign path imports none of them), subtracts `FROZEN_SHA256_2L`,
`battery_2g.FROZEN_IMPORT_SHA256_2G`, the four `INSTRUMENT_BLOBS_2L`,
2j's own residual pin (`analyze_2j.IMPORTED_SHA256_2J`) and 2k's own
residual pin (`analyze_2k.IMPORTED_SHA256_2K`) — both already folded
into `check_imports_2l`'s verified set — and prints the remainder as
the `IMPORTED_SHA256_2L` literal — paste directly into `analyze_2l.py`.

Run: `PYTHONDONTWRITEBYTECODE=1 ~/emergence-lab/.venv/bin/python -m
experiments.exp2l.tests.import_scan_2l` from the repo root."""
from __future__ import annotations

import sys
from pathlib import Path

EXP2L = Path(__file__).resolve().parents[1]
REPO = EXP2L.parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp2i import battery_2i as bi  # noqa: E402
from experiments.exp2j import analyze_2j as an2j  # noqa: E402
from experiments.exp2k import analyze_2k as an2k  # noqa: E402
from experiments.exp2k import battery_2k as bk  # noqa: E402
from experiments.exp2l import analyze_2l as an  # noqa: E402
from experiments.exp2l import battery_2l as bl  # noqa: E402


def _pull_in_every_stage_tool() -> None:
    """Every 2l module a build/freeze session imports somewhere, not
    only what `analyze_2l.run()` itself reaches — matching what the
    residual pin is FOR (2j's/2k's precedent: the whole surface a
    session touches, not merely the verdict path)."""
    import experiments.exp2l.run.endpoint_2l    # noqa: F401
    import experiments.exp2l.run.preflight_2l   # noqa: F401
    import experiments.exp2l.run.sweep_2l       # noqa: F401
    import experiments.exp2l.make_referents_2l  # noqa: F401
    import experiments.exp2l.power_2l           # noqa: F401
    import experiments.exp2l.verify_referents_2l  # noqa: F401


def scan() -> dict:
    v = an.run(root_2l=bl.EXP2L, root_2i=bi.EXP2I, root_2k=bk.EXP2K, referents_sha=False,
              imports_pinned=False, n_perm=30, n_boot=10)
    print(f"pre-campaign run: {v['verdict']} — {v['reason'][:160]}", file=sys.stderr)
    _pull_in_every_stage_tool()

    covered = {str(Path(p).resolve()) for p in bl.FROZEN_SHA256_2L}
    covered |= {str(Path(p).resolve()) for p in bg.FROZEN_IMPORT_SHA256_2G}
    covered |= {str((bg.REPO / rel).resolve()) for rel in bl.INSTRUMENT_BLOBS_2L}
    covered |= {str(Path(p).resolve()) for p in an2j.IMPORTED_SHA256_2J}
    covered |= {str(Path(p).resolve()) for p in an2k.IMPORTED_SHA256_2K}
    root = str((bg.REPO / "experiments").resolve())

    out = {}
    for name, mod in sorted(sys.modules.items()):
        f = getattr(mod, "__file__", None)
        if not f:
            continue
        rp = Path(f).resolve()
        s = str(rp)
        if not s.startswith(root + "/") or "tests" in rp.parts:
            continue
        if s in covered:
            continue
        out[rp] = bg.sha256_file(rp)
    return out


def print_literal(mapping: dict) -> None:
    print("IMPORTED_SHA256_2L = {")
    for p in sorted(mapping, key=lambda p: str(p.relative_to(bg.REPO))):
        rel = p.relative_to(bg.REPO)
        print(f'    bg.REPO / "{rel}":')
        print(f'        "{mapping[p]}",')
    print("}")


def main() -> int:
    mapping = scan()
    print_literal(mapping)
    print(f"# {len(mapping)} modules", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
