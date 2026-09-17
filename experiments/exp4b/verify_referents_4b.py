# experiments/exp4b/verify_referents_4b.py
"""The Exp 4b referent battery (Task 5 brief's 10 items; 2n's/exp4's
own `@check` shape): every referent re-asserted EXECUTABLE against the
real, closed exp4 tree -- run at build, re-run cold at the freeze.
Every check here stops SHORT of any placebo quantity (no battery is
drawn, no null is calibrated, `power_ext_4b.reproduce_power_record_4b`
is never called) -- checks (4)/(5)/(6) re-derive gates (1)/(3)/(5)
directly (`analyze_4b.gate1_rederive_4b`/`gate3_rederive_4b`/
`gate5_rederive_4b`, the SAME functions `analyze_4b.run()` calls,
called here cold on the real tree rather than through a second full
`run()` execution), and check (9) re-derives gate (2). Committed bytes
throughout: no model contact, no placebo battery."""
from __future__ import annotations

import json
import sys
from pathlib import Path

EXP4B = Path(__file__).resolve().parent
EXPERIMENTS = EXP4B.parent
REPO = EXPERIMENTS.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp2g import predictor_2g as pr  # noqa: E402
from experiments.exp4 import analyze_4 as an  # noqa: E402
from experiments.exp4 import battery_4  # noqa: E402
from experiments.exp4 import collect_4  # noqa: E402
from experiments.exp4b import analyze_4b as an4b  # noqa: E402
from experiments.exp4b import battery_4b  # noqa: E402
from experiments.exp4b import make_referents_4b as mkr4b  # noqa: E402

CHECKS = []


def check(n, name):
    def deco(fn_):
        CHECKS.append((n, name, fn_))
        return fn_
    return deco


def _eq(got, want, what):
    if got != want:
        raise AssertionError(f"{what}: got {got!r}, want {want!r}")


EXP4_TAGS_4B = (battery_4.PREREG_TAG_4, battery_4.REFERENCE_SEAL_TAG_4, battery_4b.EXP4_CLOSED_TAG)


@check(1, "battery_4b.check_exp4_closed_4b (upstream frozen pins + exp4-closed's own seven)")
def _c1(ctx):
    battery_4b.check_exp4_closed_4b()


@check(2, "exp4's three tags exist, exp4-closed binds EXP4_CLOSED_SHA256_4B")
def _c2(ctx):
    missing = [t for t in EXP4_TAGS_4B if not pr.git_tag_exists(t)]
    if missing:
        raise AssertionError(f"missing tags: {missing}")
    bad = []
    for rel, want in battery_4b.EXP4_CLOSED_SHA256_4B.items():
        got = pr.git_blob_sha256(battery_4b.EXP4_CLOSED_TAG, rel)
        if got != want:
            bad.append(f"{rel}: tag {str(got)[:12]} vs pin {want[:12]}")
    if bad:
        raise AssertionError(f"exp4-closed does not bind: {bad}")


@check(3, "referents_4b.json at the pin, zero failures")
def _c3(ctx):
    if an4b.REFERENTS_4B_SHA256 is None:
        return "SKIP"
    bad = mkr4b.check_referents_4b(an4b.REFERENTS_PATH_4B, sha_pin=an4b.REFERENTS_4B_SHA256)
    if bad:
        raise AssertionError(f"{len(bad)} referent failure(s): {bad[:5]}")


def _load_real_tree(ctx) -> dict:
    """Every input `analyze_4b`'s gates need, loaded once and cached on
    `ctx` for checks (4)/(5)/(6)/(9) to share -- no placebo quantity."""
    if "real" in ctx:
        return ctx["real"]
    root4 = battery_4.EXP4
    v4 = battery_4b.load_exp4_verdict_4b(root4)
    elig4 = battery_4b.load_exp4_eligibility_4b(root4)
    T4 = battery_4b.T_4_from_verdict_4b(v4)
    cells4 = battery_4b.cells_from_verdict_4b(v4)

    from experiments.exp2d import battery_2d as bt
    from experiments.exp2g import battery_2g as bg
    battery = bt.load_battery()
    floors = bg.load_floors()
    rung_sets = {}
    for traj in battery_4.TRAJECTORIES_4:
        outcome = battery_4.load_outcome_4(traj, battery=battery)
        rung_sets[traj] = battery_4.rung_sets_4(outcome, floors)

    stage_keys = list(battery_4.STAGE1_KEYS_4) + list(battery_4.STAGE1_FIRST_UNITS_4)
    stage_tables_4 = an.load_stage_tables_4(root4, keys=stage_keys)
    series_by_traj = {}
    for traj in battery_4.TRAJECTORIES_4:
        sweep_tables = an.load_sweep_tables_4(root4, traj)
        refs = battery_4.REFS_FOR_4[traj]
        ref_tables_raw = collect_4.load_ref_tables_4(root4, refs)
        ref_tables = {ref: rt["sets"] for ref, rt in ref_tables_raw.items()}
        series_by_traj[traj] = an.alignment_series_4(root4, traj, ref_tables, sweep_tables)

    real = {"root4": root4, "v4": v4, "elig4": elig4, "T4": T4, "cells4": cells4,
           "rung_sets": rung_sets, "stage_tables_4": stage_tables_4,
           "series_by_traj": series_by_traj}
    ctx["real"] = real
    return real


@check(4, "gate (1): T_4 literal re-derived from the real committed tree")
def _c4(ctx):
    real = _load_real_tree(ctx)
    g1 = an4b.gate1_rederive_4b(real["series_by_traj"], real["rung_sets"], real["elig4"],
                                real["cells4"], real["T4"])
    if not g1["pass"]:
        raise AssertionError(f"gate 1 disagrees: {g1}")
    print(f"       gate 1: T_4 = {g1['T_rederived']}", flush=True)


@check(5, "gate (3): lambda_hat re-derived")
def _c5(ctx):
    real = _load_real_tree(ctx)
    g3 = an4b.gate3_rederive_4b(real["series_by_traj"], real["rung_sets"], real["elig4"],
                                real["v4"])
    if not g3["pass"]:
        raise AssertionError(f"gate 3 disagrees: {g3}")
    print(f"       gate 3: lambda_hat = {g3['lambda_by_traj']}", flush=True)


@check(6, "gate (5): gate 0 fractions (site 0 excluded)")
def _c6(ctx):
    real = _load_real_tree(ctx)
    g5 = an4b.gate5_rederive_4b(real["root4"], real["stage_tables_4"], real["v4"])
    if not g5["pass"]:
        raise AssertionError(f"gate 5 disagrees: {g5}")
    # m6 (final review): assert the re-derived fraction against the
    # committed v4["gate0"][traj]["fraction_below"] directly, not only
    # `g5["pass"]` (which already made this comparison internally, but
    # this check's own job is to re-assert it against the committed
    # bytes, not merely trust the gate's verdict).
    committed_gate0 = real["v4"].get("gate0") or {}
    for traj in battery_4.TRAJECTORIES_4:
        want = (committed_gate0.get(traj) or {}).get("fraction_below")
        got = (g5["per_traj"].get(traj) or {}).get("got")
        _eq(got, want, f"{traj} gate0 fraction_below (re-derived vs committed v4)")
    print(f"       gate 5: {g5['per_traj']}", flush=True)


@check(7, "the committed cells' clear multisets equal DESIGN_CLEAR_MULTISETS_4B")
def _c7(ctx):
    real = _load_real_tree(ctx)
    got = {}
    for c in real["cells4"]:
        got.setdefault(c["traj"], []).append(c["t_clear_index"])
    for traj, want in battery_4b.DESIGN_CLEAR_MULTISETS_4B.items():
        got_sorted = tuple(sorted(got.get(traj, [])))
        want_sorted = tuple(sorted(want))
        _eq(got_sorted, want_sorted, f"{traj} clear-index multiset")


@check(8, "power_4.json's multiples and realized alpha equal the design §2 literals")
def _c8(ctx):
    power4, _ = battery_4b.load_exp4_power_4b(battery_4.EXP4)
    multiples = power4.get("zero_excess_multiples")
    _eq([float(m) for m in multiples], [1.0, 1.5, 2.0, 3.0], "zero_excess_multiples")
    scatter = power4.get("zero_excess_scatter") or {}
    want = {"1.0": 0.019, "1.5": 0.144, "2.0": 0.246, "3.0": 0.264}
    for k, w in want.items():
        got = scatter.get(k)
        if got is None or abs(float(got) - w) > 1e-3:
            raise AssertionError(f"zero_excess_scatter[{k}] = {got!r}, design §2 literal {w}")


@check(9, "gate (2): eligibility re-derived")
def _c9(ctx):
    real = _load_real_tree(ctx)
    g2 = an4b.gate2_rederive_4b(real["root4"], real["elig4"])
    if not g2["pass"]:
        raise AssertionError(f"gate 2 disagrees: {g2['diffs'][:5]}")


@check(10, "the referent manifest's file count: live == N_FILES_4B == committed n_files")
def _c10(ctx):
    live = len(mkr4b.referent_files_4b())
    _eq(live, mkr4b.N_FILES_4B, "live referent_files_4b() count vs N_FILES_4B")
    committed = json.loads((EXP4B / "referents_4b.json").read_text())
    _eq(committed["n_files"], mkr4b.N_FILES_4B, "committed referents_4b.json n_files vs N_FILES_4B")


# Finding 5's free known-answer pin: the mean over the 26 committed
# cells of sensitivities["S5 <traj>"]["best_site"][rung]["phi"] --
# read straight off the committed `v4`, no placebo quantity, no new
# real-tree execution (v4/cells4 are already loaded by `_load_real_
# tree` for checks 4-6/9). Verified once against the real tree; a
# regression pin, not a retyped guess.
BEST_SITE_MEAN_PHI_PIN_4B = 0.578468800465005


@check(11, "S7(b)'s free known-answer pin: mean best-site phi over the 26 committed cells")
def _c11(ctx):
    real = _load_real_tree(ctx)
    bs = an4b.best_site_mean_phi_4b(real["v4"], real["cells4"])
    _eq(bs["n_cells"], len(real["cells4"]), "best-site phi coverage (every real cell has one)")
    if bs["T"] is None or abs(bs["T"] - BEST_SITE_MEAN_PHI_PIN_4B) > 1e-12:
        raise AssertionError(f"mean best-site phi {bs['T']!r} != pinned "
                             f"{BEST_SITE_MEAN_PHI_PIN_4B!r}")
    print(f"       S7(b) mean best-site phi = {bs['T']!r}", flush=True)


@check(12, "S7(a): clears-and-stays T re-derived == committed sensitivities.primary_clears_and_stays.T")
def _c12(ctx):
    real = _load_real_tree(ctx)
    cas_cells = an4b.clears_and_stays_cells_4b(real["series_by_traj"], real["rung_sets"],
                                               real["elig4"])
    committed = ((real["v4"].get("sensitivities") or {}).get("primary_clears_and_stays") or {})
    committed_T = committed.get("T")
    if not cas_cells:
        raise AssertionError("no clears-and-stays cells re-derived from the real tree")
    cas_T = an.primary_4(cas_cells, n_boot=an.N_BOOT_4, seed=0)["T"]
    _eq(cas_T, committed_T, "re-derived clears-and-stays T vs committed sensitivities."
                            "primary_clears_and_stays.T")
    print(f"       S7(a) clears-and-stays T = {cas_T!r}", flush=True)


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
