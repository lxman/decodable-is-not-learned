# experiments/exp5b/tests/import_scan_5b.py
"""One-shot import-surface scan for `battery_5b.FROZEN_SHA256_5B` (`check_
frozen_5b`'s pin — every module `experiments/exp5b` imports transitively
OUTSIDE `experiments/exp5b`, Experiment 5's own modules included) and
`battery_5b.IMPORTED_SHA256_5B` (`check_imports_5b`'s residual pin —
every non-test module INSIDE `experiments/exp5b` that is not one of the
blob-bound `INSTRUMENT_BLOBS_5B` files; Experiment 5's own `import_scan_
5.py` one experiment over, 2j's F-1 lineage).

Runs `analyze_5b.run()` ONCE on the REAL pre-campaign tree (root=
`battery_5b.EXP5B` — no campaign has run yet, so it refuses early, at
"5b host record" or an earlier gate; see `read_sweep_5b.py`'s docstring
for exactly where and the pre-tag disclosure count), then imports every
5b stage tool by hand (`make_referents_5b`, `verify_referents_5b`, `run/
preflight_5b`, `run/units_5b`, `power_5b`) so their own import chains
land in `sys.modules` too — none of them run on the verdict path, but
`check_frozen_5b`/`check_imports_5b` have no way to know a module was
imported for a STAGE TOOL and not the analyzer, so both pins cover the
whole surface a build session touches. `analyze_5b.py`, `battery_5b.py`,
`collect_5b.py`, `power_5b.py` and `run/units_5b.py` are already
blob-bound (`INSTRUMENT_BLOBS_5B`) — pulling them in again is harmless,
the instrument-blob check excludes them from `IMPORTED_SHA256_5B`.

Walks `sys.modules` afterward and keeps every module whose resolved file
is under `experiments/` and not under a `tests/` directory (by FILE
PATH, not dotted name). Splits by whether the file is under
`experiments/exp5b/`: OUTSIDE -> `FROZEN_SHA256_5B` (Experiment 5's own
modules land here too, since `analyze_5b.run()`'s gate 2 runs Experiment
5's whole analyzer in-process); INSIDE and not one of `INSTRUMENT_
BLOBS_5B` -> `IMPORTED_SHA256_5B`.

Run: `PYTHONDONTWRITEBYTECODE=1 ~/emergence-lab/.venv/bin/python -m
experiments.exp5b.tests.import_scan_5b` from the repo root."""
from __future__ import annotations

import sys
from pathlib import Path

EXP5B = Path(__file__).resolve().parents[1]
REPO = EXP5B.parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp5b import analyze_5b as an  # noqa: E402
from experiments.exp5b import battery_5b as b5b  # noqa: E402


def _pull_in_every_stage_tool() -> None:
    import experiments.exp5b.make_referents_5b      # noqa: F401
    import experiments.exp5b.verify_referents_5b     # noqa: F401
    import experiments.exp5b.run.preflight_5b        # noqa: F401
    import experiments.exp5b.run.units_5b            # noqa: F401
    import experiments.exp5b.power_5b                # noqa: F401


def _blob_sha(tag, rel):
    p = REPO / rel
    return bg.sha256_file(p) if p.is_file() else None


def scan() -> tuple:
    # `frozen_check`/`referents_sha`/`imports_pinned` are all stubbed —
    # this scan runs BEFORE `FROZEN_SHA256_5B`/`IMPORTED_SHA256_5B` are
    # pinned (it is what BUILDS those pins); `check_frozen_5b`/`check_
    # imports_5b` raise "not pinned" rather than passing trivially on an
    # empty table (battery_5b's own build-stage sentinel). `tag_exists`/
    # `blob_sha` stubbed too, so the run proceeds as deep as the REAL
    # pre-campaign tree allows (through the manifest/slice/battery/
    # floors/verify loads and gate 2's full Experiment-5 analyzer run)
    # rather than stopping early at the prereg-tag check — every module
    # those loaders (and Experiment 5's own analyzer) touch is pulled in
    # this way too, not just what `_pull_in_every_stage_tool` covers.
    def blob_sha(tag, rel):
        p = REPO / rel
        return bg.sha256_file(p) if p.is_file() else None

    v = an.run(root=b5b.EXP5B, frozen_check=lambda: None, referents_sha=False, imports_pinned=False,
              tag_exists=lambda t: True, blob_sha=blob_sha,
              exp5_kwargs=dict(tag_exists=lambda t: True, blob_sha=blob_sha,
                               blobs_bound=lambda t, p, **k: []),
              n_sample=10, n_boot=10)
    print(f"pre-campaign run: {v['verdict']} — {(v['failures'] or [''])[0][:200]}", file=sys.stderr)
    _pull_in_every_stage_tool()

    exp_root = str((REPO / "experiments").resolve())
    exp5b_root = str(EXP5B.resolve()) + "/"
    instrument = {str((REPO / rel).resolve()) for rel in b5b.INSTRUMENT_BLOBS_5B}

    frozen_out, imported_out = {}, {}
    for name, mod in sorted(sys.modules.items()):
        f = getattr(mod, "__file__", None)
        if not f:
            continue
        rp = Path(f).resolve()
        s = str(rp)
        if not s.startswith(exp_root + "/") or "tests" in rp.parts:
            continue
        if s.startswith(exp5b_root):
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
    _print_literal("FROZEN_SHA256_5B", frozen)
    print()
    _print_literal("IMPORTED_SHA256_5B", imported)
    print(f"# {len(frozen)} frozen (non-exp5b) modules, {len(imported)} exp5b-own residual "
         f"module(s)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
