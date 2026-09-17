# experiments/exp4b/tests/test_analyze_4b.py
"""Tests for `analyze_4b.py` (Task 5, design §3.6/§3.7): the tree as a
pure function of `p_cal`; `write_verdict_txt_4b`'s caveat + world;
totality on a missing/malformed `root4` (fast, no world needed) --
`load_exp4_verdict_4b`'s B-5 refusal reads "carries no primary" and
strict-JSON-serializability of the return value; `stop_before=
"placebo"` on the shared synthetic LEADS world returns INSUFFICIENT_
DATA with every one of gates 1-5 present and PASSING; each gate fails
and is collected when ITS OWN committed input is perturbed (T_4,
lambda_hat, an eligibility `se`, a `power_4.json` byte), on fresh
`shutil.copytree` copies of the SAME shared world -- `conftest.py`'s
`_leads_world_4b` fixture pays the one expensive `stage="full"` sweep
(~11-13 minutes) ONCE per session."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments.exp4 import battery_4  # noqa: E402
from experiments.exp4b import analyze_4b as an4b  # noqa: E402
from experiments.exp4b.tests import full_shape_4b as fs4b  # noqa: E402
from experiments.exp4b.tests.conftest import fresh_copy_4b  # noqa: E402


def _run4b_kwargs(*, world=True):
    """`blob_sha` must be `full_shape_4b.blob_sha_4b` (the "tag-bound"
    sha IS the file's own sha) -- a lambda returning `None` makes
    `require_prereg_4b`'s equality check fail unconditionally, masked
    on a root4 that already fails for other reasons but fatal on a
    clean world (caught running the slow tests below). `world=True`
    also injects `expected_n_sim` at the world's own `n_sim=20` (a
    world's `power_4.json` is never written at the real campaign's
    1000)."""
    kw = dict(tag_exists=lambda t: True, blob_sha=fs4b.blob_sha_4b,
             referents_sha=False, imports_pinned=False, frozen_check=lambda: None)
    if world:
        from experiments.exp4.tests import full_shape as fs
        kw["expected_n_sim"] = fs.WORLD_POWER_N_SIM_4
    return kw


# ------------------------------------------------------------- the tree

@pytest.mark.parametrize("p_cal,want", [
    (0.001, "CALIBRATED"),
    (0.0099, "CALIBRATED"),
    (0.03, "MARGINAL"),
    (0.0499, "MARGINAL"),
    (0.2, "NOT-DISTINGUISHABLE"),
    (1.0, "NOT-DISTINGUISHABLE"),
])
def test_tree_p_cal_levels(p_cal, want):
    v = an4b.verdict_tree_4b([], True, p_cal)
    assert v["verdict"] == want, v


def test_tree_failures_win_over_feasibility_and_p_cal():
    v = an4b.verdict_tree_4b(["x"], True, 0.001)
    assert v["verdict"] == "INSUFFICIENT_DATA"
    assert v["reason"] == "x"


def test_tree_infeasible_placebo_pool_gives_insufficient_data():
    v = an4b.verdict_tree_4b([], False, 0.001)
    assert v["verdict"] == "INSUFFICIENT_DATA"
    assert "design §4 floor" in v["reason"]


# --------------------------------------------------------- verdict text

def test_write_verdict_txt_4b_contains_caveat_and_world():
    tree = {"verdict": "CALIBRATED", "reason": "p_cal 0.001 < 0.01"}
    gates = {n: {"pass": True} for n in ("1", "2", "3", "4", "5")}
    v = an4b.verdict_4b(tree=tree, gates=gates, exp4_block={"verdict": "LEADS", "T": 0.61},
                        pins_active={})
    txt = an4b.write_verdict_txt_4b(v)
    assert an4b.KNOWN_INPUT_CAVEAT_4B in txt
    assert "CALIBRATED" in txt


# --------------------------------------------------- totality, no world

def test_run_on_empty_root4_gives_insufficient_data_and_is_json_serializable(tmp_path):
    root4b = tmp_path / "4b"
    root4 = tmp_path / "4"          # never created -- verdict.json etc. all missing
    v = an4b.run(root4b=root4b, root4=root4, **_run4b_kwargs(world=False))
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    raw = json.dumps(v, allow_nan=False)
    reparsed = json.loads(raw)
    assert reparsed["verdict"] == v["verdict"]
    for n in ("1", "2", "3", "4", "5"):
        assert n in v["gates"]


def test_run_no_convergence_verdict_gives_insufficient_data_carries_no_primary(tmp_path):
    """B-5, cheap: a hand-built `root4` carrying only a NO-CONVERGENCE
    `results/verdict.json` (`load_exp4_verdict_4b`'s own refusal fires
    well before any expensive machinery would run -- no synthetic
    sweep needed to exercise this refusal)."""
    root4 = tmp_path / "4"
    battery_4.verdict_path(root4).parent.mkdir(parents=True, exist_ok=True)
    battery_4.verdict_path(root4).write_text(json.dumps(
        {"verdict": "NO-CONVERGENCE", "reason": "2 eligible cells on 2 rungs (need 3/3)"}))
    v = an4b.run(root4b=tmp_path / "4b", root4=root4, **_run4b_kwargs(world=False))
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert "carries no primary" in v["reason"]


def test_power_gate_must_be_full_or_skip(tmp_path):
    with pytest.raises(ValueError, match="power_gate"):
        an4b.run(root4b=tmp_path / "4b", root4=tmp_path / "4", power_gate="bogus",
                **_run4b_kwargs())


# --------------------------------------------------------- gates, a world

@pytest.mark.slow
def test_stop_before_placebo_gives_insufficient_data_with_every_gate_passing(_leads_world_4b, tmp_path):
    root4, v4 = _leads_world_4b
    root4b = tmp_path / "4b"
    v = an4b.run(root4b=root4b, root4=root4, stop_before="placebo", power_gate="full",
                **_run4b_kwargs())
    assert v["verdict"] == "INSUFFICIENT_DATA"
    assert v["reason"] == "4b: stopped before the placebo null (pre-tag tool run)"
    for n in ("1", "2", "3", "4", "5"):
        g = v["gates"].get(n)
        assert g is not None and g["pass"] is True, (n, g)
    # nothing placebo-side was ever computed
    assert v["primary"] is None
    assert v["placebo_record_sha256"] is None
    assert v["power_ext_sha256"] is None
    raw = json.dumps(v, allow_nan=False)
    json.loads(raw)


@pytest.mark.slow
def test_gate1_fails_when_t4_is_perturbed(_leads_world_4b, tmp_path):
    root4, v4 = _leads_world_4b
    world = fresh_copy_4b(root4, tmp_path)
    vp = battery_4.verdict_path(world)
    rec = json.loads(vp.read_text())
    rec["primary"]["T"] = rec["primary"]["T"] + 0.123456
    vp.write_text(json.dumps(rec))
    v = an4b.run(root4b=tmp_path / "4b", root4=world, stop_before="placebo",
                **_run4b_kwargs())
    assert v["gates"]["1"]["pass"] is False
    assert v["gates"]["2"]["pass"] is True
    assert v["gates"]["3"]["pass"] is True
    assert v["gates"]["5"]["pass"] is True
    # `stop_before="placebo"` always returns its own fixed reason,
    # regardless of any gate failure already collected -- the true
    # per-gate verdict lives in `v["gates"]`, already asserted above.
    assert v["verdict"] == "INSUFFICIENT_DATA"
    assert v["reason"] == "4b: stopped before the placebo null (pre-tag tool run)"


@pytest.mark.slow
def test_gate3_fails_when_lambda_hat_is_perturbed(_leads_world_4b, tmp_path):
    root4, v4 = _leads_world_4b
    world = fresh_copy_4b(root4, tmp_path)
    vp = battery_4.verdict_path(world)
    rec = json.loads(vp.read_text())
    traj = next(iter(rec["calibration"]["per_traj"]))
    rec["calibration"]["per_traj"][traj]["lambda_hat"] += 1.0
    vp.write_text(json.dumps(rec))
    v = an4b.run(root4b=tmp_path / "4b", root4=world, stop_before="placebo",
                **_run4b_kwargs())
    assert v["gates"]["3"]["pass"] is False
    assert v["gates"]["1"]["pass"] is True
    assert v["verdict"] == "INSUFFICIENT_DATA"
    assert v["reason"] == "4b: stopped before the placebo null (pre-tag tool run)"


@pytest.mark.slow
def test_gate2_fails_when_an_eligibility_se_is_perturbed(_leads_world_4b, tmp_path):
    root4, v4 = _leads_world_4b
    world = fresh_copy_4b(root4, tmp_path)
    ep = battery_4.eligibility_path(world)
    rec = json.loads(ep.read_text())
    traj = next(t for t, block in rec.items() if block.get("R"))
    rung = next(iter(rec[traj]["R"]))
    rec[traj]["R"][rung]["se"] = rec[traj]["R"][rung]["se"] + 1.0
    ep.write_text(json.dumps(rec))
    v = an4b.run(root4b=tmp_path / "4b", root4=world, stop_before="placebo",
                **_run4b_kwargs())
    assert v["gates"]["2"]["pass"] is False
    assert v["verdict"] == "INSUFFICIENT_DATA"
    assert v["reason"] == "4b: stopped before the placebo null (pre-tag tool run)"


@pytest.mark.slow
def test_gate4_fails_when_a_power_record_byte_is_flipped(_leads_world_4b, tmp_path):
    root4, v4 = _leads_world_4b
    world = fresh_copy_4b(root4, tmp_path)
    pp = battery_4.power_path(world)
    rec = json.loads(pp.read_text())
    rec["eligibility_sha256"] = ("f" if rec["eligibility_sha256"][0] != "f" else "0") \
        + rec["eligibility_sha256"][1:]
    pp.write_text(json.dumps(rec, indent=1))
    v = an4b.run(root4b=tmp_path / "4b", root4=world, stop_before="placebo",
                power_gate="full", **_run4b_kwargs())
    assert v["gates"]["4"]["pass"] is False
    assert v["gates"]["4"]["identical"] is False
    assert v["verdict"] == "INSUFFICIENT_DATA"
    assert v["reason"] == "4b: stopped before the placebo null (pre-tag tool run)"


@pytest.mark.slow
def test_power_gate_skip_is_disclosed_in_pins_active(_leads_world_4b, tmp_path):
    root4, v4 = _leads_world_4b
    v = an4b.run(root4b=tmp_path / "4b", root4=root4, stop_before="placebo",
                power_gate="skip", **_run4b_kwargs())
    assert v["gates"]["4"] == {"pass": True, "skipped": True}
    assert v["pins_active"]["power_gate_skipped"] is True
