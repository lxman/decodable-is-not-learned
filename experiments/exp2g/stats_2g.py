"""Exp 2g statistic (design §6.1): within-stratum Somers' D per rung,
T = the mean over eligible rungs, one-sided permutation null with the
predictor permuted WITHIN rung × stratum. Pure numpy."""

from __future__ import annotations

import numpy as np

ALPHA = 0.01              # primary
ALPHA_TWIN = 0.05         # the twin's forecast (ruling g)
T_BAR = 0.10              # effect bar (ruling c)
N_PERM = 10_000
PERM_SEED = 0
N_BOOT = 1_000
BOOT_SEED = 0


def precompute(y, strata) -> list:
    """Per stratum: the item indices and the upper-triangular matrix
    sign(y_i − y_j) masked to i < j with y_i ≠ y_j (the informative
    pairs); y and the strata are fixed across permutations."""
    y = np.asarray(y, dtype=np.float64)
    strata = np.asarray(strata)
    if y.shape != strata.shape:
        raise ValueError("precompute: y and strata lengths differ")
    out = []
    for s in sorted(set(strata.tolist())):
        idx = np.flatnonzero(strata == s)
        ys = y[idx]
        sy = np.sign(ys[:, None] - ys[None, :]).astype(np.int8)
        mask = np.triu(np.ones((len(idx), len(idx)), dtype=bool), 1)
        sy = np.where(mask, sy, 0).astype(np.int8)
        n_pairs = int(np.count_nonzero(sy))
        if n_pairs:
            out.append({"idx": idx, "sy": sy, "n_pairs": n_pairs})
    return out


def d_from_pre(x, pre) -> tuple:
    x = np.asarray(x, dtype=np.float64)
    num, den = 0.0, 0
    for blk in pre:
        xs = x[blk["idx"]]
        sx = np.sign(xs[:, None] - xs[None, :])
        num += float((sx * blk["sy"]).sum())
        den += blk["n_pairs"]
    return (num / den if den else float("nan")), den


def somers_d_within(x, y, strata) -> dict:
    y = np.asarray(y, dtype=np.float64)
    pre = precompute(y, strata)
    d, n_pairs = d_from_pre(x, pre)
    return {"d": d, "n_pairs": int(n_pairs), "n_pos": int((y > 0).sum()),
            "n_strata": len(set(np.asarray(strata).tolist())), "n": int(len(y))}


def permute_within(x, strata, rng) -> np.ndarray:
    x = np.asarray(x, dtype=np.float64)
    strata = np.asarray(strata)
    out = np.empty_like(x)
    for s in sorted(set(strata.tolist())):
        idx = np.flatnonzero(strata == s)
        out[idx] = x[rng.permutation(idx)]
    return out


def perm_test(cells, *, n_perm: int = N_PERM, seed: int = PERM_SEED) -> dict:
    """T_obs and its one-sided permutation p over the cells' rungs."""
    if not cells:
        raise ValueError("perm_test: no cells")
    pres, xs, per_rung = [], [], {}
    for c in cells:
        pre = precompute(c["y"], c["strata"])
        d, n_pairs = d_from_pre(c["x"], pre)
        if not n_pairs or not np.isfinite(d):
            raise ValueError(f"perm_test: rung {c['rung']} has no informative "
                             f"pair — not eligible")
        pres.append(pre)
        xs.append(np.asarray(c["x"], dtype=np.float64))
        per_rung[c["rung"]] = {"d": float(d), "n_pairs": int(n_pairs),
                               "n_pos": int((np.asarray(c["y"]) > 0).sum())}
    T_obs = float(np.mean([v["d"] for v in per_rung.values()]))
    rng = np.random.default_rng(seed)
    null = np.empty(n_perm)
    for k in range(n_perm):
        ds = []
        for c, pre, x in zip(cells, pres, xs):
            xp = permute_within(x, c["strata"], rng)
            ds.append(d_from_pre(xp, pre)[0])
        null[k] = float(np.mean(ds))
    ge = int((null >= T_obs).sum())
    return {"T": T_obs, "p": (1 + ge) / (1 + n_perm), "n_perm": int(n_perm),
            "seed": int(seed), "n_ge": ge, "null_mean": float(null.mean()),
            "null_sd": float(null.std(ddof=1)) if n_perm > 1 else 0.0,
            "per_rung": per_rung, "n_rungs": len(cells)}


def bootstrap_d(x, y, strata, *, n_boot: int = N_BOOT, seed: int = BOOT_SEED) -> dict:
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    strata = np.asarray(strata)
    rng = np.random.default_rng(seed)
    point = somers_d_within(x, y, strata)["d"]
    vals = []
    for _ in range(n_boot):
        idx = rng.integers(0, len(x), size=len(x))
        d = somers_d_within(x[idx], y[idx], strata[idx])["d"]
        if np.isfinite(d):
            vals.append(d)
    if not vals:
        return {"point": point, "lo": float("nan"), "hi": float("nan"), "n_boot": 0}
    return {"point": float(point), "lo": float(np.percentile(vals, 2.5)),
            "hi": float(np.percentile(vals, 97.5)), "n_boot": len(vals)}


def pooled_d(cells) -> float:
    """Pair-weighted pooled D over the cells (printed beside T)."""
    num, den = 0.0, 0
    for c in cells:
        pre = precompute(c["y"], c["strata"])
        d, n = d_from_pre(c["x"], pre)
        if n:
            num += d * n
            den += n
    return num / den if den else float("nan")
