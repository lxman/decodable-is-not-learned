"""Verify every committed referent Exp 3's frozen tree will read (doc
Open item 8, and the value-existence groundwork for the freeze).

Checks, all against committed records:

1. Gate-2 byte referents: 3b's 16 probe-size greedy cells load through
   `load_gate2_referents` (500 continuations/labels/answers each, path/
   content agreement, twin seed discipline, per-cell items_sha256 and
   max_new_tokens present with values).
2. Item-file pins: each rung's items_sha256 (agreeing across its four 3b
   cells) equals the sha256 of the item file exp3 will actually load —
   2c's tree for rev_string7/ctrl_copy/clock24_d999, 2b's for
   reverse_string. This is §4 row 1, checked at build so the campaign
   cannot discover a moved item file.
3. Gate-1 anchors: the 2c inclusion records carry ctrl_copy full-string
   480/500 (410m) and 490/500 (1b) trained; and exp3's own ported
   first_char, run over 3b's committed ctrl_copy trained continuations,
   reproduces 497/500 = .9940 at both probe sizes. The second half
   validates the port against a closed committed number — it reads no
   model and creates no new quantity.
4. Floors: the 3a file matches analyze_3's sha pin and survives the
   recompute-assert (load_floors is executed, not re-implemented).
5. Probe margins: load_probe_margins executes — values in (0,1) and
   rounding to the doc's 4dp quotes.
6. Twin hash referents: 3b's referent_check.json carries a seed-0 state
   hash for both probe sizes.
7. (--construct) The probe-size untrained twins CONSTRUCT at
   untrained_seed=0 on CPU, twice per size, the two state dicts hash
   identically, AND the hash equals 3b's recorded one — the twins exp3's
   campaign will build are byte-the-same twins 3b's cells scored.

NO mass or sampling quantity is computed here for any real cell or
model (build-session invariant; the tag does not exist yet).

Output committed as `referent_check.json`.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

EXP3 = Path(__file__).resolve().parent
EXPERIMENTS = EXP3.parent
if str(EXPERIMENTS.parent) not in sys.path:
    sys.path.insert(0, str(EXPERIMENTS.parent))

from experiments.exp3.analyze_3 import (  # noqa: E402
    GATE1_FIRST_CHAR_REFERENT, GATE1_INCLUSION_REFERENT, ITEMS_2B, ITEMS_2C,
    POSITIVE_CONTROL, PROBE_SIZES, RUNGS, RUNGS_2B, items_sha_referents,
    load_floors, load_gate2_referents, load_probe_margins,
    load_twin_hash_referents, score_cell,
)

OUT = EXP3 / "referent_check.json"
INCLUSION_2C = EXPERIMENTS / "exp2c" / "results" / "inclusion"


def check_gate2_and_item_pins(report: list) -> dict:
    refs = load_gate2_referents()   # raises on anything malformed
    report.append({"check": "gate-2 byte referents load (16 cells)",
                   "ok": True, "n_cells": len(refs)})
    shas = items_sha_referents(refs)
    for rung, want in sorted(shas.items()):
        p = (ITEMS_2B if rung in RUNGS_2B else ITEMS_2C) / f"{rung}.json"
        got = hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None
        report.append({"check": f"item file pin {rung}", "ok": got == want,
                       "path": str(p), "sha256": got, "want": want})
    return refs


def check_gate1_anchors(report: list, refs: dict) -> None:
    for size in PROBE_SIZES:
        p = INCLUSION_2C / f"{size}_trained" / f"{POSITIVE_CONTROL}.json"
        entry = {"check": f"gate-1 inclusion anchor {size}", "ok": False,
                 "path": str(p)}
        if p.is_file():
            rec = json.loads(p.read_text())
            entry.update(correct=rec.get("correct"), n=rec.get("n"),
                         want=GATE1_INCLUSION_REFERENT[size])
            entry["ok"] = (rec.get("correct") == GATE1_INCLUSION_REFERENT[size]
                           and rec.get("n") == 500)
        report.append(entry)

        ref = refs[(POSITIVE_CONTROL, size, "trained")]
        got = score_cell(ref["continuations"], ref["probe_labels"])
        want = GATE1_FIRST_CHAR_REFERENT[size]
        report.append({"check": f"gate-1 first-char recompute {size}",
                       "ok": got["correct"] == want and got["n"] == 500,
                       "correct": got["correct"], "want": want,
                       "acc": got["acc"]})


def check_floors(report: list) -> None:
    try:
        floors = load_floors()   # sha pin + recompute-assert, executed
        report.append({"check": "floors sha pin + recompute-assert",
                       "ok": True,
                       "primaries": {r: floors[r]["primary"] for r in RUNGS}})
    except Exception as exc:  # noqa: BLE001
        report.append({"check": "floors sha pin + recompute-assert",
                       "ok": False, "error": repr(exc)})


def check_margins(report: list) -> None:
    try:
        m = load_probe_margins()
        report.append({"check": "probe margins match doc 4dp quotes",
                       "ok": True, "margins": m})
    except Exception as exc:  # noqa: BLE001
        report.append({"check": "probe margins match doc 4dp quotes",
                       "ok": False, "error": repr(exc)})


def check_twin_hash_referents(report: list) -> dict:
    try:
        h = load_twin_hash_referents()
        report.append({"check": "3b twin state-hash referents present",
                       "ok": True, "hashes": h})
        return h
    except Exception as exc:  # noqa: BLE001
        report.append({"check": "3b twin state-hash referents present",
                       "ok": False, "error": repr(exc)})
        return {}


def _state_hash(model) -> str:
    h = hashlib.sha256()
    sd = model.state_dict()
    for k in sorted(sd):
        h.update(k.encode())
        h.update(sd[k].cpu().numpy().tobytes())
    return h.hexdigest()


def check_twin_construction(report: list, want_hashes: dict) -> None:
    """3b's construction, verbatim, on CPU (where from_config's seeded
    init happens regardless of the target device), twice per size — plus
    the continuity requirement: equality with 3b's recorded hash."""
    from models import load_pythia  # noqa: PLC0415 — needs exp2b on sys.path

    for size in PROBE_SIZES:
        hashes = []
        for _ in range(2):
            _, model = load_pythia(size, untrained=True, seed=0, device="cpu")
            hashes.append(_state_hash(model))
            del model
        want = want_hashes.get(size)
        report.append({"check": f"untrained twin constructs {size} seed=0",
                       "ok": hashes[0] == hashes[1] == want,
                       "state_sha256": hashes[0],
                       "deterministic": hashes[0] == hashes[1],
                       "matches_3b_record": hashes[0] == want,
                       "want": want})


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--construct", action="store_true",
                    help="also construct the probe-size untrained twins "
                         "and require equality with 3b's recorded hashes "
                         "(loads torch; a few minutes)")
    a = ap.parse_args(argv)

    # the campaign's sys.path order (3b's, order load-bearing): exp2b
    # first, exp2c inserted after so it wins — models resolves to exp2b.
    for _p in (EXPERIMENTS / "exp2b", EXPERIMENTS / "exp2c"):
        if str(_p) not in sys.path:
            sys.path.insert(0, str(_p))

    report: list[dict] = []
    refs = check_gate2_and_item_pins(report)
    check_gate1_anchors(report, refs)
    check_floors(report)
    check_margins(report)
    want_hashes = check_twin_hash_referents(report)
    if a.construct:
        check_twin_construction(report, want_hashes)

    bad = [r for r in report if not r["ok"]]
    out = {"n_checks": len(report), "n_failed": len(bad),
           "all_ok": not bad, "constructed_twins": bool(a.construct),
           "checks": report}
    OUT.write_text(json.dumps(out, indent=1))
    print(f"{len(report)} checks, {len(bad)} failed -> {OUT}")
    for r in bad:
        print("  FAIL", r)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
