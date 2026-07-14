"""Fit frozen probes over collected activations (M2 gates + M3 Stage 1).

Usage:
    python -m run.run_probes <stage> <size> [capability ...]

stage:
  m2_untrained   probes on untrained-model activations — must NOT fire; a fire
                 triggers the preregistered per-capability attrition rule (§3)
  m2_shuffled    probes on TRAINED activations with seeded label shuffles —
                 must fail everywhere; a fire is a pipeline abort
  m2_controls    probes on trained activations of the positive controls
  m3             Stage 1 scored probes (trained activations, scored battery)

Five seeds per (stage, size, capability) — design §3 process rule 5. One result
JSON per (stage, size, capability, seed) under results/probes/, skip-if-exists.

Operational choices (mechanics, ledgered): `chance` recorded for the report is
the empirical majority-class frequency of the labels; below_threshold=True for
scored capabilities by battery membership (the frozen 1b inclusion rule IS the
below-threshold certification; design §2) and for control probes trivially
(controls are pipeline gates, not scored data). The shuffled stage permutes
labels with rng(1000+seed) so shuffles are reproducible and differ per seed.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

from activations import activations_path, load_activation_map
from probe_frozen import probe_below_threshold

EXP_DIR = Path(__file__).resolve().parent.parent
SEEDS = (0, 1, 2, 3, 4)
STAGES = ("m2_untrained", "m2_shuffled", "m2_controls", "m3")
CONTROLS = ["ctrl_copy", "ctrl_next_letter"]

# Candidate family + permutation budget (mechanics, ledgered 2026-07-14 BEFORE
# any gate ran). Family = every 3rd layer plus the final layer, x 2 positions
# (410m: 18 candidates, 1b: 12). The add-one permutation floor times the
# Bonferroni family must clear alpha=.01: N_PERM=2500 gives floors .0072/.0048.
# All layers are COLLECTED; thinning happens at fit time, so the family choice
# is revisable pre-gate without recollection.
LAYER_STRIDE = 3
N_PERM = 2500


def thin_layers(act: dict) -> dict:
    n_layers = 1 + max(l for l, _ in act.keys())
    keep = set(range(0, n_layers, LAYER_STRIDE)) | {n_layers - 1}
    return {(l, s): X for (l, s), X in act.items() if l in keep}


def probe_result_path(stage: str, size: str, cap: str, seed: int) -> Path:
    return EXP_DIR / "results" / "probes" / stage / f"{size}_{cap}_seed{seed}.json"


def empirical_chance(labels) -> float:
    counts = Counter(labels)
    return max(counts.values()) / len(labels)


def normalized_margin(result_dict: dict) -> float:
    """Design §3: best normalized probe margin at the frozen significance bar;
    probes failing the bar score margin 0 ('no signal' is ordering information).
    Chance for normalization is the permutation-null mean — the probe's own
    empirically measured no-signal accuracy."""
    if result_dict["null_p"] >= 0.01:
        return 0.0
    c = result_dict["null_mean"]
    return (result_dict["accuracy"] - c) / max(1e-9, 1.0 - c)


def fit_one(stage: str, size: str, cap: str, seed: int) -> dict:
    out = probe_result_path(stage, size, cap, seed)
    if out.exists():
        return json.loads(out.read_text())

    mode = "untrained" if stage == "m2_untrained" else "trained"
    act, y, meta = load_activation_map(activations_path(size, mode, cap))
    act = thin_layers(act)
    if stage == "m2_shuffled":
        rng = np.random.default_rng(1000 + seed)
        y = rng.permutation(y)

    r = probe_below_threshold(
        act, y,
        chance=empirical_chance(y),
        checkpoint_id=f"pythia-{size}:{meta['sha'][:8]}:{mode}",
        below_threshold=True,
        n_perm=N_PERM,
        seed=seed,
    )
    d = {
        "stage": stage, "size": size, "capability": cap, "seed": seed,
        "present": r.present, "accuracy": r.accuracy, "chance": r.chance,
        "null_p": r.null_p, "null_mean": r.null_mean, "ci95": list(r.ci95),
        "best_layer": r.best_layer, "best_token": r.best_token,
        "n_candidates": r.n_layers_tested,
    }
    d["margin"] = normalized_margin(d)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(d, indent=1))
    return d


def _worker(args):
    import os
    os.environ.setdefault("OMP_NUM_THREADS", "1")  # 8 procs x full BLAS = thrash
    return fit_one(*args)


def main() -> None:
    stage, size = sys.argv[1], sys.argv[2]
    assert stage in STAGES, f"stage must be one of {STAGES}"
    if sys.argv[3:]:
        caps = sys.argv[3:]
    elif stage == "m2_controls":
        caps = CONTROLS
    else:
        from run.collect_activations import scored_battery
        caps = scored_battery()

    from multiprocessing import Pool
    jobs = [(stage, size, cap, seed) for cap in caps for seed in SEEDS
            if not probe_result_path(stage, size, cap, seed).exists()]
    cached = [(cap, seed) for cap in caps for seed in SEEDS
              if probe_result_path(stage, size, cap, seed).exists()]
    for cap, seed in cached:
        print(f"[probe] skip {stage}/{size}/{cap}/seed{seed} (exists)", flush=True)
    with Pool(processes=8) as pool:
        for d in pool.imap_unordered(_worker, jobs):
            print(f"[probe] {d['stage']}/{d['size']}/{d['capability']}/seed{d['seed']}: "
                  f"present={d['present']} p={d['null_p']:.4g} "
                  f"acc={d['accuracy']:.4f} margin={d['margin']:.4f}", flush=True)


if __name__ == "__main__":
    main()
