import json, sys, numpy as np
S = json.load(open(sys.argv[1])); rng = np.random.default_rng(0); B = 10000
def q_of(val, pool):
    pool = np.asarray(pool); return (np.sum(pool < val) + .5 * np.sum(pool == val)) / len(pool)
cells = []
for traj, d in S.items():
    a = d["a"]; flat = d["flat"]
    for r, c in d["clear_index"].items():
        if c < 2: continue
        i = c - 1
        g = lambda rr: a[rr][i] - a[rr][0]
        cells.append({"traj": traj, "rung": r, "c": c, "G": len(d["steps"]), "q": q_of(g(r), [g(f) for f in flat]), "nF": len(flat)})
def placebo(cells):
    T = np.zeros(B)
    for b in range(B):
        qs = []
        for cl in cells:
            d = S[cl["traj"]]; flat = d["flat"]; a = d["a"]; i = cl["c"] - 1
            f = flat[rng.integers(len(flat))]
            qs.append(q_of(a[f][i] - a[f][0], [a[h][i] - a[h][0] for h in flat if h != f]))
        T[b] = np.mean(qs)
    return T
U = np.mean([c["q"] for c in cells]); T = placebo(cells)
print(f"ALL windowed rising cells: n={len(cells)}  mean quantile U={U:.4f}  placebo null mean {T.mean():.4f} SD {T.std():.4f}  p_high={np.mean(T >= U):.4f}")
for traj in S:
    cs = [c for c in cells if c["traj"] == traj]; u = np.mean([c["q"] for c in cs]); Tt = placebo(cs) if cs else None
    print(f"  {traj}: n={len(cs)} nF={cs[0]['nF']}  U={u:.3f}  null SD {Tt.std():.3f}  p_high={np.mean(Tt >= u):.3f}  q: " + " ".join(f"{c['rung']}@{c['c']}={c['q']:.2f}" for c in cs))
