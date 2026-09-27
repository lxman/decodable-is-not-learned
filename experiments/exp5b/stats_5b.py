# experiments/exp5b/stats_5b.py
"""Exp 5b statistics (design §3.2–§3.5, §3.7, §5): pure functions, no I/O.
Every count is an integer of 500; R and P are Experiment 5's committed
values; M is the matched placebo; the null is Experiment 5's sign flip
verbatim (`stats_5.sign_flip_p_5`)."""
from __future__ import annotations

import math
import sys
from pathlib import Path

EXP5B = Path(__file__).resolve().parent
if str(EXP5B.parent.parent) not in sys.path:
    sys.path.insert(0, str(EXP5B.parent.parent))

from experiments.exp5 import _threads_5  # noqa: E402,F401
import numpy as np  # noqa: E402
from scipy.stats import binomtest  # noqa: E402

from experiments.exp5 import battery_5 as b5  # noqa: E402
from experiments.exp5 import stats_5 as ss  # noqa: E402
from experiments.exp5b import battery_5b as b5b  # noqa: E402

IDENT_KEYS_5B = ("small", "large", "rung", "family", "type", "f", "a", "b_minus", "b_plus", "R", "P",
                 "signed", "class", "bracket", "residual_lo", "residual_hi", "sigma", "lambda_lo",
                 "lambda_hi")
FORM_KEYS_5B = ("c_naive", "c_max", "c_minus")


# ---------------------------------------------------------------- reads

def small_reads_5b(counts_b: dict, rung: str) -> dict:
    """`counts_b`: {step: {rung: count}} for ONE small side's 5b units — the
    final plus every present, finite member."""
    f_B = int(counts_b[b5.FINAL_STEP_5][rung])
    members = {int(s): int(counts_b[s][rung]) for s in b5b.WINDOW_STEPS_5B if s in counts_b}
    return {"f_B": f_B, "members": members}


def placebo_terms_5b(cell5: dict, small: dict, *, sign=None) -> list:
    """D_sj = |(a − b_s) + sign·(f_B − n_j)| / √2 over the outer windows
    present and the members present (design §3.2)."""
    sign = b5b.PLACEBO_SIGN_5B if sign is None else sign
    a = float(cell5["a"])
    terms = []
    for side in ("b_minus", "b_plus"):
        b = cell5.get(side)
        if b is None:
            continue
        for step in sorted(small["members"]):
            n_j = small["members"][step]
            terms.append(abs((a - float(b)) + sign * (small["f_B"] - n_j)) / b5b.SQRT2_5B)
    return terms


def _mean(xs):
    return (sum(xs) / len(xs)) if xs else None


def cell_5b(cell5: dict, small: dict, floor: float, n: int = b5.N_ITEMS) -> dict:
    R, P = float(cell5["R"]), cell5["P"]
    f_B, members = int(small["f_B"]), dict(small["members"])
    Q = _mean([abs(f_B - v) for v in members.values()])
    terms = placebo_terms_5b(cell5, small)
    M = _mean(terms)
    M_minus = _mean(placebo_terms_5b(cell5, small, sign=-b5b.PLACEBO_SIGN_5B))
    reads4 = [f_B] + [members[s] for s in sorted(members, reverse=True)]     # final, 142000, 141000, 140000
    clears = {v: b5.clears_5(v, floor, n) for v in set(reads4)}
    out = {k: cell5.get(k) for k in IDENT_KEYS_5B}
    out.update({
        "f_B": f_B, "members": {str(s): members[s] for s in sorted(members, reverse=True)},
        "n_members": len(members), "n_terms": len(terms),
        "Q": Q, "M": M, "M_minus": M_minus, "defined_M": M is not None,
        "c_sym": ((R - M) / n) if M is not None else None,
        "c_naive": ((R - 0.5 * (float(P) + Q)) / n) if (Q is not None and P is not None) else None,
        "c_max": ((R - max(float(P), Q)) / n) if (Q is not None and P is not None) else None,
        "c_minus": ((R - M_minus) / n) if M_minus is not None else None,
        "c_exp5": cell5.get("c"),
        "R_gt_M": bool(M is not None and R > M),
        "small_reads": reads4, "small_clears": [bool(clears[v]) for v in reads4],
        "small_status_constant": len({clears[v] for v in reads4}) == 1,
        "small_sd": float(np.std(reads4, ddof=1)) if len(reads4) >= 2 else None,
    })
    return out


def cells_5b(cells5_live: list, counts_by_side: dict, floors: dict) -> list:
    """`cells5_live`: Experiment 5's cells with `live and defined_P`;
    `counts_by_side`: {size: {step: {rung: count}}} over the 5b units of
    the sides PRESENT. Since freeze F-1 an incomplete side's campaign
    refuses at the window-completeness site before this is ever called,
    so every side reaching a verdict is present and complete — the
    caller's `excluded`/`cells_dropped` are therefore empty on any tree
    that reaches a verdict, not a live exclusion mechanism."""
    out = []
    for c5 in cells5_live:
        side = counts_by_side.get(c5["small"])
        if side is None or b5.FINAL_STEP_5 not in side:
            continue
        out.append(cell_5b(c5, small_reads_5b(side, c5["rung"]), floors[c5["rung"]]))
    return out


def analysed_5b(cells: list, key: str = "c_sym") -> list:
    return [c for c in cells if c.get(key) is not None]


# -------------------------------------------------------------- primary

def _block_sums(cells, by, key):
    sums = {}
    for c in cells:
        sums[c[by]] = sums.get(c[by], 0.0) + float(c[key])
    return sums


def primary_5b(cells: list, *, key: str = "c_sym", n_sample=b5.N_PERM_SAMPLED_5,
               seed=b5.PERM_SEED_5) -> dict:
    live = analysed_5b(cells, key)
    n = len(live)
    rung_sums = _block_sums(live, "rung", key)
    fam_sums = _block_sums(live, "family", key)
    out = {"key": key, "T": (sum(float(c[key]) for c in live) / n) if n else None, "n_cells": n,
           "n_rungs": len(rung_sums), "n_families": len(fam_sums), "per_rung_sum": rung_sums,
           "rung_block": ss.sign_flip_p_5(list(rung_sums.values()), n, n_sample=n_sample, seed=seed),
           "family_block": ss.sign_flip_p_5(list(fam_sums.values()), n, n_sample=n_sample, seed=seed),
           "cell_level": ss.sign_flip_p_5([float(c[key]) for c in live], n, n_sample=n_sample, seed=seed)}
    out["n_nonzero_blocks"] = out["rung_block"]["n_blocks"]
    out["p_min_attainable"] = out["rung_block"]["p_min_attainable"]
    return out


# --------------------------------------------------------- sigma hat / cal

def sigma_hat_5b(cells: list) -> dict:
    """Design §3.4 / B-6: the root-mean-square over live cells of the
    per-cell sample SD (ddof 1) of the small side's four box-B reads."""
    live = [c for c in cells if c.get("small_sd") is not None and c.get("defined_M")]
    per_side = {}
    for c in live:
        per_side.setdefault(c["small"], []).append(c["small_sd"] ** 2)
    return {"pooled": (math.sqrt(float(np.mean([c["small_sd"] ** 2 for c in live]))) if live else None),
            "per_side": {s: math.sqrt(float(np.mean(v))) for s, v in sorted(per_side.items())},
            "n_cells": len(live)}


def _interp(axis, values, x):
    return float(np.interp(x, np.asarray(axis, dtype=float), np.asarray(values, dtype=float)))


def calibration_read_5b(power_rec: dict, sigma_hat, *, T_sym) -> dict:
    """The licence's calibration sub-cell (design §3.4, dial h): α and the
    null mean of T_sym read on the SIMULATED σ̂ axis; above the top →
    OFF-GRID (the top's values reported); at or below the bottom → the
    bottom's values with `below_grid`."""
    axis = list(power_rec["sigma_hat_axis"])
    alphas, nulls = list(power_rec["alpha_5b_axis"]), list(power_rec["null_mean_5b_axis"])
    if sigma_hat is None or T_sym is None:
        return {"sigma_hat": sigma_hat, "in_grid": False, "below_grid": False, "alpha_realized": None,
                "null_mean_T": None, "T_star": None, "cell": "OFF-GRID",
                "reason": "sigma_hat or T_sym undefined"}
    top, bottom = axis[-1], axis[0]
    if sigma_hat > top:
        return {"sigma_hat": float(sigma_hat), "in_grid": False, "below_grid": False,
                "alpha_realized": float(alphas[-1]), "null_mean_T": float(nulls[-1]),
                "T_star": float(T_sym - nulls[-1]), "cell": "OFF-GRID",
                "reason": f"sigma_hat {sigma_hat:.2f} above the grid's top {top:.2f}"}
    x = max(float(sigma_hat), bottom)
    alpha = _interp(axis, alphas, x)
    null = _interp(axis, nulls, x)
    return {"sigma_hat": float(sigma_hat), "in_grid": True, "below_grid": sigma_hat < bottom,
            "alpha_realized": alpha, "null_mean_T": null, "T_star": float(T_sym - null),
            "cell": "CALIBRATED" if alpha < b5b.ALPHA_CAL_5B else "INFLATED",
            "reason": f"realized alpha {alpha:.4f} at sigma_hat {x:.2f} "
                      f"({'<' if alpha < b5b.ALPHA_CAL_5B else '>='} {b5b.ALPHA_CAL_5B})"}


# ----------------------------------------------------------------- tree

def tree_5b(*, failures, primary, calibration) -> dict:
    if failures:
        return {"verdict": "INSUFFICIENT_DATA", "cell": None,
                "reason": f"{len(failures)} refusal(s); first: {failures[0]}"}
    n, k = primary["n_cells"], primary["n_nonzero_blocks"]
    if n < b5b.MIN_LIVE_CELLS_5B or k < b5b.MIN_NONZERO_BLOCKS_5B:
        return {"verdict": "UNDETERMINED", "cell": None,
                "reason": f"{n} live cells with M defined; {k} rungs with a nonzero block sum — fewer "
                          f"than {b5b.MIN_LIVE_CELLS_5B} cells or {b5b.MIN_NONZERO_BLOCKS_5B} nonzero blocks"}
    T, p = primary["T"], primary["rung_block"]["p"]
    sig, big = p < b5b.ALPHA_5B, T >= b5b.T_BAR_5B
    if sig and big:
        return {"verdict": "SURVIVES", "cell": calibration["cell"],
                "reason": f"rung-block p {p:.4g} < {b5b.ALPHA_5B} and T_sym {T:.4f} ≥ {b5b.T_BAR_5B}; "
                          f"calibration {calibration['cell']}"}
    cell = "SIZE-ONLY" if big else ("SIGN-ONLY" if sig else "INSIDE")
    return {"verdict": "NOT-SURVIVED", "cell": cell,
            "reason": f"rung-block p {p:.4g} / T_sym {T:.4f} against p < {b5b.ALPHA_5B} and "
                      f"T ≥ {b5b.T_BAR_5B}: {cell}"}


# ------------------------------------------------------------- modifier

def modifier_5b(cells: list) -> dict:
    sel = [c for c in analysed_5b(cells) if c["R_gt_M"]]
    n = len(sel)
    n_pos = sum(1 for c in sel if c["signed"] > 0)
    n_neg = sum(1 for c in sel if c["signed"] < 0)
    if n < b5.MODIFIER_MIN_CELLS_5:
        return {"modifier": "THIN", "n": n, "n_pos": n_pos, "n_neg": n_neg, "p_two_sided": None,
                "reason": f"fewer than {b5.MODIFIER_MIN_CELLS_5} cells with R > M — no test"}
    p = float(binomtest(n_pos, n, 0.5, alternative="two-sided").pvalue)
    if p < b5.MODIFIER_ALPHA_5 and n_pos > n_neg:
        m = "LARGE-AHEAD"
    elif p < b5.MODIFIER_ALPHA_5 and n_neg > n_pos:
        m = "SMALL-AHEAD"
    else:
        m = "MIXED"
    return {"modifier": m, "n": n, "n_pos": n_pos, "n_neg": n_neg, "p_two_sided": p}


# ---------------------------------------------------------- secondaries

def _sub(cells, pred, *, key="c_sym", n_sample, seed):
    sub = [c for c in analysed_5b(cells, key) if pred(c)]
    if not sub:
        return {"T": None, "p": None, "n_cells": 0, "n_rungs": 0}
    p = primary_5b(sub, key=key, n_sample=n_sample, seed=seed)
    return {"T": p["T"], "p": p["rung_block"]["p"], "n_cells": p["n_cells"], "n_rungs": p["n_rungs"],
            "n_nonzero_blocks": p["n_nonzero_blocks"]}


def s1_rows_5b(cells, *, n_sample, seed) -> dict:
    live = analysed_5b(cells)
    rows = {}
    for c in live:
        rows.setdefault(c["small"], []).append(c["c_sym"])
    return {"by_row": {s: {"T": float(np.mean(v)), "n_cells": len(v)} for s, v in sorted(rows.items())},
            "outside_2p8b": _sub(cells, lambda c: c["small"] != "2.8b", n_sample=n_sample, seed=seed),
            "referents": dict(b5b.EXP5_REFERENTS_5B)}


def _swap_cells(cells, target_of):
    """Experiment 5's statistic with f replaced by `target_of(cell)`."""
    out = []
    for c in analysed_5b(cells):
        x = target_of(c)
        if x is None:
            continue
        Rp = abs(float(c["a"]) - x)
        out.append({**c, "c_swap": (Rp - float(c["P"])) / b5.N_ITEMS})
    return out


def s2_swaps_5b(cells, *, n_sample, seed) -> dict:
    targets = {}
    for name in ("f_B",) + tuple(str(s) for s in b5b.WINDOW_STEPS_5B):
        sw = _swap_cells(cells, (lambda c: c["f_B"]) if name == "f_B" else
                         (lambda c, n=name: c["members"].get(n)))
        if not sw:
            targets[name] = {"T": None, "p": None, "n_cells": 0}
            continue
        p = primary_5b(sw, key="c_swap", n_sample=n_sample, seed=seed)
        targets[name] = {"T": p["T"], "p": p["rung_block"]["p"], "n_cells": p["n_cells"]}
    designations = {}
    for name in (str(s) for s in b5b.WINDOW_STEPS_5B):
        des = []
        for c in analysed_5b(cells):
            if name not in c["members"]:
                continue
            target = c["members"][name]
            others = {int(k): v for k, v in c["members"].items() if k != name}
            others[b5.FINAL_STEP_5] = c["f_B"]
            small = {"f_B": target, "members": others}
            terms = placebo_terms_5b(c, small)
            M = _mean(terms)
            if M is None:
                continue
            des.append({**c, "c_des": (abs(float(c["a"]) - target) - M) / b5.N_ITEMS})
        if not des:
            designations[name] = {"T": None, "p": None, "n_cells": 0}
            continue
        p = primary_5b(des, key="c_des", n_sample=n_sample, seed=seed)
        designations[name] = {"T": p["T"], "p": p["rung_block"]["p"], "n_cells": p["n_cells"]}
    return {"targets": targets, "designations": designations}


def s6_ledger_5b(cells) -> dict:
    live = analysed_5b(cells)
    named = [{"small": c["small"], "large": c["large"], "rung": c["rung"], "class": c["class"],
              "f": c["f"], "small_reads": c["small_reads"], "small_clears": c["small_clears"],
              "stable": c["small_status_constant"]}
             for c in live if c["class"] in ("L-AHEAD", "S-AHEAD")]
    return {"n_live": len(live),
            "fraction_small_status_constant": (sum(1 for c in live if c["small_status_constant"]) / len(live))
            if live else None,
            "named": named}


def s7_by_type_5b(cells, *, n_sample, seed) -> dict:
    out = {}
    for typ in ("arithmetic", "option", "string"):
        sub = [c for c in analysed_5b(cells) if c["type"] == typ]
        rungs = {c["rung"] for c in sub}
        block = {"T": (float(np.mean([c["c_sym"] for c in sub])) if sub else None), "n_cells": len(sub),
                 "n_rungs": len(rungs), "modifier": modifier_5b(sub)}
        if len(rungs) >= 5:
            block["p"] = primary_5b(sub, n_sample=n_sample, seed=seed)["rung_block"]["p"]
        else:
            block["p"] = None
            block["reason"] = "fewer than 5 rungs carry cells — no p (4b note 3)"
        out[typ] = block
    return out


def s8_one_member_5b(cells, s11_per_side: dict, *, n_sample, seed) -> dict:
    """The zero-contact reading (design §5 S8): M₁ over the two outer
    windows with Experiment 5's committed S11 read and f_A."""
    one = []
    for c in analysed_5b(cells):
        row = (s11_per_side.get(c["small"]) or {}).get(c["rung"])
        if not row or row.get("s11") is None or row.get("final") is None:
            continue
        small = {"f_B": int(row["final"]), "members": {b5.S11_STEP_5: int(row["s11"])}}
        M1 = _mean(placebo_terms_5b(c, small))
        if M1 is None:
            continue
        one.append({**c, "c_one": (float(c["R"]) - M1) / b5.N_ITEMS})
    if not one:
        return {"T1": None, "p1": None, "n_cells": 0, "T_sym_minus_T1": None}
    p1 = primary_5b(one, key="c_one", n_sample=n_sample, seed=seed)
    psym = primary_5b(cells, n_sample=n_sample, seed=seed)
    return {"T1": p1["T"], "p1": p1["rung_block"]["p"], "n_cells": p1["n_cells"],
            "T_sym_minus_T1": (psym["T"] - p1["T"]) if (psym["T"] is not None) else None}


def s9_spike_5b(cells, *, n_sample, seed) -> dict:
    small, large = b5b.SPIKE_PAIR_5B
    r = _sub(cells, lambda c: not (c["small"] == small and c["large"] == large), n_sample=n_sample, seed=seed)
    return {**r, "excluded_pair": [small, large],
            "referents": {"exp5_T": b5b.EXP5_REFERENTS_5B["spike_excluded_T"],
                          "exp5_p": b5b.EXP5_REFERENTS_5B["spike_excluded_p"]}}


def s10_forms_5b(cells, *, n_sample, seed) -> dict:
    out = {}
    for key in FORM_KEYS_5B:
        sub = analysed_5b(cells, key)
        if not sub:
            out[key] = {"T": None, "p": None, "n_cells": 0}
            continue
        p = primary_5b(sub, key=key, n_sample=n_sample, seed=seed)
        out[key] = {"T": p["T"], "p": p["rung_block"]["p"], "n_cells": p["n_cells"]}
    return out


def s12_newly_live_5b(cells5_dead: list, counts_by_side: dict, floors: dict) -> dict:
    found = []
    for c5 in cells5_dead:
        side = counts_by_side.get(c5["small"])
        if side is None or b5.FINAL_STEP_5 not in side:
            continue
        small = small_reads_5b(side, c5["rung"])
        reads = [small["f_B"]] + list(small["members"].values())
        if any(b5.clears_5(v, floors[c5["rung"]]) for v in reads):
            found.append({"small": c5["small"], "large": c5["large"], "rung": c5["rung"], "reads": reads})
    return {"n": len(found), "cells": found}
