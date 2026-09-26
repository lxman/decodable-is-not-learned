import json

import pytest

from experiments.exp2d import battery_2d as bt
from experiments.exp5 import battery_5 as b5
from experiments.exp5 import collect_5 as c5
from experiments.exp5b import battery_5b as b5b
from experiments.exp5b.run import preflight_5b as pf5b
from experiments.exp5b.run import units_5b as un
from experiments.exp5b.tests import helpers_5b as hp
from experiments.exp5.tests import fakes_5 as fk
from experiments.exp5b.tests.test_collect_5b import SIZES, AVAIL, WINDOW, _loss, _count


@pytest.fixture
def env(tmp_path, monkeypatch):
    monkeypatch.setattr(b5, "SIZES_5", SIZES)
    monkeypatch.setattr(b5, "SMALL_SIDES_5", SIZES[:-1])
    monkeypatch.setattr(b5, "LARGE_SIDES_5", SIZES[1:])
    monkeypatch.setattr(b5b, "WINDOW_STEPS_5B", WINDOW)
    monkeypatch.setattr(b5b, "FROZEN_SHA256_5B", {})
    monkeypatch.setattr(b5b, "IMPORTED_SHA256_5B", {})
    monkeypatch.setattr(b5b, "check_imports_5b", lambda: None)
    hp.wrap_prereg_over_present_blobs(monkeypatch)
    man = fk.synthetic_manifest(SIZES, AVAIL)
    battery = bt.load_battery()
    root5, root5b = tmp_path / "exp5", tmp_path / "exp5b"
    loaders5, _ = fk.make_loaders(battery, loss_fn=_loss, count_fn=_count)
    host = c5.host_record_5("cuda", fk.fake_host()["transports"], stack=fk.fake_host()["stack"],
                            gpu="fake", python="3.11.16")
    from experiments.exp2d import analyze_2d as a2d
    kw5 = dict(manifest=man, cache_root=tmp_path, device="cuda", battery=battery,
               verify_fn=a2d.load_verify(), sl=fk.small_slice(), host=host, git_sha="g1")
    for size in SIZES[:-1]:
        for step in (b5.FINAL_STEP_5, WINDOW[0]):
            c5.run_unit_5(size, step, root=root5, loaders=loaders5, why="final" if step == 143000 else "s11", **kw5)
    loaders, state = fk.make_loaders(battery, loss_fn=_loss, count_fn=_count)
    common = dict(root=root5b, exp5_root=root5, cache_root=tmp_path, device="cuda", loaders=loaders,
                  manifest=man, sl=fk.small_slice(), host_meta=fk.fake_host(), git_sha="g2",
                  verdict_sha=False, projection_commit="p2", is_ancestor=lambda a, b: True,
                  power_present=True, **hp.tag_inj())
    return dict(common=common, state=state, root5=root5, root5b=root5b, battery=battery)


def test_runner_refuses_without_the_5b_tag_the_exp5_binding_the_power_record_or_the_projection(env):
    c = dict(env["common"]); c["tag_exists"] = lambda t: t != b5b.PREREG_TAG_5B
    with pytest.raises(RuntimeError, match="exp5b-preregistered"):
        un.run(size="1b", **c)
    c = dict(env["common"]); c["tag_exists"] = lambda t: t != "exp5-closed"
    with pytest.raises(RuntimeError, match="exp5-closed"):
        un.run(size="1b", **c)
    c = dict(env["common"]); c["power_present"] = False
    with pytest.raises(RuntimeError, match="power_5b.json"):
        un.run(size="1b", **c)
    c = dict(env["common"]); c["is_ancestor"] = lambda a, b: False
    with pytest.raises(RuntimeError, match="projection"):
        un.run(size="1b", **c)
    assert not b5b.host_record_path_5b(env["root5b"]).exists()


def test_runner_writes_host_once_then_four_units_in_order_and_the_gate1_record(env):
    un.run(size="1b", **env["common"])
    root = env["root5b"]
    host = json.loads(b5b.host_record_path_5b(root).read_text())
    assert b5.host_record_failures_5(host) == []
    loaded = [s for s in env["state"]["loaded"] if s[0] == "1b"]
    assert loaded == [("1b", 143000), ("1b", 15000), ("1b", 14000), ("1b", 13000)]
    for step in (143000,) + WINDOW:
        assert b5b.unit_complete_5b(root, "1b", step)
    g = json.loads(b5b.gate1_path_5b(root).read_text())
    assert g["pass"] and set(g["per_unit"]) == {"1b/step143000", "1b/step15000"}
    # a second size appends to the gate record; the host record is reused, not rewritten
    sha = host["sha256"]
    un.run(size="2.8b", **env["common"])
    assert json.loads(b5b.host_record_path_5b(root).read_text())["sha256"] == sha
    g = json.loads(b5b.gate1_path_5b(root).read_text())
    assert set(g["per_unit"]) == {"1b/step143000", "1b/step15000", "2.8b/step143000", "2.8b/step15000"}


def test_runner_resumes_reusing_complete_units_and_redoing_a_unit_without_the_5b_record(env):
    un.run(size="1b", **env["common"])
    n = len(env["state"]["loaded"])
    b5b.unit5b_record_path_5b(env["root5b"], "1b", 14000).unlink()
    un.run(size="1b", **env["common"])
    assert len(env["state"]["loaded"]) == n + 1
    assert env["state"]["loaded"][-1] == ("1b", 14000)


def test_runner_halts_on_a_reread_digest_mismatch(env):
    loaders, _ = fk.make_loaders(env["battery"], loss_fn=_loss, count_fn=_count, digest_fn=lambda s, st: "x" + s)
    c = dict(env["common"]); c["loaders"] = loaders
    with pytest.raises(SystemExit):
        un.run(size="1b", **c)
    assert b5b.halt_marker_path_5b(env["root5b"], "1b").exists()
    with pytest.raises(RuntimeError, match="halted"):
        un.run(size="1b", **env["common"])


def test_runner_refuses_a_different_host_record(env):
    un.run(size="1b", **env["common"])
    c = dict(env["common"]); c["host_meta"] = {**fk.fake_host(), "stack": {**fk.fake_host()["stack"], "torch": "2.11.0"}}
    with pytest.raises(RuntimeError, match="host record"):
        un.run(size="2.8b", **c)


def test_runner_dry_run_prints_and_writes_nothing(env, capsys):
    un.run(size="1b", dry_run=True, **env["common"])
    assert "would run 4 unit(s)" in capsys.readouterr().out
    assert not b5b.units_root_5b(env["root5b"]).exists()


def test_preflight_writes_nothing_under_results_and_compares_two_runs(env, capsys):
    from experiments.exp2d import analyze_2d as a2d
    loaders, state = fk.make_loaders(env["battery"], loss_fn=_loss, count_fn=_count)
    host = c5.host_record_5("cuda", fk.fake_host()["transports"], stack=fk.fake_host()["stack"], gpu="fake",
                            python="3.11.16")
    out = pf5b.run(root=env["root5b"], device="cuda", cache_root=env["root5b"] / "cache", loaders=loaders,
                   manifest=env["common"]["manifest"], sl=fk.small_slice(), host=host,
                   battery=env["battery"], verify_fn=a2d.load_verify(), twice_size="1b", timed_size="2.8b")
    assert out["twice_identical"] is True and out["timed"]["size"] == "2.8b" and out["timed"]["seconds"] >= 0
    assert not (env["root5b"] / "results").exists()
    assert state["loaded"].count(("1b", 143000)) == 2 and state["loaded"].count(("2.8b", 143000)) == 1
    assert "IDENTICAL" in capsys.readouterr().out
