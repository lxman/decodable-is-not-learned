"""Design-session computation 1 (disclosed): rung-level clear flips between adjacent committed checkpoints, 2g's 2.8b grid."""
import sys
sys.path.insert(0, '.')
from experiments.exp4 import battery_4 as b4
from experiments.exp2d import stats_2d as st
from experiments.exp2d import battery_2d as b2d

floors = {r: v['floor'] for r, v in b2d.floor_table().items()}
out = b4.load_outcome_4('pythia_2.8b')
steps = sorted(int(s) for s in out['per_step'])
rungs = b2d.RUNGS

def sig(s, r):
    rec = out['per_step'][s if s in out['per_step'] else str(s)]['rungs'][r]
    return st.binomial_bar(rec['correct'], rec['n'], floors[r])['significant']

flips = pairs = live_pairs = 0
per_rung = {}
for r in rungs:
    seq = [sig(s, r) for s in steps]
    f = sum(1 for a, b in zip(seq, seq[1:]) if a != b)
    per_rung[r] = (sum(seq), f)
    flips += f; pairs += len(seq) - 1
    live_pairs += sum(1 for a, b in zip(seq, seq[1:]) if a or b)
print('pythia_2.8b steps', len(steps), 'rungs', len(rungs), 'adjacent pairs', pairs, 'flips', flips,
      'flip rate all', round(flips / pairs, 4), 'live pairs', live_pairs, 'flip rate among live', round(flips / max(live_pairs, 1), 3))
print('  rungs ever clear:', {r: v for r, v in per_rung.items() if v[0] > 0})
late = [s for s in steps if s >= 100000]
lf = sum(1 for r in rungs for a, b in zip([sig(s, r) for s in late], [sig(s, r) for s in late][1:]) if a != b)
llive = sum(1 for r in rungs for a, b in zip([sig(s, r) for s in late], [sig(s, r) for s in late][1:]) if a or b)
print('  late (>=100k) flips', lf, 'of', len(rungs) * (len(late) - 1), 'pairs; among live', llive)
