"""Fixture suite for 1c's campaign driver.

WRITTEN AFTER THE FREEZE, on purpose. The driver is execution orchestration:
it decides what runs and in what order, never what a number means. It cannot
touch the verdict, which is fixed by the frozen analyze_1c.py and locked by
that module's own fixtures. Ruling 14 of FREEZE_CHECKLIST.md.

What it must get right is the SHAPE of the campaign — which cells exist, that
twins come first, and that Stage A reads each cell's own checkpoint step
rather than a default. Those are design commitments, so they are tested.
"""
import json

import pytest

from experiments.exp1c.run import campaign_1c as c


def fake_1b_results(root, step=4516):
    for system in ("lubana_above", "lubana_below"):
        for size in ("1M", "10M"):
            for seed in range(100, 105):
                p = root / "results" / system / size / f"seed{seed}.json"
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(json.dumps({
                    "system": system, "size_bucket": size, "seed": seed,
                    "s1": {"checkpoint_id": f"step_{step + seed:07d}"}}))
    return root


# ------------------------------------------------------------- the matrix

def test_the_twin_phase_covers_every_twin_the_design_calls_for():
    """100 twins: 20 Stage A (fixed) + 40 Stage B (fixed) + 40 Stage B
    (natural). Design §8 cost: 120 fixed-arm profiles and 80 natural-arm,
    half of each being twins."""
    cells = c.cells_for_phase("twins")
    assert len(cells) == 100
    assert all(not x.trained for x in cells)
    assert sum(1 for x in cells if x.system == "sweep" and x.arm == "fixed") == 40
    assert sum(1 for x in cells if x.system == "sweep" and x.arm == "natural") == 40
    assert sum(1 for x in cells if x.system != "sweep") == 20


def test_stage_a_is_twenty_trained_cells_on_the_fixed_arm():
    cells = c.cells_for_phase("stage_a")
    assert len(cells) == 20
    assert all(x.trained and x.arm == "fixed" for x in cells)
    assert {x.system for x in cells} == {"lubana_above", "lubana_below"}


def test_stage_b_is_eighty_trained_profiles_across_both_arms():
    cells = c.cells_for_phase("stage_b")
    assert len(cells) == 80
    assert all(x.trained and x.system == "sweep" for x in cells)
    assert sum(1 for x in cells if x.arm == "fixed") == 40
    assert sum(1 for x in cells if x.arm == "natural") == 40
    assert {x.density for x in cells} == {0.25, 0.45, 0.65, 0.85}


def test_stage_a_twins_carry_a_step_and_sweep_cells_do_not(tmp_path):
    """Ruling 16: Stage A must read the checkpoint 1b scored, and those steps
    differ per cell (4516, 3660, 24421...). A default would silently answer a
    different question."""
    fake_1b_results(tmp_path)
    cells = c.cells_for_phase("stage_a", exp1b_root=tmp_path)
    assert all(x.step is not None for x in cells)
    assert len({x.step for x in cells}) > 1
    assert all(x.step is None for x in c.cells_for_phase("stage_b"))


def test_a_missing_1b_record_is_an_error_not_a_default(tmp_path):
    fake_1b_results(tmp_path)
    (tmp_path / "results" / "lubana_above" / "1M" / "seed103.json").unlink()
    with pytest.raises(ValueError, match="seed103|103"):
        c.cells_for_phase("stage_a", exp1b_root=tmp_path)


def test_an_unknown_phase_is_refused():
    with pytest.raises(ValueError, match="phase"):
        c.cells_for_phase("everything")


def test_the_matrix_is_deterministically_ordered():
    assert c.cells_for_phase("twins") == c.cells_for_phase("twins")


# ---------------------------------------------------------------- resume

def test_pending_skips_cells_that_already_have_a_record(tmp_path):
    from experiments.exp1c import records as r

    cells = c.cells_for_phase("twins")
    done = cells[0]
    p = r.record_path(tmp_path, done.system, done.arm, done.density,
                      done.size, done.seed, done.trained)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("{}")
    left = c.pending(cells, tmp_path)
    assert len(left) == 99
    assert done not in left


def test_pending_returns_everything_on_a_fresh_tree(tmp_path):
    cells = c.cells_for_phase("twins")
    assert len(c.pending(cells, tmp_path)) == len(cells)
