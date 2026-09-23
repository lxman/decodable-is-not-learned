# experiments/exp5/run/finals_5.py
"""Exp 5 stage 1 (design §7 stage 1; §3.7 gates 0, 1(a), 1(b)): the host
record (written once), gate 1(a) at 2.8b through two loader paths, the
seven finals as units (largest first), gate 1(b) against the Mac's
committed counts under the pinned tolerance, the loss table's first rows.
Refusal order: prereg tag → frozen → imports → manifest → slice →
HALTED → (dry run stops here) → the host record (written once; a later
run must present the same stack/device, and it must meet gate 0's pins). Any gate failure writes the gate record, a HALTED
marker, and exits 2 (the tree it leaves is INSUFFICIENT_DATA).

Usage: python -m experiments.exp5.run.finals_5 --device cuda [--dry-run]"""
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
from experiments.exp5 import slice_5 as sl5  # noqa: E402

FINALS_ORDER_5 = ("2.8b", "12b", "6.9b", "1.4b", "1b", "410m", "160m")   # 2.8b = gate 1(a) first


def _halt(root, size, message) -> None:
    p = b5.halt_marker_path_5(root, size)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(message + "\n")
    print(f"[5 finals] HALTED: {message}", flush=True)


def _write(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=1))


def gate1a(*, root, manifest, cache_root, device, battery, verify_fn, sl, host, loaders, git_sha):
    """2c's `main` loader (path a) vs the candidate-file loader at main's
    entry (path b, which IS the 2.8b final's unit)."""
    from experiments.exp2g.run.sweep_2g import evaluate_items
    size = "2.8b"
    t0 = time.time()
    model_a = None
    try:
        model_a, info_a = loaders["pythia_2c"](size, device)
        digest_a = loaders["digest"](model_a)
        loss_a = loaders["loss"](model_a, sl, batch_size=b5.LOSS_BATCH_5, device=device)
        runner_a = loaders["runner"](loaders["tokenizer"](size), model_a)
        evs_a = {r: evaluate_items(runner_a, battery[r], verify_fn) for r in b5.RUNGS}
    finally:
        loaders["release"](model_a)
        model_a = None
        runner_a = None
    c5.run_unit_5(size, b5.FINAL_STEP_5, root=root, manifest=manifest, cache_root=cache_root,
                  device=device, battery=battery, verify_fn=verify_fn, sl=sl, host=host,
                  loaders=loaders, git_sha=git_sha, why="final")
    d = b5.unit_dir_5(root, size, b5.FINAL_STEP_5)
    ck = json.loads((d / "_checkpoint.json").read_text())
    loss_b = json.loads((d / "_loss.json").read_text())
    diffs, compared = {}, {}
    for r in b5.RUNGS:
        conts_b = json.loads((d / f"{r}.json").read_text())["continuations"]
        pairs = list(zip(conts_b, evs_a[r]["continuations"]))
        compared[r] = len(pairs)
        diffs[r] = int(sum(1 for x, y in pairs if x != y))
    rec = {"size": size, "digest_2c_path": digest_a, "digest_candidate_path": ck["digest"],
           "digests_equal": digest_a == ck["digest"],
           "counts_2c_path": {r: evs_a[r]["correct"] for r in b5.RUNGS},
           "continuation_diffs": diffs, "continuations_compared": compared,
           "loss_2c_path": loss_a["loss"], "loss_candidate_path": loss_b["loss"],
           "loss_equal": (repr(loss_a["loss"]) == repr(loss_b["loss"])
                          and loss_a["per_doc_loss"] == loss_b["per_doc_loss"]),
           "per_doc_diffs": int(sum(1 for x, y in zip(loss_a["per_doc_loss"], loss_b["per_doc_loss"])
                                    if x != y)),
           "prereg_tag": b5.PREREG_TAG_5, "host_sha256": host["sha256"], "git_sha": git_sha,
           "seconds": round(time.time() - t0, 1)}
    failures = []
    if not rec["digests_equal"]:
        failures.append("gate 1(a): tensor digests differ between the two loader paths")
    failures += [f"gate 1(a)/{r}: {n} continuation diffs" for r, n in diffs.items() if n]
    failures += [f"gate 1(a)/{r}: {n} pairs compared, not {b5.N_ITEMS}" for r, n in compared.items()
                 if n != b5.N_ITEMS]
    if not rec["loss_equal"]:
        failures.append("gate 1(a): the slice loss differs between the two loader paths")
    rec["pass"], rec["failures"] = not failures, failures
    _write(b5.gate1a_path_5(root), rec)
    if failures:
        _halt(root, size, f"gate 1(a): {failures[:3]}")
        raise SystemExit(2)
    print("[5 finals] gate 1(a) 2.8b: PASS (digests equal, 0 continuation diffs on 34 rungs, "
          "loss identical)", flush=True)
    return rec


def gate1b(*, root, host, git_sha):
    rec = {"per_size": {}, "no_referent": [], "tolerance": {"per_rung": b5.GATE1_TOL_PER_RUNG_5,
                                                            "sum": b5.GATE1_TOL_SUM_5},
           "bench": b5.GATE1_BENCH_5, "prereg_tag": b5.PREREG_TAG_5, "host_sha256": host["sha256"],
           "git_sha": git_sha}
    failures = []
    for size in b5.SIZES_5:
        ref = b5.mac_final_counts_5(size)
        counts = {r: json.loads(b5.rung_record_path_5(root, size, b5.FINAL_STEP_5, r).read_text())["correct"]
                  for r in b5.RUNGS}
        if ref is None:
            rec["no_referent"].append(size)
            rec["per_size"][size] = {"counts": counts, "referent": None}
            continue
        bad = b5.tolerance_failures_5(counts, ref, label=f"gate 1(b) {size}")
        rec["per_size"][size] = {"counts": counts, "referent": ref,
                                 "sum_abs_diff": sum(abs(counts[r] - ref[r]) for r in b5.RUNGS),
                                 "max_abs_diff": max(abs(counts[r] - ref[r]) for r in b5.RUNGS),
                                 "failures": bad}
        failures += bad
    rec["pass"], rec["failures"] = not failures, failures
    _write(b5.gate1b_path_5(root), rec)
    if failures:
        size = failures[0].split()[2].rstrip(":").split("/")[0]
        _halt(root, size, f"gate 1(b): {failures[:3]}")
        raise SystemExit(2)
    print(f"[5 finals] gate 1(b): PASS on {[s for s in b5.SIZES_5 if s not in rec['no_referent']]}; "
          f"no referent for {rec['no_referent']}", flush=True)
    return rec


def run(*, root=EXP5, cache_root=None, device="cuda", dry_run=False, loaders=None, manifest=None,
        sl=None, host_meta=None, git_sha=None, tag_exists=None, blob_sha=None) -> None:
    prereg = b5.require_prereg_5(tag_exists=tag_exists, blob_sha=blob_sha)
    b5.check_frozen_5()
    b5.check_imports_5()
    root = Path(root)
    cache_root = cache_root if cache_root is not None else c5.CKPT_CACHE_5
    git_sha = git_sha or b5.git_sha_5()
    manifest = manifest if manifest is not None else b5.load_manifest_5(sha_pin=b5.CHECKPOINTS_SHA256_5)
    sl = sl if sl is not None else sl5.load_slice_5(sha_pin=b5.SLICE_SHA256_5)
    for size in b5.SIZES_5:
        if b5.halt_marker_path_5(root, size).exists():
            raise RuntimeError(f"refusing: {size} is halted ({b5.halt_marker_path_5(root, size)})")
    pending = [s for s in FINALS_ORDER_5 if s in b5.SIZES_5 and not b5.unit_complete_5(root, s, b5.FINAL_STEP_5)]
    if dry_run:
        host_state = "present" if b5.host_record_path_5(root).is_file() else "pending"
        print(f"[5 finals] prereg {prereg['tag']!r}; host record {host_state}; "
              f"gate 1(a) {'done' if b5.gate1a_path_5(root).is_file() else 'pending'}; "
              f"would run {len(pending)} final(s): {pending}", flush=True)
        return
    if loaders is None:
        loaders = c5.real_loaders_5()
    # gate 0: the host record, written ONCE; a later run must present the same stack/device
    hp = b5.host_record_path_5(root)
    if host_meta is None:
        transports = c5.measure_transports_5(cache_root=cache_root)
        live = c5.host_record_5(device, transports)
    else:
        live = c5.host_record_5(device, host_meta["transports"], stack=host_meta["stack"],
                                gpu=host_meta["gpu"], python=host_meta["python"])
    if hp.is_file():
        host = json.loads(hp.read_text())
        if host["stack"] != live["stack"] or host["device"] != live["device"]:
            raise RuntimeError(f"refusing: the host record on disk ({host['stack']}, "
                               f"{host['device']}) is not this process's ({live['stack']}, "
                               f"{live['device']})")
    else:
        bad = b5.host_record_failures_5(live)
        if bad:
            raise RuntimeError(f"refusing: host record: {bad}")
        _write(hp, live)
        host = live
    battery = bt.load_battery()
    verify_fn = a2d.load_verify()
    if not b5.gate1a_path_5(root).is_file():
        gate1a(root=root, manifest=manifest, cache_root=cache_root, device=device, battery=battery,
               verify_fn=verify_fn, sl=sl, host=host, loaders=loaders, git_sha=git_sha)
    for size in FINALS_ORDER_5:
        if size in b5.SIZES_5:
            c5.run_unit_5(size, b5.FINAL_STEP_5, root=root, manifest=manifest, cache_root=cache_root,
                          device=device, battery=battery, verify_fn=verify_fn, sl=sl, host=host,
                          loaders=loaders, git_sha=git_sha, why="final")
    if not b5.gate1b_path_5(root).is_file():
        gate1b(root=root, host=host, git_sha=git_sha)
    c5.rebuild_loss_table_5(root)
    print("[5 finals] complete: seven finals, gates 1(a)/(b), loss table rows", flush=True)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Exp 5 stage 1: finals + gate 1(a)/(b)")
    ap.add_argument("--root", default=str(EXP5))
    ap.add_argument("--cache-root", default=str(c5.CKPT_CACHE_5))
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--dry-run", action="store_true")
    ar = ap.parse_args(argv)
    run(root=Path(ar.root), cache_root=Path(ar.cache_root), device=ar.device, dry_run=ar.dry_run)
    return 0


if __name__ == "__main__":
    sys.exit(main())
