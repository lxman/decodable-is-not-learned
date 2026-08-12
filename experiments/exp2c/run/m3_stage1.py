# experiments/exp2c/run/m3_stage1.py
"""M3 Stage 1 assembly: the canonical predictor record.

Emits `results/probe_scores.json` in the shape `analyze.py` consumes at
M5 — `rungs` (name, family, scored, probe_score), `untrained_fires`,
`shuffled_fires`. Ascent scores are NOT written here; they do not exist
until M4, and the two-stage lock is exactly the commitment that they
did not exist when this record was made.

Two refusals, carried from the standing two-stage-lock decision:

  * refuses to run before a CLEAN M2 report, and
  * refuses to overwrite an existing record.

Both are load-bearing. The tag commits to this file's contents; a
silent rerun afterwards would void the commitment the tag encodes.

untrained_fires source — RULED 2026-08-11 (Michael): the campaign
known_absent fits, classified through the same `stats_bounds.classify_fire`
path gate 2 uses. Same population and depth as the m3 fits they control.
The tier-2 screen verdicts adjudicated INCLUSION at freeze; this is
analysis-time residual attrition, a different question over a different
population. Survivors' known_absent fits carry from the 2b tagged
record via `reuse_manifest.json` (design §7).

The probe-score arithmetic is design §3 verbatim (2b §3): seed-mean
margin, then mean over the two probe sizes.
"""

import json
from pathlib import Path

import numpy as np

try:  # experiments.exp2c.run.m3_stage1 (pytest / absolute import)
    from ..battery import family_map
    from .. import instrument
    from .. import stats_bounds as sb
    from . import campaign_m2 as m2
    from . import power_conditional as pc
except ImportError:  # pragma: no cover - `python -m run.m3_stage1`
    from battery import family_map
    import instrument
    import stats_bounds as sb
    import run.campaign_m2 as m2
    import run.power_conditional as pc

HERE = Path(__file__).resolve().parent.parent
RESULTS = HERE / "results"
REPO_ROOT = HERE.parent.parent
EXP2B = REPO_ROOT / "experiments" / "exp2b"

UNTRAINED_FIRES_SOURCE = "campaign_known_absent"


def _classify(d: dict) -> str:
    """Identical to m2_report._classify — same floor rule, same
    calibrated bands. Gate 2 and residual gate-1 attrition must not
    disagree about what a fire is."""
    floor = d["n_candidates"] / (instrument.N_PERM_FULL + 1)
    at_floor = bool(d["null_p"] <= floor * 1.0001)
    return sb.classify_fire(d["accuracy"], d["null_mean"], d["null_std"],
                            at_floor)


def _known_absent_paths(rung: str, survivors: dict) -> list[Path]:
    """Campaign fits for new-pool rungs; the 2b tagged fits for carried
    survivors, taken from the manifest rather than reconstructed."""
    if rung in survivors:
        return [REPO_ROOT / e["path"]
                for e in survivors[rung]["fits"]["known_absent"]]
    return [m2.probe_result_path("known_absent", sz, rung, s)
            for sz in m2.SIZES for s in m2.SEEDS]


def _untrained_fires(names, survivors) -> dict[str, list[str]]:
    out = {}
    for rung in names:
        fires = []
        for p in _known_absent_paths(rung, survivors):
            fires.append(_classify(json.loads(Path(p).read_text())))
        out[rung] = fires
    return out


def _shuffled_fires(report: dict) -> list[dict]:
    """m2_report stores gate-2 fires positionally
    (origin, cap, size, seed, classification, acc, null_mean);
    analyze.py reads f["classification"]."""
    out = []
    for rec in report["gate2"]["fires"]:
        origin, cap, size, seed, classification, acc, null_mean = rec
        out.append({"origin": origin, "name": cap, "size": size,
                    "seed": seed, "classification": classification,
                    "accuracy": acc, "null_mean": null_mean})
    return out


def assemble(report_path=None, out_path=None, write=True) -> dict:
    report_path = Path(report_path) if report_path else RESULTS / "m2_report.json"
    out_path = Path(out_path) if out_path else RESULTS / "probe_scores.json"

    if write and out_path.exists():
        raise RuntimeError(
            f"refusing to overwrite an existing Stage 1 record at "
            f"{out_path}: the tag commits to its contents")
    if not report_path.exists():
        raise RuntimeError(
            f"refusing to assemble without an M2 report at {report_path}")
    report = json.loads(report_path.read_text())
    if report.get("abort"):
        raise RuntimeError(
            "refusing to assemble on an M2 report with abort=True")

    fmap = family_map.scored_battery_families()
    order, _ = pc.battery_layout()          # contiguous family blocks
    scores = dict(zip(order, pc.realized_probe_scores()))
    survivors = json.loads(
        (RESULTS / "reuse_manifest.json").read_text())["survivors"]

    rungs = [{"name": n, "family": fmap[n], "scored": True,
              "probe_score": float(scores[n])} for n in order]

    record = {
        "stage": "1",
        "predictor": "basis-starved probe margin (design Sec 3): "
                     "seed-mean, then mean over the two probe sizes",
        "untrained_fires_source": UNTRAINED_FIRES_SOURCE,
        "untrained_fires_ruling": "Michael 2026-08-11",
        "m2_report_clean": True,
        "n_rungs": len(rungs),
        "n_families": len({r["family"] for r in rungs}),
        "n_live": int(sum(r["probe_score"] > 0 for r in rungs)),
        "rungs": rungs,
        "untrained_fires": _untrained_fires(order, survivors),
        "shuffled_fires": _shuffled_fires(report),
        "ascent_scores": "NOT PRESENT — eval side is locked until the "
                         "Stage 1 tag; filled at M4/M5",
    }

    if write:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(record, indent=1))
    return record


def main(argv=None) -> None:
    import argparse

    p = argparse.ArgumentParser(
        description="M3 Stage 1 assembly (commit + tag stay manual)")
    p.add_argument("--out", type=Path, default=None)
    p.add_argument("--report", type=Path, default=None)
    args = p.parse_args(argv)

    rec = assemble(report_path=args.report, out_path=args.out)
    dropped = [n for n, f in rec["untrained_fires"].items()
               if any(c in ("elevated", "structural_abort") for c in f)]
    out = args.out or (RESULTS / "probe_scores.json")
    print(f"[m3] Stage 1 record -> {out}", flush=True)
    print(f"[m3] {rec['n_rungs']} rungs / {rec['n_families']} families; "
          f"{rec['n_live']} live, {rec['n_rungs'] - rec['n_live']} flat",
          flush=True)
    print(f"[m3] untrained_fires source: {rec['untrained_fires_source']} "
          f"(ruled {rec['untrained_fires_ruling']})", flush=True)
    print(f"[m3] residual gate-1 attrition: "
          f"{dropped if dropped else 'none'}", flush=True)
    print("[m3] commit + TAG are manual. Eval side stays LOCKED until "
          "the tag exists.", flush=True)


if __name__ == "__main__":
    main()
