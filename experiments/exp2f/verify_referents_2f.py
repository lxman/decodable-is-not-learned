"""The Exp 2f referent battery: every §4 referent re-asserted
EXECUTABLE against the real committed trees — run at build, re-run
cold at the freeze. It STOPS SHORT of the verdict: no label-match
rate is computed on the committed draws or continuations here (those
are "derivable but not computed" until the tag, design §2), and the
eval-item activations do not exist before the collection.

 1  2f's 12 frozen-import pins byte-identical
 2  the two item files == their §4 pins (2d's); probe-label gates
    (sub3_mid middle digit 500/500; arith_next answer mod 7 500/500)
 3  referents_2f.json: file sha == the literal; 34 entries re-hash;
    the builder is byte-idempotent
 4  the 8 probe-item activation files == the literal pins == the
    lines of 2b's/2c's activations_sha256.txt
 5  the m3 machinery gate: 2b's starved probe on the committed
    activations reproduces the four committed m3 records EXACTLY
    (accuracy, best site, split counts)
 6  2d's main and pilot tiers for the four cells through 2d's loader:
    re-tally == stored == the exact-match pins (8/8); argmax records
    through 2d's loader == pins (4/4)
 7  floors: sub3_mid/mid_digit .132, arith_next/last_digit .120,
    arith_next/mod7 .156 (majority shares; every one ≥ 1/K)
 8  the tree and the pattern rule on synthetic inputs; α is 2b's/2d's
 9  the label functions' totality on 20,000 fuzzed strings
10  the eval-item activations and continuity records do NOT exist
    before the collection (or, if they do, pass their pins) — the
    battery reports which
"""

from __future__ import annotations

import hashlib
import json
import random
import sys
from pathlib import Path

EXP2F = Path(__file__).resolve().parent
if str(EXP2F.parent.parent) not in sys.path:
    sys.path.insert(0, str(EXP2F.parent.parent))

from experiments.exp2d import analyze_2d as a2d  # noqa: E402
from experiments.exp2d import battery_2d as bt  # noqa: E402
from experiments.exp2f import analyze_2f as a  # noqa: E402
from experiments.exp2f import labels_2f as lb  # noqa: E402
from experiments.exp2f import make_referents_2f as mk  # noqa: E402

CHECKS = []


def check(n, name):
    def deco(fn):
        CHECKS.append((n, name, fn))
        return fn
    return deco


def _eq(got, want, what):
    if got != want:
        raise AssertionError(f"{what}: got {got!r}, want {want!r}")


@check(1, "frozen-import pins (12)")
def _c1(ctx):
    a.check_frozen_imports_2f()
    _eq(len(a.FROZEN_IMPORT_SHA256_2F), 12, "pins")


@check(2, "item files + probe-label gates")
def _c2(ctx):
    ctx["battery"] = {r: bt.load_item_file(r) for r in lb.RUNGS}
    g = lb.check_probe_label_gates(ctx["battery"])
    _eq(g, {"sub3_mid/mid_digit": "PASS (500/500)",
            "arith_next/mod7": "PASS (500/500)"}, "gates")


@check(3, "referents_2f.json: literal sha, 34 entries, idempotent")
def _c3(ctx):
    rec = a.load_manifest()
    _eq(rec["n_files"], 34, "n_files")
    _eq(a.check_manifest(rec), [], "manifest failures")
    tmp = EXP2F / ".referents_2f.rebuild.json"
    try:
        mk.build(tmp)
        _eq(tmp.read_bytes() == a.REFERENTS_PATH.read_bytes(), True,
            "byte-idempotent")
    finally:
        tmp.unlink(missing_ok=True)


@check(4, "8 activation files == literal pins == digest lists")
def _c4(ctx):
    for (rung, size, mode), want in a.PROBE_NPZ_SHA_PIN.items():
        p = mk.probe_npz_path(size, mode, rung)
        got = hashlib.sha256(p.read_bytes()).hexdigest()
        _eq(got, want, f"{rung}/{size}/{mode}")
        exp = bt.EXP2B if rung in bt.REUSED else bt.EXP2C
        txt = (exp / "results" / "activations_sha256.txt").read_text()
        _eq(f"{want}  activations/{size}_{mode}/{rung}.npz" in txt, True,
            f"digest line {rung}/{size}/{mode}")


@check(5, "m3 machinery gate: four committed records reproduced exactly")
def _c5(ctx):
    _eq(a.check_m3_gate(ctx["battery"], a.M3_PIN), [], "m3 gate")
    for (rung, size), pin in a.M3_PIN.items():
        rec = json.loads(mk.m3_record_path(size, rung).read_text())
        _eq(a.m3_pin_from_record(rec), pin, f"m3 literal {rung}/{size}")


@check(6, "2d's tiers and argmax for the four cells == exact-match pins")
def _c6(ctx):
    verify = a2d.load_verify()
    tallies = {}
    for tier in ("main", "pilot"):
        cells = a2d.load_sampling_tier(a2d.EXP2D, tier, ctx["battery"], verify,
                                       rungs=lb.RUNGS)
        for (rung, size), c in cells.items():
            tallies[(rung, size, tier)] = c["verified"]
    arg = a2d.load_argmax(a2d.EXP2D, ctx["battery"], verify, rungs=lb.RUNGS)
    for (rung, size), c in arg.items():
        tallies[(rung, size, "argmax")] = c["correct"]
    _eq(a.check_exact_pin(tallies, a.EXACT_MATCH_PIN), [], "exact pins")
    _eq(len(tallies), 12, "cells")


@check(7, "floors")
def _c7(ctx):
    t = lb.floor_table(ctx["battery"])
    _eq(round(t[("sub3_mid", "mid_digit")]["floor"], 3), .132, "sub3_mid")
    _eq(round(t[("arith_next", "last_digit")]["floor"], 3), .120, "arith last")
    _eq(round(t[("arith_next", "mod7")]["floor"], 3), .156, "arith mod7")
    for k, v in t.items():
        _eq(v["floor"] >= 1 / v["n_classes"], True, f"{k} ≥ 1/K")


@check(8, "tree, pattern rule, α")
def _c8(ctx):
    c = {"x": {"D": [False, True, True], "void": False}}
    _eq(a.verdict_tree_2f([], c, 0)["verdict"], "INVERTED", "inverted")
    c["x"]["D"] = [True, True, False]
    _eq(a.verdict_tree_2f([], c, 0)["verdict"], "LADDER", "ladder")
    c["x"]["D"] = [False, False, False]
    _eq(a.verdict_tree_2f([], c, 0)["verdict"], "SILENT", "silent")
    _eq(a.verdict_tree_2f([], c, 2)["verdict"], "INSUFFICIENT_DATA", "void")
    from experiments.exp2b import probe_starved as ps
    from experiments.exp2d import stats_2d as st
    _eq((a.ALPHA is ps.ALPHA, a.ALPHA == st.ALPHA), (True, True), "alpha")


@check(9, "label totality (20,000 fuzzed strings)")
def _c9(ctx):
    rng = random.Random(0)
    alphabet = " 0123456789,-.\n#Qabc~"
    for _ in range(20_000):
        s = "".join(rng.choice(alphabet) for _ in range(rng.randrange(0, 12)))
        for kind in ("mid_digit", "last_digit", "mod7"):
            out = lb.emission_label(kind, s)
            _eq(out is lb.MISS or len(out) == 1, True, "total")


@check(10, "eval activations / continuity: absent before the collection")
def _c10(ctx):
    present = [str(p) for p in
               [a.eval_npz_path(a.EXP2F, s, m, r) for s in lb.SIZES
                for m in mk.MODES for r in lb.RUNGS]
               + [a.continuity_path(a.EXP2F, s, m) for s in lb.SIZES
                  for m in mk.MODES]
               if p.exists()]
    if present:
        for s in lb.SIZES:
            for m in mk.MODES:
                rec = json.loads(a.continuity_path(a.EXP2F, s, m).read_text())
                _eq(a.continuity_pass(rec), [], f"continuity {s}/{m}")
        print(f"      (collection present: {len(present)} files, continuity "
              f"4/4 pass)")
    else:
        print("      (no collection yet — as expected before the tag)")


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
