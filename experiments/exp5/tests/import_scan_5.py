# experiments/exp5/tests/import_scan_5.py
"""One-shot import-surface scan for `battery_5.FROZEN_SHA256_5` (`check_
frozen_5`'s pin — every module `experiments/exp5` imports transitively
OUTSIDE `experiments/exp5`) and `battery_5.IMPORTED_SHA256_5` (`check_
imports_5`'s residual pin — every non-test module INSIDE `experiments/
exp5` that is not one of the blob-bound `INSTRUMENT_BLOBS_5` files;
2j's F-1 lineage, exp4c's own `import_scan_4c.py` one experiment over).

Runs `analyze_5.run()` ONCE on the REAL pre-campaign tree (root=
`battery_5.EXP5` — no campaign has run yet, so it refuses early, at "5
host record" or an earlier gate; see `read_sweep_5.py`'s docstring for
exactly where and the pre-tag disclosure count), then imports every
exp5 stage tool by hand (`make_referents_5`, `verify_referents_5`,
`run/preflight_5`, `run/s9_mac_5`, `run/finals_5`, `run/sweep_5`,
`power_5`) so their own import chains land in `sys.modules` too — none
of them run on the verdict path, but `check_frozen_5`/`check_imports_5`
have no way to know a module was imported for a STAGE TOOL and not the
analyzer, so both pins cover the whole surface a build session
touches. `analyze_5.py`, `battery_5.py`, `run/finals_5.py`, `run/
sweep_5.py` and `power_5.py` are already blob-bound (`INSTRUMENT_
BLOBS_5`) — pulling them in again is harmless, the instrument-blob
check excludes them from `IMPORTED_SHA256_5`.

Walks `sys.modules` afterward and keeps every module whose resolved
file is under `experiments/` and not under a `tests/` directory (by
FILE PATH, not dotted name — `models`/`harness` land under
`experiments/exp2b/`/`experiments/exp2c/` on disk even though they are
imported as top-level module names via `battery_2d.py`'s sys.path
surgery, so they are caught here too). Splits by whether the file is
under `experiments/exp5/`: OUTSIDE -> `FROZEN_SHA256_5`; INSIDE and
not one of `INSTRUMENT_BLOBS_5` -> `IMPORTED_SHA256_5`.

Run: `PYTHONDONTWRITEBYTECODE=1 ~/emergence-lab/.venv/bin/python -m
experiments.exp5.tests.import_scan_5` from the repo root."""
from __future__ import annotations

import sys
from pathlib import Path

EXP5 = Path(__file__).resolve().parents[1]
REPO = EXP5.parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp5 import analyze_5 as an  # noqa: E402
from experiments.exp5 import battery_5 as b5  # noqa: E402


def _pull_in_every_stage_tool() -> None:
    import experiments.exp5.make_referents_5      # noqa: F401
    import experiments.exp5.verify_referents_5     # noqa: F401
    import experiments.exp5.run.preflight_5        # noqa: F401
    import experiments.exp5.run.s9_mac_5           # noqa: F401
    import experiments.exp5.run.finals_5           # noqa: F401
    import experiments.exp5.run.sweep_5            # noqa: F401
    import experiments.exp5.power_5                # noqa: F401


def _blob_sha(tag, rel):
    p = REPO / rel
    return bg.sha256_file(p) if p.is_file() else None


def scan() -> tuple:
    # `frozen_check` stubbed: this scan runs BEFORE `FROZEN_SHA256_5`
    # is pinned (it is what BUILDS that pin), and `check_frozen_5`
    # raises "not pinned" rather than passing trivially on an empty
    # table (battery_5's own build-stage sentinel). `tag_exists`/
    # `blob_sha` stubbed too, so the run proceeds as deep as the REAL
    # pre-campaign tree allows (through the referents/battery/floors/
    # verify loads) rather than stopping early at the prereg-tag check
    # — every module those loaders touch is pulled in this way too,
    # not just what `_pull_in_every_stage_tool` covers.
    v = an.run(root=b5.EXP5, frozen_check=lambda: None, referents_sha=False,
              imports_pinned=False, tag_exists=lambda t: True, blob_sha=_blob_sha,
              blobs_bound=lambda t, p, **k: [], n_sample=10, n_boot=10)
    print(f"pre-campaign run: {v['verdict']} — {(v['failures'] or [''])[0][:200]}",
          file=sys.stderr)
    _pull_in_every_stage_tool()

    exp_root = str((REPO / "experiments").resolve())
    exp5_root = str(EXP5.resolve()) + "/"
    instrument = {str((REPO / rel).resolve()) for rel in b5.INSTRUMENT_BLOBS_5}

    frozen_out, imported_out = {}, {}
    for name, mod in sorted(sys.modules.items()):
        f = getattr(mod, "__file__", None)
        if not f:
            continue
        rp = Path(f).resolve()
        s = str(rp)
        if not s.startswith(exp_root + "/") or "tests" in rp.parts:
            continue
        if s.startswith(exp5_root):
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
    _print_literal("FROZEN_SHA256_5", frozen)
    print()
    _print_literal("IMPORTED_SHA256_5", imported)
    print(f"# {len(frozen)} frozen (non-exp5) modules, {len(imported)} exp5-own residual "
         f"module(s)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
