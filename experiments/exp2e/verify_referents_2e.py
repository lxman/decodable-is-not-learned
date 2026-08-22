"""The Exp 2e referent battery: every §4 referent re-asserted
EXECUTABLE against the real committed trees — run at build, re-run
cold at the freeze. Equivalent in content to what run()'s referent
phase enforces on the way to a verdict, and DELIBERATELY STOPS SHORT
of the verdict: no functional of the §5.1 family is evaluated against
the label on the real tallies here (that happens once, after the tag,
on Michael's go). 2d's committed numbers are known answers; F1's
correlation is not.

Numbered checks, all-or-nothing:
 1  2e's frozen-import pins (2d's instrument, 8 files) byte-identical;
    2d's own 17 frozen-import pins through 2d's check
 2  RUNG_ORDER_2D == 2c's two committed sources (2d's check); floors
    reproduce §4's table, six option-listing rungs at max(majority,
    1/n), criterion pins (2d's checks)
 3  referents_2e.json: file sha == the literal pin; 273 entries re-hash
    on the real tree; the builder is byte-idempotent on the tree
 4  2d's referents_2d.json through 2d's loader: file sha == 2d's
    literal, 250 entries re-hash
 5  2d's stream map == the frozen formula (2d's check)
 6  the OUTCOME known-answer gate: 2c's m5 rule on the committed m4
    records reproduces ascent_scores.json 34/34; 11 rising / 23 flat
    (9 at 12b only) in 7 families
 7  the MAIN tier: 68 cells re-tallied from raw bytes through 2d's
    loader == stored tallies == the §4 literal table (68/68)
 8  the PILOT tier: 68 cells re-tallied == stored; 4,000 draws each;
    seed 1000
 9  the 2d COMPARISON GATE: 2d's thresholded predictor + primary
    re-derived from the main cells through 2d's own code == 2d's
    results/verdict.json == the literal pin (AUC .5455, block p
    .6675, CI [.5, .6667], 2 drops, 11/23, FAIL)
10  2d's verdict.json: gate 1 clean 4/4 (128,000 draws compared, no
    diff cells), declared status literal, probe AUC .6008 == the pin,
    and the probe AUC recomputed from 2c's committed probe_scores on
    the same label == the record
11  the §6 tree is 2d's with the referent branch first (synthetic
    inputs only); the pilot/main ε are 1/8,000 and 1/64,000
12  the §5.1 family on SYNTHETIC tallies only: F1 at the floor is
    log(1 + ε/c), at zero log(ε/c); B0 = −log c; F3 residuals sum to
    zero and are orthogonal to the floor rank; the paired bootstrap's
    marginals == 2d's CI (no real tally touches a functional here)
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np

EXP2E = Path(__file__).resolve().parent
if str(EXP2E.parent.parent) not in sys.path:
    sys.path.insert(0, str(EXP2E.parent.parent))

from experiments.exp2d import analyze_2d as a2d  # noqa: E402
from experiments.exp2d import battery_2d as bt  # noqa: E402
from experiments.exp2d import stats_2d as st  # noqa: E402
from experiments.exp2e import analyze_2e as a  # noqa: E402
from experiments.exp2e import functionals_2e as fn  # noqa: E402
from experiments.exp2e import make_referents_2e as mk  # noqa: E402

CHECKS = []


def check(n, name):
    def deco(fn_):
        CHECKS.append((n, name, fn_))
        return fn_
    return deco


def _eq(got, want, what):
    if got != want:
        raise AssertionError(f"{what}: got {got!r}, want {want!r}")


@check(1, "frozen-import pins (2e's 8 over 2d; 2d's 17)")
def _c1(ctx):
    a.check_frozen_imports_2e()
    a2d.check_frozen_imports_2d()
    _eq(len(a.FROZEN_IMPORT_SHA256_2E), 8, "2e pins")
    _eq(len(a2d.FROZEN_IMPORT_SHA256_2D), 17, "2d pins")


@check(2, "rung order, floors, criterion pins (2d's checks)")
def _c2(ctx):
    bt.check_order_against_2c()
    ctx["battery"] = bt.load_battery()
    ctx["floors"] = bt.floor_table(ctx["battery"])
    bt.check_floors_against_doc(ctx["floors"])
    _eq(sum(1 for r in bt.RUNGS if ctx["floors"][r]["option_copy"]), 6,
        "option-listing rungs")


@check(3, "referents_2e.json: literal sha, 273 entries, idempotent")
def _c3(ctx):
    rec = a.load_manifest()
    _eq(rec["n_files"], 273, "n_files")
    _eq(a.check_manifest(a2d.EXP2D, rec), [], "manifest failures")
    tmp = EXP2E / "results" / ".referents_2e.rebuild.json"
    tmp.parent.mkdir(exist_ok=True)
    try:
        mk.build(a2d.EXP2D, tmp)
        _eq(tmp.read_bytes() == a.REFERENTS_PATH.read_bytes(), True,
            "builder byte-idempotent")
    finally:
        tmp.unlink(missing_ok=True)
    ctx["manifest"] = rec


@check(4, "2d's referents_2d.json through 2d's loader (250)")
def _c4(ctx):
    ref = a2d.load_referents()
    _eq(ref["n_files"], 250, "2d manifest n_files")
    ctx["ref2d"] = ref


@check(5, "2d's stream map == the frozen formula")
def _c5(ctx):
    r = a2d.check_stream_map_2d()
    _eq(r["n_cells"], 136, "stream map cells")


@check(6, "outcome known-answer gate 34/34; 11/23, 9 at 12b, 7 families")
def _c6(ctx):
    out = a2d.load_outcome(ctx["floors"], referents=ctx["ref2d"])
    _eq(out["known_answer_gate"], "PASS (34/34 rungs reproduce 2c's ascent)",
        "gate")
    _eq((out["n_rising"], out["n_rising_12b"],
         len(out["families_with_rising"])), (11, 9, 7), "labels")
    _eq(len(bt.RUNGS) - out["n_rising"], 23, "flat")
    ctx["outcome"] = out


@check(7, "main tier re-tally == stored == the §4 literal table (68/68)")
def _c7(ctx):
    cells = a2d.load_sampling_tier(a2d.EXP2D, "main", ctx["battery"],
                                   a2d.load_verify())
    _eq(len(cells), 68, "main cells")
    _eq(a.check_tally_pin(cells, a.MAIN_TALLY_PIN), [], "tally pin")
    _eq({c["n_draws"] for c in cells.values()}, {32_000}, "main draws")
    ctx["main"] = cells


@check(8, "pilot tier re-tally == stored; 4,000 draws; seed 1000")
def _c8(ctx):
    cells = a2d.load_sampling_tier(a2d.EXP2D, "pilot", ctx["battery"],
                                   a2d.load_verify())
    _eq(len(cells), 68, "pilot cells")
    _eq({c["n_draws"] for c in cells.values()}, {4_000}, "pilot draws")
    _eq(a2d.TIERS["pilot"]["seed"], 1000, "pilot seed")
    ctx["pilot"] = cells


@check(9, "2d comparison gate: re-derived == verdict.json == literal")
def _c9(ctx):
    cmp = a.comparison_2d(ctx["main"], ctx["floors"], ctx["outcome"])
    _eq(a.check_comparison_2d(cmp, a2d.EXP2D, a.VERDICT_2D_PIN), [],
        "comparison failures")
    _eq(cmp["auc"], 0.5454545454545454, "2d AUC")
    _eq(sum(1 for r in bt.RUNGS if cmp["predictor"][r] > 0), 1,
        "2d positive rungs")
    ctx["cmp"] = cmp


@check(10, "2d's verdict.json: gate 1 clean, status, probe AUC pin")
def _c10(ctx):
    v = json.loads((a2d.EXP2D / "results" / "verdict.json").read_text())
    _eq(v["gate1"]["diff_cells"], [], "gate-1 diff cells")
    _eq(v["gate1"]["total_draws_compared"], 128_000, "gate-1 draws")
    _eq(v["power"]["declared_status"], "DECLARED UNDERPOWERED IN ADVANCE",
        "declared status")
    _eq(v["secondaries"]["probe_predictor_auc"]["auc"], a.PROBE_2C_AUC_PIN,
        "probe AUC pin")
    probe = a2d.load_probe_predictor()
    y = a2d._labels(ctx["outcome"], "rising")
    xp = a2d._family_contiguous(probe)
    _eq(st.auc(xp, y), a.PROBE_2C_AUC_PIN, "probe AUC recomputed")
    _eq(a2d.VERDICT_2C_PIN["rho"], 0.3679488492919918, "2c rho pin")


@check(11, "the tree and the ε constants (synthetic inputs)")
def _c11(ctx):
    _eq(fn.verdict_tree_2e(referent_failures=["x"], auc_obs=1.0,
                           block_p=0.0, ci=[.9, 1.0])["verdict"],
        "INSUFFICIENT_DATA", "referent branch first")
    _eq(fn.verdict_tree_2e(referent_failures=[], auc_obs=.8, block_p=.001,
                           ci=[.6, .9])["verdict"], "PASS", "PASS")
    _eq(fn.verdict_tree_2e(referent_failures=[], auc_obs=.8, block_p=.001,
                           ci=[.5, .9])["verdict"], "FAIL", "FAIL")
    _eq((fn.EPS_MAIN, fn.EPS_PILOT), (1 / 64_000, 1 / 8_000), "eps")
    _eq((fn.ALPHA, fn.AUC_BAR), (st.ALPHA, st.AUC_BAR), "bars are 2d's")


@check(12, "the §5.1 family on synthetic tallies only")
def _c12(ctx):
    cells = {("g", s): {"verified": 640, "n_draws": 32_000, "rate": .02}
             for s in bt.PROBE_SIZES}
    floors = {"g": {"floor": .02, "majority_floor": .02}}
    t = fn.f1_table(cells, floors, rungs=("g",))
    _eq(abs(t["g"]["score"] - math.log(1 + (1 / 64_000) / .02)) < 1e-15,
        True, "F1 at floor")
    cells0 = {("g", s): {"verified": 0, "n_draws": 32_000, "rate": 0.0}
              for s in bt.PROBE_SIZES}
    t0 = fn.f1_table(cells0, floors, rungs=("g",))
    _eq(abs(t0["g"]["score"] - math.log((1 / 64_000) / .02)) < 1e-15, True,
        "F1 at zero")
    _eq(fn.b0_table(floors, rungs=("g",))["g"]["score"], -math.log(.02), "B0")
    rng = np.random.default_rng(0)
    rungs = tuple(f"r{i}" for i in range(8))
    fl = {r: {"floor": float(c), "majority_floor": float(c)}
          for r, c in zip(rungs, rng.uniform(.002, .25, 8))}
    cs = {(r, s): {"verified": int(v), "n_draws": 32_000, "rate": v / 32_000}
          for r in rungs for s, v in zip(bt.PROBE_SIZES,
                                         rng.integers(0, 6000, 2))}
    t3 = fn.f3_table(cs, fl, rungs=rungs)
    res = np.array([t3[r]["score"] for r in rungs])
    z = np.array([t3[r]["rank_floor"] for r in rungs])
    _eq(abs(res.sum()) < 1e-9 and abs(res @ (z - z.mean())) < 1e-9, True,
        "F3 residual identities")
    fams = [bt.FAMILY_OF[r] for r in bt.RUNGS]
    x1, x2 = rng.normal(size=34), rng.normal(size=34)
    y = np.array([1] * 11 + [0] * 23)
    counts = st.bootstrap_counts_matrix(bt.N_FAMILIES, n_boot=2000)
    pb = fn.cluster_bootstrap_auc_paired(x1, x2, y, fams, counts=counts)
    _eq(pb["ci_1"], st.cluster_bootstrap_auc(x1, y, fams, counts=counts)["ci"],
        "paired marginal == 2d")


def main() -> int:
    ctx = {}
    ok = 0
    for n, name, fn_ in CHECKS:
        try:
            fn_(ctx)
        except Exception as e:   # noqa: BLE001
            print(f"  [{n:2d}] FAIL  {name}: {type(e).__name__}: {e}")
            return 1
        ok += 1
        print(f"  [{n:2d}] ok    {name}", flush=True)
    print(f"referent battery: {ok}/{len(CHECKS)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
