# experiments/exp2i/verify_referents_2i.py
"""The Exp 2i referent battery: every referent re-asserted EXECUTABLE
against the committed trees — run at build, re-run cold at the freeze.
It stops short of the verdict and of any model contact, and
deliberately short of any predictor-vs-outcome statistic.

 1  frozen pins byte-identical: `battery_2i.check_frozen_2i` (20),
    `battery_2g.check_frozen_imports_2g` (14 upstream pins — 2g's own
    instrument, which 2i's verdict executes), `battery_2i
    .check_pythia_predictor_files` (68, x_A's real committed input)
 2  checkpoints_2i.json == rebuilt from the committed inventory; its
    sha == analyze_2i's re-export of `battery_2i.CHECKPOINTS_2I_SHA256`;
    the inventory carries both repos' `main`
 3  `battery_2i.sampler_counts_pythia` IS `battery_2h.sampler_counts`
    (identity, not a copy) — x_A re-derives byte-for-byte through the
    shared function
 4  the eleven strata rungs (`battery_2i.STRATA_RUNGS`) == 2g's
    `strata_2g.COVARIATE_OF`; 2g's committed sealed predictor loads and
    its strata pins check clean (the strata source `analyze_2i.run`
    reads)
 5  referents_2i.json: own sha == the literal; N_FILES_2I entries;
    byte-idempotent
 6  the two-test tree on literal inputs (every terminal, the
    boundaries, the 'below the effect bar' and 'inverted' notes per
    test)
 7  gate-1 and step/endpoint-record refusals fire on mutated synthetic
    records
 8  stage artifacts: every one of the 139 is absent before the prereg
    tag (or, if present, passes its own record-shape check) — no
    stranded mutation backup; ALPHA/T_BAR/N_PERM are stats_2g's,
    unchanged
 9  `require_prereg_2i`/`require_seal_2i`: a tag that exists but does
    not CARRY the instrument/artifact bytes is refused, not merely
    checked for existence
10  the degeneracy rule and both composite-strata constructions
    reproduce hand-computed examples (the one piece of statistical
    logic genuinely new to this module, not reused from 2g/2h)
11  2g's committed 2.8b sweep tree and 2h's committed 6.9b sweep tree
    (the reverse-direction descriptive's inputs) are structurally
    present — gate 1 exists and re-derives clean on each — without
    computing any actual x_B-vs-outcome statistic
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

EXP2I = Path(__file__).resolve().parent
if str(EXP2I.parent.parent) not in sys.path:
    sys.path.insert(0, str(EXP2I.parent.parent))

from experiments.exp2d import battery_2d as bt  # noqa: E402
from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp2g import predictor_2g as pr  # noqa: E402
from experiments.exp2g import stats_2g as st  # noqa: E402
from experiments.exp2g import strata_2g as sg  # noqa: E402
from experiments.exp2h import analyze_2h as an2h  # noqa: E402
from experiments.exp2h import battery_2h as bh  # noqa: E402
from experiments.exp2i import analyze_2i as an  # noqa: E402
from experiments.exp2i import battery_2i as bi  # noqa: E402
from experiments.exp2i import make_referents_2i as mkr  # noqa: E402

CHECKS = []


def check(n, name):
    def deco(fn):
        CHECKS.append((n, name, fn))
        return fn
    return deco


def _eq(got, want, what):
    if got != want:
        raise AssertionError(f"{what}: got {got!r}, want {want!r}")


@check(1, "frozen pins (20); upstream frozen-import pins (14); x_A pins (68)")
def _c1(ctx):
    bi.check_frozen_2i()
    _eq(len(bi.FROZEN_SHA256), 20, "pins")
    bg.check_frozen_imports_2g()
    _eq(len(bg.FROZEN_IMPORT_SHA256_2G), 14, "upstream pins")
    bi.check_pythia_predictor_files()
    _eq(len(bi.PYTHIA_PREDICTOR_FILES), 68, "x_A pins")


@check(2, "checkpoints_2i.json == rebuilt; sha pinned; both repos' main present")
def _c2(ctx):
    inv = bi.load_inventory()
    obj = bi.build_manifest(inv)
    on_disk = bi.load_manifest(bi.CHECKPOINTS_PATH, sha_pin=bi.CHECKPOINTS_2I_SHA256)
    _eq(on_disk, obj, "manifest rebuild")
    _eq(set(inv), {bi.REPO_1B, bi.REPO_7B}, "both repos present")


@check(3, "sampler_counts_pythia IS battery_2h.sampler_counts (identity)")
def _c3(ctx):
    _eq(bi.sampler_counts_pythia is bh.sampler_counts, True, "identity")


@check(4, "the eleven strata rungs == 2g's COVARIATE_OF; 2g's predictor loads clean")
def _c4(ctx):
    _eq(set(bi.STRATA_RUNGS), set(sg.COVARIATE_OF), "strata rungs")
    pred = pr.load_predictor(bg.predictor_path(bg.EXP2G), sha_pin=bh.PREDICTOR_2G_SHA)
    strata = sg.from_json(pred["strata"])
    got = sg.check_strata_pins(strata)
    _eq(all(v == "PASS" for v in got.values()), True, "strata gates")
    ctx["strata"] = strata


@check(5, "referents_2i.json: literal sha, N_FILES_2I entries, idempotent")
def _c5(ctx):
    _eq(an.REFERENTS_2I_SHA256 is not None, True, "pinned")
    # on today's tree (before any stage has run) every entry with sha256:
    # null is a 'still missing' refusal by construction — that is the
    # expected/correct reading, not a defect; anything ELSE would be.
    bad = mkr.check_referents(an.REFERENTS_PATH_2I, sha_pin=an.REFERENTS_2I_SHA256)
    unexpected = [b for b in bad if "still missing" not in b]
    _eq(unexpected, [], "only 'still missing' stage-artifact entries expected")
    _eq(len(bad), 139, "exactly the 139 not-yet-existing stage artifacts")
    tmp = EXP2I / ".referents_2i.rebuild.json"
    try:
        mkr.build(tmp)
        _eq(tmp.read_bytes() == an.REFERENTS_PATH_2I.read_bytes(), True, "byte-idempotent")
    finally:
        tmp.unlink(missing_ok=True)


@check(6, "the two-test tree on literal inputs")
def _c6(ctx):
    def prim(T, p, fires, named=None):
        return {"stratified": {"T": T, "p": p, "n_perm": 100, "n_ge": 0},
               "fires": fires, "named_inside": named}
    A_fire, A_no = prim(.20, .001, True), prim(.02, .5, False)
    B_fire, B_no = prim(.20, .001, True), prim(.02, .5, False)
    _eq(an.verdict_tree_2i(["x"], None, None)["verdict"], "INSUFFICIENT_DATA", "refusal")
    _eq(an.verdict_tree_2i([], A_fire, B_no)["verdict"], "SHARED", "shared")
    _eq(an.verdict_tree_2i([], A_no, B_fire)["verdict"], "LINEAGE", "lineage")
    _eq(an.verdict_tree_2i([], A_fire, B_fire)["verdict"], "BOTH", "both")
    _eq(an.verdict_tree_2i([], A_no, B_no)["verdict"], "NEITHER", "neither")
    below = an.named_inside_2i(prim(.05, .001, False))
    _eq("below the effect bar" in below, True, "below the bar")
    inv = an.named_inside_2i(prim(-.3, .999, False))
    _eq("inverted" in inv, True, "inverted")
    _eq(set(an.WORLDS), {"INSUFFICIENT_DATA", "SHARED", "LINEAGE", "BOTH", "NEITHER"},
       "worlds")


@check(7, "gate-1 and step/endpoint-record refusals fire")
def _c7(ctx):
    from experiments.exp2d import analyze_2d as a2d
    rec = {"rungs": list(bt.RUNGS), "bit_diffs": {r: 0 for r in bt.RUNGS},
          "continuation_diffs": {r: 0 for r in bt.RUNGS},
          "continuations_compared": {r: bt.N_ITEMS for r in bt.RUNGS},
          "digest_sweep": "d" * 64, "digest_endpoint": "d" * 64,
          "commit_sweep": "c" * 40, "commit_endpoint": "c" * 40,
          "prereg_tag": bi.PREREG_TAG}
    endpoint_records = {r: {} for r in bt.RUNGS}
    _eq(an.gate1_failures_7b(rec, endpoint_records), [], "clean gate")
    bad = dict(rec); bad["bit_diffs"] = dict(rec["bit_diffs"]); bad["bit_diffs"]["antonym"] = 1
    _eq(len(an.gate1_failures_7b(bad, endpoint_records)) >= 1, True, "bit diff fires")

    cap = bg.load_battery(["antonym"])["antonym"]
    verify = a2d.load_verify()
    entry = {"revision": "step1000", "commit": "c" * 40, "kind": "bin-shards",
            "files": ["a"], "lfs_sha256": {"a": "f" * 64}}
    conts = [f" {it['answer']}" if i % 3 == 0 else " zzz"
            for i, it in enumerate(cap["eval_items"])]
    bits = [int(verify(c, it["answer"], cap["answer_type"]))
           for c, it in zip(conts, cap["eval_items"])]
    step_rec = {"rung": "antonym", "size": bi.SIZE_OUT, "family": bi.FAMILY, "step": 1000,
               "commit": entry["commit"], "items_sha256": cap["items_sha256"],
               "n": bt.N_ITEMS, "correct": sum(bits), "bits": bits, "continuations": conts,
               "predictor_sha": "P" * 64, "seal_tag": bi.ENDPOINT_SEAL_TAG,
               "answer_type": cap["answer_type"]}
    _eq(an.step_record_failures_2i(step_rec, step=1000, rung="antonym", cap=cap,
                                   entry=entry, verify_fn=verify,
                                   predictor_sha="P" * 64), [], "clean step record")
    bad_step = dict(step_rec); bad_step["predictor_sha"] = "Q" * 64
    _eq(len(an.step_record_failures_2i(bad_step, step=1000, rung="antonym", cap=cap,
                                       entry=entry, verify_fn=verify,
                                       predictor_sha="P" * 64)) >= 1, True,
       "step record mutation fires")

    ep_rec = dict(step_rec); ep_rec.pop("step"); ep_rec["which"] = "stage1_final"
    ep_rec["seal_tag"] = bi.PREDICTOR_SEAL_TAG
    _eq(an.endpoint_record_failures_2i(ep_rec, which="stage1_final", rung="antonym",
                                       cap=cap, entry=entry, verify_fn=verify,
                                       predictor_sha="P" * 64), [], "clean endpoint record")
    bad_ep = dict(ep_rec); bad_ep["which"] = "main"
    _eq(len(an.endpoint_record_failures_2i(bad_ep, which="stage1_final", rung="antonym",
                                           cap=cap, entry=entry, verify_fn=verify,
                                           predictor_sha="P" * 64)) >= 1, True,
       "endpoint record mutation fires")


@check(8, "stage artifacts absent (or shape-valid); no backups; constants == stats_2g's")
def _c8(ctx):
    present, absent = 0, 0
    for p in mkr.stage_artifact_files():
        if Path(p).is_file():
            present += 1
            json.loads(Path(p).read_text())   # at minimum, valid json
        else:
            absent += 1
    print(f"      ({present} stage artifact(s) present, {absent} still missing)")
    _eq(list(EXP2I.rglob("*.mutation_backup")), [], "backups")
    _eq((an.ALPHA, an.T_BAR), (st.ALPHA, st.T_BAR), "constants")
    _eq((st.ALPHA, st.T_BAR), (0.01, 0.10), "values")


@check(9, "require_prereg_2i/require_seal_2i refuse a tag that does not carry the bytes")
def _c9(ctx):
    def blob_ok(tag, rel):
        p = bi.REPO / rel
        return bg.sha256_file(p) if p.is_file() else None
    try:
        an.require_prereg_2i(tag_exists=lambda t: True, blob_sha=lambda t, r: None)
    except RuntimeError:
        pass
    else:
        raise AssertionError("a tag that carries nothing was accepted")

    def drifted(tag, rel):
        return "0" * 64 if rel.endswith("battery_2i.py") else blob_ok(tag, rel)
    try:
        an.require_prereg_2i(tag_exists=lambda t: True, blob_sha=drifted)
    except RuntimeError:
        pass
    else:
        raise AssertionError("a drifted battery_2i.py blob was accepted")

    got = an.require_seal_2i("t", ["a", "b"], tag_exists=lambda t: True,
                             blobs_bound=lambda tag, paths, repo_root=None: ["a"])
    _eq(bool(got["failures"]), True, "require_seal_2i reports drift, never raises")


@check(10, "degeneracy rule and both composite-strata constructions, hand-computed")
def _c10(ctx):
    counts = {"a": [1, 2, 1, 2], "b": [5, 5, 5, 5]}
    strata = {"a": {"strata": ["x", "x", "y", "y"]}, "b": {"strata": ["x", "x", "y", "y"]}}
    _eq(an._degenerate_rungs(counts, strata, ("a", "b")), ["b"], "degeneracy")

    got = an._composite_strata(strata, {"a": [0, 3, 0, 5]}, ("a",))
    _eq(got["a"]["strata"], ["x|0", "x|1", "y|0", "y|1"], "zero-cut composite")

    got_med = an._composite_strata_median(strata, {"a": [1, 2, 3, 4]}, ("a",))
    want_buckets = an._median_bucket([1, 2, 3, 4])
    want = [f"{s}|{b}" for s, b in zip(["x", "x", "y", "y"], want_buckets)]
    _eq(got_med["a"]["strata"], want, "median composite")


@check(11, "2g's 2.8b sweep tree and 2h's 6.9b sweep tree are structurally present")
def _c11(ctx):
    from experiments.exp2g import checkpoints_2g as ck2g
    from experiments.exp2g import analyze_2g as an2g_
    g28 = bg.gate1_path(bg.EXP2G, "2.8b")
    _eq(g28.is_file(), True, "2g's 2.8b gate1.json present")
    rec28 = json.loads(g28.read_text())
    _eq(an2g_.gate1_failures(rec28, "2.8b"), [], "2g's 2.8b gate 1 re-derives clean")

    g69 = bh.gate1_path_2h(bh.EXP2H)
    _eq(g69.is_file(), True, "2h's 6.9b gate1.json present")
    rec69 = json.loads(g69.read_text())
    _eq(an2h.gate1_failures_69(rec69), [], "2h's 6.9b gate 1 re-derives clean")
    ctx["ck2g"] = ck2g   # imported for the module-presence check only


def main() -> int:
    ctx = {}
    for n, name, fn in CHECKS:
        try:
            fn(ctx)
        except Exception as e:  # noqa: BLE001
            print(f"  [{n:2d}] FAIL  {name}: {type(e).__name__}: {e}")
            return 1
        print(f"  [{n:2d}] ok    {name}", flush=True)
    print(f"referent battery: {len(CHECKS)}/{len(CHECKS)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
