# Design-session exploration for 4c (in-sample, the four KNOWN Exp 4 trajectories; read-only).
import os
for k in ("VECLIB_MAXIMUM_THREADS","OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS"): os.environ[k] = "1"
import json, sys, numpy as np
from experiments.exp4 import battery_4 as b4, analyze_4 as a4, collect_4
from experiments.exp2g import battery_2g
root = b4.EXP4; floors = battery_2g.load_floors(); out = {}
for traj in b4.TRAJECTORIES_4:
    oc = b4.load_outcome_4(traj); rs = b4.rung_sets_4(oc, floors)
    sweep = a4.load_sweep_tables_4(root, traj)
    refs = b4.REFS_FOR_4[traj]; raw = collect_4.load_ref_tables_4(root, refs)
    ref_tables = {ref: rt["sets"] for ref, rt in raw.items()}
    s = a4.alignment_series_4(root, traj, ref_tables, sweep)
    steps = s["steps"]
    out[traj] = {"steps": steps, "a": s["a"], "R": rs["R"], "flat": rs["flat"], "transient": rs["transient"],
                 "clear_index": {r: steps.index(rs["t_clear"][r]) for r in rs["R"]}}
    print(traj, len(steps), len(rs["R"]), len(rs["flat"]), flush=True)
json.dump(out, open(sys.argv[1], "w"))
