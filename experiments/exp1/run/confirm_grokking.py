"""Grok-confirmation run (design open item, gates M4 -> M6).

Trains the base grokking config for one seed and reports the train/test accuracy
curve plus the memorization->generalization certification. NO signatures, NO RunRecord
-- its only job is to confirm the config actually groks on the Mac before spending
5 seeds x 3 sizes. If it does not grok, adjust the RECIPE (lr, weight_decay,
train_frac, steps) here -- never the frozen thresholds.

Usage:
  python -m run.confirm_grokking [total_steps] [device] [seed] [size]
  e.g.  python -m run.confirm_grokking 40000 mps 0
        python -m run.confirm_grokking "" "" 0 100M
"""

from __future__ import annotations

import sys
from pathlib import Path

from configs.grokking import grokking_config_for
from models.transformer import DecoderTransformer, TransformerConfig
from tasks.modular_arith import ModArithConfig, ModArithTask, certify_grokking
from train.loop import TrainConfig, train

EXP_DIR = Path(__file__).resolve().parents[1]


def confirm(total_steps: int | None = None, device: str | None = None, seed: int = 0,
            size: str = "1M"):
    cfg = grokking_config_for(size)
    steps = total_steps or cfg.total_steps
    dev = device or cfg.device

    task = ModArithTask(ModArithConfig(p=cfg.p, op=cfg.op, train_frac=cfg.train_frac, seed=seed))
    data = task.make_split(seed)
    model = DecoderTransformer(TransformerConfig(
        vocab_size=task.vocab_size, n_ctx=task.n_ctx,
        d_model=cfg.d_model, n_layers=cfg.n_layers, n_heads=cfg.n_heads, seed=seed,
    ))
    n_params = model.num_params()
    suffix = "" if size == "1M" else f"_{size}"
    ckpt_dir = EXP_DIR / "checkpoints" / f"grokking_confirm{suffix}" / f"seed{seed}"

    print(f"[confirm] size={size} d_model={cfg.d_model} p={cfg.p} op={cfg.op} frac={cfg.train_frac} "
          f"train={data['train_ids'].shape[0]} test={data['test_ids'].shape[0]} "
          f"params={n_params} steps={steps} device={dev}", flush=True)

    hist = train(
        model, data["train_ids"], data["train_targets"],
        data["test_ids"], data["test_targets"],
        TrainConfig(
            total_steps=steps, full_batch=cfg.full_batch, lr=cfg.lr,
            weight_decay=cfg.weight_decay, betas=cfg.betas,
            n_checkpoints=cfg.n_checkpoints, device=dev, seed=seed,
        ),
        ckpt_dir,
    )

    print(f"{'step':>8} {'train_acc':>10} {'test_acc':>10}", flush=True)
    for s, tr, te in zip(hist.steps, hist.train_acc, hist.eval_acc):
        print(f"{s:>8} {tr:>10.3f} {te:>10.3f}", flush=True)

    certified, details = certify_grokking(hist.steps, hist.train_acc, hist.eval_acc)
    print(f"\n[confirm] grokking certified: {certified}", flush=True)
    print(f"[confirm] {details}", flush=True)
    if not certified:
        print("[confirm] NOT grokked at these settings — adjust the recipe "
              "(steps/lr/weight_decay/train_frac), not the frozen thresholds.", flush=True)
    return certified, details


if __name__ == "__main__":
    steps = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1] else None
    device = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] else None
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    size = sys.argv[4] if len(sys.argv) > 4 else "1M"
    confirm(steps, device, seed, size)
