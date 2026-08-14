"""Load the campaign's 60 records and run the frozen analysis once.

**This is glue, not instrument.** `analyze_1b.verdict()` was frozen under tag
`exp1b-preregistered`; it takes lists of cell dicts and nothing in the frozen
tree reads records off disk. That gap was not caught by the plan or by the
freeze review, and this file closes it AFTER the freeze. It is therefore
written to make no decisions:

  - it reads every record under results/, with no filtering, no exclusions and
    no ordering that could matter (verdict() tallies, it does not iterate
    positionally);
  - it copies `s1.present` and `s1.accuracy` verbatim — `present` here is Exp
    1's RAW criterion, and the floor correction is applied inside the frozen
    `verdict()`, not here;
  - it takes `system`/`size_bucket`/`seed` from the record's own fields rather
    than from the directory path, and asserts the two agree, so a misfiled
    record is an error rather than a silent relabel;
  - it asserts 30 trained and 30 untrained cells before calling verdict(),
    which itself re-checks the matrix shape.

Run from the repo root:
    python -m experiments.exp1b.run.run_analysis_1b
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments.exp1b import analyze_1b as a

EXP1B_DIR = Path(__file__).resolve().parents[1]
RESULTS = EXP1B_DIR / "results"
SEEDS = (100, 101, 102, 103, 104)


def _cell(path: Path, system: str, size: str, seed: int) -> dict:
    d = json.loads(path.read_text())
    if d["system"] != system or d["size_bucket"] != size or d["seed"] != seed:
        raise ValueError(
            f"{path}: record says {d['system']}/{d['size_bucket']}/seed{d['seed']}, "
            f"path says {system}/{size}/seed{seed}")
    return {"system": system, "size_bucket": size, "seed": seed,
            "present": d["s1"]["present"], "accuracy": d["s1"]["accuracy"]}


def load() -> tuple[list[dict], list[dict]]:
    trained, untrained = [], []
    for system in a.TRAINED_ROWS:
        for size in a.SIZES:
            for seed in SEEDS:
                trained.append(_cell(
                    RESULTS / system / size / f"seed{seed}.json", system, size, seed))
                untrained.append(_cell(
                    RESULTS / "untrained" / system / size / f"seed{seed}.json",
                    system, size, seed))
    if len(trained) != 30 or len(untrained) != 30:
        raise ValueError(f"expected 30 + 30 cells, got {len(trained)} + {len(untrained)}")
    return trained, untrained


def main() -> int:
    trained, untrained = load()
    out = a.verdict(trained, untrained)

    print("=" * 62)
    print(f"EXPERIMENT 1b — VERDICT: {out['verdict']}")
    print("=" * 62)
    print()
    for row in ("grokking", "lubana_above", "lubana_below"):
        r = out["rows"][row]
        bar = "0/10" if row in a.ABSENT_ROWS else f">= {a.PRESENT_BAR}/10"
        print(f"{row:14s} {r['present']}/{r['n']} S1-present (floor-corrected)   "
              f"bar {bar}")
        print(f"{'':14s}   per-size {r['per_size']}   "
              f"raw {r['present_raw']}/{r['n']} per-size {r['per_size_raw']}")
        print(f"{'':14s}   CP95 ({r['cp95'][0]:.4f}, {r['cp95'][1]:.4f})")
    u = out["rows"]["untrained"]
    print(f"{'untrained':14s} {u['present']}/{u['n']} raw fires   "
          f"per-size {u['per_size']}   CP95 ({u['cp95'][0]:.4f}, {u['cp95'][1]:.4f})")
    print(f"{'':14s}   verdict_touching = {u['verdict_touching']} (diagnostic only)")
    print()
    if out["failures"]:
        print("FAILURES:")
        for f in out["failures"]:
            print(f"  - {f}")
    else:
        print("No failures: every verdict-touching bar met.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
