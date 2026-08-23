"""Lubana confirmation run (gates the scored M5 runs, like confirm_grokking for M4).

Trains ONE seed at each graph setting with TRUE ONLINE data (fresh sentences every
batch -- the paper's recipe; a fixed-corpus variant produced a transient rise followed
by memorization collapse, see PROGRESS.md) and reports the capability curve
(masked-argmax class-generalization rate) over training, plus the graph's
connectivity certification. No signatures, no RunRecord. The gate passes iff:
  - ABOVE: the capability transitions over training (crosses transition_level) AND
    still holds at the final checkpoint (a stable capability, not a spike), and
  - BELOW: the capability stays ~flat at chance for the entire run.

If ABOVE fails, adjust the RECIPE (steps/lr/model size), never the thresholds. If
BELOW rises well above chance, STOP: either the graph is not actually sub-critical
(config bug) or the scored capability leaks memorization — investigate before any
scored run.

Usage:  python -m run.confirm_lubana [above|below|both] [total_steps] [seed] [scale] [model_size]
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

from configs.lubana import LubanaRunConfig
from tasks.lubana_lang import LubanaConfig, LubanaLanguage
from train.lm_loop import LMTrainConfig, masked_argmax_class_rate, train_lm
from train.loop import resolve_device

from .run_lubana import _make_model

EXP_DIR = Path(__file__).resolve().parents[1]


def confirm(setting: str, total_steps: int | None = None, seed: int = 0,
            scale: str | None = None, model_size: str | None = None):
    cfg = LubanaRunConfig(setting=setting, model_size=model_size,
                          **({"scale": scale} if scale else {}))
    steps = total_steps or cfg.total_steps
    device = resolve_device(cfg.device)

    lang = LubanaLanguage(LubanaConfig(seed=seed, **cfg.lang_kwargs))
    gstats = lang.giant_component_stats()
    print(f"[lubana:{setting}] scale={cfg.scale} p_c={gstats['p_c']:.2e} "
          f"edge_prob={gstats['edge_prob']:.2e} ({cfg.lang_kwargs['edge_prob_mult']}x p_c) "
          f"giant_frac={gstats['giant_frac_mean']:.3f}", flush=True)

    # Below row: subjects restricted to singleton-component entities, for whom the
    # data carries zero class evidence (kills the island-oracle inflation; see
    # PROGRESS.md). Above row: uniform (class structure = component structure there).
    pool = lang.singleton_entities() if setting == "below" else None
    queries = lang.make_queries(cfg.n_queries, seed=seed + 1, subjects_pool=pool)
    data_rng = np.random.default_rng(seed + 2)
    batch_fn = lambda b: lang.sample_batch(b, data_rng)  # noqa: E731
    print(f"[lubana:{setting}] online data; queries={cfg.n_queries} "
          f"chance={lang.chance:.3f}"
          + (f" singleton_pool={pool.size}/{lang.cfg.n_entities}" if pool is not None else ""),
          flush=True)

    model = _make_model(lang, cfg, seed)
    print(f"[lubana:{setting}] params={model.num_params()} "
          f"model_size={cfg.model_size or 'base'}", flush=True)

    eval_fn = lambda m: masked_argmax_class_rate(m, lang, queries, device)  # noqa: E731
    hist = train_lm(
        model, batch_fn, lang.cfg.pad, eval_fn,
        LMTrainConfig(total_steps=steps, batch_size=cfg.batch_size, lr=cfg.lr,
                      weight_decay=cfg.weight_decay, n_checkpoints=cfg.n_checkpoints,
                      device=cfg.device, seed=seed),
        EXP_DIR / "checkpoints" / f"lubana_confirm_{setting}{cfg.ckpt_suffix}" / f"seed{seed}",
    )

    print(f"{'step':>8} {'loss':>8} {'metric':>8}", flush=True)
    for s, l, m in zip(hist.steps, hist.train_loss, hist.eval_metric):
        print(f"{s:>8} {l:>8.3f} {m:>8.3f}", flush=True)

    trans = hist.transition_step(cfg.transition_level)
    final = hist.eval_metric[-1] if hist.eval_metric else 0.0
    peak = max(hist.eval_metric) if hist.eval_metric else 0.0
    if setting == "above":
        ok = trans is not None and final >= cfg.transition_level
        print(f"\n[confirm] ABOVE transitioned AND held: {ok} (transition@{trans}, "
              f"final={final:.3f}, chance={lang.chance:.3f})", flush=True)
    else:
        ok = peak < cfg.below_threshold_mult * lang.chance
        print(f"\n[confirm] BELOW stayed flat: {ok} (peak={peak:.3f}, "
              f"bar={cfg.below_threshold_mult * lang.chance:.3f}, chance={lang.chance:.3f})",
              flush=True)
    return ok, hist


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "both"
    steps = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2] else None
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    scale = sys.argv[4] if len(sys.argv) > 4 else None
    model_size = sys.argv[5] if len(sys.argv) > 5 else None
    settings = ["above", "below"] if which == "both" else [which]
    results = {s: confirm(s, steps, seed, scale, model_size)[0] for s in settings}
    print(f"\n[confirm_lubana] {results}", flush=True)
