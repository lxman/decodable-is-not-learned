# Design-session computation 1 (2026-09-17): rising / flat / transient sets and clear indices for the two
# new trajectories, through battery_4's own functions on 2h's and 2l's committed sweep records.
# Run from the repo root: PYTHONPATH=. python experiments/exp4c/design_session/00_outcome_tables.py
import json
from pathlib import Path
from experiments.exp4 import battery_4 as b4
from experiments.exp2g import battery_2g
floors = battery_2g.load_floors()
def outcome(root):
    root = Path(root); steps = sorted(int(p.name[4:]) for p in root.glob("step*") if p.is_dir()); steps = [s for s in steps if s != 0]
    per = {}
    for s in steps:
        d = root / f"step{s}"; rungs = {}
        for r in b4.RUNGS:
            rec = json.loads((d / f"{r}.json").read_text()); rungs[r] = {"correct": int(rec["correct"]), "n": int(rec["n"]), "bits": rec["bits"]}
        per[s] = {"digest": json.loads((d / "_checkpoint.json").read_text()).get("digest"), "rungs": rungs}
    return {"steps": steps, "per_step": per}
for name, root in (("pythia_6.9b", "experiments/exp2h/results/sweep/6.9b"), ("olmo2_13b", "experiments/exp2l/results/sweep/olmo13b")):
    o = outcome(root); rs = b4.rung_sets_4(o, floors); steps = o["steps"]
    idx = {r: steps.index(rs["t_clear"][r]) for r in rs["R"]}
    print(name, len(steps), "points; R", len(rs["R"]), "flat", len(rs["flat"]), "transient", rs["transient"])
    print("  clear index:", dict(sorted(idx.items(), key=lambda kv: kv[1])))
    print("  flat:", rs["flat"])
