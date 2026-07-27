"""F2 source data: per-capability seed-mean starved-probe margins, trained
(m3) vs untrained (known_absent), both probe sizes, from the committed
exp2b closeout JSONs (tag exp2b-closed). Every number in paper §5 is
transcribed from this script's committed output — never from memory.

    python paper/fig2_data.py   # writes paper/fig2_data.json, prints table
"""

from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
EXP = REPO / "experiments" / "exp2b"
PROBES = EXP / "results" / "probes"
SIZES = ("410m", "1b")
SEEDS = range(5)

battery = json.loads(
    (EXP / "battery" / "items" / "scored_battery.json").read_text())
attrition = set(json.loads(
    (EXP / "results" / "m2_report.json").read_text())["attrition"])


def mean_margin(stage: str, size: str, cap: str) -> float:
    ms = []
    for s in SEEDS:
        d = json.loads((PROBES / stage / f"{size}_{cap}_seed{s}.json").read_text())
        ms.append(d["margin"])
    return sum(ms) / len(ms)


rows = []
for cap in battery:
    row = {"capability": cap, "fate": "attrited" if cap in attrition else "survivor"}
    for size in SIZES:
        row[f"trained_{size}"] = round(mean_margin("m3", size, cap), 4)
        row[f"untrained_{size}"] = round(mean_margin("known_absent", size, cap), 4)
        row[f"gap_{size}"] = round(row[f"trained_{size}"] - row[f"untrained_{size}"], 4)
    rows.append(row)

rows.sort(key=lambda r: (r["fate"], -r["gap_410m"]))
out = REPO / "paper" / "fig2_data.json"
out.write_text(json.dumps(rows, indent=1))

hdr = f"{'capability':<16}{'fate':<10}" + "".join(
    f"{c:>10}" for c in ("tr410m", "un410m", "gap410m", "tr1b", "un1b", "gap1b"))
print(hdr)
for r in rows:
    print(f"{r['capability']:<16}{r['fate']:<10}"
          f"{r['trained_410m']:>10.3f}{r['untrained_410m']:>10.3f}"
          f"{r['gap_410m']:>10.3f}{r['trained_1b']:>10.3f}"
          f"{r['untrained_1b']:>10.3f}{r['gap_1b']:>10.3f}")
print(f"\n{len(rows)} capabilities -> {out}")
