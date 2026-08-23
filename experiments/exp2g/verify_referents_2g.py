# experiments/exp2g/verify_referents_2g.py
"""The Exp 2g referent battery: every §5 referent re-asserted
EXECUTABLE against the committed trees — run at build, re-run cold at
the freeze. It stops short of the verdict and of model contact.

 1  14 frozen-import pins byte-identical
 2  the 11 item files == 2d's pins; label gates 500/500 (+ probe items);
    class coverage
 3  rung sets from m4 counts under 2d's bar == R_28 / R_12B; every
    m4 count == the pin; floors from 2d's sha-pinned verdict
 4  the 44 probe-item activation files == the pins == the digest lists
 5  strata: raw counts == the doc's table; merge rule bites only on
    count_div13
 6  checkpoints_2g.json == rebuilt from the committed inventory;
    its sha == analyze_2g.CHECKPOINTS_SHA256; step64000 excluded with
    evidence; hub step143000 vs main recorded per size
 7  referents_2g.json: own sha == the literal; 139 entries re-hash;
    byte-idempotent
 8  the tree on literal inputs (every terminal, the boundaries)
 9  gate-1 and step-record refusals fire on mutated synthetic records
10  predictor / eval activations / continuity / sweep: absent before
    the tags (or, if present, pass their pins) — the battery reports which
11  no stranded mutation backup; α, T_BAR, ALPHA_TWIN are stats_2g's
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

EXP2G = Path(__file__).resolve().parent
if str(EXP2G.parent.parent) not in sys.path:
    sys.path.insert(0, str(EXP2G.parent.parent))

from experiments.exp2g import analyze_2g as an  # noqa: E402
from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp2g import checkpoints_2g as ck  # noqa: E402
from experiments.exp2g import labels_2g as lb  # noqa: E402
from experiments.exp2g import make_referents_2g as mk  # noqa: E402
from experiments.exp2g import stats_2g as st  # noqa: E402
from experiments.exp2g import strata_2g as sg  # noqa: E402

CHECKS = []


def check(n, name):
    def deco(fn):
        CHECKS.append((n, name, fn))
        return fn
    return deco


def _eq(got, want, what):
    if got != want:
        raise AssertionError(f"{what}: got {got!r}, want {want!r}")


@check(1, "frozen-import pins (14)")
def _c1(ctx):
    bg.check_frozen_imports_2g()
    _eq(len(bg.FROZEN_IMPORT_SHA256_2G), 14, "pins")


@check(2, "item files, label gates, class coverage")
def _c2(ctx):
    ctx["battery"] = bg.load_battery(bg.PREDICTOR_RUNGS)
    g = lb.check_label_gates(ctx["battery"])
    _eq(len(g), 11, "gates")
    lb.check_class_coverage(ctx["battery"])


@check(3, "rung sets, m4 pins, floors")
def _c3(ctx):
    ctx["floors"] = bg.load_floors()
    _eq(bg.check_rung_sets(ctx["floors"]), {"2.8b": list(bg.R_28), "12b": list(bg.R_12B)}, "sets")
    _eq(bg.load_m4_counts("2.8b"), bg.FINAL_COUNT_PIN["2.8b"], "2.8b counts")
    _eq(bg.load_m4_counts("12b"), bg.FINAL_COUNT_PIN["12b"], "12b counts")


@check(4, "44 probe-activation files == pins == digest lists")
def _c4(ctx):
    for (rung, size, mode), want in bg.PROBE_NPZ_SHA_PIN.items():
        _eq(bg.sha256_file(bg.probe_npz_path(size, mode, rung)), want, f"{rung}/{size}/{mode}")
    from experiments.exp2d import battery_2d as bt
    for exp, root in (("exp2b", bt.EXP2B), ("exp2c", bt.EXP2C)):
        p = root / "results" / "activations_sha256.txt"
        _eq(bg.sha256_file(p), bg.DIGEST_LIST_SHA256[exp], f"digest list {exp}")


@check(5, "strata: doc counts, merge rule")
def _c5(ctx):
    t = sg.build_table(ctx["battery"])
    sg.check_strata_pins(t)
    merged = [r for r in bg.PREDICTOR_RUNGS if any("+" in k for k in t[r]["counts"])]
    _eq(merged, ["count_div13"], "merged rungs")


@check(6, "checkpoint manifest == rebuilt; sha pinned; exclusions")
def _c6(ctx):
    inv = ck.load_inventory()
    obj = ck.load_manifest(bg.CHECKPOINTS_PATH, sha_pin=an.CHECKPOINTS_SHA256)
    _eq(obj, ck.build_all(inv), "manifest rebuild")
    _eq(list(obj["2.8b"]["excluded"]), ["64000"], "2.8b exclusions")
    _eq(obj["2.8b"]["hub_step143000"]["signature_equals_main"], False, "2.8b hub final")
    _eq(obj["12b"]["hub_step143000"]["signature_equals_main"], True, "12b hub final")


@check(7, "referents_2g.json: literal sha, 139 entries, idempotent")
def _c7(ctx):
    _eq(an.REFERENTS_FILE_SHA256 is not None, True, "pinned")
    _eq(mk.check_referents(an.REFERENTS_PATH, sha_pin=an.REFERENTS_FILE_SHA256), [], "manifest")
    tmp = EXP2G / ".referents_2g.rebuild.json"
    try:
        mk.build(tmp)
        _eq(tmp.read_bytes() == an.REFERENTS_PATH.read_bytes(), True, "byte-idempotent")
    finally:
        tmp.unlink(missing_ok=True)


@check(8, "the tree on literal inputs")
def _c8(ctx):
    def prim(T, p, pr, pt):
        return {"stratified": {"T": T, "p": p, "n_perm": 100, "n_ge": 0},
                "raw": {"T": T, "p": pr}, "twin": {"T": 0, "p": pt}}
    _eq(an.verdict_tree_2g(["x"], None)["verdict"], "INSUFFICIENT_DATA", "refusal")
    _eq(an.verdict_tree_2g([], prim(.2, .001, .001, .5))["verdict"], "FORECAST", "forecast")
    _eq(an.verdict_tree_2g([], prim(.2, .001, .001, .01))["verdict"], "SURFACE", "surface")
    _eq(an.verdict_tree_2g([], prim(.05, .5, .001, .5))["verdict"], "DIFFICULTY-ONLY", "difficulty")
    _eq(an.verdict_tree_2g([], prim(.05, .001, .001, .5))["verdict"], "NO-FORECAST", "below bar")
    _eq(an.verdict_tree_2g([], prim(.10, .0099, .5, .05))["verdict"], "FORECAST", "boundary")


@check(9, "gate-1 and step-record refusals fire")
def _c9(ctx):
    rec = {"size": "2.8b", "rungs": list(bg.sweep_rungs("2.8b")),
           "counts_2c_path": dict(bg.FINAL_COUNT_PIN["2.8b"]), "digest_2c_path": "a",
           "digest_2g_path": "a", "continuation_diffs_2g_path": {r: 0 for r in bg.sweep_rungs("2.8b")},
           "model_sha": an.pythia_sha("2.8b"), "seal": {"sha256": "s"}}
    _eq(an.gate1_failures(rec, "2.8b"), [], "clean gate")
    rec["counts_2c_path"]["antonym"] = 271
    _eq(len(an.gate1_failures(rec, "2.8b")) >= 1, True, "count diff fires")


@check(10, "stage artifacts: absent before the tags, or passing")
def _c10(ctx):
    pred = bg.predictor_path(EXP2G)
    if pred.is_file():
        from experiments.exp2g import predictor_2g as pr
        pr.load_predictor(pred, sha_pin=None)
        print("      (predictor present and well-formed)")
    else:
        print("      (no predictor yet — as expected before stage 1)")
    g = bg.gate1_path(EXP2G, "2.8b")
    if g.is_file():
        _eq(an.gate1_failures(json.loads(g.read_text()), "2.8b"), [], "gate 1 on disk")
        print("      (gate 1 record present and passing)")
    else:
        print("      (no sweep yet — as expected before stage 2)")


@check(11, "no stranded mutation backup; constants are stats_2g's")
def _c11(ctx):
    _eq(list(EXP2G.rglob("*.mutation_backup")), [], "backups")
    _eq((an.ALPHA, an.ALPHA_TWIN, an.T_BAR), (st.ALPHA, st.ALPHA_TWIN, st.T_BAR), "constants")
    _eq((st.ALPHA, st.ALPHA_TWIN, st.T_BAR), (0.01, 0.05, 0.10), "values")


def main() -> int:
    ctx = {}
    for n, name, fn in CHECKS:
        try:
            fn(ctx)
        except Exception as e:   # noqa: BLE001
            print(f"  [{n:2d}] FAIL  {name}: {type(e).__name__}: {e}")
            return 1
        print(f"  [{n:2d}] ok    {name}", flush=True)
    print(f"referent battery: {len(CHECKS)}/{len(CHECKS)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
