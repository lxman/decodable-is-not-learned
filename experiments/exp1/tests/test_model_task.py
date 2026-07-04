"""M3 unit tests for the model, Phase-A task, and checkpointing.

These pin the contracts the driver relies on (residual-hook shape, dataset validity,
closed-form threshold, checkpoint round-trip) before the end-to-end run.
"""

import math

import numpy as np
import torch

from models.transformer import DecoderTransformer, TransformerConfig, scale_to_param_budget
from tasks.binding_task import BindingTask, BindingTaskConfig
from train.checkpointing import checkpoint_schedule, list_checkpoints, load_checkpoint, save_checkpoint


# --- model ------------------------------------------------------------------

def test_model_forward_shape_and_blocks():
    cfg = TransformerConfig(vocab_size=33, n_ctx=14, d_model=64, n_layers=2, n_heads=4)
    model = DecoderTransformer(cfg)
    ids = torch.randint(0, 33, (5, 14))
    logits = model(ids)
    assert logits.shape == (5, 14, 33)
    assert len(model.blocks) == 2  # hookable residual layers for activations.py


def test_block_output_is_residual_stream_shape():
    """activations.py hooks blocks and reads their output as [B, T, d]."""
    cfg = TransformerConfig(vocab_size=20, n_ctx=8, d_model=32, n_layers=1)
    model = DecoderTransformer(cfg)
    captured = {}
    model.blocks[0].register_forward_hook(lambda m, i, o: captured.setdefault("o", o))
    model(torch.randint(0, 20, (3, 8)))
    assert captured["o"].shape == (3, 8, 32)


def test_causal_mask_blocks_future_positions():
    """Changing a later token must not change an earlier position's logits."""
    cfg = TransformerConfig(vocab_size=20, n_ctx=8, d_model=32, n_layers=1)
    model = DecoderTransformer(cfg).eval()
    a = torch.randint(0, 20, (1, 8))
    b = a.clone()
    b[0, -1] = (b[0, -1] + 1) % 20  # perturb only the last token
    with torch.no_grad():
        la = model(a)
        lb = model(b)
    assert torch.allclose(la[0, 0], lb[0, 0], atol=1e-5)   # first position unchanged
    assert not torch.allclose(la[0, -1], lb[0, -1])         # last position changes


def test_param_count_grows_with_size():
    small = DecoderTransformer(TransformerConfig(vocab_size=50, n_ctx=16, d_model=64, n_layers=1)).num_params()
    big = DecoderTransformer(TransformerConfig(vocab_size=50, n_ctx=16, d_model=256, n_layers=3)).num_params()
    assert big > small


def test_scale_to_param_budget_is_monotone_in_target():
    c1 = scale_to_param_budget(50, 16, 100_000)
    c2 = scale_to_param_budget(50, 16, 1_000_000)
    p1 = DecoderTransformer(c1).num_params()
    p2 = DecoderTransformer(c2).num_params()
    assert p2 > p1


# --- task -------------------------------------------------------------------

def test_dataset_shapes_and_ranges():
    task = BindingTask(BindingTaskConfig(n_keys=8, n_values=8, n_pairs=4, seed=0))
    ids, labels, targets = task.make_dataset(50, seed=1)
    assert ids.shape == (50, task.cfg.n_ctx)
    assert labels.shape == (50,) and targets.shape == (50,)
    assert ids.max().item() < task.cfg.vocab_size
    assert labels.min() >= 0 and labels.max() < task.cfg.n_values
    # target token is the value class shifted into the value range
    assert torch.equal(targets, labels + task.cfg.n_keys)


def test_query_marker_and_target_recoverable():
    task = BindingTask(BindingTaskConfig(n_keys=8, n_values=8, n_pairs=4, seed=0))
    ids, labels, targets = task.make_dataset(20, seed=2)
    # second-to-last token is the QUERY marker
    assert (ids[:, -2] == task.cfg.query_token).all()
    for i in range(20):
        assert task.value_class_of_token(int(targets[i])) == int(labels[i])


def test_dataset_is_deterministic_by_seed():
    task = BindingTask(BindingTaskConfig(seed=0))
    a = task.make_dataset(30, seed=5)[0]
    b = task.make_dataset(30, seed=5)[0]
    assert torch.equal(a, b)


def test_closed_form_percolation_threshold():
    task = BindingTask(BindingTaskConfig(n_keys=16, n_values=16))
    assert task.percolation_threshold() == 1.0 / math.sqrt(15 * 15)
    assert task.chance == 1.0 / 16


# --- checkpointing ----------------------------------------------------------

def test_checkpoint_schedule_log_spaced_includes_final():
    steps = checkpoint_schedule(4000, n_points=20)
    assert steps[0] >= 1
    assert steps[-1] == 4000
    assert steps == sorted(set(steps))
    # log spacing: earlier gaps smaller than later gaps
    assert steps[1] - steps[0] < steps[-1] - steps[-2]


def test_checkpoint_save_load_round_trip(tmp_path):
    cfg = TransformerConfig(vocab_size=20, n_ctx=8, d_model=32, n_layers=1)
    model = DecoderTransformer(cfg)
    save_checkpoint(model, 123, tmp_path, extra={"eval_acc": 0.42})
    found = list_checkpoints(tmp_path)
    assert found and found[0][0] == 123
    # mutate weights, then restore and confirm identity
    with torch.no_grad():
        for p in model.parameters():
            p.add_(1.0)
    step = load_checkpoint(model, found[0][1])
    assert step == 123
    fresh = DecoderTransformer(cfg)
    fresh_step = load_checkpoint(fresh, found[0][1])
    for p, q in zip(model.parameters(), fresh.parameters()):
        assert torch.allclose(p, q)
