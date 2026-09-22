"""Design-session computation 3 (disclosed): power envelope for a PERFORMABILITY-grain primary
(binary clear at 2d's bar per read; between-size discordance minus within-size discordance;
rung-block exact sign flip). A model, not a measurement. Retired the read as the primary."""
import numpy as np, itertools
rng = np.random.default_rng(5)

def one_battery(n_cells_per_rung, e, q, delta, rng):
    blocks = []
    for n in n_cells_per_rung:
        cs = []
        for _ in range(n):
            truly_disc = rng.random() < q
            trueL = 1 if truly_disc else 0
            sigma = 0
            rA = [trueL ^ (rng.random() < e) for _ in range(2)]
            if rA[0] != rA[1]:
                continue
            d_real = 1 if rA[0] != sigma else 0
            dps = []
            for side in range(2):
                trueB = trueL ^ (rng.random() < delta)
                rB = [trueB ^ (rng.random() < e) for _ in range(2)]
                if rB[0] != rB[1]:
                    continue
                dps.append(1 if rB[0] != rA[0] else 0)
            if not dps:
                continue
            cs.append(d_real - np.mean(dps))
        blocks.append(np.array(cs))
    allc = np.concatenate(blocks) if blocks else np.array([])
    if len(allc) < 20:
        return None
    T = allc.mean()
    sums = np.array([b.sum() for b in blocks if len(b)])
    k = len(sums)
    if k <= 16:
        signs = np.array(list(itertools.product([1, -1], repeat=k)))
    else:
        signs = rng.choice([1, -1], size=(10000, k))
    null = (signs * sums).sum(1) / len(allc)
    return T, (null >= T - 1e-12).mean()

print("cells/rung profile A: 11 rungs x ~6 cells (66 live); profile B: 7 rungs x 4 (28 live)")
for label, prof in (("A", [6] * 11), ("B", [4] * 7)):
    for e in (0.05, 0.10, 0.15):
        for q in (0.0, 0.15, 0.25, 0.35):
            res = [one_battery(prof, e, q, 0.05, rng) for _ in range(400)]
            res = [r for r in res if r]
            T = np.array([r[0] for r in res]); p = np.array([r[1] for r in res])
            fire = ((p < 0.01) & (T >= 0.10)).mean()
            print(f"profile {label} e={e:.2f} q={q:.2f}: mean T {T.mean():+.3f} sd {T.std():.3f}  P(NOT-MATCHED) {fire:.2f}  P(p<.01) {(p<0.01).mean():.2f}")
