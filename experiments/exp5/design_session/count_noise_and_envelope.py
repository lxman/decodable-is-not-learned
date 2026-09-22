"""Design-session computation 4 (disclosed): count differences between adjacent committed checkpoints
on live rungs (2g's 2.8b, 2h's 6.9b), then the COUNT-grain power envelope of design §3.5
(R - P per cell, rung-block exact sign flip). The envelope is a model, not a measurement."""
import sys, json, itertools, numpy as np
sys.path.insert(0, '.')
from experiments.exp4 import battery_4 as b4
from experiments.exp2h import battery_2h as bh
from experiments.exp2d import stats_2d as st
from experiments.exp2d import battery_2d as b2d

floors = {r: v['floor'] for r, v in b2d.floor_table().items()}
rungs = b2d.RUNGS

def series_28():
    out = b4.load_outcome_4('pythia_2.8b'); steps = sorted(int(s) for s in out['per_step'])
    get = lambda s, r: out['per_step'][s if s in out['per_step'] else str(s)]['rungs'][r]['correct']
    return steps, get

def series_69():
    root = bh.sweep_dir_2h(bh.EXP2H)
    steps = sorted(int(p.name[4:]) for p in root.iterdir() if p.name.startswith('step') and p.name[4:].isdigit() and int(p.name[4:]) > 0)
    get = lambda s, r: json.load(open(bh.record_path_2h(bh.EXP2H, s, r)))['correct']
    return steps, get

diffs_all = []
for name, (steps, get) in (('2.8b', series_28()), ('6.9b', series_69())):
    d_live = []; d_late = []
    for r in rungs:
        seq = [get(s, r) for s in steps]
        sig = [st.binomial_bar(k, 500, floors[r])['significant'] for k in seq]
        for i in range(len(seq) - 1):
            if sig[i] or sig[i + 1]:
                d_live.append(abs(seq[i + 1] - seq[i]))
                if steps[i] >= 60000:
                    d_late.append(abs(seq[i + 1] - seq[i]))
    d_live = np.array(d_live); d_late = np.array(d_late); diffs_all += list(d_late)
    print(f"{name}: live adjacent pairs {len(d_live)} |dcount| mean {d_live.mean():.1f} median {np.median(d_live):.0f} p90 {np.percentile(d_live,90):.0f}; late (>=60k) n {len(d_late)} mean {d_late.mean():.1f} median {np.median(d_late):.0f} p90 {np.percentile(d_late,90):.0f}")
diffs_all = np.array(diffs_all)
print("pooled late |dcount| at 10k spacing: mean", round(diffs_all.mean(), 1), "sd of signed-equivalent ~", round(diffs_all.mean() * 1.25, 1))

rng = np.random.default_rng(7)

def battery(prof, sd, q, off, drift, rng):
    blocks = []
    for n in prof:
        cs = []
        for _ in range(n):
            true_off = off if rng.random() < q else 0.0
            f = 0.0
            a = true_off + rng.normal(0, sd, 2).mean()
            b1 = true_off + rng.normal(0, drift) + rng.normal(0, sd, 2).mean()
            b2 = true_off + rng.normal(0, drift) + rng.normal(0, sd, 2).mean()
            R = abs(a - f); P = (abs(a - b1) + abs(a - b2)) / 2
            cs.append((R - P) / 500)
        blocks.append(np.array(cs))
    allc = np.concatenate(blocks); T = allc.mean()
    sums = np.array([b.sum() for b in blocks]); k = len(sums)
    signs = np.array(list(itertools.product([1, -1], repeat=k))) if k <= 14 else rng.choice([1, -1], size=(10000, k))
    null = (signs * sums).sum(1) / len(allc)
    return T, (null >= T - 1e-12).mean()

print("\ncount-grain envelope: per-read count noise sd (items), placebo drift sd (items), true offset 25 items (.05) on a fraction q of live cells; bar T>=.02, p<.01 rung-block")
for label, prof in (("A 11x6", [6] * 11), ("B 7x4", [4] * 7), ("C 9x5", [5] * 9)):
    for sd in (6, 10, 15):
        for q in (0.0, 0.25, 0.5):
            res = np.array([battery(prof, sd, q, 25, 4, rng) for _ in range(400)])
            T, p = res[:, 0], res[:, 1]
            print(f"profile {label} sd={sd:2d} q={q:.2f}: mean T {T.mean():+.4f} sd {T.std():.4f}  P(NOT-MATCHED) {((p<.01)&(T>=.02)).mean():.2f}  P(p<.01) {(p<.01).mean():.2f}")
