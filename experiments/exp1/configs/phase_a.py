"""Frozen Phase-A configuration (pipeline debug).

One place holding every knob for the Phase-A run so a RunRecord can serialize the
exact config that produced it. These are debug-grade values, not the scored
grokking/Lubana configs (those arrive in M4/M5 with their own frozen configs).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class PhaseAConfig:
    # data
    n_keys: int = 16
    n_values: int = 16
    edge_prob: float = 0.6
    n_pairs: int = 6
    n_train: int = 20_000
    n_eval: int = 2_000
    n_probe: int = 2_000

    # model
    d_model: int = 128
    n_layers: int = 2
    n_heads: int = 4

    # training
    total_steps: int = 4_000
    batch_size: int = 256
    lr: float = 1e-3
    weight_decay: float = 1.0
    n_checkpoints: int = 40
    device: str = "cpu"           # deterministic debug; M4+ move to MPS

    # signature params
    n_perm: int = 500             # S1 permutation null (debug-sized)
    alpha: float = 0.01
    s2_n_per_query: int = 2_000
    s2_n_queries: int = 25
    s2_temperature: float = 1.0
    # below-threshold rule for Phase A: argmax essentially at chance (< 2x chance).
    # Distinct from the frozen grokking rule (< 5%), because 16-way chance (6.25%)
    # already exceeds 5%. Documented in PROGRESS.md as a Phase-A-only choice.
    below_threshold_mult: float = 2.0
    s3_target_level: float = 0.6  # probe-accuracy crossing that defines the forecast

    def as_dict(self) -> dict:
        return asdict(self)
