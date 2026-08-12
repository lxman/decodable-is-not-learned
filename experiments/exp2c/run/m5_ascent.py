"""Scale-ascent score — the OUTCOME side of Exp 2c (design §3).

RULED 2026-08-11 (Michael): mirror the probe side exactly.

    probe   margin = (starved-val acc - null mean) / (1 - null mean),
                     zero below the significance bar
            score  = seed-mean, then mean over the two probe sizes

    eval    margin = (trained acc - untrained floor) / (1 - untrained floor),
                     zero below the significance bar
            score  = mean over the three eval sizes

Symmetry between predictor and outcome is the point of the ruling: two
different rules for "what counts as signal" on the two sides of a rank
correlation would be a degree of freedom, and one that could be chosen
after seeing the data.

The significance bar. The probe side's bar is a hypothesis test at
alpha .01 (permutation null, Bonferroni over candidates) — NOT an
interval-overlap rule — so the eval side uses a hypothesis test too:
Fisher exact, one-sided, trained against its own empirical untrained
floor, judged per (rung, size) cell at the same alpha. Exact rather
than approximate, consistent with the harness's existing
Clopper-Pearson choice, and it introduces no fitted or extrapolated
quantity (design §3 forbids those). Multiplicity mirrors the probe side
too: each rung is judged on its own, exactly as each probe fit is.

CP bounds ride on every cell, zero or not (design §4: "every zero a CP
bound").

WRITTEN AND FROZEN WHILE M4 WAS STILL RUNNING, with its numbers
unlooked-at. Every test in tests/test_m5_ascent.py runs on synthetic
cells for that reason. The rule was fixed before the data could
influence it, which is the only thing that makes it a preregistration
rather than a post hoc choice.
"""

from __future__ import annotations

import json
from pathlib import Path

try:  # experiments.exp2c.run.m5_ascent (pytest / absolute import)
    from ..analyze import AnalyzeInputs
    from ..harness import clopper_pearson
    from . import campaign_m4 as m4
except ImportError:  # pragma: no cover - `python -m run.m5_ascent`
    from analyze import AnalyzeInputs
    from harness import clopper_pearson
    import run.campaign_m4 as m4

EXP_DIR = Path(__file__).resolve().parent.parent
RESULTS = EXP_DIR / "results"

ALPHA = 0.01                     # the probe side's bar, mirrored
EVAL_SIZES = m4.EVAL_SIZES


# ------------------------------------------------------------ the margin

def ascent_margin(trained: dict, untrained: dict, alpha: float = ALPHA) -> dict:
    """One (rung, size) cell's normalized argmax margin.

    Zero unless the trained arm beats its own empirical floor by a
    one-sided Fisher exact test at `alpha`. Never negative."""
    from scipy.stats import fisher_exact

    t_k, t_n = int(trained["correct"]), int(trained["n"])
    u_k, u_n = int(untrained["correct"]), int(untrained["n"])
    t_acc, u_acc = t_k / t_n, u_k / u_n

    # rows = (trained, untrained), cols = (correct, wrong)
    _, p = fisher_exact([[t_k, t_n - t_k], [u_k, u_n - u_k]],
                        alternative="greater")
    significant = bool(p < alpha) and t_acc > u_acc
    margin = (t_acc - u_acc) / (1.0 - u_acc) if significant else 0.0

    return {"margin": float(max(0.0, margin)),
            "significant": significant,
            "p": float(p),
            "trained_acc": t_acc,
            "untrained_floor": u_acc,
            "trained_cp95": list(clopper_pearson(t_k, t_n)),
            "untrained_cp95": list(clopper_pearson(u_k, u_n))}


def rung_ascent_score(cells: dict, alpha: float = ALPHA) -> dict:
    """Mean normalized margin across the three eval sizes.

    `cells` maps size -> (trained_result, untrained_result). All three
    sizes are required: a rung averaged over a different denominator
    than its neighbours would carry a silently different meaning into
    the ranking."""
    missing = [s for s in EVAL_SIZES if s not in cells]
    if missing:
        raise ValueError(f"missing eval sizes {missing}; "
                         f"the ascent score is a mean over all of "
                         f"{list(EVAL_SIZES)}")
    per_size = {s: ascent_margin(cells[s][0], cells[s][1], alpha)
                for s in EVAL_SIZES}
    score = sum(v["margin"] for v in per_size.values()) / len(EVAL_SIZES)
    return {"ascent_score": float(score), "per_size": per_size}


# --------------------------------------------------------- the assembly

def _cell_path(results_dir: Path, size: str, mode: str, name: str) -> Path:
    return Path(results_dir) / "m4" / f"{size}_{mode}" / f"{name}.json"


def assemble(results_dir=None, out_path=None, write=True,
             alpha: float = ALPHA) -> dict:
    """Score every rung from the completed M4 campaign.

    Refuses on an incomplete campaign: ranking rungs against different
    amounts of evidence is exactly the kind of quiet bias the design's
    'no fitted or extrapolated quantities' rule exists to prevent."""
    results_dir = Path(results_dir) if results_dir else RESULTS
    out_path = Path(out_path) if out_path else results_dir / "ascent_scores.json"

    names = m4.eval_capability_names()
    wanted = [(s, m, n) for s in EVAL_SIZES for m in m4.MODES for n in names]
    absent = [c for c in wanted if not _cell_path(results_dir, *c).exists()]
    if absent:
        raise RuntimeError(
            f"refusing to score an incomplete M4 campaign: "
            f"{len(absent)} of {len(wanted)} cells missing "
            f"(e.g. {'/'.join(absent[0])})")

    rungs = {}
    for name in names:
        cells = {}
        for size in EVAL_SIZES:
            cells[size] = tuple(
                json.loads(_cell_path(results_dir, size, mode, name).read_text())
                for mode in ("trained", "untrained"))
        rungs[name] = rung_ascent_score(cells, alpha)

    record = {
        "outcome": "scale-ascent score (design §3): mean normalized "
                   "argmax margin over 2.8b/6.9b/12b, zero below the "
                   "significance bar",
        "rule": "mirrors the probe side (ruled Michael 2026-08-11); "
                "bar = one-sided Fisher exact vs the empirical untrained "
                "floor at alpha",
        "alpha": alpha,
        "eval_sizes": list(EVAL_SIZES),
        "n_rungs": len(rungs),
        "n_nonzero": int(sum(v["ascent_score"] > 0 for v in rungs.values())),
        "rungs": rungs,
    }
    if write:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(record, indent=1))
    return record


# ------------------------------------------------------------- the join

def join(probe: dict, ascent: dict) -> AnalyzeInputs:
    """Merge the Stage 1 predictor with the M4 outcome into the frozen
    analysis's input, preserving the family-block order probe_scores.json
    was written in."""
    rungs = []
    for r in probe["rungs"]:
        a = ascent["rungs"].get(r["name"])
        if a is None:
            raise ValueError(
                f"{r['name']} is scored on the probe side but has no "
                f"ascent score")
        rungs.append(dict(r, ascent_score=float(a["ascent_score"])))
    return AnalyzeInputs(rungs=rungs,
                         untrained_fires=probe["untrained_fires"],
                         shuffled_fires=probe["shuffled_fires"])


def main(argv=None) -> None:
    rec = assemble()
    print(f"[m5] ascent scores -> {RESULTS / 'ascent_scores.json'}", flush=True)
    print(f"[m5] {rec['n_rungs']} rungs, {rec['n_nonzero']} with "
          f"nonzero ascent", flush=True)
    print("[m5] the verdict projection goes in the ledger BEFORE "
          "analyze.py runs (standing practice).", flush=True)


if __name__ == "__main__":
    main()
