# experiments/exp4b/tests/test_full_shape_4b.py
"""World-terminal tests for `analyze_4b.run()` (Task 5 brief's Step
1, `test_full_shape_4b.py`; ambiguity resolution 6): "leads" (the
shared seed=11 world) turns out to pool only 7 eligible placebo rungs
-- below the design §4 feasibility floor (8) -- so it reaches
INSUFFICIENT_DATA via that floor with every one of gates 1-5 still
PASSING (a build finding, disclosed on the test itself and in
PROGRESS.md, not a defect); "follows" is the world that clears the
floor and reaches a non-INSUFFICIENT terminal with the full placebo
pipeline completed (`s1.arms` six entries, `p_cal` in [0, 1],
specifically NOT-DISTINGUISHABLE or MARGINAL -- T_4 near zero has
nowhere far above a flat-rung null to sit); "no_convergence" reaches
INSUFFICIENT_DATA (B-5) via a cheap hand-built `root4` (no synthetic
sweep needed -- `load_exp4_verdict_4b`'s own refusal fires first); a
truncated `sets/<rung>.npz` reaches INSUFFICIENT_DATA through the
totality collector, never a raise.

Per the brief's "keep the slow module to ONE world build plus cheap
copies": ONE genuinely new `stage="full"` build happens in THIS
module ("follows", module-scoped `_follows_world_4b`) -- "leads"
reuses `conftest.py`'s session-scoped `_leads_world_4b` fixture
(already paid for by `test_analyze_4b.py`'s own slow tests in the same
session), "no_convergence" needs no build at all, and the truncated-
npz case is a `shutil.copytree` of the shared leads world. Finding 3:
neither synthetic world's OWN noise lands `run()` in CALIBRATED or
MARGINAL ("leads" hits the feasibility floor first; "follows" lands at
p_cal=.99), so `placebo_4b.p_cal_4b` is monkeypatched to force each
boundary case on the SAME shared "follows" world -- no third build."""
from __future__ import annotations

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
    """See `test_analyze_4b.py`'s own copy: `blob_sha` must be
    `full_shape_4b.blob_sha_4b`, not a lambda returning `None`
    (`require_prereg_4b` fails unconditionally otherwise); `world=True`
    injects `expected_n_sim` at the world's own `n_sim=20`."""
    kw = dict(tag_exists=lambda t: True, blob_sha=fs4b.blob_sha_4b,
             referents_sha=False, imports_pinned=False, frozen_check=lambda: None)
    if world:
        from experiments.exp4.tests import full_shape as fs
        kw["expected_n_sim"] = fs.WORLD_POWER_N_SIM_4
    return kw


def _assert_full_completion(v, v4):
    """Every assertion a genuinely COMPLETED placebo pipeline must
    satisfy -- called only on a world that clears the design §4
    feasibility floor (see the "leads" test below for the world that
    does not)."""
    assert v["verdict"] != "INSUFFICIENT_DATA", v["reason"]
    assert v["verdict"] in an4b.battery_4b.WORLDS_4B, v["verdict"]
    assert 0.0 <= v["primary"]["p_cal"] <= 1.0
    assert v["primary"]["T4"] == v4["primary"]["T"]
    assert sorted(v["s1"]["arms"]["arms"]) == \
        sorted(["observed_lambda", "4.0", "6.0", "8.0", "12.0", "rms_lambda"])
    for name in ("s3", "s4", "s5", "s6", "s7", "s8"):
        assert v[name] is not None, name
    for n in ("1", "2", "3", "4", "5"):
        assert v["gates"][n]["pass"] is True, (n, v["gates"][n])
    assert v["placebo_record_sha256"] is not None
    assert v["power_ext_sha256"] is not None


@pytest.mark.slow
def test_leads_world_feasibility_floor(_leads_world_4b, tmp_path):
    """BUILD FINDING (Task 5, disclosed in PROGRESS.md): the shared
    seed=11 "leads" world (`conftest.py`'s `_leads_world_4b`) pools
    only 7 eligible placebo rungs across the four trajectories under
    the leave-one-out 2-SE eligibility bar -- below `MIN_PLACEBO_
    TOTAL_4B` (8) -- so exp4b's OWN design §4 feasibility floor fires
    on it, correctly, reaching INSUFFICIENT_DATA. This is the world's
    OWN synthetic-noise property (exp4's `full_shape.build_world` is
    frozen under `experiments/exp4/`, never edited here), not a defect
    in the floor or the gates: every one of gates 1-5 still PASSES
    cleanly (the machinery up to the placebo pipeline is exercised in
    full), and the pipeline correctly refuses to build a null out of
    too few placebo rungs rather than silently narrowing it. The
    genuinely completing world is "follows", below."""
    root4, v4 = _leads_world_4b
    assert v4["verdict"] not in ("INSUFFICIENT_DATA", "NO-CONVERGENCE"), v4["reason"]
    v = an4b.run(root4b=tmp_path / "4b", root4=root4, power_gate="full", **_run4b_kwargs())
    assert v["verdict"] == "INSUFFICIENT_DATA"
    assert "design §4 floor" in v["reason"], v["reason"]
    for n in ("1", "2", "3", "4", "5"):
        assert v["gates"][n]["pass"] is True, (n, v["gates"][n])
    # Task 5 review, finding 4: the feasibility block is now
    # UNCONDITIONAL -- reachable exactly on the path where `primary`
    # stays `None` (the floor fires before any calibration is
    # attempted), so this is the ONE terminal that actually exercises
    # `floor_ok is False` with real per-trajectory deficits attached.
    feas = v["feasibility"]
    assert feas["floor_ok"] is False, feas
    assert set(feas["per_traj"]) == set(battery_4.TRAJECTORIES_4)
    for traj, rec in feas["per_traj"].items():
        assert set(rec) == {"n_real", "n_eligible_placebo", "deficit"}, (traj, rec)
    out_v = battery_4.verdict_path(tmp_path / "4b")
    assert not out_v.exists()          # write=False (default)


# `_follows_world_4b` is now `conftest.py`'s own SESSION-scoped fixture
# (Task 6: promoted from this module's own module-scoped copy so
# `test_totality_4b.py`/`test_determinism_4b.py` can share the same
# ~11-13 minute `stage="full"` build rather than paying for their own --
# see conftest.py's docstring). Still shared read-only by the
# follows-terminal test and the two forced-p_cal tests below (finding
# 3) -- no second build, now session-wide rather than module-wide.


@pytest.mark.slow
def test_follows_world_reaches_not_distinguishable_or_marginal(_follows_world_4b, tmp_path):
    root4, v4 = _follows_world_4b
    assert v4["verdict"] == "FOLLOWS", v4["reason"]
    v = an4b.run(root4b=tmp_path / "4b", root4=root4, power_gate="full", **_run4b_kwargs())
    _assert_full_completion(v, v4)
    assert v["verdict"] in ("NOT-DISTINGUISHABLE", "MARGINAL"), v["verdict"]
    # Task 5 review, finding 4 (the completing side of the assertion
    # added to the "leads" floor test above): on a world that CLEARS
    # the floor, `feasibility`'s `per_traj` is the AUTHORITATIVE block
    # `draw_batteries_4b` itself used (run()'s own preference), not the
    # hand-rolled duplicate -- still present, still one entry per
    # trajectory.
    assert v["feasibility"]["per_traj"], v["feasibility"]
    assert set(v["feasibility"]["per_traj"]) == set(battery_4.TRAJECTORIES_4)
    print(f"\n    follows world -> exp4b verdict {v['verdict']} (p_cal={v['primary']['p_cal']})")


def _force_p_cal_4b(monkeypatch, forced):
    """Finding 3: no synthetic world's OWN noise lands `run()` in
    CALIBRATED or MARGINAL ("leads" hits the feasibility floor first;
    "follows" lands NOT-DISTINGUISHABLE on its own p_cal=.99) --
    `placebo_4b.p_cal_4b` is monkeypatched to force the boundary case
    while keeping `p_low`/`B` genuine (computed through the real
    function on the actual `T_b`/`T4`, only `p_cal` overridden). Every
    call site (the primary, `per_traj_4b`, `per_type_4b`, S7) sees the
    same forced value -- benign for what these tests check."""
    from experiments.exp4b import placebo_4b
    real_p_cal_4b = placebo_4b.p_cal_4b

    def fake(T_b, T4_arg):
        return {**real_p_cal_4b(T_b, T4_arg), "p_cal": forced}

    monkeypatch.setattr(placebo_4b, "p_cal_4b", fake)


@pytest.mark.slow
def test_follows_world_reaches_calibrated_when_p_cal_forced(_follows_world_4b, tmp_path, monkeypatch):
    root4, v4 = _follows_world_4b
    _force_p_cal_4b(monkeypatch, 0.005)
    v = an4b.run(root4b=tmp_path / "4b", root4=root4, power_gate="full", **_run4b_kwargs())
    assert v["verdict"] == "CALIBRATED", v["reason"]
    assert v["primary"]["p_cal"] == 0.005
    assert v["primary"]["p_low"] is not None and v["primary"]["B"] is not None   # genuine, not faked
    txt = an4b.write_verdict_txt_4b(v)
    assert "CALIBRATED" in txt
    # Task 5 review, finding 3's follow-on: forcing `p_cal` alone does
    # not touch anything else the pipeline computed -- the whole
    # completion contract (S1-S8, every gate, both sha256 records)
    # still holds on this terminal.
    _assert_full_completion(v, v4)


@pytest.mark.slow
def test_follows_world_reaches_marginal_when_p_cal_forced(_follows_world_4b, tmp_path, monkeypatch):
    root4, v4 = _follows_world_4b
    _force_p_cal_4b(monkeypatch, 0.03)
    v = an4b.run(root4b=tmp_path / "4b", root4=root4, power_gate="full", **_run4b_kwargs())
    assert v["verdict"] == "MARGINAL", v["reason"]
    assert v["primary"]["p_cal"] == 0.03
    assert v["primary"]["p_low"] is not None and v["primary"]["B"] is not None
    txt = an4b.write_verdict_txt_4b(v)
    assert "MARGINAL" in txt
    _assert_full_completion(v, v4)


def test_no_convergence_world_gives_insufficient_data(tmp_path):
    """B-5, cheap (ambiguity resolution 6): a hand-built `root4`
    carrying only a NO-CONVERGENCE `results/verdict.json` -- no
    synthetic sweep needed, since `load_exp4_verdict_4b`'s own refusal
    fires before any placebo machinery would run."""
    import json
    root4 = tmp_path / "no_convergence"
    battery_4.verdict_path(root4).parent.mkdir(parents=True, exist_ok=True)
    battery_4.verdict_path(root4).write_text(json.dumps(
        {"verdict": "NO-CONVERGENCE", "reason": "1 eligible cell on 1 rung (need 3/3)"}))
    v = an4b.run(root4b=tmp_path / "4b", root4=root4, power_gate="full",
                **_run4b_kwargs(world=False))
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert "carries no primary" in v["reason"]


@pytest.mark.slow
def test_truncated_set_table_gives_insufficient_data_not_a_raise(_leads_world_4b, tmp_path):
    root4, v4 = _leads_world_4b
    world = fresh_copy_4b(root4, tmp_path)
    # Truncate one flat rung's set table at a non-endpoint grid step of
    # the shortest trajectory (pythia_2.8b) -- read by gate (1)'s
    # `alignment_series_4` re-derivation over every grid step.
    traj = "pythia_2.8b"
    step = battery_4.GRID_4[traj][1]
    p = battery_4.unit_dir(world, traj, step) / "sets" / f"{v4['rung_sets'][traj]['flat'][0]}.npz"
    data = p.read_bytes()
    p.write_bytes(data[: len(data) // 2])
    v = an4b.run(root4b=tmp_path / "4b", root4=world, power_gate="full", **_run4b_kwargs())
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
