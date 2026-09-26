import json

import pytest

from experiments.exp2d import analyze_2d as a2d
from experiments.exp2d import battery_2d as bt
from experiments.exp2g import battery_2g as bg
from experiments.exp5 import battery_5 as b5
from experiments.exp5 import collect_5 as c5
from experiments.exp5b import battery_5b as b5b
from experiments.exp5b import collect_5b as c5b
from experiments.exp5.tests import fakes_5 as fk

SIZES = ("1b", "2.8b", "6.9b")
AVAIL = tuple(range(1000, 17000, 1000)) + (143000,)
WINDOW = (15000, 14000, 13000)


def _loss(size, step):
    return {"1b": 2.6, "2.8b": 2.3, "6.9b": 2.1}[size] + 30.0 / (step ** 0.5)


def _count(size, step, rung):
    if rung not in ("antonym", "antonym6", "arith_next"):
        return 0
    return min(500, int(80 + 120 * (1 - 1 / (1 + step / 5000))))


@pytest.fixture
def env(tmp_path, monkeypatch):
    monkeypatch.setattr(b5, "SIZES_5", SIZES)
    monkeypatch.setattr(b5, "SMALL_SIDES_5", SIZES[:-1])
    monkeypatch.setattr(b5, "LARGE_SIDES_5", SIZES[1:])
    monkeypatch.setattr(b5b, "WINDOW_STEPS_5B", WINDOW)
    man = fk.synthetic_manifest(SIZES, AVAIL)
    battery = bt.load_battery()
    verify_fn = a2d.load_verify()
    host = c5.host_record_5("cuda", fk.fake_host()["transports"], stack=fk.fake_host()["stack"],
                            gpu="fake", python="3.11.16")
    root5, root5b = tmp_path / "exp5", tmp_path / "exp5b"
    loaders5, _ = fk.make_loaders(battery, loss_fn=_loss, count_fn=_count)
    kw = dict(manifest=man, cache_root=tmp_path, device="cuda", battery=battery, verify_fn=verify_fn,
              sl=fk.small_slice(), host=host, git_sha="g1")
    # "Experiment 5's committed units": the finals and the S11-step units, written by Experiment 5's writer
    for size in SIZES[:-1]:
        for step in (b5.FINAL_STEP_5, WINDOW[0]):
            c5.run_unit_5(size, step, root=root5, loaders=loaders5, why="final" if step == 143000 else "s11", **kw)
    return dict(root5=root5, root5b=root5b, kw=kw, battery=battery, host=host, man=man)


def test_run_unit_5b_writes_the_5b_record_last_and_compares_a_reread(env):
    loaders, state = fk.make_loaders(env["battery"], loss_fn=_loss, count_fn=_count)
    r = c5b.run_unit_5b("1b", b5.FINAL_STEP_5, root=env["root5b"], exp5_root=env["root5"], why="final",
                        loaders=loaders, **env["kw"])
    assert r["action"] == "loaded" and r["reread"]["digest_equal"] and r["reread"]["byte_identical"]
    assert r["reread"]["loss_delta"] == 0.0 and r["reread"]["tolerance_failures"] == []
    d = b5b.unit_dir_5b(env["root5b"], "1b", b5.FINAL_STEP_5)
    rec = json.loads((d / "_unit_5b.json").read_text())
    assert b5b.unit5b_record_failures_5b(rec, size="1b", step=b5.FINAL_STEP_5, host=env["host"]) == []
    assert (d / "_unit_5b.json").stat().st_mtime_ns >= (d / "_unit.json").stat().st_mtime_ns
    assert b5b.unit_complete_5b(env["root5b"], "1b", b5.FINAL_STEP_5)
    # a non-re-read member carries no reread record
    r2 = c5b.run_unit_5b("1b", WINDOW[1], root=env["root5b"], exp5_root=env["root5"], why="member",
                         loaders=loaders, **env["kw"])
    assert r2["reread"] is None
    rec2 = json.loads(b5b.unit5b_record_path_5b(env["root5b"], "1b", WINDOW[1]).read_text())
    assert rec2["reread"] is False and rec2["reread_record"] is None
    # reuse: a complete 5b unit is never reloaded
    n = len(state["loaded"])
    r3 = c5b.run_unit_5b("1b", b5.FINAL_STEP_5, root=env["root5b"], exp5_root=env["root5"], why="final",
                         loaders=loaders, **env["kw"])
    assert r3["action"] == "reused" and len(state["loaded"]) == n


def test_run_unit_5b_redoes_a_unit_without_the_5b_record(env):
    """Review Focus 1: Experiment-5-complete but no _unit_5b.json → re-run whole."""
    loaders, state = fk.make_loaders(env["battery"], loss_fn=_loss, count_fn=_count)
    c5b.run_unit_5b("1b", WINDOW[1], root=env["root5b"], exp5_root=env["root5"], why="member",
                    loaders=loaders, **env["kw"])
    b5b.unit5b_record_path_5b(env["root5b"], "1b", WINDOW[1]).unlink()
    assert b5.unit_complete_5(env["root5b"], "1b", WINDOW[1]) and not b5b.unit_complete_5b(env["root5b"], "1b", WINDOW[1])
    n = len(state["loaded"])
    r = c5b.run_unit_5b("1b", WINDOW[1], root=env["root5b"], exp5_root=env["root5"], why="member",
                        loaders=loaders, **env["kw"])
    assert r["action"] == "loaded" and len(state["loaded"]) == n + 1
    assert b5b.unit_complete_5b(env["root5b"], "1b", WINDOW[1])


def test_reread_digest_mismatch_halts_after_writing_the_unit(env):
    loaders, _ = fk.make_loaders(env["battery"], loss_fn=_loss, count_fn=_count,
                                 digest_fn=lambda s, st: "other-" + s)
    with pytest.raises(SystemExit):
        c5b.run_unit_5b("1b", b5.FINAL_STEP_5, root=env["root5b"], exp5_root=env["root5"], why="final",
                        loaders=loaders, **env["kw"])
    assert b5b.halt_marker_path_5b(env["root5b"], "1b").exists()
    rec = json.loads(b5b.unit5b_record_path_5b(env["root5b"], "1b", b5.FINAL_STEP_5).read_text())
    assert rec["reread_record"]["digest_equal"] is False
    # halt_on_digest=False (the analyzer's refusal tests build such trees)
    r = c5b.run_unit_5b("2.8b", b5.FINAL_STEP_5, root=env["root5b"], exp5_root=env["root5"], why="final",
                        loaders=loaders, halt_on_digest=False, **env["kw"])
    assert r["reread"]["digest_equal"] is False


def test_reread_count_tolerance_is_recorded_not_halted(env):
    def count_b(size, step, rung):
        return _count(size, step, rung) + (20 if (rung == "antonym" and step == b5.FINAL_STEP_5) else 0)
    loaders, _ = fk.make_loaders(env["battery"], loss_fn=_loss, count_fn=count_b)
    r = c5b.run_unit_5b("1b", b5.FINAL_STEP_5, root=env["root5b"], exp5_root=env["root5"], why="final",
                        loaders=loaders, **env["kw"])
    assert r["reread"]["digest_equal"] and r["reread"]["tolerance_failures"]
    assert r["reread"]["count_abs_diff_max"] == 20 and not r["reread"]["byte_identical"]
    g = c5b.gate1_record_5b(env["root5b"], host=env["host"], git_sha="g1")
    assert g["pass"] is False and g["per_unit"]["1b/step143000"]["count_abs_diff_max"] == 20


def test_reread_loss_delta_beyond_tolerance_is_recorded(env):
    loaders, _ = fk.make_loaders(env["battery"], loss_fn=lambda s, st: _loss(s, st) + 1e-3, count_fn=_count)
    r = c5b.run_unit_5b("1b", WINDOW[0], root=env["root5b"], exp5_root=env["root5"], why="member",
                        loaders=loaders, **env["kw"])
    assert r["reread"]["loss_within_tol"] is False and r["reread"]["loss_delta"] == pytest.approx(1e-3)


def test_nothing_is_written_under_the_exp5_root(env):
    from experiments.exp5.run import preflight_5 as pf5
    before = pf5._results_snapshot(env["root5"])
    loaders, _ = fk.make_loaders(env["battery"], loss_fn=_loss, count_fn=_count)
    for step in (b5.FINAL_STEP_5,) + WINDOW:
        c5b.run_unit_5b("1b", step, root=env["root5b"], exp5_root=env["root5"],
                        why="final" if step == 143000 else "member", loaders=loaders, **env["kw"])
    assert pf5._results_snapshot(env["root5"]) == before
