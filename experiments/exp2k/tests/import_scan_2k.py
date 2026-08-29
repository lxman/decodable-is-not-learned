# experiments/exp2k/tests/import_scan_2k.py
"""One-shot import-surface scan for `IMPORTED_SHA256_2K` (analyze_2k.
check_imports_2k's own residual pin — 2j's F-1 lineage, closed on
2k's own files at pin time rather than discovered at the freeze).

Runs `analyze_2k.run()` ONCE on the REAL pre-campaign tree — the 2k
tier does not exist yet, so the run lands INSUFFICIENT_DATA, but it
still executes every 2i-side loader (`load_2i_tree`, 2j's block) and
the 2k-side halt scan / seal read before it refuses — then imports
every 2k stage tool by hand (`run/seal_2k.py`, `power_2k.py`,
`make_referents_2k.py`, `verify_referents_2k.py`, `run/tier_2k.py`,
`run/campaign_2k.py`, `run/rehearse_2k.py`) so their own import chains
land in `sys.modules` too — none of them run on the verdict path, but
`check_imports_2k` has no way to know that a module was imported for a
STAGE TOOL and not the analyzer, so the residual pin covers the whole
surface a build session touches, matching 2j's own precedent.

Walks `sys.modules` afterward and keeps every module whose resolved
file is under `experiments/` and not under a `tests/` directory (2j's
disclosed exclusion: world fixtures and this scan itself live there,
the campaign path imports none of them), subtracts `FROZEN_SHA256_2K`,
`battery_2g.FROZEN_IMPORT_SHA256_2G` and the three `INSTRUMENT_BLOBS_2K`,
and prints the remainder as the `IMPORTED_SHA256_2K` literal — paste
directly into `analyze_2k.py`.

Run: `PYTHONDONTWRITEBYTECODE=1 ~/emergence-lab/.venv/bin/python -m
experiments.exp2k.tests.import_scan_2k` from the repo root."""
from __future__ import annotations

import sys
from pathlib import Path

EXP2K = Path(__file__).resolve().parents[1]
REPO = EXP2K.parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp2i import battery_2i as bi  # noqa: E402
from experiments.exp2k import analyze_2k as an  # noqa: E402
from experiments.exp2k import battery_2k as bk  # noqa: E402


def _pull_in_every_stage_tool() -> None:
    """Every 2k module a build/freeze session imports somewhere, not
    only what `analyze_2k.run()` itself reaches — matching what the
    residual pin is FOR (2j's precedent: the whole surface a session
    touches, not merely the verdict path)."""
    import experiments.exp2k.run.campaign_2k     # noqa: F401
    import experiments.exp2k.run.rehearse_2k     # noqa: F401
    import experiments.exp2k.run.seal_2k         # noqa: F401
    import experiments.exp2k.run.tier_2k         # noqa: F401
    import experiments.exp2k.make_referents_2k   # noqa: F401
    import experiments.exp2k.power_2k            # noqa: F401
    import experiments.exp2k.verify_referents_2k  # noqa: F401


def _pull_in_gate1_rederivation_surface() -> None:
    """`battery_2k.diff_seed0` LAZILY imports `experiments.exp3d.
    rederive_3d.diff_seed` — invisible to a pre-campaign `an.run()`
    (every rung fails "record or draws file missing" before
    `load_tier_2k`'s `_gate()` ever calls it) and to a bare `import
    experiments.exp2k.run.tier_2k` (the runner's OWN gate-1 check is a
    separate, inline comparison that never imports `rederive_3d`).
    `rederive_3d.py` itself IS in FROZEN_FILES_2K, but its own
    module-level import (`from experiments.exp3d.analyze_3d import
    ...`, which in turn imports `functional_3d`/`rank_test_3d`) pulls
    in three more files plus the `exp3d` package `__init__.py`, none
    previously listed anywhere. A real campaign run — or any full-shape
    world with real tier data, as `test_seal_2k.py`'s worlds already
    are — imports this chain the moment `load_tier_2k`'s gate-1
    re-derivation runs; a bare module import reproduces the same
    `sys.modules` state without needing real tier data or model
    contact, so it belongs in the residual pin now rather than being
    discovered as a live gap once the campaign runs."""
    import experiments.exp3d.rederive_3d   # noqa: F401


def scan() -> dict:
    v = an.run(root_2i=bi.EXP2I, root_2k=bk.EXP2K, referents_sha=False, imports_pinned=False,
              n_perm=30, n_boot=10)
    print(f"pre-campaign run: {v['verdict']} — {v['reason'][:160]}", file=sys.stderr)
    _pull_in_every_stage_tool()
    _pull_in_gate1_rederivation_surface()

    covered = {str(Path(p).resolve()) for p in bk.FROZEN_SHA256_2K}
    covered |= {str(Path(p).resolve()) for p in bg.FROZEN_IMPORT_SHA256_2G}
    covered |= {str((bg.REPO / rel).resolve()) for rel in bk.INSTRUMENT_BLOBS_2K}
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
    print("IMPORTED_SHA256_2K = {")
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
