# experiments/exp6/run/seal_predictor_6.py
"""Seal the predictor stage (design §3.3): every unit present, every
record MEASURED against what it must be, gate 1-P re-derived from the
bytes with its coverage, then one file table and its composite sha.
Refuses to seal over a halt marker or a missing unit (5b F-1)."""
from __future__ import annotations

import sys
from pathlib import Path

EXP6 = Path(__file__).resolve().parents[1]
REPO = EXP6.parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp6 import battery_6 as b6  # noqa: E402
from experiments.exp6 import records_6 as r6  # noqa: E402
from experiments.exp6 import referents_6 as rf  # noqa: E402
from experiments.exp6.run import _common_6 as cm  # noqa: E402


def load_unit(root, predictor, tier, rung, cap) -> tuple:
    """(failures, {"record","rows","bits"}) for one unit, through the
    same checks the analyzer runs."""
    t = r6.tier_shape(predictor, tier)
    dpath = r6.tier_draws_path(root, predictor, tier, rung)
    rpath = r6.tier_record_path(root, predictor, tier, rung)
    if not rpath.is_file() or not dpath.is_file():
        return [f"6 predictor {predictor}/{tier}/{rung}: unit missing"], None
    rec = r6.read_json(rpath)
    rows = r6.read_draws(dpath, seeds=t["seeds"], dps=t["dps"])
    bits = r6.bits_of(rows, cap, seeds=t["seeds"])
    bad = r6.tier_record_failures(rec, predictor=predictor, tier=tier, rung=rung,
                                  cap=cap, bits=bits,
                                  model_pin=rf.model_pin(predictor),
                                  draws_sha256=r6.sha256_file(dpath))
    return bad, {"record": rec, "rows": rows, "bits": bits}


def gate1p(root, units: dict) -> tuple:
    """Gate 1-P RE-DERIVED: each gated unit's draws against the
    committed stream, byte for byte, coverage counted."""
    bad, out = [], {}
    for p, t, r in rf.gated_units():
        u = units.get((p, t, r))
        if u is None:
            bad.append(f"6 gate 1-P {p}/{t}/{r}: unit missing")
            continue
        sh = r6.tier_shape(p, t)
        d = r6.diff_draws(u["rows"], rf.committed_rows(p, t, r), seeds=sh["seeds"])
        d["committed_draws_sha256"] = r6.sha256_file(rf.committed_draws_path(p, t, r))
        want = b6.N_ITEMS * sh["k"]
        if d["n_diffs"] or d["items_compared"] != b6.N_ITEMS or \
                d["draws_compared"] != want:
            bad.append(f"6 gate 1-P {p}/{t}/{r}: {d['n_diffs']} diffs over "
                       f"{d['draws_compared']} of {want} draws")
        out[f"{p}/{t}/{r}"] = d
    return bad, out


def collect(root) -> tuple:
    bad, units = [], {}
    battery = b6.load_battery_6()
    for p, t, r in r6.predictor_units():
        f, u = load_unit(root, p, t, r, battery[r])
        bad += f
        if u is not None:
            units[(p, t, r)] = u
    return bad, units


def file_table(root) -> dict:
    base = r6.results(root) / "predictor"
    skip = {r6.seal_path(root).resolve()}
    return {str(p.relative_to(root)): r6.sha256_file(p)
            for p in sorted(base.rglob("*"))
            if p.is_file() and p.resolve() not in skip}


def seal(root=EXP6, *, tag_exists=None, blob_sha=None, frozen_check=None) -> dict:
    cm.gates(tag_exists=tag_exists, blob_sha=blob_sha, frozen_check=frozen_check)
    if r6.seal_path(root).exists():
        raise RuntimeError("the predictor is already sealed")
    cm.refuse_if_halted(root)
    bad, units = collect(root)
    g_bad, gate = gate1p(root, units)
    bad += g_bad
    if bad:
        raise RuntimeError(f"cannot seal: {len(bad)} failure(s): {bad[:5]}")
    cm.exit_gate(r6.predictor_halt_path(root), frozen_check=frozen_check)
    r6.write_json(r6.gate1p_path(root), {"units": gate, "prereg_tag": r6.PREREG_TAG_6,
                                         "git_sha": cm.p6.git_sha()})
    files = file_table(root)
    counts = {p: {r: r6.counts_of(units[(p, "main", r)]["bits"])
                  for r in r6.tier_shape(p, "main")["rungs"]}
              for p in r6.PREDICTORS_6}
    rec = {"tag": r6.PREDICTOR_SEAL_TAG_6, "files": files,
           "sha256": r6.composite_sha(files), "counts": counts,
           "n_units": len(units),
           "models": {p: rf.model_pin(p) for p in r6.PREDICTORS_6}}
    r6.write_json(r6.seal_path(root), rec)
    return rec


if __name__ == "__main__":
    out = seal()
    print(out["tag"], out["sha256"], out["n_units"], "units,", len(out["files"]),
          "files")
