"""Grokking configuration (the resolution row).

Design doc §5: Nanda-style decoder on (a.b) mod 113; base ~1 layer, d_model 128,
4 heads (<1M params). High weight decay + full-batch GD are the standard grokking
recipe (Nanda et al. 2023). These values are provisional until the grok-confirmation
run (open item: "Confirm the Nanda grokking config groks reliably at the base size
before scaling"); once confirmed they are frozen for the scored 5-seed run and the
M6 size sweep. Frozen values and the confirming run are recorded in PROGRESS.md.

The below-threshold rule here is the FROZEN §3 rule (argmax test acc < 5%), valid
because 113-way chance is ~0.88% << 5% (unlike Phase A's 16-way).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class GrokkingConfig:
    # task
    p: int = 113
    op: str = "mul"               # (a . b) mod 113
    train_frac: float = 0.4

    # model (base "1M" bucket; <1M params by design)
    d_model: int = 128
    n_layers: int = 1
    n_heads: int = 4

    # training (grokking recipe). Confirmed: seed 0 groks by ~step 1900 (mem @262,
    # gen @1578). total_steps frozen at 10k — captures pre-grok + the transition + a
    # stable plateau, and stops BEFORE the late weight-decay "slingshot" collapses the
    # 40k confirmation showed (steps ~16k and ~40k). The trajectory to 10k is identical
    # to the 40k run (no LR schedule); only the stop point moves. See PROGRESS.md.
    total_steps: int = 10_000
    full_batch: bool = True
    lr: float = 1e-3
    weight_decay: float = 1.0
    betas: tuple[float, float] = (0.9, 0.98)
    n_checkpoints: int = 60        # dense enough to place the sudden transition + precursor
    device: str = "mps"           # long run; MPS-validated for GPTNeoX fp forward passes

    # frozen §3/§4 signature params
    below_threshold_level: float = 0.05   # argmax test acc < 5%
    alpha: float = 0.01
    n_perm: int = 1000
    s2_n_per_query: int = 100_000
    s2_n_queries: int = 50
    s2_temperature: float = 1.0
    s3_target_level: float = 0.5          # probe-accuracy crossing defining the forecast

    size_bucket: str = "1M"

    def as_dict(self) -> dict:
        return asdict(self)
