# experiments/exp4/verify_referents_4.py
"""The Exp 4 referent battery (Task 5 brief's 11 items; 2n's `@check`
shape): every pre-campaign referent re-asserted EXECUTABLE against the
committed trees — run at build, re-run cold at the freeze. Stops SHORT
of any alignment statistic (no k-NN, no overlap, no CKA) — those need
exp4's own campaign, which has not run.

 1  frozen pins byte-identical (`battery_4.check_frozen_4`; prints
    "empty" when FROZEN_SHA256_4 is not yet pinned)
 2  the closed tags of the four upstream trajectory experiments exist:
    `exp2g-closed`, `exp2i-closed`, `exp2m-closed`, `exp2n-closed`
 3  `referents_4.json`: `make_referents_4.check_referents` at the pin
    returns zero failures
 4  the four manifests load at their pins with `GRID_4` reproduced
    (`battery_4.manifests_4`, which raises on any grid mismatch)
 5  the four rung sets reproduce `RUNG_SET_PIN_4` AND `t_clear ==
    T_CLEAR_PIN_4` (`battery_4.check_rung_set_pins_4`, both halves once
    `T_CLEAR_PIN_4` is pinned)
 6  every grid step's + every endpoint's + every init's committed
    digest is readable and non-empty (92 grid steps + 4 inits = 96)
 7  `metric_4`'s planted-calibration fixture reproduced byte-for-byte
 8  `analyze_4.s2_known_answer_gates_4()` reproduces 2d's AUC
    .5454545454545454 and 2e's .6126482213438735 exactly
 9  `metric_4.SITE_COUNT_PIN_4` / `battery_4.N_HIDDEN_PIN_4` consistent
    (every n_hidden value used by an exp4 key has a pinned site count,
    and `sites_4` reproduces it)
10  `battery_4.PYTHIA_COMMITS_4`'s three scanned shas equal
    `hub_inventory_pythia_4.json`'s
11  the referent manifest's file count: `make_referents_4.
    referent_files()` (live) == `N_FILES_4` == the committed
    `referents_4.json`'s own `n_files`
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

EXP4 = Path(__file__).resolve().parent
EXPERIMENTS = EXP4.parent
REPO = EXPERIMENTS.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp2d import stats_2d as st  # noqa: E402
from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp2g import predictor_2g as pr  # noqa: E402
from experiments.exp4 import analyze_4 as an  # noqa: E402
from experiments.exp4 import battery_4  # noqa: E402
from experiments.exp4 import make_referents_4 as mkr  # noqa: E402
from experiments.exp4 import metric_4  # noqa: E402

CHECKS = []


def check(n, name):
    def deco(fn_):
        CHECKS.append((n, name, fn_))
        return fn_
    return deco


def _eq(got, want, what):
    if got != want:
        raise AssertionError(f"{what}: got {got!r}, want {want!r}")


CLOSED_TAGS_4 = ("exp2g-closed", "exp2i-closed", "exp2m-closed", "exp2n-closed")


@check(1, "frozen pins byte-identical")
def _c1(ctx):
    if not battery_4.FROZEN_SHA256_4:
        return "SKIP"
    battery_4.check_frozen_4()


@check(2, "the four upstream experiments' closed tags exist")
def _c2(ctx):
    missing = [t for t in CLOSED_TAGS_4 if not pr.git_tag_exists(t)]
    if missing:
        raise AssertionError(f"missing tags: {missing}")


@check(3, "referents_4.json at the pin, zero failures")
def _c3(ctx):
    if an.REFERENTS_4_SHA256 is None:
        return "SKIP"
    bad = mkr.check_referents(battery_4.EXP4 / "referents_4.json", sha_pin=an.REFERENTS_4_SHA256)
    if bad:
        raise AssertionError(f"{len(bad)} referent failure(s): {bad[:5]}")


@check(4, "the four manifests load at their pins, GRID_4 reproduced")
def _c4(ctx):
    m = battery_4.manifests_4()
    _eq(set(m), set(battery_4.TRAJECTORIES_4), "manifests_4 keys")


@check(5, "the four rung sets reproduce RUNG_SET_PIN_4 and t_clear == T_CLEAR_PIN_4")
def _c5(ctx):
    if battery_4.T_CLEAR_PIN_4 is None:
        return "SKIP"
    floors = bg.load_floors()
    battery = ctx.setdefault("battery", None)
    from experiments.exp2d import battery_2d as bt
    if battery is None:
        battery = bt.load_battery()
        ctx["battery"] = battery
    for traj in battery_4.TRAJECTORIES_4:
        outcome = battery_4.load_outcome_4(traj, battery=battery)
        rs = battery_4.rung_sets_4(outcome, floors)
        bad = battery_4.check_rung_set_pins_4(traj, rs)
        if bad:
            raise AssertionError(f"{traj}: {bad}")
        ctx.setdefault("rung_sets", {})[traj] = rs


@check(6, "every grid step's + endpoint's + init's committed digest is readable (92 + 4)")
def _c6(ctx):
    n = 0
    for traj in battery_4.TRAJECTORIES_4:
        for step in battery_4.GRID_4[traj]:
            d = battery_4.committed_step_digest_4(traj, step)
            if not d:
                raise AssertionError(f"{traj} step{step}: empty digest")
            n += 1
        d = battery_4.committed_init_digest_4(traj)
        if not d:
            raise AssertionError(f"{traj}: empty init digest")
        n += 1
    _eq(n, 96, "grid steps (92) + inits (4)")


@check(7, "metric_4's planted-calibration fixture reproduced")
def _c7(ctx):
    import numpy as np
    fixture = json.loads((EXP4 / "tests" / "fixtures" / "calibration_curve_4.json").read_text())
    levels = [i / 19 for i in range(20)]
    curve = []
    for s in levels:
        vals = []
        for seed in range(5):
            X, Y = metric_4.planted_pair(500, 64, s, seed)
            vals.append(metric_4.mutual_knn_from_sets(metric_4.knn_sets(X), metric_4.knn_sets(Y))["mean"])
        curve.append(float(np.mean(vals)))
    _eq(levels, fixture["levels"], "calibration levels")
    for got, want in zip(curve, fixture["curve"]):
        if abs(got - want) > 1e-9:
            raise AssertionError(f"calibration curve drift: {got} != {want}")


@check(8, "S2 known-answer AUCs (.5455 / .6126) exact")
def _c8(ctx):
    res = an.s2_known_answer_gates_4()
    if abs(res["auc_2d"] - 0.5454545454545454) >= 1e-12:
        raise AssertionError(f"2d AUC drift: {res['auc_2d']}")
    if abs(res["auc_2e"] - 0.6126482213438735) >= 1e-12:
        raise AssertionError(f"2e AUC drift: {res['auc_2e']}")


@check(9, "SITE_COUNT_PIN_4 / N_HIDDEN_PIN_4 consistent")
def _c9(ctx):
    used_n_hidden = set(battery_4.N_HIDDEN_PIN_4.values())
    missing = used_n_hidden - set(metric_4.SITE_COUNT_PIN_4)
    if missing:
        raise AssertionError(f"n_hidden values with no pinned site count: {missing}")
    for n_hidden, want in metric_4.SITE_COUNT_PIN_4.items():
        got = len(metric_4.sites_4(n_hidden))
        if got != want:
            raise AssertionError(f"sites_4({n_hidden}) = {got} != pinned {want}")


@check(10, "the Pythia inventory's three commits equal the literals")
def _c10(ctx):
    inv = battery_4.load_pythia_inventory_4()
    for size in battery_4._PYTHIA_SCAN_SIZES:
        got = inv["commits"][size]
        want = battery_4.PYTHIA_COMMITS_4[size]
        _eq(got, want, f"{size} commit")


@check(11, "the referent manifest's file count: live == N_FILES_4 == committed n_files")
def _c11(ctx):
    live = len(mkr.referent_files())
    _eq(live, mkr.N_FILES_4, "live referent_files() count vs N_FILES_4")
    committed = json.loads((EXP4 / "referents_4.json").read_text())
    _eq(committed["n_files"], mkr.N_FILES_4, "committed referents_4.json n_files vs N_FILES_4")


def main() -> int:
    ctx = {}
    n_ok = 0
    for n, name, fn_ in CHECKS:
        try:
            result = fn_(ctx)
        except Exception as e:  # noqa: BLE001
            print(f"  [{n:2d}] FAIL  {name}: {type(e).__name__}: {e}")
            return 1
        if result == "SKIP":
            print(f"  [{n:2d}] skip  {name} (pin not yet set)", flush=True)
        else:
            print(f"  [{n:2d}] ok    {name}", flush=True)
            n_ok += 1
    print(f"referent battery: {n_ok}/{len(CHECKS)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
