"""Phase-A driver: train once, run all three signatures, emit one RunRecord.

Design doc §5 run order step 1. This is the end-to-end pipeline debug (implementation
plan M3): it shakes out activations.py <-> probe.py and the sampling/forecast glue on
a real (if tiny) model. Phase-A verdicts are NOT scored into the truth table; the goal
is a valid RunRecord with sensible numbers and no crashes.

Run:  python -m run.run_phaseA            # from experiments/exp1/
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import torch

from configs.phase_a import PhaseAConfig
from models.transformer import DecoderTransformer, TransformerConfig
from signatures import (
    GTCheck,
    ResidualActivationCollector,
    RunRecord,
    elicit_by_sampling,
    forecast_from_below,
    probe_below_threshold,
)
from signatures.probe import best_probe_accuracy
from tasks.binding_task import BindingTask, BindingTaskConfig
from train.checkpointing import list_checkpoints, load_checkpoint
from train.loop import TrainConfig, resolve_device, train

from .provenance import git_sha, lib_versions

EXP_DIR = Path(__file__).resolve().parents[1]


def _batched(ids: torch.Tensor, batch: int = 512):
    for i in range(0, ids.shape[0], batch):
        yield ids[i : i + batch]


def _collect_acts(model, ids, device):
    with ResidualActivationCollector(
        model, list(model.blocks), token_indices=(-1,), device=device
    ) as col:
        return col.collect(_batched(ids))


def _make_sample_fn(model, device, temperature):
    """sample_fn(query, n, rng): forward the query once, draw n temperature samples."""
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


def run_phase_a(seed: int = 0, out_dir: Path | None = None) -> RunRecord:
    cfg = PhaseAConfig()
    out_dir = out_dir or EXP_DIR
    device = resolve_device(cfg.device)

    # --- task + data --------------------------------------------------------
    task = BindingTask(BindingTaskConfig(
        n_keys=cfg.n_keys, n_values=cfg.n_values, edge_prob=cfg.edge_prob,
        n_pairs=cfg.n_pairs, seed=seed,
    ))
    train_ids, _, train_tgt = task.make_dataset(cfg.n_train, seed=seed)
    eval_ids, _, eval_tgt = task.make_dataset(cfg.n_eval, seed=seed + 1)
    probe_ids, probe_labels, probe_tgt = task.make_dataset(cfg.n_probe, seed=seed + 2)

    # --- model + train ------------------------------------------------------
    model = DecoderTransformer(TransformerConfig(
        vocab_size=task.cfg.vocab_size, n_ctx=task.cfg.n_ctx,
        d_model=cfg.d_model, n_layers=cfg.n_layers, n_heads=cfg.n_heads, seed=seed,
    ))
    ckpt_dir = out_dir / "checkpoints" / "phaseA" / f"seed{seed}"
    hist = train(
        model, train_ids, train_tgt, eval_ids, eval_tgt,
        TrainConfig(
            total_steps=cfg.total_steps, batch_size=cfg.batch_size, lr=cfg.lr,
            weight_decay=cfg.weight_decay, n_checkpoints=cfg.n_checkpoints,
            device=cfg.device, seed=seed,
        ),
        ckpt_dir,
    )

    step_acc = dict(zip(hist.steps, hist.eval_acc))
    ckpts = list_checkpoints(ckpt_dir)
    true_transition = hist.transition_step(0.5)
    below_cut = cfg.below_threshold_mult * task.chance
    below = [(s, p) for (s, p) in ckpts if step_acc[s] < below_cut]

    # Latest below-threshold checkpoint: closest to the transition, most informative.
    s1_step, s1_path = below[-1] if below else ckpts[0]
    load_checkpoint(model, s1_path, map_location=device)
    model.to(device)

    # --- S1: probe below threshold -----------------------------------------
    acts = _collect_acts(model, probe_ids, device)
    s1 = probe_below_threshold(
        acts, probe_labels.numpy(), chance=task.chance,
        checkpoint_id=f"step_{s1_step:07d}", below_threshold=True,
        alpha=cfg.alpha, n_perm=cfg.n_perm, seed=seed,
    )

    # --- S2: exhaustive sampling at the same checkpoint ---------------------
    q_ids, _, q_tgt = task.make_dataset(cfg.s2_n_queries, seed=seed + 3)
    queries = [{"ids": q_ids[i : i + 1], "target": int(q_tgt[i])} for i in range(cfg.s2_n_queries)]
    sample_fn = _make_sample_fn(model, device, cfg.s2_temperature)

    @torch.no_grad()
    def argmax_fn(query):
        return int(model(query["ids"].to(device))[0, -1, :].argmax())

    s2 = elicit_by_sampling(
        sample_fn, queries, verifier=lambda q, s: s == q["target"],
        guessing_floor=task.chance, n_per_query=cfg.s2_n_per_query,
        argmax_fn=argmax_fn, checkpoint_id=f"step_{s1_step:07d}", seed=seed,
    )

    # --- S3: forecast from the probe-accuracy precursor ---------------------
    pre = [(s, p) for (s, p) in ckpts
           if true_transition is None or s < true_transition]
    xs, ys = [], []
    for s, p in pre:
        load_checkpoint(model, p, map_location=device)
        model.to(device)
        acc, _ = best_probe_accuracy(_collect_acts(model, probe_ids, device),
                                     probe_labels.numpy(), seed=seed)
        xs.append(float(s))
        ys.append(float(acc))

    if true_transition is not None and len(xs) >= 3:
        s3 = forecast_from_below(
            xs, ys, true_transition=float(true_transition),
            target_level=cfg.s3_target_level, axis="training_steps", seed=seed,
        )
    else:
        # Not enough pre-transition points (transition too early/never): forecast is
        # undefined. Record an explicit absent rather than fabricate one.
        from signatures.schema import ForecastResult
        s3 = ForecastResult(
            present=False, predicted_transition=float("nan"),
            true_transition=float(true_transition or -1),
            interval90=(float("nan"), float("nan")), rel_error=float("inf"),
            slope_ci=(0.0, 0.0), beats_no_transition_baseline=False,
            axis="training_steps",
        )

    # --- assemble + persist -------------------------------------------------
    torch_v, tf_v = lib_versions()
    rec = RunRecord(
        system="phaseA", size_bucket="phaseA", seed=seed,
        git_sha=git_sha(EXP_DIR), torch_version=torch_v, transformers_version=tf_v,
        gt_check=GTCheck(
            certified=true_transition is not None,
            method="phaseA_induction_over_training",
            details={
                "final_eval_acc": hist.eval_acc[-1] if hist.eval_acc else None,
                "transition_step": true_transition,
                "chance": task.chance,
                "percolation_threshold_pc": task.percolation_threshold(),
                "edge_prob": cfg.edge_prob,
                "n_params": model.num_params(),
            },
        ),
        s1=s1, s2=s2, s3=s3,
        config=cfg.as_dict(),
    )
    rec.save(out_dir / "results" / "phaseA" / f"seed{seed}.json")
    return rec


if __name__ == "__main__":
    rec = run_phase_a(seed=0)
    print("Phase-A RunRecord written.")
    print(f"  gt certified : {rec.gt_check.certified}  "
          f"(transition @ {rec.gt_check.details['transition_step']}, "
          f"final acc {rec.gt_check.details['final_eval_acc']:.3f})")
    print(f"  S1 probe     : present={rec.s1.present}  acc={rec.s1.accuracy:.3f} "
          f"(chance {rec.s1.chance:.3f})  p={rec.s1.null_p:.4g}  layer={rec.s1.best_layer}")
    print(f"  S2 sampling  : present={rec.s2.present} absent={rec.s2.absent}  "
          f"rate={rec.s2.rate_point:.2e}  CP=[{rec.s2.cp_lower:.2e},{rec.s2.cp_upper:.2e}]")
    print(f"  S3 forecast  : present={rec.s3.present}  pred={rec.s3.predicted_transition:.1f} "
          f"true={rec.s3.true_transition:.1f}  interval={rec.s3.interval90}")
