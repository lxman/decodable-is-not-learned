# experiments/exp4c/verify_referents_4c.py
"""The Exp 4c referent battery (Task 5 brief's 12 items; 2n's/exp4's
own `@check` shape): every referent re-asserted EXECUTABLE against the
committed trees — run at build, re-run cold at the freeze. Items 1-9
and 11 stop SHORT of any alignment statistic; item 10 is the ONE
statistic this battery computes, on KNOWN runs (Exp 4's own committed
tables — the discovery gate's known-answer reproduction, design
§3.7(1)); item 12 is a GATE on 4c's OWN sweep (SKIPs before it has
run). Committed bytes throughout: no model contact.

 1  frozen pins byte-identical (`battery_4c.check_frozen_4c`, which ALSO
    verifies `battery_4.FROZEN_SHA256_4` (57) + `EXP4_CLOSED_SHA256_4C`
    (8) + `EXP4B_CLOSED_SHA256_4C` (3) = 68 files even while 4c's own
    `FROZEN_SHA256_4C` stays empty; this item never SKIPs)
 2  the five upstream/sibling closed tags exist: `exp2h-closed`,
    `exp2l-closed`, `exp4-closed`, `exp4-reference-sealed`,
    `exp4b-closed`
 3  `referents_4c.json`: `make_referents_4c.check_referents_4c` at the
    pin returns zero failures
 4  the two manifests load at their pins with `GRID_4C` reproduced and
    each carrying its own step-0 entry (`battery_4c.manifests_4c`,
    which raises on any grid mismatch or a missing step-0 entry)
 5  the two rung sets reproduce `RUNG_SET_PIN_4C` AND their clear
    indices reproduce `CLEAR_INDEX_PIN_4C`
    (`battery_4c.check_rung_set_pins_4c`)
 6  every grid step's + every step-0's committed digest is readable,
    non-empty and 64 hex characters (22 + 16 + 2 = 40)
 7  `battery_4c.SITE_COUNT_PIN_4C` reproduces through `metric_4.
    sites_4` for every `n_hidden` `battery_4c.N_HIDDEN_PIN_4C` uses
 8  the five Exp 4 reference keys are complete (`battery_4.
    unit_complete_4`) and seal-bound (`exp4-reference-sealed` binds
    every one of `battery_4c.exp4_reference_paths_4c`)
 9  the referent manifest's file count: live `make_referents_4c.
    referent_files_4c()` == `N_FILES_4C` == the committed
    `referents_4c.json`'s own `n_files`
10  the discovery-set gate: `rank_4c.discovery_set_4c()` reproduces
    `rank_4c.DISCOVERY_PIN_4C` exactly (`rank_4c.
    check_discovery_pins_4c` returns zero failures) — the ONE
    statistic this battery computes, entirely on Exp 4's KNOWN,
    committed tables; prints U
11  `results/power_4c.json` reproduces byte for byte under
    `power_4c.compute` at its own recorded `n_sim`/`seed`, and its
    `cells_sha256` equals the LIVE `power_4c.structure_sha256_4c(
    power_4c.cell_structure_4c())`; prints the declaration
12  gate 0 (`analyze_4c.gate0_4c`) on the two new runs' own committed
    sweep trees, site 0 excluded, PASSES on both trajectories; SKIPs
    before 4c's own sweep has produced a step-0 AND an endpoint unit
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

EXP4C = Path(__file__).resolve().parent
EXPERIMENTS = EXP4C.parent
REPO = EXPERIMENTS.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp2g import predictor_2g as pr  # noqa: E402
from experiments.exp4 import battery_4  # noqa: E402
from experiments.exp4c import analyze_4c as an  # noqa: E402
from experiments.exp4c import battery_4c as bc  # noqa: E402
from experiments.exp4 import metric_4  # noqa: E402
from experiments.exp4c import make_referents_4c as mkr  # noqa: E402
from experiments.exp4c import power_4c as pw4c  # noqa: E402
from experiments.exp4c import rank_4c as rk  # noqa: E402

CHECKS = []


def check(n, name):
    def deco(fn_):
        CHECKS.append((n, name, fn_))
        return fn_
    return deco


def _eq(got, want, what):
    if got != want:
        raise AssertionError(f"{what}: got {got!r}, want {want!r}")


CLOSED_TAGS_4C = ("exp2h-closed", "exp2l-closed", "exp4-closed", "exp4-reference-sealed",
                  "exp4b-closed")


@check(1, "frozen pins byte-identical")
def _c1(ctx):
    bc.check_frozen_4c()
    if not bc.FROZEN_SHA256_4C:
        n = (len(battery_4.FROZEN_SHA256_4) + len(bc.EXP4_CLOSED_SHA256_4C)
            + len(bc.EXP4B_CLOSED_SHA256_4C))
        print(f"       FROZEN_SHA256_4C empty (covered by exp4/exp4b's own tables); "
             f"{n} pinned files verified", flush=True)


@check(2, "the five upstream/sibling closed tags exist")
def _c2(ctx):
    missing = [t for t in CLOSED_TAGS_4C if not pr.git_tag_exists(t)]
    if missing:
        raise AssertionError(f"missing tags: {missing}")


@check(3, "referents_4c.json at the pin, zero failures")
def _c3(ctx):
    if an.REFERENTS_4C_SHA256 is None:
        return "SKIP"
    bad = mkr.check_referents_4c(EXP4C / "referents_4c.json", sha_pin=an.REFERENTS_4C_SHA256)
    if bad:
        raise AssertionError(f"{len(bad)} referent failure(s): {bad[:5]}")


@check(4, "the two manifests load at their pins, GRID_4C + step-0 entries reproduced")
def _c4(ctx):
    m = bc.manifests_4c()
    _eq(set(m), set(bc.TRAJECTORIES_4C), "manifests_4c keys")
    ctx["manifests"] = m


@check(5, "the two rung sets reproduce RUNG_SET_PIN_4C and CLEAR_INDEX_PIN_4C")
def _c5(ctx):
    floors = bg.load_floors()
    from experiments.exp2d import battery_2d as bt
    battery = bt.load_battery()
    ctx["battery"] = battery
    rung_sets = {}
    for traj in bc.TRAJECTORIES_4C:
        outcome = bc.load_outcome_4c(traj, battery=battery)
        rs = bc.rung_sets_4c(outcome, floors)
        bad = bc.check_rung_set_pins_4c(traj, rs, outcome["steps"])
        if bad:
            raise AssertionError(f"{traj}: {bad}")
        rung_sets[traj] = rs
    ctx["rung_sets"] = rung_sets


@check(6, "every grid step's + step-0's committed digest is readable (22 + 16 + 2 = 40)")
def _c6(ctx):
    n = 0
    for traj in bc.TRAJECTORIES_4C:
        for step in (bc.INIT_STEP_4C,) + tuple(bc.GRID_4C[traj]):
            d = bc.committed_step_digest_4c(traj, step)
            if not d or len(d) != 64:
                raise AssertionError(f"{traj} step{step}: digest {d!r} is not 64 hex chars")
            int(d, 16)   # raises ValueError if not hex
            n += 1
    _eq(n, 40, "22 + 16 + 2 committed digests")


@check(7, "SITE_COUNT_PIN_4C reproduces through metric_4.sites_4")
def _c7(ctx):
    used = {bc.N_HIDDEN_PIN_4C[k] for k in bc.N_HIDDEN_PIN_4C}
    missing = used - set(bc.SITE_COUNT_PIN_4C)
    if missing:
        raise AssertionError(f"n_hidden values with no pinned site count: {missing}")
    for n_hidden, want in bc.SITE_COUNT_PIN_4C.items():
        got = len(metric_4.sites_4(n_hidden))
        if got != want:
            raise AssertionError(f"sites_4({n_hidden}) = {got} != pinned {want}")


@check(8, "the five Exp 4 reference keys are complete and seal-bound")
def _c8(ctx):
    keys = tuple(sorted({r for refs in bc.REFS_FOR_4C.values() for r in refs})) + \
        ("ladder_pythia_6.9b",)
    _eq(len(keys), 5, "reference key count")
    incomplete = [k for k in keys if not battery_4.unit_complete_4(battery_4.EXP4, k)]
    if incomplete:
        raise AssertionError(f"incomplete reference units: {incomplete}")
    from experiments.exp2i import analyze_2i as an2i
    seal = an2i.require_seal_2i(battery_4.REFERENCE_SEAL_TAG_4, bc.exp4_reference_paths_4c(
        battery_4.EXP4), tag_exists=pr.git_tag_exists, blobs_bound=None, repo_root=REPO)
    if seal.get("failures"):
        raise AssertionError(f"reference seal: {seal['failures']}")


@check(9, "the referent manifest's file count: live == N_FILES_4C == committed n_files")
def _c9(ctx):
    live = len(mkr.referent_files_4c())
    _eq(live, mkr.N_FILES_4C, "live referent_files_4c() count vs N_FILES_4C")
    committed = json.loads((EXP4C / "referents_4c.json").read_text())
    _eq(committed["n_files"], mkr.N_FILES_4C, "committed referents_4c.json n_files vs N_FILES_4C")


@check(10, "the discovery-set gate reproduces DISCOVERY_PIN_4C exactly (KNOWN runs)")
def _c10(ctx):
    rec = rk.discovery_set_4c(battery_4.EXP4)
    bad = rk.check_discovery_pins_4c(rec)
    if bad:
        raise AssertionError(f"{len(bad)} discovery pin failure(s): {bad}")
    print(f"       discovery U={rec['U']:.4f} over {rec['n_cells']} cells, "
         f"family p={rec['p_family']:.4g}", flush=True)


@check(11, "power_4c.json reproduces byte for byte; declaration printed")
def _c11(ctx):
    p = EXP4C / "results" / "power_4c.json"
    if not p.is_file():
        return "SKIP"
    power = json.loads(p.read_text())
    rec2 = pw4c.compute(pw4c.cell_structure_4c(), n_sim=int(power["n_sim"]),
                        seed=int(power["seed"]))
    rec2["prereg_tag"] = power.get("prereg_tag")
    extra = sorted(set(power) - set(rec2))
    missing = sorted(set(rec2) - set(power))
    if extra or missing:
        raise AssertionError(f"power_4c.json key set mismatch: extra {extra}, missing {missing}")
    a_s = json.dumps(rec2, sort_keys=True)
    b_s = json.dumps(power, sort_keys=True)
    if a_s != b_s:
        raise AssertionError("power_4c.json did not reproduce byte for byte")
    live_sha = pw4c.structure_sha256_4c(pw4c.cell_structure_4c())
    if power.get("cells_sha256") != live_sha:
        raise AssertionError(f"power_4c.json cells_sha256 {power.get('cells_sha256')} != live "
                             f"{live_sha}")
    print(f"       power declaration: {power['declaration']}", flush=True)


@check(12, "gate 0 on the two new runs' own sweep trees: PASS with site 0 excluded")
def _c12(ctx):
    traj0 = bc.TRAJECTORIES_4C[0]
    d0 = battery_4.unit_dir(bc.EXP4C, traj0, bc.INIT_STEP_4C)
    dend = battery_4.unit_dir(bc.EXP4C, traj0, bc.ENDPOINT_STEP_4C[traj0])
    if not d0.is_dir() or not dend.is_dir():
        return "SKIP"
    from experiments.exp4c import analyze_4c as an4c
    from experiments.exp4 import collect_4
    _eq(list(rk.EXCLUDED_SITES_4C), [0], "EXCLUDED_SITES_4C")
    out = []
    for traj in bc.TRAJECTORIES_4C:
        refs = bc.REFS_FOR_4C[traj]
        ref_raw = collect_4.load_ref_tables_4(battery_4.EXP4, refs)
        ref_tables = {r: t["sets"] for r, t in ref_raw.items()}
        init_unit = an4c._load_one_unit_4c(bc.EXP4C, (traj, bc.INIT_STEP_4C))
        endpoint_unit = an4c._load_one_unit_4c(bc.EXP4C, (traj, bc.ENDPOINT_STEP_4C[traj]))
        g0 = an4c.gate0_4c(bc.EXP4C, traj, ref_tables, init_unit, endpoint_unit)
        if not g0["pass"]:
            raise AssertionError(f"{traj}: gate 0 {g0['fraction_below']:.4f} < the .90 bar over "
                                 f"{g0['n_cells']} cells ({g0['n_cells_excluded']} excluded)")
        out.append(f"{traj} {g0['fraction_below']:.4f} ({g0['n_cells']} cells, "
                   f"{g0['n_cells_excluded']} excluded)")
    print("       gate 0 (site 0 excluded): " + "; ".join(out), flush=True)


@check(13, "gate 1's comparator matches the sweep endpoint's pins, cold (FREEZE F-3)")
def _c13(ctx):
    """FREEZE F-3: everything that decides whether gate 1's BYTE
    comparison can succeed is readable without loading a model. For
    `pythia_6.9b` the comparator is Exp 4's committed, seal-bound
    `ladder_pythia_6.9b` table — checkpoint identity, render, batch
    composition, site family, reference set, depth pairing and 34-rung
    coverage, all answerable today, before 15 h of shard streaming. For
    `olmo2_13b` the comparator is 4c's own thin endpoint, which the
    campaign writes; `available` is False until it exists."""
    lines = []
    for traj in bc.TRAJECTORIES_4C:
        c = bc.gate1_comparator_failures_4c(bc.EXP4C, battery_4.EXP4, traj)
        if not c["available"]:
            lines.append(f"{traj}: {c['root']}/{c['key']} not written yet (this run's own)")
            continue
        if c["failures"]:
            raise AssertionError(f"{traj}: {c['failures']}")
        if not c["digest_equal"]:
            raise AssertionError(f"{traj}: comparator {c['root']}/{c['key']} was collected on "
                                 f"{c['digest']!r}, the committed endpoint is "
                                 f"{c['committed_digest']!r}")
        lines.append(f"{traj}: {c['root']}/{c['key']} digest_equal, pins equal")
    print("       " + "; ".join(lines), flush=True)


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
            print(f"  [{n:2d}] skip  {name} (not yet applicable)", flush=True)
        else:
            print(f"  [{n:2d}] ok    {name}", flush=True)
            n_ok += 1
    print(f"referent battery: {n_ok}/{len(CHECKS)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
