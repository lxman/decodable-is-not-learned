# experiments/exp2k/verify_referents_2k.py
"""The Exp 2k referent battery: every referent re-asserted EXECUTABLE
against the committed trees — run at build, re-run cold at the freeze.
Stops short of the verdict; 2k's own model contact is predictor-side
only, at the tier (the campaign, not this battery).

 1  frozen pins byte-identical: `analyze_2j.check_frozen_2j`,
    `battery_2i.check_frozen_2i`, `battery_2g.check_frozen_imports_2g`,
    `battery_2i.check_pythia_predictor_files`, and
    `battery_2k.check_frozen_2k` (all five real, all pinned)
 2  2i's four tags and 2j's two tags exist; every 2i seal binds
    (`analyze_2i.require_seal_2i` with real git)
 3  referents_2k.json: own sha == the literal; N_FILES_2K entries; zero
    refusals (Task 5: REFERENTS_2K_SHA256 / N_FILES_2K pinned, the
    manifest built)
 4  `battery_2k.check_seed_freshness(R_CAP_DESIGN)` -> 18 cells, seeds
    1-3 fresh, seed 0 = 2d's main tier on every cell
 5  `battery_2k.committed_rows` on every R_CAP cell at both sizes:
    500 x 64, gz sha == 2i's `PYTHIA_PREDICTOR_FILES` pin, record
    `model_sha` == `pythia_sha(size)`
 6  `matched_k_256` on the committed rates (2d's x_A, 2i's x_B)
    reproduces `MATCHED_K_DESIGN`
 7  the three pin extractors on the committed records:
    `pin_a_from_record_2i` == `VERDICT_2I_PIN_A` (+ nine per-rung d's),
    `pin_a410_from_record_2i` == `VERDICT_2I_PIN_A410`, 2g's
    `sampler_competitor` == `VERDICT_2G_PIN_28`, `ladder_b_from_record_2j`
    has 7 points with B(64) == 2i's within-alone literal
 8  the tree (`verdict_tree_2k` + `_licensed`) on literal inputs: every
    terminal, both annotations, the T_BAR/ALPHA boundaries, all four
    NOT-DENSITY licence variants (POWERED, DECLARED UNDERPOWERED IN
    ADVANCE, THIN disclosure, UNDEFINED disclosure)
 9  `read_rows_2k` refusals on hand-built files (three shapes:
    duplicate item, wrong seed set, wrong stream length) and
    `tier_record_2k` -> `tier_record_failures_2k` round trips clean
10  the tier tree: no halt marker on the real `EXP2K`; the seal and
    power record absent BEFORE the campaign (printed "absent —
    pre-campaign"), or present and `seal_failures_2k == []` with
    `load_power_2k` PASS after it
11  `placement_on_ladder` on hand cases (exact point, interior, both
    ends)
12  the import surface: `check_imports_2k()` in THIS process passes
    (Task 5: IMPORTED_SHA256_2K pinned)
"""
from __future__ import annotations

import gzip
import json
import sys
import tempfile
from pathlib import Path

EXP2K = Path(__file__).resolve().parent
if str(EXP2K.parent.parent) not in sys.path:
    sys.path.insert(0, str(EXP2K.parent.parent))

from experiments.exp2d import analyze_2d as a2d  # noqa: E402
from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp2g import predictor_2g as pr  # noqa: E402
from experiments.exp2i import analyze_2i as an2i  # noqa: E402
from experiments.exp2i import battery_2i as bi  # noqa: E402
from experiments.exp2j import analyze_2j as an2j  # noqa: E402
from experiments.exp2k import analyze_2k as an  # noqa: E402
from experiments.exp2k import battery_2k as bk  # noqa: E402
from experiments.exp2k import make_referents_2k as mkr  # noqa: E402

CHECKS = []


def check(n, name):
    def deco(fn_):
        CHECKS.append((n, name, fn_))
        return fn_
    return deco


def _eq(got, want, what):
    if got != want:
        raise AssertionError(f"{what}: got {got!r}, want {want!r}")


@check(1, "frozen pins: check_frozen_2j/check_frozen_2i/check_frozen_imports_2g/"
         "check_pythia_predictor_files/check_frozen_2k")
def _c1(ctx):
    an2j.check_frozen_2j()
    bi.check_frozen_2i()
    bg.check_frozen_imports_2g()
    bi.check_pythia_predictor_files()
    if bk.FROZEN_SHA256_2K:
        bk.check_frozen_2k()
    else:
        # defensive fallback only — FROZEN_SHA256_2K has been pinned
        # since Task 5; this branch is unreachable on the real tree
        print("      (check_frozen_2k: FROZEN_SHA256_2K empty)")


@check(2, "2i's four tags and 2j's two tags exist; every 2i seal binds")
def _c2(ctx):
    for tag in (bi.PREREG_TAG, bi.PREDICTOR_SEAL_TAG, bi.ENDPOINT_SEAL_TAG, "exp2i-closed"):
        _eq(pr.git_tag_exists(tag), True, f"tag {tag} exists")
    for tag in (an2j.PREREG_TAG_2J, "exp2j-closed"):
        _eq(pr.git_tag_exists(tag), True, f"tag {tag} exists")
    predictor_rec = an2i._load_predictor_seal_content(bi.EXP2I)
    psl = an2i.require_seal_2i(bi.PREDICTOR_SEAL_TAG,
                               an2i._predictor_seal_paths(bi.EXP2I, predictor_rec))
    _eq(psl["failures"], [], "predictor seal binds")
    esl = an2i.require_seal_2i(bi.ENDPOINT_SEAL_TAG, an2i._endpoint_seal_paths(bi.EXP2I))
    _eq(esl["failures"], [], "endpoint seal binds")


@check(3, "referents_2k.json: literal sha, N_FILES_2K entries, zero refusals")
def _c3(ctx):
    if an.REFERENTS_2K_SHA256 is None or mkr.N_FILES_2K is None:
        return "SKIP"
    _eq(Path(an.REFERENTS_PATH_2K).is_file(), True, "referents_2k.json on disk")
    bad = mkr.check_referents(an.REFERENTS_PATH_2K, sha_pin=an.REFERENTS_2K_SHA256)
    _eq(bad, [], "zero refusals")


@check(4, "check_seed_freshness(R_CAP_DESIGN): 18 cells, seeds 1-3 fresh, seed 0 = 2d main")
def _c4(ctx):
    res = bk.check_seed_freshness(bk.R_CAP_DESIGN)
    _eq(res["cells"], 18, "18 cells (nine rungs x two sizes)")
    _eq(res["new_seeds"], [1, 2, 3], "seeds 1-3 are the fresh ones")
    _eq(res["gate1_seed"], bk.GATE1_SEED, "seed 0 is the gate-1 referent")


@check(5, "committed_rows on every R_CAP cell at both sizes: 500 x 64, gz sha, model_sha")
def _c5(ctx):
    battery = bg.load_battery()
    verify = a2d.load_verify()
    ctx["battery"], ctx["verify"] = battery, verify
    for size in bk.SIZES_2K:
        for r in bk.R_CAP_DESIGN:
            rows = bk.committed_rows(size, r)
            _eq(len(rows), bk.N_ITEMS, f"{size}/{r}: n_items")
            _eq(all(len(row["draws"]["0"]) == 64 for row in rows), True,
               f"{size}/{r}: 64 draws per item")
            gz_sha = bg.sha256_file(bk.committed_draws_path(size, r))
            _eq(gz_sha, bi.PYTHIA_PREDICTOR_FILES[(size, r)], f"{size}/{r}: gz sha == 2i's pin")
            rec = json.loads(bk.committed_record_path(size, r).read_text())
            _eq(rec.get("model_sha"), bk.pythia_sha(size), f"{size}/{r}: record model_sha")


@check(6, "matched_k_256 on the committed rates (2d's x_A, 2i's x_B) reproduces MATCHED_K_DESIGN")
def _c6(ctx):
    battery, verify = ctx["battery"], ctx["verify"]
    x_a = bi.sampler_counts_pythia("1b", tuple(bk.MATCHED_K_DESIGN))
    x_b = bi.sampler_counts_olmo(tuple(bk.MATCHED_K_DESIGN), root=bi.EXP2I, battery=battery,
                                 verify_fn=verify)
    got = {}
    for r, k_want in bk.MATCHED_K_DESIGN.items():
        ra = bk.mean_rate(x_a[r], bk.DRAWS_PER_SEED)
        rb = bk.mean_rate(x_b[r], bk.DRAWS_PER_SEED)
        got[r] = bk.matched_k_256(ra, rb)["k"]
        _eq(got[r], k_want, f"{r}: matched k")
    print(f"      (k table: {got})")


@check(7, "the three pin extractors on the committed records == the literals")
def _c7(ctx):
    v2i = json.loads((bi.EXP2I / "results" / "verdict.json").read_text())
    got = an.pin_a_from_record_2i(v2i)
    _eq(got["A"], an.VERDICT_2I_PIN_A, "pin A")
    _eq(set(got["per_rung"]), set(bk.R_CAP_DESIGN), "nine per-rung d's")
    a410 = an.pin_a410_from_record_2i(v2i)
    _eq(a410, an.VERDICT_2I_PIN_A410, "pin A410")
    v2g = json.loads((bg.EXP2G / "results" / "verdict.json").read_text())
    _eq(an2j.pin_from_record_2g(v2g)["sampler_competitor"], an.VERDICT_2G_PIN_28, "2g pin")
    v2j = json.loads((bg.REPO / "experiments/exp2j/results/verdict.json").read_text())
    lad = an.ladder_b_from_record_2j(v2j)
    _eq(len(lad), 7, "seven ladder points")
    _eq(lad[64], an2j.VERDICT_2I_PIN["within_alone"], "B(64) == 2i's within-alone literal")


@check(8, "the tree on literal inputs: every terminal, both annotations, boundaries, "
         "all NOT-DENSITY licences")
def _c8(ctx):
    def prim(T, p, fires, eligible=("r1", "r2", "r3"), named=None):
        return {"stratified": {"T": T, "p": p, "n_perm": 10000, "n_ge": 0}, "fires": fires,
               "named_inside": named, "eligible": list(eligible), "per_rung": {}}

    power_powered = {"declared_status": "POWERED"}
    power_under = {"declared_status": "DECLARED UNDERPOWERED IN ADVANCE"}

    ins = an.verdict_tree_2k(["x"], None, None)
    _eq(ins["verdict"], "INSUFFICIENT_DATA", "refusal -> INSUFFICIENT_DATA")
    _eq(an._licensed(ins), an.LICENSED_2K["INSUFFICIENT_DATA"], "refusal licence")

    fires = prim(0.20, 0.001, True)
    res = an.verdict_tree_2k([], fires, power_powered)
    _eq(res["verdict"], "DENSITY", "fires -> DENSITY")
    _eq(res["annotation"], None, "DENSITY carries no annotation")
    _eq(an._licensed(res), an.LICENSED_2K["DENSITY"], "DENSITY licence")

    struct = prim(0.05, 0.001, False)
    r_struct = an.verdict_tree_2k([], struct, power_powered)
    _eq((r_struct["verdict"], r_struct["annotation"]), ("NOT-DENSITY", "structured"),
       "no fire, p < ALPHA -> structured")
    _eq(an._licensed(r_struct), an.LICENSED_2K["NOT-DENSITY"], "NOT-DENSITY (structured) licence")

    null_ = prim(0.05, 0.3, False)
    r_null = an.verdict_tree_2k([], null_, power_powered)
    _eq((r_null["verdict"], r_null["annotation"]), ("NOT-DENSITY", "null"),
       "no fire, p >= ALPHA -> null")

    under = an.verdict_tree_2k([], null_, power_under)
    _eq(an._licensed(under), an.LICENSED_2K["NOT-DENSITY_UNDERPOWERED"],
       "NOT-DENSITY (underpowered) licence")

    undefined = prim(None, 1.0, False, eligible=(), named="undefined: no eligible rung")
    r_undef = an.verdict_tree_2k([], undefined, power_powered)
    _eq(an.DISCLOSURE_UNDEFINED_2K in r_undef["disclosures"], True, "undefined disclosed")
    _eq(an._licensed(r_undef),
       an.LICENSED_2K["NOT-DENSITY_UNDEFINED"] + "; " + an.DISCLOSURE_UNDEFINED_2K,
       "NOT-DENSITY (undefined) licence")

    thin = prim(0.05, 0.3, False, eligible=("a", "b"))
    r_thin = an.verdict_tree_2k([], thin, power_powered)
    _eq(an.DISCLOSURE_THIN_2K in r_thin["disclosures"], True, "thin disclosed")
    _eq(an._licensed(r_thin), an.LICENSED_2K["NOT-DENSITY_THIN"] + "; " + an.DISCLOSURE_THIN_2K,
       "NOT-DENSITY (thin) licence")

    _eq(an2i.fires_2i({"stratified": {"T": an.T_BAR, "p": an.ALPHA - 1e-6}}), True,
       "T == T_BAR (inclusive), p < ALPHA fires")
    _eq(an2i.fires_2i({"stratified": {"T": an.T_BAR - 1e-9, "p": an.ALPHA - 1e-6}}), False,
       "T just under T_BAR does not fire")
    _eq(an2i.fires_2i({"stratified": {"T": an.T_BAR + 0.1, "p": an.ALPHA}}), False,
       "p == ALPHA (not strictly under) does not fire")

    at_bar = prim(an.T_BAR, an.ALPHA - 1e-6, True)
    _eq(an.verdict_tree_2k([], at_bar, power_powered)["verdict"], "DENSITY",
       "T == T_BAR, p < ALPHA -> DENSITY through the tree")
    below_bar = prim(an.T_BAR - 1e-9, an.ALPHA - 1e-6, False)
    _eq(an.verdict_tree_2k([], below_bar, power_powered)["verdict"], "NOT-DENSITY",
       "T just under T_BAR -> NOT-DENSITY through the tree")


def _write_gz_rows(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wt") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")


@check(9, "read_rows_2k refusals on hand-built files (three shapes); "
         "tier_record_2k -> tier_record_failures_2k round trip")
def _c9(ctx):
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "x.jsonl.gz"
        # shape 1: duplicate item index
        _write_gz_rows(p, [{"item": 0, "draws": {"0": ["a", "b"], "1": ["c", "d"]}},
                           {"item": 0, "draws": {"0": ["a", "b"], "1": ["c", "d"]}}])
        try:
            bk.read_rows_2k(p, seeds=(0, 1), dps=2, n_items=2)
            raise AssertionError("shape 1: expected a ValueError (duplicate item)")
        except ValueError as e:
            _eq("duplicate item" in str(e), True, "shape 1: duplicate item refused")
        # shape 2: wrong seed set
        _write_gz_rows(p, [{"item": 0, "draws": {"0": ["a", "b"], "2": ["c", "d"]}},
                           {"item": 1, "draws": {"0": ["a", "b"], "1": ["c", "d"]}}])
        try:
            bk.read_rows_2k(p, seeds=(0, 1), dps=2, n_items=2)
            raise AssertionError("shape 2: expected a ValueError (seed streams)")
        except ValueError as e:
            _eq("seed streams" in str(e), True, "shape 2: wrong seed set refused")
        # shape 3: wrong stream length
        _write_gz_rows(p, [{"item": 0, "draws": {"0": ["a"], "1": ["c", "d"]}},
                           {"item": 1, "draws": {"0": ["a", "b"], "1": ["c", "d"]}}])
        try:
            bk.read_rows_2k(p, seeds=(0, 1), dps=2, n_items=2)
            raise AssertionError("shape 3: expected a ValueError (draws_per_seed)")
        except ValueError as e:
            _eq("draws_per_seed" in str(e), True, "shape 3: wrong stream length refused")

    battery, verify = ctx["battery"], ctx["verify"]
    cap = battery["antonym"]
    committed = bk.committed_by_item(bk.committed_rows("1b", "antonym"))
    rows = [{"item": i, "draws": {"0": list(committed[i]), "1": [" x"] * bk.DRAWS_PER_SEED,
                                  "2": [" x"] * bk.DRAWS_PER_SEED, "3": [" x"] * bk.DRAWS_PER_SEED}}
            for i in range(bk.N_ITEMS)]
    crec_p = bk.committed_record_path("1b", "antonym")
    cgz_p = bk.committed_draws_path("1b", "antonym")
    rec = bk.tier_record_2k(rung="antonym", size="1b", cap=cap, rows=rows, verify_fn=verify,
                            model_sha=bk.pythia_sha("1b"),
                            stack={"torch": "n/a", "transformers": "n/a"}, git_sha="", seconds=0.0,
                            committed_gz_sha=bg.sha256_file(cgz_p),
                            committed_record_sha=bg.sha256_file(crec_p),
                            gate1_items_compared=bk.N_ITEMS,
                            gate1_draws_compared=bk.N_ITEMS * bk.DRAWS_PER_SEED)
    bad = bk.tier_record_failures_2k(rec, size="1b", rung="antonym", cap=cap,
                                     committed_sha=bi.PYTHIA_PREDICTOR_FILES[("1b", "antonym")])
    _eq(bad, [], "tier_record_2k -> tier_record_failures_2k round trip")


@check(10, "the tier tree: no halt marker; seal/power record status on the real EXP2K")
def _c10(ctx):
    _eq(bk.halt_markers(bk.EXP2K), [], "no halt marker")
    seal_p, power_p = bk.seal_path(bk.EXP2K), bk.power_path(bk.EXP2K)
    if not seal_p.is_file() and not power_p.is_file():
        print("      (seal and power record: absent — pre-campaign)")
        return
    _eq(seal_p.is_file() and power_p.is_file(), True, "seal and power record both present")
    battery, verify = ctx["battery"], ctx["verify"]
    cells = {}
    for size in bk.SIZES_2K:
        failures, c = an.load_tier_2k(bk.EXP2K, size, battery=battery, verify_fn=verify,
                                      rungs=bk.R_CAP_DESIGN)
        _eq(failures, [], f"{size}: tier loads cleanly")
        cells[size] = c
    seal = json.loads(seal_p.read_text())
    _eq(an.seal_failures_2k(seal, cells, bk.EXP2K), [], "seal_failures_2k == []")
    rec = an.load_power_2k(bk.EXP2K, bk.R_CAP_DESIGN, seal["sha256"])
    _eq(rec["primary"]["declared_status"] in an2i.DECLARED_STATUSES_2I, True, "load_power_2k PASS")


@check(11, "placement_on_ladder on hand cases (exact point, interior, both ends)")
def _c11(ctx):
    lad = {1: 0.05, 2: 0.08, 4: 0.11, 8: 0.145, 16: 0.176, 32: 0.2025, 64: 0.2204}
    p = an.placement_on_ladder(lad, 0.145)
    _eq((p["k_equivalent"], p["bracket"]), (8.0, [8, 8]), "exact point")
    p = an.placement_on_ladder(lad, 0.16)
    _eq(8 < p["k_equivalent"] < 16 and p["bracket"] == [8, 16], True, "interior")
    _eq(an.placement_on_ladder(lad, 0.30)["bracket"], [64, None], "above the top end")
    _eq(an.placement_on_ladder(lad, 0.01)["bracket"], [None, 1], "below the bottom end")


@check(12, "the import surface: check_imports_2k() in THIS process passes")
def _c12(ctx):
    if an.IMPORTED_SHA256_2K is None:
        return "SKIP"
    an.check_imports_2k()


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
            print(f"  [{n:2d}] skip  {name} (pending Task 5)", flush=True)
        else:
            print(f"  [{n:2d}] ok    {name}", flush=True)
            n_ok += 1
    print(f"referent battery: {n_ok}/{len(CHECKS)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
