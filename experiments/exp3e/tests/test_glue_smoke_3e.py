"""Glue smoke (doc Open item 8): the campaign driver's frozen order,
the runner's refusal preconditions on an empty tree, and the committed
artifacts' presence."""
from pathlib import Path

from experiments.exp3e import analyze_3e as e
from experiments.exp3e.run import campaign_3e, run_cell_3e

EXP3E = Path(e.EXP3E)


def test_tier_plan_is_the_frozen_order():
    assert campaign_3e.tier_plan() == [
        ("gate1", "410m"), ("gate1", "1b"),
        ("sampling", "410m"), ("sampling", "1b")]


def test_campaign_dry_run(capsys):
    rc = campaign_3e.main(["--dry-run", "--out-root", "/nonexistent"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "4 tiers selected" in out
    assert "s28-s43" in out and "s152-s167" in out


def test_runner_refuses_on_empty_tree(tmp_path):
    ok, why = run_cell_3e.scorer_gates_clean(tmp_path)
    assert not ok and "missing" in why
    ok, why = run_cell_3e.gate1_clean(tmp_path)
    assert not ok and "missing" in why


def test_runner_refuses_failed_scorer_gates(tmp_path):
    p = tmp_path / "results" / "scorer_gates.json"
    p.parent.mkdir(parents=True)
    p.write_text('{"passed": false, "gate_a": {"passed": false}, '
                 '"gate_b": {"passed": true}}')
    ok, why = run_cell_3e.scorer_gates_clean(tmp_path)
    assert not ok and "did not pass" in why


def test_block_plan():
    assert run_cell_3e.sampling_record_path(
        "/r", "1b", e.SEED_BLOCKS["1b"][0]).name == \
        "reverse_string.s40-s55.json"
    assert e.SEED_BLOCKS["410m"][-1] == tuple(range(76, 92))


def test_committed_artifacts_exist():
    for p in (e.PARTITION_PATH, e.POWER_PATH, e.STREAM_MAP_3E_PATH):
        assert Path(p).is_file(), p


def test_watcher_exists_and_executable():
    w = EXP3E / "run" / "commit_watcher_3e.sh"
    assert w.is_file()
    assert w.stat().st_mode & 0o111
