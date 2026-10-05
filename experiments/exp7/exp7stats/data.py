"""Independent strict analysis contract: derive all scores from raw strings."""
from dataclasses import dataclass
from fractions import Fraction as F
from exp7core.scoring import answer, score_draws, outcome_counts, Score, Table
from exp7core.strata import availability_buckets
from exp7core.inference import Cell
from .common import ARMS, FAMILIES, PREDICTORS, require, pin, digest, PRODUCTION


@dataclass(frozen=True)
class Pair:
    id: str
    index: int
    targets: tuple
    kind: str
    base: str
    prompts: tuple
    baselines: tuple


@dataclass(frozen=True)
class Baseline:
    status: str
    na_reason: object
    outputs: object
    abstained: object


@dataclass(frozen=True)
class Battery:
    families: tuple
    sha256: str
    certificate_sha256: str
    levels_sha256: str
    baseline_coverage: tuple

    def family(self, name):
        return dict(self.families)[name]


@dataclass(frozen=True)
class Predictor:
    name: str
    raw: tuple
    scores: tuple
    strata: tuple
    partitions: tuple

    def family(self, name):
        return dict(self.scores)[name]


def keys(value, wanted, label):
    require(type(value) is dict and set(value) == set(wanted), f"{label} keys")


def load_battery(payload, shape=PRODUCTION):
    keys(payload, ("schema", "sha256", "certificate_sha256", "levels_sha256", "baseline_ids", "baseline_coverage", "families"), "battery")
    require(payload["schema"] == "exp7.analysis-battery.v1", "battery schema")
    for name in ("sha256", "certificate_sha256", "levels_sha256"):
        pin(payload[name])
    keys(payload["families"], FAMILIES, "battery family")
    keys(payload["baseline_ids"], FAMILIES, "baseline family")
    result, ids, prompts, baseline_cells = [], set(), set(), {}
    for f in FAMILIES:
        baseline_ids = payload["baseline_ids"][f]
        require(type(baseline_ids) in (list, tuple) and baseline_ids
                and len(set(baseline_ids)) == len(baseline_ids)
                and all(type(v) is str and v for v in baseline_ids), "baseline IDs")
        if shape == PRODUCTION:
            require(len(baseline_ids) == 21, f"baseline_missing: {f}: baseline catalog coverage requires exactly21 cells")
        rows = payload["families"][f]
        require(type(rows) in (list, tuple) and len(rows) == shape.n, "battery family coverage")
        pairs = []
        for i, row in enumerate(rows):
            keys(row, ("id", "index", "targets", "answer_type", "base", "prompts_sha256", "baselines"), "pair")
            require(type(row["index"]) is int and row["index"] == i and row["id"] == f"{f}:{i:04d}", "pair order/identity")
            require(row["id"] not in ids, "duplicate pair")
            ids.add(row["id"])
            require(type(row["targets"]) in (tuple, list) and len(row["targets"]) == 2, "targets")
            targets = tuple(row["targets"])
            a = tuple(answer(v, row["answer_type"]) for v in targets)
            require(a[0] != a[1], "normalized target collision")
            require(type(row["base"]) is str and row["base"], "tagged base ID")
            keys(row["prompts_sha256"], ARMS, "prompt pins")
            ps = tuple(pin(row["prompts_sha256"][arm]) for arm in ARMS)
            require(len(set(ps)) == 4 and not set(ps) & prompts, "duplicate prompt hash")
            prompts.update(ps)
            require(type(row["baselines"]) is dict, "baseline_missing: missing catalog mapping")
            missing = sorted(set(baseline_ids)-set(row["baselines"]))
            require(not missing, f"baseline_missing: {row['id']}: {missing}")
            keys(row["baselines"], baseline_ids, "baseline coverage")
            bs = []
            for name in sorted(baseline_ids):
                value = row["baselines"][name]
                keys(value, ("status", "na_reason", "outputs", "abstained"), "baseline applicability")
                require(value["status"] in ("APPLICABLE", "NOT_APPLICABLE"), "explicit baseline applicability")
                identity = (value["status"], value["na_reason"])
                if (f, name) in baseline_cells:
                    require(baseline_cells[(f, name)] == identity, "baseline cell applicability changes across pairs")
                else:
                    baseline_cells[(f, name)] = identity
                if value["status"] == "NOT_APPLICABLE":
                    require(type(value["na_reason"]) is str and value["na_reason"].strip()
                            and value["outputs"] is None and value["abstained"] is None, "N/A reason/output contract")
                    baseline = Baseline("NOT_APPLICABLE", value["na_reason"], None, None)
                else:
                    require(value["na_reason"] is None, "applicable baseline has N/A reason")
                    keys(value["outputs"], ARMS, "baseline raw arms")
                    keys(value["abstained"], ARMS, "baseline abstention metadata")
                    outputs = tuple(value["outputs"][arm] for arm in ARMS)
                    abstained = tuple(value["abstained"][arm] for arm in ARMS)
                    require(all(type(s) is str for s in outputs), "baseline raw strings")
                    require(all(type(v) is bool for v in abstained), "baseline abstention flags")
                    require(all(not flag or output == "" for flag, output in zip(abstained, outputs)),
                            "abstention must be empty-string MISS with preserved metadata")
                    baseline = Baseline("APPLICABLE", None, outputs, abstained)
                bs.append((name, baseline))
            pairs.append(Pair(row["id"], i, targets, row["answer_type"], row["base"], ps, tuple(bs)))
        result.append((f, tuple(pairs)))
    coverage = {"applicable_cells": sum(v[0] == "APPLICABLE" for v in baseline_cells.values()),
                "not_applicable_cells": sum(v[0] == "NOT_APPLICABLE" for v in baseline_cells.values())}
    keys(payload["baseline_coverage"], coverage, "baseline coverage")
    require(all(type(payload["baseline_coverage"][k]) is int and payload["baseline_coverage"][k] == v
                for k, v in coverage.items()), "baseline applicability denominator mismatch")
    if shape == PRODUCTION:
        require(coverage == {"applicable_cells": 49, "not_applicable_cells": 35},
                "certified 49 applicable +35 N/A baseline cells required")
    return Battery(tuple(result), payload["sha256"], payload["certificate_sha256"], payload["levels_sha256"], tuple(coverage.items()))


def load_one_predictor(payload, battery, name, k, shape=PRODUCTION):
    keys(payload, FAMILIES, "predictor families")
    raw, scores, strata, partitions = [], [], [], []
    for f in FAMILIES:
        rows, pairs = payload[f], battery.family(f)
        require(type(rows) in (tuple, list) and len(rows) == shape.n, "predictor row coverage")
        fr, fs = [], []
        for row, pair in zip(rows, pairs):
            keys(row, ("id", "draws"), "predictor row")
            require(row["id"] == pair.id, "predictor row order")
            keys(row["draws"], ARMS, "predictor four arms")
            draws = row["draws"]
            score = score_draws(draws, pair.targets, pair.kind, k=k)
            fr.append(tuple(tuple(draws[a]) for a in ARMS))
            fs.append(score)
        base = tuple(p.base for p in pairs)
        parts = {}
        for label, number in (("base", 1), ("median", 2), ("tercile", 3)):
            labs, report = availability_buckets(base, tuple(s.u for s in fs), parts=number)
            parts[label] = (labs, report)
        raw.append((f, tuple(fr)))
        scores.append((f, tuple(fs)))
        strata.append((f, parts["median"][0]))
        partitions.append((f, parts))
    return Predictor(name, tuple(raw), tuple(scores), tuple(strata), tuple(partitions))


def load_predictors(payload, battery, shape=PRODUCTION):
    keys(payload, ("schema", "trained", "twin"), "predictors")
    require(payload["schema"] == "exp7.analysis-predictors.v1", "predictor schema")
    keys(payload["trained"], PREDICTORS, "trained predictors")
    out = {p: load_one_predictor(payload["trained"][p], battery, p, 64, shape) for p in PREDICTORS}
    out["twin"] = load_one_predictor(payload["twin"], battery, "twin", 16, shape)
    return out


def load_outcomes(payload, battery, shape=PRODUCTION):
    keys(payload, ("schema", "grid", "families"), "outcomes")
    require(payload["schema"] == "exp7.analysis-outcomes.v1" and
            tuple(payload["grid"]) == shape.grid and
            all(type(x) is int for x in payload["grid"]), "exact outcome grid")
    keys(payload["families"], FAMILIES, "outcome families")
    out = {}
    for f in FAMILIES:
        rows, pairs = payload["families"][f], battery.family(f)
        require(type(rows) in (tuple, list) and len(rows) == shape.n, "outcome rows")
        got = []
        for row, pair in zip(rows, pairs):
            keys(row, ("id", "outputs"), "outcome row")
            require(row["id"] == pair.id, "outcome row order")
            keys(row["outputs"], tuple(str(v) for v in shape.grid), "outcome step coverage")
            values = {step: row["outputs"][str(step)] for step in shape.grid}
            stats = outcome_counts(values, pair.targets, pair.kind, steps=shape.grid)
            got.append({**stats, "raw": tuple(tuple(values[t][a] for a in ARMS) for t in shape.grid)})
        out[f] = tuple(got)
    return out


def cells(predictor, outcomes, battery, *, partition="median", outcome="y", scores=None):
    source = dict(predictor.scores) if scores is None else scores
    return tuple(Cell(f, tuple(p.id for p in battery.family(f)), tuple(source[f]),
                      tuple(o[outcome] for o in outcomes[f]),
                      tuple(dict(predictor.partitions)[f][partition][0])) for f in FAMILIES)


def score_slice(predictor, battery, start, stop):
    require(0 <= start < stop <= len(dict(predictor.raw)[FAMILIES[0]][0][0]), "draw slice")
    return {f: tuple(score_draws({a: row[j][start:stop] for j, a in enumerate(ARMS)},
                                pair.targets, pair.kind, k=stop-start)
                     for row, pair in zip(dict(predictor.raw)[f], battery.family(f))) for f in FAMILIES}


def predictor_support(predictor):
    from collections import Counter
    from exp7core.inference import mean, groups
    out = {}
    for f, scores in predictor.scores:
        strata = dict(predictor.strata)[f]
        out[f] = {"n": len(scores), "unique_x": len({s.x for s in scores}),
                  "x_tie_sizes": sorted(Counter(s.x for s in scores).values(), reverse=True),
                  "mean_u": mean([s.u for s in scores]),
                  "unsupported_renders": sum(s.unsupported for s in scores),
                  "row_totals": [s.row_totals for s in scores],
                  "blocks": [{"n": len(ix), "unique_x": len({scores[i].x for i in ix})}
                             for ix in groups(strata)]}
    return out


def baseline_score(pair, value):
    require(isinstance(value, Baseline) and value.status == "APPLICABLE", "cannot score an N/A baseline")
    return score_draws({a: [value.outputs[j]] for j, a in enumerate(ARMS)}, pair.targets, pair.kind, k=1)
