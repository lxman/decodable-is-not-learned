# experiments/exp4b/power_ext_4b.py
"""Experiment 4b's power-record reproduction gate and the parametric-
completion extension arms (design `experiment-4b-design.md` §3.5 "The
parametric completion (S1)" and §3.6 gate (4); plan Task 3).

`reproduce_power_record_4b` is gate (4): `power_4.compute` re-run at
the committed `power_4.json` record's own `n_sim`/`seed`/`phis`, with
every other input (`elig`/`floors`/`battery`/`rung_sets`/`grids`)
built exactly as `power_4.main` builds them, re-serialized exactly as
`power_4.main` serializes, and compared byte for byte against the
committed file on disk -- so the completion below is provably the
same machinery Exp 4's power stage ran, not a re-implementation.
Never writes.

`simulate_zero_excess_scaled` is `power_4._simulate_zero_excess`'s
body, copied rather than invoked (nothing in `power_4.py` exposes a
per-trajectory-scale variant), with the two `* scale` noise-draw sites
replaced by `* scale_by_traj[traj]`; `extension_arms_4b` runs it once
(the "observed_lambda" arm, §3.5 (i)) and the frozen function four
more times (§3.5 (ii), multiples {4, 6, 8, 12}) plus once more at the
RMS of the per-trajectory lambda-hats, all five-plus-one draws
consumed off ONE seeded stream in a fixed order. `p_iid_4b` is
p_iid = P(T_iid >= T_4) read off the "observed_lambda" arm's `Ts`
(§3.5 (i)).

Zero model contact; no torch import. `experiments.exp4._threads_4` is
imported first, before numpy, following `analyze_4.py`'s and
`placebo_4b.py`'s convention even though this module is not itself an
entry point (nothing here does a multi-threaded BLAS reduction that a
generation script would run standalone, but every downstream import of
`experiments.exp4.analyze_4` pulls numpy in transitively, and pinning
costs nothing to keep consistent).

Failure messages here are prefixed "4b: "."""
from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

# See module docstring: _threads_4 must be imported before numpy (and
# before every experiments.* import that pulls numpy in transitively).
from experiments.exp4 import _threads_4  # noqa: E402,F401

import numpy as np  # noqa: E402

from experiments.exp2d import battery_2d as bt  # noqa: E402
from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp4 import analyze_4 as an  # noqa: E402
from experiments.exp4 import battery_4  # noqa: E402
from experiments.exp4 import power_4  # noqa: E402
from experiments.exp4b import battery_4b  # noqa: E402

# ------------------------------------------------------- gate (4): reproduce


def _first_diff_4b(committed_bytes: bytes, reproduced_bytes: bytes):
    """The first line (1-based) at which the two serializations
    differ, as `"line {n}: committed={...!r} reproduced={...!r}"` with
    both texts truncated to 200 chars; `None` when the byte strings
    are identical (never called in that case) or when no line-level
    difference is found (unreachable when the caller has already
    checked `committed_bytes != reproduced_bytes`, since two distinct
    byte strings differ on at least one line)."""
    c_lines = committed_bytes.decode("utf-8", errors="replace").split("\n")
    r_lines = reproduced_bytes.decode("utf-8", errors="replace").split("\n")
    for i in range(max(len(c_lines), len(r_lines))):
        c = c_lines[i] if i < len(c_lines) else None
        r = r_lines[i] if i < len(r_lines) else None
        if c != r:
            c_disp = "<no line>" if c is None else c[:200]
            r_disp = "<no line>" if r is None else r[:200]
            return f"line {i + 1}: committed={c_disp!r} reproduced={r_disp!r}"
    return None


def reproduce_power_record_4b(root4, *, rec=None) -> dict:
    """design §3.6 gate (4). Re-runs `power_4.compute` at
    `rec["n_sim"]`/`rec["seed"]`/`tuple(rec["phis"])`, with `elig`
    read from `battery_4.eligibility_path(root4)` and `floors`/
    `battery`/`rung_sets`/`grids` built exactly as `power_4.main`
    builds them -- none of those four depend on `root4` (they read
    the same real committed exp2g/2i/2m/2n bytes and the same
    `battery_4.GRID_4` constant regardless of which tree's
    `power_4.json` is under test, so a synthetic `full_shape` world
    and the real exp4 tree both reproduce against the identical
    `rung_sets`/`grids` their own `power_4.compute()` call used).
    Re-serializes with `json.dumps(reproduced, indent=1)` after
    setting `eligibility_sha256`/`prereg_tag`, exactly as `power_4.
    main` does before it writes.

    `rec=None` (the normal case) loads the committed record from
    `battery_4.power_path(root4)` for its `n_sim`/`seed`/`phis`. A
    `rec` argument overrides only what gets re-run; `identical` and
    `committed_sha256` always compare against the FILE on disk, never
    against a serialization of the `rec` argument -- so passing a
    `rec` with different `n_sim` deliberately produces `identical=
    False` against whatever is actually committed.

    Never writes. Returns `{"identical": bool, "seconds": float,
    "committed_sha256": str, "reproduced_sha256": str, "first_diff":
    str | None}`."""
    root4 = Path(root4)
    power_file = battery_4.power_path(root4)
    committed_bytes = power_file.read_bytes()
    committed_sha256 = hashlib.sha256(committed_bytes).hexdigest()
    if rec is None:
        rec = json.loads(committed_bytes.decode("utf-8"))

    elig_path = battery_4.eligibility_path(root4)
    elig_sha = bg.sha256_file(elig_path)
    elig = json.loads(elig_path.read_text())

    floors = bg.load_floors()
    battery = bt.load_battery()
    rung_sets = {}
    for traj in battery_4.TRAJECTORIES_4:
        outcome = battery_4.load_outcome_4(traj, battery=battery)
        rung_sets[traj] = battery_4.rung_sets_4(outcome, floors)
    grids = {traj: list(battery_4.GRID_4[traj]) for traj in battery_4.TRAJECTORIES_4}

    t0 = time.time()
    reproduced = power_4.compute(elig, rung_sets, grids, n_sim=rec["n_sim"], seed=rec["seed"],
                                 phis=tuple(rec["phis"]))
    seconds = time.time() - t0
    reproduced["eligibility_sha256"] = elig_sha
    reproduced["prereg_tag"] = battery_4.PREREG_TAG_4

    reproduced_bytes = json.dumps(reproduced, indent=1).encode("utf-8")
    reproduced_sha256 = hashlib.sha256(reproduced_bytes).hexdigest()

    identical = reproduced_bytes == committed_bytes
    first_diff = None if identical else _first_diff_4b(committed_bytes, reproduced_bytes)

    return {"identical": identical, "seconds": seconds, "committed_sha256": committed_sha256,
           "reproduced_sha256": reproduced_sha256, "first_diff": first_diff}


# --------------------------------------------- the scaled zero-excess arm


def simulate_zero_excess_scaled(*, pool_info, traj_info, trend_arr, rung_sets, rng, n_sim,
                                scale_by_traj: dict, seed, scale_index) -> dict:
    """`power_4._simulate_zero_excess`'s body, copied verbatim, with
    exactly two sites changed -- both noise-draw scales, `* scale`
    becoming `* scale_by_traj[traj]`:

      (1) the flat-rung loop (`for traj in pool_trajs: ... for r in
          ti["flat"]: noise = rng.normal(0.0, ti["flat_se"][r] *
          scale, size=G)`) -- `traj` is the loop's own variable;
      (2) the pool loop (`for (traj, rung), info in pool_info.items():
          noise = rng.normal(0.0, info["se_r"] * scale, size=
          info["G"])`) -- `traj` comes from the `(traj, rung)` key.

    The eligibility bar (`excess[rung][-1] >= an.SE_MULTIPLE_4 *
    info["se_r"]`) is untouched -- it was never multiplied by `scale`
    in the frozen original either (design §3.5/`ZERO_EXCESS_NOTE_4`:
    the multiple models between-checkpoint scatter the item bootstrap
    does not see; multiplying the bar too would defeat the reading),
    so nothing differs there between the two functions.

    Returns everything `_arm_from_counts` returns, PLUS "Ts" (every
    draw's T, draw order, `None` dropped -- literally the same list
    `_arm_from_counts` itself reduces to mean_T/sd_T, exposed here
    rather than discarded) and "scale_by_traj" (`{traj: float}`).
    `"scatter_multiple"` is set to `None` here (task-3-brief's
    equivalence gate): the frozen function sets it to the single
    scalar `scale`, but there is no single scalar when the scale is
    per-trajectory."""
    pool_trajs = sorted(traj_info)
    world_counts = {w: 0 for w in an.WORLDS_4}
    Ts, elig_counts = [], []
    for draw in range(n_sim):
        series_by_traj = {}
        for traj in pool_trajs:
            ti = traj_info[traj]
            steps = ti["steps"]
            G = len(steps)
            a = {}
            for r in ti["flat"]:
                noise = rng.normal(0.0, ti["flat_se"][r] * scale_by_traj[traj], size=G)
                a[r] = (trend_arr[traj] + noise).tolist()
            series_by_traj[traj] = {"steps": steps, "a": a}
        for (traj, rung), info in pool_info.items():
            noise = rng.normal(0.0, info["se_r"] * scale_by_traj[traj], size=info["G"])
            series_by_traj[traj]["a"][rung] = (trend_arr[traj] + noise).tolist()

        eligibility_sim = {}
        for traj in pool_trajs:
            rs = rung_sets[traj]
            trend = an.trend_4(series_by_traj[traj]["a"], rs["flat"], series_by_traj[traj]["steps"])
            excess = an.excess_4(series_by_traj[traj]["a"], trend, series_by_traj[traj]["steps"])
            Rdict = {}
            for (t2, rung), info in pool_info.items():
                if t2 != traj:
                    continue
                ok = excess[rung][-1] >= an.SE_MULTIPLE_4 * info["se_r"]
                Rdict[rung] = {"eligible": bool(ok), "t_clear": info["t_clear"],
                              "t_clear_index": info["c_r"]}
            eligibility_sim[traj] = {"R": Rdict}

        rs_subset = {traj: rung_sets[traj] for traj in pool_trajs}
        cells = an.cells_4(series_by_traj, rs_subset, eligibility_sim)
        n_cells = len(cells)
        elig_counts.append(n_cells)
        if n_cells == 0:
            tree = an.verdict_tree_4([], 0, 0, {})
            T = None
        else:
            n_rungs_draw = len({c["rung"] for c in cells})
            boot_seed = seed * 7919 + (911_000 + scale_index) * 1_000_003 + draw
            primary = an.primary_4(cells, n_boot=power_4.N_BOOT_POWER_4, seed=boot_seed)
            tree = an.verdict_tree_4([], n_cells, n_rungs_draw, primary)
            T = primary["T"]
        world_counts[tree["verdict"]] = world_counts.get(tree["verdict"], 0) + 1
        if T is not None:
            Ts.append(T)

    if world_counts.get("INSUFFICIENT_DATA", 0):
        raise RuntimeError("4b: simulate_zero_excess_scaled: a simulated draw reached "
                           "INSUFFICIENT_DATA (should be unreachable — failures is always [])")
    arm = power_4._arm_from_counts(world_counts, Ts, elig_counts, n_sim)
    arm["scatter_multiple"] = None
    arm["Ts"] = list(Ts)
    arm["scale_by_traj"] = {t: float(v) for t, v in scale_by_traj.items()}
    return arm


# ------------------------------------------------------ the extension arms


def _pool_inputs_4b(elig: dict, rung_sets: dict, grids: dict):
    """Reproduces the block of `power_4.compute`'s body that builds
    `pool`/`pool_info`/`traj_info`/`trend_arr` from `elig`/
    `rung_sets`/`grids` -- the part of `compute()` between `pool =
    _pool(elig)` and the end of the `trend_arr` loop. Those three
    dicts are not exposed as a separately callable frozen helper (only
    `_pool` itself is), so the construction is copied here verbatim;
    `power_4._pool` is CALLED, not reimplemented. `cell_info`/
    `m_by_phi`/`construction` -- built later in `compute()`, consumed
    only by the phi arms -- are not needed by the zero-excess arms and
    are not built here."""
    pool = power_4._pool(elig)
    pool_trajs = sorted({t for t, _ in pool})

    pool_info = {}
    for traj, rung in pool:
        e = elig[traj]["R"][rung]
        tci = e.get("t_clear_index")
        pool_info[(traj, rung)] = dict(G=len(list(grids[traj])),
                                       c_r=None if tci is None else int(tci),
                                       se_r=float(e["se"]), t_clear=e.get("t_clear"))

    traj_info = {}
    for traj in pool_trajs:
        flat = list(rung_sets[traj]["flat"])
        flat_se = {r: float(elig[traj]["flat"][r]["se_at_end"]) for r in flat}
        steps = list(grids[traj])
        traj_info[traj] = dict(flat=flat, flat_se=flat_se, steps=steps,
                               trend_t1=float(elig[traj]["trend_t1"]),
                               trend_end=float(elig[traj]["trend_end"]))

    trend_arr = {}
    for traj, ti in traj_info.items():
        steps_arr = np.asarray(ti["steps"], dtype=np.float64)
        s0, s1 = steps_arr[0], steps_arr[-1]
        if s0 <= 0:
            raise ValueError(f"4b: {traj}'s grid starts at step {s0!r} <= 0 -- log-linear trend "
                             f"interpolation needs a strictly positive t_1")
        if s1 == s0:
            frac = np.zeros_like(steps_arr)
        else:
            frac = (np.log(steps_arr) - np.log(s0)) / (np.log(s1) - np.log(s0))
        trend_arr[traj] = ti["trend_t1"] + (ti["trend_end"] - ti["trend_t1"]) * frac

    return pool, pool_info, traj_info, trend_arr


def extension_arms_4b(elig: dict, rung_sets: dict, grids: dict, lambda_by_traj: dict, *,
                      multiples=battery_4b.EXT_MULTIPLES_4B, n_sim=battery_4b.N_SIM_EXT_4B,
                      seed=battery_4b.EXT_SEED_4B) -> dict:
    """design §3.5 (S1), the parametric completion's extension arms:
    ONE `rng = np.random.default_rng(seed)`, consumed in this fixed
    order (so every arm after the first draws from whatever the
    earlier arms left in the stream -- `power_4.RNG_ORDER_NOTE_4`'s
    convention, carried over): "observed_lambda" (§3.5 (i), the
    observed per-trajectory lambda-hat, via `simulate_zero_excess_
    scaled`), then each of `multiples` in order (§3.5 (ii), the frozen
    `power_4._simulate_zero_excess` at that scalar multiple), then
    "rms_lambda" (the frozen function again, at scale = sqrt(mean of
    `lambda_by_traj`'s values squared)). `scale_index` runs 0, 1, 2,
    ... across every arm in this same order (it enters the frozen
    function's own bootstrap seed via its `scale_index` parameter --
    kept sequential and gapless here so the six arms' bootstrap seeds
    never collide).

    Returns `{"arms": {name: arm}, "order": [name, ...], "seed":
    seed, "n_sim": n_sim, "lambda_by_traj": {traj: float}}`."""
    pool, pool_info, traj_info, trend_arr = _pool_inputs_4b(elig, rung_sets, grids)
    rng = np.random.default_rng(seed)

    arms: dict = {}
    order: list = []
    scale_index = 0

    scale_by_traj = {traj: float(lambda_by_traj[traj]) for traj in sorted(traj_info)}
    arms["observed_lambda"] = simulate_zero_excess_scaled(
        pool_info=pool_info, traj_info=traj_info, trend_arr=trend_arr, rung_sets=rung_sets,
        rng=rng, n_sim=n_sim, scale_by_traj=scale_by_traj, seed=seed, scale_index=scale_index)
    order.append("observed_lambda")
    scale_index += 1

    for mult in multiples:
        name = str(float(mult))
        arms[name] = power_4._simulate_zero_excess(
            pool_info=pool_info, traj_info=traj_info, trend_arr=trend_arr, rung_sets=rung_sets,
            rng=rng, n_sim=n_sim, scale=float(mult), seed=seed, scale_index=scale_index)
        order.append(name)
        scale_index += 1

    rms = float(np.sqrt(np.mean([float(v) ** 2 for v in lambda_by_traj.values()])))
    arms["rms_lambda"] = power_4._simulate_zero_excess(
        pool_info=pool_info, traj_info=traj_info, trend_arr=trend_arr, rung_sets=rung_sets,
        rng=rng, n_sim=n_sim, scale=rms, seed=seed, scale_index=scale_index)
    order.append("rms_lambda")

    return {"arms": arms, "order": order, "seed": seed, "n_sim": n_sim,
           "lambda_by_traj": {t: float(v) for t, v in lambda_by_traj.items()}}


# ----------------------------------------------------------------- p_iid


def p_iid_4b(Ts: list, T4: float) -> dict:
    """design §3.5 (i): p_iid = P(T_iid >= T_4), read off the
    "observed_lambda" arm's `Ts` against the committed `T_4`, one-
    sided with the sign-flip test's own tolerance
    (`primary_4`'s own `>= x - 1e-15`):

        p_iid = (1 + #{T in Ts : T >= T4 - 1e-15}) / (len(Ts) + 1)

    plus the null's own mean and sample SD (`ddof=1`) for the S1
    side-by-side reading -- both `None` when there are fewer than two
    draws to estimate a spread from (`null_mean` is additionally
    `None` when `Ts` is empty)."""
    n = len(Ts)
    count = sum(1 for T in Ts if T >= T4 - 1e-15)
    p_iid = (1 + count) / (n + 1)
    null_mean = float(np.mean(Ts)) if n else None
    null_sd = float(np.std(Ts, ddof=1)) if n > 1 else None
    return {"p_iid": p_iid, "n": n, "null_mean": null_mean, "null_sd": null_sd}
