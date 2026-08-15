"""Verify every committed referent 3b's frozen tree will read (open item 7,
and the value-existence groundwork for freeze rule 3).

Checks, all against committed records:

1. The 16 probe-size inclusion records exist, carry the design §4 values
   exactly (ctrl_copy 480/490 trained, reversal 0×8, clock24_d999 18/24
   trained, all untrained 0), and their `sha` matches the pinned revision
   3b's runner will load (`models.PYTHIA_SHAS`) with `untrained_seed` 0 on
   untrained records — the twins 3b constructs are the twins the inclusion
   screen scored.
2. The 24 exp3a records — gate 3's byte referents — are STRUCTURALLY sound:
   500 continuations, labels and answers each, path/content agreement,
   untrained_seed 0 where untrained. Structure only: this script computes
   NO first-character quantity. That number does not exist yet for any
   cell, and does not exist until after the exp3b-preregistered tag.
3. The floors file matches analyze_3b's sha pin and survives the
   recompute-assert (load_floors is executed, not re-implemented).
4. The 20 m3 probe seed records behind probe_margins.json exist.
5. The probe-size untrained twins CONSTRUCT at untrained_seed=0
   (`--construct`): load_pythia(size, untrained=True, seed=0) on CPU, twice
   per size, asserting the two state dicts hash identically — the twin is a
   deterministic function of (config sha, seed), which is what lets 2b/2c's
   untrained inclusion records stand as referents for cells 3b collects.

Output committed as `referent_check.json`.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

EXP3B = Path(__file__).resolve().parent
EXPERIMENTS = EXP3B.parent
if str(EXPERIMENTS.parent) not in sys.path:
    sys.path.insert(0, str(EXPERIMENTS.parent))

from experiments.exp3b.analyze_3b import (  # noqa: E402
    BYTE_REFERENT_ROOT, EVAL_SIZES, FLOORS_PATH, FLOORS_SHA256, MODES,
    PROBE_SIZES, RUNGS, load_floors, load_inclusion_referents,
)

OUT = EXP3B / "referent_check.json"

# design §4's table, verbatim: (rung, size, mode) -> committed correct/500
DESIGN_INCLUSION = {}
for _r in RUNGS:
    for _s in PROBE_SIZES:
        DESIGN_INCLUSION[(_r, _s, "untrained")] = 0
        DESIGN_INCLUSION[(_r, _s, "trained")] = 0
DESIGN_INCLUSION[("ctrl_copy", "410m", "trained")] = 480
DESIGN_INCLUSION[("ctrl_copy", "1b", "trained")] = 490
DESIGN_INCLUSION[("clock24_d999", "410m", "trained")] = 18
DESIGN_INCLUSION[("clock24_d999", "1b", "trained")] = 24

M3_TREES = {"rev_string7": EXPERIMENTS / "exp2c" / "results" / "probes" / "m3",
            "reverse_string": EXPERIMENTS / "exp2b" / "results" / "probes" / "m3"}


def check_inclusion(report: list) -> None:
    from models import PYTHIA_SHAS  # noqa: PLC0415 — needs exp2b on sys.path

    refs = load_inclusion_referents()  # raises on any missing/valueless record
    root_2c = EXPERIMENTS / "exp2c" / "results" / "inclusion"
    root_2b = EXPERIMENTS / "exp2b" / "results" / "inclusion"
    for (rung, size, mode), ref in sorted(refs.items()):
        root = root_2b if rung == "reverse_string" else root_2c
        rec = json.loads((root / f"{size}_{mode}" / f"{rung}.json").read_text())
        ok = (ref["n"] == 500
              and ref["correct"] == DESIGN_INCLUSION[(rung, size, mode)]
              and rec["sha"] == PYTHIA_SHAS[size]
              and rec["untrained_seed"] == (0 if mode == "untrained" else None))
        report.append({"check": f"inclusion {rung}/{size}/{mode}",
                       "ok": bool(ok),
                       "correct": ref["correct"],
                       "want_correct": DESIGN_INCLUSION[(rung, size, mode)],
                       "sha": rec["sha"], "want_sha": PYTHIA_SHAS[size],
                       "untrained_seed": rec["untrained_seed"]})


def check_byte_referents(report: list) -> None:
    """Structure only. NO first-character quantity is computed here."""
    for rung in RUNGS:
        for size in EVAL_SIZES:
            for mode in MODES:
                p = BYTE_REFERENT_ROOT / f"{size}_{mode}" / f"{rung}.json"
                entry = {"check": f"byte_referent {rung}/{size}/{mode}",
                         "ok": False}
                if p.is_file():
                    rec = json.loads(p.read_text())
                    entry["ok"] = bool(
                        rec.get("rung") == rung and rec.get("size") == size
                        and rec.get("mode") == mode
                        and rec.get("n_items") == 500
                        and len(rec.get("continuations", [])) == 500
                        and len(rec.get("probe_labels", [])) == 500
                        and len(rec.get("answers", [])) == 500
                        and rec.get("untrained_seed") ==
                        (0 if mode == "untrained" else None))
                report.append(entry)


def check_floors(report: list) -> None:
    got = hashlib.sha256(FLOORS_PATH.read_bytes()).hexdigest()
    report.append({"check": "floors sha pin", "ok": got == FLOORS_SHA256,
                   "sha256": got})
    try:
        floors = load_floors()   # executes the recompute-assert
        report.append({"check": "floors recompute-assert", "ok": True,
                       "primaries": {r: floors[r]["primary"] for r in RUNGS}})
    except Exception as exc:  # noqa: BLE001
        report.append({"check": "floors recompute-assert", "ok": False,
                       "error": repr(exc)})


def check_m3(report: list) -> None:
    for rung, tree in M3_TREES.items():
        for size in PROBE_SIZES:
            missing = [s for s in range(5)
                       if not (tree / f"{size}_{rung}_seed{s}.json").is_file()]
            report.append({"check": f"m3 seeds {rung}/{size}",
                           "ok": not missing, "missing_seeds": missing})


def _state_hash(model) -> str:
    h = hashlib.sha256()
    sd = model.state_dict()
    for k in sorted(sd):
        h.update(k.encode())
        h.update(sd[k].cpu().numpy().tobytes())
    return h.hexdigest()


def check_twin_construction(report: list) -> None:
    """The construction 3b's runner performs, on CPU (where from_config's
    seeded init happens regardless of the target device), twice per size."""
    from models import load_pythia  # noqa: PLC0415

    for size in PROBE_SIZES:
        hashes = []
        for _ in range(2):
            _, model = load_pythia(size, untrained=True, seed=0, device="cpu")
            hashes.append(_state_hash(model))
            del model
        report.append({"check": f"untrained twin constructs {size} seed=0",
                       "ok": hashes[0] == hashes[1],
                       "state_sha256": hashes[0],
                       "deterministic": hashes[0] == hashes[1]})


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--construct", action="store_true",
                    help="also construct the probe-size untrained twins "
                         "(loads torch; a few minutes)")
    a = ap.parse_args(argv)

    # the runner's sys.path order, so `models` resolves to exp2b
    for _p in (EXPERIMENTS / "exp2b", EXPERIMENTS / "exp2c"):
        if str(_p) not in sys.path:
            sys.path.insert(0, str(_p))

    report: list[dict] = []
    check_inclusion(report)
    check_byte_referents(report)
    check_floors(report)
    check_m3(report)
    if a.construct:
        check_twin_construction(report)

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
