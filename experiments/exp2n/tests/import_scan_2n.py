# experiments/exp2n/tests/import_scan_2n.py
"""One-shot import-surface scan for `IMPORTED_SHA256_2N` (analyze_2n.
check_imports_2n's own residual pin — 2j's F-1 lineage, closed on 2n's
own files at pin time rather than discovered at the freeze).

Runs `analyze_2n.run()` ONCE on the REAL pre-campaign tree — no Comma
v0.1-1T endpoint/sweep/power/rung-set records exist yet, so the run
lands INSUFFICIENT_DATA, but it still executes every predictor-side
loader first: 2k's tier (`analyze_2k.load_tier_2k`, real and closed, so
its own gate-1 re-derivation runs to completion — including its lazily
imported `experiments.exp3d.rederive_3d` chain) and 2i's sealed OLMo-2
1B counts (`load_predictor_records_2i`, `sampler_counts_olmo`), plus
the 2n-side halt scan and both predictor-seal reads, before refusing on
the missing prereg tag and the absent Comma endpoint/rung-set/power/
sweep records — then imports every 2n stage tool by hand
(`run/endpoint_2n.py`, `run/sweep_2n.py`, `run/preflight_2n.py`,
`power_2n.py`, `make_referents_2n.py`, `verify_referents_2n.py`) so
their own import chains land in `sys.modules` too — none of them run
on the verdict path, but `check_imports_2n` has no way to know that a
module was imported for a STAGE TOOL and not the analyzer, so the
residual pin covers the whole surface a build session touches,
matching 2j's/2k's/2l's/2m's own precedent.

Walks `sys.modules` afterward and keeps every module whose resolved
file is under `experiments/` and not under a `tests/` directory (2j's
disclosed exclusion: world fixtures and this scan itself live there,
the campaign path imports none of them), subtracts `FROZEN_SHA256_2N`,
`battery_2g.FROZEN_IMPORT_SHA256_2G`, the four `INSTRUMENT_BLOBS_2N`,
2j's own residual pin (`analyze_2j.IMPORTED_SHA256_2J`), 2k's
(`analyze_2k.IMPORTED_SHA256_2K`), 2l's (`analyze_2l.IMPORTED_SHA256_2L`)
and 2m's (`analyze_2m.IMPORTED_SHA256_2M`) — all four already folded
into `check_imports_2n`'s verified set — and prints the remainder as
the `IMPORTED_SHA256_2N` literal — paste directly into `analyze_2n.py`.

Run: `PYTHONDONTWRITEBYTECODE=1 ~/emergence-lab/.venv/bin/python -m
experiments.exp2n.tests.import_scan_2n` from the repo root."""
from __future__ import annotations

import sys
from pathlib import Path

EXP2N = Path(__file__).resolve().parents[1]
REPO = EXP2N.parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp2i import battery_2i as bi  # noqa: E402
from experiments.exp2j import analyze_2j as an2j  # noqa: E402
from experiments.exp2k import analyze_2k as an2k  # noqa: E402
from experiments.exp2k import battery_2k as bk  # noqa: E402
from experiments.exp2l import analyze_2l as an2l  # noqa: E402
from experiments.exp2l import battery_2l as bl  # noqa: E402
from experiments.exp2m import analyze_2m as an2m  # noqa: E402
from experiments.exp2m import battery_2m as bm  # noqa: E402
from experiments.exp2n import analyze_2n as an  # noqa: E402
from experiments.exp2n import battery_2n as bn  # noqa: E402


def _pull_in_every_stage_tool() -> None:
    """Every 2n module a build/freeze session imports somewhere, not
    only what `analyze_2n.run()` itself reaches — matching what the
    residual pin is FOR (2j's/2k's/2l's/2m's precedent: the whole
    surface a session touches, not merely the verdict path)."""
    import experiments.exp2n.run.endpoint_2n     # noqa: F401
    import experiments.exp2n.run.preflight_2n    # noqa: F401
    import experiments.exp2n.run.sweep_2n        # noqa: F401
    import experiments.exp2n.make_referents_2n   # noqa: F401
    import experiments.exp2n.power_2n            # noqa: F401
    import experiments.exp2n.verify_referents_2n  # noqa: F401


def scan() -> dict:
    v = an.run(root_2n=bn.EXP2N, root_2i=bi.EXP2I, root_2k=bk.EXP2K, root_2l=bl.EXP2L,
              root_2m=bm.EXP2M, referents_sha=False, imports_pinned=False, n_perm=30, n_boot=10)
    print(f"pre-campaign run: {v['verdict']} — {v['reason'][:160]}", file=sys.stderr)
    _pull_in_every_stage_tool()

    covered = {str(Path(p).resolve()) for p in bn.FROZEN_SHA256_2N}
    covered |= {str(Path(p).resolve()) for p in bg.FROZEN_IMPORT_SHA256_2G}
    covered |= {str((bg.REPO / rel).resolve()) for rel in bn.INSTRUMENT_BLOBS_2N}
    covered |= {str(Path(p).resolve()) for p in an2j.IMPORTED_SHA256_2J}
    covered |= {str(Path(p).resolve()) for p in an2k.IMPORTED_SHA256_2K}
    covered |= {str(Path(p).resolve()) for p in an2l.IMPORTED_SHA256_2L}
    covered |= {str(Path(p).resolve()) for p in an2m.IMPORTED_SHA256_2M}
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
    print("IMPORTED_SHA256_2N = {")
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
