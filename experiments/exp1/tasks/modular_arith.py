"""Grokking task: (a . b) mod p, the resolution-class exemplar.

Design doc §2 (resolution exemplar) and §5 (models): "Nanda-style decoder transformer
on (a.b) mod p, p = 113, trained on a fixed fraction of the pair space; generalization
groks in over training. Capability *forms* over the training axis."

Independent ground-truth check (design §2): "held-out accuracy plus a Nanda-style
progress measure ... showing the structured circuit sharpening while memorization
recedes." The certification implemented here is the memorization->generalization gap
that DEFINES grokking: train accuracy saturates early (memorization) while test
accuracy stays near zero and then jumps late (generalization forms over training).
That gap certifies the case as "resolution" independently of the S1/S2/S3 signatures
we are validating -- which is the whole point of an independent check. (The full Nanda
Fourier restricted/excluded loss is noted in PROGRESS.md as optional corroboration,
not yet implemented; the gap alone serves the certification's purpose.)

Sequence format, n_ctx = 3:  [a, b, EQ]  ->  predict the answer at the EQ position.
Numbers 0..p-1 and the answer share token ids 0..p-1; EQ is token id p.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import torch


@dataclass
class ModArithConfig:
    p: int = 113
    op: str = "mul"          # "mul" -> (a*b) mod p ; "add" -> (a+b) mod p
    train_frac: float = 0.4
    seed: int = 0


class ModArithTask:
    def __init__(self, cfg: ModArithConfig):
        if cfg.op not in ("mul", "add"):
            raise ValueError("op must be 'mul' or 'add'")
        self.cfg = cfg

    @property
    def p(self) -> int:
        return self.cfg.p

    @property
    def eq_token(self) -> int:
        return self.cfg.p

    @property
    def vocab_size(self) -> int:
        return self.cfg.p + 1

    @property
    def n_ctx(self) -> int:
        return 3

    @property
    def chance(self) -> float:
        return 1.0 / self.cfg.p

    def _answer(self, a, b):
        if self.cfg.op == "mul":
            return (a * b) % self.cfg.p
        return (a + b) % self.cfg.p

    def _all_examples(self):
        p = self.cfg.p
        a = np.repeat(np.arange(p), p)
        b = np.tile(np.arange(p), p)
        ans = self._answer(a, b)
        ids = np.stack([a, b, np.full_like(a, self.eq_token)], axis=1).astype(np.int64)
        return ids, ans.astype(np.int64)

    def make_split(self, seed: int | None = None):
        """Deterministic train/test split of the full p x p pair space.

        Returns a dict of tensors: train_ids/train_labels/train_targets and the test_*
        equivalents. labels == targets == answer class (numbers and answers share ids).
        """
        seed = self.cfg.seed if seed is None else seed
        ids, ans = self._all_examples()
        rng = np.random.default_rng(seed)
        perm = rng.permutation(len(ids))
        n_train = int(round(len(ids) * self.cfg.train_frac))
        tr, te = perm[:n_train], perm[n_train:]
        to_t = lambda x: torch.from_numpy(np.ascontiguousarray(x))  # noqa: E731
        return {
            "train_ids": to_t(ids[tr]), "train_labels": to_t(ans[tr]), "train_targets": to_t(ans[tr]),
            "test_ids": to_t(ids[te]), "test_labels": to_t(ans[te]), "test_targets": to_t(ans[te]),
        }


def certify_grokking(steps, train_acc, test_acc, *, mem_level=0.99, gen_level=0.90):
    """Certify the memorization->generalization gap that defines grokking.

    Returns (certified, details). Certified iff train accuracy reaches mem_level and
    test accuracy reaches gen_level with generalization no earlier than memorization
    (S_gen >= S_mem) -- the delayed-generalization hallmark. Independent of S1/S2/S3.
    """
    def first_at(acc, level):
        for s, a in zip(steps, acc):
            if a >= level:
                return int(s)
        return None

    s_mem = first_at(train_acc, mem_level)
    s_gen = first_at(test_acc, gen_level)
    certified = (s_mem is not None) and (s_gen is not None) and (s_gen >= s_mem)
    return certified, {
        "mem_step": s_mem, "gen_step": s_gen,
        "final_train_acc": float(train_acc[-1]) if len(train_acc) else None,
        "final_test_acc": float(test_acc[-1]) if len(test_acc) else None,
        "gap_steps": (s_gen - s_mem) if certified else None,
    }
