# experiments/exp6/run/seal_endpoint_6.py
"""Seal the endpoint stage (design §3.4, §4), on the Mac, after the
endpoint records have been pulled from the box: every record MEASURED
against what it must be, gate 1(b) re-derived from the bytes, then the
RUNG SETS by rule — R_f is the rungs of the new battery whose stage-1
endpoint count clears 2d's bar against the rung's floor — and the table
of files the seal names. Written ONCE. The power record is written
next (power_6.py); the tag `exp6-endpoint-sealed` binds both and every
file named here.

    python -m experiments.exp6.run.seal_endpoint_6
"""
from __future__ import annotations

import sys
from pathlib import Path

EXP6 = Path(__file__).resolve().parents[1]
REPO = EXP6.parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp6 import battery_6 as b6  # noqa: E402
from experiments.exp6 import families_6 as fm  # noqa: E402
from experiments.exp6 import floors_6 as fl  # noqa: E402
from experiments.exp6 import records_6 as r6  # noqa: E402
from experiments.exp6 import referents_6 as rf  # noqa: E402
from experiments.exp6.run import _common_6 as cm  # noqa: E402

RULE_6 = ("R_f = the rungs of RUNGS_6 whose stage1_final count clears 2d's "
          "binomial bar (alpha .01) against the rung's floor; the anchors and "
          "the control are never in a rung set")


def load_hosts(root) -> tuple:
    """(failures, {sha256: record}) over results/hosts/."""
    bad, out = [], {}
    d = cm.hosts_dir(root)
    for p in sorted(d.glob("*.json")) if d.is_dir() else []:
        rec = r6.read_json(p)
        f = cm.host_failures(rec)
        if p.name != f"{str(rec.get('sha256'))[:12]}.json":
            f.append(f"host record {p.name}: not named by its own sha256")
        bad += [f"6 host {p.name}: {m}" for m in f]
        out[rec.get("sha256")] = rec
    return bad, out


def load_which(root, family, which, *, battery, man, seal_sha256, hosts) -> tuple:
    """(failures, {"load", "records"}) for one model load of the
    endpoint stage, through the checks the analyzer runs."""
    label = f"6 endpoint {family}/{which}"
    lp = r6.endpoint_load_path(root, family, which)
    if not lp.is_file():
        return [f"{label}: load record missing"], None
    load = r6.read_json(lp)
    key = fm.endpoint_step(family) if which == "stage1_final" else fm.INIT
    entry = dict(fm.entry(family, man, key))
    if which == "stage1_final":
        entry["kind"] = "thin-loader"
    bad = r6.load_record_failures(load, family=family, key=which, entry=entry)
    if load.get("host_sha256") not in hosts:
        bad.append(f"{label}: host {str(load.get('host_sha256'))[:12]} has no "
                   f"host record")
    bad += rf.digest_failures(load, family, which,
                              label=f"6 gate 1(d) {family}/{which}")
    recs = {}
    for rung in b6.ALL_RUNGS_6:
        rp = r6.endpoint_record_path(root, family, which, rung)
        if not rp.is_file():
            bad.append(f"{label}/{rung}: record missing")
            continue
        rec = r6.read_json(rp)
        bad += r6.unit_record_failures(
            rec, family=family, rung=rung, cap=battery[rung], load=load,
            seal_sha256=seal_sha256, host_sha256=load.get("host_sha256"),
            which=which)
        recs[rung] = rec
    return bad, {"load": load, "records": recs}


def collect(root, *, battery, seal_sha256) -> tuple:
    bad, hosts = load_hosts(root)
    out = {}
    for f in fm.FAMILIES_6:
        man = fm.manifest(f)
        out[f] = {}
        for w in r6.ENDPOINT_WHICH_6:
            fb, got = load_which(root, f, w, battery=battery, man=man,
                                 seal_sha256=seal_sha256, hosts=hosts)
            bad += fb
            if got is not None and len(got["records"]) == len(b6.ALL_RUNGS_6):
                out[f][w] = got
    return bad, out, hosts


def gate1b_rederived(ep: dict) -> dict:
    """Gate 1(b) from the records: the anchors on the box against the
    Mac's committed counts, the endpoint and the init referent."""
    counts, short = {}, []
    for f in fm.FAMILIES_6:
        if set(ep.get(f, {})) != set(r6.ENDPOINT_WHICH_6):
            short.append(f"6 gate 1(b) {f}: the endpoint stage is incomplete")
            continue
        counts[f] = {w: {r: int(ep[f][w]["records"][r]["correct"])
                         for r in b6.ANCHORS_6} for w in r6.ENDPOINT_WHICH_6}
    rec = rf.gate1b_record(counts)
    rec["failures"] = short + rec["failures"]
    rec["pass"] = not rec["failures"]
    return rec


GATE1B_FIELDS = ("families", "tolerance_per_rung", "pass", "failures")


def gate1b_failures(root, ep, hosts) -> list:
    """The runner's gate record against the re-derivation."""
    p = r6.gate1b_path(root)
    if not p.is_file():
        return ["6 gate 1(b): record missing"]
    rec, redo = r6.read_json(p), gate1b_rederived(ep)
    bad = list(redo["failures"])
    if rec.get("host_sha256") not in hosts:
        bad.append(f"6 gate 1(b): host {str(rec.get('host_sha256'))[:12]} has no "
                   f"host record")
    for k in GATE1B_FIELDS:
        if rec.get(k) != redo[k]:
            bad.append(f"6 gate 1(b): the record's {k} does not re-derive from "
                       f"the endpoint records")
    if rec.get("prereg_tag") != r6.PREREG_TAG_6:
        bad.append("6 gate 1(b): prereg_tag")
    return bad


def clears_heuristic(k: int, h: dict):
    """Does a count clear the rung's HEURISTIC floor as well (plan delta
    B-22)? None where the rung has no guesser; False where a guesser
    scores every item, which no count beats."""
    hf = h["heuristic_floor"]
    if hf is None:
        return None
    return bool(hf < 1.0 and fl.clears(int(k), b6.N_ITEMS, hf)["significant"])


def derive_rung_sets(ep: dict, floors: dict, heuristics: dict) -> dict:
    """R_f by the ruled rule (2d's bar against the rule's floor), and
    beside it R_heuristic: the rungs of R_f whose count also clears the
    heuristic floor. The primary reads R_f; a named sensitivity reads
    R_heuristic (plan delta B-31). Both are sealed before any sweep."""
    fams = {}
    for f in fm.FAMILIES_6:
        recs = ep[f]["stage1_final"]["records"]
        rows, keep, beyond = {}, [], []
        for r in b6.RUNGS_6:
            k = int(recs[r]["correct"])
            bar = fl.clears(k, b6.N_ITEMS, floors[r]["floor"])
            over = clears_heuristic(k, heuristics[r])
            rows[r] = {"count": k, "floor": floors[r]["floor"],
                       "p": bar["p"], "clears": bool(bar["significant"]),
                       "heuristic": heuristics[r]["heuristic"],
                       "heuristic_floor": heuristics[r]["heuristic_floor"],
                       "clears_heuristic": over}
            if bar["significant"]:
                keep.append(r)
                if over is not False:
                    beyond.append(r)
        fams[f] = {
            "R": keep, "R_heuristic": beyond,
            "flat": [r for r in b6.RUNGS_6 if r not in keep],
            "rungs": rows,
            "anchors": {r: int(recs[r]["correct"]) for r in b6.ANCHORS_6},
            "control": int(recs[b6.CONTROL_6]["correct"]),
            "init": {r: int(ep[f]["init"]["records"][r]["correct"])
                     for r in b6.ALL_RUNGS_6},
            "n_grid": len(fm.grid(f)), "endpoint_step": fm.endpoint_step(f)}
    return fams


def named_files(root, hosts_used) -> list:
    """The relative paths the seal names: every endpoint record, the
    load records, the gate record, and the host records the endpoint
    records name (a sweep host, written later, is not among them)."""
    out = [r6.gate1b_path(root)]
    out += [cm.hosts_dir(root) / f"{h[:12]}.json" for h in sorted(hosts_used)]
    for f in fm.FAMILIES_6:
        for w in r6.ENDPOINT_WHICH_6:
            out.append(r6.endpoint_load_path(root, f, w))
            out += [r6.endpoint_record_path(root, f, w, r) for r in b6.ALL_RUNGS_6]
    return [str(Path(p).relative_to(root)) for p in out]


def seal_paths(root) -> list:
    """Everything `exp6-endpoint-sealed` binds."""
    named = r6.read_json(r6.rung_sets_path(root))["sealed_files"]
    return [Path(root) / rel for rel in named] + [r6.rung_sets_path(root),
                                                  r6.power_path(root)]


def endpoint_sha256(root) -> str:
    """The composite sha of the sealed endpoint stage, stamped on every
    sweep record."""
    return r6.composite_sha({str(Path(p).relative_to(root)): r6.sha256_file(p)
                             for p in seal_paths(root)})


def rung_sets_failures(rec: dict, ep: dict, floors: dict, heuristics: dict,
                       root) -> list:
    """The committed rung sets against their own re-derivation, and the
    file table against the disk (the analyzer's check)."""
    bad = []
    if rec.get("families") != derive_rung_sets(ep, floors, heuristics):
        bad.append("6 rung sets: the record does not re-derive from the endpoint "
                   "records and the floors")
    if rec.get("rule") != RULE_6 or rec.get("prereg_tag") != r6.PREREG_TAG_6:
        bad.append("6 rung sets: rule or prereg_tag")
    hosts_used = {ep[f][w]["load"].get("host_sha256") for f in ep for w in ep[f]}
    want = named_files(root, hosts_used)
    if rec.get("sealed_files") != want:
        bad.append("6 rung sets: sealed_files is not the endpoint stage's file table")
    for rel, sha in (rec.get("sealed_sha256") or {}).items():
        p = Path(root) / rel
        if not p.is_file() or r6.sha256_file(p) != sha:
            bad.append(f"6 rung sets: {rel} is not the sealed file")
    if set(rec.get("sealed_sha256") or {}) != set(want):
        bad.append("6 rung sets: sealed_sha256 does not cover sealed_files")
    return bad


def seal(root=EXP6, *, tag_exists=None, blob_sha=None, blobs_bound=None,
         frozen_check=None) -> dict:
    from experiments.exp6.run import endpoint_6 as ep_run
    cm.gates(tag_exists=tag_exists, blob_sha=blob_sha, frozen_check=frozen_check)
    pseal = ep_run.require_predictor_seal(root, tag_exists=tag_exists,
                                          blobs_bound=blobs_bound)
    if r6.rung_sets_path(root).exists():
        raise RuntimeError("the rung sets exist — the endpoint stage is sealed ONCE")
    cm.refuse_if_halted(root)
    battery = b6.load_battery_6()
    floors = fl.floor_table_6(battery)
    fl.check_floor_pins_6(floors)
    heuristics = fl.heuristic_table_6(battery)
    fl.check_heuristic_pins_6(heuristics)
    bad, ep, hosts = collect(root, battery=battery, seal_sha256=pseal["sha256"])
    if not bad:
        bad += gate1b_failures(root, ep, hosts)
    if bad:
        raise RuntimeError(f"cannot seal: {len(bad)} failure(s): {bad[:5]}")
    cm.exit_gate(r6.endpoint_halt_path(root), frozen_check=frozen_check)
    hosts_used = {ep[f][w]["load"]["host_sha256"] for f in ep for w in ep[f]}
    named = named_files(root, hosts_used)
    rec = {"tag": r6.ENDPOINT_SEAL_TAG_6, "prereg_tag": r6.PREREG_TAG_6,
           "rule": RULE_6, "families": derive_rung_sets(ep, floors, heuristics),
           "predictor_sha256": pseal["sha256"], "sealed_files": named,
           "sealed_sha256": {rel: r6.sha256_file(Path(root) / rel) for rel in named},
           "git_sha": cm.p6.git_sha()}
    r6.write_json(r6.rung_sets_path(root), rec)
    return rec


if __name__ == "__main__":
    out = seal()
    for f, row in out["families"].items():
        print(f"{f:12s} R_f {len(row['R']):2d} of {len(b6.RUNGS_6)}: {row['R']}")
        gone = [r for r in row["R"] if r not in row["R_heuristic"]]
        print(f"{'':12s} not beyond the heuristic floor: {gone}")
