"""Order-statistics bounds for fire classification (design §4, open
item 4). All bounds derive from the mechanism that generates floor
fires: an at-floor fire beat all N permuted fits, so its accuracy lives
in the distribution of the max of N null draws. Quantile of the max:
P(max <= z) = Phi(z)^N  =>  z_q = Phi^-1(q^(1/N)), in null-SD units."""

from scipy.stats import norm

def max_quantile(n: int, q: float) -> float:
    return float(norm.ppf(q ** (1.0 / n)))

TIER1_BAR = max_quantile(500, 0.99)
GATE2_TOLERATED = (max_quantile(2500, 0.005), max_quantile(2500, 0.995))
GATE2_ABORT = max_quantile(2500, 1 - 1e-4)

def classify_fire(acc: float, null_mean: float, null_sd: float,
                  at_floor: bool) -> str:
    if not at_floor:
        return "not_fire"
    z = (acc - null_mean) / null_sd
    lo, hi = GATE2_TOLERATED
    if z <= hi:
        return "tolerated"          # includes z < lo: never punish weak
    if z <= GATE2_ABORT:
        return "elevated"           # feeds the binomial count test only
    return "structural_abort"
