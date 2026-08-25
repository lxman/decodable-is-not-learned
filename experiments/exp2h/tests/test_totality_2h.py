# experiments/exp2h/tests/test_totality_2h.py
"""Verdict-path totality (freeze F-1): every tree the runner can leave —
and every hand-editable shape short of it — must reach a FROZEN TERMINAL
through `analyze_2h.run()`, never an uncaught exception. Each case below
RAISED before the freeze's `collect_total` closure; the control proves
the same harness still reaches CONFIRMED on an untouched world.

The 2d F-1 standard, one level over: §6's first terminal has to be
reachable from the tree the analyzer is actually handed.
"""
import json
import shutil

import pytest

from experiments.exp2g import battery_2g as bg
from experiments.exp2h import analyze_2h as an
from experiments.exp2h import battery_2h as bh
from experiments.exp2h.tests import full_shape as fs


@pytest.fixture(scope="module")
def base_world(tmp_path_factory):
    root = tmp_path_factory.mktemp("totality_base")
    seal = fs.write_world(root, mode="rank")
    return root, seal


@pytest.fixture
def world(base_world, tmp_path):
    root, seal = base_world
    shutil.copytree(root / "results", tmp_path / "results")
    return tmp_path, seal


def _run(root, seal, **kw):
    kw.setdefault("n_perm", 20)
    kw.setdefault("n_boot", 10)
    return an.run(root=root, referents_sha=None, power_sha=None,
                  manifest_sha=an.CHECKPOINTS_2H_SHA256, **{**seal, **kw})


def _insufficient(root, seal, needle):
    v = _run(root, seal)
    assert v["verdict"] == "INSUFFICIENT_DATA", v["verdict"]
    assert needle in v["reason"], v["reason"]
    assert v["primary"] is None
    return v


# ------------------------------------------------- gate-1 record shapes

@pytest.mark.parametrize("payload", ["[]", '"halted"', '{"size": "6.9b", "rungs": ['])
def test_gate1_non_dict_or_torn(world, payload):
    root, seal = world
    bh.gate1_path_2h(root).write_text(payload)
    _insufficient(root, seal, "gate 1 6.9b")


@pytest.mark.parametrize("field,value", [("rungs", 34),
                                         ("continuation_diffs_2h_path", [0, 0]),
                                         ("counts_2c_path", [1, 2, 3])])
def test_gate1_field_of_the_wrong_type(world, field, value):
    root, seal = world
    p = bh.gate1_path_2h(root)
    rec = json.loads(p.read_text())
    rec[field] = value
    p.write_text(json.dumps(rec))
    _insufficient(root, seal, "gate 1 6.9b")


def test_gate1_is_a_directory(world):
    root, seal = world
    p = bh.gate1_path_2h(root)
    p.unlink()
    p.mkdir()
    _insufficient(root, seal, "record missing")


# ------------------------------------------------------- the halt marker

def test_halt_marker_is_a_directory(world):
    root, seal = world
    bh.halt_marker_path_2h(root).mkdir(parents=True)
    _insufficient(root, seal, "halt marker")


def test_halt_marker_present(world):
    root, seal = world
    bh.halt_marker_path_2h(root).write_text("gate 1 6.9b: counts drifted\n")
    _insufficient(root, seal, "the runner halted")


# --------------------------------------------------------- step records

def test_step_record_non_dict(world):
    root, seal = world
    bh.record_path_2h(root, 40000, "antonym").write_text("[]")
    _insufficient(root, seal, "sweep 6.9b")


def test_checkpoint_record_non_dict(world):
    root, seal = world
    bh.checkpoint_record_path_2h(root, 40000).write_text("[]")
    _insufficient(root, seal, "sweep 6.9b")


def test_step_record_is_a_directory(world):
    root, seal = world
    p = bh.record_path_2h(root, 40000, "antonym")
    p.unlink()
    p.mkdir()
    _insufficient(root, seal, "sweep record missing")


def test_sweep_dir_replaced_by_a_file(world):
    root, seal = world
    d = bh.sweep_dir_2h(root)
    shutil.rmtree(d)
    d.write_text("not a directory")
    _insufficient(root, seal, "gate 1 6.9b")


# ------------------------------------------- the primary's own refusals

def _rewrite_r69(root, fn):
    bat = bg.load_battery(list(bh.R_69))
    for step in bh.GRID_69:
        for r in bh.R_69:
            p = bh.record_path_2h(root, step, r)
            rec = json.loads(p.read_text())
            fn(rec, bat[r])
            rec["correct"] = sum(rec["bits"])
            p.write_text(json.dumps(rec))


def test_no_eligible_rung_is_a_terminal_not_a_crash(world):
    """Every R_69 rung thin (n_pos 0): `primary_2h` raises 'no eligible
    rung' — behind the freeze's refusal it is INSUFFICIENT_DATA."""
    root, seal = world

    def z(rec, cap):
        rec["continuations"] = [" zzz"] * len(rec["bits"])
        rec["bits"] = [0] * len(rec["bits"])
    _rewrite_r69(root, z)
    _insufficient(root, seal, "no eligible rung")


def test_no_informative_pair_is_a_terminal_not_a_crash(world):
    """y constant on every item of every rung: `perm_test` raises 'no
    informative pair' — likewise a terminal."""
    root, seal = world

    def one(rec, cap):
        rec["continuations"] = [f" {it['answer']}" for it in cap["eval_items"]]
        rec["bits"] = [1] * len(rec["bits"])
    _rewrite_r69(root, one)
    _insufficient(root, seal, "no informative pair")


# ------------------------------------------------------------- control

def test_untouched_world_still_confirms(world):
    root, seal = world
    v = _run(root, seal, n_perm=200, n_boot=20)
    assert v["verdict"] == "CONFIRMED", v["reason"]
    assert v["primary"]["stratified"]["T"] >= 0.10


# ------------------------------- the median split cannot reach the verdict

def test_median_split_touches_only_its_own_secondary(world, monkeypatch):
    """Attack-list item 1: `sampler_beyond_probe` buckets the probe's
    continuous scores at their per-rung MEDIAN (no natural zero cut,
    unlike the sampler's count) — a disclosed choice, not a frozen one.
    Replacing the bucketing with a constant changes THAT secondary and
    nothing else: not the verdict, not the primary, not the other
    secondaries."""
    root, seal = world
    base = _run(root, seal, n_perm=200, n_boot=20)
    monkeypatch.setattr(an, "_median_bucket", lambda scores: [0] * len(scores))
    other = _run(root, seal, n_perm=200, n_boot=20)

    assert other["verdict"] == base["verdict"] == "CONFIRMED"
    assert other["reason"] == base["reason"]
    assert json.dumps(other["primary"], sort_keys=True, default=str) == \
        json.dumps(base["primary"], sort_keys=True, default=str)
    changed = [k for k in base["secondaries"]
               if json.dumps(base["secondaries"][k], sort_keys=True, default=str) !=
               json.dumps(other["secondaries"][k], sort_keys=True, default=str)]
    assert changed == ["sampler_beyond_probe"], changed
