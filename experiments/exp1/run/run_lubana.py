"""Lubana scored driver: train one (setting, seed), run all three signatures, emit a
RunRecord. Design doc §5 run order step 3 — the percolation ground-truth row
(lubana_below) and the control row (lubana_above).

The instrument is the same frozen code the grokking row used (post-M4 freeze): this
IS its out-of-sample test. Operationalizations preregistered in PROGRESS.md:

- Capability: class-structure generalization (masked argmax over never-trainable
  descriptive properties; pass iff same-class). Chance = 1/|C|.
- Below-threshold rule: capability metric < 1.5 * chance.
- S1: linear probe of the SUBJECT ENTITY'S CLASS from residual activations on
  one-prompt-per-entity data — the example split is therefore an ENTITY split, so
  above-chance validation requires the model to organize held-out entities by class
  (a random example-split would let the probe memorize the entity->class lookup and
  fire on an untrained model).
- S2: full-vocab temperature sampling at the prompt's next-token position; verifier =
  the class-generalization check; empirical guessing floor from an untrained control;
  argmax "fails" iff the masked-argmax metric < 1.5 * chance.
- S3: lubana_above -> training-axis probe precursor (as grokking, frozen log
  transform). lubana_below -> GRAPH-axis attempt (design §3): dedicated sub-critical
  runs at s3_graph_points * p_c, fixed s3_graph_budget_steps each, y = capability
  metric, forecast toward the true transition at p_c.
- gt_check: the graph's own giant-component fraction (data structure, model-free) +
  the capability curve's behaviour (above: transitioned and held; below: flat).

Run one seed:  python -m run.run_lubana <above|below> <seed> [scale] [model_size]
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import torch

from configs.lubana import MODEL_SIZE_TARGETS, LubanaRunConfig
from models.transformer import DecoderTransformer, TransformerConfig, scale_width_to_budget
from signatures import (
    GTCheck,
    ResidualActivationCollector,
    RunRecord,
    elicit_by_sampling,
    forecast_from_below,
    probe_below_threshold,
)
from signatures.probe import best_probe_accuracy
from signatures.schema import ForecastResult
from tasks.lubana_lang import LubanaConfig, LubanaLanguage
from train.checkpointing import list_checkpoints, load_checkpoint
from train.lm_loop import LMTrainConfig, masked_argmax_class_rate, train_lm
from train.loop import resolve_device

from .provenance import git_sha, lib_versions

EXP_DIR = Path(__file__).resolve().parents[1]


def _size_bucket(n_params: int) -> str:
    """Nearest order-of-magnitude bucket of the frozen schema."""
    return min(("1M", "10M", "100M"), key=lambda b: abs(np.log10(n_params) - np.log10({"1M": 1e6, "10M": 1e7, "100M": 1e8}[b])))


def _entity_probe_data(lang, device, model, pool=None):
    """One prompt per entity ('BOS e lVerb0'); activations at the entity position and
    the last position; labels = entity class. Entity-split by construction. `pool`
    restricts to given entities (below row: singleton components, so islandmate
    label-matching cannot masquerade as class structure)."""
    cfg = lang.cfg
    ents = np.asarray(pool) if pool is not None else np.arange(cfg.n_entities)
    prompts = np.full((ents.size, 3), cfg.pad, dtype=np.int64)
    for i, e in enumerate(ents):
        prompts[i] = [cfg.bos, int(e), cfg.tok_lverb0]  # fixed lVerb: no confound
    ids = torch.from_numpy(prompts)
    with ResidualActivationCollector(model, list(model.blocks), token_indices=(1, -1), device=device) as col:
        acts = col.collect([ids[i : i + 512] for i in range(0, ents.size, 512)])
    return acts, lang.entity_class[ents].copy()


def _make_model(lang, cfg, seed):
    if cfg.model_size:  # M6: width-only scaling, depth/heads at the validated base
        tcfg = scale_width_to_budget(
            lang.cfg.vocab_size, lang.cfg.max_len, MODEL_SIZE_TARGETS[cfg.model_size],
            n_layers=cfg.n_layers, n_heads=cfg.n_heads, seed=seed,
        )
        return DecoderTransformer(tcfg)
    return DecoderTransformer(TransformerConfig(
        vocab_size=lang.cfg.vocab_size, n_ctx=lang.cfg.max_len,
        d_model=cfg.d_model, n_layers=cfg.n_layers, n_heads=cfg.n_heads, seed=seed,
    ))


def _train_setting(lang, cfg, seed, steps, ckpt_dir, device, pool=None):
    model = _make_model(lang, cfg, seed)
    queries = lang.make_queries(cfg.n_queries, seed=seed + 1, subjects_pool=pool)
    data_rng = np.random.default_rng(seed + 2)
    hist = train_lm(
        model, lambda b: lang.sample_batch(b, data_rng), lang.cfg.pad,
        lambda m: masked_argmax_class_rate(m, lang, queries, device),
        LMTrainConfig(total_steps=steps, batch_size=cfg.batch_size, lr=cfg.lr,
                      weight_decay=cfg.weight_decay, n_checkpoints=cfg.n_checkpoints,
                      device=cfg.device, seed=seed),
        ckpt_dir,
    )
    return model, queries, hist


def _sample_fn_for(model, device, temperature):
    @torch.no_grad()
    def sample_fn(query, n, rng):
        model.eval()
        logits = model(query["ids"].to(device))[0, -1, :].float().cpu().numpy()
        logits = logits / temperature
        logits -= logits.max()
        probs = np.exp(logits)
        probs /= probs.sum()
        return rng.choice(len(probs), size=n, p=probs).tolist()
    return sample_fn


def run_lubana(setting: str, seed: int = 0, scale: str | None = None,
               model_size: str | None = None, out_dir: Path | None = None) -> RunRecord:
    cfg = LubanaRunConfig(setting=setting, model_size=model_size,
                          **({"scale": scale} if scale else {}))
    out_dir = out_dir or EXP_DIR
    device = resolve_device(cfg.device)

    lang = LubanaLanguage(LubanaConfig(seed=seed, **cfg.lang_kwargs))
    gstats = lang.giant_component_stats()
    below_bar = cfg.below_threshold_mult * lang.chance
    # Below row: evaluation entities restricted to singleton components (zero class
    # evidence in training data -> the no-capability floor is exactly chance).
    pool = lang.singleton_entities() if setting == "below" else None

    ckpt_dir = out_dir / "checkpoints" / f"lubana_{setting}{cfg.ckpt_suffix}" / f"seed{seed}"
    model, queries, hist = _train_setting(lang, cfg, seed, cfg.total_steps, ckpt_dir, device, pool=pool)

    step_metric = dict(zip(hist.steps, hist.eval_metric))
    ckpts = list_checkpoints(ckpt_dir)
    true_transition = hist.transition_step(cfg.transition_level)

    # --- checkpoint for S1/S2: latest below-threshold (metric < 1.5*chance). For the
    # below setting every checkpoint qualifies -> the LAST one (the strongest case:
    # absent even after full training).
    below_ckpts = [(s, p) for (s, p) in ckpts if step_metric[s] < below_bar]
    s1_step, s1_path = below_ckpts[-1] if below_ckpts else ckpts[0]
    load_checkpoint(model, s1_path, map_location=device)
    model.to(device)

    # --- S1 --------------------------------------------------------------------
    acts, class_labels = _entity_probe_data(lang, device, model, pool=pool)
    s1 = probe_below_threshold(
        acts, class_labels, chance=lang.chance,
        checkpoint_id=f"step_{s1_step:07d}", below_threshold=True,
        alpha=cfg.alpha, n_perm=cfg.n_perm, seed=seed,
    )

    # --- S2 --------------------------------------------------------------------
    q2 = lang.make_queries(cfg.s2_n_queries, seed=seed + 3, subjects_pool=pool)
    q_list = [{"ids": q2["prompts"][i : i + 1], "idx": i} for i in range(cfg.s2_n_queries)]
    verifier = lambda q, tok: lang.verify_choice(q["idx"], q2, int(tok))  # noqa: E731

    control = _make_model(lang, cfg, seed + 10_000).to(device)
    control_floor = elicit_by_sampling(
        _sample_fn_for(control, device, cfg.s2_temperature), q_list, verifier,
        guessing_floor=0.0, n_per_query=cfg.s2_n_per_query, argmax_fn=None,
        checkpoint_id="untrained_control", seed=seed,
    ).cp_upper

    @torch.no_grad()
    def argmax_fn(query):
        logits = model(query["ids"].to(device))[0, -1, :].float().cpu()
        logits[~q2["masks"][query["idx"]]] = float("-inf")
        return int(logits.argmax())

    s2 = elicit_by_sampling(
        _sample_fn_for(model, device, cfg.s2_temperature), q_list, verifier,
        guessing_floor=control_floor, n_per_query=cfg.s2_n_per_query,
        argmax_fn=argmax_fn, argmax_reliable_level=below_bar,
        checkpoint_id=f"step_{s1_step:07d}", seed=seed,
    )

    # --- S3 --------------------------------------------------------------------
    if setting == "above":
        # training-axis probe precursor, as grokking (frozen log transform)
        pre = [(s, p) for (s, p) in ckpts if true_transition is None or s < true_transition]
        xs, ys = [], []
        for s, p in pre:
            load_checkpoint(model, p, map_location=device)
            model.to(device)
            a, _ = _entity_probe_data(lang, device, model)
            acc, _key = best_probe_accuracy(a, class_labels, seed=seed)
            xs.append(float(s))
            ys.append(float(acc))
        if true_transition is not None and len(xs) >= 3:
            s3 = forecast_from_below(
                xs, ys, true_transition=float(true_transition),
                target_level=cfg.s3_target_level, axis="training_steps",
                transform=cfg.s3_precursor_transform, seed=seed,
            )
        else:
            s3 = ForecastResult(
                present=False, predicted_transition=float("nan"),
                true_transition=float(true_transition or -1),
                interval90=(float("nan"), float("nan")), rel_error=float("inf"),
                slope_ci=(0.0, 0.0), beats_no_transition_baseline=False,
                axis="training_steps",
            )
    else:
        # GRAPH-axis attempt from below the percolation threshold (design §3):
        # dedicated sub-critical runs, y = capability metric after a fixed budget.
        xs, ys = [], []
        for mult in cfg.s3_graph_points:
            sub_kw = dict(cfg.lang_kwargs)
            sub_kw["edge_prob_mult"] = mult
            sub_lang = LubanaLanguage(LubanaConfig(seed=seed, **sub_kw))
            sub_dir = out_dir / "checkpoints" / f"lubana_s3graph_{mult}{cfg.ckpt_suffix}" / f"seed{seed}"
            _m, _q, sub_hist = _train_setting(
                sub_lang, cfg, seed, cfg.s3_graph_budget_steps, sub_dir, device,
                pool=sub_lang.singleton_entities())  # island-free metric, as the main below row
            xs.append(float(sub_lang.cfg.edge_prob))          # absolute p
            ys.append(float(sub_hist.eval_metric[-1]))
        s3 = forecast_from_below(
            xs, ys, true_transition=float(lang.cfg.p_c),
            target_level=cfg.s3_target_level, axis="graph_param",
            transform=cfg.s3_precursor_transform, seed=seed,
        )

    # --- assemble ----------------------------------------------------------------
    final_metric = hist.eval_metric[-1] if hist.eval_metric else 0.0
    peak_metric = max(hist.eval_metric) if hist.eval_metric else 0.0
    if setting == "above":
        certified = (gstats["giant_frac_min"] > 0.3 and true_transition is not None
                     and final_metric >= cfg.transition_level)
    else:
        certified = gstats["giant_frac_mean"] < 0.1 and peak_metric < below_bar

    n_params = model.num_params()
    torch_v, tf_v = lib_versions()
    rec = RunRecord(
        system=cfg.system, size_bucket=_size_bucket(n_params), seed=seed,
        git_sha=git_sha(EXP_DIR), torch_version=torch_v, transformers_version=tf_v,
        gt_check=GTCheck(
            certified=bool(certified), method="graph_connectivity+capability_curve",
            details={**gstats, "transition_step": true_transition,
                     "final_metric": final_metric, "peak_metric": peak_metric,
                     "chance": lang.chance, "below_bar": below_bar,
                     "n_params": n_params, "scale": cfg.scale},
        ),
        s1=s1, s2=s2, s3=s3, config=cfg.as_dict(),
    )
    rec.save(out_dir / "results" / cfg.system / rec.size_bucket / f"seed{seed}.json")
    return rec


if __name__ == "__main__":
    setting = sys.argv[1]
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    scale = sys.argv[3] if len(sys.argv) > 3 else None
    model_size = sys.argv[4] if len(sys.argv) > 4 else None
    rec = run_lubana(setting, seed, scale, model_size)
    print(f"[lubana_{setting} seed {seed}] gt_certified={rec.gt_check.certified} "
          f"(final={rec.gt_check.details['final_metric']:.3f} "
          f"peak={rec.gt_check.details['peak_metric']:.3f} "
          f"giant={rec.gt_check.details['giant_frac_mean']:.3f})")
    print(f"  S1 present={rec.s1.present} acc={rec.s1.accuracy:.3f} "
          f"(chance {rec.s1.chance:.3f}) p={rec.s1.null_p:.4g} @ {rec.s1.checkpoint_id}")
    print(f"  S2 present={rec.s2.present} absent={rec.s2.absent} "
          f"rate={rec.s2.rate_point:.2e} CP=[{rec.s2.cp_lower:.2e},{rec.s2.cp_upper:.2e}] "
          f"floor={rec.s2.guessing_floor:.2e}")
    print(f"  S3 present={rec.s3.present} axis={rec.s3.axis} "
          f"pred={rec.s3.predicted_transition:.4g} true={rec.s3.true_transition:.4g}")
