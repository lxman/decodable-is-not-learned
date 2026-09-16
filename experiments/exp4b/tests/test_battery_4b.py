# experiments/exp4b/tests/test_battery_4b.py
"""Known-answer / unit tests for `battery_4b.py` (Task 1): the
exp4-closed pin, the prereg binding, the exp4 record loaders, and the
constants Task 1 establishes for the rest of the build.

No model contact. No network beyond the `slow`-marked real-git gate
(`check_exp4_closed_4b`'s file hashing and `require_prereg_4b`'s tag
lookup against the real repository)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.exp2g import battery_2g as bg  # noqa: E402
from experiments.exp4 import battery_4  # noqa: E402
from experiments.exp4b import battery_4b as b4b  # noqa: E402

_SEVEN_PATHS = {
    "experiments/exp4/__init__.py",
    "experiments/exp4/analyze_4.py",
    "experiments/exp4/battery_4.py",
    "experiments/exp4/metric_4.py",
    "experiments/exp4/collect_4.py",
    "experiments/exp4/power_4.py",
    "experiments/exp4/make_referents_4.py",
}


# ------------------------------------------------------- the exp4-closed pin

def test_exp4_closed_sha256_4b_has_exactly_the_seven_paths():
    assert set(b4b.EXP4_CLOSED_SHA256_4B) == _SEVEN_PATHS
    assert all(len(v) == 64 for v in b4b.EXP4_CLOSED_SHA256_4B.values())


def test_check_exp4_closed_4b_raises_naming_a_drifted_file(monkeypatch):
    bad = dict(b4b.EXP4_CLOSED_SHA256_4B)
    bad["experiments/exp4/metric_4.py"] = "0" * 64
    monkeypatch.setattr(b4b, "EXP4_CLOSED_SHA256_4B", bad)
    with pytest.raises(RuntimeError, match="experiments/exp4/metric_4.py"):
        b4b.check_exp4_closed_4b()


@pytest.mark.slow
def test_real_git_gates():
    """`check_exp4_closed_4b` passes on the committed exp4 tree (calls
    `battery_4.check_frozen_4()` too); `require_prereg_4b` against real
    git refuses — `exp4b-preregistered` does not exist yet."""
    b4b.check_exp4_closed_4b()
    with pytest.raises(RuntimeError, match=b4b.PREREG_TAG_4B):
        b4b.require_prereg_4b()


# ------------------------------------------------------- prereg binding

def test_require_prereg_4b_with_stand_ins(monkeypatch):
    with pytest.raises(RuntimeError, match="does not exist"):
        b4b.require_prereg_4b(tag_exists=lambda t: False, blob_sha=lambda t, r: None)

    present = tuple(r for r in b4b.INSTRUMENT_BLOBS_4B if (b4b.REPO / r).is_file())
    assert present  # battery_4b.py exists at this point in the build
    monkeypatch.setattr(b4b, "INSTRUMENT_BLOBS_4B", present)

    ok = b4b.require_prereg_4b(
        tag_exists=lambda t: True,
        blob_sha=lambda tag, rel: bg.sha256_file(b4b.REPO / rel))
    assert ok["tag"] == b4b.PREREG_TAG_4B
    assert set(ok["instrument_blobs"]) == set(present)

    with pytest.raises(RuntimeError, match="does not bind"):
        b4b.require_prereg_4b(tag_exists=lambda t: True, blob_sha=lambda t, r: "0" * 64)


# --------------------------------------------------------- exp4 record loaders

def test_load_exp4_verdict_4b_raises_on_no_primary(tmp_path):
    (tmp_path / "results").mkdir()
    battery_4.verdict_path(tmp_path).write_text(json.dumps({"verdict": "NO-CONVERGENCE"}))
    with pytest.raises(ValueError, match="carries no primary"):
        b4b.load_exp4_verdict_4b(tmp_path)


def test_load_exp4_verdict_4b_on_the_real_committed_verdict():
    v = b4b.load_exp4_verdict_4b(battery_4.EXP4)
    assert v["verdict"] not in ("INSUFFICIENT_DATA", "NO-CONVERGENCE")
    assert v["primary"]["T"] is not None


def test_load_exp4_eligibility_4b_on_the_real_tree():
    elig = b4b.load_exp4_eligibility_4b(battery_4.EXP4)
    assert isinstance(elig, dict) and set(elig) == set(battery_4.TRAJECTORIES_4)


def test_load_exp4_power_4b_on_the_real_tree():
    rec, sha = b4b.load_exp4_power_4b(battery_4.EXP4)
    assert isinstance(rec, dict) and rec
    assert sha == bg.sha256_file(battery_4.power_path(battery_4.EXP4))


def test_T_4_from_verdict_4b_reads_the_primary_T():
    v = b4b.load_exp4_verdict_4b(battery_4.EXP4)
    assert b4b.T_4_from_verdict_4b(v) == v["primary"]["T"]


# ------------------------------------------------------------------- cells

def test_cells_from_verdict_4b_grid_lookup():
    v = {"cells": [
        {"traj": "pythia_2.8b", "rung": "antonym", "phi": 0.5, "t_clear": 30000},
        {"traj": "olmo2_7b", "rung": "sub3_mid", "phi": 0.25, "t_clear": 64000},
    ]}
    cells = b4b.cells_from_verdict_4b(v)
    assert len(cells) == 2
    c0 = next(c for c in cells if c["traj"] == "pythia_2.8b")
    assert c0["t_clear_index"] == list(battery_4.GRID_4["pythia_2.8b"]).index(30000) == 7
    assert c0["rung"] == "antonym" and c0["phi"] == 0.5 and c0["t_clear"] == 30000


def test_cells_from_verdict_4b_raises_on_a_step_not_on_the_grid():
    v = {"cells": [{"traj": "pythia_2.8b", "rung": "antonym", "phi": 0.5, "t_clear": 30001}]}
    with pytest.raises(ValueError, match=r"4b: t_clear 30001 not on GRID_4\[pythia_2\.8b\]"):
        b4b.cells_from_verdict_4b(v)


def test_cells_from_verdict_4b_on_the_real_committed_verdict():
    v = b4b.load_exp4_verdict_4b(battery_4.EXP4)
    cells = b4b.cells_from_verdict_4b(v)
    assert len(cells) == v["primary"]["n_cells"]
    for c in cells:
        assert battery_4.GRID_4[c["traj"]][c["t_clear_index"]] == c["t_clear"]


# --------------------------------------------------------------- real design

def test_real_design_4b_counts_and_sorted_clear_indices():
    cells = [
        {"traj": "pythia_2.8b", "rung": "antonym6", "phi": 0.6, "t_clear": 10000,
         "t_clear_index": 4},
        {"traj": "pythia_2.8b", "rung": "antonym", "phi": 0.4, "t_clear": 30000,
         "t_clear_index": 7},
        {"traj": "olmo2_7b", "rung": "sub3_mid", "phi": 0.2, "t_clear": 64000,
         "t_clear_index": 6},
    ]
    design = b4b.real_design_4b(cells)
    assert set(design) == set(battery_4.TRAJECTORIES_4)
    assert design["pythia_2.8b"] == {"n": 2, "clear_indices": [4, 7],
                                     "rungs": ["antonym", "antonym6"]}
    assert design["olmo2_7b"] == {"n": 1, "clear_indices": [6], "rungs": ["sub3_mid"]}
    for traj in ("smollm3_3b", "comma_7b"):
        assert design[traj] == {"n": 0, "clear_indices": [], "rungs": []}


def test_real_design_4b_on_the_real_committed_verdict():
    v = b4b.load_exp4_verdict_4b(battery_4.EXP4)
    cells = b4b.cells_from_verdict_4b(v)
    design = b4b.real_design_4b(cells)
    assert sum(design[t]["n"] for t in battery_4.TRAJECTORIES_4) == len(cells)
    for traj in battery_4.TRAJECTORIES_4:
        assert design[traj]["clear_indices"] == sorted(design[traj]["clear_indices"])


# ------------------------------------------------------------------ constants

def test_constants_literal():
    assert b4b.B_4B == 10_000
    assert b4b.SEED_4B == 0
    assert b4b.B_ALPHA_4B == b4b.B_4B
    assert b4b.ALPHA_4B == 0.01
    assert b4b.MARGINAL_4B == 0.05
    assert b4b.MIN_PLACEBO_TOTAL_4B == 8
    assert b4b.MIN_PLACEBO_PER_TRAJ_4B == 3
    assert b4b.EXT_MULTIPLES_4B == (4.0, 6.0, 8.0, 12.0)
    assert b4b.N_SIM_EXT_4B == 1000
    assert b4b.EXT_SEED_4B == 4242
    assert b4b.N_BOOT_LEVELS_4B == 2000
    assert b4b.WORLDS_4B == ("INSUFFICIENT_DATA", "CALIBRATED", "MARGINAL",
                             "NOT-DISTINGUISHABLE")
    assert b4b.TYPES_4B == ("arithmetic", "option", "string")


def test_paths():
    root = Path("/tmp/_exp4b_paths_test_root")
    assert b4b.verdict_path_4b(root) == root / "results" / "verdict.json"
    assert b4b.verdict_txt_path_4b(root) == root / "results" / "VERDICT.txt"
    assert b4b.placebo_record_path_4b(root) == root / "results" / "placebo.json"
    assert b4b.power_ext_path_4b(root) == root / "results" / "power_ext.json"


def test_tag_names_and_instrument_blobs():
    assert b4b.PREREG_TAG_4B == "exp4b-preregistered"
    assert b4b.CLOSED_TAG_4B == "exp4b-closed"
    assert b4b.EXP4_CLOSED_TAG == "exp4-closed"
    assert b4b.INSTRUMENT_BLOBS_4B == (
        "experiments/exp4b/analyze_4b.py",
        "experiments/exp4b/battery_4b.py",
        "experiments/exp4b/placebo_4b.py",
        "experiments/exp4b/power_ext_4b.py",
        "experiments/exp4b/levels_4b.py",
    )
