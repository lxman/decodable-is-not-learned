"""M2 gate adjudication against the CALIBRATED bounds (design §4).

Applies, never chooses, the frozen rules — written fresh against 2c's
stats_bounds rather than ported from 2b's m2_report, whose per-fire
floor-signature predicate and pooled abort are the two Section-6
defects the 2c design replaced (rulings a/b; fixture-suite rule).

GATE 2 (shuffled): per-fire classification via stats_bounds.classify_fire
  (tolerated band [z.005, z.995] of the max of 2,500 null draws;
  elevated feeds the count test, never aborts; abort ONLY beyond
  z_{1-1e-4} = 5.37). The binomial count test governs: all present
  fires (whatever their band) against the conservative floor rate over
  ALL shuffled fits — the 220 new-pool fits this campaign produced plus
  the 12 carried survivors' 120 fits from the tagged 2b record
  (declared at freeze: "2b shuffled fits carry for gate 2's count
  test"). Abort authority lives here and only here.

GATE 3 (known-present): entity_track + ctrl_copy trained fits must show
  seed-majority (>=3/5) present at both sizes AND seed-mean starved
  margin >= 0.2 at 1b.

GATE 4 (argmax): echoed from the committed M1 inclusion record — it was
  adjudicated at freeze (ctrl_copy .960/.980 >= .9), not here.

Exit codes: 0 = gates clean, 2 = pipeline abort (gate 2 structural).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from scipy.stats import binom

try:
    from . import campaign_m2 as m2
    from .. import instrument
    from .. import stats_bounds as sb
except ImportError:  # pragma: no cover - `python -m run.m2_report` from exp2c/
    import instrument
    import stats_bounds as sb
    from run import campaign_m2 as m2

HERE = Path(__file__).resolve().parent.parent
EXP2B = HERE.parent / "exp2b"
SIZES = ("410m", "1b")
SEEDS = m2.SEEDS
RATE_MAX = max(instrument.FLOORS.values())        # 18/2501, conservative
BINOM_ALPHA = 0.01
KNOWN_PRESENT_MARGIN = 0.2


def _classify(d: dict) -> str:
    floor = d["n_candidates"] / (instrument.N_PERM_FULL + 1)
    at_floor = bool(d["null_p"] <= floor * 1.0001)
    return sb.classify_fire(d["accuracy"], d["null_mean"], d["null_std"],
                            at_floor)


def _shuffled_fit_files() -> list[tuple[str, Path]]:
    """(origin, path) for every shuffled fit in gate 2's count test:
    2c's new-pool fits + the carried 2b survivor fits."""
    files: list[tuple[str, Path]] = []
    for cap in m2.new_pool_rungs():
        for sz in SIZES:
            for s in SEEDS:
                files.append(("2c", m2.probe_result_path("shuffled", sz, cap, s)))
    for cap in sorted(m2.survivors()):
        for sz in SIZES:
            for s in SEEDS:
                files.append(
                    ("2b", EXP2B / "results" / "probes" / "shuffled" /
                     f"{sz}_{cap}_seed{s}.json"))
    return files


def main() -> None:
    abort = False
    print("== 2c M2 gate report (stats_bounds-calibrated, design §4) ==",
          flush=True)

    fires, structural = [], []
    n_fits = 0
    for origin, path in _shuffled_fit_files():
        d = json.loads(path.read_text())
        n_fits += 1
        if d["present"]:
            cls = _classify(d)
            rec = (origin, d["capability"], d["size"], d["seed"], cls,
                   round(d["accuracy"], 4), round(d["null_mean"], 4))
            fires.append(rec)
            if cls == "structural_abort":
                structural.append(rec)
    p_cnt = float(binom.sf(len(fires) - 1, n_fits, RATE_MAX)) if fires else 1.0
    exp = n_fits * RATE_MAX
    print(f"[m2] GATE2 shuffled: {len(fires)} fire(s) in {n_fits} fits "
          f"(E<={exp:.2f} at the conservative floor rate; "
          f"count-test p={p_cnt:.3f})", flush=True)
    for rec in fires:
        print(f"[m2]   fire: {rec}", flush=True)
    if structural:
        abort = True
        print(f"[m2]   STRUCTURAL fire(s) beyond z={sb.GATE2_ABORT:.2f} "
              f"-> PIPELINE ABORT", flush=True)
    if p_cnt < BINOM_ALPHA:
        abort = True
        print(f"[m2]   fire COUNT exceeds the floor rate (p={p_cnt:.4g}) "
              f"-> PIPELINE ABORT", flush=True)

    gate3 = {}
    for cap in m2.KNOWN_PRESENT_CAPS:
        for sz in SIZES:
            ds = [json.loads(m2.probe_result_path(
                "known_present", sz, cap, s).read_text()) for s in SEEDS]
            maj = sum(d["present"] for d in ds) >= 3
            mean_margin = sum(d["margin"] for d in ds) / len(ds)
            ok = maj and (sz != "1b" or mean_margin >= KNOWN_PRESENT_MARGIN)
            gate3[f"{cap}/{sz}"] = {"majority": maj,
                                    "mean_margin": round(mean_margin, 4),
                                    "ok": ok}
            print(f"[m2] GATE3 known-present {cap}/{sz}: majority={maj} "
                  f"mean_margin={mean_margin:.3f} -> "
                  f"{'OK' if ok else 'GATE FAIL'}", flush=True)

    for sz in SIZES:
        arg = json.loads((HERE / "results" / "inclusion" / f"{sz}_trained" /
                          "ctrl_copy.json").read_text())
        print(f"[m2] GATE4 ctrl_copy argmax/{sz} (adjudicated at freeze): "
              f"{arg['acc']:.3f}", flush=True)

    report = {"gate2": {"n_fits": n_fits, "fires": fires,
                        "structural": structural, "count_p": p_cnt},
              "gate3": gate3, "abort": abort}
    (HERE / "results" / "m2_report.json").write_text(
        json.dumps(report, indent=1))
    print(f"[m2] report written -> results/m2_report.json "
          f"({'ABORT' if abort else 'clean'})", flush=True)
    sys.exit(2 if abort else 0)


if __name__ == "__main__":
    main()
