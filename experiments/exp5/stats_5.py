# experiments/exp5/stats_5.py
"""Exp 5 statistics (design §3.4–§3.6, §3.8, S1/S4/S5/S7): pure functions,
no I/O, no torch. Every count is an integer of 500; every read's clear
status is 2d's bar (`battery_5.clears_5`)."""
from __future__ import annotations

import math
import sys
from pathlib import Path

EXP5 = Path(__file__).resolve().parent
if str(EXP5.parent.parent) not in sys.path:
    sys.path.insert(0, str(EXP5.parent.parent))

from experiments.exp5 import _threads_5  # noqa: E402,F401
import numpy as np  # noqa: E402
from scipy.stats import binomtest, spearmanr  # noqa: E402

from experiments.exp5 import battery_5 as b5  # noqa: E402

WORLDS_5 = ("INSUFFICIENT_DATA", "UNDETERMINED", "NOT-MATCHED", "MATCHED")
MODIFIERS_5 = ("LARGE-AHEAD", "SMALL-AHEAD", "MIXED", "THIN")
CLASSES_5 = ("L-AHEAD", "S-AHEAD", "CONCORDANT", "UNSTABLE", "PLACEBO-ONLY")


# ---------------------------------------------------------------- reads

def _mean(xs):
    return (sum(xs) / len(xs)) if xs else None


def reads_5(counts: dict, plan: dict, rung: str) -> dict:
    lo, hi = plan["bracket"]
    bm = [int(counts[s][rung]) for s in plan["b_minus"]]
    bp = [int(counts[s][rung]) for s in plan["b_plus"]]
    c_lo, c_hi = int(counts[lo][rung]), int(counts[hi][rung])
    return {"lo": c_lo, "hi": c_hi, "a": (c_lo + c_hi) / 2, "b_minus": _mean(bm),
            "b_plus": _mean(bp), "raw": {"lo": c_lo, "hi": c_hi, "b_minus": bm, "b_plus": bp}}


def cell_5(*, f: int, reads: dict, floor: float, n: int = b5.N_ITEMS) -> dict:
    raw = reads["raw"]
    f = int(f)
    seven = [f, raw["lo"], raw["hi"]] + list(raw["b_minus"]) + list(raw["b_plus"])
    clears = {k: b5.clears_5(k, floor, n) for k in set(seven)}
    live = any(clears[k] for k in seven)
    a = reads["a"]
    R = abs(a - f)
    sides = [abs(a - reads[k]) for k in ("b_minus", "b_plus") if reads[k] is not None]
    P = (sum(sides) / len(sides)) if sides else None
    sigma, lam_lo, lam_hi = clears[f], clears[raw["lo"]], clears[raw["hi"]]
    if lam_lo and lam_hi and not sigma:
        cls = "L-AHEAD"
    elif sigma and not lam_lo and not lam_hi:
        cls = "S-AHEAD"
    elif sigma and lam_lo and lam_hi:
        cls = "CONCORDANT"
    elif lam_lo != lam_hi:
        cls = "UNSTABLE"
    else:
        cls = "PLACEBO-ONLY" if live else None
    return {"f": f, "lo": raw["lo"], "hi": raw["hi"], "a": a, "b_minus": reads["b_minus"],
            "b_plus": reads["b_plus"], "raw_reads": seven, "live": bool(live),
            "defined_P": P is not None, "R": R, "P": P,
            "c": ((R - P) / n) if P is not None else None, "signed": (a - f) / n,
            "R_gt_P": (P is not None and R > P), "sigma": bool(sigma),
            "lambda_lo": bool(lam_lo), "lambda_hi": bool(lam_hi),
            "b_minus_clears_both": bool(len(raw["b_minus"]) == 2
                                        and all(clears[k] for k in raw["b_minus"])),
            "class": cls}


def cells_5(pairs_data: list, floors: dict) -> list:
    """`pairs_data`: [{"small", "large", "plan" (done), "f": {rung: count},
    "counts": {step: {rung: count}}}, ...] over KEPT pairs only."""
    out = []
    for pd in pairs_data:
        plan = pd["plan"]
        for rung in b5.RUNGS:
            r = reads_5(pd["counts"], plan, rung)
            c = cell_5(f=pd["f"][rung], reads=r, floor=floors[rung])
            c.update({"small": pd["small"], "large": pd["large"], "rung": rung,
                      "family": b5.FAMILY_OF[rung], "type": b5.RUNG_TYPE_5[rung],
                      "bracket": list(plan["bracket"]), "b_minus_steps": list(plan["b_minus"]),
                      "b_plus_steps": list(plan["b_plus"]),
                      "residual_lo": plan["residual_lo"], "residual_hi": plan["residual_hi"]})
            out.append(c)
    return out


def analysed_5(cells: list) -> list:
    return [c for c in cells if c["live"] and c["defined_P"]]


# -------------------------------------------------------- the sign flip

def sign_flip_p_5(block_sums, n_cells: int, *, max_enumerate=b5.MAX_ENUMERATE_BLOCKS_5,
                  n_sample=b5.N_PERM_SAMPLED_5, seed=b5.PERM_SEED_5) -> dict:
    """p = P(T_null ≥ T) under independent sign flips of the blocks with a
    NONZERO sum; enumerated (identity included) below the guard, sampled
    with the add-one convention above it."""
    all_sums = [float(s) for s in block_sums]
    T = sum(all_sums) / n_cells if n_cells else 0.0
    sums = np.array([s for s in all_sums if s != 0.0], dtype=np.float64)
    k = int(len(sums))
    base = {"T": float(T), "n_blocks": k, "n_blocks_total": len(all_sums), "n_cells": int(n_cells)}
    if k == 0:
        return {**base, "p": 1.0, "method": "degenerate", "n_perms": 0, "resolution": None,
                "null_mean": 0.0, "null_sd": 0.0, "count_ge": 0, "p_min_attainable": 1.0}
    if k <= max_enumerate:
        signs = (((np.arange(2 ** k, dtype=np.int64)[:, None] >> np.arange(k)) & 1) * 2 - 1)
        null = (signs.astype(np.float64) @ sums) / n_cells
        count = int(np.sum(null >= T - 1e-12))
        return {**base, "p": count / len(null), "method": "enumerated", "n_perms": int(len(null)),
                "resolution": 1.0 / len(null), "count_ge": count,
                "p_min_attainable": 1.0 / len(null),   # 2^-k: the identity is always counted
                "null_mean": float(null.mean()), "null_sd": float(null.std())}
    rng = np.random.default_rng(seed)
    signs = rng.choice(np.array([-1.0, 1.0]), size=(int(n_sample), k))
    null = (signs @ sums) / n_cells
    count = int(np.sum(null >= T - 1e-12))
    return {**base, "p": (1 + count) / (n_sample + 1), "method": "sampled",
            "n_perms": int(n_sample), "resolution": 1.0 / (n_sample + 1), "count_ge": count,
            "p_min_attainable": 1.0 / (n_sample + 1),
            "null_mean": float(null.mean()), "null_sd": float(null.std()), "seed": int(seed)}


def _block_sums(cells, key):
    sums = {}
    for c in cells:
        sums[c[key]] = sums.get(c[key], 0.0) + c["c"]
    return sums


def primary_5(cells: list, *, n_sample=b5.N_PERM_SAMPLED_5, seed=b5.PERM_SEED_5) -> dict:
    live = analysed_5(cells)
    n = len(live)
    rung_sums = _block_sums(live, "rung")
    fam_sums = _block_sums(live, "family")
    out = {"T": (sum(c["c"] for c in live) / n) if n else None, "n_cells": n,
           "n_rungs": len(rung_sums), "n_families": len(fam_sums),
           "n_excluded_dead": sum(1 for c in cells if not c["live"]),
           "n_excluded_undefined_P": sum(1 for c in cells if c["live"] and not c["defined_P"]),
           "per_rung_sum": rung_sums,
           "rung_block": sign_flip_p_5(list(rung_sums.values()), n, n_sample=n_sample, seed=seed),
           "family_block": sign_flip_p_5(list(fam_sums.values()), n, n_sample=n_sample, seed=seed),
           "cell_level": sign_flip_p_5([c["c"] for c in live], n, n_sample=n_sample, seed=seed)}
    # final review I-5 (ruling: additive, printed only): the rung-block flip's resolution
    out["n_nonzero_blocks"] = out["rung_block"]["n_blocks"]
    out["p_min_attainable"] = out["rung_block"]["p_min_attainable"]
    return out


# ---------------------------------------------------------- the modifier

def modifier_5(cells: list) -> dict:
    sel = [c for c in analysed_5(cells) if c["R_gt_P"]]
    n = len(sel)
    n_pos = sum(1 for c in sel if c["signed"] > 0)
    n_neg = sum(1 for c in sel if c["signed"] < 0)
    if n < b5.MODIFIER_MIN_CELLS_5:
        return {"modifier": "THIN", "n": n, "n_pos": n_pos, "n_neg": n_neg, "p_two_sided": None,
                "reason": f"fewer than {b5.MODIFIER_MIN_CELLS_5} cells with R > P — no test"}
    p = float(binomtest(n_pos, n, 0.5, alternative="two-sided").pvalue)
    if p < b5.MODIFIER_ALPHA_5 and n_pos > n_neg:
        m = "LARGE-AHEAD"
    elif p < b5.MODIFIER_ALPHA_5 and n_neg > n_pos:
        m = "SMALL-AHEAD"
    else:
        m = "MIXED"
    return {"modifier": m, "n": n, "n_pos": n_pos, "n_neg": n_neg, "p_two_sided": p}


def signed_offset_ci_5(cells: list, *, n_boot=b5.N_BOOT_5, seed=b5.BOOT_SEED_5) -> dict:
    live = [c for c in cells if c["live"]]
    rungs = sorted({c["rung"] for c in live})
    by_rung = {r: [c["signed"] for c in live if c["rung"] == r] for r in rungs}
    vals = [c["signed"] for c in live]
    if not rungs:
        return {"mean": None, "ci95": [None, None], "n_rungs": 0, "n_cells": 0}
    rng = np.random.default_rng(seed)
    boots = np.empty(n_boot)
    for b in range(n_boot):
        pick = rng.choice(len(rungs), size=len(rungs), replace=True)
        xs = [v for i in pick for v in by_rung[rungs[i]]]
        boots[b] = float(np.mean(xs))
    return {"mean": float(np.mean(vals)), "ci95": [float(np.percentile(boots, 2.5)),
                                                    float(np.percentile(boots, 97.5))],
            "n_rungs": len(rungs), "n_cells": len(live), "n_boot": int(n_boot), "seed": int(seed)}


# ------------------------------------------------------------ the ledger

def ledger_5(cells: list) -> dict:
    live = [c for c in cells if c["live"]]
    classes = {k: sum(1 for c in live if c["class"] == k) for k in CLASSES_5}
    named = [{"small": c["small"], "large": c["large"], "rung": c["rung"], "class": c["class"],
              "f": c["f"], "lo": c["lo"], "hi": c["hi"], "bracket": c["bracket"],
              "residual_lo": c["residual_lo"], "residual_hi": c["residual_hi"],
              "b_minus_clears_both": c["b_minus_clears_both"]}
             for c in live if c["class"] in ("L-AHEAD", "S-AHEAD")]
    return {"n_live": len(live), "classes": classes,
            "unstable_fraction": (classes["UNSTABLE"] / len(live)) if live else None,
            "named": named}


# -------------------------------------------------------------- the tree

def tree_5(*, failures, primary, modifier) -> dict:
    if failures:
        return {"verdict": "INSUFFICIENT_DATA", "modifier": None,
                "reason": f"{len(failures)} refusal(s); first: {failures[0]}"}
    n, k = primary["n_cells"], primary["n_rungs"]
    if n < b5.MIN_LIVE_CELLS_5 or k < b5.MIN_LIVE_RUNGS_5:
        return {"verdict": "UNDETERMINED", "modifier": None,
                "reason": f"{n} live cells with P defined over {k} rungs — fewer than "
                          f"{b5.MIN_LIVE_CELLS_5} cells or {b5.MIN_LIVE_RUNGS_5} rungs"}
    T, p = primary["T"], primary["rung_block"]["p"]
    if p < b5.ALPHA_5 and T >= b5.T_BAR_5:
        return {"verdict": "NOT-MATCHED", "modifier": modifier["modifier"],
                "reason": f"rung-block p {p:.4g} < {b5.ALPHA_5} and T {T:.4f} ≥ {b5.T_BAR_5}; "
                          f"modifier {modifier['modifier']}"}
    return {"verdict": "MATCHED", "modifier": None,
            "reason": f"rung-block p {p:.4g} / T {T:.4f} do not meet p < {b5.ALPHA_5} and "
                      f"T ≥ {b5.T_BAR_5}"}


# ------------------------------------------------------------ secondaries

def s4_size_ratio_5(cells: list, n_params: dict) -> dict:
    live = analysed_5(cells)
    x = [math.log(n_params[c["large"]] / n_params[c["small"]]) for c in live]
    y = [c["c"] for c in live]
    per_pair = {}
    for c in live:
        per_pair.setdefault(f"{c['small']}→{c['large']}", []).append(c["c"])
    rho = spearmanr(x, y).statistic if len(set(x)) > 1 and len(set(y)) > 1 and len(live) > 2 else None
    return {"spearman": (float(rho) if rho is not None and not math.isnan(rho) else None),
            "n_cells": len(live),
            "per_pair": {k: {"mean_c": float(np.mean(v)), "n": len(v),
                             "log_ratio": math.log(n_params[k.split("→")[1]] / n_params[k.split("→")[0]])}
                         for k, v in per_pair.items()}}


def s5_by_type_5(cells: list) -> dict:
    out = {}
    for typ in ("arithmetic", "option", "string"):
        sub = [c for c in analysed_5(cells) if c["type"] == typ]
        rungs = {c["rung"] for c in sub}
        block = {"T": (float(np.mean([c["c"] for c in sub])) if sub else None), "n_cells": len(sub),
                 "n_rungs": len(rungs), "modifier": modifier_5(sub)}
        if len(rungs) >= 5:
            sums = _block_sums(sub, "rung")
            block["p"] = sign_flip_p_5(list(sums.values()), len(sub))["p"]
        else:
            block["p"] = None
            block["reason"] = "fewer than 5 rungs carry cells — no p (4b note 3)"
        out[typ] = block
    return out


def s7_by_pair_5(cells: list) -> dict:
    out = {}
    for c in analysed_5(cells):
        out.setdefault(f"{c['small']}→{c['large']}", []).append(c["c"])
    return {k: {"mean_c": float(np.mean(v)), "n_live": len(v)} for k, v in out.items()}
