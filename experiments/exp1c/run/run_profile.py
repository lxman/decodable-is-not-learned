"""Exp 1c's profile runner: one cell's 8-site channel profile.

Reads the checkpoint tree exp1's `run_lubana.py` wrote during the 1b campaign
and probes it. Trains nothing. Modifies nothing under experiments/exp1/ or
experiments/exp1b/.

WHAT THIS DOES THAT 1B DID NOT. 1b stored one probe result per cell — the
argmax over 8 candidates — so the channel profile was thrown away at write
time and cannot be recovered from the records. This runner keeps all 8.

INTERFACES, read from the frozen exp1 source and restated here because
reproducing them from memory is how a wrong `chance` gets baked into a frozen
instrument (Exp 1's units failure, 2c's chance-floor defect):

  language   LubanaLanguage(LubanaConfig(seed=seed, **cfg.lang_kwargs))
             with lang_kwargs["edge_prob_mult"] overridden to the density.
             lang_kwargs is a function of `scale` alone — verified identical
             for model_size "1M" and None — so the 20 sweep languages
             (4 densities x 5 seeds) serve both size tiers.
                                                  configs/lubana.py:100
  pool       lang.singleton_entities() sub-critically; None above p_c, where
             the giant component has absorbed every entity and the singleton
             pool is empty by construction (measured: 0 at 10 p_c).
                                                  run_lubana.py:133
  model      _make_model(lang, cfg, seed)         run_lubana.py:80
  probe data _entity_probe_data(lang, device, model, pool=)
             one prompt per entity, [BOS, e, lVerb0], sites (layer, token)
             for token in (1, -1) over model.blocks.
                                                  run_lubana.py:64
  capability the checkpoint's own `eval_metric` — measured across the sweep
             before the freeze at 0.0976 mean against a chance of 0.1000, i.e.
             flat and at chance at every density, which is the other half of
             the preregistered conjunction.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import torch

EXP1C_DIR = Path(__file__).resolve().parents[1]
EXP1_DIR = EXP1C_DIR.parent / "exp1"

# exp1's runners import their own package absolutely; this is the only
# integration step needed and it modifies nothing under experiments/exp1/.
if str(EXP1_DIR) not in sys.path:
    sys.path.insert(0, str(EXP1_DIR))

from experiments.exp1.run.provenance import git_sha  # noqa: E402
from experiments.exp1.run.run_lubana import (  # noqa: E402
    LubanaConfig,
    LubanaLanguage,
    LubanaRunConfig,
    _entity_probe_data,
    _make_model,
    resolve_device,
)

from experiments.exp1c.records import ProfileRecord, record_path  # noqa: E402
from experiments.exp1c.run.profile_lib import (  # noqa: E402
    checkpoint_path,
    probe_sites,
    stratified_subsample,
)

# Design §4. 40/class has ZERO margin at 0.85 p_c, so the subsample asserts the
# count rather than shrinking to fit.
PER_CLASS = 40
VAL_FRAC = 0.25
# Raised from 1b's 1,000: at that count, Bonferroni across 8 sites makes the
# corrected p 8(k+1)/1001, so only a zero-exceedance sweep passes and the
# per-site test is binary. All ten of 1b's lubana_above fires sit at exactly
# 8/1001, pinned to that quantization floor.
N_PERM = 10_000
SWEEP_STEP = 10_000                     # the sweep's full training budget
SWEEP_DENSITIES = (0.25, 0.45, 0.65, 0.85)
LUBANA_MODEL_SIZE = {"1M": "1M", "10M": None}


def _config(system: str, size: str, density: float):
    setting = "above" if system == "lubana_above" else "below"
    cfg = LubanaRunConfig(setting=setting, scale="paper",
                          model_size=LUBANA_MODEL_SIZE[size])
    kw = dict(cfg.lang_kwargs)
    kw["edge_prob_mult"] = float(density)
    return cfg, kw


def probe_pool(system: str, arm: str, density: float, seed: int):
    """The entities this cell probes — identical for the trained cell and its
    twin, which is what makes the margin a paired difference rather than a
    comparison of two samples."""
    if system == "sweep" and not any(abs(density - d) < 1e-9
                                     for d in SWEEP_DENSITIES):
        raise ValueError(
            f"density {density} is not one the sweep trained {SWEEP_DENSITIES}")
    _cfg, kw = _config(system, "1M", density)
    lang = LubanaLanguage(LubanaConfig(seed=seed, **kw))
    if system == "lubana_above":
        ents = np.arange(lang.cfg.n_entities)
    else:
        ents = np.asarray(lang.singleton_entities(), dtype=int)
    if arm == "fixed":
        ents = stratified_subsample(ents, lang.entity_class[ents],
                                    PER_CLASS, seed=seed)
    return ents


def run_profile(system: str, arm: str, density: float, size: str, seed: int,
                *, trained: bool, out_root, step: int | None = None,
                n_perm: int | None = None) -> ProfileRecord:
    """Probe one cell at all 8 sites and save. Resumable: an existing record is
    returned untouched rather than recomputed."""
    out_path = record_path(out_root, system, arm, density, size, seed, trained)
    if out_path.exists():
        return ProfileRecord.load(out_path)

    ents = probe_pool(system, arm, density, seed)
    cfg, kw = _config(system, size, density)
    lang = LubanaLanguage(LubanaConfig(seed=seed, **kw))
    device = resolve_device(cfg.device)

    model = _make_model(lang, cfg, seed)
    capability = None
    if trained:
        ckpt_step = SWEEP_STEP if step is None else step
        ckpt = torch.load(checkpoint_path(system, size, seed, step=ckpt_step,
                                          density=density if system == "sweep"
                                          else None),
                          map_location="cpu", weights_only=False)
        model.load_state_dict(ckpt["state_dict"])
        capability = float(ckpt["eval_metric"])
    model.to(device)

    acts, labels = _entity_probe_data(lang, device, model, pool=ents)
    sites, n_val = probe_sites(
        acts, labels, seed=seed, val_frac=VAL_FRAC, return_n_val=True,
        # The natural arm is diagnostic and computes margins only — that is the
        # whole reason it costs 640 fits against the fixed arm's 9.6 M.
        n_perm=(n_perm if n_perm is not None else N_PERM)
        if arm == "fixed" else None)

    rec = ProfileRecord(
        system=system, arm=arm, density=float(density), size_bucket=size,
        seed=seed, trained=trained, sites=sites, n_rows=int(len(labels)),
        n_val=int(n_val), per_class=PER_CLASS if arm == "fixed" else None,
        capability_metric=capability, git_sha=git_sha(EXP1C_DIR),
        config=cfg.as_dict())
    rec.save(out_path)
    return rec


if __name__ == "__main__":
    system, arm, density, size, seed, trained = (
        sys.argv[1], sys.argv[2], float(sys.argv[3]), sys.argv[4],
        int(sys.argv[5]), sys.argv[6].lower() in ("1", "true", "trained"))
    out_root = Path(sys.argv[7]) if len(sys.argv) > 7 else EXP1C_DIR
    step = int(sys.argv[8]) if len(sys.argv) > 8 else None
    rec = run_profile(system, arm, density, size, seed, trained=trained,
                      out_root=out_root, step=step)
    print(f"[{system}/{arm}/p{density:g}/{size}/seed{seed}"
          f"/{'trained' if trained else 'twin'}] n={rec.n_rows} "
          f"val={rec.n_val} acc=" +
          " ".join(f"{s.layer}{'L' if s.token == -1 else 'E'}:{s.accuracy:.3f}"
                   for s in rec.sites))
