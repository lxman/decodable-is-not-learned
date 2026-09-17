# experiments/exp4b/tests/test_power_ext_4b.py
"""Tests for `power_ext_4b.py` (Task 3, design §3.5/§3.6 gate (4)):

  (a) `reproduce_power_record_4b` on a `full_shape.build_world(...,
      "leads", stage="full")` tree returns `identical=True` against
      the world's own committed `power_4.json`; after flipping one
      byte of a COPY of that committed record (the copy's
      `eligibility_sha256` field, a hex digit -- keeps the file valid
      JSON so `n_sim`/`seed`/`phis` still load, but makes the re-
      derived bytes disagree with what is now on disk), it returns
      `identical=False` with `first_diff` set.
  (b) `simulate_zero_excess_scaled` at a UNIFORM per-trajectory scale
      (`scale_by_traj = {t: 2.0 for t in traj_info}`) equals `power_4.
      _simulate_zero_excess(..., scale=2.0, ...)` field for field on
      the same seeded stream and the same `seed`/`scale_index` -- the
      equivalence gate the brief requires; PLUS (review Finding 2) the
      same equivalence per REAL trajectory at that trajectory's own
      distinct `LAMBDA_BY_TRAJ` scale, on `pool_info`/`traj_info`/
      `trend_arr`/`rung_sets` restricted to just that trajectory --
      pins `scale_by_traj[traj]` itself, which a uniform scale cannot.
  (c) `extension_arms_4b` at `n_sim=20` on the world produces the six
      arms in the documented order, with `Ts` present (length <= 20)
      only on the "observed_lambda" arm; PLUS (review Finding 1) a
      hand-rolled reference built from ONE fresh `default_rng` seeded
      and consumed in the same order (observed_lambda, then the "4.0"
      multiple) reproduces those two arms bit for bit -- the single-
      shared-stream contract `RNG_ORDER_NOTE_4` carries over.
  (d) `p_iid_4b`'s hand example, plus its `n < 2` edge cases.

Every world is ONE `full_shape.build_world(..., "leads", seed=11,
stage="full")` tree, built once (module-scoped fixture,
`test_full_shape_4.py`'s own pattern) because a `stage="full"` build
sweeps the real 92-point grid (~11 minutes, per `experiments/exp4/
PROGRESS.md`) -- every other test either reads it directly (read-only)
or works on a `shutil.copytree` (the byte-flip test, which mutates)."""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import numpy as np
import pytest

REPO = Path(__file__).resolve().parents[3]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp2d import battery_2d as bt  # noqa: E402
from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp4 import battery_4  # noqa: E402
from experiments.exp4 import power_4  # noqa: E402
from experiments.exp4.tests import full_shape as fs  # noqa: E402
from experiments.exp4b import battery_4b  # noqa: E402
from experiments.exp4b import power_ext_4b as pe  # noqa: E402

LAMBDA_BY_TRAJ = {"pythia_2.8b": 6.23, "olmo2_7b": 6.47, "smollm3_3b": 7.30, "comma_7b": 7.32}


def _load_inputs(root):
    """`elig`/`rung_sets`/`grids` built exactly as `power_4.main`
    builds them, elig read from `root`."""
    elig_path = battery_4.eligibility_path(root)
    elig = json.loads(elig_path.read_text())
    floors = bg.load_floors()
    battery = bt.load_battery()
    rung_sets = {}
    for traj in battery_4.TRAJECTORIES_4:
        outcome = battery_4.load_outcome_4(traj, battery=battery)
        rung_sets[traj] = battery_4.rung_sets_4(outcome, floors)
    grids = {traj: list(battery_4.GRID_4[traj]) for traj in battery_4.TRAJECTORIES_4}
    return elig, rung_sets, grids


@pytest.fixture(scope="module")
def _leads_world(tmp_path_factory):
    """ONE full-grid LEADS-mode world with a real `power_4.json` at
    `fs.WORLD_POWER_N_SIM_4` (20), built once and shared read-only;
    tests that need to mutate the tree work on a `_fresh_copy`."""
    root = tmp_path_factory.mktemp("leads_world")
    fs.build_world(root, "leads", seed=11, stage="full")
    return root


def _fresh_copy(template_root, tmp_path):
    dst = tmp_path / "world"
    shutil.copytree(template_root, dst)
    return dst


# --------------------------------------------- reproduce_power_record_4b


@pytest.mark.slow
def test_reproduce_power_record_identical(_leads_world):
    out = pe.reproduce_power_record_4b(_leads_world)
    assert out["identical"] is True
    assert out["first_diff"] is None
    assert out["committed_sha256"] == out["reproduced_sha256"]
    assert out["seconds"] >= 0.0
    # Recorded (not asserted) for Task 5, which measures the real exp4
    # tree's n_sim=1000 record separately: this is the world's own
    # n_sim=20 figure, a first-order lower bound on gate (4)'s cost.
    print(f"\nreproduce_power_record_4b seconds (world, n_sim=20): {out['seconds']:.4f}")


@pytest.mark.slow
def test_reproduce_power_record_detects_one_byte_flip(_leads_world, tmp_path):
    root = _fresh_copy(_leads_world, tmp_path)
    p = battery_4.power_path(root)
    rec = json.loads(p.read_text())
    sha = rec["eligibility_sha256"]
    flipped = ("0" if sha[0] != "0" else "1") + sha[1:]
    assert flipped != sha
    rec["eligibility_sha256"] = flipped
    p.write_text(json.dumps(rec, indent=1))

    out = pe.reproduce_power_record_4b(root)
    assert out["identical"] is False
    assert out["first_diff"] is not None
    assert "eligibility_sha256" in out["first_diff"]
    assert out["committed_sha256"] != out["reproduced_sha256"]


@pytest.mark.slow
def test_reproduce_power_record_never_writes(_leads_world, tmp_path):
    root = _fresh_copy(_leads_world, tmp_path)
    p = battery_4.power_path(root)
    before = p.read_bytes()
    pe.reproduce_power_record_4b(root)
    assert p.read_bytes() == before


def test_reproduce_power_record_detects_byte_difference_fast(tmp_path, monkeypatch):
    """Mutation harness finding (Task 6, controller ruling): the slow
    byte-flip test above (`test_reproduce_power_record_detects_one_
    byte_flip`) needs a full `_leads_world` and never runs in the
    mutation harness's FAST suite. `power_4.compute` -- the one real
    input that is actually expensive (n_sim simulations) -- is
    monkeypatched to a trivial, instant stub that ignores its
    arguments; every other real input `reproduce_power_record_4b`
    reads (`bg.load_floors`, `bt.load_battery`, `battery_4.
    load_outcome_4`/`rung_sets_4` per real trajectory) is cheap and
    left genuine, so what is under test is `reproduce_power_record_4b`'s
    OWN byte-comparison logic, not a synthetic world's plausibility."""
    battery_4.eligibility_path(tmp_path).parent.mkdir(parents=True, exist_ok=True)
    battery_4.eligibility_path(tmp_path).write_text("{}")
    committed = {"n_sim": 5, "seed": 0, "phis": [0.0], "eligibility_sha256": "committed-marker",
                "prereg_tag": "committed-tag"}
    battery_4.power_path(tmp_path).write_text(json.dumps(committed, indent=1))

    def fake_compute(elig, rung_sets, grids, *, n_sim, seed, phis):
        return {"n_sim": n_sim, "seed": seed, "phis": list(phis), "marker": "reproduced-not-committed"}

    monkeypatch.setattr(power_4, "compute", fake_compute)
    out = pe.reproduce_power_record_4b(tmp_path)
    assert out["identical"] is False
    assert out["first_diff"] is not None
    assert out["committed_sha256"] != out["reproduced_sha256"]


# ------------------------------------------- simulate_zero_excess_scaled


@pytest.mark.slow
def test_simulate_zero_excess_scaled_equals_frozen_at_uniform_scale(_leads_world):
    elig, rung_sets, grids = _load_inputs(_leads_world)
    pool, pool_info, traj_info, trend_arr = pe._pool_inputs_4b(elig, rung_sets, grids)
    scale_by_traj = {t: 2.0 for t in traj_info}

    scaled = pe.simulate_zero_excess_scaled(
        pool_info=pool_info, traj_info=traj_info, trend_arr=trend_arr, rung_sets=rung_sets,
        rng=np.random.default_rng(7), n_sim=5, scale_by_traj=scale_by_traj, seed=99,
        scale_index=3)
    frozen = power_4._simulate_zero_excess(
        pool_info=pool_info, traj_info=traj_info, trend_arr=trend_arr, rung_sets=rung_sets,
        rng=np.random.default_rng(7), n_sim=5, scale=2.0, seed=99, scale_index=3)

    scaled_cmp = dict(scaled)
    scaled_ts = scaled_cmp.pop("Ts")
    scaled_scale_by_traj = scaled_cmp.pop("scale_by_traj")
    scaled_multiple = scaled_cmp.pop("scatter_multiple")

    frozen_cmp = dict(frozen)
    frozen_multiple = frozen_cmp.pop("scatter_multiple")

    assert scaled_multiple is None
    assert frozen_multiple == 2.0
    assert scaled_cmp == frozen_cmp   # P_LEADS/.../mean_T/sd_T/mean_eligible_cells/construction_miss_count
    assert scaled_scale_by_traj == {t: 2.0 for t in traj_info}
    assert isinstance(scaled_ts, list)
    assert len(scaled_ts) <= 5


@pytest.mark.slow
def test_simulate_zero_excess_scaled_per_trajectory_mapping(_leads_world):
    """Finding 2 (review): the uniform-scale gate above cannot tell
    `scale_by_traj[traj]` apart from a mis-keyed lookup (a stale
    outer-loop `traj`, `next(iter(scale_by_traj.values()))`, always
    the first pool trajectory, ...) -- every trajectory gets the same
    2.0 either way, so any of those bugs passes it too. Restrict
    `pool_info`/`traj_info`/`trend_arr`/`rung_sets` to ONE real
    trajectory at a time (dict slices -- straightforward, per the
    review's own note) and require `simulate_zero_excess_scaled({t:
    s})` to equal `power_4._simulate_zero_excess(scale=s)` for that
    trajectory's OWN `s`, run across all four real trajectories at
    their own distinct `LAMBDA_BY_TRAJ` values -- a lookup that
    silently returns some OTHER trajectory's scale, or a name absent
    from the single-entry restricted map, fails immediately (a wrong
    value or a `KeyError`), which the chosen implementation of Finding
    2's fix (task-3-report.md) documents in place of the weaker
    single-trajectory-differs alternative the review also offered."""
    elig, rung_sets, grids = _load_inputs(_leads_world)
    pool, pool_info, traj_info, trend_arr = pe._pool_inputs_4b(elig, rung_sets, grids)

    for traj in sorted(traj_info):
        s = float(LAMBDA_BY_TRAJ[traj])
        pool_info_t = {k: v for k, v in pool_info.items() if k[0] == traj}
        traj_info_t = {traj: traj_info[traj]}
        trend_arr_t = {traj: trend_arr[traj]}
        rung_sets_t = {traj: rung_sets[traj]}

        scaled_t = pe.simulate_zero_excess_scaled(
            pool_info=pool_info_t, traj_info=traj_info_t, trend_arr=trend_arr_t,
            rung_sets=rung_sets_t, rng=np.random.default_rng(31), n_sim=8,
            scale_by_traj={traj: s}, seed=13, scale_index=0)
        frozen_t = power_4._simulate_zero_excess(
            pool_info=pool_info_t, traj_info=traj_info_t, trend_arr=trend_arr_t,
            rung_sets=rung_sets_t, rng=np.random.default_rng(31), n_sim=8, scale=s, seed=13,
            scale_index=0)

        scaled_t_cmp = dict(scaled_t)
        scaled_t_cmp.pop("Ts")
        scaled_t_cmp.pop("scale_by_traj")
        scaled_t_cmp.pop("scatter_multiple")
        frozen_t_cmp = dict(frozen_t)
        frozen_t_cmp.pop("scatter_multiple")

        assert scaled_t_cmp == frozen_t_cmp, traj


# --------------------------------------------------- extension_arms_4b


@pytest.mark.slow
def test_extension_arms_order_and_ts(_leads_world):
    elig, rung_sets, grids = _load_inputs(_leads_world)
    out = pe.extension_arms_4b(elig, rung_sets, grids, LAMBDA_BY_TRAJ, n_sim=20)

    assert out["order"] == ["observed_lambda", "4.0", "6.0", "8.0", "12.0", "rms_lambda"]
    assert set(out["arms"]) == set(out["order"])
    assert out["n_sim"] == 20
    assert out["seed"] == battery_4b.EXT_SEED_4B
    assert out["lambda_by_traj"] == LAMBDA_BY_TRAJ

    observed = out["arms"]["observed_lambda"]
    assert isinstance(observed["Ts"], list)
    assert len(observed["Ts"]) <= 20
    assert observed["scatter_multiple"] is None

    for name in out["order"][1:]:
        arm = out["arms"][name]
        assert "Ts" not in arm
        assert "scale_by_traj" not in arm
    assert out["arms"]["4.0"]["scatter_multiple"] == 4.0
    assert out["arms"]["rms_lambda"]["scatter_multiple"] == pytest.approx(
        float(np.sqrt(np.mean([v ** 2 for v in LAMBDA_BY_TRAJ.values()]))))

    # Finding 1 (review): the single-stream contract is the whole point
    # of extension_arms_4b -- ONE rng, consumed by every arm in order,
    # not a fresh stream per arm -- and nothing above distinguishes the
    # two. Hand-roll the same first two draws (observed_lambda at
    # scale_index=0, then the "4.0" multiple at scale_index=1) on a
    # FRESH rng seeded identically to what extension_arms_4b used
    # internally, in the same order, and require bit-for-bit equality
    # with what it actually produced. A refactor that gave each arm
    # its own fresh `default_rng(seed)` (destroying RNG_ORDER_NOTE_4's
    # "successive draws from one stream" property and the reason
    # `scale_index` is gapless) would still pass every assertion above
    # but fail this one -- observed_lambda would match (it is still
    # the first draw off a `default_rng(seed)`), but the "4.0" arm
    # would draw from its OWN fresh stream at index 0 instead of
    # continuing the shared one, and disagree.
    pool, pool_info, traj_info, trend_arr = pe._pool_inputs_4b(elig, rung_sets, grids)
    scale_by_traj_ref = {traj: float(LAMBDA_BY_TRAJ[traj]) for traj in sorted(traj_info)}
    ref_rng = np.random.default_rng(battery_4b.EXT_SEED_4B)
    observed_ref = pe.simulate_zero_excess_scaled(
        pool_info=pool_info, traj_info=traj_info, trend_arr=trend_arr, rung_sets=rung_sets,
        rng=ref_rng, n_sim=20, scale_by_traj=scale_by_traj_ref, seed=battery_4b.EXT_SEED_4B,
        scale_index=0)
    multiple_ref = power_4._simulate_zero_excess(
        pool_info=pool_info, traj_info=traj_info, trend_arr=trend_arr, rung_sets=rung_sets,
        rng=ref_rng, n_sim=20, scale=4.0, seed=battery_4b.EXT_SEED_4B, scale_index=1)

    assert observed_ref == out["arms"]["observed_lambda"]
    assert multiple_ref == out["arms"]["4.0"]


def test_simulate_zero_excess_scaled_eligibility_bar_is_inclusive_at_the_boundary():
    """Mutation harness finding (Task 6, controller ruling): weakening
    the eligibility bar from `>=` to `>` is a measure-zero event under
    REAL (continuous) simulated noise -- confirmed empirically: applying
    ONLY this mutation and re-running the two slow equivalence tests
    above changes NOTHING (6/6 still pass; `test-injected` mutation
    reverted immediately after). A fixed, deterministic noise stand-in
    (never `np.random.default_rng`, so the exact excess value is chosen,
    not hoped for) engineers the boundary EXACTLY: one flat rung with
    zero noise (trend stays 0 at every step), one pool rung whose last-
    step noise puts `excess[rung][-1]` at PRECISELY `SE_MULTIPLE_4 *
    se_r` (2.0 * 1.0 = 2.0) -- `>=` counts it eligible (`cells_4` keeps
    the one cell, `mean_eligible_cells` = 1.0), `>` does not (0 cells,
    `mean_eligible_cells` = 0.0). `t_clear_index` = 2 (>= `MIN_CLEAR_
    INDEX_4` = 2 -- one below that, `phi_4` returns `None` regardless of
    eligibility, which would mask the very thing under test)."""
    class _FixedRng:
        """A `.normal()`-only stand-in for `np.random.Generator`:
        returns each caller-supplied array in order, ignoring
        loc/scale/size beyond bookkeeping -- deterministic in place of
        random, so an exact floating-point boundary can be engineered."""
        def __init__(self, sequence):
            self._seq = list(sequence)

        def normal(self, loc, scale, size):
            return np.asarray(self._seq.pop(0), dtype=np.float64)

    pool_info = {("T", "X"): {"G": 3, "c_r": 2, "se_r": 1.0, "t_clear": 2}}
    traj_info = {"T": {"flat": ["F"], "flat_se": {"F": 1.0}, "steps": [0, 1, 2],
                       "trend_t1": 0.0, "trend_end": 0.0}}
    trend_arr = {"T": np.array([0.0, 0.0, 0.0])}
    rung_sets = {"T": {"flat": ["F"], "R": {"X": {}}}}

    fake_rng = _FixedRng([[0.0, 0.0, 0.0], [0.0, 0.0, 2.0]])   # flat noise, then pool noise
    out = pe.simulate_zero_excess_scaled(
        pool_info=pool_info, traj_info=traj_info, trend_arr=trend_arr, rung_sets=rung_sets,
        rng=fake_rng, n_sim=1, scale_by_traj={"T": 1.0}, seed=0, scale_index=0)
    assert out["mean_eligible_cells"] == 1.0, out


def test_simulate_zero_excess_scaled_noise_draws_are_scaled_at_each_site():
    """Mutation harness review finding 1: the two slow equivalence
    tests above kill the flat-rung and pool-rung scale-drop mutations
    only JOINTLY (both dropped at once, in one `test_power_ext_4b.py
    -m slow` run against a real world) -- a joint failure does not
    attribute a kill to either mutant site specifically, and no fast
    test observed either. `_FixedRng` (used just above) cannot do this
    either: it ignores `scale` by design. This spies on `.normal()`
    itself (real value generation delegated to a genuine `Generator`,
    so downstream code sees real noise, not a fixture the test had to
    hand-craft) and asserts each of the TWO calls carries the CORRECT
    `scale` argument: the flat-rung site's `ti["flat_se"][r] *
    scale_by_traj[traj]`, the pool-rung site's `info["se_r"] *
    scale_by_traj[traj]` -- one trajectory, one flat rung, one pool
    rung, DISTINCT `flat_se`/`se_r`/`scale_by_traj` values so a
    stale/mis-keyed lookup at either site would read as a wrong
    number, not accidentally the right one."""
    class _SpyRng:
        def __init__(self, real):
            self._real = real
            self.calls = []   # [(loc, scale, size), ...] in call order

        def normal(self, loc, scale, size):
            self.calls.append((loc, scale, size))
            return self._real.normal(loc, scale, size)

    pool_info = {("T", "X"): {"G": 1, "c_r": 0, "se_r": 5.0, "t_clear": 0}}
    traj_info = {"T": {"flat": ["F"], "flat_se": {"F": 3.0}, "steps": [0],
                       "trend_t1": 0.0, "trend_end": 0.0}}
    trend_arr = {"T": np.array([0.0])}
    rung_sets = {"T": {"flat": ["F"], "R": {"X": {}}}}

    spy = _SpyRng(np.random.default_rng(0))
    pe.simulate_zero_excess_scaled(
        pool_info=pool_info, traj_info=traj_info, trend_arr=trend_arr, rung_sets=rung_sets,
        rng=spy, n_sim=1, scale_by_traj={"T": 2.0}, seed=0, scale_index=0)

    assert len(spy.calls) == 2, spy.calls
    flat_call, pool_call = spy.calls
    assert flat_call[1] == pytest.approx(3.0 * 2.0), flat_call     # kills #18 alone
    assert pool_call[1] == pytest.approx(5.0 * 2.0), pool_call     # kills #19 alone


# --------------------------------------------------------------- p_iid_4b


def test_p_iid_hand_example():
    Ts = [0.1, 0.2, 0.3, 0.4, 0.5]
    out = pe.p_iid_4b(Ts, 0.35)
    assert out["n"] == 5
    assert out["p_iid"] == pytest.approx(0.5)          # (1 + 2) / (5 + 1)
    assert out["null_mean"] == pytest.approx(0.3)
    assert out["null_sd"] == pytest.approx(float(np.std(Ts, ddof=1)))


def test_p_iid_boundary_tolerance():
    # T4 exactly on a Ts value must count (the -1e-15 tolerance).
    out = pe.p_iid_4b([0.35, 0.1], 0.35)
    assert out["p_iid"] == pytest.approx(2 / 3)         # (1 + 1) / (2 + 1)


def test_p_iid_empty():
    out = pe.p_iid_4b([], 0.1)
    assert out == {"p_iid": 1.0, "n": 0, "null_mean": None, "null_sd": None}


def test_p_iid_single():
    out = pe.p_iid_4b([0.5], 0.1)
    assert out["n"] == 1
    assert out["p_iid"] == pytest.approx(1.0)           # (1 + 1) / (1 + 1)
    assert out["null_mean"] == pytest.approx(0.5)
    assert out["null_sd"] is None
