"""M2 gate adjudication with CALIBRATED tolerances (design §4 — no
zero-tolerance rules on nonzero-rate tests; the Exp 2 roman lesson).

Usage:  python -m run.m2_report_2b

Frozen rules applied, not chosen, here:

GATE 1 (known-absent, untrained under starved splits):
  Per-fit false-fire probability under clean machinery is the add-one floor x
  Bonferroni family: 18/2501 at 410m, 14/2501 at 1b. Across all fits the
  observed fire count must be consistent with that rate — one-sided binomial
  p >= .01 against the CONSERVATIVE (max) rate — AND every fire must carry the
  floor signature: corrected p at its family's floor AND accuracy within 3
  null-SD of the null mean. A structurally-above fire is a real leak: that
  capability is DROPPED (attrition, battery re-committed before Stage 1).
  Too many floor-signature fires (binomial p < .01) is a pipeline abort.

GATE 2 (known-present): entity_track + ctrl_copy on trained weights must show
  seed-majority (>=3/5) present at both sizes AND seed-mean starved margin
  >= 0.2 at 1b. Failure = gate failure for the one-ledgered-fix process.

GATE 3 (shuffled): same binomial + floor-signature machinery as gate 1;
  a structurally-above fire is a pipeline abort (exit 2).

GATE 4 (argmax positive control): ctrl_copy argmax >= 0.9 at both sizes
  (from the committed M1 inclusion results).

Exit codes: 0 = gates clean (attrition possible), 2 = pipeline abort.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from scipy.stats import binom

from run.battery_sets import CONTROLS, GATE_CAPS, scored_battery
from run.run_probes_2b import SEEDS, probe_result_path

EXP_DIR = Path(__file__).resolve().parent.parent
SIZES = ("410m", "1b")
FLOOR_RATE = {"410m": 18 / 2501, "1b": 14 / 2501}
RATE_MAX = max(FLOOR_RATE.values())
BINOM_ALPHA = 0.01
KNOWN_PRESENT_MARGIN = 0.2
ARGMAX_RELIABLE = 0.9


def load(stage, size, cap, seed):
    return json.loads(probe_result_path(stage, size, cap, seed).read_text())


def floor_signature(d, size) -> bool:
    """p exactly at its family's add-one floor AND accuracy within 3 null-SD."""
    fam = d["n_candidates"]
    at_floor = abs(d["null_p"] - fam / 2501) < 1e-9
    near_null = abs(d["accuracy"] - d["null_mean"]) <= 3 * max(d["null_std"], 1e-9)
    return at_floor and near_null


def sweep(stage, caps):
    fires, leaks = [], []
    n_fits = 0
    for cap in caps:
        for sz in SIZES:
            for s in SEEDS:
                d = load(stage, sz, cap, s)
                n_fits += 1
                if d["present"]:
                    (fires if floor_signature(d, sz) else leaks).append(
                        (cap, sz, s, round(d["accuracy"], 4),
                         round(d["null_mean"], 4)))
    p_count = float(binom.sf(len(fires) + len(leaks) - 1, n_fits, RATE_MAX)) \
        if (fires or leaks) else 1.0
    return fires, leaks, n_fits, p_count


def main() -> None:
    battery = scored_battery()
    abort = False
    attrition = []

    print("== M2 gate report (calibrated tolerances, design §4) ==", flush=True)

    fires, leaks, n, p_cnt = sweep("known_absent", battery)
    exp = n / 2 * (FLOOR_RATE["410m"] + FLOOR_RATE["1b"])
    print(f"[m2] GATE1 known-absent: {len(fires)} floor-signature fire(s) + "
          f"{len(leaks)} structural leak(s) in {n} fits "
          f"(E~{exp:.2f} at the floor rate; count-test p={p_cnt:.3f})", flush=True)
    for f in fires:
        print(f"[m2]   floor fire (tolerated): {f}", flush=True)
    for cap, sz, s, acc, nm in leaks:
        if cap not in attrition:
            attrition.append(cap)
        print(f"[m2]   STRUCTURAL LEAK: {cap}/{sz}/seed{s} acc={acc} vs "
              f"null={nm} -> ATTRITION", flush=True)
    if p_cnt < BINOM_ALPHA:
        abort = True
        print(f"[m2]   fire COUNT exceeds the floor rate (p={p_cnt:.4g}) "
              f"-> PIPELINE ABORT", flush=True)

    s_fires, s_leaks, s_n, s_p = sweep("shuffled", battery)
    print(f"[m2] GATE3 shuffled: {len(s_fires)} floor fire(s) + "
          f"{len(s_leaks)} structural in {s_n} fits (count-test p={s_p:.3f})",
          flush=True)
    if s_leaks or s_p < BINOM_ALPHA:
        abort = True
        print(f"[m2]   -> PIPELINE ABORT ({s_leaks or 'count'})", flush=True)

    for cap in GATE_CAPS + CONTROLS:
        for sz in SIZES:
            ds = [load("known_present", sz, cap, s) for s in SEEDS]
            maj = sum(d["present"] for d in ds) >= 3
            mean_margin = sum(d["margin"] for d in ds) / len(ds)
            ok = maj and (sz != "1b" or mean_margin >= KNOWN_PRESENT_MARGIN)
            print(f"[m2] GATE2 known-present {cap}/{sz}: majority={maj} "
                  f"mean_margin={mean_margin:.3f} -> "
                  f"{'OK' if ok else 'GATE FAIL'}", flush=True)

    for sz in SIZES:
        arg = json.loads((EXP_DIR / "results" / "inclusion" / f"{sz}_trained" /
                          "ctrl_copy.json").read_text())
        ok = arg["acc"] >= ARGMAX_RELIABLE
        print(f"[m2] GATE4 ctrl_copy argmax/{sz}: {arg['acc']:.3f} -> "
              f"{'OK' if ok else 'GATE FAIL'}", flush=True)

    report = {"attrition": attrition, "gate1": {"fires": fires, "leaks": leaks,
              "count_p": p_cnt}, "gate3": {"fires": s_fires, "leaks": s_leaks,
              "count_p": s_p}}
    (EXP_DIR / "results" / "m2_report.json").write_text(json.dumps(report, indent=1))
    print(f"[m2] report written; attrition={attrition or 'none'}", flush=True)
    sys.exit(2 if abort else 0)


if __name__ == "__main__":
    main()
