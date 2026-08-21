"""Glue smoke: the driver's frozen order, the runner's refusals on an
empty/partial tree, the committed artifacts' presence. No model."""
import json
from pathlib import Path

import pytest

from experiments.exp2d import analyze_2d as a
from experiments.exp2d.run import campaign_2d, run_cell_2d
from experiments.exp2d.tests import full_shape as fs


def test_tier_plan_is_the_frozen_order():
    assert campaign_2d.tier_plan() == [
        ("pilot", "410m"), ("pilot", "1b"),
        ("main", "410m"), ("main", "1b"),
        ("argmax", "410m"), ("argmax", "1b")]


def test_campaign_dry_run(capsys):
    rc = campaign_2d.main(["--dry-run", "--out-root", "/nonexistent"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "6 tiers selected" in out and "34 rung(s) pending" in out
    assert "[float32]" in out and "[float16]" in out


def test_runner_refuses_main_without_pilot_and_power(tmp_path):
    with pytest.raises(RuntimeError, match="pilot/410m incomplete"):
        run_cell_2d.check_preconditions("main", tmp_path)
    battery, _ = fs.battery()
    verify = a.load_verify()
    for size in a.PROBE_SIZES:
        for rung in a.RUNGS:
            rows = fs.synthetic_rows(battery[rung], seed=a.TIERS["pilot"]["seed"], dps=8, verified=0)
            fs.write_sampling_cell(tmp_path, "pilot", size, rung, rows,
                                   verify=verify)
    with pytest.raises(RuntimeError, match="power_2d.json missing"):
        run_cell_2d.check_preconditions("main", tmp_path)
    fs.write_power(tmp_path, "DECLARED UNDERPOWERED IN ADVANCE")
    run_cell_2d.check_preconditions("main", tmp_path)   # runs anyway (c)
    with pytest.raises(RuntimeError, match="main/410m incomplete"):
        run_cell_2d.check_preconditions("argmax", tmp_path)


def test_gate1_diff_halts_every_tier(tmp_path):
    p = a.gate1_record_path(tmp_path, "1b", "reverse_string")
    p.parent.mkdir(parents=True)
    p.write_text(json.dumps({"n_diffs": 3}))
    for kind in ("pilot", "main", "argmax"):
        with pytest.raises(RuntimeError, match="gate 1 fired"):
            run_cell_2d.check_preconditions(kind, tmp_path)


def test_pilot_has_no_preconditions_but_gate1(tmp_path):
    run_cell_2d.check_preconditions("pilot", tmp_path)


def test_committed_artifacts_exist():
    for p in (a.STREAM_MAP_2D_PATH, a.REFERENTS_PATH):
        assert Path(p).is_file(), p
    w = a.EXP2D / "run" / "commit_watcher_2d.sh"
    assert w.is_file() and w.stat().st_mode & 0o111


def test_matrix_literals():
    assert a.TIERS == {"pilot": {"seed": 1000, "draws_per_seed": 8},
                       "main": {"seed": 0, "draws_per_seed": 64}}
    assert a.GATE1_COVERAGE == 32_000 and a.PILOT_DRAWS_PER_RUNG == 4_000
    assert a.STREAM_NAMESPACE == "exp3"
    # ruling L: the pilot seed lies outside every committed range
    from experiments.exp3 import analyze_3 as a3
    from experiments.exp3d import analyze_3d as d
    from experiments.exp3e import analyze_3e as e
    used = set(a3.SEEDS) | set(range(4, 16)) | \
        {s for v in d.SEED_BLOCKS.values() for b in v for s in b} | \
        {s for v in e.NEW_SEEDS_3E.values() for s in v}
    assert max(used) == 167 and a.TIERS["pilot"]["seed"] not in used
