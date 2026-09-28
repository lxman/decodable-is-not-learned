# experiments/exp6/power_6.py
"""ONE power record (design §4), written at the endpoint stage after the
rung sets and before the projection: 2i's machinery
(`power_2i._one_test_power`) run once per test — eight tests, two
predictors by four families — on the REAL sealed predictors in the
battery's own strata, n_pos bounded below by each family's stage-1
endpoint count, y from a latent mixing rank(x) at calibrated strength,
every simulated cell through `analyze_2i.fires_2i`. Bar per test:
P(fires | D = .15) >= .75, else DECLARED UNDERPOWERED IN ADVANCE.

Then the TREE, which no earlier experiment had: a predictor holds when
it fires on three of four families. Families are simulated
independently — a modelling choice, printed as one; the families' real
orders are correlated (2m's S8 read .23-.46) and the record cannot know
by how much before the sweep. The two predictors are read on the SAME
outcomes, so their joint is not simulated at all: P(GENERAL) and
P(BATTERY-BOUND) are printed as Fréchet BOUNDS, not as numbers.

Predictor A's four 64-draw blocks' SD per family (2k's process note).
The pilot tier feeds NOTHING here: liveness is what the sealed main tier
shows, and the degenerate rungs are dropped by the analyzer's own rule.

    python -m experiments.exp6.power_6 [--jobs 8]   (writes power_6.json ONCE)
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

EXP6 = Path(__file__).resolve().parent
REPO = EXP6.parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp6 import battery_6 as b6  # noqa: E402
from experiments.exp6 import families_6 as fm  # noqa: E402
from experiments.exp6 import records_6 as r6  # noqa: E402
from experiments.exp6 import strata_6 as s6  # noqa: E402

TESTS_6 = tuple((t, f) for t in ("A", "B") for f in fm.FAMILIES_6)
HOLDS_AT = 3                       # families a predictor must fire on (design §1)
MIN_RUNGS = 3                      # rungs a test must read to be EVALUABLE
N_SIM_BLOCKS = 200
STATUSES_6 = ("POWERED", "DECLARED UNDERPOWERED IN ADVANCE", "THIN")
INDEPENDENCE_NOTE_6 = (
    "Tree-level figures treat the four families as independent given the "
    "alternative. That is a modelling choice: the families' real orders are "
    "correlated (2m's S8 read .23-.46 on 2c's battery), which raises the chance "
    "that the tests fire or fail TOGETHER and so widens both tails of the count "
    "of firing families. The two predictors are read on the same outcomes and "
    "their joint is not modelled: every figure that involves both is a Fréchet "
    "bound.")
NOTE_6 = (
    "Computed at the endpoint stage from the REAL sealed predictors and the four "
    "families' stage-1 endpoint counts: a claim about each test's RESOLUTION in "
    "the battery's strata, not about what will be found. P(fires | D = .10) is "
    "the coin-flip statement — the T >= .10 bar decides, not p.")


def test_name(test: str, family: str) -> str:
    return f"{test}:{family}"


def poisson_binomial_at_least(ps, k: int) -> float:
    """P(at least k of the independent events occur)."""
    dist = [1.0]
    for p in ps:
        nxt = [0.0] * (len(dist) + 1)
        for j, v in enumerate(dist):
            nxt[j] += v * (1.0 - p)
            nxt[j + 1] += v * p
        dist = nxt
    return float(sum(dist[k:]))


def frechet(p: float, q: float) -> list:
    """Bounds on P(both) from the two marginals alone."""
    return [max(0.0, p + q - 1.0), min(p, q)]


def tree_level(tests: dict) -> dict:
    """From the eight per-test records: per predictor, P(holds) at each
    D and under the null over its EVALUABLE families; then the bounds
    on the two worlds a decision rests on."""
    out = {"independence_note": INDEPENDENCE_NOTE_6, "holds_at": HOLDS_AT,
           "predictors": {}}
    # every target any test was simulated at: a predictor with too few
    # evaluable families still gets a row at each (it cannot hold: 0)
    keys = sorted({d for r in tests.values() for d in (r.get("targets") or {})})
    for t in ("A", "B"):
        rows = {f: tests[test_name(t, f)] for f in fm.FAMILIES_6}
        ev = [f for f in fm.FAMILIES_6 if not rows[f]["thin"]]
        rec = {"evaluable": ev, "status_if_nothing_else": ("U" if len(ev) < 3 else None),
               "p_holds": {}, "p_fails": {}}
        for d in keys + ["null"]:
            ps = [(rows[f]["null"]["false_fire_rate"] if d == "null"
                   else rows[f]["targets"][d]["p_fires"]) for f in ev]
            if len(ev) < 3:
                rec["p_holds"][d], rec["p_fails"][d] = 0.0, 0.0
                continue
            rec["p_holds"][d] = poisson_binomial_at_least(ps, HOLDS_AT)
            rec["p_fails"][d] = 1.0 - poisson_binomial_at_least(ps, 2)
        out["predictors"][t] = rec
    a, b = out["predictors"]["A"], out["predictors"]["B"]
    out["p_general"] = {d: frechet(a["p_holds"][d], b["p_holds"][d])
                        for d in a["p_holds"] if d in b["p_holds"]}
    out["p_battery_bound"] = {d: frechet(a["p_fails"][d], b["p_fails"][d])
                              for d in a["p_fails"] if d in b["p_fails"]}
    return out


def declaration_failures(name: str, rec: dict) -> list:
    """A per-test record's declaration RE-DERIVED from its own numbers
    (Exp 4 F-4: a declaration is a measurement, not an attestation)."""
    from experiments.exp2i import power_2i as pw
    bad = []
    if rec.get("declared_status") not in STATUSES_6:
        return [f"6 power {name}: declared_status {rec.get('declared_status')!r}"]
    keep = rec.get("rungs_simulated")
    if rec.get("thin") != (len(keep or []) < MIN_RUNGS):
        bad.append(f"6 power {name}: thin is not len(rungs_simulated) < {MIN_RUNGS}")
    if not keep:
        if rec["declared_status"] != "THIN":
            bad.append(f"6 power {name}: nothing simulated and not declared THIN")
        return bad
    at = (rec.get("targets") or {}).get(str(pw.DECLARE_AT))
    if at is None:
        return bad + [f"6 power {name}: no target at D = {pw.DECLARE_AT}"]
    want = "POWERED" if at["p_fires"] >= pw.BAR else "DECLARED UNDERPOWERED IN ADVANCE"
    if rec["declared_status"] != want:
        bad.append(f"6 power {name}: declared {rec['declared_status']} against "
                   f"P(fires) {at['p_fires']} and the bar {pw.BAR}")
    for k, v in (("bar", pw.BAR), ("declare_at", pw.DECLARE_AT), ("n_sim", pw.N_SIM),
                 ("n_perm", pw.N_PERM_POWER)):
        if rec.get(k) != v:
            bad.append(f"6 power {name}: {k} {rec.get(k)!r} against {v!r}")
    return bad


def claim_failures(power: dict, inputs: dict) -> list:
    """The record's claims against what the analyzer holds: the rungs
    of each test, the endpoint's lower bound, the degeneracy rule, the
    grid length, the tree — all re-derived (2m R-1's lineage)."""
    from experiments.exp2i import analyze_2i as an2i
    bad = []
    tests = power.get("tests") or {}
    if sorted(tests) != sorted(test_name(t, f) for t, f in TESTS_6):
        return [f"6 power: tests {sorted(tests)} are not the eight"]
    for t, f in TESTS_6:
        name, rec, inp = test_name(t, f), tests[test_name(t, f)], inputs[(t, f)]
        rungs = list(inp["rungs"])
        if rec.get("rungs") != rungs:
            bad.append(f"6 power {name}: rungs are not R_f")
        if rec.get("n_pos_lower_bound") != {r: int(inp["n_pos"][r]) for r in rungs}:
            bad.append(f"6 power {name}: n_pos_lower_bound is not the endpoint's")
        if rec.get("n_trained_steps") != inp["n_steps"]:
            bad.append(f"6 power {name}: n_trained_steps is not the grid's length")
        dropped = list(an2i._degenerate_rungs(inp["x"], inp["strata"], rungs))
        if rec.get("dropped_degenerate") != dropped:
            bad.append(f"6 power {name}: dropped_degenerate does not re-derive")
        if rec.get("rungs_simulated") != [r for r in rungs if r not in dropped]:
            bad.append(f"6 power {name}: rungs_simulated does not re-derive")
        if (rec.get("t_bar"), rec.get("alpha")) != (an2i.T_BAR, an2i.ALPHA):
            bad.append(f"6 power {name}: t_bar / alpha")
        bad += declaration_failures(name, rec)
    if not bad and power.get("tree") != tree_level(tests):
        bad.append("6 power: the tree-level figures do not re-derive from the tests")
    return bad


def _worker(job):
    """One test's power in its own process (deterministic: every seed is
    fixed inside 2i's machinery, so the pool's order changes nothing)."""
    name, strata, x, n_pos, rungs, n_steps = job
    from experiments.exp2i import power_2i as pw
    rec = pw._one_test_power(strata, x, n_pos, rungs, n_steps=n_steps)
    return name, rec


def compute(inputs: dict, *, jobs: int = 1, blocks=None) -> dict:
    """`inputs[(test, family)]` = {"x","strata","n_pos","rungs","n_steps"}
    (+ "bits" for Test A when `blocks` is wanted)."""
    work = [(test_name(t, f), inputs[(t, f)]["strata"], inputs[(t, f)]["x"],
             inputs[(t, f)]["n_pos"], tuple(inputs[(t, f)]["rungs"]),
             inputs[(t, f)]["n_steps"]) for t, f in TESTS_6]
    if jobs > 1:
        import multiprocessing as mp
        with mp.get_context("spawn").Pool(jobs) as pool:
            done = dict(pool.map(_worker, work))
    else:
        done = dict(_worker(w) for w in work)
    tests = {}
    for t, f in TESTS_6:
        rec = done[test_name(t, f)]
        rec.update({"test": t, "family": f, "predictor": r6.TEST_PREDICTOR[t]})
        tests[test_name(t, f)] = rec
    out = {"tests": tests, "tree": tree_level(tests), "note": NOTE_6}
    if blocks is not None:
        out["block_sd_A"] = {f: blocks(inputs[("A", f)]) for f in fm.FAMILIES_6}
    return out


def block_sd(inp: dict) -> dict:
    from experiments.exp2n import power_2n as p2n
    if len(inp["rungs"]) == 0:
        return {"n_sim": 0, "note": "R_f is empty; nothing simulated"}
    return p2n.block_sd_A(inp["strata"], inp["bits"], inp["x"], inp["n_pos"],
                          tuple(inp["rungs"]), n_steps=inp["n_steps"],
                          n_sim=N_SIM_BLOCKS)


def real_inputs(root) -> tuple:
    """The eight tests' inputs from the sealed tree, through the
    analyzer's own loaders. Refuses on any failure."""
    from experiments.exp6 import analyze_6 as an
    ctx, bad = an.load_sealed_stages(root)
    if bad:
        raise RuntimeError(f"refusing: the sealed stages do not re-derive: {bad[:5]}")
    return an.test_inputs(ctx), ctx


def main(argv=None, *, root=EXP6, tag_exists=None, blob_sha=None, blobs_bound=None,
         frozen_check=None) -> dict:
    from experiments.exp2i import power_2i as pw
    from experiments.exp6 import analyze_6 as an
    from experiments.exp6.run import _common_6 as cm
    from experiments.exp6.run import endpoint_6 as ep
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, default=8)
    a = ap.parse_args(argv)
    cm.gates(tag_exists=tag_exists, blob_sha=blob_sha, frozen_check=frozen_check)
    seal = ep.require_predictor_seal(root, tag_exists=tag_exists,
                                     blobs_bound=blobs_bound)
    out = r6.power_path(root)
    if out.exists():
        raise RuntimeError(f"{out} exists — the power record is written ONCE")
    if not r6.rung_sets_path(root).is_file():
        raise RuntimeError("the rung sets are missing — seal the endpoint stage first")
    inputs, _ = real_inputs(root)
    rec = compute(inputs, jobs=a.jobs, blocks=block_sd)
    cm.exit_gate(r6.endpoint_halt_path(root), frozen_check=frozen_check)
    rec.update({"predictor_sha256": seal["sha256"],
                "rung_sets_sha256": r6.sha256_file(r6.rung_sets_path(root)),
                "calibration_note": an.CALIBRATION_SENTENCE_6,
                "shape_note": pw.SHAPE_NOTE_2I, "prereg_tag": r6.PREREG_TAG_6,
                "git_sha": cm.p6.git_sha()})
    from experiments.exp2i import analyze_2i as an2i
    r6.write_json(out, an2i._json_safe(rec))
    for name, t in rec["tests"].items():
        print(f"{name:14s} {t['declared_status']:34s} {t.get('declaration', '')}")
    print("P(GENERAL | D = .15) in", rec["tree"]["p_general"].get("0.15"))
    print("P(BATTERY-BOUND | null) in", rec["tree"]["p_battery_bound"].get("null"))
    return rec


if __name__ == "__main__":
    main()
