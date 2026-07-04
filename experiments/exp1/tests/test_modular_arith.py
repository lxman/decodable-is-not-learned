"""M4 unit tests for the modular-arithmetic (grokking) task and the grokking
certification. The full grokking behaviour is confirmed separately by the
grok-confirmation run (it is too long for the unit suite)."""

import numpy as np
import torch

from tasks.modular_arith import ModArithConfig, ModArithTask, certify_grokking


def test_full_pair_space_and_shapes():
    task = ModArithTask(ModArithConfig(p=113, op="mul", train_frac=0.4))
    d = task.make_split(seed=0)
    n = 113 * 113
    assert d["train_ids"].shape[0] + d["test_ids"].shape[0] == n
    assert d["train_ids"].shape[1] == 3
    assert task.vocab_size == 114 and task.eq_token == 113
    assert abs(task.chance - 1 / 113) < 1e-9


def test_answers_correct_mul():
    task = ModArithTask(ModArithConfig(p=113, op="mul"))
    d = task.make_split(seed=1)
    ids, ans = d["train_ids"], d["train_targets"]
    a, b = ids[:, 0], ids[:, 1]
    assert (ids[:, 2] == task.eq_token).all()
    assert torch.equal(ans, (a * b) % 113)


def test_answers_correct_add():
    task = ModArithTask(ModArithConfig(p=113, op="add"))
    d = task.make_split(seed=1)
    ids, ans = d["train_ids"], d["train_targets"]
    assert torch.equal(ans, (ids[:, 0] + ids[:, 1]) % 113)


def test_split_is_deterministic_and_disjoint():
    task = ModArithTask(ModArithConfig(train_frac=0.4))
    a = task.make_split(seed=7)
    b = task.make_split(seed=7)
    assert torch.equal(a["train_ids"], b["train_ids"])
    # train/test partition the pair space with no overlap
    def keyset(ids):
        return {(int(r[0]), int(r[1])) for r in ids}
    assert keyset(a["train_ids"]).isdisjoint(keyset(a["test_ids"]))


def test_train_frac_controls_size():
    small = ModArithTask(ModArithConfig(train_frac=0.3)).make_split(0)["train_ids"].shape[0]
    big = ModArithTask(ModArithConfig(train_frac=0.5)).make_split(0)["train_ids"].shape[0]
    assert big > small


# --- certification ----------------------------------------------------------

def test_certify_grokking_detects_delayed_generalization():
    steps = [1, 10, 100, 1000, 10000]
    train_acc = [0.2, 0.99, 1.0, 1.0, 1.0]     # memorizes early
    test_acc = [0.01, 0.01, 0.02, 0.1, 0.95]   # generalizes late
    cert, details = certify_grokking(steps, train_acc, test_acc)
    assert cert is True
    assert details["mem_step"] == 10 and details["gen_step"] == 10000
    assert details["gap_steps"] == 9990


def test_certify_rejects_no_generalization():
    steps = [1, 10, 100]
    cert, details = certify_grokking(steps, [0.99, 1.0, 1.0], [0.01, 0.01, 0.02])
    assert cert is False
    assert details["gen_step"] is None


def test_certify_rejects_generalization_before_memorization():
    # test crosses gen_level before train crosses mem_level -> not the grokking pattern
    steps = [1, 2, 3]
    cert, _ = certify_grokking(steps, [0.5, 0.5, 0.99], [0.95, 0.95, 0.95])
    assert cert is False
