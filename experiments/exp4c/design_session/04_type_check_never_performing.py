import json, sys, numpy as np
ARITH = {"add3_mid","sub3_mid","add4_mid","sub4_mid","add_base8","sub_base8","arith_next","quad_next","count_div13","count_div7","median5","median7","oct2dec","base7","base12_digitsum","base13","mod13","mod13_comp","mod17","mod19","isqrt_gap","collatz_step2","roman_sum7","clock24","clock24_d999"}
S = json.load(open(sys.argv[1]))
def q_of(val, pool):
    pool = np.asarray(pool); return (np.sum(pool < val) + .5 * np.sum(pool == val)) / len(pool)
print("Non-arithmetic FLAT rungs (never perform) ranked among ARITHMETIC flat rungs, growth since t_1:")
allq = []
for traj, d in S.items():
    a = d["a"]; G = len(d["steps"]); af = [f for f in d["flat"] if f in ARITH]; nf = [f for f in d["flat"] if f not in ARITH]
    for f in nf:
        qs = [q_of(a[f][i] - a[f][0], [a[h][i] - a[h][0] for h in af]) for i in range(1, G)]
        early = np.mean(qs[: max(1, (G - 1) // 3)]); allq.append(np.mean(qs))
        print(f"  {traj:12s} {f:15s} mean q over grid {np.mean(qs):.2f} (first third {early:.2f}, at endpoint {qs[-1]:.2f}); arithmetic flat pool n={len(af)}")
print(f"mean over {len(allq)} non-arithmetic flat rungs: {np.mean(allq):.3f}")
