"""M1 inclusion pass: argmax at a probe-side size on every battery capability.

Usage:
    python -m run.run_inclusion <size> <trained|untrained> [capability ...]

size            410m | 1b   (probe side only — M1 never touches 2.8b+;
                             the two-stage lock forbids it before Stage 1 commits)
trained         pretrained weights at the ledgered SHA
untrained       seeded random init, same architecture — the empirical chance
                floor for this size (design §3), untrained seed 0, ledgered

One result JSON per (size, mode, capability) under results/inclusion/;
existing results are skipped (process rule 7: durable + resumable). The model
loads lazily on the first miss and is reused for every remaining capability.
"""

from __future__ import annotations

import sys

from battery.base import ITEMS_DIR, load_items
from harness import HFRunner, evaluate_to_file, result_path
from models import EVAL_SIZES, PROBE_SIZES, PYTHIA_SHAS, load_pythia

UNTRAINED_SEED = 0


def all_capability_names() -> list[str]:
    return sorted(p.stem for p in ITEMS_DIR.glob("*.json")
                  if p.stem not in ("scored_battery", "ejections"))


def main() -> None:
    size, mode = sys.argv[1], sys.argv[2]
    assert size in PROBE_SIZES, f"M1 runs probe sizes only, not {size!r} {EVAL_SIZES}"
    assert mode in ("trained", "untrained")
    caps = sys.argv[3:] or all_capability_names()

    runner = None

    def runner_factory():
        nonlocal runner
        if runner is None:
            tok, model = load_pythia(size, untrained=(mode == "untrained"),
                                     seed=UNTRAINED_SEED)
            runner = HFRunner(tok, model)
        return runner

    meta = {"size": size, "mode": mode, "sha": PYTHIA_SHAS[size],
            "untrained_seed": UNTRAINED_SEED if mode == "untrained" else None}
    for name in caps:
        r = evaluate_to_file(runner_factory, load_items(name),
                             result_path("inclusion", size, mode, name), meta)
        print(f"[m1] {size}/{mode}/{name}: acc={r['acc']:.4f} "
              f"cp95=({r['cp95'][0]:.4f},{r['cp95'][1]:.4f}) n={r['n']}", flush=True)


if __name__ == "__main__":
    main()
