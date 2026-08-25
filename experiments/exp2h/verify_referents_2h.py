# experiments/exp2h/verify_referents_2h.py
"""The Exp 2h referent battery: every referent re-asserted EXECUTABLE
against the committed trees — run at build, re-run cold at the
freeze. It stops short of the verdict and of any model contact.

 1  the 10 frozen-2g pins byte-identical (`battery_2h.check_frozen_2h`);
    the 14 upstream frozen-import pins (`battery_2g.check_frozen_imports_2g`)
    byte-identical too — 2g's own instrument, which 2h's verdict executes
 2  R_69 reproduces from the committed m4 6.9b counts under 2d's bar;
    every m4 6.9b count == the pin
 3  checkpoints_2h.json == rebuilt from the committed inventory; its
    sha == analyze_2h.CHECKPOINTS_2H_SHA256; hub step143000 vs main
 4  `sampler_counts` reproduces `analyze_2g.sampler_counts_1b` exactly
    on every rung of R_28 ∩ R_69
 5  referents_2h.json: own sha == the literal; N_FILES_2H entries;
    byte-idempotent
 6  the tree on literal inputs (every terminal, the boundaries, the
    'below the effect bar' and 'inverted' notes)
 7  gate-1 and step-record refusals fire on mutated synthetic records
 8  stage artifacts: absent before the prereg tag (or, if present,
    pass their pins) — no stranded mutation backup; ALPHA/T_BAR/N_PERM
    are stats_2g's, unchanged
 9  the freeze's three closures: `collect_total` collects every
    exception shape a torn/hand-edited tree presents (F-1); gate 1's
    zero-diff check is anchored to an attested comparison COVERAGE
    (F-2); the prereg tag must CARRY the three instrument modules, not
    merely exist (F-3)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

EXP2H = Path(__file__).resolve().parent
if str(EXP2H.parent.parent) not in sys.path:
    sys.path.insert(0, str(EXP2H.parent.parent))

from experiments.exp2g import analyze_2g as an2g  # noqa: E402
from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp2g import stats_2g as st  # noqa: E402
from experiments.exp2h import analyze_2h as an  # noqa: E402
from experiments.exp2h import battery_2h as bh  # noqa: E402
from experiments.exp2h import make_referents_2h as mkh  # noqa: E402

CHECKS = []


def check(n, name):
    def deco(fn):
        CHECKS.append((n, name, fn))
        return fn
    return deco


def _eq(got, want, what):
    if got != want:
        raise AssertionError(f"{what}: got {got!r}, want {want!r}")


@check(1, "frozen-2g pins (10); upstream frozen-import pins (14)")
def _c1(ctx):
    bh.check_frozen_2h()
    _eq(len(bh.FROZEN_2G_SHA256), 10, "pins")
    bg.check_frozen_imports_2g()
    _eq(len(bg.FROZEN_IMPORT_SHA256_2G), 14, "upstream pins")


@check(2, "R_69 from m4 6.9b counts + 2d's bar; m4 pins")
def _c2(ctx):
    ctx["floors"] = bg.load_floors()
    _eq(bh.check_rung_set_69(ctx["floors"]), tuple(bh.R_69), "rung set")
    _eq(bh.load_m4_counts_69(), bh.FINAL_COUNT_PIN_69, "m4 6.9b counts")


@check(3, "checkpoints_2h.json == rebuilt; sha pinned; hub step143000")
def _c3(ctx):
    inv = bh.load_inventory_69()
    obj = bh.build_manifest_69(inv)
    on_disk = bh.load_manifest_69(bh.CHECKPOINTS_PATH_69, sha_pin=an.CHECKPOINTS_2H_SHA256)
    _eq(on_disk, obj, "manifest rebuild")
    _eq(obj["hub_step143000"]["signature_equals_main"], True, "6.9b hub final")
    _eq(obj["final_duplicates"], [], "kind-specific signature — see PROGRESS.md's "
       "Task 1 entry (\"Discrepancy against the plan, disclosed rather than bent\")")


@check(4, "sampler_counts reproduces analyze_2g.sampler_counts_1b on the overlap")
def _c4(ctx):
    from experiments.exp2d import analyze_2d as a2d
    from experiments.exp2d import battery_2d as bt
    overlap = tuple(sorted(set(bg.R_28) & set(bh.R_69)))
    battery = bt.load_battery()
    verify_fn = a2d.load_verify()
    ref = an2g.sampler_counts_1b(bg.EXP2D, battery, verify_fn, overlap)
    got = bh.sampler_counts("1b", overlap)
    for r in overlap:
        _eq(got[r], ref[r], f"sampler_counts/{r}")


@check(5, "referents_2h.json: literal sha, N_FILES_2H entries, idempotent")
def _c5(ctx):
    _eq(an.REFERENTS_2H_SHA256 is not None, True, "pinned")
    _eq(mkh.check_referents(an.REFERENTS_PATH_2H, sha_pin=an.REFERENTS_2H_SHA256), [],
       "manifest")
    tmp = EXP2H / ".referents_2h.rebuild.json"
    try:
        mkh.build(tmp)
        _eq(tmp.read_bytes() == an.REFERENTS_PATH_2H.read_bytes(), True, "byte-idempotent")
    finally:
        tmp.unlink(missing_ok=True)


@check(6, "the tree on literal inputs")
def _c6(ctx):
    def prim(T, p):
        return {"stratified": {"T": T, "p": p, "n_perm": 100, "n_ge": 0}}
    _eq(an.verdict_tree_2h(["x"], None)["verdict"], "INSUFFICIENT_DATA", "refusal")
    _eq(an.verdict_tree_2h([], prim(.20, .001))["verdict"], "CONFIRMED", "confirmed")
    _eq(an.verdict_tree_2h([], prim(.02, .5))["verdict"], "NOT-CONFIRMED", "not-confirmed")
    v = an.verdict_tree_2h([], prim(.05, .001))
    _eq(v["verdict"] == "NOT-CONFIRMED" and "below the effect bar" in v["reason"], True,
       "below the bar")
    v = an.verdict_tree_2h([], prim(-.3, .999))
    _eq(v["verdict"] == "NOT-CONFIRMED" and "inverted" in v["reason"], True, "inverted")
    _eq(an.verdict_tree_2h([], prim(.10, .0099))["verdict"], "CONFIRMED", "boundary in")
    _eq(an.verdict_tree_2h([], prim(.10, .01))["verdict"], "NOT-CONFIRMED", "boundary out")
    _eq(set(an.WORLDS), {"INSUFFICIENT_DATA", "CONFIRMED", "NOT-CONFIRMED"}, "worlds")


@check(7, "gate-1 and step-record refusals fire")
def _c7(ctx):
    from experiments.exp2d import battery_2d as bt
    rec = {"size": "6.9b", "rungs": list(bt.RUNGS),
           "counts_2c_path": dict(bh.FINAL_COUNT_PIN_69), "digest_2c_path": "a",
           "digest_2h_path": "a", "continuation_diffs_2h_path": {r: 0 for r in bt.RUNGS},
           "continuations_compared_2h_path": {r: bt.N_ITEMS for r in bt.RUNGS},
           "model_sha": an2g.pythia_sha("6.9b"), "prereg_tag": bh.PREREG_TAG_2H}
    _eq(an.gate1_failures_69(rec), [], "clean gate")
    bad = dict(rec); bad["counts_2c_path"] = dict(rec["counts_2c_path"])
    bad["counts_2c_path"]["antonym"] += 1
    _eq(len(an.gate1_failures_69(bad)) >= 1, True, "count diff fires")
    bad2 = dict(rec); bad2["prereg_tag"] = "wrong-tag"
    _eq(len(an.gate1_failures_69(bad2)) >= 1, True, "tag mismatch fires")

    # step-record refusals: an2g.step_record_failures, as load_sweep_69 uses
    # it (M-2: check 7's title covers both gate-1 AND step-record refusals,
    # but only gate-1 was exercised — this closes the gap)
    from experiments.exp2d import analyze_2d as a2d
    cap = bg.load_battery(["antonym"])["antonym"]
    verify = a2d.load_verify()
    entry = {"revision": "step1000", "commit": "c" * 40, "kind": "bin",
             "files": ["pytorch_model.bin"], "lfs_sha256": {"pytorch_model.bin": "f" * 64}}
    conts = [f" {it['answer']}" if i % 3 == 0 else " zzz"
            for i, it in enumerate(cap["eval_items"])]
    bits = [int(verify(c, it["answer"], cap["answer_type"]))
           for c, it in zip(conts, cap["eval_items"])]
    step_rec = {"rung": "antonym", "size": "6.9b", "step": 1000,
               "revision": entry["revision"], "commit": entry["commit"],
               "items_sha256": cap["items_sha256"], "n": bt.N_ITEMS,
               "correct": sum(bits), "bits": bits, "continuations": conts,
               "predictor_sha": bh.PREDICTOR_2G_SHA, "seal_tag": bg.SEAL_TAG,
               "answer_type": cap["answer_type"]}
    _eq(an2g.step_record_failures(step_rec, size="6.9b", step=1000, rung="antonym",
                                  cap=cap, entry=entry, verify_fn=verify,
                                  seal_sha=bh.PREDICTOR_2G_SHA), [], "clean step record")
    bad_step = dict(step_rec); bad_step["predictor_sha"] = "t" * 64
    _eq(len(an2g.step_record_failures(bad_step, size="6.9b", step=1000, rung="antonym",
                                      cap=cap, entry=entry, verify_fn=verify,
                                      seal_sha=bh.PREDICTOR_2G_SHA)) >= 1, True,
       "step record mutation fires")


@check(8, "stage artifacts absent (or passing); no backups; constants == stats_2g's")
def _c8(ctx):
    g = bh.gate1_path_2h(EXP2H)
    if g.is_file():
        _eq(an.gate1_failures_69(json.loads(g.read_text())), [], "gate 1 on disk")
        print("      (gate 1 record present and passing)")
    else:
        print("      (no sweep yet — as expected before the prereg tag)")
    _eq(list(EXP2H.rglob("*.mutation_backup")), [], "backups")
    _eq((an.ALPHA, an.T_BAR), (st.ALPHA, st.T_BAR), "constants")
    _eq((st.ALPHA, st.T_BAR), (0.01, 0.10), "values")


@check(9, "the freeze's closures: refusal surface, gate-1 coverage, tag-bound instrument")
def _c9(ctx):
    from experiments.exp2d import battery_2d as bt
    # F-1: every shape a torn / hand-edited / directory-shaped tree can
    # present is a COLLECTED failure, not an exception out of run()
    for exc in (ValueError, KeyError, RuntimeError, TypeError, AttributeError,
                OSError, FileNotFoundError, IsADirectoryError, json.JSONDecodeError):
        def boom(e=exc):
            if e is json.JSONDecodeError:
                json.loads("{")
            raise e("x") if e is not IsADirectoryError else e(21, "Is a directory", "/p")
        val, f = an.collect_total(boom, "probe")
        _eq((val, len(f)), (None, 1), f"collect_total does not collect {exc.__name__}")
    _eq(an.collect_total(lambda: 7, "ok"), (7, []), "collect_total passes a value through")
    # F-2: the gate-1 zero-diff check is anchored to an attested coverage
    rec = {"size": "6.9b", "rungs": list(bt.RUNGS),
           "counts_2c_path": dict(bh.FINAL_COUNT_PIN_69), "digest_2c_path": "a",
           "digest_2h_path": "a", "continuation_diffs_2h_path": {r: 0 for r in bt.RUNGS},
           "continuations_compared_2h_path": {r: bt.N_ITEMS for r in bt.RUNGS},
           "model_sha": an2g.pythia_sha("6.9b"), "prereg_tag": bh.PREREG_TAG_2H}
    _eq(an.gate1_failures_69(rec), [], "coverage-complete gate")
    short = dict(rec)
    short["continuations_compared_2h_path"] = {**rec["continuations_compared_2h_path"],
                                               "antonym": 0}
    _eq(any("pairs compared" in f for f in an.gate1_failures_69(short)), True,
       "truncated comparison refused")
    # F-3: the tag has to CARRY the instrument, not merely exist
    _eq(len(an.INSTRUMENT_BLOBS_2H), 3, "instrument blobs")
    for rel in an.INSTRUMENT_BLOBS_2H:
        _eq((bg.REPO / rel).is_file(), True, f"{rel} present")
    ok = an.require_prereg_2h(tag_exists=lambda t: True,
                              blob_sha=lambda tag, rel: bg.sha256_file(bg.REPO / rel))
    _eq(sorted(ok["instrument_blobs"]), sorted(an.INSTRUMENT_BLOBS_2H), "blob record")
    for bad in (lambda tag, rel: None, lambda tag, rel: "0" * 64):
        try:
            an.require_prereg_2h(tag_exists=lambda t: True, blob_sha=bad)
        except RuntimeError:
            continue
        raise AssertionError("a tag that does not carry the instrument was accepted")


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
