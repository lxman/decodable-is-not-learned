"""Natural-arm pool trend — the diagnostic that names the FAIL variant.

WRITTEN AFTER THE FREEZE, AND THIS IS A GAP, DISCLOSED.

`analyze_1c.verdict()` accepts `natural_l0_tracks_pool` as an INPUT but the
frozen module contains no function that computes it. That quantity selects
between two named results — `FAIL (layer-0 leakage)` when the mechanism is
confirmed and `FAIL (layer-0, mechanism unconfirmed)` when it is not — so it
is verdict-ADJACENT even though it is not verdict-touching.

This is the same class of gap 1b hit: `analyze_1b.py` was frozen with a
`verdict()` and no record loader, and the glue had to be written after the
campaign ran. 1c fixed that one (the loader IS frozen) and then reproduced
the pattern one level over. Recorded rather than quietly patched.

WHAT IS AND IS NOT PREREGISTERED HERE:

  preregistered   The RULE. Design §4: "Every Stage B cell is therefore
                  additionally profiled at its natural pool size
                  (866 / 773 / 659 / 536), and L is regressed on pool size
                  across that arm." That sentence was frozen at
                  `exp1c-preregistered`, before any probe ran.
  NOT frozen      This implementation, written 2026-08-14 after Stage B
                  completed. It is a faithful transcription of the frozen
                  sentence and nothing more: same block structure, same
                  within-block relabeling null, same one-sided direction as
                  the primary test, differing only in the regressor (pool
                  size instead of density) and the outcome (L instead of M).

DIRECTION. "L tracks pool size" means L is LARGER where the pool is LARGER,
i.e. a positive slope on pool size. Because the pool shrinks monotonically as
density rises, that is the same as a NEGATIVE slope on density — the opposite
sign to the accumulation the primary test looks for. The two hypotheses point
in opposite directions along the axis, which is what makes the diagnostic
informative rather than decorative.
"""

from __future__ import annotations

from itertools import permutations

import numpy as np

from experiments.exp1c import analyze_1c as a

_TIE_TOL = 1e-12


def pool_trend(cells, *, field: str = "l0_margin", n_draw: int = 100_000,
               seed: int = 0) -> dict:
    """Regress `field` on pool size, blocked on (size, seed), one-sided positive.

    `cells` are natural-arm cells from `analyze_1c.assemble_cells`, each
    carrying `n_rows` (the natural pool) and the margin of interest.
    """
    grouped: dict[tuple, list] = {}
    for c in cells:
        grouped.setdefault((c["size_bucket"], c["seed"]), []).append(
            (float(c["n_rows"]), float(c[field])))

    blocks = [sorted(v) for v in grouped.values() if len(v) == len(a.DENSITIES)]
    if not blocks:
        raise ValueError("no live blocks on the natural arm")

    perms = np.asarray(list(permutations(range(len(a.DENSITIES)))))
    rng = np.random.default_rng(seed)

    obs = 0.0
    xs, ys = [], []
    for b in blocks:
        x = np.array([p for p, _ in b])
        y = np.array([m for _, m in b])
        x = x - x.mean()                    # centre WITHIN block, as the
        obs += float((x * y).sum())         # primary test centres density
        xs.append(x)
        ys.append(y)

    null = np.zeros(n_draw)
    for x, y in zip(xs, ys):
        idx = rng.integers(0, len(perms), size=n_draw)
        null += (x[perms[idx]] * y).sum(axis=1)

    denom = sum(float((x ** 2).sum()) for x in xs)
    p = (int(np.sum(null >= obs - _TIE_TOL)) + 1) / (n_draw + 1)
    return {"slope": obs / denom, "p": p, "n_blocks": len(blocks),
            "tracks_pool": bool(p < a.ALPHA and obs > 0)}
