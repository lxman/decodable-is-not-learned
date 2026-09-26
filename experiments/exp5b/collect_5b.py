# experiments/exp5b/collect_5b.py
"""The Exp 5b per-unit pipeline (design §3.1, §3.6 gate 1): Experiment 5's
unit writer verbatim into 5b's tree, then 5b's attestation `_unit_5b.json`
written LAST, carrying — on the twelve re-read units — the comparison
against Experiment 5's committed unit of the same (size, step). A tensor
digest that differs from the committed one is the wrong network: the
size halts (design §7 stage 2). Count and loss tolerances are the
analyzer's; the runner records them."""
from __future__ import annotations

import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

EXP5B = Path(__file__).resolve().parent
REPO = EXP5B.parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp5 import _threads_5  # noqa: E402,F401
from experiments.exp5 import battery_5 as b5  # noqa: E402
from experiments.exp5 import collect_5 as c5  # noqa: E402
from experiments.exp5b import battery_5b as b5b  # noqa: E402


def _write(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=1))


def reread_compare_5b(root5b, size, step, *, exp5_root) -> dict:
    """The twelve-unit gate 1 (design §3.6): this box's unit against
    Experiment 5's committed unit of the same (size, step)."""
    d_here = b5b.unit_dir_5b(root5b, size, step)
    ck_here = json.loads((d_here / "_checkpoint.json").read_text())
    ck_there = b5b.exp5_unit_record_5b(exp5_root, size, step, "_checkpoint.json")
    ls_here = json.loads((d_here / "_loss.json").read_text())
    ls_there = b5b.exp5_unit_record_5b(exp5_root, size, step, "_loss.json")
    counts_here, counts_there, cont_diffs = {}, {}, {}
    for r in b5.RUNGS:
        rg_here = json.loads((d_here / f"{r}.json").read_text())
        rg_there = b5b.exp5_unit_record_5b(exp5_root, size, step, f"{r}.json")
        counts_here[r], counts_there[r] = int(rg_here["correct"]), int(rg_there["correct"])
        cont_diffs[r] = int(sum(1 for x, y in zip(rg_here["continuations"], rg_there["continuations"]) if x != y))
    diffs = {r: abs(counts_here[r] - counts_there[r]) for r in b5.RUNGS}
    per_doc = int(sum(1 for x, y in zip(ls_here["per_doc_loss"], ls_there["per_doc_loss"]) if x != y))
    loss_delta = abs(float(ls_here["loss"]) - float(ls_there["loss"]))
    tol = b5.tolerance_failures_5(counts_here, counts_there, label=f"gate 1 {size}/step{int(step)}")
    return {"digest_equal": ck_here["digest"] == ck_there["digest"], "digest_here": ck_here["digest"],
            "digest_committed": ck_there["digest"], "loss_here": ls_here["loss"], "loss_committed": ls_there["loss"],
            "loss_delta": loss_delta, "per_doc_diffs": per_doc, "count_abs_diff": diffs,
            "count_abs_diff_sum": int(sum(diffs.values())), "count_abs_diff_max": int(max(diffs.values())),
            "continuation_diffs": cont_diffs, "continuation_diffs_sum": int(sum(cont_diffs.values())),
            "byte_identical": bool(per_doc == 0 and repr(ls_here["loss"]) == repr(ls_there["loss"])
                                   and sum(cont_diffs.values()) == 0 and sum(diffs.values()) == 0),
            "tolerance_failures": tol, "loss_within_tol": loss_delta <= b5b.LOSS_TOL_5B}


def write_unit5b_record_5b(root, size, step, *, why, host, git_sha, reread) -> Path:
    p = b5b.unit5b_record_path_5b(root, size, step)
    _write(p, {"size": size, "step": int(step), "why": why, "reread": reread is not None,
               "reread_record": reread, "prereg_tag": b5b.PREREG_TAG_5B,
               "exp5_closed_tag": b5b.EXP5_CLOSED_TAG_5B, "host_sha256": host["sha256"],
               "git_sha": git_sha, "written_utc": datetime.now(timezone.utc).isoformat()})
    return p


def run_unit_5b(size, step, *, root, exp5_root, why, halt_on_digest=True, **kw) -> dict:
    """One 5b unit: Experiment 5's writer (37 files, `_unit.json` last),
    then `_unit_5b.json` LAST. A directory that is not 5b-complete is
    removed whole first (Review Focus 1: a unit written by Experiment 5's
    writer but killed before the attestation is re-run, never adopted)."""
    if b5b.unit_complete_5b(root, size, step):
        rec = json.loads(b5b.unit5b_record_path_5b(root, size, step).read_text())
        ls = json.loads(b5.loss_record_path_5(root, size, step).read_text())
        return {"action": "reused", "loss": ls["loss"], "finite": b5.loss_is_finite_5(ls), "size": size,
                "step": int(step), "reread": rec.get("reread_record")}
    d = b5b.unit_dir_5b(root, size, step)
    if d.exists():
        shutil.rmtree(d)
    r = c5.run_unit_5(size, step, root=root, why=why, **kw)
    reread = None
    if int(step) in b5b.reread_steps_5b():
        reread = reread_compare_5b(root, size, step, exp5_root=exp5_root)
    write_unit5b_record_5b(root, size, step, why=why, host=kw["host"], git_sha=kw["git_sha"], reread=reread)
    if reread is not None:
        print(f"[5b] {size}/step{int(step)} re-read vs Experiment 5: digest_equal {reread['digest_equal']} "
              f"byte_identical {reread['byte_identical']} |Δℓ| {reread['loss_delta']:.2e} "
              f"Σ|Δcount| {reread['count_abs_diff_sum']} max {reread['count_abs_diff_max']}", flush=True)
        if not reread["digest_equal"] and halt_on_digest:
            hp = b5b.halt_marker_path_5b(root, size)
            hp.parent.mkdir(parents=True, exist_ok=True)
            msg = (f"gate 1: tensor digest at {size}/step{int(step)} ({reread['digest_here'][:12]}) is not "
                   f"Experiment 5's committed ({reread['digest_committed'][:12]}) — the wrong network")
            hp.write_text(msg + "\n")
            print(f"[5b] HALTED: {msg}", flush=True)
            raise SystemExit(2)
    return {**r, "reread": reread}


def gate1_record_5b(root, *, host, git_sha) -> dict:
    """The runner's attestation over every re-read unit present (rewritten
    after every side); the analyzer RE-DERIVES the comparison (F-2's lesson)."""
    per_unit, failures = {}, []
    for size in b5b.small_sides_5b():
        for step in b5b.reread_steps_5b():
            p = b5b.unit5b_record_path_5b(root, size, step)
            if not p.is_file():
                continue
            rec = json.loads(p.read_text())
            rr = rec.get("reread_record") or {}
            per_unit[f"{size}/step{int(step)}"] = rr
            if not rr.get("digest_equal"):
                failures.append(f"{size}/step{int(step)}: digest differs")
            if not rr.get("loss_within_tol"):
                failures.append(f"{size}/step{int(step)}: |Δℓ| {rr.get('loss_delta')} > {b5b.LOSS_TOL_5B}")
            failures += list(rr.get("tolerance_failures") or [])
    rec = {"per_unit": per_unit, "pass": not failures, "failures": failures,
           "tolerance": {"per_rung": b5.GATE1_TOL_PER_RUNG_5, "sum": b5.GATE1_TOL_SUM_5, "loss": b5b.LOSS_TOL_5B},
           "prereg_tag": b5b.PREREG_TAG_5B, "host_sha256": host["sha256"], "git_sha": git_sha}
    _write(b5b.gate1_path_5b(root), rec)
    return rec
