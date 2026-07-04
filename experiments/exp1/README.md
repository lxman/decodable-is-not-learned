# Experiment 1 — Validate the Instrument

Code for Experiment 1. **Read `../../experiment-1-design.md` (frozen, preregistered) and
`../../experiment-1-implementation-plan.md` first** — this directory implements them and
adds no hypotheses or thresholds.

One-line purpose: show the three-signature test can tell a resolution-class transition
(modular-arithmetic grokking) from a percolation-class one (Lubana formal language below
threshold) on cases where the class is known by construction.

## Setup

```
source ~/emergence-lab/.venv/bin/activate
pip install -r experiments/exp1/requirements.txt   # adds scikit-learn, scipy, matplotlib
```

Runs entirely on the Mac (M4 Pro, 48 GB, MPS). The DGX Sparks are never used.

## Layout

- `signatures/` — the reusable instrument (S1 probe, S2 sampling, S3 forecast) + stats +
  the frozen `RunRecord` schema. Imports nothing from the task/model code; Exp 2/3/4 import
  this package.
- `tasks/` — modular arithmetic (grokking), Lubana formal language, Phase-A binding task.
- `models/` — minimal decoder with a size knob (~1M / 10M / 100M).
- `train/` — shared training loop + checkpointing.
- `configs/`, `run/` — resolved configs and thin per-run drivers.
- `analyze.py` — the frozen analysis script. Committed + git-tagged before result-grade data.
- `results/` — committed `RunRecord` JSON per run + the final truth table.
- `checkpoints/` — gitignored; regenerable from configs + seeds.

## Tests

```
cd experiments/exp1 && python -m pytest
```

## Status

- M0 — scaffold + deps. **Done.**
- M1 — frozen contracts: `signatures/stats.py` + `signatures/schema.py` (24 tests). **Done.**
- M2 — signature bodies: `activations.py` + `probe.py` (S1) + `sampling.py` (S2) + `forecast.py` (S3), each validated on planted-signal inputs (43 tests cumulative). **Done.**
- M3 — Phase-A pipeline debug: minimal decoder + binding task + training loop + driver run end-to-end into `results/phaseA/seed0.json` (54 tests). Probe reads the latent answer at a below-threshold checkpoint (S1 present). **Done.**
- M3.5 — **FREEZE** `analyze.py` + schema; tag `exp1-analysis-frozen`. *Next.*
- M4–M7 — see the implementation plan's milestone list.

See `PROGRESS.md` for the full build ledger (milestone → design §, commit, tests) and
the pre-freeze operational choices.
