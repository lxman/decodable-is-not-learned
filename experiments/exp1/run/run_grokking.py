"""Grokking scored driver: train one seed, run all three signatures, emit a RunRecord.

Design doc §5 run order step 2 (the resolution row). Uses the FROZEN §3 rules: the
below-threshold checkpoint is the latest with argmax test acc < 5%; chance = 1/113;
S3's precursor is the S1 probe-accuracy trajectory over pre-transition checkpoints.
The independent ground-truth check is the memorization->generalization gap
(tasks.modular_arith.certify_grokking), not any signature.

Run one seed:   python -m run.run_grokking [seed]
Run 5 seeds:    for s in 0 1 2 3 4; do python -m run.run_grokking $s; done
"""

from __future__ import annotations

import sys
from pathlib import Path

import torch

from configs.grokking import GrokkingConfig
from models.transformer import DecoderTransformer, TransformerConfig
from signatures import (
    GTCheck,
    RunRecord,
    elicit_by_sampling,
    forecast_from_below,
    probe_below_threshold,
)
from signatures.probe import best_probe_accuracy
from signatures.schema import ForecastResult
from tasks.modular_arith import ModArithConfig, ModArithTask, certify_grokking
from train.checkpointing import list_checkpoints, load_checkpoint
from train.loop import TrainConfig, resolve_device, train

# Reuse the signature-running helpers built and debugged in Phase A.
from .run_phaseA import _collect_acts, _make_sample_fn
from .provenance import git_sha, lib_versions

EXP_DIR = Path(__file__).resolve().parents[1]


def run_grokking(seed: int = 0, out_dir: Path | None = None) -> RunRecord:
    cfg = GrokkingConfig()
    out_dir = out_dir or EXP_DIR
    device = resolve_device(cfg.device)

    task = ModArithTask(ModArithConfig(p=cfg.p, op=cfg.op, train_frac=cfg.train_frac, seed=seed))
    data = task.make_split(seed)
    model = DecoderTransformer(TransformerConfig(
        vocab_size=task.vocab_size, n_ctx=task.n_ctx,
        d_model=cfg.d_model, n_layers=cfg.n_layers, n_heads=cfg.n_heads, seed=seed,
    ))
    ckpt_dir = out_dir / "checkpoints" / "grokking" / f"seed{seed}"
    hist = train(
        model, data["train_ids"], data["train_targets"],
        data["test_ids"], data["test_targets"],
        TrainConfig(
            total_steps=cfg.total_steps, full_batch=cfg.full_batch, lr=cfg.lr,
            weight_decay=cfg.weight_decay, betas=cfg.betas,
            n_checkpoints=cfg.n_checkpoints, device=cfg.device, seed=seed,
        ),
        ckpt_dir,
    )

    step_test = dict(zip(hist.steps, hist.eval_acc))
    ckpts = list_checkpoints(ckpt_dir)
    true_transition = hist.transition_step(0.5)

    # Probe set: a held-out sample of the test pairs (never trained on). Sized by
    # cfg.probe_n so the probe is not data-starved (a 113-way linear probe needs
    # enough examples/class to lead the model's own argmax — the S1/S3 premise).
    n_probe = min(cfg.probe_n, data["test_ids"].shape[0])
    probe_ids = data["test_ids"][:n_probe]
    probe_labels = data["test_labels"][:n_probe].numpy()

    # --- S1 at the latest below-threshold checkpoint (argmax test acc < 5%) ---
    below = [(s, p) for (s, p) in ckpts if step_test[s] < cfg.below_threshold_level]
    s1_step, s1_path = below[-1] if below else ckpts[0]
    load_checkpoint(model, s1_path, map_location=device)
    model.to(device)
    acts = _collect_acts(model, probe_ids, device)
    s1 = probe_below_threshold(
        acts, probe_labels, chance=task.chance,
        checkpoint_id=f"step_{s1_step:07d}", below_threshold=True,
        alpha=cfg.alpha, n_perm=cfg.n_perm, seed=seed,
    )

    # --- S2 at the same checkpoint -----------------------------------------
    q_split = ModArithTask(ModArithConfig(p=cfg.p, op=cfg.op, train_frac=cfg.train_frac,
                                          seed=seed)).make_split(seed)
    qi = q_split["test_ids"][: cfg.s2_n_queries]
    qt = q_split["test_targets"][: cfg.s2_n_queries]
    queries = [{"ids": qi[i : i + 1], "target": int(qt[i])} for i in range(qi.shape[0])]
    verifier = lambda q, s: s == q["target"]  # noqa: E731
    sample_fn = _make_sample_fn(model, device, cfg.s2_temperature)

    @torch.no_grad()
    def argmax_fn(query):
        return int(model(query["ids"].to(device))[0, -1, :].argmax())

    # Empirical guessing floor (design §3): a random-init UNTRAINED control sampled
    # identically. Use its Clopper-Pearson upper bound as the floor, so "present"
    # requires clearing even the optimistic estimate of guessing.
    control = DecoderTransformer(TransformerConfig(
        vocab_size=task.vocab_size, n_ctx=task.n_ctx,
        d_model=cfg.d_model, n_layers=cfg.n_layers, n_heads=cfg.n_heads, seed=seed + 10_000,
    )).to(device)
    control_floor = elicit_by_sampling(
        _make_sample_fn(control, device, cfg.s2_temperature), queries, verifier,
        guessing_floor=0.0, n_per_query=cfg.s2_n_per_query, argmax_fn=None,
        checkpoint_id="untrained_control", seed=seed,
    ).cp_upper

    s2 = elicit_by_sampling(
        sample_fn, queries, verifier,
        guessing_floor=control_floor, n_per_query=cfg.s2_n_per_query,
        argmax_fn=argmax_fn, argmax_reliable_level=cfg.below_threshold_level,
        checkpoint_id=f"step_{s1_step:07d}", seed=seed,
    )

    # --- S3 forecast from the probe-accuracy precursor ----------------------
    pre = [(s, p) for (s, p) in ckpts if true_transition is None or s < true_transition]
    xs, ys = [], []
    for s, p in pre:
        load_checkpoint(model, p, map_location=device)
        model.to(device)
        acc, _ = best_probe_accuracy(_collect_acts(model, probe_ids, device), probe_labels, seed=seed)
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
            slope_ci=(0.0, 0.0), beats_no_transition_baseline=False, axis="training_steps",
        )

    certified, gt_details = certify_grokking(hist.steps, hist.train_acc, hist.eval_acc)
    gt_details.update({"transition_step": true_transition, "n_params": model.num_params(),
                       "below_threshold_checkpoint": s1_step})

    torch_v, tf_v = lib_versions()
    rec = RunRecord(
        system="grokking", size_bucket=cfg.size_bucket, seed=seed,
        git_sha=git_sha(EXP_DIR), torch_version=torch_v, transformers_version=tf_v,
        gt_check=GTCheck(certified=certified, method="memorization_generalization_gap",
                         details=gt_details),
        s1=s1, s2=s2, s3=s3, config=cfg.as_dict(),
    )
    rec.save(out_dir / "results" / "grokking" / cfg.size_bucket / f"seed{seed}.json")
    return rec


if __name__ == "__main__":
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    rec = run_grokking(seed)
    print(f"[grokking seed {seed}] gt_certified={rec.gt_check.certified} "
          f"(mem@{rec.gt_check.details['mem_step']} gen@{rec.gt_check.details['gen_step']})")
    print(f"  S1 present={rec.s1.present} acc={rec.s1.accuracy:.3f} (chance {rec.s1.chance:.4f}) "
          f"p={rec.s1.null_p:.4g} @ {rec.s1.checkpoint_id}")
    print(f"  S2 present={rec.s2.present} absent={rec.s2.absent} rate={rec.s2.rate_point:.2e} "
          f"CP=[{rec.s2.cp_lower:.2e},{rec.s2.cp_upper:.2e}]")
    print(f"  S3 present={rec.s3.present} pred={rec.s3.predicted_transition:.0f} "
          f"true={rec.s3.true_transition:.0f}")
