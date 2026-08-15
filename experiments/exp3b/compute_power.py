"""Exact power from the frozen floors (design §7, open item 6).

For each rung: the critical count under a one-sided exact binomial against
the rung's committed floor at alpha = .01 / 8 (Bonferroni across the eight
probe-size trained cells, n = 500), power at a grid of true first-character
rates, and the blind region [floor, crit/n) inside which a true rate is
indistinguishable from floor at this design's resolution.

Reads the floors through analyze_3b.load_floors — sha-pinned and
recompute-asserted — so this table can never be computed against floors the
verdict would not use. Output committed as `power.json`; the design doc's
§7 numbers (crit 46/500 at floor .056, power .980 at .12 and .745 at .10;
crit 44 at .054) are asserted, not trusted.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from scipy.stats import binom

EXP3B = Path(__file__).resolve().parent
if str(EXP3B.parent.parent) not in sys.path:
    sys.path.insert(0, str(EXP3B.parent.parent))

from experiments.exp3b.analyze_3b import (  # noqa: E402
    ALPHA, N_PROBE_TESTS, RUNGS, load_floors,
)

N = 500
TRUE_RATES = (0.06, 0.075, 0.09, 0.10, 0.12, 0.15, 0.20)
OUT = EXP3B / "power.json"

# design §7's quoted values, asserted against the recompute
DESIGN_QUOTES = {"rev_string7": {"crit": 46, "power": {0.12: 0.98, 0.10: 0.745}},
                 "reverse_string": {"crit": 44}}


def critical_count(floor: float, *, n: int = N, alpha: float = ALPHA,
                   n_tests: int = N_PROBE_TESTS) -> int:
    """Smallest count whose one-sided p against `floor` clears the
    Bonferroni-corrected alpha."""
    a = alpha / n_tests
    return next(k for k in range(n + 1) if float(binom.sf(k - 1, n, floor)) < a)


def main() -> dict:
    floors = load_floors()
    out = {"n": N, "alpha": ALPHA, "n_tests": N_PROBE_TESTS,
           "true_rates": list(TRUE_RATES), "rungs": {}}
    for rung in RUNGS:
        f = floors[rung]["primary"]
        crit = critical_count(f)
        power = {str(t): float(binom.sf(crit - 1, N, t)) for t in TRUE_RATES}
        out["rungs"][rung] = {
            "floor": f, "critical_count": crit, "critical_acc": crit / N,
            "power": power,
            "blind_region": [f, crit / N],
        }
        q = DESIGN_QUOTES.get(rung, {})
        if "crit" in q:
            assert crit == q["crit"], (
                f"{rung}: critical count {crit} does not match the design "
                f"doc's {q['crit']} — surface this, do not overwrite")
        for t, want in q.get("power", {}).items():
            got = float(binom.sf(crit - 1, N, t))
            assert abs(got - want) < 5e-3, (
                f"{rung}: power {got:.4f} at true rate {t} vs design's {want}")
    OUT.write_text(json.dumps(out, indent=1))
    return out


if __name__ == "__main__":
    r = main()
    for rung, d in r["rungs"].items():
        pw = {t: round(v, 3) for t, v in d["power"].items()}
        print(f"{rung}: floor {d['floor']} crit {d['critical_count']}/{N} "
              f"(acc {d['critical_acc']:.3f}) power {pw}")
    print(f"wrote {OUT}")
