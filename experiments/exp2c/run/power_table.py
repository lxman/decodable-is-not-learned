# experiments/exp2c/run/power_table.py
"""MC calibration + power under the family-correlation model (design
§5, open item 1). Latent model per simulated battery: family effect
u_f ~ N(0,1); rung latents x = sqrt(rho_family)*u_f + sqrt(1-rho)*e for
BOTH the margin variable and (independently under H0) the ascent
variable; under H1 the two latents share a common component scaled to
target Spearman rho_true. Observed values are the latents' ranks —
Gaussian copula, so Spearman's rho is what the shared scale controls.
The naive test is the ordinary 1e5-draw permutation p on rungs; the
calibrated cutoff is the largest naive-p threshold whose rejection rate
under the family H0 is <= .01."""

import itertools
import json
import math
from pathlib import Path

import numpy as np
from scipy.stats import rankdata, spearmanr

try:  # `experiments.exp2c.run.power_table` (pytest / absolute import)
    from ..battery import family_map
except ImportError:  # pragma: no cover - `python -m run.power_table` from exp2c/
    from battery import family_map


def _battery(rng, families, rho_family, shared):
    xs, ys = [], []
    for size in families:
        uf_x, uf_y = rng.normal(size=2)
        for _ in range(size):
            c = rng.normal() * shared
            ex = np.sqrt(rho_family) * uf_x + \
                np.sqrt(1 - rho_family) * rng.normal()
            ey = np.sqrt(rho_family) * uf_y + \
                np.sqrt(1 - rho_family) * rng.normal()
            xs.append(ex + c)
            ys.append(ey + c)
    return np.array(xs), np.array(ys)


def _naive_perm_p_loop(x, y, rng, n_perm=2000):
    """Reference implementation, verbatim from the plan text (task-9 brief
    Step 3). Kept as the ground truth the vectorized `_naive_perm_p` is
    guarded against (exact p-value equality, test_naive_perm_p_equivalence);
    plan-deviation ruling ledgered in PROGRESS.md 2026-07-29."""
    obs = spearmanr(x, y).statistic
    perms = np.array([spearmanr(x, rng.permutation(y)).statistic
                      for _ in range(n_perm)])
    return (1 + np.sum(perms >= obs)) / (n_perm + 1)


def _naive_perm_p(x, y, rng, n_perm=2000):
    """Vectorized equivalent of `_naive_perm_p_loop` (ruling 2026-07-29).
    Rank-transforms once with rankdata's average-rank semantics (spearmanr's
    own ranking); draws the permutations with the SAME `rng.permutation`
    call sequence as the loop (`rng.permutation(n)` consumes the identical
    RNG stream as `rng.permutation(y)`, and rankdata is permutation-
    equivariant, so ranking-then-permuting equals permuting-then-ranking);
    vectorizes only the Pearson-on-ranks arithmetic. The observed statistic
    goes through the same vectorized arithmetic as the permuted ones, so
    the `perms >= obs` lattice ties resolve exactly as in the loop version
    (rank products are dyadic rationals summed exactly in float64). The
    p-value formula is unchanged."""
    n = len(y)
    rx = rankdata(x)
    ry = rankdata(y)
    idx = np.stack([rng.permutation(n) for _ in range(n_perm)])

    rxc = rx - rx.mean()
    ryc = ry - ry.mean()
    dx = np.sqrt(rxc @ rxc / (n - 1))
    dy = np.sqrt(ryc @ ryc / (n - 1))  # permutation-invariant

    # mirror np.corrcoef's sequential divisions ((cov/dx)/dy) and clip
    obs = np.clip((rxc @ ryc / (n - 1)) / dx / dy, -1.0, 1.0)
    covs = (ryc[idx] @ rxc) / (n - 1)
    perms = np.clip(covs / dx / dy, -1.0, 1.0)
    return (1 + np.sum(perms >= obs)) / (n_perm + 1)


def _shared_for_target_rho(rho_true):
    # calibrate the shared-component scale so pop Spearman ~= rho_true
    return np.sqrt(rho_true / max(1e-9, (1 - rho_true))) if rho_true < 1 else 10.0


def simulate(families, rho_family, rho_true, n_sims=1000, seed=0,
             n_perm=1000):
    rng = np.random.default_rng(seed)
    null_ps, alt_ps = [], []
    for _ in range(n_sims):
        x0, y0 = _battery(rng, families, rho_family, shared=0.0)
        null_ps.append(_naive_perm_p(x0, y0, rng, n_perm))
        x1, y1 = _battery(rng, families, rho_family,
                          shared=_shared_for_target_rho(rho_true))
        alt_ps.append(_naive_perm_p(x1, y1, rng, n_perm))
    null_ps, alt_ps = np.sort(null_ps), np.array(alt_ps)
    k = max(0, int(np.floor(0.01 * len(null_ps))) - 1)
    cutoff = float(null_ps[k]) if len(null_ps) else 0.01
    return {"calibrated_cutoff": cutoff,
            "alpha_at_cutoff": float(np.mean(np.array(null_ps) <= cutoff)),
            "power": float(np.mean(alt_ps <= cutoff)),
            "naive_p_dist": [float(null_ps[i])
                             for i in (0, len(null_ps) // 2, -1)]}


HERE = Path(__file__).resolve().parent.parent   # experiments/exp2c
RESULTS = HERE / "results"
ITEMS_DIR = HERE / "battery" / "items"
SCREEN_DIR = RESULTS / "screen"

RHO_TRUE_VALUES = (0.0, 0.5, 0.6, 0.7, 0.8)
FRAGILITY_DELTA = 0.2
N_SIMS = 5000
N_PERM = 5000


# --------------------------------------- exact family-block permutation
# (design doc Sec 5 preregistered fallback; adopted by ruling 2026-08-01
# after the calibrated-naive test's cutoff was found to depend 5.1x on
# the uninformed rho_family=0.5 fallback -- see PROGRESS.md. Everything
# below is new machinery; `simulate`/`_naive_perm_p*` above are untouched.)

EXACT_PERM_GUARD = 5_000_000  # exact_block_perms raises above this count


def _block_perm_offsets(families: list[int]):
    """Shared offset/grouping bookkeeping for `exact_block_perms` and
    `sampled_block_perms` (factored out for the sampled-permutation
    extension, growth ruling 2026-08-01, rather than duplicated between
    them). Returns `(n, offsets, group_items)`: `n` is the total rung
    count; `offsets[i]` is block `i`'s starting rung index; `group_items`
    is `[(size, [block indices]), ...]`, grouping same-size families in
    the order those sizes FIRST appear in `families` -- the same
    iteration order `exact_block_perms` always used, preserved here so
    its output is unaffected by the refactor."""
    families = list(families)
    n = sum(families)
    offsets = np.cumsum([0] + families)[:-1].tolist()

    size_groups: dict[int, list[int]] = {}
    for block_idx, size in enumerate(families):
        size_groups.setdefault(size, []).append(block_idx)
    group_items = list(size_groups.items())
    return n, offsets, group_items


def _block_perm_total(group_items) -> int:
    """Total block-permutation group size (product of per-same-size-group
    factorials), given `group_items` from `_block_perm_offsets`. Shared by
    `exact_block_perms`'s guard check and `exact_block_p`/`simulate_exact`'s
    enumerate-vs-sample routing, so both always agree on what "the group
    size" is for a given `families` shape."""
    total = 1
    for _, block_idxs in group_items:
        total *= math.factorial(len(block_idxs))
    return total


def _compose_block_perm_row(n, offsets, group_items, combo) -> np.ndarray:
    """Build one composed same-size-block-permutation index row from
    `combo` (a tuple of per-group donor-position sequences, one per
    `group_items` entry -- `combo[g][slot_pos]` is the donor position
    within group g's blocks for recipient slot `slot_pos`). Shared row-
    construction arithmetic for `exact_block_perms` (looping combos from
    `itertools.product`, exhaustive) and `sampled_block_perms` (looping
    i.i.d. uniform combos) -- within-block order is always preserved
    position-for-position (donor block's i-th rung -> recipient block's
    i-th position), matching `exact_block_perms`'s documented exchange
    convention exactly, since both callers route through this one
    function rather than each re-implementing it."""
    idx = np.empty(n, dtype=np.int64)
    for (size, block_idxs), perm in zip(group_items, combo):
        for slot_pos, donor_pos in enumerate(perm):
            recipient_block = block_idxs[slot_pos]
            donor_block = block_idxs[donor_pos]
            r0 = offsets[recipient_block]
            d0 = offsets[donor_block]
            idx[r0:r0 + size] = np.arange(d0, d0 + size)
    return idx


def exact_block_perms(families: list[int]) -> np.ndarray:
    """Enumerate every family-block permutation for the exact fallback
    test (design Sec 5; ruling 2026-08-01).

    Layout convention: rungs are laid out as CONTIGUOUS per-family
    blocks, in the order given by `families` (block i occupies rung
    indices sum(families[:i]) .. sum(families[:i+1])) -- the same
    contiguous-block layout `_battery`/`simulate` already produce and
    consume. Callers (including the future analyze.py amendment, queued
    separately) must arrange their x/y rung-score arrays into that same
    per-family-contiguous order before calling this or `exact_block_p`;
    this module does not carry family labels alongside x/y, only the
    `families` size vector, so the caller owns getting the grouping
    right (e.g. via `family_map.scored_battery_families()`'s iteration
    order, which is what `family_sizes()` -- used below -- is derived
    from).

    Exchange convention: under H0, ascent-score family BLOCKS are
    exchangeable among families of the SAME SIZE only -- a size-4
    family's block can swap only with another size-4 family's block,
    never with a size-2 family's. Within a block, rung order is
    preserved across the swap: the donor block's i-th rung maps to the
    recipient family's i-th rung position (position-for-position, not
    re-permuted internally). x (probe scores) is never touched by this
    function; it stays fixed to rung identity. Only y (ascent scores) is
    block-permuted downstream, via row-gather (`y[idx]`) on the index
    matrix this function returns.

    Enumeration is exact and exhaustive, not sampled: for a same-size
    group with m families, the number of block-reassignments is m! (a
    full bijection of that group's blocks onto that group's family
    slots); the total permutation count is the product of m! across all
    same-size groups (order of `families` does not affect the total,
    only which rung indices fall in which block). The identity
    assignment is always included -- for every group, the identity
    permutation is one of its m! members -- so the smallest achievable
    exact p-value is 1/N_total.

    Returns an (N_total, n_rungs) int64 index matrix; row r is a
    permutation `idx` such that `y[idx]` is the r-th block-permuted
    ascent-score vector. Deterministic and RNG-free: row order follows
    `itertools.permutations`/`itertools.product`'s fixed lexicographic
    order (over range(m) per same-size group, product taken across
    groups in the order those group-sizes first appear in `families`),
    so identical `families` input always yields identical output,
    including row order -- row 0 is always the full identity
    permutation (each group's first-yielded permutation is its own
    identity, and `itertools.product` yields the all-first-elements
    combination first).

    Raises ValueError if the exact total (product of per-group
    factorials) exceeds `EXACT_PERM_GUARD` (5e6) -- computed BEFORE any
    row is generated, so an oversized shape fails fast rather than
    silently exploding memory/time. Escalate rather than raising the
    guard."""
    families = list(families)
    n, offsets, group_items = _block_perm_offsets(families)

    total = _block_perm_total(group_items)
    if total > EXACT_PERM_GUARD:
        raise ValueError(
            f"exact_block_perms: {total} permutations for families="
            f"{families} exceeds the guard ({EXACT_PERM_GUARD}); "
            f"enumeration would not fit the documented guard -- escalate "
            f"instead of raising it.")

    group_perm_lists = [list(itertools.permutations(range(len(block_idxs))))
                        for _, block_idxs in group_items]

    rows = np.empty((total, n), dtype=np.int64)
    for row_i, combo in enumerate(itertools.product(*group_perm_lists)):
        rows[row_i] = _compose_block_perm_row(n, offsets, group_items, combo)
    return rows


def sampled_block_perms(families: list[int], m: int,
                        rng: np.random.Generator) -> np.ndarray:
    """`m` i.i.d. uniform draws from the SAME block-permutation group
    `exact_block_perms` enumerates exhaustively (sampled-permutation
    extension, growth ruling 2026-08-01, for shapes whose group size
    exceeds `EXACT_PERM_GUARD`). Each row independently draws a uniform
    permutation WITHIN EVERY same-size family group (via
    `rng.permutation`, which draws uniformly over the symmetric group of
    that size) and composes them into one rung-index row via
    `_compose_block_perm_row` -- the same offset bookkeeping and
    within-block-order-preservation `exact_block_perms` uses, reused via
    `_block_perm_offsets`/`_compose_block_perm_row` rather than
    duplicated here.

    Rows are NOT filtered for distinctness and the identity permutation
    is NOT excluded: each row is simply an independent uniform draw from
    the group, so repeats (including the identity) occur with their true
    group-theoretic probability, exactly as the statistical spec
    requires (growth ruling 2026-08-01). No enumeration guard applies
    here -- `m` is caller-controlled and unrelated to the (possibly
    astronomically large) exact group size that would trip
    `EXACT_PERM_GUARD`.

    Returns an `(m, n_rungs)` int64 index matrix; row order carries no
    meaning (unlike `exact_block_perms`, there is no lexicographic
    guarantee and row 0 is not guaranteed to be the identity)."""
    families = list(families)
    n, offsets, group_items = _block_perm_offsets(families)
    rows = np.empty((m, n), dtype=np.int64)
    for row_i in range(m):
        combo = tuple(rng.permutation(len(block_idxs))
                     for _, block_idxs in group_items)
        rows[row_i] = _compose_block_perm_row(n, offsets, group_items, combo)
    return rows


def _exact_block_p_from_perms(x, y, perms: np.ndarray) -> dict:
    """Shared arithmetic for `exact_block_p`/`simulate_exact`: rank-Pearson
    on ranks (average-rank ties, matching `_naive_perm_p`'s convention),
    one matmul across all rows of `perms`. `dy` is computed once from the
    unpermuted ranks -- permutation-invariant, since every row is a
    rearrangement of the same rank multiset. `perms` row 0 is the
    identity (see `exact_block_perms`), so `rhos[0]` is bit-identical to
    `obs` (same arithmetic, same values) and the identity always counts
    toward `p`'s numerator -- the min achievable p is 1/n_perms."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    n = len(x)
    rx = rankdata(x)
    ry = rankdata(y)
    rxc = rx - rx.mean()
    ryc = ry - ry.mean()
    dx = np.sqrt(rxc @ rxc / (n - 1))
    dy = np.sqrt(ryc @ ryc / (n - 1))  # permutation-invariant

    obs = np.clip((rxc @ ryc / (n - 1)) / dx / dy, -1.0, 1.0)
    ryc_perm = ryc[perms]                 # (n_perms, n)
    covs = (ryc_perm @ rxc) / (n - 1)     # one matmul for all correlations
    rhos = np.clip(covs / dx / dy, -1.0, 1.0)

    n_perms = perms.shape[0]
    count = int(np.sum(rhos >= obs))
    return {
        "p": count / n_perms,
        "rho_obs": float(obs),
        "n_perms": int(n_perms),
        "resolution": 1.0 / n_perms,
    }


def _sampled_block_p_from_perms(x, y, perms: np.ndarray) -> dict:
    """Add-one p-value convention for the SAMPLED block-permutation test
    (sampled-permutation extension, growth ruling 2026-08-01 statistical
    spec): p = (1 + #{sampled rho >= rho_obs}) / (M + 1). This is the
    standard sampled-permutation-test convention that preserves
    P(p <= t) <= t under H0 for ANY M -- the observed statistic is
    treated as one additional draw alongside the M sampled ones, so the
    smallest achievable p is 1/(M+1) rather than 0 (unlike the exhaustive
    enumeration's exact count/n_perms, p can never be exactly zero here
    no matter how extreme rho_obs is).

    Deliberately a SEPARATE function from `_exact_block_p_from_perms`
    (not a shared-formula refactor of it) so the enumerated path's
    byte-exact p = count/n_perms formula stays completely untouched by
    this extension -- the rank-Pearson arithmetic below is intentionally
    duplicated, not extracted, to keep that non-interference obviously
    true by inspection rather than by tracing a shared code path."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    n = len(x)
    rx = rankdata(x)
    ry = rankdata(y)
    rxc = rx - rx.mean()
    ryc = ry - ry.mean()
    dx = np.sqrt(rxc @ rxc / (n - 1))
    dy = np.sqrt(ryc @ ryc / (n - 1))  # permutation-invariant

    obs = np.clip((rxc @ ryc / (n - 1)) / dx / dy, -1.0, 1.0)
    ryc_perm = ryc[perms]                 # (m, n)
    covs = (ryc_perm @ rxc) / (n - 1)     # one matmul for all correlations
    rhos = np.clip(covs / dx / dy, -1.0, 1.0)

    m = perms.shape[0]
    count = int(np.sum(rhos >= obs))
    return {
        "p": (1 + count) / (m + 1),
        "rho_obs": float(obs),
        "n_perms": int(m),
        "resolution": 1.0 / (m + 1),
    }


def exact_block_p(x, y, families, *, max_enumerate=EXACT_PERM_GUARD,
                  n_sample=100_000, seed=0) -> dict:
    """Exact (or, for oversized shapes, sampled) one-sided family-block
    permutation p-value (design Sec 5 fallback; sampled extension per
    growth ruling 2026-08-01): enumerates every block permutation via
    `exact_block_perms` and counts how many yield Spearman rho >= the
    observed rho (identity included). No RNG -- deterministic given
    (x, y, families). Returns `{p, rho_obs, n_perms, resolution}`
    (resolution = 1/n_perms), all required by the design's "achievable
    permutation count and resolution stated" clause.

    Extended (growth ruling 2026-08-01): when the exact block-permutation
    group size exceeds `max_enumerate` (default `EXACT_PERM_GUARD`, 5e6
    -- the same threshold `exact_block_perms` itself guards at), routes
    to `sampled_block_perms` instead of `exact_block_perms`, drawing
    `n_sample` (default 100_000) i.i.d. uniform group elements with a
    seeded `np.random.default_rng(seed)` and computing an add-one
    p-value via `_sampled_block_p_from_perms` rather than the exact
    count/n_perms formula. BELOW the threshold, behavior is
    BYTE-UNCHANGED from before this extension (same enumeration, same
    `_exact_block_p_from_perms` call, same dict) -- only a `"method"`
    key is added: `"enumerated"` below the threshold, `"sampled"` above
    it (in the sampled case the dict's `n_perms`/`resolution` reflect
    `n_sample`/1/(n_sample+1), per `_sampled_block_p_from_perms`, not the
    unenumerated exact group size).

    Raises ValueError if len(x) or len(y) disagrees with sum(families)
    -- the caller mis-grouped its rung arrays (see the layout convention
    in exact_block_perms) and should get a named mismatch, not a matmul
    traceback."""
    n = sum(families)
    if len(x) != n or len(y) != n:
        raise ValueError(
            f"exact_block_p: sum(families)={n} but len(x)={len(x)}, "
            f"len(y)={len(y)} -- x/y must cover exactly the rungs of "
            f"`families`, laid out as contiguous per-family blocks "
            f"(see exact_block_perms's layout convention).")

    _, _, group_items = _block_perm_offsets(families)
    total = _block_perm_total(group_items)

    if total <= max_enumerate:
        perms = exact_block_perms(families)
        result = _exact_block_p_from_perms(x, y, perms)
        result["method"] = "enumerated"
        return result

    rng = np.random.default_rng(seed)
    perms = sampled_block_perms(families, n_sample, rng)
    result = _sampled_block_p_from_perms(x, y, perms)
    result["method"] = "sampled"
    return result


def simulate_exact(families, rho_family, rho_true, n_sims=1000, seed=0, *,
                   max_enumerate=EXACT_PERM_GUARD, n_sample=100_000):
    """Exact-test analogue of `simulate` (design Sec 5 fallback). Reuses
    `_battery`'s latent model and `_shared_for_target_rho`'s effect-size
    calibration UNCHANGED; the only difference from `simulate` is that
    each sim's p-value comes from exact enumeration (`exact_block_perms`
    / `_exact_block_p_from_perms`) rather than the naive MC permutation
    test, so there is no RNG in the test itself and no calibration step
    -- the cutoff is fixed at .01 (the design's alpha target) rather than
    estimated. `exact_block_perms(families)` is computed once and reused
    across all `n_sims` sims (families is fixed for the whole call).

    Extended (growth ruling 2026-08-01): when the exact block-permutation
    group size exceeds `max_enumerate`, routes to `sampled_block_perms`
    instead -- drawn ONCE, like the enumerated `perms`, and reused across
    all `n_sims` sims, consuming from the SAME seeded `rng` the sim
    loop's `_battery` draws use (so `seed` alone still determines the
    whole run) -- and scores every sim's p-value via
    `_sampled_block_p_from_perms`'s add-one convention instead of
    `_exact_block_p_from_perms`'s exact count/n_perms formula. BELOW the
    threshold, behavior (including RNG consumption order) is
    BYTE-UNCHANGED from before this extension.

    Returns `power` (fraction of H1 sims with p < .01), `alpha` (fraction
    of H0 sims with p < .01 -- bounded <= .01 by construction under exact
    permutation exchangeability, since x and y are independent draws when
    shared=0.0; reported as observed, not assumed), plus `n_perms`,
    `resolution` (shared across all sims, since they depend only on
    `families`), and `method` ("enumerated" or "sampled")."""
    rng = np.random.default_rng(seed)

    _, _, group_items = _block_perm_offsets(families)
    total = _block_perm_total(group_items)
    if total <= max_enumerate:
        perms = exact_block_perms(families)
        method = "enumerated"
        p_from_perms = _exact_block_p_from_perms
        n_perms = perms.shape[0]
        resolution = 1.0 / n_perms
    else:
        perms = sampled_block_perms(families, n_sample, rng)
        method = "sampled"
        p_from_perms = _sampled_block_p_from_perms
        n_perms = perms.shape[0]
        resolution = 1.0 / (n_perms + 1)

    null_ps, alt_ps = [], []
    for _ in range(n_sims):
        x0, y0 = _battery(rng, families, rho_family, shared=0.0)
        null_ps.append(p_from_perms(x0, y0, perms)["p"])
        x1, y1 = _battery(rng, families, rho_family,
                          shared=_shared_for_target_rho(rho_true))
        alt_ps.append(p_from_perms(x1, y1, perms)["p"])

    null_ps = np.array(null_ps)
    alt_ps = np.array(alt_ps)
    return {
        "alpha": float(np.mean(null_ps < 0.01)),
        "power": float(np.mean(alt_ps < 0.01)),
        "n_perms": int(n_perms),
        "resolution": float(resolution),
        "method": method,
    }


# ---------------------------------------------------------- exact-test CLI

RHO_FAMILY_EXACT_DEFAULT = 0.5
RHO_FAMILY_SWEEP_EXACT = (0.3, 0.5, 0.7)
RHO_TRUE_FOR_SWEEP_EXACT = 0.6


def _run_power_table_exact(families, *, rho_family=RHO_FAMILY_EXACT_DEFAULT,
                           n_sims=N_SIMS, seed=0,
                           rho_true_values=RHO_TRUE_VALUES,
                           rho_family_sweep=RHO_FAMILY_SWEEP_EXACT,
                           rho_true_for_sweep=RHO_TRUE_FOR_SWEEP_EXACT):
    """Exact-test power table (design Sec 5 fallback): a rho_true sweep at
    a fixed rho_family=0.5, plus a POWER robustness sweep across
    rho_family at rho_true=0.6. Unlike `_run_power_table`'s calibrated-
    naive test, alpha here does not depend on rho_family (the exact
    test's alpha is bounded by construction, not calibrated against a
    nuisance parameter) -- the rho_family sweep demonstrates power
    robustness to that unknown nuisance parameter, not calibration
    fragility; there is no cutoff to drift."""
    runs = {}
    n_perms = resolution = None
    for rho_true in rho_true_values:
        r = simulate_exact(families, rho_family, rho_true,
                           n_sims=n_sims, seed=seed)
        runs[rho_true] = r
        n_perms, resolution = r["n_perms"], r["resolution"]

    power_sweep = {}
    for rho_f in rho_family_sweep:
        power_sweep[rho_f] = simulate_exact(families, rho_f,
                                            rho_true_for_sweep,
                                            n_sims=n_sims, seed=seed)

    return {
        "families": families,
        "n_sims": n_sims,
        "n_perms": n_perms,
        "resolution": resolution,
        "rho_family": rho_family,
        "rho_true_values": list(rho_true_values),
        "runs": {str(k): v for k, v in runs.items()},
        "rho_true_for_sweep": rho_true_for_sweep,
        "power_sweep_rho_family_values": list(rho_family_sweep),
        "power_sweep": {str(k): v for k, v in power_sweep.items()},
    }


def _write_markdown_exact(out: dict, path: Path) -> None:
    lines = [
        "# Experiment 2c: exact family-block permutation power table",
        "",
        "Design Sec 5 preregistered fallback (adopted by ruling "
        "2026-08-01): exact enumeration over same-size family-block "
        "permutations, replacing the rho_family-calibrated naive test. "
        "Alpha is bounded by construction (<= .01, not calibrated); "
        "power still depends on rho_family as a nuisance parameter of "
        "the simulated data -- swept below for robustness, not "
        "calibration fragility.",
        "",
        f"Family sizes: {out['families']}",
        f"n_perms={out['n_perms']}, resolution={out['resolution']:.6g}",
        f"n_sims={out['n_sims']}",
        "",
        "## Power at rho_family=0.5",
        "",
        "| rho_true | alpha | power |",
        "|---|---|---|",
    ]
    for rho_true in out["rho_true_values"]:
        r = out["runs"][str(rho_true)]
        lines.append(f"| {rho_true} | {r['alpha']:.4f} | {r['power']:.4f} |")
    lines += [
        "",
        f"## Power robustness sweep (rho_true={out['rho_true_for_sweep']}, "
        "rho_family varies)",
        "",
        "| rho_family | alpha | power |",
        "|---|---|---|",
    ]
    for rho_f in out["power_sweep_rho_family_values"]:
        r = out["power_sweep"][str(rho_f)]
        lines.append(f"| {rho_f} | {r['alpha']:.4f} | {r['power']:.4f} |")
    lines.append("")
    path.write_text("\n".join(lines))


def main_exact(argv=None) -> None:
    import argparse

    p = argparse.ArgumentParser(
        description="Exact family-block permutation power table "
                    "(design Sec 5 fallback, ruling 2026-08-01)")
    p.add_argument("--items-dir", type=Path, default=None)
    p.add_argument("--screen-dir", type=Path, default=None)
    p.add_argument("--results-dir", type=Path, default=None)
    p.add_argument("--n-sims", type=int, default=N_SIMS)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--out-json", type=Path, default=None)
    p.add_argument("--out-md", type=Path, default=None)
    args = p.parse_args(argv)

    items_dir = args.items_dir or ITEMS_DIR
    screen_dir = args.screen_dir or SCREEN_DIR
    results_dir = args.results_dir or RESULTS
    families = family_map.family_sizes(items_dir, screen_dir)

    out = _run_power_table_exact(families, n_sims=args.n_sims, seed=args.seed)

    out_json = args.out_json or (results_dir / "power_table_exact.json")
    out_md = args.out_md or (results_dir / "power_table_exact.md")
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(out, indent=1))
    _write_markdown_exact(out, out_md)

    print(f"[power_table] wrote {out_json} and {out_md} "
          f"(exact test, families={families})", flush=True)


# ------------------------------------------------------------------- CLI


def _family_sizes(items_dir: Path = ITEMS_DIR,
                  screen_dir: Path = SCREEN_DIR) -> list[int]:
    """Family sizes for the FULL scored battery (ruling 2026-08-01): the
    new-pool specs surviving tier-1 screening, plus the 12 reused 2b
    survivors joining their families. Delegates to family_map.family_sizes,
    which is screen-aware (a rung whose tier-1 verdict is missing or
    "reject" -- e.g. the ejected base12 -- is excluded) and
    reused-inclusive (family_map.REUSED_FAMILIES)."""
    return family_map.family_sizes(items_dir, screen_dir)


def _read_rho_family(results_dir: Path = RESULTS) -> float:
    d = json.loads((results_dir / "family_corr.json").read_text())
    return float(d["rho_family"])


def _run_power_table(families, rho_family_est, *, n_sims=N_SIMS,
                     n_perm=N_PERM, rho_true_values=RHO_TRUE_VALUES,
                     fragility_delta=FRAGILITY_DELTA, seed=0):
    """Runs `simulate` across rho_true_values at the estimated rho_family,
    plus the +/- fragility_delta sweep on rho_family (at rho_true=0.0, the
    calibration point) to check how much the calibrated cutoff moves.
    Returns the assembled results dict and whether the sweep is FRAGILE
    (cutoff drifts by >2x across the sweep)."""
    rho_family_sweep = [rho_family_est - fragility_delta, rho_family_est,
                        rho_family_est + fragility_delta]
    rho_family_sweep = [r for r in rho_family_sweep if 0.0 <= r <= 1.0]

    main_runs = {}
    for rho_true in rho_true_values:
        main_runs[rho_true] = simulate(families, rho_family_est, rho_true,
                                       n_sims=n_sims, seed=seed, n_perm=n_perm)

    fragility_runs = {}
    for rho_f in rho_family_sweep:
        fragility_runs[rho_f] = simulate(families, rho_f, 0.0,
                                         n_sims=n_sims, seed=seed,
                                         n_perm=n_perm)

    cutoffs = [r["calibrated_cutoff"] for r in fragility_runs.values()]
    if min(cutoffs) > 0:
        drift_ratio = max(cutoffs) / min(cutoffs)
    elif max(cutoffs) == 0:
        drift_ratio = 1.0            # all-zero sweep: no drift to report
    else:
        drift_ratio = float("inf")   # some zero, some not: unbounded drift
    fragile = drift_ratio > 2.0

    return {
        "families": families,
        "rho_family_estimate": rho_family_est,
        "n_sims": n_sims,
        "n_perm": n_perm,
        "rho_true_values": list(rho_true_values),
        "runs": {str(k): v for k, v in main_runs.items()},
        "fragility_sweep": {str(k): v for k, v in fragility_runs.items()},
        "fragility_drift_ratio": drift_ratio,
        "fragile": fragile,
    }, fragile


def _write_markdown(out: dict, path: Path) -> None:
    lines = [
        "# Experiment 2c: MC calibration + power table",
        "",
        f"Family sizes: {out['families']}",
        f"rho_family estimate: {out['rho_family_estimate']}",
        f"n_sims={out['n_sims']}, n_perm={out['n_perm']}",
        "",
        "## Power at rho_family estimate",
        "",
        "| rho_true | calibrated_cutoff | alpha_at_cutoff | power |",
        "|---|---|---|---|",
    ]
    for rho_true in out["rho_true_values"]:
        r = out["runs"][str(rho_true)]
        lines.append(f"| {rho_true} | {r['calibrated_cutoff']:.5f} | "
                     f"{r['alpha_at_cutoff']:.4f} | {r['power']:.4f} |")
    lines += [
        "",
        "## Fragility sweep (rho_family, rho_true=0.0)",
        "",
        "| rho_family | calibrated_cutoff |",
        "|---|---|",
    ]
    for rho_f, r in out["fragility_sweep"].items():
        lines.append(f"| {rho_f} | {r['calibrated_cutoff']:.5f} |")
    lines += [
        "",
        f"Drift ratio across sweep: {out['fragility_drift_ratio']:.3f}",
        f"FRAGILE: {out['fragile']}",
        "",
    ]
    path.write_text("\n".join(lines))


def main(argv=None) -> None:
    import argparse
    import sys

    # --exact dispatches to the design Sec 5 fallback table (main_exact)
    # instead of the calibrated-naive table below; the rest of main()'s
    # body -- the calibrated-naive path -- is untouched.
    if argv is None:
        argv = sys.argv[1:]
    if "--exact" in argv:
        main_exact([a for a in argv if a != "--exact"])
        return

    p = argparse.ArgumentParser(
        description="MC calibration + power table under the family model")
    p.add_argument("--items-dir", type=Path, default=ITEMS_DIR)
    p.add_argument("--screen-dir", type=Path, default=SCREEN_DIR)
    p.add_argument("--results-dir", type=Path, default=RESULTS)
    p.add_argument("--n-sims", type=int, default=N_SIMS)
    p.add_argument("--n-perm", type=int, default=N_PERM)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--out-json", type=Path, default=None)
    p.add_argument("--out-md", type=Path, default=None)
    args = p.parse_args(argv)

    families = _family_sizes(args.items_dir, args.screen_dir)
    rho_family_est = _read_rho_family(args.results_dir)

    out, fragile = _run_power_table(families, rho_family_est,
                                    n_sims=args.n_sims, n_perm=args.n_perm,
                                    seed=args.seed)

    out_json = args.out_json or (args.results_dir / "power_table.json")
    out_md = args.out_md or (args.results_dir / "power_table.md")
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(out, indent=1))
    _write_markdown(out, out_md)

    if fragile:
        print(f"FRAGILE: calibrated cutoff drift ratio "
              f"{out['fragility_drift_ratio']:.3f} across rho_family sweep "
              f"{list(out['fragility_sweep'].keys())}", flush=True)
    print(f"[power_table] wrote {out_json} and {out_md} "
          f"(families={families}, rho_family={rho_family_est})", flush=True)


if __name__ == "__main__":
    main()
