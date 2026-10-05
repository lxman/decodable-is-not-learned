"""Shared pair-bundle bootstrap for every descriptive and paired difference."""
from dataclasses import dataclass
from fractions import Fraction as F
from exp7core.inference import mean
from exp7core.resampling import bundle_indices, interval, paired_difference
from .common import require
from .kernels import somers


@dataclass(frozen=True)
class Metric:
    families: tuple
    x: dict
    y: dict
    strata: dict

    def __post_init__(self):
        require(len(set(self.families)) == len(self.families), "metric family set")
        for f in self.families:
            require(f in self.x and f in self.y and f in self.strata, "metric family missing")
            require(len(self.x[f]) == len(self.y[f]) == len(self.strata[f]) > 0, "metric lengths")

    def evaluate(self, indices=None):
        if not self.families:
            return {"T": None, "mean": None, "families": (), "per_family": {},
                    "reason": "empty eligible set"}
        per, means = {}, []
        for f in self.families:
            ix = range(len(self.x[f])) if indices is None else indices[f]
            x = tuple(self.x[f][i] for i in ix)
            y = tuple(self.y[f][i] for i in ix)
            s = tuple(self.strata[f][i] for i in ix)
            per[f] = somers(x, y, s)
            means.append(mean(x))
        defined = all(v["D"] is not None for v in per.values())
        return {"T": mean([v["D"] for v in per.values()]) if defined else None,
                "mean": mean(means), "families": self.families, "per_family": per,
                "reason": None if defined else "outcome-uninformative required family"}


def run(metrics, family_sizes, *, B, namespace):
    require(type(metrics) is dict and metrics and all(isinstance(m, Metric) for m in metrics.values()),
            "bootstrap metrics")
    samples = {name: {"T": [], "mean": []} for name in metrics}
    for indices in bundle_indices(family_sizes, B=B, namespace=namespace):
        for name, metric in metrics.items():
            result = metric.evaluate(indices)
            for key in ("T", "mean"):
                samples[name][key].append(result[key])
    summaries = {}
    for name, metric in metrics.items():
        summaries[name] = {**metric.evaluate(), "bootstrap": {
            key: interval(values) for key, values in samples[name].items()},
            "bootstrap_note": "Fixed eligible families/strata; whole shared pair bundles; undefined counted."}
    return summaries, samples


def difference(summaries, samples, left, right, *, key="T"):
    a, b = summaries[left][key], summaries[right][key]
    return {"left": left, "right": right, "quantity": key,
            "difference": a-b if a is not None and b is not None else None,
            "bootstrap": paired_difference(samples[left][key], samples[right][key]),
            "left_families": summaries[left]["families"],
            "right_families": summaries[right]["families"]}
