"""Residual-stream activation extraction for S1 (the probe).

Design doc §3, S1: "Train a linear probe on frozen residual-stream activations ...
Layer and token position selected on a validation split."

This module turns a model + a fixed probe dataset into the `{(layer, token): array}`
map that `probe.probe_below_threshold` consumes. It is deliberately model-agnostic:
it hooks whatever modules the caller declares to be the per-layer residual stream
(for our minimal decoder, that's each block's output), so the same collector serves
Exp 1's custom transformer and, later, HF models in Exp 2/4.

Storage note (implementation plan §5): we hook and read activations on demand from a
fixed probe set rather than caching activations to disk. Only model checkpoints are
persisted; activations are recomputed at analysis time. This bounds `checkpoints/`.
"""

from __future__ import annotations

import numpy as np
import torch


class ResidualActivationCollector:
    """Capture per-layer residual-stream activations at chosen token positions.

    Parameters
    ----------
    model : torch.nn.Module
        Model to run in eval/no-grad mode.
    layer_modules : list[torch.nn.Module]
        The submodules whose *output* is the residual stream after each layer, in
        depth order. Index i in the returned keys corresponds to layer_modules[i].
    token_indices : tuple[int, ...]
        Sequence positions to read (e.g. (-1,) for the answer/last token). Negative
        indices count from the end, as in Python/torch.

    Use as a context manager so hooks are always removed::

        with ResidualActivationCollector(model, blocks, token_indices=(-1,)) as col:
            acts = col.collect(batches)   # {(layer, token): np.ndarray[N, d]}
    """

    def __init__(self, model, layer_modules, token_indices=(-1,), device=None):
        if not layer_modules:
            raise ValueError("layer_modules must be non-empty")
        self.model = model
        self.layer_modules = list(layer_modules)
        self.token_indices = tuple(token_indices)
        self.device = device
        self._handles: list = []
        self._captured: dict[int, torch.Tensor] = {}

    def __enter__(self) -> "ResidualActivationCollector":
        for layer_idx, module in enumerate(self.layer_modules):
            self._handles.append(module.register_forward_hook(self._make_hook(layer_idx)))
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    def close(self) -> None:
        for h in self._handles:
            h.remove()
        self._handles.clear()

    def _make_hook(self, layer_idx: int):
        def hook(_module, _inputs, output):
            # Blocks may return the residual tensor directly or a tuple whose first
            # element is it (GPTNeoX-style). Normalize to the tensor.
            tensor = output[0] if isinstance(output, tuple) else output
            self._captured[layer_idx] = tensor.detach()
        return hook

    @torch.no_grad()
    def collect(self, batches, forward_fn=None) -> dict[tuple[int, int], np.ndarray]:
        """Run `batches` through the model, return {(layer, token): [N, d]} arrays.

        `batches` is any iterable of model inputs (e.g. batched input_id tensors).
        `forward_fn(batch)` runs the model; defaults to `self.model(batch)`. The
        return value of forward_fn is ignored — activations come from the hooks.
        """
        if forward_fn is None:
            forward_fn = lambda b: self.model(b)  # noqa: E731
        self.model.eval()

        # {(layer, token): [list of per-batch [b, d] arrays]}
        buffers: dict[tuple[int, int], list[np.ndarray]] = {
            (layer_idx, tok): []
            for layer_idx in range(len(self.layer_modules))
            for tok in self.token_indices
        }

        for batch in batches:
            if self.device is not None and hasattr(batch, "to"):
                batch = batch.to(self.device)
            self._captured.clear()
            forward_fn(batch)
            if len(self._captured) != len(self.layer_modules):
                raise RuntimeError(
                    "not every declared layer fired a hook; check layer_modules "
                    "matches the model's forward path"
                )
            for layer_idx, tensor in self._captured.items():
                # tensor: [batch, seq, d]
                for tok in self.token_indices:
                    sel = tensor[:, tok, :]  # [batch, d]
                    buffers[(layer_idx, tok)].append(sel.float().cpu().numpy())

        return {key: np.concatenate(chunks, axis=0) for key, chunks in buffers.items()}
