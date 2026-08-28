# experiments/exp2j/functionals_2j.py
"""The four item functionals of design §5.1, the bucket rule and
composite-strata builder of §5.2, and the density-matched block
thinner of §5.4. Pure functions over 2c/2b item files ("caps") and
committed draw rows in 2d's row format. Zero model contact.

Normalization is 2c's `harness.normalize_answer` — the same function
`load_verify_3c` applies on both sides of the verify criterion — and
the draw side mirrors 3c's total wrapper (`IndexError -> None`, a
value no normalized answer can equal). `test_functionals_2j` proves
the π predicate equals `verify_fn(draw, a_i, answer_type)` on the
real committed draws."""
from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

import numpy as np

EXP2J = Path(__file__).resolve().parent
if str(EXP2J.parent.parent) not in sys.path:
    sys.path.insert(0, str(EXP2J.parent.parent))

from experiments.exp2c import harness  # noqa: E402
from experiments.exp2d import analyze_2d as a2d  # noqa: E402
from experiments.exp2i import battery_2i as bi  # noqa: E402

FUNCTIONALS = ("pi", "L", "R", "O")
LADDER = (1, 2, 4, 8, 16, 32, 64)
DRAWS_PER_ITEM = bi.DRAWS_PER_ITEM      # 64
SEED = bi.SAMPLING_SEED                 # 0
N_ITEMS = bi.N_ITEMS                    # 500


# ------------------------------------------------------------ normalizing

def normalized_answers(cap) -> list:
    at = cap["answer_type"]
    return [harness.normalize_answer(str(it["answer"]), at) for it in cap["eval_items"]]


def normalized_draw(d, answer_type):
    """verify_3c's draw side, verbatim in spirit: a draw the normalizer
    cannot parse is never a match (None), never an exception."""
    try:
        return harness.normalize_answer(str(d), answer_type)
    except IndexError:
        return None


# -------------------------------------------------------------- draw rows

def draw_rows_2i(root, rung) -> list:
    return a2d.read_rows(bi.predictor_draws_path(root, rung), seed=SEED,
                         dps=DRAWS_PER_ITEM, n_items=N_ITEMS)


def draw_rows_2d(size, rung) -> list:
    return a2d.read_rows(a2d.tier_draws_path(a2d.EXP2D, "main", size, rung), seed=SEED,
                         dps=DRAWS_PER_ITEM, n_items=N_ITEMS)


def verified_bits(rows, cap, verify_fn) -> list:
    """500 × 64 bit vectors in the committed draw order; summing a row
    reproduces `sampler_counts_*`'s count exactly (tested)."""
    bits = [None] * N_ITEMS
    at = cap["answer_type"]
    for row in rows:
        ans = cap["eval_items"][row["item"]]["answer"]
        bits[row["item"]] = [int(bool(verify_fn(d, ans, at)))
                             for d in row["draws"][str(SEED)]]
    if any(b is None for b in bits):
        raise ValueError("verified_bits: coverage incomplete")
    return bits


def counts_from_bits(bits) -> list:
    return [int(sum(b)) for b in bits]


# ------------------------------------------------------------ functionals

def wrong_target_propensity(rows, cap, *, loo=False) -> list:
    """π_i (design §5.1, dial d): among all committed draws of the
    predictor on items j whose normalized answer differs from a_i, the
    fraction whose normalized output equals a_i — the rate at which
    the model says a_i when a_i is WRONG. `loo=True` is the §5.6
    sensitivity: every j ≠ i counts, same-answer items included."""
    ans = normalized_answers(cap)
    at = cap["answer_type"]
    per_item = [None] * N_ITEMS
    for row in rows:
        per_item[row["item"]] = Counter(normalized_draw(d, at)
                                        for d in row["draws"][str(SEED)])
    if any(c is None for c in per_item):
        raise ValueError("wrong_target_propensity: coverage incomplete")
    total = Counter()
    by_answer = {}
    for i, c in enumerate(per_item):
        total.update(c)
        acc = by_answer.setdefault(ans[i], [Counter(), 0])
        acc[0].update(c)
        acc[1] += DRAWS_PER_ITEM
    n_total = N_ITEMS * DRAWS_PER_ITEM
    out = []
    for i in range(N_ITEMS):
        a = ans[i]
        if loo:
            num, den = total[a] - per_item[i][a], n_total - DRAWS_PER_ITEM
        else:
            num, den = total[a] - by_answer[a][0][a], n_total - by_answer[a][1]
        out.append(float(num) / den if den > 0 else 0.0)
    return out


def answer_length(cap) -> list:
    return [len(a) for a in normalized_answers(cap)]


def repeated_char(cap) -> list:
    return [int(len(set(a)) < len(a)) for a in normalized_answers(cap)]


def input_overlap(cap) -> list:
    """Fraction of the normalized answer's characters (with
    multiplicity) that occur anywhere in the item's own `question`,
    lowercased — the normalized answer is lowercase, so the question
    is compared in the same case (build decision, ledgered)."""
    out = []
    for it, a in zip(cap["eval_items"], normalized_answers(cap)):
        q = str(it["question"]).lower()
        out.append(sum(1 for ch in a if ch in q) / len(a) if a else 0.0)
    return out


def functional_table(cap, rows) -> dict:
    return {"pi": wrong_target_propensity(rows, cap), "L": answer_length(cap),
            "R": repeated_char(cap), "O": input_overlap(cap)}


# ------------------------------------------------------------ bucket rule

def bucket(values) -> tuple:
    """design §5.2 / dial b: 1[F > med]; if constant, 1[F >= med]; if
    still constant, dropped. 2i's `_median_bucket` is the strict first
    branch alone (ties fall in bucket 0)."""
    arr = np.asarray(values, dtype=np.float64)
    if len(set(arr.tolist())) < 2:
        return None, "dropped_constant"
    med = float(np.median(arr))
    b = [int(v > med) for v in arr]
    if len(set(b)) == 2:
        return b, "median"
    b = [int(v >= med) for v in arr]
    if len(set(b)) == 2:
        return b, "tie_fallback"
    return None, "dropped_after_fallback"


def bucket_terciles(values) -> tuple:
    """§5.6 sensitivity: 0/1/2 by the number of tercile cut points
    strictly exceeded; collapses to `bucket` if fewer than two levels
    survive."""
    arr = np.asarray(values, dtype=np.float64)
    if len(set(arr.tolist())) < 2:
        return None, "dropped_constant"
    q1, q2 = (float(v) for v in np.quantile(arr, [1 / 3, 2 / 3]))
    b = [int(v > q1) + int(v > q2) for v in arr]
    if len(set(b)) >= 2:
        return b, "terciles"
    return bucket(values)


def composite_strata(base, tables, rungs, *, functionals=FUNCTIONALS,
                     bucket_fn=bucket) -> tuple:
    """Composite stratum = base stratum joined with the bucket of every
    surviving functional, in FUNCTIONALS order — 2i's `_composite_
    strata` string-join construction generalised. Returns the strata
    dict (the shape `_run_test` reads) and the per-rung rule report."""
    out, report = {}, {}
    for r in rungs:
        parts = [list(base[r]["strata"])]
        rep = {}
        for f in functionals:
            b, rule = bucket_fn(tables[r][f])
            rep[f] = rule
            if b is not None:
                parts.append([str(v) for v in b])
        out[r] = {"strata": ["|".join(p) for p in zip(*parts)]}
        report[r] = rep
    return out, report


# ------------------------------------------------------------- thinning

def mean_rate(counts) -> float:
    return float(sum(counts)) / (len(counts) * DRAWS_PER_ITEM)


def matched_k(rate_a, rate_b) -> dict:
    """design §5.4: the denser predictor is thinned to
    k = clip(floor(64 · r_sparse / r_dense + 0.5), 1, 64); equal rates
    thin nothing."""
    if rate_a == rate_b:
        return {"denser": None, "k": DRAWS_PER_ITEM, "n_blocks": 1}
    if rate_a > rate_b:
        denser, sparse, dense = "A", rate_b, rate_a
    else:
        denser, sparse, dense = "B", rate_a, rate_b
    k = int(np.floor(DRAWS_PER_ITEM * sparse / dense + 0.5))
    k = min(DRAWS_PER_ITEM, max(1, k))
    return {"denser": denser, "k": k, "n_blocks": DRAWS_PER_ITEM // k}


def thinned_counts(bits, k, block) -> list:
    return [int(sum(b[block * k:(block + 1) * k])) for b in bits]


def zero_fraction_k(bits_dense, counts_sparse) -> int:
    """§5.4 sensitivity: the k (block 0) whose positive-item fraction
    is closest to the sparser predictor's; ties to the smaller k."""
    target = sum(1 for c in counts_sparse if c > 0) / len(counts_sparse)
    best = None
    for k in range(1, DRAWS_PER_ITEM + 1):
        frac = sum(1 for b in bits_dense if sum(b[:k]) > 0) / len(bits_dense)
        d = abs(frac - target)
        if best is None or d < best[0]:
            best = (d, k)
    return best[1]
