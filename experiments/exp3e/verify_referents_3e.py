"""The Exp 3e referent battery: every §4 referent, re-asserted
EXECUTABLE against the real committed trees — run at build, re-run
cold at the freeze, and equivalent in content to what run() enforces
on the way to a verdict (the checks live in the frozen loaders; this
battery exists so they can be exercised without a tranche on disk).

Numbered checks, all-or-nothing:
 1  frozen-import pins byte-identical (exp3 ×5, 3c ×3, 3d ×4, 2c, 2b)
 2  item files: sha pins + the strata pin (194/155/151); the len-4
    stratum splits 45 repeat-class + 149 all-distinct
 3  3b-derived sha_refs == the §4 literal pins (two sources, one value)
 4  the 45-item subset: literal == recompute from the item file ==
    partition record; subset sha; the 13 non-reachable == the §3 list
 5  partition_3e.json reproduces from the item file; file sha pinned;
    printed classification matches the doc (17/15/13; |M| 10/6/5/11;
    variants 21/15; no palindromes)
 6  power_3e.json: m_min 8, m_min_anti 3, THIN_MAX 10, m_s,min 3 ==
    recompute from the frozen partition
 7  stream_map_3e.json == the frozen formula + continuity with exp3,
    3c AND 3d maps; subset substreams == the imported formula
 8  every committed draws file == its §4 literal sha (13 reverse_string
    + 2 ctrl_copy); the 3c pair also == 3d's own literal pins
 9  the 26 committed fires re-scored from raw bytes == the §4 pin;
    the 19 repeat-class addresses == the subset filter (gate a)
10  ctrl_copy re-scored at target = copy answer == 12787/16000 and
    13460/16000 (gate b); both == exp3's sha-pinned verdict entries
11  results/scorer_gates.json: present, PASS, referents == pins
12  the twin record: 0 fires / 512,000 + 64,000 draws, from raw bytes
    through exp3's own loader
13  the verify wrapper: 3c's crasher class scores False on the draw
    side; answer-side crash stays a hard error (criterion totality)
14  gate-1 referents: the expected fires at seeds 20 (1b) / 24 (410m)
    are present in the committed 3d shards at their addresses, and the
    shards carry every subset item (coverage pinned at 2,880)
15  3d's verdict record (sha-pinned): its new-fire addresses == the
    3d-source entries of the 26-address pin
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

EXP3E = Path(__file__).resolve().parent
if str(EXP3E.parent.parent) not in sys.path:
    sys.path.insert(0, str(EXP3E.parent.parent))
for _p in (EXP3E.parent / "exp2b", EXP3E.parent / "exp2c"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from experiments.exp3 import analyze_3 as a3  # noqa: E402
from experiments.exp3c import analyze_3c as c  # noqa: E402
from experiments.exp3d import analyze_3d as d  # noqa: E402
from experiments.exp3e import analyze_3e as e  # noqa: E402
from experiments.exp3e import partition_3e as pt  # noqa: E402
from experiments.exp3e import scorer_3e as sc  # noqa: E402
from experiments.exp3e.rederive_3e import subset_committed_rows  # noqa: E402

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
    e.check_frozen_imports_3e()


@check(2, "item files: sha + strata pins; 45 + 149 split")
def _c2(ctx):
    ctx["items"] = d.load_item_file(e.RUNG)
    ctx["ctrl"] = d.load_item_file(a3.POSITIVE_CONTROL)
    answers = ctx["items"]["answers"]
    _eq(len(pt.repeat_class_len4(answers)), 45, "repeat class")
    _eq(len(e.all_distinct_len4(answers)), e.N_ALL_DISTINCT_LEN4,
        "all-distinct len-4")


@check(3, "3b-derived sha_refs == §4 literal pins")
def _c3(ctx):
    gate2 = a3.load_gate2_referents()
    sha_refs = a3.items_sha_referents(gate2)
    ctx["sha_refs"] = sha_refs
    for rung in (e.RUNG, a3.POSITIVE_CONTROL):
        _eq(sha_refs.get(rung), e.ITEMS_SHA_PIN[rung], f"{rung} sha")


@check(4, "subset literal == recompute == partition; non-reachable list")
def _c4(ctx):
    answers = ctx["items"]["answers"]
    _eq(tuple(pt.repeat_class_len4(answers)), e.SUBSET_ITEMS_PIN,
        "subset literal")
    _eq(e.subset_sha256(e.SUBSET_ITEMS_PIN), e.SUBSET_SHA256_PIN,
        "subset sha")
    ctx["partition"] = e.load_partition_3e(
        answers, subset_pin=e.SUBSET_ITEMS_PIN,
        file_sha_pin=e.PARTITION_FILE_SHA256,
        non_reachable_pin=e.NON_REACHABLE_PIN)


@check(5, "partition record == doc's printed classification")
def _c5(ctx):
    p = ctx["partition"]
    _eq({k: len(v) for k, v in p["sub_classes"].items()},
        {"transposition": 17, "rotation": 15, "non_reachable": 13},
        "sub-classes")
    _eq(p["pattern_counts"], {"0,1": 8, "2,3": 5, "0,2": 10, "0,3": 6,
                              "1,2": 11, "1,3": 5}, "pattern counts")
    from collections import Counter
    m = Counter((tuple(en["repeat_pattern"]), len(en["matched_competitors"]))
                for en in p["entries"] if en["reachable"])
    _eq(dict(m), {((0, 2), 1): 10, ((0, 3), 2): 6, ((1, 3), 3): 5,
                  ((1, 2), 0): 11}, "|M| structure")
    _eq(len(p["arm_items"]), 21, "arm items")
    _eq(len(p["arm_sit_out"]), 11, "sit-out items")
    _eq({v: len(p["variants"][v]["reachable"]) for v in p["variants"]},
        {"adjacent": 21, "rotations": 15}, "variants")
    for en in p["entries"]:
        _eq(len(en["neighbours"]), 7, f"|N| of item {en['item']}")
        _eq(en["entropy_bits"], 6.0, f"entropy of item {en['item']}")


@check(6, "power record pins == recompute")
def _c6(ctx):
    ctx["power"] = e.load_power_pin_3e(ctx["partition"])
    _eq((ctx["power"]["m_min"], ctx["power"]["m_min_anti_disclosed"],
         ctx["power"]["thin_max"], ctx["power"]["m_s_min"]),
        (8, 3, 10, 3), "power pins")


@check(7, "stream map == formula + continuity with exp3/3c/3d")
def _c7(ctx):
    e.check_stream_map_3e()
    d.check_stream_map_3d()
    c.check_stream_map()


@check(8, "committed draws files == §4 literal shas (+ 3d's pins)")
def _c8(ctx):
    for size in e.SIZES_3E:
        _eq(e.COMMITTED_DRAWS_SHA256[e.RUNG][size]["3c"],
            d.COMMITTED_3C_DRAWS_SHA256[size], f"3c {size} sha vs 3d pin")
    ctx["rows"] = e.load_committed_rows()     # sha-checks every file


@check(9, "26 committed fires re-scored == pin; 19 == subset (gate a)")
def _c9(ctx):
    ctx["score"] = sc.load_scorer()
    ctx["base"] = e.committed_base_3e(
        ctx["rows"], ctx["items"]["answers"], ctx["items"]["answer_type"],
        ctx["score"], ctrl_answers=ctx["ctrl"]["answers"],
        ctrl_answer_type=ctx["ctrl"]["answer_type"])
    for size in e.SIZES_3E:
        _eq(ctx["base"][size]["subset_addresses"],
            e.REPEAT_CLASS_FIRES_PIN[size], f"gate (a) {size}")
        _eq(ctx["base"][size]["n_draws_per_item"], e.K_COMMITTED[size],
            f"committed draws per item {size}")


@check(10, "ctrl_copy re-scored == 12787/16000, 13460/16000 (gate b)")
def _c10(ctx):
    v = json.loads((e.EXP3 / "results" / "verdict.json").read_text())
    for size in e.SIZES_3E:
        _eq(ctx["base"]["ctrl_gate_b"][size], e.CTRL_SAMPLED_RATE_PIN[size],
            f"gate (b) {size}")
        entry = v["fires"][f"{a3.POSITIVE_CONTROL}/{size}/trained"]
        _eq((entry["full_string_total"], entry["n_draws"]),
            (e.CTRL_SAMPLED_RATE_PIN[size]["count"],
             e.CTRL_SAMPLED_RATE_PIN[size]["n_draws"]),
            f"exp3 verdict ctrl entry {size}")


@check(11, "scorer_gates.json present, PASS, referents == pins")
def _c11(ctx):
    e.load_scorer_gates_3e()


@check(12, "twin record 0 / 512k + 64k from raw bytes")
def _c12(ctx):
    t = e.load_twin_record(e.EXP3)
    _eq((t["fires"], t["reversal_twin_draws"], t["control_twin_draws"]),
        (0, e.TWIN_PINS["reversal"], e.TWIN_PINS["control"]), "twin")


@check(13, "verify wrapper totality (draw side) + answer-side hard error")
def _c13(ctx):
    score = ctx["score"]
    for crasher in (".\t.", "'\x0b'", '"\r"'):
        if score(crasher, "ecde", "word") is not False:
            raise AssertionError(f"crasher {crasher!r} did not score False")
    try:
        score(" ecde", ".\t.", "word")
    except IndexError:
        pass
    else:
        raise AssertionError("answer-side crash did not raise")


@check(14, "gate-1 referents present in the committed 3d shards")
def _c14(ctx):
    for size in e.SIZES_3E:
        rows = ctx["rows"][e.RUNG][size]
        seed = str(e.GATE1_SEED_3E[size])
        sub = subset_committed_rows(
            [{"item": i, "draws": {seed: rows[i][seed]}}
             for i in e.SUBSET_ITEMS_PIN], e.SUBSET_ITEMS_PIN)
        _eq(sum(len(r["draws"][seed]) for r in sub), e.GATE1_COVERAGE,
            f"gate-1 coverage {size}")
        answers = ctx["items"]["answers"]
        got = []
        for r in sub:
            for d_idx, text in enumerate(r["draws"][seed]):
                if ctx["score"](text, answers[r["item"]],
                                ctx["items"]["answer_type"]):
                    got.append({"item": r["item"], "seed": int(seed),
                                "draw": d_idx})
        _eq(got, e.GATE1_EXPECTED_FIRES[size], f"gate-1 fires {size}")


@check(15, "3d verdict record (sha-pinned) new fires == 3d-source pin")
def _c15(ctx):
    v = json.loads((e.EXP3D / "results" / "verdict.json").read_text())
    for size in e.SIZES_3E:
        got = e._sorted_addresses(v["fires"][size]["addresses"])
        want = e._sorted_addresses(a for a in e.COMMITTED_FIRES_PIN[size]
                                   if a["source"] == "3d")
        _eq(got, want, f"3d verdict addresses {size}")


def main() -> int:
    ctx = {}
    failed = []
    for n, name, fn in CHECKS:
        try:
            fn(ctx)
            print(f"  {n:2d} ok   {name}")
        except Exception as ex:  # noqa: BLE001 — every failure named
            failed.append((n, name, ex))
            print(f"  {n:2d} FAIL {name}: {ex}")
    print(f"{len(CHECKS) - len(failed)}/{len(CHECKS)} referent checks "
          f"passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
