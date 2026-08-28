# experiments/exp2j/verify_referents_2j.py
"""The Exp 2j referent battery: every referent re-asserted EXECUTABLE
against the committed trees — run at build, re-run cold at the freeze.
It stops short of the verdict and of any model contact (2j is
analysis-only, so there never is one) and deliberately short of any
predictor-vs-outcome statistic.

 1  frozen pins byte-identical: `analyze_2j.check_frozen_2j`,
    `battery_2i.check_frozen_2i`, `battery_2g.check_frozen_imports_2g`,
    `battery_2i.check_pythia_predictor_files`
 2  2i's four tags exist and both 2i seals bind
    (`analyze_2i.require_seal_2i` with real git)
 3  referents_2j.json: own sha == the literal; N_FILES_2J entries; zero
    refusals — SKIPPED (printed "pending Task 4") until Task 4 pins
    REFERENTS_2J_SHA256/N_FILES_2J and builds the manifest
 4  the design §2 item-file table (Task 1's `REAL` dict,
    `test_functionals_2j.py`) reproduces on all nine rungs
 5  `verified_bits` == `battery_2i.sampler_counts_olmo` (x_B) and ==
    `battery_2i.sampler_counts_pythia("1b")` (x_A) on every R_CAP rung
 6  the bucket rule's three branches on hand cases, plus the rule
    report on the real committed tables (O dropped on antonym/
    antonym6/odd6, printed)
 7  `matched_k` on the committed mean rates reproduces design §5.4's k
    table (x_B: add3_mid 7, add_base8 7, arith_next 9, sub_base8 11,
    antonym 22, antonym6 23, sub3_mid 40, odd6 57; x_A: sub4_mid ~26)
 8  the three pin extractors (`pin_from_record_2i`/`_2g`/`_2h`) on the
    committed verdict files equal `VERDICT_2I_PIN`/`_2G_PIN`/`_2H_PIN`
 9  the tree (`verdict_tree_2j` + `_licensed`) on literal inputs: every
    terminal, the T_BAR/ALPHA boundaries, all four ABSORBED licence
    variants (POWERED, DECLARED UNDERPOWERED IN ADVANCE, THIN
    disclosure, UNDEFINED disclosure)
10  `t_only`'s T == `_run_test`'s stratified T on a toy, bit-for-bit
11  2i's committed `power_2i.json` B null SD / min-detectable T equal
    the literals `power_2j.py`'s own source carries
12  `power_2j.json` exists, `declared_status` valid, rungs == R_CAP,
    `n_trained_steps` == the grid, and (freeze F-2) the composite
    partition the record was simulated over == the one the analyzer
    builds today — SKIPPED (printed "pending Task 4") until the power
    record is run
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import numpy as np

EXP2J = Path(__file__).resolve().parent
if str(EXP2J.parent.parent) not in sys.path:
    sys.path.insert(0, str(EXP2J.parent.parent))

from experiments.exp2d import analyze_2d as a2d  # noqa: E402
from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp2g import predictor_2g as pr  # noqa: E402
from experiments.exp2g import strata_2g as sg  # noqa: E402
from experiments.exp2h import battery_2h as bh  # noqa: E402
from experiments.exp2i import analyze_2i as an2i  # noqa: E402
from experiments.exp2i import battery_2i as bi  # noqa: E402
from experiments.exp2j import analyze_2j as an  # noqa: E402
from experiments.exp2j import functionals_2j as fn  # noqa: E402
from experiments.exp2j import make_referents_2j as mkr  # noqa: E402

CHECKS = []


def check(n, name):
    def deco(fn_):
        CHECKS.append((n, name, fn_))
        return fn_
    return deco


def _eq(got, want, what):
    if got != want:
        raise AssertionError(f"{what}: got {got!r}, want {want!r}")


@check(1, "frozen pins: analyze_2j/battery_2i/battery_2g/x_A predictor files")
def _c1(ctx):
    an.check_frozen_2j()
    bi.check_frozen_2i()
    bg.check_frozen_imports_2g()
    bi.check_pythia_predictor_files()


@check(2, "2i's four tags exist; both 2i seals bind")
def _c2(ctx):
    for tag in (bi.PREREG_TAG, bi.PREDICTOR_SEAL_TAG, bi.ENDPOINT_SEAL_TAG):
        _eq(pr.git_tag_exists(tag), True, f"tag {tag} exists")
    # exp2i-closed is the fourth tag the design's own inventory names
    # (not one of battery_2i's three constants — asserted by literal).
    _eq(pr.git_tag_exists("exp2i-closed"), True, "tag exp2i-closed exists")
    predictor_rec = an2i._load_predictor_seal_content(bi.EXP2I)
    psl = an2i.require_seal_2i(bi.PREDICTOR_SEAL_TAG,
                               an2i._predictor_seal_paths(bi.EXP2I, predictor_rec))
    _eq(psl["failures"], [], "predictor seal binds")
    esl = an2i.require_seal_2i(bi.ENDPOINT_SEAL_TAG, an2i._endpoint_seal_paths(bi.EXP2I))
    _eq(esl["failures"], [], "endpoint seal binds")


@check(3, "referents_2j.json: literal sha, N_FILES_2J entries, zero refusals")
def _c3(ctx):
    if an.REFERENTS_2J_SHA256 is None or mkr.N_FILES_2J is None:
        return "SKIP"
    _eq(Path(an.REFERENTS_PATH_2J).is_file(), True, "referents_2j.json on disk")
    bad = mkr.check_referents(an.REFERENTS_PATH_2J, sha_pin=an.REFERENTS_2J_SHA256)
    _eq(bad, [], "zero refusals")


@check(4, "design §2 item-file table (the REAL dict) reproduces on all nine rungs")
def _c4(ctx):
    from experiments.exp2j.tests.test_functionals_2j import REAL
    for rung, (distinct, rep, verb) in REAL.items():
        cap = bg.load_battery((rung,))[rung]
        ans = [str(it["answer"]) for it in cap["eval_items"]]
        _eq(len(set(ans)), distinct, f"{rung}: distinct answers")
        _eq(sum(fn.repeated_char(cap)), rep, f"{rung}: repeated-char answers")
        _eq(sum(1 for it in cap["eval_items"] if str(it["answer"]) in it["question"]),
           verb, f"{rung}: answer verbatim in question")
        if rung in ("antonym", "antonym6", "odd6"):
            _eq(fn.bucket(fn.input_overlap(cap))[1], "dropped_constant",
               f"{rung}: O dropped_constant")
    _eq(len(REAL), 9, "nine rungs")


@check(5, "verified_bits == sampler_counts_olmo (x_B) / sampler_counts_pythia (x_A) on R_CAP")
def _c5(ctx):
    bat = bg.load_battery()
    verify = a2d.load_verify()
    r_cap = tuple(bi.STRATA_RUNGS)
    prod_b = bi.sampler_counts_olmo(r_cap, root=bi.EXP2I, battery=bat, verify_fn=verify)
    prod_a = bi.sampler_counts_pythia("1b", r_cap)
    for r in r_cap:
        bits_b = fn.verified_bits(fn.draw_rows_2i(bi.EXP2I, r), bat[r], verify)
        _eq(fn.counts_from_bits(bits_b), prod_b[r], f"x_B counts {r}")
        bits_a = fn.verified_bits(fn.draw_rows_2d("1b", r), bat[r], verify)
        _eq(fn.counts_from_bits(bits_a), prod_a[r], f"x_A counts {r}")
    ctx["battery"] = bat
    ctx["verify"] = verify
    ctx["r_cap"] = r_cap


@check(6, "bucket rule's three branches (hand cases); real-table drop report")
def _c6(ctx):
    b, rule = fn.bucket([2] * 196 + [3] * 304)
    _eq((rule, sum(b)), ("tie_fallback", 304), "branch: tie_fallback")
    b, rule = fn.bucket([0] * 400 + [1] * 100)
    _eq((rule, sum(b)), ("median", 100), "branch: median")
    b, rule = fn.bucket([1] * 274 + [0] * 226)
    _eq((rule, sum(b)), ("tie_fallback", 274), "branch: tie_fallback (antonym's own R shape)")
    b, rule = fn.bucket([7] * 500)
    _eq((b, rule), (None, "dropped_constant"), "branch: dropped_constant")

    bat, verify, r_cap = ctx["battery"], ctx["verify"], ctx["r_cap"]
    pred2g = pr.load_predictor(bg.predictor_path(bg.EXP2G), sha_pin=bh.PREDICTOR_2G_SHA)
    strata = sg.from_json(pred2g["strata"])
    tables = {r: fn.functional_table(bat[r], fn.draw_rows_2i(bi.EXP2I, r)) for r in r_cap}
    comp, report = fn.composite_strata(strata, tables, r_cap)
    dropped_o = sorted(r for r in r_cap
                       if report[r]["O"] in ("dropped_constant", "dropped_after_fallback"))
    print(f"      (O dropped on {dropped_o})")
    # design §2's own worked example names three (antonym/antonym6/odd6,
    # the rungs `test_functionals_2j.REAL` covers); the real R_CAP set
    # adds a fourth found here — median5's answer is always one of the
    # listed option numbers, verbatim in its question on all 500 items
    # (overlap == 1.0 everywhere), so O is dropped_constant there too.
    _eq(set(dropped_o), {"antonym", "antonym6", "odd6", "median5"},
       "O dropped on the three design §2 names it, plus median5 (found here)")
    ctx["strata"] = strata
    ctx["tables"] = tables


K_TABLE_2J = {"add3_mid": ("B", 7), "add_base8": ("B", 7), "arith_next": ("B", 9),
             "sub_base8": ("B", 11), "antonym": ("B", 22), "antonym6": ("B", 23),
             "sub3_mid": ("B", 40), "odd6": ("B", 57), "sub4_mid": ("A", 26)}


@check(7, "matched_k on the committed mean rates reproduces design §5.4's k table")
def _c7(ctx):
    bat, verify = ctx["battery"], ctx["verify"]
    x_a = bi.sampler_counts_pythia("1b", tuple(K_TABLE_2J))
    x_b = bi.sampler_counts_olmo(tuple(K_TABLE_2J), root=bi.EXP2I, battery=bat, verify_fn=verify)
    got = {}
    for r, (denser, k_want) in K_TABLE_2J.items():
        m = fn.matched_k(fn.mean_rate(x_a[r]), fn.mean_rate(x_b[r]))
        got[r] = (m["denser"], m["k"])
        if r != "sub4_mid":     # sub4_mid is "≈26" by design (near-zero rates both sides)
            _eq(m["denser"], denser, f"{r}: denser side")
            _eq(m["k"], k_want, f"{r}: k")
    print(f"      (k table: {got})")
    _eq(abs(got["sub4_mid"][1] - 26) <= 3, True, "sub4_mid: k ~= 26")


@check(8, "the three pin extractors on the committed verdict files == the literals")
def _c8(ctx):
    v2i = json.loads((bi.EXP2I / "results" / "verdict.json").read_text())
    v2g = json.loads((bg.EXP2G / "results" / "verdict.json").read_text())
    v2h = json.loads((bh.EXP2H / "results" / "verdict.json").read_text())
    _eq(an.pin_from_record_2i(v2i), an.VERDICT_2I_PIN, "2i pin")
    _eq(an.pin_from_record_2g(v2g), an.VERDICT_2G_PIN, "2g pin")
    _eq(an.pin_from_record_2h(v2h), an.VERDICT_2H_PIN, "2h pin")


@check(9, "the tree on literal inputs: every terminal, the boundaries, all ABSORBED licences")
def _c9(ctx):
    def prim(T, p, fires, named=None, eligible=("a", "b", "c")):
        return {"stratified": {"T": T, "p": p, "n_perm": 100, "n_ge": 0},
               "fires": fires, "named_inside": named, "eligible": list(eligible)}

    power_powered = {"declared_status": "POWERED"}
    power_under = {"declared_status": "DECLARED UNDERPOWERED IN ADVANCE"}

    ins = an.verdict_tree_2j(["x"], None, None)
    _eq(ins["verdict"], "INSUFFICIENT_DATA", "refusal")
    _eq(an._licensed(ins), an.LICENSED_2J["INSUFFICIENT_DATA"], "refusal licence")

    fires = prim(0.20, 0.001, True)
    res = an.verdict_tree_2j([], fires, power_powered)
    _eq(res["verdict"], "RESIDUAL", "fires -> RESIDUAL")
    _eq(an._licensed(res), an.LICENSED_2J["RESIDUAL"], "RESIDUAL licence")

    no_fire = prim(0.02, 0.5, False)
    abs_powered = an.verdict_tree_2j([], no_fire, power_powered)
    _eq(abs_powered["verdict"], "ABSORBED", "no fire, POWERED -> ABSORBED")
    _eq(an._licensed(abs_powered), an.LICENSED_2J["ABSORBED"], "ABSORBED (POWERED) licence")

    abs_under = an.verdict_tree_2j([], no_fire, power_under)
    _eq(abs_under["verdict"], "ABSORBED", "no fire, UNDERPOWERED -> ABSORBED")
    _eq(an._licensed(abs_under), an.LICENSED_2J["ABSORBED_UNDERPOWERED"],
       "ABSORBED (underpowered) licence")

    undefined = prim(None, 1.0, False, named="undefined: no eligible rung", eligible=())
    abs_undef = an.verdict_tree_2j([], undefined, power_powered)
    _eq(an.DISCLOSURE_UNDEFINED_2J in abs_undef["disclosures"], True, "undefined disclosed")
    _eq(an._licensed(abs_undef), an.LICENSED_2J["ABSORBED_UNDEFINED"] + "; " +
       an.DISCLOSURE_UNDEFINED_2J, "ABSORBED (undefined) licence")

    thin = prim(0.02, 0.5, False, eligible=("a", "b"))
    abs_thin = an.verdict_tree_2j([], thin, power_powered)
    _eq(an.DISCLOSURE_THIN_2J in abs_thin["disclosures"], True, "thin disclosed")
    _eq(an._licensed(abs_thin), an.LICENSED_2J["ABSORBED_THIN"] + "; " + an.DISCLOSURE_THIN_2J,
       "ABSORBED (thin) licence")

    # the T_BAR/ALPHA boundaries, on 2i's shared `fires_2i` rule itself
    # (T_BAR inclusive, ALPHA exclusive) — then through the tree.
    _eq(an2i.fires_2i({"stratified": {"T": an.T_BAR, "p": an.ALPHA - 1e-6}}), True,
       "T == T_BAR (inclusive), p < ALPHA fires")
    _eq(an2i.fires_2i({"stratified": {"T": an.T_BAR - 1e-9, "p": an.ALPHA - 1e-6}}), False,
       "T just under T_BAR does not fire")
    _eq(an2i.fires_2i({"stratified": {"T": an.T_BAR + 0.1, "p": an.ALPHA}}), False,
       "p == ALPHA (not strictly under) does not fire")

    at_bar = prim(an.T_BAR, an.ALPHA - 1e-6, True)
    _eq(an.verdict_tree_2j([], at_bar, power_powered)["verdict"], "RESIDUAL",
       "T == T_BAR, p < ALPHA -> RESIDUAL through the tree")
    below_bar = prim(an.T_BAR - 1e-9, an.ALPHA - 1e-6, False)
    _eq(an.verdict_tree_2j([], below_bar, power_powered)["verdict"], "ABSORBED",
       "T just under T_BAR -> ABSORBED through the tree")


@check(10, "t_only's T == _run_test's stratified T on a toy, bit-for-bit")
def _c10(ctx):
    rng = np.random.default_rng(0)
    n = 40
    counts = {"toy": [int(v) for v in rng.integers(0, 64, size=n)]}
    y = [int(v) for v in rng.integers(0, 5, size=n)]
    for i in range(bg.ELIGIBILITY_MIN_POS):
        if y[i] == 0:
            y[i] = 1
    strata = {"toy": {"strata": ["0" if i % 2 == 0 else "1" for i in range(n)]}}
    out = {"toy": {"y": y}}
    a = an.t_only(counts, "1b", out, strata, ("toy",))
    b = an._run_test(counts, "1b", out, strata, ("toy",), n_perm=5, n_boot=2)
    _eq(a["T"], b["stratified"]["T"], "t_only vs _run_test T")


@check(11, "2i's committed power_2i.json B null SD / min-detectable T == power_2j.py's carried literals")
def _c11(ctx):
    from experiments.exp2j import power_2j as pw2j
    src = Path(pw2j.__file__).read_text()
    m = re.search(r'"null_sd_T":\s*([0-9.]+),\s*"min_detectable_T":\s*([0-9.]+)', src)
    if not m:
        raise AssertionError("power_2j.py's base_strata_reference literal not found in source")
    null_sd_lit, min_det_lit = float(m.group(1)), float(m.group(2))
    committed = json.loads(bi.power_path(bi.EXP2I).read_text())
    _eq(null_sd_lit, round(committed["B"]["null"]["null_sd_T"], 4), "null_sd_T literal")
    _eq(min_det_lit, round(committed["B"]["min_detectable_T"], 5), "min_detectable_T literal")


@check(12, "power_2j.json exists, declared_status valid, rungs == R_CAP")
def _c12(ctx):
    p = EXP2J / "results" / "power_2j.json"
    if not p.is_file():
        return "SKIP"
    rec = json.loads(p.read_text())
    rung_set = an2i._load_rung_set(bi.EXP2I)
    r_cap = set(rung_set["R_CAP"])
    _eq(rec["primary"]["declared_status"] in an2i.DECLARED_STATUSES_2I, True,
       "declared_status valid")
    _eq(set(rec["primary"]["rungs"]), r_cap, "rungs == R_CAP")
    # freeze coverage census: `_load_power_2j` also refuses on the grid
    # size, and (F-2) on the composite partition the record was
    # simulated over — both re-asserted cold here rather than only
    # inside the analyzer.
    _eq(rec["primary"]["n_trained_steps"], len(bi.trained_steps_7b()), "n_trained_steps")
    _eq(set(rec["composite_report"]), r_cap, "composite_report covers R_CAP")
    _eq(set(rec["n_composite_strata"]), r_cap, "n_composite_strata covers R_CAP")
    strata, tables = ctx["strata"], ctx["tables"]
    comp, report = fn.composite_strata(strata, {r: tables[r] for r in r_cap}, tuple(r_cap))
    _eq(an.check_power_partition_2j(rec, report,
                                    {r: len(set(comp[r]["strata"])) for r in r_cap},
                                    tuple(r_cap)), [],
       "the power record's partition == the one the analyzer builds today")


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
            print(f"  [{n:2d}] skip  {name} (pending Task 4)", flush=True)
        else:
            print(f"  [{n:2d}] ok    {name}", flush=True)
            n_ok += 1
    print(f"referent battery: {n_ok}/{len(CHECKS)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
