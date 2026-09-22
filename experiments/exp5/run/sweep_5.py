# experiments/exp5/run/sweep_5.py
"""Exp 5 stage 2 for ONE large size (design §7 stage 2; §3.2; §3.7 gates
1(c), 4, 5): the spine in order (the final exists from stage 1), gate
1(c) where a committed interior referent exists (2.8b/6.9b), then per
small partner (ascending) the deterministic search — `search_5.plan_5`
over this size's complete units, load what it asks for, log every
request as `loaded` or `reused` — and the S11 unit when the size is a
small side. Refusal order: prereg tag → frozen → imports → the targets
seal (finals + gates + host + power bound) → the power record on disk →
the projection in HEAD's history (B-7) → the host record equal to this
process's stack/device → HALTED → the finals present.

Window prefetch: once a pair's bracket is fixed (bisection resolved),
`plan_5`'s own `need` dict for a WINDOW step carries the full band
(`"window": b_minus + b_plus`) — the partner loop stashes it in `band`
before calling `request()`, so while one window step's unit is loading,
the next missing window step in that same band is prefetched. `band`
is cleared to None on every SPINE/BISECT need, so a bisection step is
never prefetched (which step comes next depends on the loss just
measured), and `search_5.plan_5` stays the sole authority on both what
to request and what the band is.

Usage: python -m experiments.exp5.run.sweep_5 --size 12b --device cuda [--dry-run]"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

EXP5 = Path(__file__).resolve().parents[1]
REPO = EXP5.parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp5 import _threads_5  # noqa: E402,F401
from experiments.exp2d import analyze_2d as a2d  # noqa: E402
from experiments.exp2d import battery_2d as bt  # noqa: E402
from experiments.exp5 import battery_5 as b5  # noqa: E402
from experiments.exp5 import collect_5 as c5  # noqa: E402
from experiments.exp5 import search_5 as se  # noqa: E402
from experiments.exp5 import slice_5 as sl5  # noqa: E402


def _halt(root, size, message) -> None:
    p = b5.halt_marker_path_5(root, size)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(message + "\n")
    print(f"[5 sweep] HALTED: {message}", flush=True)


def _write(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=1))


def _losses_of(root, size) -> dict:
    d = b5.units_root_5(root) / size
    out = {}
    if d.exists():
        for p in d.iterdir():
            if p.name.startswith("step") and p.name[4:].isdigit():
                step = int(p.name[4:])
                if b5.unit_complete_5(root, size, step):
                    out[step] = json.loads(b5.loss_record_path_5(root, size, step).read_text())["loss"]
    return out


def gate1c(*, root, size, host, git_sha):
    rec = {"size": size, "steps": {}, "tolerance": {"per_rung": b5.GATE1_TOL_PER_RUNG_5,
                                                      "sum": b5.GATE1_TOL_SUM_5},
           "prereg_tag": b5.PREREG_TAG_5, "host_sha256": host["sha256"], "git_sha": git_sha}
    failures = []
    for step in b5.gate1_interior_steps_5(size):
        ref = b5.mac_interior_counts_5(size, step)
        counts = {r: json.loads(b5.rung_record_path_5(root, size, step, r).read_text())["correct"]
                  for r in b5.RUNGS}
        bad = b5.tolerance_failures_5(counts, ref, label=f"gate 1(c) {size}/step{step}")
        rec["steps"][str(step)] = {"counts": counts, "referent": ref, "failures": bad,
                                   "sum_abs_diff": sum(abs(counts[r] - ref[r]) for r in b5.RUNGS),
                                   "max_abs_diff": max(abs(counts[r] - ref[r]) for r in b5.RUNGS)}
        failures += bad
    rec["pass"], rec["failures"] = not failures, failures
    _write(b5.gate1c_path_5(root, size), rec)
    if failures:
        _halt(root, size, f"gate 1(c): {failures[:3]}")
        raise SystemExit(2)
    print(f"[5 sweep] gate 1(c) {size}: PASS on {len(rec['steps'])} interior checkpoints", flush=True)
    return rec


def run(*, size, root=EXP5, cache_root=None, device="cuda", dry_run=False, loaders=None,
        manifest=None, sl=None, host_meta=None, git_sha=None, tag_exists=None, blob_sha=None,
        seal_check=None, projection_commit=None, is_ancestor=None, power_present=None) -> None:
    prereg = b5.require_prereg_5(tag_exists=tag_exists, blob_sha=blob_sha)
    b5.check_frozen_5()
    b5.check_imports_5()
    root = Path(root)
    cache_root = cache_root if cache_root is not None else c5.CKPT_CACHE_5
    git_sha = git_sha or b5.git_sha_5()
    seal = (seal_check or b5.require_targets_seal_5)(root, tag_exists=tag_exists)
    if seal["failures"]:
        raise RuntimeError(f"refusing: the targets seal: {seal['failures'][0]}")
    present = b5.power_path_5(root).is_file() if power_present is None else power_present
    if not present:
        raise RuntimeError("refusing: results/power_5.json is not present — power ONCE precedes the seal")
    pc = b5.projection_commit_5() if projection_commit is None and is_ancestor is None else projection_commit
    anc = is_ancestor or b5.is_ancestor_5
    if not pc or not anc(pc, git_sha):
        raise RuntimeError("refusing: the projection is not committed in this HEAD's history "
                           "(design §7: the projection is sealed before the sweep)")
    hp = b5.host_record_path_5(root)
    if not hp.is_file():
        raise RuntimeError("refusing: no host record — run finals_5 first")
    host = json.loads(hp.read_text())
    live_stack = host_meta["stack"] if host_meta is not None else c5.stack_5()
    if host["stack"] != live_stack or host["device"] != device:
        raise RuntimeError(f"refusing: host record {host['stack']}/{host['device']} is not this "
                           f"process's {live_stack}/{device}")
    if b5.halt_marker_path_5(root, size).exists():
        raise RuntimeError(f"refusing: {size} is halted ({b5.halt_marker_path_5(root, size)})")
    manifest = manifest if manifest is not None else b5.load_manifest_5(sha_pin=b5.CHECKPOINTS_SHA256_5)
    for s in b5.SIZES_5:
        if not b5.unit_complete_5(root, s, b5.FINAL_STEP_5):
            raise RuntimeError(f"refusing: the {s} final is not complete — run finals_5 first")
    spine = b5.spine_5(manifest, size)
    partners = [s for s in b5.SIZES_5 if b5.SIZES_5.index(s) < b5.SIZES_5.index(size)]
    if dry_run:
        done = _losses_of(root, size)
        print(f"[5 sweep] {size}: prereg {prereg['tag']!r}; spine {spine}; partners {partners}; "
              f"units complete {sorted(done)}; gate 1(c) "
              f"{'n/a' if not b5.gate1_interior_steps_5(size) else ('done' if b5.gate1c_path_5(root, size).is_file() else 'pending')}",
              flush=True)
        return
    sl = sl if sl is not None else sl5.load_slice_5(sha_pin=b5.SLICE_SHA256_5)
    if loaders is None:
        loaders = c5.real_loaders_5()
    battery = bt.load_battery()
    verify_fn = a2d.load_verify()
    pf = c5.Prefetcher(loaders, cache_root=cache_root)
    kw = dict(root=root, manifest=manifest, cache_root=cache_root, device=device, battery=battery,
              verify_fn=verify_fn, sl=sl, host=host, loaders=loaders, git_sha=git_sha, prefetcher=pf)
    log_path = b5.search_log_path_5(root, size)
    log = json.loads(log_path.read_text()) if log_path.is_file() else \
        {"size": size, "spine": list(spine), "spine_substitutions": b5.spine_substitutions_5(manifest, size),
         "requests": [], "pairs": {}, "s11": None, "prereg_tag": b5.PREREG_TAG_5, "git_sha": git_sha}

    def request(step, why, pair=None):
        nxt = _next_known(step)
        if nxt is not None and not b5.unit_complete_5(root, size, nxt):
            pf.start(size, b5.entry_5(manifest, size, nxt))
        r = c5.run_unit_5(size, step, why=why, **kw)
        ev = {"step": int(step), "why": why, "action": r["action"], "loss": r["loss"]}
        (log["pairs"][pair]["requests"] if pair else log["requests"]).append(ev)
        _write(log_path, log)
        c5.rebuild_loss_table_5(root)
        return r["loss"]

    # Window-prefetch band: the current pair's `b_minus + b_plus` list,
    # straight from `plan_5`'s own "window"-need dict (RULING B), while
    # the partner loop is issuing WINDOW requests; cleared to None on
    # every SPINE/BISECT need so a bisection step is never treated as a
    # window member. `_next_known` is the one function `request`
    # consults; extending it (not `request` itself) keeps the spine
    # loop's call sites unchanged.
    band = None

    def _next_known(step):
        if step in spine:
            i = spine.index(step)
            return spine[i + 1] if i + 1 < len(spine) else None
        if band and step in band:
            i = band.index(step)
            return band[i + 1] if i + 1 < len(band) else None
        return None

    # (1) the spine
    for s in spine:
        if not b5.unit_complete_5(root, size, s):
            request(s, "spine")
    # gate 1(c)
    if b5.gate1_interior_steps_5(size) and not b5.gate1c_path_5(root, size).is_file():
        gate1c(root=root, size=size, host=host, git_sha=git_sha)
    # (2) per partner: the search
    avail = b5.available_5(manifest, size)
    for small in partners:
        target = json.loads(b5.loss_record_path_5(root, small, b5.FINAL_STEP_5).read_text())["loss"]
        log["pairs"].setdefault(small, {"target": target, "requests": [], "status": "open", "plan": None})
        if log["pairs"][small]["status"] in ("done", "dropped"):
            continue
        losses = _losses_of(root, size)
        while True:
            p = se.plan_5(losses, avail, spine, target)
            if p["status"] == "need":
                band = p["window"] if p["why"] == "window" else None
                losses[p["step"]] = request(p["step"], p["why"], pair=small)
                continue
            log["pairs"][small].update({"status": p["status"], "plan": p})
            # RULING A: the complete request sequence a fresh reader of the committed loss
            # table would replay (gate 4's identity), each step marked "loaded" if THIS run's
            # own request() call fetched it for this pair, "reused" if plan_5 silently found it
            # already known (the spine, an earlier partner's fetch, or the final).
            loaded_here = {r["step"] for r in log["pairs"][small]["requests"]}
            rep = se.replay_5(losses, avail, spine, target)
            log["pairs"][small]["requested_all"] = [
                {"step": s, "why": why, "action": ("loaded" if s in loaded_here else "reused")}
                for s, why in rep["requested"]]
            _write(log_path, log)
            print(f"[5 sweep] {size} × {small}: {p['status']}"
                  + (f" bracket {p['bracket']} window {p['b_minus']}+{p['b_plus']}"
                     if p["status"] == "done" else ""), flush=True)
            break
    # (3) S11
    if size in b5.SMALL_SIDES_5 and (log["s11"] is None or not b5.unit_complete_5(root, size, b5.S11_STEP_5)):
        loss = request(b5.S11_STEP_5, "s11")
        log["s11"] = {"step": b5.S11_STEP_5, "loss": loss}
        _write(log_path, log)
    pf.wait()
    c5.rebuild_loss_table_5(root)
    print(f"[5 sweep] {size}: complete", flush=True)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Exp 5 stage 2: one large size's spine, search, windows, S11")
    ap.add_argument("--size", required=True, choices=b5.SIZES_5)
    ap.add_argument("--root", default=str(EXP5))
    ap.add_argument("--cache-root", default=str(c5.CKPT_CACHE_5))
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--dry-run", action="store_true")
    ar = ap.parse_args(argv)
    run(size=ar.size, root=Path(ar.root), cache_root=Path(ar.cache_root), device=ar.device,
        dry_run=ar.dry_run)
    return 0


if __name__ == "__main__":
    sys.exit(main())
