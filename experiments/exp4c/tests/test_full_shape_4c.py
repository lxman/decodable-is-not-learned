# experiments/exp4c/tests/test_full_shape_4c.py
"""World-terminal tests for `analyze_4c.run()` (Task 4 brief, step 2):
every terminal and every modifier cell reached through the production
path, every refusal route delivered as INSUFFICIENT_DATA rather than
raised, and the verdict strict-JSON-able.

Every world is built by `full_shape_4c.build_world`, which writes
through the production persistence from synthetic activations — no
torch, no network, no model contact. The grids are the REAL
`GRID_4C`: `run()`'s "4c checkpoint manifests" gate compares the live
grid against 2h's and 2l's committed manifests with no injection
point, so a shrunk grid would fail that gate before any later one
(Exp 4's own precedent). One `replicates` build is shared, via
`copy_world`, by the refusal-route tests, the MARGINAL test, the
TYPE-GENERAL test and the determinism fixture."""
from __future__ import annotations

import json

import pytest

from experiments.exp4c import analyze_4c as an
from experiments.exp4c import battery_4c as bc
from experiments.exp4c import rank_4c as rk
from experiments.exp4c.tests import full_shape_4c as fs4c

pytestmark = pytest.mark.slow

WORLD_SEED_4C = 0


@pytest.fixture(autouse=True)
def _blobs_that_exist(monkeypatch):
    monkeypatch.setattr(bc, "INSTRUMENT_BLOBS_4C", fs4c.existing_instrument_blobs_4c())


def _build(tmp_path_factory, mode, seed=WORLD_SEED_4C):
    root = tmp_path_factory.mktemp(f"world_{mode}")
    return fs4c.build_world(root / "root4c", root / "root4", mode, seed=seed)


@pytest.fixture(scope="module")
def replicates_world(tmp_path_factory):
    """The one shared build. `type_general` is the SAME construction by
    the brief's own definition (both put every rising rung's task
    signal up before t-), so it is tested on this world rather than
    rebuilt."""
    return _build(tmp_path_factory, "replicates")


@pytest.fixture(scope="module")
def not_replicated_world(tmp_path_factory):
    return _build(tmp_path_factory, "not_replicated")


@pytest.fixture(scope="module")
def reversed_world(tmp_path_factory):
    return _build(tmp_path_factory, "reversed")


@pytest.fixture(scope="module")
def type_bound_world(tmp_path_factory):
    return _build(tmp_path_factory, "type_bound")


def _needle_in_failures(v, needle):
    text = " ".join(v.get("failures") or []) + " " + (v.get("reason") or "")
    return needle.lower() in text.lower()


# ---------------------------------------------------------------- terminals

def test_replicates_world_reaches_replicates(replicates_world):
    v = fs4c.run_world(replicates_world)
    assert v["verdict"] == "REPLICATES", v["reason"]
    assert v["primary"]["U"] > 0.75
    assert v["primary"]["n_cells"] == 26
    assert v["primary"]["n_families"] == 9
    assert v["modifier"]["modifier"] in ("TYPE-GENERAL", "TYPE-BOUND")
    for name in ("S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8", "S9", "S10"):
        assert name in v["secondaries"], name
        entry = v["secondaries"][name]
        assert not (isinstance(entry, dict) and "failed" in entry), (name, entry)
    assert v["licence"]["sentence"].startswith("on two training runs nobody had read")
    assert f"{an.KNOWN_OUTCOME_CAVEAT_4C} {an.NOT_A_FORECAST_4C}" in v["licence"]["sentence"]
    # S8 (design §5): the per-reference series over the grid, per rung —
    # not a level
    s8 = v["secondaries"]["S8"]["per_traj"]
    for traj, block in s8.items():
        steps = list(bc.GRID_4C[traj])
        assert block["steps"] == steps
        assert set(block["a_by_ref"]) == set(bc.REFS_FOR_4C[traj])
        for ref, by_rung in block["a_by_ref"].items():
            assert set(by_rung) == set(bc.RUNGS)
            assert all(len(vals) == len(steps) for vals in by_rung.values())
        assert set(block["a_by_ref_endpoint_mean"]) == set(bc.REFS_FOR_4C[traj])
    # the world reaches REPLICATES for the RIGHT reason: every cell's
    # pre-clear growth is ahead of its own run's flat pool
    assert all(c["q"] > 0.5 for c in v["primary"]["cells"])
    for traj in bc.TRAJECTORIES_4C:
        assert v["gate0"][traj]["pass"] is True, (traj, v["gate0"][traj])
        assert v["gate1"][traj]["digest_equal"] is True
        assert all(v["gate1"][traj]["sets_equal"].values())


def test_type_general_world(replicates_world):
    v = fs4c.run_world(replicates_world)
    assert v["modifier"]["modifier"] == "TYPE-GENERAL"
    assert v["modifier"]["arith"]["p_plus"] < rk.MARGINAL_4C


def test_not_replicated_world(not_replicated_world):
    v = fs4c.run_world(not_replicated_world)
    assert v["verdict"] == "NOT-REPLICATED", v["reason"]
    assert v["tree"]["reversed"] is False
    assert v["primary"]["p_plus"] >= rk.MARGINAL_4C


def test_reversed_world(reversed_world):
    v = fs4c.run_world(reversed_world)
    assert v["verdict"] == "NOT-REPLICATED", v["reason"]
    assert v["tree"]["reversed"] is True
    assert v["primary"]["p_minus"] < rk.MARGINAL_4C
    # reversed for the right reason: the rising tasks' pre-clear growth
    # sits below the never-performing tasks'
    assert v["primary"]["U"] < 0.5
    assert v["licence"]["reversed"] is True
    assert "sat below" in v["licence"]["sentence"]


def test_type_bound_world(type_bound_world):
    v = fs4c.run_world(type_bound_world)
    assert v["modifier"]["modifier"] == "TYPE-BOUND", v["modifier"]
    assert v["modifier"]["nonarith"]["p_family"] is None
    assert v["modifier"]["nonarith"]["p_family_reason"]
    assert v["modifier"]["nonarith"]["U"] > 0.5
    assert v["modifier"]["arith"]["p_plus"] >= rk.MARGINAL_4C
    assert v["modifier"]["nonarith"]["p_placebo_nonarith"] is not None
    assert an.MODIFIER_NOUN_4C["TYPE-BOUND"] in v["licence"]["sentence"]


def test_marginal_terminal_is_reachable_by_the_tree(replicates_world, monkeypatch):
    """The MARGINAL cell, reached through the production path: with
    alpha driven below the flip's own resolution, the REPLICATES world's
    p+ lands in [alpha, .05)."""
    monkeypatch.setattr(rk, "ALPHA_4C", 1e-9)
    v = fs4c.run_world(replicates_world)
    assert v["verdict"] == "MARGINAL", v["reason"]
    assert v["licence"]["world"] == "MARGINAL"
    assert v["tree"]["reversed"] is False


# ------------------------------------------------------------- refusals

@pytest.mark.parametrize("route", fs4c.MISSING_ROUTES_4C)
def test_every_refusal_route_lands_insufficient(route, replicates_world, tmp_path):
    w = fs4c.copy_world(replicates_world, tmp_path)
    needle = fs4c.apply_missing_4c(w, route)
    v = fs4c.run_world(w)
    assert v["verdict"] == "INSUFFICIENT_DATA", (route, v["reason"])
    assert _needle_in_failures(v, needle), (route, v["failures"])
    assert v["licence"]["sentence"].startswith("no licence")


def test_a_failing_exit_import_pin_reaches_the_verdict(replicates_world, tmp_path, monkeypatch):
    """I-1: the tree is computed AFTER the exit import check. A pin that
    passes at entry and fails at exit (a secondary imported something
    the entry check never saw — 2j F-1's own shape) must turn the
    verdict INSUFFICIENT_DATA, not sit in `failures` beside a
    REPLICATES."""
    w = fs4c.copy_world(replicates_world, tmp_path)
    calls = {"n": 0}

    def flaky_check():
        calls["n"] += 1
        if calls["n"] >= 2:
            raise RuntimeError("unpinned module on the import surface: synthetic")

    monkeypatch.setattr(an, "check_imports_4c", flaky_check)
    v = fs4c.run_world(w, imports_pinned=True)
    assert calls["n"] == 2, calls
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert _needle_in_failures(v, "import surface (exit)")
    assert v["pins_active"]["import_surface"] is True
    assert v["calibration"] is None
    assert v["licence"]["sentence"].startswith("no licence")


def test_a_torn_gate1_record_is_collected_not_raised(replicates_world, tmp_path):
    from experiments.exp4 import battery_4
    w = fs4c.copy_world(replicates_world, tmp_path)
    battery_4.gate1_path(w["root4c"], "pythia_6.9b").write_text(json.dumps([1, 2, 3]))
    v = fs4c.run_world(w)
    assert v["verdict"] == "INSUFFICIENT_DATA"


def test_a_power_record_with_the_wrong_n_sim_refuses(replicates_world, tmp_path):
    w = fs4c.copy_world(replicates_world, tmp_path)
    p = w["root4c"] / "results" / "power_4c.json"
    rec = json.loads(p.read_text())
    rec["n_sim"] = rec["n_sim"] + 1
    p.write_text(json.dumps(rec))
    v = fs4c.run_world(w)
    assert v["verdict"] == "INSUFFICIENT_DATA"
    assert _needle_in_failures(v, "n_sim")


def test_a_discovery_record_off_its_pin_refuses(replicates_world, tmp_path):
    w = fs4c.copy_world(replicates_world, tmp_path)

    def bad_discovery(root4=None):
        rec = fs4c.discovery_stub_4c(root4)
        rec["U"] = rec["U"] + 1e-9
        return rec
    v = fs4c.run_world(w, discovery_check=bad_discovery)
    assert v["verdict"] == "INSUFFICIENT_DATA"
    assert _needle_in_failures(v, "discovery gate")


# ---------------------------------------------------------------- record

def test_verdict_json_is_strict(replicates_world, tmp_path):
    from experiments.exp4 import battery_4
    w = fs4c.copy_world(replicates_world, tmp_path)
    v = fs4c.run_world(w, write=True)
    json.dumps(v, allow_nan=False)
    on_disk = json.loads(battery_4.verdict_path(w["root4c"]).read_text())
    assert on_disk["verdict"] == v["verdict"]
    txt = battery_4.verdict_txt_path(w["root4c"]).read_text()
    assert "EXPERIMENT 4c VERDICT" in txt
    assert "Type modifier" in txt and "Licence:" in txt and "Pins active" in txt
    # the two B-element placebo arrays are summarized, never carried
    assert "U_b" not in json.dumps(v["placebo"])


# ------------------------------------------- FREEZE F-4: the cache key

def test_world_input_modules_match_the_mutation_harnesss_world_writing_set():
    """FREEZE F-4: the cache key and the mutation harness's own
    cache-bypass list are the same four modules, or one of them is
    wrong."""
    from experiments.exp4c.tests import mutation_check as mc
    assert {str(p) for p in fs4c.WORLD_INPUT_MODULES_4C} == set(mc.WORLD_WRITING_PATHS_4C)


def test_the_cache_key_moves_when_a_world_writing_module_moves(tmp_path, monkeypatch):
    """FREEZE F-4: an edit to any world-writing module is a cache MISS,
    not a stale hit."""
    before = fs4c.world_inputs_digest_4c()
    assert before == fs4c.world_inputs_digest_4c()
    fake = tmp_path / "battery_4c.py"
    fake.write_text("# a different battery_4c\n")
    monkeypatch.setattr(fs4c, "WORLD_INPUT_MODULES_4C",
                        (fake,) + fs4c.WORLD_INPUT_MODULES_4C[1:])
    assert fs4c.world_inputs_digest_4c() != before


def test_the_cache_key_is_not_only_mode_and_seed():
    d = fs4c.world_inputs_digest_4c()
    assert len(d) == 12 and d.isalnum()
