"""Record container for Experiment 1c's channel profiles.

One record per (system, arm, density, size, seed, trained/twin). Deliberately
separate from exp1's RunRecord and 1b's UntrainedRecord: both of those store a
SINGLE probe result — the argmax over candidates — and the argmax collapse is
the thing this experiment exists to stop doing. A 1c profile carries all 8
sites, unreduced, so the analysis can take a mean rather than inherit a
selection.

Nothing under experiments/exp1/ or experiments/exp1b/ is modified.

TWO ARMS, DIFFERENT SHAPES, both enforced here rather than trusted:

  fixed    the verdict-touching arm. n = 400, class-stratified at 40/class.
           Every site carries an UNCORRECTED permutation p; the Bonferroni
           family size is an analysis decision and lives in analyze_1c.
  natural  the diagnostic arm (design §4, verdict_touching: False). Natural
           pool size, margins only, NO null — which is the entire reason it
           costs 640 fits against the fixed arm's 9.6 M. A null appearing on
           this arm means the runner silently spent 10,000x its budget, so it
           is a hard error, not a warning.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

LAYERS = (0, 1, 2, 3)
TOKENS = (1, -1)
N_SITES = len(LAYERS) * len(TOKENS)
ARMS = ("fixed", "natural")
SYSTEMS = ("sweep", "lubana_above", "lubana_below")
SIZE_BUCKETS = ("1M", "10M")
# 0.25-0.85 are the sub-critical sweep; 0.50 is the scored lubana_below row
# (the consistency check) and 10.0 is lubana_above (the Stage A present row).
DENSITIES = (0.25, 0.45, 0.50, 0.65, 0.85, 10.0)


@dataclass
class SiteResult:
    layer: int
    token: int
    accuracy: float
    null_p_raw: float | None = None
    null_mean: float | None = None

    def __post_init__(self) -> None:
        if self.layer not in LAYERS:
            raise ValueError(f"layer must be one of {LAYERS}, got {self.layer!r}")
        if self.token not in TOKENS:
            raise ValueError(f"token must be one of {TOKENS}, got {self.token!r}")


@dataclass
class ProfileRecord:
    system: str
    arm: str
    density: float
    size_bucket: str
    seed: int
    trained: bool
    sites: list[SiteResult]
    n_rows: int
    n_val: int
    per_class: int | None
    capability_metric: float | None
    git_sha: str
    config: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.system not in SYSTEMS:
            raise ValueError(f"system must be one of {SYSTEMS}, got {self.system!r}")
        if self.arm not in ARMS:
            raise ValueError(f"arm must be one of {ARMS}, got {self.arm!r}")
        if self.size_bucket not in SIZE_BUCKETS:
            raise ValueError(
                f"size_bucket must be one of {SIZE_BUCKETS}, got "
                f"{self.size_bucket!r}")
        if not any(abs(float(self.density) - d) < 1e-9 for d in DENSITIES):
            raise ValueError(
                f"density {self.density!r} is not one the experiment ran "
                f"{DENSITIES}")

        if len(self.sites) != N_SITES:
            raise ValueError(
                f"a profile must carry all {N_SITES} sites — got "
                f"{len(self.sites)}")
        keys = [(s.layer, s.token) for s in self.sites]
        if len(set(keys)) != N_SITES:
            raise ValueError(f"duplicate sites in profile: {keys}")

        has_null = [s.null_p_raw is not None for s in self.sites]
        if self.arm == "fixed" and not all(has_null):
            raise ValueError(
                "the fixed arm is verdict-touching and every site must carry a "
                "permutation null — the two-gate rule is undefined without one")
        if self.arm == "natural" and any(has_null):
            raise ValueError(
                "the natural arm computes margins only and must carry no "
                "permutation null (design §4); a null here means the runner "
                "spent 10,000x the budgeted fits")

        if not self.trained and self.capability_metric is not None:
            raise ValueError(
                "an untrained twin has no capability metric — a number here "
                "would enter the 'capability stays flat' half of the hypothesis")

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_dict(cls, d: dict) -> "ProfileRecord":
        return cls(system=d["system"], arm=d["arm"], density=d["density"],
                   size_bucket=d["size_bucket"], seed=d["seed"],
                   trained=d["trained"],
                   sites=[SiteResult(**s) for s in d["sites"]],
                   n_rows=d["n_rows"], n_val=d["n_val"],
                   per_class=d.get("per_class"),
                   capability_metric=d.get("capability_metric"),
                   git_sha=d["git_sha"], config=d.get("config", {}))

    @classmethod
    def from_json(cls, s: str) -> "ProfileRecord":
        return cls.from_dict(json.loads(s))

    def save(self, path: str | Path) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.to_json())
        return path

    @classmethod
    def load(cls, path: str | Path) -> "ProfileRecord":
        return cls.from_json(Path(path).read_text())


def record_path(out_root: str | Path, system: str, arm: str, density: float,
                size: str, seed: int, trained: bool) -> Path:
    """The durable unit: one JSON per profile, resumable by existence."""
    kind = "trained" if trained else "twin"
    return (Path(out_root) / "results" / arm / system / f"p{density:g}" / size
            / f"seed{seed}_{kind}.json")
