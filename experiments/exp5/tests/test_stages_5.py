# experiments/exp5/tests/test_stages_5.py
import json
import subprocess
from pathlib import Path

import pytest

from experiments.exp2d import battery_2d as bt
from experiments.exp2d import analyze_2d as a2d
from experiments.exp2g import battery_2g as bg
from experiments.exp5 import battery_5 as b5
from experiments.exp5 import collect_5 as c5
from experiments.exp5.run import finals_5 as fin
from experiments.exp5.run import preflight_5 as pf5
from experiments.exp5.run import s9_mac_5 as s9
from experiments.exp5.run import sweep_5 as sw
from experiments.exp5 import search_5 as se
from experiments.exp5.tests import fakes_5 as fk

SIZES = ("1b", "2.8b", "6.9b")
AVAIL = tuple(range(1000, 17000, 1000)) + (143000,)
SPINE = (1000, 4000, 16000, 143000)


def _loss(size, step):
    base = {"1b": 2.6, "2.8b": 2.3, "6.9b": 2.1}[size]
    return base + 30.0 / (step ** 0.5)


def _count(size, step, rung):
    if rung not in ("antonym", "antonym6", "arith_next"):
        return 0
    return min(500, int(80 + 120 * (1 - 1 / (1 + step / 5000))))


@pytest.fixture
def env(tmp_path, monkeypatch):
    monkeypatch.setattr(b5, "SIZES_5", SIZES)
    monkeypatch.setattr(b5, "PAIRS_5", tuple((s, L) for i, s in enumerate(SIZES) for L in SIZES[i + 1:]))
    monkeypatch.setattr(b5, "SMALL_SIDES_5", SIZES[:-1])
    monkeypatch.setattr(b5, "LARGE_SIDES_5", SIZES[1:])
    monkeypatch.setattr(b5, "SPINE_5", SPINE)
    monkeypatch.setattr(b5, "GATE1_INTERIOR_5", {})
    monkeypatch.setattr(b5, "GATE1_REFERENT_SOURCE_5", {})
    monkeypatch.setattr(b5, "FROZEN_SHA256_5", {})
    monkeypatch.setattr(b5, "IMPORTED_SHA256_5", {})
    monkeypatch.setattr(b5, "check_imports_5", lambda: None)   # pinned at Task 6; a no-op here
    # analyze_5.py/power_5.py are Task 5/6 deliverables, not yet on disk at Task 4 —
    # `require_prereg_5`'s `blobs` keyword-default is bound to INSTRUMENT_BLOBS_5 at DEFINITION
    # time (module import), so patching the module attribute alone does not reach it; wrap the
    # function so `finals_5.run`/`sweep_5.run`'s un-parameterized call (they never pass `blobs=`)
    # is exercised over the files the build has BY THIS TASK's end (parallels the check_imports_5
    # override above, same reason).
    _orig_require_prereg_5 = b5.require_prereg_5
    _blobs_so_far = tuple(p for p in b5.INSTRUMENT_BLOBS_5
                          if p not in ("experiments/exp5/analyze_5.py", "experiments/exp5/power_5.py"))
    monkeypatch.setattr(b5, "require_prereg_5",
                        lambda *, tag_exists=None, blob_sha=None, blobs=_blobs_so_far:
                        _orig_require_prereg_5(tag_exists=tag_exists, blob_sha=blob_sha, blobs=blobs))
    monkeypatch.setattr(b5, "S11_STEP_5", 15000)
    man = fk.synthetic_manifest(SIZES, AVAIL)
    battery = bt.load_battery()
    loaders, state = fk.make_loaders(battery, loss_fn=_loss, count_fn=_count,
                                     pythia_2c_count_fn=_count, loss_2c_fn=_loss)
    prereg = dict(tag_exists=lambda t: True, blob_sha=lambda t, r: bg.sha256_file(b5.REPO / r))
    common = dict(root=tmp_path, cache_root=tmp_path, device="cuda", loaders=loaders,
                  manifest=man, sl=fk.small_slice(), host_meta=fk.fake_host(),
                  git_sha="g1", **prereg)
    return dict(common=common, state=state, root=tmp_path, battery=battery)


def _seal_ok(root, tag_exists=None, blobs_bound=None):
    return {"tag": b5.TARGETS_SEAL_TAG_5, "n_paths": 0, "failures": []}


def test_finals_refuses_without_the_prereg_tag(env):
    c = dict(env["common"]); c["tag_exists"] = lambda t: False
    with pytest.raises(RuntimeError, match="does not exist"):
        fin.run(**c)


def test_finals_writes_host_gate1a_gate1b_and_seven_finals(env):
    fin.run(**env["common"])
    root = env["root"]
    host = json.loads(b5.host_record_path_5(root).read_text())
    assert b5.host_record_failures_5(host) == []
    g1a = json.loads(b5.gate1a_path_5(root).read_text())
    assert g1a["pass"] and g1a["digests_equal"] and g1a["loss_equal"] and \
        all(v == 0 for v in g1a["continuation_diffs"].values()) and \
        all(v == 500 for v in g1a["continuations_compared"].values())
    g1b = json.loads(b5.gate1b_path_5(root).read_text())
    assert g1b["pass"] and g1b["no_referent"] == list(SIZES)     # GATE1_REFERENT_SOURCE_5 emptied
    for size in SIZES:
        assert b5.unit_complete_5(root, size, b5.FINAL_STEP_5)
    table = json.loads(b5.loss_table_path_5(root).read_text())
    assert set(table) == set(SIZES) and all("143000" in table[s] for s in SIZES)
    assert env["state"]["loaded"].count(("2.8b", 143000)) == 1       # gate 1(a)'s path b IS the unit


def test_finals_halts_on_a_gate1a_digest_mismatch(env):
    c = dict(env["common"])
    loaders, _ = fk.make_loaders(env["battery"], loss_fn=_loss, count_fn=_count,
                                 pythia_2c_count_fn=_count, loss_2c_fn=_loss, pythia_2c_digest="other")
    c["loaders"] = loaders
    with pytest.raises(SystemExit):
        fin.run(**c)
    assert b5.halt_marker_path_5(env["root"], "2.8b").exists()
    assert not b5.gate1a_path_5(env["root"]).is_file() or \
        not json.loads(b5.gate1a_path_5(env["root"]).read_text())["pass"]


def test_finals_halts_on_a_gate1b_tolerance_failure(env, monkeypatch):
    monkeypatch.setattr(b5, "GATE1_REFERENT_SOURCE_5", {"1b": "fake"})
    monkeypatch.setattr(b5, "mac_final_counts_5",
                        lambda size: ({r: 0 for r in bt.RUNGS} if size == "1b" else None))
    with pytest.raises(SystemExit):
        fin.run(**env["common"])
    assert b5.halt_marker_path_5(env["root"], "1b").exists()
    g1b = json.loads(b5.gate1b_path_5(env["root"]).read_text())
    assert not g1b["pass"] and any("antonym" in f for f in g1b["failures"])


def test_finals_host_record_is_write_once_and_stack_checked(env):
    fin.run(**env["common"])
    c = dict(env["common"]); c["host_meta"] = {**fk.fake_host(), "stack": {**fk.fake_host()["stack"], "torch": "9.9"}}
    with pytest.raises(RuntimeError, match="host record"):
        fin.run(**c)


def _sweep_kwargs(env, **over):
    kw = dict(env["common"])
    kw.update(dict(seal_check=_seal_ok, projection_commit="p1", is_ancestor=lambda a, b: True,
                   power_present=True))
    kw.update(over)
    return kw


def test_sweep_refuses_without_finals_seal_power_or_projection(env):
    fin.run(**env["common"])
    with pytest.raises(RuntimeError, match="seal"):
        sw.run(size="2.8b", **_sweep_kwargs(env, seal_check=lambda r, **k: {"failures": ["x"]}))
    with pytest.raises(RuntimeError, match="power"):
        sw.run(size="2.8b", **_sweep_kwargs(env, power_present=False))
    with pytest.raises(RuntimeError, match="projection"):
        sw.run(size="2.8b", **_sweep_kwargs(env, projection_commit=None))
    with pytest.raises(RuntimeError, match="projection"):
        sw.run(size="2.8b", **_sweep_kwargs(env, is_ancestor=lambda a, b: False))


def test_sweep_spine_then_brackets_then_windows_then_s11(env):
    fin.run(**env["common"])
    sw.run(size="2.8b", **_sweep_kwargs(env))
    root = env["root"]
    log = json.loads(b5.search_log_path_5(root, "2.8b").read_text())
    assert log["spine"] == list(SPINE)
    assert [r["step"] for r in log["requests"][:len(SPINE) - 1]] == list(SPINE[:-1])
    pair = log["pairs"]["1b"]
    assert pair["status"] == "done"
    lo, hi = pair["plan"]["bracket"]
    losses = {int(k): v["loss"] for k, v in json.loads(b5.loss_table_path_5(root).read_text())["2.8b"].items()}
    assert losses[lo] >= pair["target"] > losses[hi] and hi - lo == 1000
    for s in pair["plan"]["b_minus"] + pair["plan"]["b_plus"] + [lo, hi]:
        assert b5.unit_complete_5(root, "2.8b", s)
    assert log["s11"]["step"] == 15000 and b5.unit_complete_5(root, "2.8b", 15000)
    # nothing else loaded: every unit on disk is named by the spine, the pair, the final or S11
    named = set(SPINE) | {lo, hi} | set(pair["plan"]["b_minus"]) | set(pair["plan"]["b_plus"]) \
        | set(pair["plan"]["bisected"]) | {15000}
    on_disk = {int(p.name[4:]) for p in (b5.units_root_5(root) / "2.8b").iterdir() if p.name.startswith("step")}
    assert on_disk == named


def test_sweep_reuses_units_across_partners_and_records_it(env):
    fin.run(**env["common"])
    sw.run(size="6.9b", **_sweep_kwargs(env))
    root = env["root"]
    manifest = env["common"]["manifest"]
    log = json.loads(b5.search_log_path_5(root, "6.9b").read_text())
    # RULING A: `requested_all` is the complete replay (spine + bisect + window, in order),
    # each step marked "loaded" (this pair's own request() calls, in `requests`) or "reused"
    # (plan_5 found it already known — the spine, or the pre-loaded final). The plain
    # `requests` list stays loaded-only, so it alone never shows "reused" (confirmed structural
    # in the Task 4 report); `requested_all` is where both actions are visible.
    actions = [r["action"] for pair in log["pairs"].values() for r in pair["requested_all"]]
    assert "reused" in actions and "loaded" in actions
    assert set(log["pairs"]) == {"1b", "2.8b"}
    loaded = env["state"]["loaded"]
    assert len(loaded) == len(set(loaded))            # no unit loaded twice

    # gate 4's identity: requested_all reproduces exactly what a fresh reader of the COMMITTED
    # loss table (not the in-memory losses the run used) would replay, for every done pair.
    avail = b5.available_5(manifest, "6.9b")
    spine = b5.spine_5(manifest, "6.9b")
    table = json.loads(b5.loss_table_path_5(root).read_text())["6.9b"]
    losses_committed = {int(k): v["loss"] for k, v in table.items()}
    for small, pair in log["pairs"].items():
        if pair["status"] != "done":
            continue
        rep = se.replay_5(losses_committed, avail, spine, pair["target"])
        assert [r["step"] for r in pair["requested_all"]] == se.requested_steps_5(rep)


def test_sweep_drops_a_pair_the_large_model_never_reaches(env, monkeypatch):
    fin.run(**env["common"])
    # make 1b's final loss LOWER than anything 2.8b reaches
    p = b5.loss_record_path_5(env["root"], "1b", b5.FINAL_STEP_5)
    rec = json.loads(p.read_text()); rec["loss"] = 0.5
    for v in rec["per_set"].values():
        v["loss"] = 0.5
    p.write_text(json.dumps(rec))
    unit = json.loads(b5.unit_record_path_5(env["root"], "1b", b5.FINAL_STEP_5).read_text())
    unit["files"]["_loss.json"] = bg.sha256_file(p)
    b5.unit_record_path_5(env["root"], "1b", b5.FINAL_STEP_5).write_text(json.dumps(unit))
    c5.rebuild_loss_table_5(env["root"])
    sw.run(size="2.8b", **_sweep_kwargs(env))
    log = json.loads(b5.search_log_path_5(env["root"], "2.8b").read_text())
    assert log["pairs"]["1b"]["status"] == "dropped"


def test_sweep_resumes_and_refuses_when_halted(env):
    fin.run(**env["common"])
    sw.run(size="2.8b", **_sweep_kwargs(env))
    n = len(env["state"]["loaded"])
    sw.run(size="2.8b", **_sweep_kwargs(env))          # idempotent: nothing new loaded
    assert len(env["state"]["loaded"]) == n
    b5.halt_marker_path_5(env["root"], "2.8b").write_text("x\n")
    with pytest.raises(RuntimeError, match="halted"):
        sw.run(size="2.8b", **_sweep_kwargs(env))


def test_sweep_dry_run_writes_nothing(env):
    fin.run(**env["common"])
    before = {p for p in env["root"].rglob("*")}
    sw.run(size="2.8b", dry_run=True, **_sweep_kwargs(env))
    assert {p for p in env["root"].rglob("*")} == before


def test_sweep_gate1c_halts_on_tolerance(env, monkeypatch):
    fin.run(**env["common"])
    monkeypatch.setattr(b5, "GATE1_INTERIOR_5", {"2.8b": (1000, 4000)})
    monkeypatch.setattr(b5, "mac_interior_counts_5", lambda size, step: {r: 400 for r in bt.RUNGS})
    with pytest.raises(SystemExit):
        sw.run(size="2.8b", **_sweep_kwargs(env))
    g = json.loads(b5.gate1c_path_5(env["root"], "2.8b").read_text())
    assert not g["pass"] and b5.halt_marker_path_5(env["root"], "2.8b").exists()


def test_sweep_prefetches_spine_and_window_steps_but_never_bisected(env):
    fin.run(**env["common"])
    sw.run(size="2.8b", **_sweep_kwargs(env))
    root = env["root"]
    log = json.loads(b5.search_log_path_5(root, "2.8b").read_text())
    prefetched = set(env["state"]["prefetched"])
    # Every spine step after the first — except the spine's own last point,
    # which is FINAL_STEP_5: fin.run() above already completed that unit,
    # so the completeness guard suppresses its prefetch (nothing to fetch).
    for s in SPINE[1:-1]:
        assert ("2.8b", b5.revision_of_5(s)) in prefetched
    assert ("2.8b", b5.revision_of_5(SPINE[-1])) not in prefetched
    for pair in log["pairs"].values():
        window_reqs = [r["step"] for r in pair["requests"] if r["why"] == "window"]
        for s in window_reqs[1:]:                     # every WINDOW step after the first
            assert ("2.8b", b5.revision_of_5(s)) in prefetched
        for r in pair["requests"]:                     # NO bisected step is ever prefetched
            if r["why"] == "bisect":
                assert ("2.8b", b5.revision_of_5(r["step"])) not in prefetched


def test_preflight_runs_on_the_fakes_and_writes_nothing_under_results(env, tmp_path_factory):
    fin.run(**env["common"])
    root = env["root"]
    cache_root = tmp_path_factory.mktemp("preflight_cache")   # separate from root/results entirely
    before = {p for p in root.rglob("*")}
    host = c5.host_record_5("cuda", fk.fake_host()["transports"], stack=fk.fake_host()["stack"],
                            gpu="fake", python="3.11.16")
    pf5.run(root=root, cache_root=cache_root, device="cuda", loaders=env["common"]["loaders"],
           manifest=env["common"]["manifest"], sl=env["common"]["sl"], battery=env["battery"],
           verify_fn=a2d.load_verify(), host=host,
           probe_size="6.9b", probe_steps=(1000, 2000), rung="antonym", final_size="1b")
    after = {p for p in root.rglob("*")}
    assert after == before                             # nothing landed under root/ at all —
    # in particular results/host_5.json (already written by the fin.run() call above) is untouched


def test_s9_mac_writes_one_unit_with_host_record_and_tolerance(env):
    fin.run(**env["common"])
    sw.run(size="2.8b", **_sweep_kwargs(env))
    root = env["root"]
    box_counts = {r: json.loads(b5.rung_record_path_5(root, "2.8b", 4000, r).read_text())["correct"]
                 for r in bt.RUNGS}
    host = s9.mac_host_record_5(write_once_root=root, stack=fk.fake_host()["stack"],
                                gpu="fake-mac", python="3.11.16")
    assert b5.host_record_failures_5(host) == [] and host["device"] == "mps"
    assert s9.s9_host_path_5(root).is_file()
    # write-once: a second call with a DIFFERENT stack still returns the on-disk record
    host2 = s9.mac_host_record_5(write_once_root=root,
                                 stack={**fk.fake_host()["stack"], "torch": "9.9"})
    assert host2 == host
    out = s9.run(size="2.8b", step=4000, root=root, cache_root=root, device="mps",
                loaders=env["common"]["loaders"], manifest=env["common"]["manifest"],
                sl=env["common"]["sl"], host=host, box_counts=box_counts)
    d = b5.s9_dir_5(root, "2.8b", 4000)
    assert set(p.name for p in d.iterdir()) == set(b5.unit_files_5()) | {"_unit.json"}
    assert out["failures"] == []                        # identical counts against itself
    assert not b5.unit_complete_5(root, "2.8b", 4000) or \
        b5.rung_record_path_5(root, "2.8b", 4000, "antonym").is_file()   # the campaign unit untouched


# ------------------------------------------------------- box shell scripts

SCRIPTS_5 = ("campaign_5.sh", "box_setup_5.sh", "pull_units_5.sh", "status_box_5.sh",
            "commit_watcher_5.sh")


@pytest.mark.parametrize("name", SCRIPTS_5)
def test_box_script_is_syntactically_valid_bash(name):
    p = Path(__file__).resolve().parents[1] / "run" / name
    assert p.is_file(), f"{p} missing"
    r = subprocess.run(["bash", "-n", str(p)], capture_output=True, text=True)
    assert r.returncode == 0, f"{name}: {r.stderr}"


@pytest.mark.parametrize("name", SCRIPTS_5)
def test_box_script_is_executable(name):
    p = Path(__file__).resolve().parents[1] / "run" / name
    assert p.stat().st_mode & 0o111, f"{name} is not executable"
