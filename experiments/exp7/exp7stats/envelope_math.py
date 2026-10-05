"""Strict envelope arithmetic from retained per-render target counts, no RNG."""
from fractions import Fraction as F
from functools import lru_cache
from exp7core.scoring import Table, Score
from exp7core.inference import mean
from exp7core.simulations import prompt_probabilities, expected_x, binomial_interval
from .common import require
from .saved_math import unpack, checked_bound


@lru_cache(maxsize=128)
def sample_summary(packed, n, families, pattern, delta):
    values = unpack(packed, n*families*8).reshape(n*families, 8)
    scores, minimum, histograms = [], [], [dict() for _ in range(4)]
    probabilities = [row for p in pattern for row in prompt_probabilities(*p[:2], p[2], delta)["rows"]]
    for row in values:
        row = [int(v) for v in row]
        score = Score(Table(*row[:4], 64), Table(*row[4:], 64))
        for j, probability in enumerate(probabilities):
            a, b = row[2*j:2*j+2]
            require(all(p != 0 or v == 0 for p, v in zip(probability, (a, b, 64-a-b))),
                    "saved count has zero categorical probability")
        scores.append(score)
        lower = []
        for table in (score.canonical, score.sham):
            k = table.n00+table.n10
            a = max(0, k-table.m1)
            lower.append(F(a,table.m0)-F(k-a,table.m1) if table.supported else F(0))
        minimum.append(mean(lower))
        for j, total in enumerate(score.row_totals):
            histograms[j][str(total)] = histograms[j].get(str(total), 0)+1
    return {"mean_x": mean([s.x for s in scores]), "mean_u": mean([s.u for s in scores]),
            "mean_d": mean([s.d for s in scores]), "unsupported": sum(s.unsupported for s in scores),
            "histograms": histograms, "minimum_mean_x": mean(minimum)}


def envelope_record(index, pattern, family_count, delta, spec, *, samples=None, mc=None):
    tables = [prompt_probabilities(*row[:2], row[2], delta) for row in pattern]
    base = {"id": f"E{index}/f{family_count}/delta{delta.numerator}_{delta.denominator}",
            "pattern": pattern, "families": family_count, "delta": delta, "probabilities": tables}
    if any(t["status"] != "SUPPORTED" for t in tables):
        require(samples is None and mc is None, "impossible envelope cell has samples")
        return {**base, "status": "UNSUPPORTED", "N": 0, "reason": "impossible conditional proportions; no clipping"}
    expected = mean([expected_x(row[0], row[1], delta, 64) for row in pattern])
    if all(row[0] == 0 or row[1] == 0 for row in pattern):
        require(samples is None and mc is None, "analytic envelope cell has samples")
        return {**base, "status": "ANALYTIC-ZERO-SUPPORT", "N": 0, "expected_x": expected,
                "p_fires": F(0), "p_only_probability": F(0), "mean_x": F(0),
                "unsupported_render_fraction": F(1), "note": "Structural zero, not an estimated zero pass rate."}
    nrep = spec.envelope_replicates
    require(type(samples) in (tuple, list) and type(mc) in (tuple, list) and len(samples) == len(mc) == nrep, "envelope count/MC trace coverage")
    rows = [sample_summary(v, spec.n, family_count, tuple(tuple(x) for x in pattern), delta) for v in samples]
    decisions = [checked_bound(bound, spec.permutations, all_ge=row["mean_x"] == row["minimum_mean_x"])
                 for row, bound in zip(rows, mc)]
    rejects = sum(d["reject"] for d in decisions)
    fires = sum(d["reject"] and row["mean_x"] >= F(1, 20) for d, row in zip(decisions, rows))
    hist = [dict() for _ in range(4)]
    for row in rows:
        for j, counts in enumerate(row["histograms"]):
            for value, count in counts.items():
                hist[j][value] = hist[j].get(value, 0)+count
    return {**base, "status": "SIMULATED", "N": nrep, "expected_x": expected,
            "score_counts": samples, "randomization_bounds": mc,
            "mean_x": mean([r["mean_x"] for r in rows]), "mean_d": mean([r["mean_d"] for r in rows]),
            "mean_u": mean([r["mean_u"] for r in rows]), "fire_count": fires, "p_fires": F(fires, nrep),
            "interval95": binomial_interval(fires, nrep), "p_only_count": rejects, "p_only_fraction": F(rejects, nrep),
            "p_only_interval95": binomial_interval(rejects, nrep),
            "unsupported_render_fraction": F(sum(r["unsupported"] for r in rows), nrep*spec.n*family_count*2),
            "target_row_histograms": hist, "note": "Finite-k support-penalized selectivity only, not joint power."}
