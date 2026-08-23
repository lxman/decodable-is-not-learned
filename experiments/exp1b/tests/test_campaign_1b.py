"""Campaign driver: the plan's shape, its ordering, and skip-if-exists.

No test runs a cell. The point of these is that the plan is complete, uses
fresh seeds, orders the cheap tier first, and that a trained cell and its
untrained twin are guaranteed to be built from the same recipe — the last of
which is what makes them twins at all.
"""
import pytest

from experiments.exp1b.run import campaign_1b as c
from experiments.exp1b.run import run_untrained as ru


def test_plan_covers_every_cell():
    plan = c.campaign_plan()
    assert len(plan) == 2 * 3 * 2 * 5      # kinds x systems x sizes x seeds
    assert {k for k, _, _, _ in plan} == {"trained", "untrained"}
    assert {s for _, _, s, _ in plan} == {"1M", "10M"}
    assert {sd for _, _, _, sd in plan} == {100, 101, 102, 103, 104}
    assert len(set(plan)) == len(plan)     # no cell planned twice


def test_plan_never_uses_an_exp1_seed():
    """Seeds 0-4 have known S1 outcomes; reusing one would not be a fresh test."""
    assert all(sd >= 100 for _, _, _, sd in c.campaign_plan())


def test_plan_runs_the_cheap_tier_first():
    plan = c.campaign_plan()
    order = []
    for _, _, size, _ in plan:
        if size not in order:
            order.append(size)
    assert order == ["1M", "10M"]


def test_untrained_cells_run_last():
    """They are nearly free and depend on nothing, so they must not sit in
    front of the tier that takes days."""
    kinds = [k for k, _, _, _ in c.campaign_plan()]
    assert kinds.index("untrained") > max(
        i for i, k in enumerate(kinds) if k == "trained")


def test_grokking_runs_first_within_a_size():
    """~31 min for five seeds against ~24 h for a lubana row: the row that can
    surface a problem quickly goes first."""
    first = [s for k, s, z, _ in c.campaign_plan() if k == "trained" and z == "1M"]
    assert first[0] == "grokking"


def test_trained_and_untrained_paths_do_not_collide():
    t = c.record_path_for("trained", "grokking", "1M", 100)
    u = c.record_path_for("untrained", "grokking", "1M", 100)
    assert t != u
    assert u.parent.parent.parent.name == "untrained"


def test_remaining_skips_existing_records(tmp_path, monkeypatch):
    monkeypatch.setattr(c, "OUT_ROOT", tmp_path)
    before = len(c.remaining())
    p = c.record_path_for(*c.campaign_plan()[0])
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("{}")
    assert len(c.remaining()) == before - 1


def test_remaining_is_empty_when_every_record_exists(tmp_path, monkeypatch):
    monkeypatch.setattr(c, "OUT_ROOT", tmp_path)
    for cell in c.campaign_plan():
        p = c.record_path_for(*cell)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("{}")
    assert c.remaining() == []


def test_the_lubana_recipe_is_shared_with_the_untrained_runner():
    """A trained cell and its twin must be the same architecture on the same
    data. If the campaign redefined scale or model_size, they would silently
    stop being twins and the floor correction would compare across recipes.
    Shared objects, not equal copies."""
    assert c.LUBANA_SCALE is ru.LUBANA_SCALE
    assert c.LUBANA_MODEL_SIZE is ru.LUBANA_MODEL_SIZE
    assert set(c.LUBANA_MODEL_SIZE) == set(c.SIZES)


def test_every_planned_cell_has_a_dispatch_route():
    """No (kind, system) pair may fall through to an unhandled branch."""
    for kind, system, size, seed in c.campaign_plan():
        assert c.describe_cell(kind, system, size, seed)


def _record_calls(monkeypatch, tmp_path):
    """Replace the three runners with recorders. Nothing trains."""
    calls = []
    monkeypatch.setattr(c, "OUT_ROOT", tmp_path)
    monkeypatch.setattr(c, "run_grokking",
                        lambda *a, **k: calls.append(("grokking", a, k)))
    monkeypatch.setattr(c, "run_lubana",
                        lambda *a, **k: calls.append(("lubana", a, k)))
    monkeypatch.setattr(c, "run_untrained",
                        lambda *a, **k: calls.append(("untrained", a, k)))
    return calls


def test_grokking_dispatch_passes_seed_and_size_in_that_order(monkeypatch, tmp_path):
    """run_grokking(seed, size, out_dir) — swapping the first two is a silent
    disaster: 'seed 1M' is not a TypeError, it is a wrong run."""
    calls = _record_calls(monkeypatch, tmp_path)
    c.run_cell("trained", "grokking", "10M", 103)
    name, args, kwargs = calls[0]
    assert name == "grokking"
    assert args[0] == 103 and args[1] == "10M"
    assert kwargs["out_dir"] == tmp_path


def test_lubana_dispatch_maps_system_to_setting_and_size_to_model_size(
        monkeypatch, tmp_path):
    calls = _record_calls(monkeypatch, tmp_path)
    c.run_cell("trained", "lubana_below", "10M", 101)
    c.run_cell("trained", "lubana_above", "1M", 100)
    below, above = calls[0][1], calls[1][1]
    assert below[0] == "below" and below[1] == 101
    assert above[0] == "above" and above[1] == 100
    # scale is the shared constant; 10M carries model_size None, 1M carries "1M"
    assert below[2] == ru.LUBANA_SCALE and below[3] is None
    assert above[2] == ru.LUBANA_SCALE and above[3] == "1M"


def test_untrained_dispatch_passes_system_size_seed_and_root(monkeypatch, tmp_path):
    calls = _record_calls(monkeypatch, tmp_path)
    c.run_cell("untrained", "lubana_above", "1M", 104)
    _name, args, _kwargs = calls[0]
    assert args == ("lubana_above", "1M", 104, tmp_path)


def test_an_unknown_route_is_refused_not_silently_skipped(monkeypatch, tmp_path):
    _record_calls(monkeypatch, tmp_path)
    with pytest.raises(ValueError):
        c.run_cell("trained", "phaseA", "1M", 100)
