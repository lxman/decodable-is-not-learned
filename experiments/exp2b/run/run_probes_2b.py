"""Fit starved probes over collected activations (M2 gates + M3 Stage 1).

Usage:
    python -m run.run_probes_2b <stage> <size> [capability ...]

stage:
  known_absent   starved probes on UNTRAINED activations — gate 1 (design §4):
                 fires must be consistent with the permutation-floor rate and
                 carry the floor signature; a structurally-above fire drops
                 that capability (attrition)
  shuffled       starved probes on TRAINED activations, labels shuffled with
                 rng(1000+seed) — gate 3, same binomial tolerance
  known_present  trained activations of entity_track + ctrl_copy — gate 2:
                 the instrument must SEE plainly-present capabilities
  m3             Stage 1 scored probes (trained, scored battery)

Five seeds per (stage, size, capability); the starving split re-draws per seed
(process rule 5). One JSON per unit under results/probes/, skip-if-exists —
the same layout distributed workers sync back into (idempotent merge).
Per-capability SplitParams come from the frozen spec registry; bases and
labels from the committed item files.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

from activations import activations_path, load_activation_map
from battery.base import load_items
from battery.generators import SPECS
from probe_starved import probe_starved
from run.battery_sets import CONTROLS, GATE_CAPS, scored_battery

EXP_DIR = Path(__file__).resolve().parent.parent
SEEDS = (0, 1, 2, 3, 4)
STAGES = ("known_absent", "shuffled", "known_present", "m3")
LAYER_STRIDE = 3
_SPEC = {s.name: s for s in SPECS}


def thin_layers(act: dict) -> dict:
    n_layers = 1 + max(l for l, _ in act.keys())
    keep = set(range(0, n_layers, LAYER_STRIDE)) | {n_layers - 1}
    return {(l, s): X for (l, s), X in act.items() if l in keep}


def probe_result_path(stage: str, size: str, cap: str, seed: int) -> Path:
    return EXP_DIR / "results" / "probes" / stage / f"{size}_{cap}_seed{seed}.json"


def fit_one(stage: str, size: str, cap: str, seed: int) -> dict:
    out = probe_result_path(stage, size, cap, seed)
    if out.exists():
        return json.loads(out.read_text())

    mode = "untrained" if stage == "known_absent" else "trained"
    act, y, meta = load_activation_map(activations_path(size, mode, cap))
    act = thin_layers(act)
    items = load_items(cap)["probe_items"]
    bases = [tuple(it["basis"]) for it in items]
    assert len(bases) == len(y)
    split_labels = None
    if stage == "shuffled":
        rng = np.random.default_rng(1000 + seed)
        split_labels = y   # split from TRUE labels; only the fit is shuffled
        y = rng.permutation(y)

    r = probe_starved(
        act, y, bases,
        split_params=_SPEC[cap].split_params,
        checkpoint_id=f"pythia-{size}:{meta['sha'][:8]}:{mode}",
        seed=seed,
        split_labels=split_labels,
    )
    import socket
    d = {"stage": stage, "size": size, "capability": cap,
         "host": socket.gethostname(), **r}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(d, indent=1))
    return d


def _worker(args):
    import os
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    return fit_one(*args)


def default_caps(stage: str) -> list[str]:
    return (GATE_CAPS + CONTROLS) if stage == "known_present" else scored_battery()


def run_stage(stage: str, size: str, caps: list[str], processes: int = 8) -> None:
    """fit_one rechecks existence at execution time, so results synced in from
    other workers mid-stage are skipped — collisions cost at most one unit.

    processes <= 1 runs INLINE (no multiprocessing at all): Windows Task
    Scheduler sessions deny the handle duplication Pool's spawn needs
    (WinError 5) — sharded single-process instances sidestep it entirely."""
    jobs = [(stage, size, cap, seed) for cap in caps for seed in SEEDS
            if not probe_result_path(stage, size, cap, seed).exists()]
    print(f"[probe] {stage}/{size}: {len(jobs)} to fit, "
          f"{len(caps) * len(SEEDS) - len(jobs)} cached", flush=True)

    def report(d):
        print(f"[probe] {d['stage']}/{d['size']}/{d['capability']}/seed{d['seed']}: "
              f"present={d['present']} p={d['null_p']:.4g} "
              f"acc={d['accuracy']:.4f} margin={d['margin']:.4f}", flush=True)

    if processes <= 1:
        for job in jobs:
            report(_worker(job))
        return
    from multiprocessing import Pool
    with Pool(processes=processes) as pool:
        for d in pool.imap_unordered(_worker, jobs):
            report(d)


def main() -> None:
    stage, size = sys.argv[1], sys.argv[2]
    assert stage in STAGES, f"stage must be one of {STAGES}"
    caps = sys.argv[3:] or default_caps(stage)
    run_stage(stage, size, caps)


if __name__ == "__main__":
    main()
