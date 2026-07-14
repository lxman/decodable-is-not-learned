"""Assemble Stage 1 probe scores (design §3) from completed m3 probe results.

Usage:  python -m run.m3_stage1

Probe margin per (capability, model) = seed-mean of the five per-seed margins
(margin 0 where the frozen bar was missed). Probe score per capability = mean of
the two models' margins. Writes results/probe_scores.json in exactly the schema
frozen analyze.py binds to, plus a per-cell breakdown for the record.

Refuses to overwrite: Stage 1 is committed and TAGGED before any 2.8b+ query
(the two-stage lock). Refuses to run at all if results/m2_report.json is missing
(gates first) or records a pipeline abort.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

from run.collect_activations import scored_battery
from run.run_probes import SEEDS, probe_result_path

EXP_DIR = Path(__file__).resolve().parent.parent
SIZES = ("410m", "1b")


def main() -> None:
    out = EXP_DIR / "results" / "probe_scores.json"
    if out.exists():
        sys.exit(f"{out} exists — Stage 1 is committed; it does not get recomputed")
    m2 = EXP_DIR / "results" / "m2_report.json"
    if not m2.exists():
        sys.exit("m2_report.json missing — gates run before Stage 1 (design §5)")
    report = json.loads(m2.read_text())
    if report["shuffled_fires"]:
        sys.exit("m2 recorded a pipeline abort — Stage 1 blocked")

    battery = [c for c in scored_battery() if c not in set(report["attrition"])]
    scores, detail = {}, {}
    for cap in battery:
        per_model = {}
        for sz in SIZES:
            margins = [json.loads(probe_result_path("m3", sz, cap, s).read_text())["margin"]
                       for s in SEEDS]
            per_model[sz] = {"seed_margins": margins,
                             "mean": float(np.mean(margins)),
                             "sd": float(np.std(margins, ddof=1))}
        score = float(np.mean([per_model[sz]["mean"] for sz in SIZES]))
        scores[cap] = {"probe_margin": score}
        detail[cap] = per_model
        print(f"[m3] {cap:16s} probe_score={score:+.4f} "
              f"(410m {per_model['410m']['mean']:+.4f}, 1b {per_model['1b']['mean']:+.4f})",
              flush=True)

    out.write_text(json.dumps(scores, indent=1))
    (EXP_DIR / "results" / "probe_scores_detail.json").write_text(json.dumps(detail, indent=1))
    print(f"[m3] wrote {out} — COMMIT AND TAG before any 2.8b+ query (two-stage lock)",
          flush=True)


if __name__ == "__main__":
    main()
