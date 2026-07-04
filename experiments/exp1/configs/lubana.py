"""Lubana configuration (percolation ground-truth row + control row).

Two graph settings per design doc §2:
  - BELOW threshold: edge_prob = 0.5 * p_c  -> fragmented graph; the class structure
    is unrecoverable in principle; the scored capability can never form. Signatures
    predicted ABSENT, forever.
  - ABOVE threshold: edge_prob = 10 * p_c   -> giant component per class (the paper's
    base setting p=0.1 is ~40x its p_c; 10x keeps a robust giant component while
    staying comparable per scale). Capability forms over training. Signatures
    predicted PRESENT (the control row).

Scale: `scale="reduced"` is a structure-preserving reduction (|E|=300, |K|=3000,
|C|=10 -> per-class 30x300) of the paper's base (|E|=900, |K|=18000, |C|=10 ->
per-class 90x1800), analogous to the paper's own |K| sweep. `scale="paper"` is the
faithful base. The scored 5-seed runs use the scale recorded in PROGRESS.md before
launch; the reduction changes p_c but not the percolation structure.

Model/optimizer values are nanoGPT-style recipe choices (the paper's appendix tables
are not machine-readable via ar5iv; recorded as recipe, not thresholds).

Below-threshold rule (preregistered here, BEFORE any Lubana run): the frozen §3 rule
("argmax test acc < 5%") is unusable at 10-way chance (10%), exactly as in Phase A.
Rule used: argmax capability metric < 1.5 * chance. Logged in PROGRESS.md.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass


_SCALES = {
    "reduced": dict(n_classes=10, n_entities=300, n_properties=3000),
    "paper": dict(n_classes=10, n_entities=900, n_properties=18000),
}

BELOW_MULT = 0.5
ABOVE_MULT = 10.0


@dataclass(frozen=True)
class LubanaRunConfig:
    scale: str = "reduced"
    setting: str = "above"          # "above" | "below"

    # data
    n_train_sentences: int = 60_000
    n_queries: int = 500            # scored capability queries (held-out pairs)
    n_probe: int = 4000             # probe sentences for S1 activations

    # model (nanoGPT-small recipe)
    d_model: int = 256
    n_layers: int = 4
    n_heads: int = 8

    # training
    total_steps: int = 30_000
    batch_size: int = 64
    lr: float = 3e-4
    weight_decay: float = 0.1
    n_checkpoints: int = 50
    device: str = "mps"

    # signature params (instrument frozen post-M4; these mirror grokking where scale-free)
    alpha: float = 0.01
    n_perm: int = 1000
    below_threshold_mult: float = 1.5     # argmax metric < 1.5*chance  (preregistered)
    transition_level: float = 0.5         # capability metric crossing = the transition
    s2_n_per_query: int = 2_000
    s2_n_queries: int = 50
    s2_temperature: float = 1.0
    s3_target_level: float = 0.5
    s3_precursor_transform: str = "log"   # same frozen method as grokking
    # Graph-axis S3 for lubana_below (design §3: forecast attempted from below the
    # graph threshold). Per seed: dedicated sub-critical runs at these multiples of
    # p_c, each trained s3_graph_budget_steps, y = capability metric; forecast toward
    # the true transition at p_c. Preregistered before scored runs.
    s3_graph_points: tuple[float, ...] = (0.25, 0.45, 0.65, 0.85)
    s3_graph_budget_steps: int = 10_000

    @property
    def lang_kwargs(self) -> dict:
        kw = dict(_SCALES[self.scale])
        kw["edge_prob_mult"] = BELOW_MULT if self.setting == "below" else ABOVE_MULT
        return kw

    @property
    def system(self) -> str:
        return "lubana_below" if self.setting == "below" else "lubana_above"

    def as_dict(self) -> dict:
        return asdict(self)
