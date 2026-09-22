"""Design-session computation 2 (disclosed): rung-level clear flips between adjacent committed checkpoints, 2h's 6.9b grid."""
import sys, json
sys.path.insert(0, '.')
from experiments.exp2h import battery_2h as bh
from experiments.exp2d import stats_2d as st
from experiments.exp2d import battery_2d as b2d

floors = {r: v['floor'] for r, v in b2d.floor_table().items()}
root = bh.sweep_dir_2h(bh.EXP2H)
steps = sorted(int(p.name[4:]) for p in root.iterdir() if p.name.startswith('step') and p.name[4:].isdigit() and int(p.name[4:]) > 0)

def correct(step, rung):
    d = json.load(open(bh.record_path_2h(bh.EXP2H, step, rung)))
    return d['correct'], d.get('n', 500)

per = {}
flips = live = 0
for r in b2d.RUNGS:
    seq = []
    for s in steps:
        k, n = correct(s, r)
        seq.append(st.binomial_bar(k, n, floors[r])['significant'])
    f = sum(1 for a, b in zip(seq, seq[1:]) if a != b)
    live += sum(1 for a, b in zip(seq, seq[1:]) if a or b)
    per[r] = (sum(seq), f); flips += f
print('pythia_6.9b steps', len(steps), 'flips', flips, 'live adjacent pairs', live, 'rate among live', round(flips / max(live, 1), 3))
print(' ever-clear rungs:', {r: v for r, v in per.items() if v[0] > 0})
