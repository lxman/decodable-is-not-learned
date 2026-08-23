"""Language-model training loop for the Lubana task (M5).

Differences from train/loop.py (which the grokking runs depend on and which stays
untouched): the objective is next-token cross-entropy over ALL positions with PAD
ignored (the paper trains "a GPT architecture model with the standard autoregressive
language modeling objective"), and evaluation is a caller-supplied callback (the
masked-argmax class-generalization rate), since the capability is not a last-position
answer.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import torch
import torch.nn.functional as F

from .checkpointing import checkpoint_schedule, save_checkpoint
from .loop import resolve_device


@dataclass
class LMTrainConfig:
    total_steps: int = 30_000
    batch_size: int = 64
    lr: float = 3e-4
    weight_decay: float = 0.1
    betas: tuple[float, float] = (0.9, 0.95)
    n_checkpoints: int = 50
    device: str = "mps"
    seed: int = 0


@dataclass
class LMHistory:
    steps: list[int] = field(default_factory=list)
    eval_metric: list[float] = field(default_factory=list)   # capability metric
    train_loss: list[float] = field(default_factory=list)

    def transition_step(self, level: float) -> int | None:
        for s, a in zip(self.steps, self.eval_metric):
            if a >= level:
                return s
        return None


def train_lm(model, batch_fn, pad_token: int, eval_fn, cfg: LMTrainConfig, ckpt_dir):
    """Train with next-token CE (PAD ignored); checkpoint + eval_fn on the schedule.

    batch_fn(batch_size) -> [B, T] token rows (BOS + sentence + PAD...). TRUE ONLINE
    data, the paper's "fresh batch of strings every iteration": the caller closes over
    a seeded rng and generates fresh sentences per call. (A fixed-corpus variant was
    tried first and produced memorization collapse -- see PROGRESS.md M5 notes.)
    eval_fn(model) -> float: the capability metric at this checkpoint.
    """
    device = resolve_device(cfg.device)
    model.to(device)
    opt = torch.optim.AdamW(
        model.parameters(), lr=cfg.lr, weight_decay=cfg.weight_decay, betas=cfg.betas
    )
    schedule = set(checkpoint_schedule(cfg.total_steps, cfg.n_checkpoints))
    hist = LMHistory()

    for step in range(1, cfg.total_steps + 1):
        model.train()
        ids = batch_fn(cfg.batch_size).to(device)
        logits = model(ids)[:, :-1, :]
        targets = ids[:, 1:]
        loss = F.cross_entropy(
            logits.reshape(-1, logits.shape[-1]), targets.reshape(-1),
            ignore_index=pad_token,
        )
        opt.zero_grad()
        loss.backward()
        opt.step()

        if step in schedule:
            metric = float(eval_fn(model))
            hist.steps.append(step)
            hist.eval_metric.append(metric)
            hist.train_loss.append(float(loss.detach()))
            save_checkpoint(model, step, ckpt_dir,
                            extra={"eval_metric": metric, "train_loss": float(loss.detach())})

    return hist


@torch.no_grad()
def masked_argmax_class_rate(model, lang, queries: dict, device, batch: int = 256) -> float:
    """The scored capability metric: fraction of queries where the argmax over UNSEEN
    descriptive properties belongs to the subject's class. Chance ~ 1/|C|."""
    model.eval()
    prompts = queries["prompts"]
    masks = queries["masks"]
    n = prompts.shape[0]
    correct = 0
    for i in range(0, n, batch):
        p = prompts[i : i + batch].to(device)
        logits = model(p)[:, -1, :].float().cpu()
        logits[~masks[i : i + batch]] = float("-inf")
        choice = logits.argmax(-1)
        for j, tok in enumerate(choice.tolist()):
            if lang.verify_choice(i + j, queries, tok):
                correct += 1
    return correct / n
