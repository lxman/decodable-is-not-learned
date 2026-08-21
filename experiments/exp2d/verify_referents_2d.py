"""The Exp 2d referent battery: every §4 referent, re-asserted
EXECUTABLE against the real committed trees — run at build, re-run
cold at the freeze, and equivalent in content to what run() enforces
on the way to a verdict (the checks live in the frozen loaders; this
battery exists so they can be exercised without a campaign on disk).

Numbered checks, all-or-nothing:
 1  frozen-import pins byte-identical (2c ×10, 2b, exp3 ×4, 3c, 3d)
 2  the 34 item files == their §4 pins; the 12 survivors' == 2c's
    reuse manifest; answer types == the registry; two types present
 3  RUNG_ORDER_2D == 2c's family map == probe_scores.json row order;
    family sizes (4,2,2,4,2,2,1,2,1,1,2,4,2,2,1,2)
 4  referents_2d.json: file sha == the literal pin; all 250 entries
    re-hash on disk
 5  majority floors reproduce §4's printed table (with the two
    ledgered slips); every floor ≥ 1/500
 6  the OUTCOME known-answer gate: 2c's m5 rule on the committed m4
    records reproduces ascent_scores.json 34/34; the frozen §5.2 rule
    yields 13 rising / 21 flat (12 at 12b only) in 7 families
 7  stream_map_2d.json == the frozen formula; seed-0 reversal entries
    == exp3's committed map (continuity, 4 cells)
 8  exp3's four committed reversal shards == their §4 literal shas;
    reverse_string's == 3e's pins by value
 9  gate-1 comparator on committed bytes: exp3's own seed-0 rows
    through `compare_rows` → 0 diffs on all four cells, fires == the
    expected addresses (item 436 / draw 6 at reverse_string/1b only)
10  the twin record: 0 fires / 512,000 + 64,000 draws from raw bytes
    through exp3's own loader
11  the verify wrapper: 3c's crasher class scores False on the draw
    side; answer-side crash stays a hard error; FILLER verifies for
    neither answer type present
12  2c's verdict.json == the VERDICT_2C_PIN literals (ρ .368, block p
    .1305, CI, FAIL)
13  the block-permutation group for the pinned family vector routes
    to `sampled` (52,254,720 > 5e6) with 100,000 draws — 2c's own
    routing on the same vector
14  exp3's four committed redecode records == their §4 literal shas
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

EXP2D = Path(__file__).resolve().parent
if str(EXP2D.parent.parent) not in sys.path:
    sys.path.insert(0, str(EXP2D.parent.parent))

from experiments.exp2d import analyze_2d as a  # noqa: E402
from experiments.exp2d import battery_2d as bt  # noqa: E402
from experiments.exp2d import rederive_2d as rd  # noqa: E402
from experiments.exp2d import stats_2d as st  # noqa: E402

CHECKS = []


def check(n, name):
    def deco(fn):
        CHECKS.append((n, name, fn))
        return fn
    return deco


def _eq(got, want, what):
    if got != want:
        raise AssertionError(f"{what}: got {got!r}, want {want!r}")


@check(1, "frozen-import pins")
def _c1(ctx):
    a.check_frozen_imports_2d()


@check(2, "item files: sha pins, survivors == manifest, answer types")
def _c2(ctx):
    ctx["battery"] = bt.load_battery()
    _eq(len(ctx["battery"]), 34, "battery size")
    types = {c["answer_type"] for c in ctx["battery"].values()}
    _eq(types, set(bt.ANSWER_TYPES_PRESENT), "answer types present")


@check(3, "RUNG_ORDER_2D == family map == probe_scores order")
def _c3(ctx):
    r = bt.check_order_against_2c()
    _eq(tuple(r["family_sizes"]), (4, 2, 2, 4, 2, 2, 1, 2, 1, 1, 2, 4, 2, 2,
                                   1, 2), "family sizes")


@check(4, "referents_2d.json: file sha pinned, 250 entries re-hash")
def _c4(ctx):
    ref = a.load_referents()
    _eq(ref["n_files"], 250, "referent count")
    ctx["referents"] = ref


@check(5, "majority floors == §4 table; every floor ≥ 1/500")
def _c5(ctx):
    ctx["floors"] = bt.floor_table(ctx["battery"])
    bt.check_floors_against_doc(ctx["floors"])
    for r, f in ctx["floors"].items():
        if f["floor"] < 1 / 500:
            raise AssertionError(f"{r}: floor {f['floor']} < 1/500")


@check(6, "outcome known-answer gate; 13/21 rising split in 7 families")
def _c6(ctx):
    out = a.load_outcome(ctx["floors"], referents=ctx["referents"])
    _eq(out["n_rising"], 13, "n rising")
    _eq(out["n_rising_12b"], 12, "n rising at 12b only")
    _eq(len(out["families_with_rising"]), 7, "families with rising")
    _eq(sorted(r for r in a.RUNGS if out["rungs"][r]["rising"]),
        ["add3_mid", "add_base8", "antonym", "antonym6", "arith_next",
         "count_div13", "median5", "median7", "odd6", "odd_one_out",
         "sub3_mid", "sub4_mid", "sub_base8"], "rising set")
    ctx["outcome"] = out


@check(7, "stream_map_2d.json == formula; continuity with exp3 (4 cells)")
def _c7(ctx):
    r = a.check_stream_map_2d()
    _eq(r["n_cells"], 136, "map cells")


@check(8, "exp3's 4 committed reversal shards == §4 literals (== 3e's)")
def _c8(ctx):
    for rung in a.REVERSAL_RUNGS:
        for size in a.PROBE_SIZES:
            _, gz = rd.committed_shard_paths(rung, size)
            got = hashlib.sha256(gz.read_bytes()).hexdigest()
            _eq(got, a.COMMITTED_DRAWS_SHA256[rung][size],
                f"{rung}/{size} shard sha")
    from experiments.exp3e import analyze_3e as e
    for size in a.PROBE_SIZES:
        _eq(a.COMMITTED_DRAWS_SHA256["reverse_string"][size],
            e.COMMITTED_DRAWS_SHA256["reverse_string"][size]["exp3"],
            f"reverse_string/{size} == 3e's pin")


@check(9, "gate-1 comparator on committed bytes: 0 diffs, fires == pin")
def _c9(ctx):
    from experiments.exp3.run.run_cell import read_draws
    vf = a.load_verify()
    ctx["verify"] = vf
    for rung in a.REVERSAL_RUNGS:
        cap = ctx["battery"][rung]
        answers = [str(it["answer"]) for it in cap["eval_items"]]
        for size in a.PROBE_SIZES:
            _, gz = rd.committed_shard_paths(rung, size)
            rows = [{"item": r["item"], "draws": {"0": r["draws"]["0"]}}
                    for r in read_draws(gz)]
            cmp = rd.compare_rows(rung, size, rows, answers=answers,
                                  answer_type=cap["answer_type"],
                                  verify_fn=vf)
            _eq(len(cmp["diffs"]), 0, f"{rung}/{size} diffs")
            _eq(cmp["draws_compared"], a.GATE1_COVERAGE,
                f"{rung}/{size} coverage")
            _eq(cmp["fires"], list(a.GATE1_EXPECTED_FIRES[(rung, size)]),
                f"{rung}/{size} fires")


@check(10, "twin record 0 / 512,000 + 64,000 through exp3's loader")
def _c10(ctx):
    tw = a.load_twin_record(verify_fn=ctx["verify"])
    _eq((tw["fires"], tw["reversal_twin_draws"], tw["control_twin_draws"]),
        (0, 512_000, 64_000), "twin")


@check(11, "verify wrapper totality: crasher False; answer side hard")
def _c11(ctx):
    vf = ctx["verify"]
    _eq(vf("'\t'", "abcd", "word"), False, "3c crasher class (quote-wrapped tab)")
    _eq(vf("(\u2003)", "abcd", "word"), False, "punctuation-wrapped em space")
    _eq(vf("", "abcd", "word"), False, "empty draw")
    _eq(vf(" ~~", "12", "number"), False, "filler/number")
    _eq(vf(" ~~", "abcd", "word"), False, "filler/word")
    _eq(vf(" 12\nfoo", "12", "number"), True, "number first line")
    _eq(vf(" Abcd.", "abcd", "word"), True, "word normalized")
    try:
        vf("x", "'\t'", "word")
    except IndexError:
        pass
    else:
        raise AssertionError("answer-side crash must stay a hard error")


@check(12, "2c's verdict.json == VERDICT_2C_PIN")
def _c12(ctx):
    v = json.loads((a.EXP2C / "results" / "verdict.json").read_text())
    for k in ("rho", "block_p", "ci", "verdict"):
        _eq(v[k], a.VERDICT_2C_PIN[k], f"2c verdict {k}")


@check(13, "block group routes to sampled (52,254,720) at 100,000")
def _c13(ctx):
    g = st.block_perm_group(bt.FAMILY_SIZES)
    _eq(g["method"], "sampled", "routing")
    _eq(g["group_size"], 52_254_720, "group size")
    _eq(g["perms"].shape, (st.PERM_SAMPLE, 34), "perm matrix shape")
    # 2c's own exact_block_p routes identically on the same vector
    import numpy as np
    r = st.spearman_block_p(np.arange(34.0), np.arange(34.0), bt.FAMILY_SIZES)
    _eq(r["method"], "sampled", "2c routing")
    _eq(r["n_perms"], st.PERM_SAMPLE, "2c n_perms")


@check(14, "exp3's 4 committed redecode records == §4 literals")
def _c14(ctx):
    for rung in a.REVERSAL_RUNGS:
        for size in a.PROBE_SIZES:
            p = a.EXP3 / "results" / "redecode" / f"{size}_trained" / f"{rung}.json"
            got = hashlib.sha256(p.read_bytes()).hexdigest()
            _eq(got, a.COMMITTED_REDECODE_SHA256[rung][size],
                f"{rung}/{size} redecode sha")
            rec = json.loads(p.read_text())
            _eq(len(rec["continuations"]), 500, "continuations")
            _eq(rec["max_new_tokens"], bt.max_new_tokens(rung), "budget")


def run_all(out_path=None) -> dict:
    ctx = {}
    results = []
    for n, name, fn in CHECKS:
        try:
            fn(ctx)
            results.append({"n": n, "name": name, "ok": True})
            print(f"  [{n:2d}] OK   {name}", flush=True)
        except Exception as e:  # noqa: BLE001 — the battery reports, then fails
            results.append({"n": n, "name": name, "ok": False,
                            "error": f"{type(e).__name__}: {e}"})
            print(f"  [{n:2d}] FAIL {name}: {type(e).__name__}: {e}",
                  flush=True)
    rec = {"n_checks": len(results),
           "n_ok": sum(r["ok"] for r in results),
           "all_ok": all(r["ok"] for r in results),
           "checks": results}
    if out_path:
        Path(out_path).write_text(json.dumps(rec, indent=1))
    return rec


if __name__ == "__main__":
    rec = run_all(EXP2D / "referent_check_2d.json")
    print(f"[2d referents] {rec['n_ok']}/{rec['n_checks']} "
          f"{'ALL OK' if rec['all_ok'] else 'FAILURES'}")
    sys.exit(0 if rec["all_ok"] else 1)
