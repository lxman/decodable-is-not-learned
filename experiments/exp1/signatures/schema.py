"""The frozen data contract: RunRecord and the three signature result types.

`analyze.py` depends ONLY on this schema, not on signature internals. That is the
decoupling the implementation plan calls for: probe/sampling/forecast logic can be
refined during Phase-A debugging, but once a result-grade run exists these shapes
are frozen and the analysis script is tagged against them.

Each signature module (probe.py, sampling.py, forecast.py) imports its result type
from here and returns an instance. One run of one (system, size, seed) produces one
RunRecord, serialized to results/<system>/<size>/<seed>.json.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field, fields, is_dataclass
from pathlib import Path

# Allowed categorical values, validated on construction so a typo can't quietly
# create a fourth "system" that analyze.py would drop from the truth table.
SYSTEMS = ("grokking", "lubana_below", "lubana_above", "phaseA")
SIZE_BUCKETS = ("1M", "10M", "100M", "phaseA")
AXES = ("training_steps", "graph_param")


@dataclass
class ProbeResult:
    """S1 — probeability below threshold."""

    present: bool
    accuracy: float
    chance: float
    null_p: float          # permutation p, Bonferroni-corrected across layers
    null_mean: float
    ci95: tuple[float, float]
    best_layer: int
    best_token: int
    n_layers_tested: int
    checkpoint_id: str
    below_threshold: bool
    signature: str = "S1"


@dataclass
class SamplingResult:
    """S2 — elicitability by exhaustive sampling."""

    present: bool
    absent: bool
    passes: int
    n: int
    rate_point: float
    cp_lower: float
    cp_upper: float        # ALWAYS a number; the "never a claimed zero" guarantee
    guessing_floor: float
    argmax_fails: bool
    checkpoint_id: str
    signature: str = "S2"


@dataclass
class ForecastResult:
    """S3 — forecastability from below."""

    present: bool
    predicted_transition: float
    true_transition: float
    interval90: tuple[float, float]
    rel_error: float
    slope_ci: tuple[float, float]
    beats_no_transition_baseline: bool
    axis: str              # one of AXES
    signature: str = "S3"


@dataclass
class GTCheck:
    """Independent ground-truth certification that a run is the class it claims.

    Class membership must NOT rest on the signatures we are validating (design §2):
    grokking is certified by held-out accuracy + Nanda restricted/excluded loss;
    Lubana by the graph-predicted percolation threshold. `details` holds the
    task-specific numbers; `certified` is the decidable verdict.
    """

    certified: bool
    method: str
    details: dict = field(default_factory=dict)


@dataclass
class RunRecord:
    """One (system, size, seed) run. The unit analyze.py globs and pools."""

    system: str
    size_bucket: str
    seed: int
    git_sha: str
    torch_version: str
    transformers_version: str
    gt_check: GTCheck
    s1: ProbeResult
    s2: SamplingResult
    s3: ForecastResult
    config: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.system not in SYSTEMS:
            raise ValueError(f"system must be one of {SYSTEMS}, got {self.system!r}")
        if self.size_bucket not in SIZE_BUCKETS:
            raise ValueError(f"size_bucket must be one of {SIZE_BUCKETS}, got {self.size_bucket!r}")
        if self.s3.axis not in AXES:
            raise ValueError(f"s3.axis must be one of {AXES}, got {self.s3.axis!r}")

    # ---- serialization ------------------------------------------------------
    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_dict(cls, d: dict) -> "RunRecord":
        return cls(
            system=d["system"],
            size_bucket=d["size_bucket"],
            seed=d["seed"],
            git_sha=d["git_sha"],
            torch_version=d["torch_version"],
            transformers_version=d["transformers_version"],
            gt_check=_build(GTCheck, d["gt_check"]),
            s1=_build(ProbeResult, d["s1"]),
            s2=_build(SamplingResult, d["s2"]),
            s3=_build(ForecastResult, d["s3"]),
            config=d.get("config", {}),
        )

    @classmethod
    def from_json(cls, s: str) -> "RunRecord":
        return cls.from_dict(json.loads(s))

    def save(self, path: str | Path) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.to_json())
        return path

    @classmethod
    def load(cls, path: str | Path) -> "RunRecord":
        return cls.from_json(Path(path).read_text())


def _build(dc_type, d: dict):
    """Reconstruct a flat dataclass from a dict, coercing list->tuple for tuple fields.

    JSON has no tuples, so ci95/interval90/slope_ci round-trip as lists; coerce them
    back so equality with the original dataclass holds.
    """
    kwargs = {}
    for f in fields(dc_type):
        if f.name not in d:
            continue  # let the dataclass default apply
        val = d[f.name]
        if isinstance(val, list) and _is_tuple_field(f.type):
            val = tuple(val)
        kwargs[f.name] = val
    return dc_type(**kwargs)


def _is_tuple_field(type_hint) -> bool:
    # Fields are annotated as tuple[...] (a string under `from __future__ import
    # annotations`); a substring check is enough for this frozen, known schema.
    return "tuple" in str(type_hint)


__all__ = [
    "SYSTEMS",
    "SIZE_BUCKETS",
    "AXES",
    "ProbeResult",
    "SamplingResult",
    "ForecastResult",
    "GTCheck",
    "RunRecord",
]
