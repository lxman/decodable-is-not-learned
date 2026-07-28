"""Appendix A source: one example item per capability and the complete
per-seed starved margins (trained m3 and untrained known_absent, both
sizes, 5 seeds) from the committed fit files (tag exp2b-closed). The
paper's Appendix A is pasted verbatim from this script's output.

    python paper/appendixA_data.py  # writes paper/appendixA.md, prints it
"""

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
EXP = REPO / "experiments" / "exp2b"
ITEMS = EXP / "battery" / "items"
PROBES = EXP / "results" / "probes"
SIZES = ("410m", "1b")
SEEDS = range(5)

scored = json.loads((ITEMS / "scored_battery.json").read_text())
attrition = set(json.loads(
    (EXP / "results" / "m2_report.json").read_text())["attrition"])
order = sorted(scored, key=lambda c: (c not in attrition, c))


def seed_margins(stage, size, cap):
    return [json.loads(
        (PROBES / stage / f"{size}_{cap}_seed{s}.json").read_text())["margin"]
        for s in SEEDS]


out = ["### A.1 One item per capability", ""]
for cap in order:
    d = json.loads((ITEMS / f"{cap}.json").read_text())
    it = d["probe_items"][0]
    out.append(f"- **{cap}** — \"{it['question']}\" → {it['answer']} "
               f"(probe label: {it['probe_label']})")

out += ["", "### A.2 All starved margins, per seed", "",
        "| capability | 410M untrained | 410M trained | 1B untrained "
        "| 1B trained |", "|---|---|---|---|---|"]
for cap in order:
    cells = []
    for size in SIZES:
        for stage in ("known_absent", "m3"):
            cells.append(" / ".join(
                f"{m:.2f}" for m in seed_margins(stage, size, cap)))
    out.append(f"| {cap} | {cells[0]} | {cells[1]} | {cells[2]} | "
               f"{cells[3]} |")

text = "\n".join(out)
(HERE / "appendixA.md").write_text(text + "\n")
print(text)
print(f"\n{len(order)} capabilities -> {HERE / 'appendixA.md'}")
