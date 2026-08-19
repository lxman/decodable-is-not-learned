"""Glue smoke (doc Open item 7): the campaign driver's frozen order,
the runner's refusal preconditions on an empty tree, and the
committed artifacts' presence."""
from pathlib import Path

from experiments.exp3d import analyze_3d as d
from experiments.exp3d.run import campaign_3d, run_cell_3d

EXP3D = Path(d.EXP3D)


def test_tier_plan_is_the_frozen_order():
    assert campaign_3d.tier_plan() == [
        ("gate1", "410m"), ("gate1", "1b"),
        ("scoring", "410m"), ("scoring", "1b"),
        ("sampling", "410m"), ("sampling", "1b")]


def test_campaign_dry_run(capsys):
    rc = campaign_3d.main(["--dry-run"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "6 tiers selected" in out


def test_runner_refuses_on_empty_tree(tmp_path):
    ok, why = run_cell_3d.gate1_clean(tmp_path)
    assert not ok and "missing" in why
    ok, why = run_cell_3d.scoring_clean(tmp_path)
    assert not ok and "missing" in why


def test_committed_artifacts_exist():
    for p in (d.SELECTION_PATH, d.POWER_PATH, d.STREAM_MAP_3D_PATH,
              EXP3D / "span_validation_3d.json"):
        assert Path(p).is_file(), p


def test_watcher_exists_and_executable():
    w = EXP3D / "run" / "commit_watcher_3d.sh"
    assert w.is_file()
    assert w.stat().st_mode & 0o111
