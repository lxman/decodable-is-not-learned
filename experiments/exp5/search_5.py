# experiments/exp5/search_5.py
"""The Exp 5 matching search (design §3.2), as ONE pure function that is
TOTAL over every partial loss table: `plan_5` reads the losses scored so
far and returns either the next step to load (`need`), a `dropped` pair
(no spine interval crosses the target), or `done` with the bracket and
the window. The runner loops on it (load the needed step, add its loss,
call again); the analyzer calls it once over the committed table and
refuses on anything but `done`/`dropped` (gate 4). No choice the search
makes can change a read — a unit is written once — only which reads
exist; the design's §11 freeze assignment.

Order of requests, fixed: the spine in SPINE order; then bisection —
the available step nearest the midpoint of (lo, hi), ties toward the
lower step, lo ← step if its loss ≥ target else hi ← step — until lo and
hi are adjacent on the available list; then the window, B⁻ (ascending)
then B⁺ (ascending). Loss monotonicity is NOT assumed: a spike inside
the interval only steers the bisection, and the returned bracket always
straddles the target between two ADJACENT available steps.

Ratification slip 9 (2026-09-23, design §3.7 gate 3 / §3.2 step 4): a
loaded unit whose slice loss is NOT finite is passed in `absent` (never
in `losses`). A window member in `absent` is ABSENT — its side shorter,
listed in the plan's `absent`, exactly the list-edge rule; a step the
search would READ (spine or bisection) that is in `absent` is a fourth
terminal status, `nonfinite` — the runner halts on it and the analyzer
refuses (gate 3: finite on every spine and bisection unit)."""
from __future__ import annotations

import sys
from pathlib import Path

EXP5 = Path(__file__).resolve().parent
if str(EXP5.parent.parent) not in sys.path:
    sys.path.insert(0, str(EXP5.parent.parent))

from experiments.exp5 import battery_5 as b5  # noqa: E402


def bisect_step_5(available, lo: int, hi: int):
    inside = [s for s in available if lo < s < hi]
    if not inside:
        return None
    mid = (lo + hi) / 2.0
    return min(inside, key=lambda s: (abs(s - mid), s))


def plan_5(losses: dict, available, spine, target: float, *, n_side=b5.N_WINDOW_SIDE_5,
           absent=()) -> dict:
    avail = tuple(sorted(int(s) for s in available))
    aset = set(avail)
    spine = tuple(int(s) for s in spine)
    for s in spine:
        if s not in aset:
            raise ValueError(f"spine step {s} is not on the available list")
    losses = {int(k): float(v) for k, v in losses.items()}
    absent = {int(s) for s in absent}
    both = sorted(absent & set(losses))
    if both:
        raise ValueError(f"step(s) {both} are in both `losses` and `absent` — an absent (non-finite) "
                         f"unit's loss is never a table entry")
    for s in spine:
        if s not in losses:
            if s in absent:
                return {"status": "nonfinite", "step": s, "why": "spine"}
            return {"status": "need", "step": s, "why": "spine"}
    interval = None
    for a, b in zip(spine, spine[1:]):
        if losses[a] >= target > losses[b]:
            interval = (a, b)
            break
    if interval is None:
        return {"status": "dropped", "reason": "no spine interval crosses the target",
                "spine_losses": {str(s): losses[s] for s in spine}, "target": float(target)}
    lo, hi = interval
    bisected = []
    while True:
        step = bisect_step_5(avail, lo, hi)
        if step is None:
            break
        if step not in losses:
            if step in absent:
                return {"status": "nonfinite", "step": step, "why": "bisect"}
            return {"status": "need", "step": step, "why": "bisect", "lo": lo, "hi": hi}
        bisected.append(step)
        if losses[step] >= target:
            lo = step
        else:
            hi = step
    i_lo, i_hi = avail.index(lo), avail.index(hi)
    assert i_hi == i_lo + 1
    b_minus_all = list(avail[max(0, i_lo - n_side):i_lo])
    b_plus_all = list(avail[i_hi + 1:i_hi + 1 + n_side])
    band = [s for s in b_minus_all + b_plus_all if s not in absent]
    for s in band:
        if s not in losses:
            return {"status": "need", "step": s, "why": "window",
                    "bracket": [lo, hi], "window": band}
    b_minus = [s for s in b_minus_all if s not in absent]
    b_plus = [s for s in b_plus_all if s not in absent]
    return {"status": "done", "bracket": [lo, hi], "b_minus": b_minus, "b_plus": b_plus,
            "absent": [s for s in b_minus_all + b_plus_all if s in absent],
            "interval": list(interval), "bisected": bisected,
            "edge": {"b_minus": len(b_minus), "b_plus": len(b_plus)},
            "residual_lo": losses[lo] - target, "residual_hi": target - losses[hi],
            "width_steps": hi - lo, "width_tokens": (hi - lo) * b5.TOKENS_PER_STEP_5,
            "target": float(target)}


def replay_5(losses: dict, available, spine, target: float, absent=()) -> dict:
    """The request sequence a runner would have made against a COMPLETE
    table: `plan_5` re-run with the table revealed one requested step at
    a time. `requested` = [(step, why), ...]; `status`/`plan` = the end.
    A step in `absent` (loaded, loss not finite — slip 9) is revealed
    like any other request, in the order the runner met it: as a window
    member it is listed and then skipped; as a step the search would
    READ it ends the replay with `nonfinite`. A step requested twice is
    a logic defect and raises."""
    absent = {int(s) for s in absent}
    seen, seen_absent, requested = {}, set(), []
    while True:
        p = plan_5(seen, available, spine, target, absent=seen_absent)
        if p["status"] != "need":
            return {"status": p["status"], "plan": p, "requested": requested}
        step = p["step"]
        if step in seen or step in seen_absent:
            raise RuntimeError(f"replay_5: step {step} requested twice ({p['why']}) — the planner "
                               f"is not total over this table")
        if step in absent:
            requested.append((step, p["why"]))
            if p["why"] != "window":
                return {"status": "nonfinite", "plan": {"status": "nonfinite", "step": step,
                                                        "why": p["why"]}, "requested": requested}
            seen_absent.add(step)
            continue
        if step not in losses:
            return {"status": "incomplete", "plan": p, "requested": requested,
                    "missing": step}
        requested.append((step, p["why"]))
        seen[step] = losses[step]


def requested_steps_5(replay: dict) -> list:
    return [s for s, _ in replay["requested"]]
