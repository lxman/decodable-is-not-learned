# experiments/exp6/run/sweep_6.py
"""The sweep (design §3.4, §7): one family per invocation, the smallest
family first.

    python -m experiments.exp6.run.sweep_6 --family smollm3_3b --device cuda

Gate 1 runs FIRST, on every host that sweeps a family:
  (a) the endpoint through BOTH loader paths on this host — identical
      bits and continuations on all twenty rungs, 500 compared per rung,
      tensor digests equal;
  (b) this host's endpoint against the SEALED endpoint-stage records —
      within the cross-host tolerance on every rung (the endpoint stage
      ran on another instance);
  (c) the anchors against the Mac's committed counts, here and again at
      every grid step.
Both of the host's reads are kept under `gate1_<host>/`, so the analyzer
re-derives the gate from bytes. A failure writes HALTED and stops; the
analyzer reads that tree as INSUFFICIENT_DATA. The first host's
candidate-loader read of the endpoint is also the grid's endpoint unit.
Nothing is overwritten: a host that takes over a family writes its own
gate directory and continues at the first incomplete step.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

EXP6 = Path(__file__).resolve().parents[1]
REPO = EXP6.parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp6 import battery_6 as b6  # noqa: E402
from experiments.exp6 import families_6 as fm  # noqa: E402
from experiments.exp6 import pins_6 as p6  # noqa: E402
from experiments.exp6 import records_6 as r6  # noqa: E402
from experiments.exp6 import referents_6 as rf  # noqa: E402
from experiments.exp6.run import _common_6 as cm  # noqa: E402
from experiments.exp6.run import endpoint_6 as ep  # noqa: E402
from experiments.exp6.run import predict_6 as pr  # noqa: E402
from experiments.exp6.run import seal_endpoint_6 as se  # noqa: E402


def require_endpoint_seal(root, *, tag_exists=None, blobs_bound=None) -> str:
    """The endpoint stage is sealed and the tag binds every file the
    rung-sets record names, the record itself and the power record.
    Returns the composite sha stamped on every sweep record."""
    for p in (r6.rung_sets_path(root), r6.power_path(root)):
        if not p.is_file():
            raise RuntimeError(f"{p} missing — the endpoint stage is not sealed")
    p6.require_seal(r6.ENDPOINT_SEAL_TAG_6, se.seal_paths(root),
                    tag_exists=tag_exists, blobs_bound=blobs_bound)
    return se.endpoint_sha256(root)


def step_complete(root, family, step) -> bool:
    return r6.whole(r6.checkpoint_path(root, family, step)) and all(
        [r6.whole(r6.sweep_record_path(root, family, step, r))
         for r in b6.ALL_RUNGS_6])


def halt(root, family, lines) -> None:
    p = r6.sweep_halt_path(root, family)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("\n".join(lines) + "\n")


def anchor_failures(counts: dict, family, step, *, label) -> list:
    mac = {r: rf.mac_count(family, step, r) for r in b6.ANCHORS_6}
    return rf.anchor_tolerance(counts, mac, label=label)


def _probe(battery) -> list:
    return pr.prompts_of(battery[b6.RUNGS_6[0]])


def read_model(family, key, *, load_fn, entry, battery, host, device, loaders) -> dict:
    """Load once, measure, score all twenty rungs. Returns
    {"load", "evs"}; writes nothing."""
    t0 = time.time()
    model, tok, info = load_fn()
    try:
        cm.require_the_macs_weights(
            info, family, key, entry,
            label=f"6 gate 1(d) {family}/{r6.GATE_READS_6[key]}"
            if key in r6.GATE_READS_6 else f"6 gate 1(d) {family}/{fm.step_dir(key)}")
        runner = loaders["runner"](family, tok, model)
        load = r6.load_record(family=family, key=key, entry=entry, info=info,
                              device=device, host_sha256=host["sha256"],
                              seconds=time.time() - t0,
                              n_nonfinite=loaders["nonfinite"](model, tok,
                                                               _probe(battery)))
        evs = {}
        for rung in b6.ALL_RUNGS_6:
            t1 = time.time()
            evs[rung] = r6.evaluate_items_6(runner, battery[rung])
            evs[rung]["seconds"] = time.time() - t1
    finally:
        loaders["release"](model)
    return {"load": load, "evs": evs}


def write_units(read, *, family, battery, ctx, path_of, load_path, step=None,
                which=None) -> None:
    """Records first, the load record LAST (the completeness signal)."""
    for rung, ev in read["evs"].items():
        r6.write_json(path_of(rung), r6.unit_record(
            family=family, rung=rung, cap=battery[rung], ev=ev, load=read["load"],
            host_sha256=ctx["host"]["sha256"], seal_sha256=ctx["seal_sha"],
            stack=ctx["stack"], git_sha=ctx["git_sha"], seconds=ev["seconds"],
            step=step, which=which, endpoint_sha256=ctx["endpoint_sha"]))
    r6.write_json(load_path, read["load"])


def gate1_record(family, *, thin, cand, sealed, thin_load, cand_load,
                 anchor_bad, sealed_load) -> dict:
    """Gate 1 as a pure function of three reads of the endpoint: this
    host's two and the sealed one. The analyzer calls it on the bytes."""
    rows, bad = {}, []
    for r in b6.ALL_RUNGS_6:
        a, b, s = thin[r], cand[r], sealed[r]
        n = len(a["bits"])
        bit = sum(1 for x, y in zip(a["bits"], b["bits"]) if x != y)
        con = sum(1 for x, y in zip(a["continuations"], b["continuations"])
                  if x != y)
        d = abs(int(a["correct"]) - int(s["correct"]))
        rows[r] = {"compared": n, "bit_diffs": bit, "continuation_diffs": con,
                   "sealed_count": int(s["correct"]), "host_count": int(a["correct"]),
                   "abs_diff_vs_sealed": d}
        if n != b6.N_ITEMS or len(b["bits"]) != b6.N_ITEMS or \
                len(a["continuations"]) != b6.N_ITEMS or \
                len(b["continuations"]) != b6.N_ITEMS:
            bad.append(f"6 gate 1(a) {family}/{r}: {n} items compared, not "
                       f"{b6.N_ITEMS}")
        if bit or con:
            bad.append(f"6 gate 1(a) {family}/{r}: {bit} bit and {con} "
                       f"continuation diffs between the two loaders")
        if d > rf.TOL_PER_RUNG_6:
            bad.append(f"6 gate 1(b) {family}/{r}: |Δ| {d} > {rf.TOL_PER_RUNG_6} "
                       f"against the sealed endpoint record")
    if not thin_load.get("digest") or thin_load.get("digest") != cand_load.get("digest"):
        bad.append(f"6 gate 1(a) {family}: the two loaders' tensor digests differ")
    if not sealed_load.get("digest") or \
            sealed_load.get("digest") != cand_load.get("digest"):
        # the read that set R_f and this host's file-verified read are one model
        bad.append(f"6 gate 1(b) {family}: this host's tensor digest is not the "
                   f"sealed endpoint read's")
    bad += list(anchor_bad)
    return {"family": family, "rungs": rows,
            "rungs_compared": len(rows), "items_per_rung": b6.N_ITEMS,
            "digest_thin": thin_load.get("digest"),
            "digest_candidate": cand_load.get("digest"),
            "digest_sealed": sealed_load.get("digest"),
            "commit": cand_load.get("commit"),
            "tolerance_per_rung": rf.TOL_PER_RUNG_6, "failures": bad,
            "pass": not bad}


def run_gate1(family, *, root, man, battery, ctx, loaders, cache_root) -> dict:
    end = fm.endpoint_step(family)
    entry = fm.entry(family, man, end)
    host, device = ctx["host"], ctx["device"]
    h = host["sha256"]
    thin = read_model(family, r6.SWEEP_THIN, entry=entry, battery=battery,
                      host=host, device=device, loaders=loaders,
                      load_fn=lambda: loaders["thin"](family, man, device=device))
    thin["load"]["kind"] = "thin-loader"
    write_units(thin, family=family, battery=battery, ctx=ctx, which=r6.SWEEP_THIN,
                path_of=lambda r: r6.gate_record_path(root, family, h,
                                                      r6.SWEEP_THIN, r),
                load_path=r6.gate_load_path(root, family, h, r6.SWEEP_THIN))
    try:
        cand = read_model(
            family, r6.SWEEP_CAND, entry=entry, battery=battery, host=host,
            device=device, loaders=loaders,
            load_fn=lambda: loaders["checkpoint"](family, man, end, device=device,
                                                  cache_root=cache_root))
    finally:
        loaders["free"](family, man, end, cache_root=cache_root)
    write_units(cand, family=family, battery=battery, ctx=ctx, which=r6.SWEEP_CAND,
                path_of=lambda r: r6.gate_record_path(root, family, h,
                                                      r6.SWEEP_CAND, r),
                load_path=r6.gate_load_path(root, family, h, r6.SWEEP_CAND))
    sealed = {r: r6.read_json(r6.endpoint_record_path(root, family,
                                                      "stage1_final", r))
              for r in b6.ALL_RUNGS_6}
    counts = {r: int(cand["evs"][r]["correct"]) for r in b6.ANCHORS_6}
    gate = gate1_record(
        family, thin=thin["evs"], cand=cand["evs"], sealed=sealed,
        thin_load=thin["load"], cand_load=cand["load"],
        sealed_load=r6.read_json(r6.endpoint_load_path(root, family, "stage1_final")),
        anchor_bad=anchor_failures(counts, family, end,
                                   label=f"6 gate 1(c) {family}/step{end}"))
    gate.update({"host_sha256": h, "prereg_tag": r6.PREREG_TAG_6,
                 "endpoint_sha256": ctx["endpoint_sha"], "stack": ctx["stack"],
                 "git_sha": ctx["git_sha"]})
    r6.write_json(r6.gate1_path(root, family, h), gate)
    if gate["pass"] and not step_complete(root, family, end):
        # the grid's endpoint unit IS this host's candidate read
        step_load = dict(cand["load"], key=int(end))
        write_units({"load": step_load, "evs": cand["evs"]}, family=family,
                    battery=battery, ctx=ctx, step=end,
                    path_of=lambda r: r6.sweep_record_path(root, family, end, r),
                    load_path=r6.checkpoint_path(root, family, end))
    return gate


def run_step(family, step, *, root, man, battery, ctx, loaders, cache_root) -> list:
    """One grid step through the candidate-file loader; the anchors
    gated BEFORE the completeness signal is written. Returns the gate's
    failures (empty = pass)."""
    device = ctx["device"]
    try:
        read = read_model(
            family, int(step), entry=fm.entry(family, man, step), battery=battery,
            host=ctx["host"], device=device, loaders=loaders,
            load_fn=lambda: loaders["checkpoint"](family, man, step, device=device,
                                                  cache_root=cache_root))
    except cm.GateFired as e:   # the load record is the evidence; no unit was scored
        r6.write_json(r6.halted_step_dir(root, family, step) / "_checkpoint.json",
                      e.load)
        return e.failures
    finally:
        loaders["free"](family, man, step, cache_root=cache_root)
    counts = {r: int(read["evs"][r]["correct"]) for r in b6.ANCHORS_6}
    bad = anchor_failures(counts, family, step,
                          label=f"6 gate 1(c) {family}/step{step}")
    if bad:                 # the evidence is kept; the step stays incomplete
        d = r6.halted_step_dir(root, family, step)
        write_units(read, family=family, battery=battery, ctx=ctx, step=step,
                    path_of=lambda r: d / f"{r}.json",
                    load_path=d / "_checkpoint.json")
        return bad
    write_units(read, family=family, battery=battery, ctx=ctx, step=step,
                path_of=lambda r: r6.sweep_record_path(root, family, step, r),
                load_path=r6.checkpoint_path(root, family, step))
    return []


def run(family, *, root=EXP6, device="cuda", loaders=None, dry_run=False,
        cache_root=fm.CKPT_CACHE_6, tag_exists=None, blob_sha=None,
        blobs_bound=None, frozen_check=None, host=None) -> dict:
    if family not in fm.FAMILIES_6:
        raise ValueError(f"{family!r} is not a family")
    cm.gates(tag_exists=tag_exists, blob_sha=blob_sha, frozen_check=frozen_check)
    seal = ep.require_predictor_seal(root, tag_exists=tag_exists,
                                     blobs_bound=blobs_bound)
    endpoint_sha = require_endpoint_seal(root, tag_exists=tag_exists,
                                         blobs_bound=blobs_bound)
    cm.refuse_if_halted(root)
    end = fm.endpoint_step(family)
    order = [end] + [s for s in fm.grid(family) if s != end]
    if dry_run:
        return {"pending": [s for s in order if not step_complete(root, family, s)]}
    host = host or cm.ensure_host(root, device)
    bad = cm.host_failures(host)
    if bad:
        raise RuntimeError(f"host record: {bad}")
    loaders = ep.real_loaders() if loaders is None else loaders
    battery = b6.load_battery_6()
    man = fm.manifest(family)
    ctx = {"host": host, "device": device, "seal_sha": seal["sha256"],
           "endpoint_sha": endpoint_sha, "stack": cm.short_stack(),
           "git_sha": p6.git_sha()}
    kw = dict(root=root, man=man, battery=battery, ctx=ctx, loaders=loaders,
              cache_root=cache_root)
    gpath = r6.gate1_path(root, family, host["sha256"])
    if not gpath.exists():
        try:
            gate = run_gate1(family, **kw)
        except cm.GateFired as e:
            halt(root, family, e.failures + [json.dumps(e.load, sort_keys=True)])
            raise
        if not gate["pass"]:
            halt(root, family, gate["failures"])
            raise RuntimeError(f"GATE 1 FIRED: {gate['failures'][:3]}")
    elif not r6.read_json(gpath).get("pass"):
        raise RuntimeError(f"{gpath} records a failed gate")
    done = []
    for step in order:
        if step_complete(root, family, step):
            continue
        fails = run_step(family, step, **kw)
        if fails:
            halt(root, family, fails)
            gate = "1(d)" if any(x.startswith("6 gate 1(d)") for x in fails) else "1(c)"
            raise RuntimeError(f"GATE {gate} FIRED: {fails}")
        done.append(step)
    cm.exit_gate(r6.sweep_halt_path(root, family), frozen_check=frozen_check)
    return {"family": family, "steps_run": done, "host_sha256": host["sha256"]}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--family", required=True, choices=fm.FAMILIES_6)
    ap.add_argument("--root", default=str(EXP6))
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--cache-root", default=str(fm.CKPT_CACHE_6))
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    print(run(a.family, root=Path(a.root), device=a.device,
              cache_root=Path(a.cache_root), dry_run=a.dry_run))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
