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
      equivalence gate the brief requires.
  (c) `extension_arms_4b` at `n_sim=20` on the world produces the six
      arms in the documented order, with `Ts` present (length <= 20)
      only on the "observed_lambda" arm.
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
