"""Minimal decoder transformer.

Built here for Experiment 1 and reused across the size sweep (M6) and, via the same
residual-hook contract, by Exp 2/4. Design doc §5: "Nanda-style decoder transformer
... Base config ~ 1 layer, d_model 128, 4 heads (< 1M params). Size sweep scales
depth/width to ~1M, 10M, 100M."

Contract with `signatures/activations.py`: each block's forward RETURNS the residual
stream after that block, and the blocks are exposed as `model.blocks` (a ModuleList),
so a collector hooks `list(model.blocks)` to read per-layer residuals. Do not change
what a block returns without updating the activation collector.
"""

from __future__ import annotations

from dataclasses import dataclass

import torch
import torch.nn as nn


@dataclass
class TransformerConfig:
    vocab_size: int
    n_ctx: int                     # max sequence length
    d_model: int = 128
    n_layers: int = 1
    n_heads: int = 4
    d_mlp: int | None = None       # defaults to 4 * d_model
    seed: int = 0

    @property
    def mlp_width(self) -> int:
        return self.d_mlp if self.d_mlp is not None else 4 * self.d_model


class Block(nn.Module):
    """Pre-norm attention + MLP. Returns the residual stream after the block."""

    def __init__(self, cfg: TransformerConfig):
        super().__init__()
        self.ln1 = nn.LayerNorm(cfg.d_model)
        self.attn = nn.MultiheadAttention(
            cfg.d_model, cfg.n_heads, batch_first=True, bias=True
        )
        self.ln2 = nn.LayerNorm(cfg.d_model)
        self.mlp = nn.Sequential(
            nn.Linear(cfg.d_model, cfg.mlp_width),
            nn.GELU(),
            nn.Linear(cfg.mlp_width, cfg.d_model),
        )

    def forward(self, x: torch.Tensor, attn_mask: torch.Tensor) -> torch.Tensor:
        h = self.ln1(x)
        a, _ = self.attn(h, h, h, attn_mask=attn_mask, need_weights=False)
        x = x + a
        x = x + self.mlp(self.ln2(x))
        return x


class DecoderTransformer(nn.Module):
    def __init__(self, cfg: TransformerConfig):
        super().__init__()
        torch.manual_seed(cfg.seed)
        self.cfg = cfg
        self.embed = nn.Embedding(cfg.vocab_size, cfg.d_model)
        self.pos = nn.Embedding(cfg.n_ctx, cfg.d_model)
        self.blocks = nn.ModuleList([Block(cfg) for _ in range(cfg.n_layers)])
        self.ln_f = nn.LayerNorm(cfg.d_model)
        self.unembed = nn.Linear(cfg.d_model, cfg.vocab_size, bias=False)

    def _causal_mask(self, t: int, device) -> torch.Tensor:
        # Additive float mask: 0 on/below diagonal, -inf above (future positions).
        return torch.triu(
            torch.full((t, t), float("-inf"), device=device), diagonal=1
        )

    def forward(self, ids: torch.Tensor) -> torch.Tensor:
        b, t = ids.shape
        if t > self.cfg.n_ctx:
            raise ValueError(f"sequence length {t} exceeds n_ctx {self.cfg.n_ctx}")
        pos_ids = torch.arange(t, device=ids.device)
        x = self.embed(ids) + self.pos(pos_ids)[None, :, :]
        mask = self._causal_mask(t, ids.device)
        for blk in self.blocks:
            x = blk(x, mask)
        return self.unembed(self.ln_f(x))  # logits [b, t, vocab]

    def num_params(self) -> int:
        return sum(p.numel() for p in self.parameters())


def scale_width_to_budget(
    vocab_size: int, n_ctx: int, target_params: int, *,
    n_layers: int, n_heads: int, seed: int = 0,
) -> TransformerConfig:
    """M6 scaling rule: hold a system's validated depth/heads FIXED, scale width only.

    `scale_to_param_budget` below walks depth-first and hands back degenerate
    architectures at large budgets (e.g. 1 layer x ~1550 wide for the Lubana vocab at
    100M) — a different architecture family than the one the confirmation gates
    validated. Width-only scaling keeps a single varying factor across the size sweep.
    Picks the d_model (multiple of n_heads) whose parameter count is nearest the
    target; buckets are order-of-magnitude, exactness is unnecessary.
    """
    def params_at(d_model: int) -> tuple[TransformerConfig, int]:
        cfg = TransformerConfig(
            vocab_size=vocab_size, n_ctx=n_ctx, d_model=d_model,
            n_layers=n_layers, n_heads=n_heads, seed=seed,
        )
        return cfg, DecoderTransformer(cfg).num_params()

    lo, hi = 1, 2  # in units of n_heads
    while params_at(hi * n_heads)[1] < target_params:
        lo, hi = hi, hi * 2
    while hi - lo > 1:  # params are monotone in width
        mid = (lo + hi) // 2
        if params_at(mid * n_heads)[1] < target_params:
            lo = mid
        else:
            hi = mid
    return min(
        (params_at(m * n_heads) for m in (lo, hi)),
        key=lambda t: abs(t[1] - target_params),
    )[0]


def scale_to_param_budget(
    vocab_size: int, n_ctx: int, target_params: int, *, n_heads: int = 4, seed: int = 0
) -> TransformerConfig:
    """Pick (n_layers, d_model) to land near target_params for the M6 size sweep.

    Coarse: walk depth 1->6 and widen d_model (a multiple of n_heads) until the
    parameter count first reaches the target. Exact matching is unnecessary — the
    design's size buckets are order-of-magnitude (1M/10M/100M).
    """
    best = None
    for n_layers in range(1, 7):
        for d_model in range(n_heads, 2048 + 1, n_heads):
            cfg = TransformerConfig(
                vocab_size=vocab_size, n_ctx=n_ctx, d_model=d_model,
                n_layers=n_layers, n_heads=n_heads, seed=seed,
            )
            p = DecoderTransformer(cfg).num_params()
            if best is None or abs(p - target_params) < abs(best[1] - target_params):
                best = (cfg, p)
            if p >= target_params:
                break
        if best and best[1] >= target_params:
            break
    return best[0]
