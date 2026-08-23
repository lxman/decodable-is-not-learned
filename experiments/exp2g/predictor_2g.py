# experiments/exp2g/predictor_2g.py
"""Exp 2g predictor (design §3, the seal): one committed file —
for every predictor rung, eval item, probe size and mode, the probe's
log-probability of the item's true label at the CV-chosen site (and
at 2f's eval-chosen site as the printed sensitivity), the strata, and
the sha of every input — tagged `exp2g-predictor-sealed` BEFORE any
checkpoint loads. The runner and the analyzer refuse anything else.

Gate P (design §5) has two halves: the collector's continuity records
(collect_eval_2g) and, here, 2f's four committed per-site eval
accuracies reproduced EXACTLY by this module's probe code on 2f's
committed activation files — probing is deterministic on this stack."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

EXP2G = Path(__file__).resolve().parent
if str(EXP2G.parent.parent) not in sys.path:
    sys.path.insert(0, str(EXP2G.parent.parent))

from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp2g import collect_eval_2g as ce  # noqa: E402
from experiments.exp2g import labels_2g as lb  # noqa: E402
from experiments.exp2g import probe_2g as pg  # noqa: E402
from experiments.exp2g import strata_2g as sg  # noqa: E402
from experiments.exp2c.run.screen import _load_activation_map  # noqa: E402

REPO = bg.REPO
PREDICTOR_REL = "experiments/exp2g/results/predictor/predictor.json"
VERDICT_2F_SHA256 = \
    "79c31e0c41bf30928a34b0032c3f56c929f9edcc16c3b147b1e38554a577f8c0"


# ------------------------------------------------------------- loaders

def load_eval_acts(root, size, mode, rung, cap, *, n_layers):
    p = bg.eval_npz_path(root, size, mode, rung)
    act, y, meta = _load_activation_map(Path(p))
    want = ce.eval_meta(size=size, mode=mode, rung=rung, n_layers=n_layers, stack=None)
    for k, v in want.items():
        if k == "stack":
            continue
        if meta.get(k) != v:
            raise ValueError(f"{p}: {k} = {meta.get(k)!r}, expected {v!r}")
    answers = [str(it["answer"]) for it in cap["eval_items"]]
    if [str(v) for v in y] != answers:
        raise ValueError(f"{p}: y is not the committed answer list")
    X0 = next(iter(act.values()))
    if X0.shape[0] != bg.N_ITEMS:
        raise ValueError(f"{p}: {X0.shape[0]} rows")
    return pg.thin(act), answers, meta


# --------------------------------------------------------------- gate P

def check_2f_gate() -> dict:
    """2f's committed per-site eval accuracies (trained, 4 cells)
    reproduced exactly by pb.eval_probe_sites on 2f's committed files."""
    from experiments.exp2f import analyze_2f as a2f
    from experiments.exp2f import labels_2f as lb2f
    from experiments.exp2f import probe_2f as pb
    vpath = a2f.EXP2F / "results" / "verdict.json"
    if bg.sha256_file(vpath) != VERDICT_2F_SHA256:
        raise ValueError("2f's verdict.json is not the committed file")
    v = json.loads(vpath.read_text())
    out = {}
    for rung in lb2f.RUNGS:
        cap = bg.load_battery([rung])[rung]
        kind = lb2f.PRIMARY[rung]
        for size in lb2f.SIZES:
            act_tr, _, meta = a2f.load_probe_acts(
                a2f.mk.probe_npz_path(size, "trained", rung), cap,
                sha_pin=a2f.PROBE_NPZ_SHA_PIN[(rung, size, "trained")])
            ev, _, _ = a2f.load_eval_acts(a2f.EXP2F, size, "trained", rung, cap,
                                          n_layers=int(meta["n_layers"]))
            y_tr = [lb2f.answer_label(kind, it["answer"]) for it in cap["probe_items"]]
            y_ev = lb2f.eval_labels(cap, kind)
            res = pb.eval_probe_sites(act_tr, y_tr, ev, y_ev, sorted(act_tr))
            want = v["cells"][f"{rung}/{size}"]["probe"]["trained"]["per_site"]
            got = {pg.site_key(s): res[s]["acc"] for s in res}
            for k, w in want.items():
                if k not in got or abs(got[k] - w["acc"]) > 1e-12:
                    raise ValueError(f"gate P {rung}/{size} site {k}: got "
                                     f"{got.get(k)}, 2f committed {w['acc']}")
            out[f"{rung}/{size}"] = "PASS"
    return out


# ------------------------------------------------------------- builder

def _git_sha() -> str:
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO, capture_output=True,
                          text=True).stdout.strip()


def build_predictor(*, root=EXP2G, probe_root=None, eval_root=None, write=True,
                    with_2f_gate=True) -> dict:
    eval_root = eval_root or root
    bg.check_frozen_imports_2g()
    battery = bg.load_battery(bg.PREDICTOR_RUNGS)
    gates = {"labels": lb.check_label_gates(battery),
             "class_coverage": {r: "PASS" for r in lb.check_class_coverage(battery)},
             "rung_sets": bg.check_rung_sets(bg.load_floors())}
    table = sg.build_table(battery)
    gates["strata"] = sg.check_strata_pins(table)
    cont = {}
    for size in bg.PROBE_SIZES:
        for mode in bg.MODES:
            rec = json.loads(bg.continuity_path(eval_root, size, mode).read_text())
            bad = ce.continuity_failures(rec, size=size, mode=mode)
            if bad:
                raise ValueError("; ".join(bad))
            cont[f"{size}/{mode}"] = "PASS"
    gates["continuity"] = cont
    if with_2f_gate:
        gates["gate_2f"] = check_2f_gate()
    cells, inputs = {}, {"probe_npz": {}, "eval_npz": {}, "items": {}, "continuity": {}}
    for rung in bg.PREDICTOR_RUNGS:
        cap = battery[rung]
        inputs["items"][rung] = cap["items_sha256"]
        cells[rung] = {}
        y_train = lb.probe_labels(cap, rung)
        y_eval = lb.eval_labels(cap, rung)
        for size in bg.PROBE_SIZES:
            cells[rung][size] = {}
            for mode in bg.MODES:
                pp = bg.probe_npz_path(size, mode, rung, probe_root=probe_root)
                act_tr, _, meta = bg.load_probe_acts(
                    pp, cap, sha_pin=(bg.PROBE_NPZ_SHA_PIN[(rung, size, mode)]
                                      if probe_root is None else None))
                ev, _, _ = load_eval_acts(eval_root, size, mode, rung, cap,
                                          n_layers=int(meta["n_layers"]))
                cell = pg.score_cell(act_tr, y_train, ev, y_eval)
                cells[rung][size][mode] = cell
                inputs["probe_npz"][f"{rung}/{size}/{mode}"] = bg.sha256_file(pp)
                inputs["eval_npz"][f"{rung}/{size}/{mode}"] = \
                    bg.sha256_file(bg.eval_npz_path(eval_root, size, mode, rung))
                print(f"[2g predictor] {rung}/{size}/{mode}: site {cell['site']} "
                      f"cv {cell['cv']['best_acc']:.3f} eval {cell['eval_acc']:.3f}",
                      flush=True)
    for size in bg.PROBE_SIZES:
        for mode in bg.MODES:
            inputs["continuity"][f"{size}/{mode}"] = \
                bg.sha256_file(bg.continuity_path(eval_root, size, mode))
    rec = {"rungs": list(bg.PREDICTOR_RUNGS), "sizes": list(bg.PROBE_SIZES),
           "modes": list(bg.MODES), "primary_size": bg.PRIMARY_SIZE,
           "cells": cells, "strata": sg.to_json(table),
           "label_kinds": {r: lb.KIND_OF[r] for r in bg.PREDICTOR_RUNGS},
           "gates": gates, "inputs": inputs, "stack": ce.stack_info(),
           "git_sha": _git_sha()}
    if write:
        p = bg.predictor_path(root)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(rec, indent=1, sort_keys=True))
        bg.strata_path(root).write_text(json.dumps(sg.to_json(table), indent=1,
                                                   sort_keys=True))
        bg.predictor_sha_path(root).write_text(f"{bg.sha256_file(p)}  predictor.json\n")
    return rec


# ------------------------------------------------------------ the seal

def predictor_sha(root=EXP2G) -> str:
    return bg.sha256_file(bg.predictor_path(root))


def git_tag_exists(tag: str) -> bool:
    out = subprocess.run(["git", "tag", "--list", tag], cwd=REPO,
                         capture_output=True, text=True)
    return tag in out.stdout.split()


def git_blob_sha256(tag: str, relpath: str):
    out = subprocess.run(["git", "show", f"{tag}:{relpath}"], cwd=REPO,
                         capture_output=True)
    if out.returncode != 0:
        return None
    return hashlib.sha256(out.stdout).hexdigest()


def require_seal(root=EXP2G, *, tag_exists=None, blob_sha=None) -> dict:
    """The two-stage lock, in code: the seal tag exists, the predictor
    file on disk hashes to the blob the tag carries, and the sha file
    agrees. Raises RuntimeError otherwise."""
    tag_exists = tag_exists or git_tag_exists
    blob_sha = blob_sha or git_blob_sha256
    if not tag_exists(bg.SEAL_TAG):
        raise RuntimeError(f"refusing: the seal tag {bg.SEAL_TAG!r} does not exist — "
                           f"the predictor must be committed and tagged first")
    p = bg.predictor_path(root)
    if not p.is_file():
        raise RuntimeError(f"refusing: {p} is missing")
    got = bg.sha256_file(p)
    at_tag = blob_sha(bg.SEAL_TAG, PREDICTOR_REL)
    if at_tag != got:
        raise RuntimeError(f"refusing: predictor sha {got} differs from the sealed "
                           f"blob {at_tag}")
    sp = bg.predictor_sha_path(root)
    if not sp.is_file() or sp.read_text().split()[0] != got:
        raise RuntimeError("refusing: predictor_sha256.txt disagrees with the file")
    return {"tag": bg.SEAL_TAG, "sha256": got}


def load_predictor(path, *, sha_pin) -> dict:
    raw = Path(path).read_bytes()
    got = hashlib.sha256(raw).hexdigest()
    if sha_pin is not None and got != sha_pin:
        raise ValueError(f"{path} hashes to {got}, pinned {sha_pin}")
    rec = json.loads(raw)
    if rec.get("rungs") != list(bg.PREDICTOR_RUNGS) or \
            rec.get("sizes") != list(bg.PROBE_SIZES) or rec.get("modes") != list(bg.MODES):
        raise ValueError(f"{path}: not the frozen rung/size/mode layout")
    for r in bg.PREDICTOR_RUNGS:
        for s in bg.PROBE_SIZES:
            for m in bg.MODES:
                c = rec["cells"][r][s][m]
                if len(c["scores"]) != bg.N_ITEMS or \
                        len(c["eval_rule"]["scores"]) != bg.N_ITEMS:
                    raise ValueError(f"{path}: {r}/{s}/{m} scores are not "
                                     f"{bg.N_ITEMS} long")
    table = sg.from_json(rec["strata"])
    sg.check_strata_pins(table)
    rec["sha256"] = got
    return rec


def cell_scores(pred: dict, rung, size, mode, *, rule="cv") -> np.ndarray:
    c = pred["cells"][rung][size][mode]
    return np.asarray(c["scores"] if rule == "cv" else c["eval_rule"]["scores"],
                      dtype=np.float64)


if __name__ == "__main__":
    rec = build_predictor()
    print("predictor sha256", predictor_sha())
