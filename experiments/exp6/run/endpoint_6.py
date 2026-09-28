# experiments/exp6/run/endpoint_6.py
"""The endpoint stage (design §3.4, §7): for each family, its stage-1
endpoint through the THIN loader and its init referent, on all twenty
rungs. Then gate 1(b): the anchors against the Mac's committed counts,
within Exp 5's cross-host tolerance.

    python -m experiments.exp6.run.endpoint_6 --device cuda [--family olmo7b]

Runs only after the predictor is sealed. The rung sets and the power
record are written on the Mac (run/seal_endpoint_6.py, power_6.py),
not here.
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
from experiments.exp6.run import predict_6 as pr  # noqa: E402


def real_loaders() -> dict:
    return {"thin": fm.load_thin, "init": fm.load_init,
            "checkpoint": fm.load_checkpoint, "runner": fm.runner,
            "release": fm.release, "free": fm.free, "nonfinite": cm.n_nonfinite}


def require_predictor_seal(root, *, tag_exists=None, blobs_bound=None) -> dict:
    """The predictor seal exists, its file table is the disk's, and the
    tag binds every file it names."""
    from experiments.exp6.run import seal_predictor_6 as sp
    seal = r6.read_json(r6.seal_path(root))
    files = sp.file_table(root)
    if seal.get("files") != files or seal.get("sha256") != r6.composite_sha(files):
        raise RuntimeError("the predictor seal does not describe the files on disk")
    p6.require_seal(r6.PREDICTOR_SEAL_TAG_6,
                    [Path(root) / rel for rel in files] + [r6.seal_path(root)],
                    tag_exists=tag_exists, blobs_bound=blobs_bound)
    return seal


def which_complete(root, family, which) -> bool:
    return r6.whole(r6.endpoint_load_path(root, family, which)) and all(
        [r6.whole(r6.endpoint_record_path(root, family, which, r))
         for r in b6.ALL_RUNGS_6])


def run_which(family, which, *, root, device, man, battery, host, seal_sha,
              loaders, stack, git_sha) -> dict:
    if which_complete(root, family, which):
        return r6.read_json(r6.endpoint_load_path(root, family, which))
    t0 = time.time()
    key = fm.endpoint_step(family) if which == "stage1_final" else fm.INIT
    entry = fm.entry(family, man, key)
    load_fn = loaders["thin"] if which == "stage1_final" else loaders["init"]
    model, tok, info = load_fn(family, man, device=device)
    try:
        cm.require_the_macs_weights(info, family, which, entry,
                                    label=f"6 gate 1(d) {family}/{which}")
        runner = loaders["runner"](family, tok, model)
        probe = pr.prompts_of(battery[b6.RUNGS_6[0]])
        load = r6.load_record(family=family, key=which, entry=entry, info=info,
                              device=device, host_sha256=host["sha256"],
                              seconds=time.time() - t0,
                              n_nonfinite=loaders["nonfinite"](model, tok, probe))
        if which == "stage1_final":
            load["kind"] = "thin-loader"
        for rung in b6.ALL_RUNGS_6:
            path = r6.endpoint_record_path(root, family, which, rung)
            if path.exists():
                continue
            t1 = time.time()
            ev = r6.evaluate_items_6(runner, battery[rung])
            r6.write_json(path, r6.unit_record(
                family=family, rung=rung, cap=battery[rung], ev=ev, load=load,
                host_sha256=host["sha256"], seal_sha256=seal_sha, stack=stack,
                git_sha=git_sha, seconds=time.time() - t1, which=which))
        r6.write_json(r6.endpoint_load_path(root, family, which), load)   # LAST
    finally:
        loaders["release"](model)
    return load


def anchor_counts(root, family, which) -> dict:
    return {r: int(r6.read_json(r6.endpoint_record_path(root, family, which, r))
                   ["correct"]) for r in b6.ANCHORS_6}


def gate1b(root, families) -> dict:
    """The anchors on this host against the Mac's committed records:
    the stage-1 endpoint and the init referent, each within
    `TOL_PER_RUNG_6` per rung (`referents_6.gate1b_record`)."""
    return rf.gate1b_record({f: {w: anchor_counts(root, f, w)
                                 for w in r6.ENDPOINT_WHICH_6} for f in families})


def run(*, root=EXP6, device="cuda", families=None, loaders=None, dry_run=False,
        tag_exists=None, blob_sha=None, blobs_bound=None, frozen_check=None,
        host=None) -> dict:
    cm.gates(tag_exists=tag_exists, blob_sha=blob_sha, frozen_check=frozen_check)
    seal = require_predictor_seal(root, tag_exists=tag_exists,
                                  blobs_bound=blobs_bound)
    if r6.rung_sets_path(root).exists():
        raise RuntimeError("the endpoint stage is sealed; nothing is read after it")
    cm.refuse_if_halted(root)
    families = tuple(families or fm.FAMILIES_6)
    todo = [(f, w) for f in families for w in r6.ENDPOINT_WHICH_6
            if not which_complete(root, f, w)]
    if dry_run:
        return {"pending": [f"{f}/{w}" for f, w in todo]}
    host = host or cm.ensure_host(root, device)
    bad = cm.host_failures(host)
    if bad:
        raise RuntimeError(f"host record: {bad}")
    loaders = real_loaders() if loaders is None else loaders
    battery = b6.load_battery_6()
    stack, sha = cm.short_stack(), p6.git_sha()
    try:
        for f, w in todo:
            run_which(f, w, root=root, device=device, man=fm.manifest(f),
                      battery=battery, host=host, seal_sha=seal["sha256"],
                      loaders=loaders, stack=stack, git_sha=sha)
    except cm.GateFired as e:
        r6.endpoint_halt_path(root).parent.mkdir(parents=True, exist_ok=True)
        r6.endpoint_halt_path(root).write_text(
            "\n".join(e.failures + [json.dumps(e.load, sort_keys=True)]) + "\n")
        raise
    done = [f for f in fm.FAMILIES_6
            if all(which_complete(root, f, w) for w in r6.ENDPOINT_WHICH_6)]
    gate = gate1b(root, done)
    gate.update({"host_sha256": host["sha256"], "git_sha": sha,
                 "prereg_tag": r6.PREREG_TAG_6})
    if todo or not r6.gate1b_path(root).exists():
        # a run that read nothing leaves the record of the run that did
        r6.write_json(r6.gate1b_path(root), gate)
    if not gate["pass"]:
        r6.endpoint_halt_path(root).write_text("\n".join(gate["failures"]) + "\n")
        raise RuntimeError(f"GATE 1(b) FIRED: {gate['failures'][:3]}")
    cm.exit_gate(r6.endpoint_halt_path(root), frozen_check=frozen_check)
    return gate


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(EXP6))
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--family", action="append", choices=fm.FAMILIES_6)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    out = run(root=Path(a.root), device=a.device, families=a.family,
              dry_run=a.dry_run)
    print(out if a.dry_run else f"gate 1(b): pass={out['pass']} over "
                                f"{sorted(out['families'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
