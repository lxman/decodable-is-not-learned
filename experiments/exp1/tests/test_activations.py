"""M2 tests for residual-stream extraction.

Validated on a toy model whose intermediate values are known in closed form, so a
shape or token-selection bug can't hide behind a real transformer.
"""

import numpy as np
import torch
import torch.nn as nn

from signatures.activations import ResidualActivationCollector


class ToyModel(nn.Module):
    """Embed ids to width d, then two 'blocks' that each add a fixed constant.

    Block outputs (the residual stream) are therefore exactly predictable, so the
    collector's captured activations can be checked against ground truth.
    """

    def __init__(self, vocab=10, d=4):
        super().__init__()
        self.embed = nn.Embedding(vocab, d)
        self.block0 = nn.Identity()
        self.block1 = nn.Identity()
        with torch.no_grad():
            self.embed.weight.copy_(torch.arange(vocab * d, dtype=torch.float).reshape(vocab, d))

    def forward(self, ids):
        h = self.embed(ids)
        h = self.block0(h) + 1.0
        h = self.block1(h) + 10.0
        return h


def test_collect_shapes_and_values():
    model = ToyModel()
    ids = torch.tensor([[1, 2, 3], [4, 5, 6]])  # batch 2, seq 3
    with ResidualActivationCollector(model, [model.block0, model.block1], token_indices=(-1,)) as col:
        acts = col.collect([ids])

    # Two layers x one token position.
    assert set(acts.keys()) == {(0, -1), (1, -1)}
    for arr in acts.values():
        assert arr.shape == (2, 4)  # N=2 rows, d=4

    # block0 is Identity, so its captured output is the embedding of the last token
    # (before the +1 that happens AFTER the hooked module). Last tokens are ids 3 and 6.
    emb = model.embed.weight.detach().numpy()
    np.testing.assert_allclose(acts[(0, -1)], emb[[3, 6]])
    np.testing.assert_allclose(acts[(1, -1)], (emb + 1.0)[[3, 6]])


def test_multiple_token_indices_and_concat_across_batches():
    model = ToyModel()
    b1 = torch.tensor([[1, 2, 3]])
    b2 = torch.tensor([[4, 5, 6]])
    with ResidualActivationCollector(model, [model.block1], token_indices=(0, -1)) as col:
        acts = col.collect([b1, b2])
    assert set(acts.keys()) == {(0, 0), (0, -1)}
    # Concatenated across the two batches -> N=2.
    assert acts[(0, 0)].shape == (2, 4)
    emb = model.embed.weight.detach().numpy() + 1.0
    np.testing.assert_allclose(acts[(0, 0)], emb[[1, 4]])   # first tokens
    np.testing.assert_allclose(acts[(0, -1)], emb[[3, 6]])  # last tokens


def test_hooks_removed_on_context_exit():
    model = ToyModel()
    with ResidualActivationCollector(model, [model.block0]) as col:
        pass
    assert col._handles == []
    # A subsequent forward must not repopulate the capture buffer.
    col._captured.clear()
    model(torch.tensor([[1, 2, 3]]))
    assert col._captured == {}
