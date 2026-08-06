"""M1 inclusion pass for 2c: argmax at a probe-side size on the NEW-pool
scored rungs + ctrl_copy (design §6 M1; gate 4).

Usage:
    python -m run.run_inclusion <size> <trained|untrained> [capability ...]

size            410m | 1b   (probe side only — M1 never touches 2.8b+;
                             the two-stage lock forbids it before Stage 1)
trained         pretrained weights at the ledgered SHA
untrained       seeded random init, same architecture — the empirical
                chance floor for this size (design §3), seed 0

Scope (design §7 data-reuse): the 12 reused survivors' M1 record
carries from 2b ("the 2b fits ARE the 2c fits ... none recomputed"),
so the default capability list is the tier-1-passing NEW-pool rungs
plus ctrl_copy — gate 4's control, measured on 2c's own items, never
transferred. The carry is a named freeze-checklist line.

One result JSON per (size, mode, capability) under results/inclusion/;
existing results are skipped (process rule 7: durable + resumable).
Ported from exp2b/run/run_inclusion.py; model loading goes through
exp2b's pinned models.py via the instrument sys.path shim (same SHAs,
same fp16/MPS policy — no second loader to drift).
"""

from __future__ import annotations

import sys

import instrument  # noqa: F401  (puts exp2b on sys.path: models, splits)
import models  # exp2b's pinned loader, reached through the shim

from battery.family_map import REUSED_FAMILIES, scored_battery_families
from harness import HFRunner, evaluate_to_file, load_items, result_path

PROBE_SIZES = models.PROBE_SIZES
UNTRAINED_SEED = 0


def m1_capability_names() -> list[str]:
    """Tier-1-passing new-pool rungs (screen-aware, reused excluded) +
    the gate-4 control."""
    new_pool = sorted(n for n in scored_battery_families()
                      if n not in REUSED_FAMILIES)
    return new_pool + ["ctrl_copy"]


def main() -> None:
    size, mode = sys.argv[1], sys.argv[2]
    assert size in PROBE_SIZES, \
        f"M1 runs probe sizes only, not {size!r} {models.EVAL_SIZES}"
    assert mode in ("trained", "untrained")
    caps = sys.argv[3:] or m1_capability_names()

    runner = None

    def runner_factory():
        nonlocal runner
        if runner is None:
            tok, model = models.load_pythia(
                size, untrained=(mode == "untrained"), seed=UNTRAINED_SEED)
            runner = HFRunner(tok, model)
        return runner

    meta = {"size": size, "mode": mode, "sha": models.PYTHIA_SHAS[size],
            "untrained_seed": UNTRAINED_SEED if mode == "untrained" else None}
    for name in caps:
        r = evaluate_to_file(runner_factory, load_items(name),
                             result_path("inclusion", size, mode, name), meta)
        print(f"[m1] {size}/{mode}/{name}: acc={r['acc']:.4f} "
              f"cp95=({r['cp95'][0]:.4f},{r['cp95'][1]:.4f}) n={r['n']}",
              flush=True)


if __name__ == "__main__":
    main()
