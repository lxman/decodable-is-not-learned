# experiments/exp5/verify_referents_5.py
"""The Exp 5 referent battery (Task 6 brief's 13 items; exp4c's/2n's own
`@check` shape): every referent re-asserted EXECUTABLE against the
committed trees — run at the build, re-run cold at the freeze and after
every stage. Items 11 and 13 SKIP before the targets stage / before any
campaign gate record exists; item 7 SKIPs (with the reason printed)
when the Pile-validation file is not in the local cache — it is never
downloaded inside the cold battery. Committed bytes throughout: no
model contact.

 1  frozen pins byte-identical (`battery_5.check_frozen_5`)
 2  the closed tags exist: exp2c-closed, exp2d-closed, exp2g-closed,
    exp2h-closed
 3  `referents_5.json` at its pin: `check_referents_5` returns zero
    failures
 4  the manifest loads at `CHECKPOINTS_SHA256_5`; every size's
    available list ends at 143000 and has no 0; every size's spine is
    nine distinct points; every exclusion carries a reason; 2.8b's
    64000 is excluded
 5  the manifest's entries at 2g's/2h's closed grid steps carry the
    same LFS shas as 2g's/2h's own committed (closed) manifests — the
    Hub-rewrite check
 6  the committed slice loads at `SLICE_SHA256_5` with exactly 2^21
    scored tokens and `SLICE_META_PIN_5`
 7  the slice RE-DERIVES from the pinned file (`slice_file_path_5`'s
    own dataset/revision/file, found through `hf_hub_download(...,
    local_files_only=True)` — SKIP with the reason printed when it is
    not in the local cache; never a download here), `slice_equal_5`
    empty; the tokenizer pins hold (`tokenizer_pins_5`)
 8  the Mac referents load for the five sizes (`mac_final_counts_5`,
    all 34 rungs) and the fifteen interior checkpoints
    (`mac_interior_counts_5`, 2.8b's 7 + 6.9b's 8, all 34 rungs each —
    12b's descriptive steps are NOT part of `gate1_interior_steps_5`
    and so are not counted among these fifteen), PLUS 12b's own six
    `GATE1_DESCRIPTIVE_12B_5` steps at exactly
    `GATE1_DESCRIPTIVE_12B_RUNGS_5` (11 rungs, not 34 — B-6 ruling
    2026-09-22: see PROGRESS.md's Task 6 finding on 12b's committed
    sweep records)
 9  `tolerance_failures_5` on the A100 benchmark's own committed 6.9b
    argmax counts against `FINAL_COUNT_PIN_69` is EMPTY, with max|Δ| 8
    and Σ|Δ| 57 exactly — the known-answer gate for the pinned
    tolerance (`GATE1_BENCH_5`)
10  the search planner: `replay_5` on a synthetic monotone table lands
    adjacent, straddling brackets for 50 random targets; `plan_5` is
    total over 300 random partial tables (the Task 3 property, run
    cold)
11  the power record, WHEN PRESENT (post-targets): reproduces byte for
    byte under `power_5.compute` at its own `n_sim`/`seed`,
    `finals_sha256` equal; SKIP before the targets stage
12  the referent manifest's file count: live `referent_files_5()` ==
    `N_FILES_5` == the committed `referents_5.json`'s own `n_files`
13  gate 1(a)/(b)/(c) records, WHEN PRESENT: `gate1a_failures_5` / the
    re-derived (b) / (c) empty; SKIP otherwise (no campaign has run)

Run: `PYTHONDONTWRITEBYTECODE=1 ~/emergence-lab/.venv/bin/python -m
experiments.exp5.verify_referents_5` from the repo root."""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

EXP5 = Path(__file__).resolve().parent
EXPERIMENTS = EXP5.parent
REPO = EXPERIMENTS.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp5 import _threads_5  # noqa: E402,F401
from experiments.exp2d import battery_2d as bt  # noqa: E402
from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp2g import predictor_2g as pr  # noqa: E402
from experiments.exp2h import battery_2h as bh  # noqa: E402
from experiments.exp5 import analyze_5 as an  # noqa: E402
from experiments.exp5 import battery_5 as b5  # noqa: E402
from experiments.exp5 import make_referents_5 as mkr  # noqa: E402
from experiments.exp5 import power_5 as pw  # noqa: E402
from experiments.exp5 import search_5 as se5  # noqa: E402
from experiments.exp5 import slice_5 as sl5  # noqa: E402

CHECKS = []
CLOSED_TAGS_5 = ("exp2c-closed", "exp2d-closed", "exp2g-closed", "exp2h-closed")


def check(n, name):
    def deco(fn_):
        CHECKS.append((n, name, fn_))
        return fn_
    return deco


@check(1, "frozen pins byte-identical")
def _c1(ctx):
    b5.check_frozen_5()
    print(f"       {len(b5.FROZEN_SHA256_5)} pinned files verified", flush=True)


@check(2, "the closed tags exist: exp2c/2d/2g/2h-closed")
def _c2(ctx):
    missing = [t for t in CLOSED_TAGS_5 if not pr.git_tag_exists(t)]
    if missing:
        raise AssertionError(f"missing tags: {missing}")


@check(3, "referents_5.json at the pin: check_referents_5 returns zero failures")
def _c3(ctx):
    if an.REFERENTS_5_SHA256 is None:
        return "SKIP (REFERENTS_5_SHA256 not pinned)"
    bad = mkr.check_referents_5(EXP5 / "referents_5.json", sha_pin=an.REFERENTS_5_SHA256)
    if bad:
        raise AssertionError(f"{len(bad)} referent failure(s): {bad[:5]}")


@check(4, "the manifest: available ends at 143000/no 0; spine 9 distinct; exclusions carry a "
         "reason; 2.8b's 64000 excluded")
def _c4(ctx):
    m = b5.load_manifest_5(sha_pin=b5.CHECKPOINTS_SHA256_5)
    for size in b5.SIZES_5:
        avail = m[size]["available"]
        if not avail or avail[-1] != b5.FINAL_STEP_5:
            raise AssertionError(f"{size}: available list ends at {avail[-1:]}, not "
                                 f"[{b5.FINAL_STEP_5}]")
        if 0 in avail:
            raise AssertionError(f"{size}: available list carries step 0")
        for step, rec in m[size]["excluded"].items():
            if not rec.get("reason"):
                raise AssertionError(f"{size} excluded step{step}: no reason recorded")
        sp = b5.spine_5(m, size)
        if len(set(sp)) != 9:
            raise AssertionError(f"{size}: spine {sp} is not nine distinct points")
    if "64000" not in m["2.8b"]["excluded"]:
        raise AssertionError("2.8b's step64000 is not excluded")
    ctx["manifest"] = m


@check(5, "the manifest's entries at 2g's/2h's closed grid steps carry the same LFS shas "
         "(Hub-rewrite check)")
def _c5(ctx):
    m = ctx.get("manifest") or b5.load_manifest_5(sha_pin=b5.CHECKPOINTS_SHA256_5)
    old_2g = json.loads((bg.EXP2G / "checkpoints_2g.json").read_text())
    old_2h = json.loads((bh.EXP2H / "checkpoints_2h.json").read_text())
    # `checkpoints_2g.json` is keyed by size at the top ({"2.8b": {...},
    # "12b": {...}}); `checkpoints_2h.json` is flat (one size, no
    # top-level "6.9b" key) — both verified from the files themselves.
    plan = (("2.8b", old_2g["2.8b"], bg.trained_steps("2.8b")),
            ("12b", old_2g["12b"], bg.trained_steps("12b")),
            ("6.9b", old_2h, bh.trained_steps_69()))
    bad, n = [], 0
    for size, old, steps in plan:
        for step in steps:
            new_e = (m[size]["entries"] or {}).get(str(step))
            old_e = (old["entries"] or {}).get(str(step))
            if new_e is None or old_e is None:
                bad.append(f"{size}/step{step}: entry missing (fresh {new_e is not None}, "
                          f"closed {old_e is not None})")
                continue
            if new_e["lfs_sha256"] != old_e["lfs_sha256"]:
                bad.append(f"{size}/step{step}: LFS shas differ from 2g's/2h's closed manifest "
                          f"— possible Hub rewrite")
            n += 1
    if bad:
        raise AssertionError(bad[:5])
    print(f"       {n} closed grid step(s) unchanged on the Hub (2.8b {len(plan[0][2])}, "
         f"12b {len(plan[1][2])}, 6.9b {len(plan[2][2])})", flush=True)


@check(6, "the committed slice loads at SLICE_SHA256_5, 2^21 scored tokens, SLICE_META_PIN_5")
def _c6(ctx):
    sl = sl5.load_slice_5(sha_pin=b5.SLICE_SHA256_5)
    if sl["meta"]["n_scored"] != b5.SLICE_N_SCORED_5:
        raise AssertionError(f"n_scored {sl['meta']['n_scored']} != {b5.SLICE_N_SCORED_5}")
    for k, want in b5.SLICE_META_PIN_5.items():
        if sl["meta"].get(k) != want:
            raise AssertionError(f"meta.{k} = {sl['meta'].get(k)!r} != {want!r}")
    ctx["slice"] = sl


@check(7, "the slice re-derives from the pinned file (SKIP if not cached); slice_equal_5 empty; "
         "tokenizer pins hold")
def _c7(ctx):
    from huggingface_hub import hf_hub_download
    try:
        path = hf_hub_download(b5.SLICE_DATASET_5, b5.SLICE_FILE_5, repo_type="dataset",
                               revision=b5.SLICE_REVISION_5, cache_dir=str(sl5.SLICE_CACHE_5),
                               local_files_only=True)
    except Exception as e:  # noqa: BLE001 — huggingface_hub's own not-cached exception
        return f"SKIP (the pile-val file is not in the local cache: {type(e).__name__}: {e})"
    sl5.verify_slice_file_5(path)
    try:
        tok = sl5.load_slice_tokenizer_5()
    except Exception as e:  # noqa: BLE001
        return f"SKIP (the tokenizer is not cached: {type(e).__name__}: {e})"
    pins = sl5.tokenizer_pins_5(tok)
    tok._pins_5 = pins
    committed = ctx.get("slice") or sl5.load_slice_5(sha_pin=b5.SLICE_SHA256_5)
    rebuilt = sl5.build_slice_5(tok, path)
    diffs = sl5.slice_equal_5(committed, rebuilt)
    if diffs:
        raise AssertionError(f"slice_equal_5 found differences: {diffs}")
    print(f"       re-derived {rebuilt['meta']['n_scored']} scored tokens from {path}", flush=True)


@check(8, "the Mac referents load for the five sizes and the fifteen interior checkpoints, "
         "all 34 rungs, plus 12b's six B-6 descriptive steps at 11 rungs")
def _c8(ctx):
    n_sizes = 0
    for size in b5.SIZES_5:
        ref = b5.mac_final_counts_5(size)
        if ref is None:
            continue
        if set(ref) != set(bt.RUNGS):
            raise AssertionError(f"{size}: mac_final_counts_5 does not cover all 34 rungs")
        n_sizes += 1
    if n_sizes != 5:
        raise AssertionError(f"{n_sizes} sizes carry a Mac final referent, expected 5")
    n_interior = 0
    for size in ("2.8b", "6.9b"):
        for step in b5.gate1_interior_steps_5(size):
            ref = b5.mac_interior_counts_5(size, step)
            if ref is None or set(ref) != set(bt.RUNGS):
                raise AssertionError(f"{size}/step{step}: mac_interior_counts_5 missing or "
                                     f"incomplete")
            n_interior += 1
    if n_interior != 15:
        raise AssertionError(f"{n_interior} interior checkpoints loaded, expected 15 (7 + 8)")
    n_12b = 0
    for step in b5.GATE1_DESCRIPTIVE_12B_5:
        ref = b5.mac_interior_counts_5("12b", step)
        if ref is None or set(ref) != set(b5.GATE1_DESCRIPTIVE_12B_RUNGS_5):
            raise AssertionError(f"12b/step{step}: mac_interior_counts_5 missing or does not "
                                 f"cover exactly GATE1_DESCRIPTIVE_12B_RUNGS_5 (11 rungs)")
        n_12b += 1
    if n_12b != 6:
        raise AssertionError(f"{n_12b} 12b descriptive steps loaded, expected 6")
    print(f"       5 final referents + {n_interior} interior referents (34 rungs each) + "
         f"{n_12b} 12b descriptive steps (11 rungs each)", flush=True)


@check(9, "tolerance_failures_5 on the A100 benchmark's committed 6.9b counts is empty, "
         "max|Δ| 8 Σ|Δ| 57")
def _c9(ctx):
    p = (REPO / "tools" / "vast_bench" / "runs" / "2026-09-20-a100-40gb-vast51754225"
        / "bench_results.json")
    d = json.loads(p.read_text())
    rungs = d["argmax"]["rungs"]
    if set(rungs) != set(bt.RUNGS):
        raise AssertionError("bench_results.json argmax rungs != the 34 RUNGS")
    counts = {r: int(v["correct"]) for r, v in rungs.items()}
    bad = b5.tolerance_failures_5(counts, bh.FINAL_COUNT_PIN_69, label="bench 6.9b")
    if bad:
        raise AssertionError(bad)
    diffs = [abs(counts[r] - bh.FINAL_COUNT_PIN_69[r]) for r in bt.RUNGS]
    max_d, sum_d = max(diffs), sum(diffs)
    want = (b5.GATE1_BENCH_5["max_abs_diff"], b5.GATE1_BENCH_5["sum_abs_diff"])
    if (max_d, sum_d) != want:
        raise AssertionError(f"max|Δ| {max_d} / Σ|Δ| {sum_d} != the pinned {want}")
    print(f"       max|Δ| {max_d}, Σ|Δ| {sum_d} (GATE1_BENCH_5 pins {want[0]}/{want[1]})",
         flush=True)


@check(10, "the search planner: replay_5 lands adjacent straddling brackets (50 targets); "
          "plan_5 is total over 300 partial tables")
def _c10(ctx):
    spine = b5.SPINE_5
    avail = tuple(range(1000, 144000, 1000))

    def curve(step, A=2.0, B=40.0):
        return A + B / (step ** 0.5)
    full = {s: curve(s) for s in avail}
    rng = random.Random(1)
    n_done = 0
    for _ in range(50):
        target = rng.uniform(curve(143000), curve(1000))
        r = se5.replay_5(full, avail, spine, target)
        if r["status"] != "done":
            continue
        lo, hi = r["plan"]["bracket"]
        i_lo, i_hi = avail.index(lo), avail.index(hi)
        if i_hi != i_lo + 1:
            raise AssertionError(f"bracket {[lo, hi]} not adjacent on the available list")
        if not (full[lo] >= target > full[hi]):
            raise AssertionError(f"bracket {[lo, hi]} does not straddle target {target}")
        n_done += 1
    if n_done == 0:
        raise AssertionError("none of the 50 replay_5 targets reached 'done'")
    rng2 = random.Random(2)
    for _ in range(300):
        keep = {s: v for s, v in full.items() if rng2.random() < 0.5}
        target = rng2.uniform(curve(143000), curve(1000))
        p = se5.plan_5(keep, avail, spine, target)
        if p["status"] not in ("need", "dropped", "done"):
            raise AssertionError(f"plan_5 returned an unexpected status {p['status']!r}")
        if p["status"] == "need" and (p["step"] not in avail or p["step"] in keep):
            raise AssertionError(f"plan_5 requested an already-known or off-list step "
                                 f"{p['step']}")
    print(f"       replay_5: {n_done}/50 targets done, brackets adjacent and straddling; "
         f"plan_5: total over 300 partial tables", flush=True)


@check(11, "power_5.json reproduces byte for byte, WHEN PRESENT; SKIP before the targets stage")
def _c11(ctx):
    p = b5.power_path_5(b5.EXP5)
    if not p.is_file():
        return "SKIP (results/power_5.json does not exist yet — before the targets stage)"
    rec = json.loads(p.read_text())
    finals_counts = pw.load_finals_counts_5(b5.EXP5)
    floors = b5.load_floors_5()
    recomputed = pw.compute(finals_counts, floors, n_sim=rec["n_sim"], seed=rec["seed"])
    recomputed["finals_sha256"] = pw.finals_sha256_5(b5.EXP5)
    if json.dumps(recomputed, sort_keys=True) != json.dumps(rec, sort_keys=True):
        raise AssertionError("power_5.json did not reproduce byte for byte")
    print(f"       declaration: {rec['declaration']}", flush=True)


@check(12, "the referent manifest's file count: live == N_FILES_5 == committed n_files")
def _c12(ctx):
    live = len(mkr.referent_files_5())
    if live != mkr.N_FILES_5:
        raise AssertionError(f"live referent_files_5() count {live} != N_FILES_5 {mkr.N_FILES_5}")
    committed = json.loads((EXP5 / "referents_5.json").read_text())
    if committed["n_files"] != mkr.N_FILES_5:
        raise AssertionError(f"committed referents_5.json n_files {committed['n_files']} != "
                             f"N_FILES_5 {mkr.N_FILES_5}")


@check(13, "gate 1(a)/(b)/(c) records, WHEN PRESENT: zero failures; SKIP otherwise")
def _c13(ctx):
    lines, any_present = [], False
    if b5.gate1a_path_5(b5.EXP5).is_file():
        any_present = True
        rec = json.loads(b5.gate1a_path_5(b5.EXP5).read_text())
        bad = an.gate1a_failures_5(rec)
        if bad:
            raise AssertionError(f"gate 1(a): {bad}")
        lines.append("1(a) ok")
    if b5.gate1b_path_5(b5.EXP5).is_file():
        any_present = True
        rec = json.loads(b5.gate1b_path_5(b5.EXP5).read_text())
        bad = an.gate1b_failures_5(b5.EXP5, rec)
        if bad:
            raise AssertionError(f"gate 1(b): {bad}")
        lines.append("1(b) ok")
    for size in ("2.8b", "6.9b"):
        p = b5.gate1c_path_5(b5.EXP5, size)
        if p.is_file():
            any_present = True
            rec = json.loads(p.read_text())
            bad = an.gate1c_failures_5(b5.EXP5, size, rec)
            if bad:
                raise AssertionError(f"gate 1(c) {size}: {bad}")
            lines.append(f"1(c) {size} ok")
    if not any_present:
        return "SKIP (no campaign has run — no gate 1(a)/(b)/(c) record exists yet)"
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
        if isinstance(result, str) and result.startswith("SKIP"):
            reason = result[4:].strip() or "(not yet applicable)"
            print(f"  [{n:2d}] skip  {name} {reason}", flush=True)
        else:
            print(f"  [{n:2d}] ok    {name}", flush=True)
            n_ok += 1
    print(f"referent battery: {n_ok}/{len(CHECKS)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
