import json, sys, itertools, numpy as np
sys.path.insert(0, "/Users/michaeljordan/emergence-paper")
from experiments.exp2d.battery_2d import FAMILY_OF
ARITH = {"add3_mid","sub3_mid","add4_mid","sub4_mid","add_base8","sub_base8","arith_next","quad_next","count_div13","count_div7","median5","median7","oct2dec","base7","base12_digitsum","base13","mod13","mod13_comp","mod17","mod19","isqrt_gap","collatz_step2","roman_sum7","clock24","clock24_d999"}
S = json.load(open(sys.argv[1]))
def q_of(val, pool):
    pool = np.asarray(pool); return (np.sum(pool < val) + .5 * np.sum(pool == val)) / len(pool)
def cells_of(S, rising_ok=lambda r: True, flat_ok=lambda f: True):
    out = []
    for traj, d in S.items():
        a = d["a"]; flat = [f for f in d["flat"] if flat_ok(f)]
        for r, c in d["clear_index"].items():
            if c < 2 or not rising_ok(r) or len(flat) < 3: continue
            i = c - 1; g = lambda rr: a[rr][i] - a[rr][0]
            out.append({"traj": traj, "rung": r, "q": q_of(g(r), [g(f) for f in flat]), "nF": len(flat)})
    return out
def signflip(cells, key):
    blocks = sorted({key(c) for c in cells}); idx = {b: i for i, b in enumerate(blocks)}
    sums = np.zeros(len(blocks))
    for c in cells: sums[idx[key(c)]] += c["q"] - .5
    n = len(blocks); obs = sums.sum()
    if n <= 20:
        signs = np.array(list(itertools.product((1, -1), repeat=n))); tot = signs @ sums
    else:
        tot = np.random.default_rng(0).choice((1, -1), size=(100000, n)) @ sums
    return n, float(np.mean(tot >= obs - 1e-12))
for label, cs in (("ALL cells vs ALL flat", cells_of(S)),
                  ("ARITHMETIC rising vs ARITHMETIC flat", cells_of(S, lambda r: r in ARITH, lambda f: f in ARITH)),
                  ("NON-arithmetic rising vs ALL flat", cells_of(S, lambda r: r not in ARITH))):
    U = np.mean([c["q"] for c in cs]); nr, pr = signflip(cs, lambda c: c["rung"]); nf, pf = signflip(cs, lambda c: FAMILY_OF[c["rung"]])
    print(f"{label}: n={len(cs)} U={U:.4f} | rung-level sign-flip ({nr} rungs) p={pr:.4f} | family-block ({nf} families) p={pf:.4f}")
    for t in S:
        sub = [c["q"] for c in cs if c["traj"] == t]
        if sub: print(f"     {t}: n={len(sub)} U={np.mean(sub):.3f}")
