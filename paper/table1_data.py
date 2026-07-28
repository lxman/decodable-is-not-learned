"""Table T1 source: the full scored battery — task, probe label, surface
basis, split parameters, and fate — assembled from the committed battery
item files and m2_report.json (tag exp2b-closed). The paper's Table 1 is
pasted verbatim from this script's output; rerun and diff to verify.

    python paper/table1_data.py   # writes paper/table1.md, prints it
"""

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
ITEMS = REPO / "experiments" / "exp2b" / "battery" / "items"
scored = json.loads((ITEMS / "scored_battery.json").read_text())
attrition = set(json.loads(
    (REPO / "experiments" / "exp2b" / "results" / "m2_report.json")
    .read_text())["attrition"])

# Basis strings abridged for print ONLY where the committed spec string
# carries internal cross-references; the item files hold the verbatim
# text. Every abridgment is listed here so the mapping is diffable.
ABRIDGE = {
    "clock24": "offset token D (475 values); mod-of-offset sibling of "
               "weekday",
    "oct2dec": "octal string (4,032 values); value-mod-10 sibling of "
               "bin2dec",
    "reverse_string": "final BPE chunk of the input (chunks, not "
                      "strings, are the lookup unit)",
}

rows = []
for cap in scored:
    d = json.loads((ITEMS / f"{cap}.json").read_text())
    f = d["feasibility"]
    p = f["params"]
    seeds = f["per_seed"].values()
    n_items = len(d["probe_items"])
    val = round(sum(s["n_val"] for s in seeds) / len(f["per_seed"]))
    train = round(sum(s["n_train"] for s in seeds) / len(f["per_seed"]))
    held = [round(sum(s["held_per_component"][i] for s in seeds)
                  / len(f["per_seed"]))
            for i in range(len(f["component_cardinalities"]))]
    rows.append({
        "capability": cap,
        "fate": "attrited" if cap in attrition else "survivor",
        "task": d["description"],
        "label": d["probe_label_space"],
        "basis": ABRIDGE.get(cap, d["basis_kind"]),
        "card": f["component_cardinalities"],
        "holdout": p["holdout_frac"] or p["n_holdout"],
        "held": held,
        "val": val,
        "train": train,
        "disc": n_items - val - train,
    })

rows.sort(key=lambda r: (r["fate"] == "survivor", r["capability"]))

lines = [
    "| capability | task | probe label | surface basis | split "
    "(held-out / observed values) | val / train / disc. | fate |",
    "|---|---|---|---|---|---|---|",
]
for r in rows:
    split = "; ".join(f"{h:,}/{c:,}" for h, c in zip(r["held"], r["card"]))
    lines.append(
        f"| {r['capability']} | {r['task']} | {r['label']} | "
        f"{r['basis']} | {r['holdout']} → {split} | "
        f"{r['val']:,} / {r['train']:,} / {r['disc']:,} | {r['fate']} |")

table = "\n".join(lines)
(HERE / "table1.md").write_text(table + "\n")
print(table)
n_att = sum(r["fate"] == "attrited" for r in rows)
print(f"\n{len(rows)} capabilities ({n_att} attrited, "
      f"{len(rows) - n_att} survivors) -> {HERE / 'table1.md'}")
