"""Frozen analysis for Experiment 1c (design doc §4, §5).

Reads the sub-critical density sweep that `run_lubana.py`'s S3 graph branch
trained and never probed: 40 cells at 0.25/0.45/0.65/0.85 p_c, from which one
scalar each was taken and the rest discarded.

WHAT IS ADJUDICATED. The pooled OLS slope of the DEPTH MARGIN on p/p_c, one
sided positive, against an exact within-block relabeling null over the four
density levels, blocked on (size, seed). Nothing else touches the verdict.

THE TWO GATES. A site fires iff BOTH the label-permutation null (Bonferroni
across all 8 sites) AND the per-site floor correction (trained accuracy
strictly above its own twin's, at the SAME site) admit it. Ruled 2026-08-14
before any 1c probe ran. Both are required because 1b measured that they are
load-bearing on different rows and neither suffices alone: the floor
correction demoted grokking/10M/seed104 (trained .017333 against a twin of
.017333) which the null had admitted, and the null blocked
lubana_below/1M/seed100 at p = .847 where the margin was positive. A rule
carrying only the floor admits reservoir decodability; a rule carrying only
the null admits whatever the random expansion already separates.

MEANS, NOT MAXIMA. Margins average the paired per-site differences. A max
over differences is biased upward and its null distribution depends on the
number of sites — the defect design §2 identifies in grokking's Bonferroni
family of one, which this experiment does not reproduce.

RAW p IN, CORRECTED p HERE. Records store each site's UNCORRECTED
permutation p. The Bonferroni family size is an analysis decision, so it
lives in this frozen file where a fixture can test it, not in the runner.
"""

from __future__ import annotations

from itertools import permutations
from pathlib import Path

import numpy as np

LAYERS = (0, 1, 2, 3)
TOKENS = (1, -1)
N_SITES = len(LAYERS) * len(TOKENS)
DEPTH_LAYERS = tuple(l for l in LAYERS if l >= 1)
ALPHA = 0.01

DENSITIES = (0.25, 0.45, 0.65, 0.85)     # sub-critical sweep, multiples of p_c
SIZES = ("1M", "10M")
SEEDS = (100, 101, 102, 103, 104)
MIN_LIVE_BLOCKS = 8                       # of 10; below this, INSUFFICIENT_DATA
CLASSES = ("depth", "L0-only", "silent")

# Permutation ties must survive floating-point reordering: a flat block sums to
# the same value under every relabeling, but not necessarily to the same BITS.
# Without this tolerance a null that is mathematically equal to the observed
# statistic can compare as strictly less, making p anti-conservative.
_TIE_TOL = 1e-12


def _field(site, name):
    """Sites arrive as plain dicts from fixtures and as SiteResult dataclasses
    from records. The analysis is deliberately agnostic: a fixture suite that
    could only be written against the record type would test the container as
    much as the statistic."""
    try:
        return site[name]
    except TypeError:
        return getattr(site, name)


def _site_key(s):
    return (int(_field(s, "layer")), int(_field(s, "token")))


def site_fires(trained_site, twin_site, *, n_sites: int = N_SITES,
               alpha: float = ALPHA) -> bool:
    """Both gates, conjoined. See the module docstring for why neither alone."""
    if _site_key(trained_site) != _site_key(twin_site):
        raise ValueError(
            f"a cell and its twin must be compared at the same site — got "
            f"{_site_key(trained_site)} against {_site_key(twin_site)}")
    null_admits = float(_field(trained_site, "null_p_raw")) * n_sites < alpha
    floor_admits = (float(_field(trained_site, "accuracy"))
                    > float(_field(twin_site, "accuracy")))
    return bool(null_admits and floor_admits)


def _paired(trained_sites, twin_sites):
    if len(trained_sites) != N_SITES or len(twin_sites) != N_SITES:
        raise ValueError(
            f"a profile must carry all {N_SITES} sites — got "
            f"{len(trained_sites)} trained and {len(twin_sites)} twin")
    tw = {_site_key(s): s for s in twin_sites}
    if len(tw) != N_SITES:
        raise ValueError(f"twin profile has duplicate sites")
    out = []
    for t in trained_sites:
        k = _site_key(t)
        if k not in tw:
            raise ValueError(f"trained site {k} has no twin at the same site")
        out.append((t, tw[k]))
    return out


def _mean_margin(trained_sites, twin_sites, layers) -> float:
    diffs = [float(_field(t, "accuracy")) - float(_field(w, "accuracy"))
             for t, w in _paired(trained_sites, twin_sites)
             if int(_field(t, "layer")) in layers]
    if not diffs:
        raise ValueError(f"no sites at layers {layers}")
    return sum(diffs) / len(diffs)


def depth_margin(trained_sites, twin_sites) -> float:
    """M — mean paired difference over the six sites with layer >= 1."""
    return _mean_margin(trained_sites, twin_sites, DEPTH_LAYERS)


def l0_margin(trained_sites, twin_sites) -> float:
    """L — mean paired difference over the two layer-0 sites. Diagnostic."""
    return _mean_margin(trained_sites, twin_sites, (0,))


def classify(trained_sites, twin_sites, *, alpha: float = ALPHA) -> dict:
    """{depth, L0-only, silent} by precedence, with both counts kept visible."""
    fired = [(int(_field(t, "layer")), site_fires(t, w, alpha=alpha))
             for t, w in _paired(trained_sites, twin_sites)]
    n_depth = sum(1 for layer, f in fired if f and layer >= 1)
    n_l0 = sum(1 for layer, f in fired if f and layer == 0)
    if n_depth:
        cls = "depth"
    elif n_l0:
        cls = "L0-only"
    else:
        cls = "silent"
    return {"class": cls, "n_depth_fired": n_depth, "n_l0_fired": n_l0}


# -------------------------------------------------- loading and assembly
#
# The loader is frozen WITH the analysis, per design §9. 1b froze analyze_1b.py
# with a verdict() and no record loader; the gap surfaced at analysis time and
# run_analysis_1b.py had to be written after the campaign had already run. A
# frozen verdict function that cannot be fed from disk is not a frozen
# analysis, so the path from records to verdict is fixture-tested here.

def load_profiles(root, *, arm: str | None = None) -> list:
    from experiments.exp1c.records import ProfileRecord

    base = Path(root) / "results"
    if arm is not None:
        base = base / arm
    if not base.is_dir():
        return []
    return [ProfileRecord.load(p) for p in sorted(base.rglob("*.json"))]


def _profile_key(p):
    return (p.system, p.arm, round(float(p.density), 9), p.size_bucket, p.seed)


def pair_profiles(profiles):
    """Match every trained profile to its own twin. Never falls back."""
    trained, twins = {}, {}
    for p in profiles:
        k = _profile_key(p)
        target = trained if p.trained else twins
        if k in target:
            raise ValueError(
                f"duplicate {'trained' if p.trained else 'twin'} profile for "
                f"{k} — one cell cannot have two")
        target[k] = p
    out = []
    for k in sorted(trained, key=str):
        if k not in twins:
            raise ValueError(
                f"trained cell {k} has no twin — every margin in this "
                f"experiment is a paired difference and there is no fallback "
                f"floor to substitute")
        out.append((trained[k], twins[k]))
    return out


def assemble_cells(profiles) -> list[dict]:
    """Records on disk -> the exact cell shape `verdict` consumes."""
    cells = []
    for t, w in pair_profiles(profiles):
        cell = {
            "system": t.system, "arm": t.arm, "density": float(t.density),
            "size_bucket": t.size_bucket, "seed": t.seed,
            "depth_margin": depth_margin(t.sites, w.sites),
            "l0_margin": l0_margin(t.sites, w.sites),
            "capability_metric": t.capability_metric,
            "n_rows": t.n_rows,
        }
        # The natural arm carries no nulls by construction (records.py), so the
        # two-gate rule is undefined there and the cell stays unclassified.
        if t.arm == "fixed":
            cell.update(classify(t.sites, w.sites))
        else:
            cell["class"] = None
        cells.append(cell)
    return cells


# ------------------------------------------------------------ primary test

def _sd(xs) -> float:
    """Sample sd (ddof=1) — an estimate of the population variance, which is
    what the power table consumes."""
    return float(np.std(np.asarray(xs, dtype=float), ddof=1))


def _sign_flip_p(values, *, n_draw: int, seed: int) -> float:
    """One-sided randomization test that the mean exceeds zero.

    Distribution-free, and it is the right null for a paired difference: under
    'training added nothing at this site' the sign of each cell's margin is
    exchangeable.
    """
    v = np.asarray(values, dtype=float)
    obs = float(v.mean())
    rng = np.random.default_rng(seed)
    signs = rng.choice((-1.0, 1.0), size=(n_draw, v.size))
    null = (signs * v).mean(axis=1)
    return (int(np.sum(null >= obs - _TIE_TOL)) + 1) / (n_draw + 1)


def stage_a_gate(above_profiles, below_profiles, *, seed: int,
                 alpha: float = ALPHA, n_draw: int = 100_000) -> dict:
    """Design §8 step 3. The measure must reproduce known answers before it is
    allowed anywhere near the sweep."""
    above = [depth_margin(t.sites, w.sites)
             for t, w in pair_profiles(above_profiles)]
    below = [depth_margin(t.sites, w.sites)
             for t, w in pair_profiles(below_profiles)]
    expected = len(SIZES) * len(SEEDS)
    for name, row in (("lubana_above", above), ("lubana_below", below)):
        if len(row) != expected:
            raise ValueError(
                f"stage A needs {expected} cells for {name}, got {len(row)}")

    n_positive = sum(1 for m in above if m > 0)
    below_p = _sign_flip_p(below, n_draw=n_draw, seed=seed)

    failures = []
    if n_positive < 8:
        failures.append(
            f"lubana_above: depth margin positive in {n_positive}/{expected}, "
            f"bar is >= 8 — the measure does not reproduce a row 1b scored "
            f"10/10 S1-present")
    if below_p < alpha:
        failures.append(
            f"lubana_below: depth margin significantly above zero "
            f"(p = {below_p:.5f} < {alpha}) — the measure reads structure "
            f"where 1b's closed record found none in 10/10 cells")

    return {"pass": not failures, "failures": failures,
            "above_positive": n_positive, "below_p": below_p,
            "sd_depth_margin": _sd(below),
            "sd_depth_margin_above": _sd(above)}


def _contrast():
    d = np.asarray(DENSITIES, dtype=float)
    return d - d.mean()


def slope_and_p(blocks, *, n_draw: int = 100_000, seed: int = 0) -> dict:
    """Pooled OLS slope of the margin on p/p_c, one-sided positive.

    Null: exact within-block relabeling of the four density levels (4! = 24 per
    block, sampled). Blocking on (size, seed) is what makes the test paired
    against initialization and scale; a between-block null would read
    seed-to-seed variation as signal.
    """
    if not blocks:
        raise ValueError("no live blocks — the slope test is undefined")
    x = _contrast()
    M = np.empty((len(blocks), len(DENSITIES)), dtype=float)
    for i, b in enumerate(blocks):
        for j, d in enumerate(DENSITIES):
            if d not in b:
                raise ValueError(
                    f"block {i} is missing density {d} — a partial block cannot "
                    f"enter a within-block relabeling null")
            M[i, j] = float(b[d])

    denom = len(blocks) * float((x ** 2).sum())
    obs = float((M * x).sum())

    xp = x[np.asarray(list(permutations(range(len(DENSITIES)))))]   # (24, 4)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, xp.shape[0], size=(n_draw, len(blocks)))
    null = np.einsum("nk,dnk->d", M, xp[idx])

    p = (int(np.sum(null >= obs - _TIE_TOL)) + 1) / (n_draw + 1)
    return {"slope": obs / denom, "p": p, "n_blocks": len(blocks),
            "n_draw": n_draw}


def _live_blocks(cells, field="depth_margin"):
    """Group cells into (size, seed) blocks; a block is live iff it carries all
    four densities. Partial blocks are dropped and counted, never patched."""
    grouped: dict[tuple, dict] = {}
    for c in cells:
        grouped.setdefault((c["size_bucket"], c["seed"]), {})[
            float(c["density"])] = float(c[field])
    return [b for b in grouped.values()
            if all(d in b for d in DENSITIES)]


def _class_tables(cells):
    total = {k: 0 for k in CLASSES}
    by_density = {d: {k: 0 for k in CLASSES} for d in DENSITIES}
    for c in cells:
        cls = c["class"]
        if cls not in total:
            raise ValueError(f"unknown cell class {cls!r}, expected {CLASSES}")
        total[cls] += 1
        by_density[float(c["density"])][cls] += 1
    return total, by_density


def verdict(stage_a, cells, *, below_silent: bool,
            natural_l0_tracks_pool=None, alpha: float = ALPHA,
            n_draw: int = 100_000, seed: int = 0) -> dict:
    """The frozen verdict tree, adjudicated in design §5's precedence order.

    Precedence is the part that goes wrong quietly. 2c reached FAIL on a branch
    adjudicated before the PASS branch was ever tested — correct, and legible
    only because the order was frozen in advance. It is frozen here too.
    """
    classes, classes_by_density = _class_tables(cells)
    blocks = _live_blocks(cells)
    out = {
        "classes": classes,
        "classes_by_density": classes_by_density,
        "n_blocks": len(blocks),
        "variant": None,
        # Design §4: the natural-n arm exists to test the frozen prediction's
        # MECHANISM. A statistic the prediction says will move is not a test of
        # the prediction, so it can never enter this tree.
        "natural_arm_verdict_touching": False,
        "natural_l0_tracks_pool": natural_l0_tracks_pool,
        "slope": None,
        "p": None,
    }

    if not stage_a.get("pass"):
        return {**out, "verdict": "INSUFFICIENT_DATA",
                "reason": "stage A confirmation gate failed: "
                          + "; ".join(stage_a.get("failures", []))}

    if not below_silent:
        return {**out, "verdict": "INSUFFICIENT_DATA",
                "reason": "consistency check failed at 0.50 p_c — the sweep "
                          "implies structure where the closed 1b lubana_below "
                          "record found none, so the measure is wrong, not the "
                          "record"}

    if len(blocks) < MIN_LIVE_BLOCKS:
        return {**out, "verdict": "INSUFFICIENT_DATA",
                "reason": f"only {len(blocks)} live blocks of "
                          f"{len(SIZES) * len(SEEDS)}, floor is "
                          f"{MIN_LIVE_BLOCKS}"}

    test = slope_and_p(blocks, n_draw=n_draw, seed=seed)
    out.update(slope=test["slope"], p=test["p"], n_draw=test["n_draw"])

    if test["p"] < alpha and test["slope"] > 0:
        return {**out, "verdict": "PASS",
                "reason": f"depth margin rises with density: slope "
                          f"{test['slope']:.4f}, block p {test['p']:.5f}"}

    variant = None
    if classes["L0-only"]:
        variant = ("layer-0 leakage" if natural_l0_tracks_pool is True
                   else "layer-0, mechanism unconfirmed")
    return {**out, "verdict": "FAIL", "variant": variant,
            "reason": f"no detectable sub-critical accumulation: slope "
                      f"{test['slope']:.4f}, block p {test['p']:.5f}"}
