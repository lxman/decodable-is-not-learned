# experiments/exp5b/verify_referents_5b.py
"""The Exp 5b referent battery (Task 6 brief's 12 items; Experiment 5's own
`verify_referents_5.py` shape): every referent re-asserted EXECUTABLE
against the committed trees — run at the build, re-run cold at the freeze
and after every stage. Items 9, 10 and 12 SKIP before the power record is
written / before any 5b unit exists. Committed bytes throughout, plus one
in-process re-derivation of Experiment 5's OWN cold battery (item 5) and
34 seeded synthetic identity checks (item 8) — no model contact.

 1  frozen pins byte-identical (`battery_5b.check_frozen_5b`) and the
    import pins (`check_imports_5b` after importing every 5b module and
    stage tool)
 2  the tags exist: exp5-closed, exp5-preregistered, exp5-targets-sealed,
    exp2c-closed, exp2d-closed
 3  the exp5-closed binding (`require_exp5_closed_5b` against real git):
    the thirteen blobs equal disk; verdict.json at
    `EXP5_VERDICT_SHA256_5B`
 4  `referents_5b.json` at its pin: `check_referents_5b` returns zero
    failures
 5  Experiment 5's own cold battery passes on Experiment 5's tree
    (`verify_referents_5.main() == 0`, items 11 and 13 live — the closed
    record still reproduces)
 6  the literal verdict pin equals the committed verdict.json's fields
    (`exp5_verdict_pin_failures_5b` empty)
 7  the window steps: every small side's manifest entries for
    140000-143000 present and unexcluded; the kinds printed
    (safetensors-single/-shards, bin, bin-shards — design §3.1)
 8  stats_5b's identities on SYNTHETIC cells (never the committed
    table): a noiseless small side gives M = P/√2 on 200 random cells; a
    between-size offset added to every large-side read leaves M
    unchanged
 9  the power record, WHEN PRESENT: `prereg_tag`/`n_sim`/`seed`/
    `exp5_closed_tag` measured; reproduces byte-for-byte under
    `compute_5b` from `load_cells5_live_5b(EXP5)`; `structure_sha256`
    equal; SKIP before it is written
10  gate 1 re-derived, WHEN 5b units are present (any side directory
    under results/units): zero failures over the re-read units present;
    SKIP otherwise
11  the referent manifest's file count: live `referent_files_5b()` ==
    `N_FILES_5B` == the committed `referents_5b.json`'s own `n_files`
12  every 5b unit present carries a valid `_unit_5b.json` (contract) and
    the host record passes gate 0; SKIP when no unit exists

Run: `PYTHONDONTWRITEBYTECODE=1 ~/emergence-lab/.venv/bin/python -m
experiments.exp5b.verify_referents_5b` from the repo root."""
from __future__ import annotations

import io
import json
import random
import sys
from contextlib import redirect_stdout
from pathlib import Path

EXP5B = Path(__file__).resolve().parent
EXPERIMENTS = EXP5B.parent
REPO = EXPERIMENTS.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp5 import _threads_5  # noqa: E402,F401
from experiments.exp2d import analyze_2d as a2d  # noqa: E402
from experiments.exp2d import battery_2d as bt  # noqa: E402
from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp2g import predictor_2g as pr  # noqa: E402
from experiments.exp5 import battery_5 as b5  # noqa: E402
from experiments.exp5 import slice_5 as sl5  # noqa: E402
from experiments.exp5 import stats_5 as ss  # noqa: E402
from experiments.exp5 import verify_referents_5 as vr5  # noqa: E402
from experiments.exp5b import analyze_5b as an  # noqa: E402
from experiments.exp5b import battery_5b as b5b  # noqa: E402
from experiments.exp5b import make_referents_5b as mkr  # noqa: E402
from experiments.exp5b import power_5b as pw5b  # noqa: E402
from experiments.exp5b import stats_5b as st  # noqa: E402

CHECKS = []
CLOSED_TAGS_5B = ("exp5-closed", "exp5-preregistered", "exp5-targets-sealed",
                  "exp2c-closed", "exp2d-closed")


def check(n, name):
    def deco(fn_):
        CHECKS.append((n, name, fn_))
        return fn_
    return deco


def _pull_in_every_5b_module() -> None:
    import experiments.exp5b.battery_5b            # noqa: F401
    import experiments.exp5b.stats_5b               # noqa: F401
    import experiments.exp5b.power_5b               # noqa: F401
    import experiments.exp5b.collect_5b             # noqa: F401
    import experiments.exp5b.analyze_5b             # noqa: F401
    import experiments.exp5b.make_referents_5b      # noqa: F401
    import experiments.exp5b.verify_referents_5b    # noqa: F401
    import experiments.exp5b.run.preflight_5b       # noqa: F401
    import experiments.exp5b.run.units_5b           # noqa: F401


@check(1, "frozen pins byte-identical; the import pins after importing every 5b module and stage tool")
def _c1(ctx):
    b5b.check_frozen_5b()
    _pull_in_every_5b_module()
    b5b.check_imports_5b()
    print(f"       {len(b5b.FROZEN_SHA256_5B)} frozen + {len(b5b.IMPORTED_SHA256_5B)} imported pin(s) "
         f"verified", flush=True)


@check(2, "the tags exist: exp5-closed, exp5-preregistered, exp5-targets-sealed, exp2c-closed, exp2d-closed")
def _c2(ctx):
    missing = [t for t in CLOSED_TAGS_5B if not pr.git_tag_exists(t)]
    if missing:
        raise AssertionError(f"missing tags: {missing}")


@check(3, "the exp5-closed binding: the thirteen blobs equal disk; verdict.json at its pin")
def _c3(ctx):
    closed = b5b.require_exp5_closed_5b()
    if len(closed["blobs"]) != len(b5.INSTRUMENT_BLOBS_5):
        raise AssertionError(f"{len(closed['blobs'])} blobs bound, expected {len(b5.INSTRUMENT_BLOBS_5)}")
    if closed["verdict_sha256"] != b5b.EXP5_VERDICT_SHA256_5B:
        raise AssertionError(f"verdict.json hashes to {closed['verdict_sha256']}, pinned "
                             f"{b5b.EXP5_VERDICT_SHA256_5B}")
    ctx["closed"] = closed


@check(4, "referents_5b.json at its pin: check_referents_5b returns zero failures")
def _c4(ctx):
    if an.REFERENTS_5B_SHA256 is None:
        return "SKIP (REFERENTS_5B_SHA256 not pinned)"
    bad = mkr.check_referents_5b(EXP5B / "referents_5b.json", sha_pin=an.REFERENTS_5B_SHA256)
    if bad:
        raise AssertionError(f"{len(bad)} referent failure(s): {bad[:5]}")


@check(5, "Experiment 5's own cold battery passes (verify_referents_5.main() == 0, items 11/13 land ok)")
def _c5(ctx):
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = vr5.main()
    out = buf.getvalue()
    if rc != 0:
        raise AssertionError(f"verify_referents_5.main() returned {rc}:\n{out[-2000:]}")
    for n in (11, 13):
        if f"[{n:2d}] ok" not in out:
            raise AssertionError(f"item {n} of Experiment 5's own battery did not land 'ok' "
                                 f"(SKIP or FAIL — the closed record should still reproduce): "
                                 f"{out[-2000:]}")
    print("       " + out.strip().splitlines()[-1], flush=True)


@check(6, "the literal verdict pin equals the committed verdict.json's fields")
def _c6(ctx):
    v5 = json.loads((b5b.EXP5 / "results" / "verdict.json").read_text())
    bad = b5b.exp5_verdict_pin_failures_5b(v5)
    if bad:
        raise AssertionError(bad)


@check(7, "the window steps: every small side's manifest entries for 140000-143000 present and "
         "unexcluded; the kinds printed")
def _c7(ctx):
    m = ctx.get("manifest") or b5.load_manifest_5(sha_pin=b5.CHECKPOINTS_SHA256_5)
    steps = (b5.FINAL_STEP_5,) + tuple(b5b.WINDOW_STEPS_5B)
    kinds = set()
    for size in b5b.small_sides_5b():
        entries, excluded = m[size]["entries"], m[size]["excluded"]
        for step in steps:
            e = entries.get(str(step))
            if e is None:
                raise AssertionError(f"{size}/step{step}: no manifest entry")
            if str(step) in excluded:
                raise AssertionError(f"{size}/step{step}: excluded ({excluded[str(step)]})")
            kinds.add(e["kind"])
    ctx["manifest"] = m
    print(f"       kinds present over the window steps: {sorted(kinds)}", flush=True)


@check(8, "stats_5b's identities on synthetic cells: M = P/sqrt2 on a noiseless small side; a "
         "between-size offset added to every large-side read leaves M unchanged")
def _c8(ctx):
    rng = random.Random(20260925)
    n_checked = 0
    for _ in range(200):
        f = rng.randint(50, 450)
        lo, hi = rng.randint(50, 450), rng.randint(50, 450)
        bm = [rng.randint(50, 450) for _ in range(2)]
        bp = [rng.randint(50, 450) for _ in range(2)]
        reads = {"lo": lo, "hi": hi, "a": (lo + hi) / 2, "b_minus": sum(bm) / 2, "b_plus": sum(bp) / 2,
                 "raw": {"lo": lo, "hi": hi, "b_minus": bm, "b_plus": bp}}
        c5 = ss.cell_5(f=f, reads=reads, floor=0.1)
        small = {"f_B": f, "members": {140000: f, 141000: f, 142000: f}}    # noiseless: every member == f_B
        c5b = st.cell_5b(c5, small, 0.1)
        want_M = c5["P"] / b5b.SQRT2_5B
        if c5b["M"] is None or abs(c5b["M"] - want_M) > 1e-9:
            raise AssertionError(f"noiseless-small-side identity failed: M={c5b['M']!r} want {want_M!r}")
        off = rng.uniform(-75.0, 75.0)
        reads2 = dict(reads, a=reads["a"] + off, b_minus=reads["b_minus"] + off,
                      b_plus=reads["b_plus"] + off)
        c5_off = ss.cell_5(f=f, reads=reads2, floor=0.1)
        c5b_off = st.cell_5b(c5_off, small, 0.1)
        if abs(c5b_off["M"] - c5b["M"]) > 1e-9:
            raise AssertionError(f"between-size-offset identity failed: M={c5b_off['M']!r} vs {c5b['M']!r}")
        n_checked += 1
    print(f"       {n_checked} noiseless-small-side + {n_checked} offset-invariance identities, "
         f"all < 1e-9", flush=True)


@check(9, "the power record, WHEN PRESENT: reproduces byte for byte under compute_5b; SKIP before "
         "it is written")
def _c9(ctx):
    p = b5b.power_path_5b(b5b.EXP5B)
    if not p.is_file():
        return "SKIP (results/power_5b.json does not exist yet — before the tag)"
    rec = json.loads(p.read_text())
    if rec.get("prereg_tag") != b5b.PREREG_TAG_5B or rec.get("exp5_closed_tag") != b5b.EXP5_CLOSED_TAG_5B:
        raise AssertionError(f"power record: prereg_tag/exp5_closed_tag {rec.get('prereg_tag')!r}/"
                             f"{rec.get('exp5_closed_tag')!r} mismatch")
    if rec.get("n_sim") != pw5b.N_SIM_5B or rec.get("seed") != pw5b.SEED_5B:
        raise AssertionError(f"power record: n_sim/seed {rec.get('n_sim')}/{rec.get('seed')} != "
                             f"power_5b's {pw5b.N_SIM_5B}/{pw5b.SEED_5B}")
    cells5 = pw5b.load_cells5_live_5b(b5b.EXP5)
    floors = b5.load_floors_5()
    recomputed = pw5b.compute_5b(cells5, floors, n_sim=rec["n_sim"], seed=rec["seed"])
    recomputed["exp5_verdict_sha256"] = rec.get("exp5_verdict_sha256")
    if json.dumps(recomputed, sort_keys=True) != json.dumps(rec, sort_keys=True):
        raise AssertionError("power_5b.json did not reproduce byte for byte")
    print(f"       declaration: {rec['declaration']}", flush=True)


@check(10, "gate 1 re-derived, WHEN 5b units are present: zero failures over the re-read units "
          "present; SKIP otherwise")
def _c10(ctx):
    units_root = b5b.units_root_5b(b5b.EXP5B)
    if not units_root.is_dir() or not any(units_root.iterdir()):
        return "SKIP (no 5b unit exists yet — no campaign has run)"
    manifest = ctx.get("manifest") or b5.load_manifest_5(sha_pin=b5.CHECKPOINTS_SHA256_5)
    battery = bt.load_battery()
    verify_fn = a2d.load_verify()
    host_p = b5b.host_record_path_5b(b5b.EXP5B)
    host = json.loads(host_p.read_text()) if host_p.is_file() else None
    sl = sl5.load_slice_5(sha_pin=b5.SLICE_SHA256_5)
    sides = {}
    for size in b5b.small_sides_5b():
        try:
            sides[size] = an.load_side_5b(b5b.EXP5B, size, manifest=manifest, battery=battery,
                                          verify_fn=verify_fn, host=host, slice_sha=sl["sha256"],
                                          n_scored=sl["meta"]["n_scored"])
        except Exception:  # noqa: BLE001 — an absent/torn side is simply excluded here
            sides[size] = None
    rec, bad = an.gate1_rederive_5b(b5b.EXP5B, b5b.EXP5, sides)
    if bad:
        raise AssertionError(bad[:6])
    print(f"       {rec['n_units']} re-read unit(s) re-derived, zero failures", flush=True)


@check(11, "the referent manifest's file count: live == N_FILES_5B == committed n_files")
def _c11(ctx):
    live = len(mkr.referent_files_5b())
    if live != mkr.N_FILES_5B:
        raise AssertionError(f"live referent_files_5b() count {live} != N_FILES_5B {mkr.N_FILES_5B}")
    committed = json.loads((EXP5B / "referents_5b.json").read_text())
    if committed["n_files"] != mkr.N_FILES_5B:
        raise AssertionError(f"committed referents_5b.json n_files {committed['n_files']} != "
                             f"N_FILES_5B {mkr.N_FILES_5B}")


@check(12, "every 5b unit present carries a valid _unit_5b.json and the host record passes gate 0; "
          "SKIP when no unit exists")
def _c12(ctx):
    units_root = b5b.units_root_5b(b5b.EXP5B)
    if not units_root.is_dir() or not any(units_root.iterdir()):
        return "SKIP (no 5b unit exists yet)"
    host_p = b5b.host_record_path_5b(b5b.EXP5B)
    if not host_p.is_file():
        raise AssertionError("host record missing but a 5b unit exists")
    host = json.loads(host_p.read_text())
    bad = b5.host_record_failures_5(host)
    if bad:
        raise AssertionError(f"host record: {bad}")
    n = 0
    for size in b5b.small_sides_5b():
        d = units_root / size
        if not d.is_dir():
            continue
        for step_dir in sorted(d.iterdir()):
            if not step_dir.is_dir() or not step_dir.name.startswith("step") or \
                    not step_dir.name[4:].isdigit():
                continue
            step = int(step_dir.name[4:])
            p = b5b.unit5b_record_path_5b(b5b.EXP5B, size, step)
            if not p.is_file():
                raise AssertionError(f"{size}/step{step}: no _unit_5b.json")
            rec = json.loads(p.read_text())
            bad = b5b.unit5b_record_failures_5b(rec, size=size, step=step, host=host)
            if bad:
                raise AssertionError(bad[:5])
            n += 1
    print(f"       {n} unit(s), each with a valid _unit_5b.json", flush=True)


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
