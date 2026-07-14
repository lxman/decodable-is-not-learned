"""M2 gate adjudication from completed probe results (design §3 controls + §5 M2).

Usage:  python -m run.m2_report

Frozen rules applied, not chosen, here:
- UNTRAINED control: a capability whose untrained-model probe fires (present in
  ANY seed at either size) is DROPPED from the scored battery — preregistered
  attrition, battery re-committed before Stage 1; neither an abort nor the
  one-change budget (§3, fixed 2026-07-06 pre-freeze).
- SHUFFLED-label control: any fire anywhere is a PIPELINE ABORT (exit 2).
- POSITIVE controls: probe must fire (majority of seeds) on trained activations
  at both sizes AND M1 argmax must be reliable at both sizes. Failure here is a
  gate failure for the one-ledgered-fix process — reported, not auto-fixed.

Exit codes: 0 = gates clean (possibly with attrition), 2 = pipeline abort.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from run.collect_activations import scored_battery
from run.run_probes import CONTROLS, SEEDS, probe_result_path

EXP_DIR = Path(__file__).resolve().parent.parent
SIZES = ("410m", "1b")
ARGMAX_RELIABLE = 0.9  # positive controls are 'plainly present' (design §2); .99/1.0 and .34/.85 observed


def load(stage, size, cap, seed):
    return json.loads(probe_result_path(stage, size, cap, seed).read_text())


def main() -> None:
    battery = scored_battery()
    abort = False
    attrition = []

    print("== M2 gate report ==", flush=True)

    for cap in battery:
        fires = [(sz, s) for sz in SIZES for s in SEEDS
                 if load("m2_untrained", sz, cap, s)["present"]]
        if fires:
            attrition.append(cap)
            print(f"[m2] UNTRAINED fires on {cap} at {fires} -> ATTRITION (drop, re-commit battery)",
                  flush=True)
    if not attrition:
        print("[m2] untrained control: silent on all capabilities/sizes/seeds", flush=True)

    shuffled_fires = [(cap, sz, s) for cap in battery for sz in SIZES for s in SEEDS
                      if load("m2_shuffled", sz, cap, s)["present"]]
    if shuffled_fires:
        abort = True
        print(f"[m2] SHUFFLED-LABEL FIRES: {shuffled_fires} -> PIPELINE ABORT", flush=True)
    else:
        print("[m2] shuffled-label control: fails everywhere (as it must)", flush=True)

    for cap in CONTROLS:
        for sz in SIZES:
            probe_ok = sum(load("m2_controls", sz, cap, s)["present"] for s in SEEDS) >= 3
            arg = json.loads(
                (EXP_DIR / "results" / "inclusion" / f"{sz}_trained" / f"{cap}.json").read_text())
            arg_ok = arg["acc"] >= ARGMAX_RELIABLE
            status = "OK" if (probe_ok and arg_ok) else "GATE FAIL"
            print(f"[m2] positive control {cap}/{sz}: probe_majority={probe_ok} "
                  f"argmax={arg['acc']:.3f} (reliable={arg_ok}) -> {status}", flush=True)

    report = {"attrition": attrition, "shuffled_fires": shuffled_fires}
    (EXP_DIR / "results" / "m2_report.json").write_text(json.dumps(report, indent=1))
    print(f"[m2] report written; attrition={attrition or 'none'}", flush=True)
    sys.exit(2 if abort else 0)


if __name__ == "__main__":
    main()
