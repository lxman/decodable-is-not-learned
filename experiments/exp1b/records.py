"""Record container for Exp 1b's untrained-control cells.

Deliberately separate from exp1's RunRecord: that type mandates
SamplingResult and ForecastResult values, which a probe-only cell on a
randomly initialized network has no meaningful value for, and its SYSTEMS
tuple is frozen under the exp1 tag. Exp 1b does not modify exp1.

One record per untrained TWIN — matched to its trained cell's system,
size, seed, architecture, probe data and labels (design §3, amended
2026-08-12). The twin tests the probe that was actually run, not a probe
nobody ran.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

from experiments.exp1.signatures.schema import ProbeResult, _build

UNTRAINED_SYSTEMS = ("grokking", "lubana_above", "lubana_below")
SIZE_BUCKETS = ("1M", "10M")


@dataclass
class UntrainedRecord:
    system: str
    size_bucket: str
    seed: int
    git_sha: str
    s1: ProbeResult
    config: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.system not in UNTRAINED_SYSTEMS:
            raise ValueError(
                f"system must be one of {UNTRAINED_SYSTEMS}, got "
                f"{self.system!r}")
        if self.size_bucket not in SIZE_BUCKETS:
            raise ValueError(
                f"size_bucket must be one of {SIZE_BUCKETS}, got "
                f"{self.size_bucket!r}")

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_dict(cls, d: dict) -> "UntrainedRecord":
        return cls(system=d["system"], size_bucket=d["size_bucket"],
                   seed=d["seed"], git_sha=d["git_sha"],
                   s1=_build(ProbeResult, d["s1"]), config=d.get("config", {}))

    @classmethod
    def from_json(cls, s: str) -> "UntrainedRecord":
        return cls.from_dict(json.loads(s))

    def save(self, path: str | Path) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.to_json())
        return path

    @classmethod
    def load(cls, path: str | Path) -> "UntrainedRecord":
        return cls.from_json(Path(path).read_text())
