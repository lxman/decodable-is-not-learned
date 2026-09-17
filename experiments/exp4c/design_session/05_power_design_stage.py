import sys, itertools, json, numpy as np
sys.path.insert(0, "/Users/michaeljordan/emergence-paper")
from experiments.exp2d.battery_2d import FAMILY_OF
ARITH = {"add3_mid","sub3_mid","add4_mid","sub4_mid","add_base8","sub_base8","arith_next","quad_next","count_div13","count_div7","median5","median7","oct2dec","base7","base12_digitsum","base13","mod13","mod13_comp","mod17","mod19","isqrt_gap","collatz_step2","roman_sum7","clock24","clock24_d999"}
R69 = ["add3_mid","add_base8","antonym","antonym6","arith_next","count_div13","odd6","sub_base8"]
R13 = ["add3_mid","add4_mid","add_base8","antonym","antonym6","arith_next","count_div13","median5","median7","oct2dec","odd6","odd_one_out","quad_next","rev_string7","reverse_string","sub3_mid","sub4_mid","sub_base8"]
cells = [("6.9b", r, 24) for r in R69] + [("13b", r, 15) for r in R13]
fams = sorted({FAMILY_OF[r] for _, r, _ in cells}); fi = np.array([fams.index(FAMILY_OF[r]) for _, r, _ in cells])
ar = np.array([r in ARITH for _, r, _ in cells]); nF = np.array([n for *_, n in cells])
print("cells", len(cells), "families", len(fams), fams, "| arithmetic", int(ar.sum()), "non-arithmetic", int((~ar).sum()))
signs = np.array(list(itertools.product((1, -1), repeat=len(fams)))); rng = np.random.default_rng(1)
def draw(mu, rho):
    # latent normal per cell with a shared rung effect (same rung in both trajectories correlated rho), mapped to a discrete rank quantile
    rungs = sorted({r for _, r, _ in cells}); ri = np.array([rungs.index(r) for _, r, _ in cells])
    z = np.sqrt(rho) * rng.standard_normal(len(rungs))[ri] + np.sqrt(1 - rho) * rng.standard_normal(len(cells))
    from math import erf
    u = np.array([.5 * (1 + erf(v / 2 ** .5)) for v in z])          # uniform under the null
    # shift: mean-mu via a power transform u**(1/k) with mean k/(k+1) = mu
    k = mu / (1 - mu); u = u ** (1 / k)
    return (np.floor(u * nF) + .5) / (nF + 0)                          # mid-rank quantile on n_F comparators
def pval(q):
    s = np.zeros(len(fams)); np.add.at(s, fi, q - .5); tot = signs @ s
    return np.mean(tot >= s.sum() - 1e-12)
for label, mu_a, mu_n in (("null", .5, .5), ("uniform lead .60", .60, .60), ("uniform lead .65", .65, .65), ("uniform lead .70", .70, .70), ("in-sample shape (.51 arith / .76 non-arith)", .51, .76)):
    for rho in (0.0, 0.5):
        ps = []
        for _ in range(2000):
            mu = np.where(ar, mu_a, mu_n); q = np.array([draw(m, rho)[j] for j, m in enumerate(mu)]) if mu_a != mu_n else draw(mu_a, rho)
            ps.append(pval(q))
        ps = np.array(ps); print(f"  {label:45s} rho={rho}: P(p<.01)={np.mean(ps < .01):.3f}  P(p<.05)={np.mean(ps < .05):.3f}")
