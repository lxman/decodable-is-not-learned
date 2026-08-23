"""Shared training loop.

Trains a DecoderTransformer to predict the answer token at the final sequence
position (next-token loss on the last position only -- the answer). At each scheduled
step it records argmax eval accuracy and saves a checkpoint, producing both the
argmax learning curve (whose jump defines the transition for S3) and the below-
threshold checkpoints S1/S2 read.

Reused by grokking (M4) and Lubana (M5); only the dataset and config differ.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import torch
import torch.nn.functional as F

from .checkpointing import checkpoint_schedule, save_checkpoint


@dataclass
class TrainConfig:
    total_steps: int = 4000
    batch_size: int = 256
    lr: float = 1e-3
    weight_decay: float = 1.0        # high WD is standard for grokking (Nanda); harmless here
    betas: tuple[float, float] = (0.9, 0.98)
    n_checkpoints: int = 40
    eval_batch: int = 2000
    device: str = "cpu"              # "cpu" | "mps" | "auto"
    full_batch: bool = False         # grokking uses full-batch GD (Nanda); Phase A minibatches
    seed: int = 0


def resolve_device(name: str) -> torch.device:
    if name == "auto":
        return torch.device("mps") if torch.backends.mps.is_available() else torch.device("cpu")
    return torch.device(name)


@torch.no_grad()
def eval_argmax_accuracy(model, ids, target_tokens, device, batch: int) -> float:
    model.eval()
    correct = 0
    n = ids.shape[0]
    for i in range(0, n, batch):
        chunk = ids[i : i + batch].to(device)
        logits = model(chunk)[:, -1, :]  # last position
        pred = logits.argmax(-1).cpu()
        correct += int((pred == target_tokens[i : i + batch]).sum())
    return correct / n


@dataclass
class TrainHistory:
    steps: list[int] = field(default_factory=list)
    eval_acc: list[float] = field(default_factory=list)
    train_acc: list[float] = field(default_factory=list)

    def transition_step(self, level: float = 0.5) -> int | None:
        """First checkpoint step whose eval argmax accuracy >= level (else None)."""
        for s, a in zip(self.steps, self.eval_acc):
            if a >= level:
                return s
        return None


def train(model, train_ids, train_targets, eval_ids, eval_targets, cfg: TrainConfig, ckpt_dir):
    """Train, checkpointing on the schedule. Returns TrainHistory.

    Loss/accuracy are on the final-position answer token. Records BOTH train and test
    argmax accuracy at each checkpoint (grokking's certification needs the
    memorization/generalization gap). full_batch=True does full-batch GD (grokking);
    otherwise seeded minibatches keep the run reproducible given (cfg.seed, data).
    """
    device = resolve_device(cfg.device)
    model.to(device)
    opt = torch.optim.AdamW(
        model.parameters(), lr=cfg.lr, weight_decay=cfg.weight_decay, betas=cfg.betas
    )
    gen = torch.Generator().manual_seed(cfg.seed)
    n_train = train_ids.shape[0]
    schedule = set(checkpoint_schedule(cfg.total_steps, cfg.n_checkpoints))
    hist = TrainHistory()

    if cfg.full_batch:
        fb_ids = train_ids.to(device)
        fb_tgt = train_targets.to(device)

    for step in range(1, cfg.total_steps + 1):
        model.train()
        if cfg.full_batch:
            ids, tgt = fb_ids, fb_tgt
        else:
            idx = torch.randint(0, n_train, (cfg.batch_size,), generator=gen)
            ids = train_ids[idx].to(device)
            tgt = train_targets[idx].to(device)
        logits = model(ids)[:, -1, :]
        loss = F.cross_entropy(logits, tgt)
        opt.zero_grad()
        loss.backward()
        opt.step()

        if step in schedule:
            eval_acc = eval_argmax_accuracy(model, eval_ids, eval_targets, device, cfg.eval_batch)
            train_acc = eval_argmax_accuracy(model, train_ids, train_targets, device, cfg.eval_batch)
            hist.steps.append(step)
            hist.eval_acc.append(eval_acc)
            hist.train_acc.append(train_acc)
            save_checkpoint(model, step, ckpt_dir, extra={"eval_acc": eval_acc, "train_acc": train_acc})

    return hist
