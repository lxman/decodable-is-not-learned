# experiments/exp2j/tests/test_totality_2j.py
"""Verdict-path totality (2h's F-1 lesson, carried forward through 2i to
2j): every tree `analyze_2j.run()` can be handed — the upstream 2i-tree
shapes 2i's own totality already proved reach a terminal through ITS
loaders, reached here through 2j's `run()` instead; PLUS the shapes new
to 2j's own readers (the power record, the three comparison verdict.json
files, 2i's F-1 attested-vs-re-derived check one file type over) — must
reach a FROZEN TERMINAL (INSUFFICIENT_DATA), never an uncaught
exception. Each case below RAISES before `collect_total`'s closure if
it is stripped; the control proves the same harness still reaches
RESIDUAL on an untouched world.

2i's own totality module already proved the FULL battery of these
shapes against 2i's loaders directly (missing/torn/directory/mutated-
field variants for every record kind); this file does not repeat that
sweep. It proves the ONE thing 2i's totality cannot: that 2j's `run()`
routes the SAME upstream failures — reached this time through 2i's
loaders CALLED FROM 2j — to the same terminal, one representative shape
per upstream site, plus every shape genuinely new to 2j's own readers."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from experiments.exp2g import battery_2g as bg
from experiments.exp2i import analyze_2i as an2i
from experiments.exp2i import battery_2i as bi
from experiments.exp2j import analyze_2j as an
from experiments.exp2j.tests import full_shape as fs


@pytest.fixture(scope="module")
def base_world(tmp_path_factory):
    root = tmp_path_factory.mktemp("totality_base")
    seal = fs.write_world_2j(root, world="residual")
    return root, seal


@pytest.fixture
def world(base_world, tmp_path):
    root, seal = base_world
    shutil.copytree(root / "results", tmp_path / "results")
    return tmp_path, seal


def _run(root, seal, **kw):
    kw.setdefault("n_perm", 30)
    kw.setdefault("n_boot", 10)
    # the seal's own `verdict_2i_path` is an ABSOLUTE path baked in at
    # `base_world` build time (`root / "results" / "verdict.json"` for
    # the ORIGINAL base root) — every per-test `world` fixture copies
    # `results/` into a FRESH `tmp_path`, so a test that edits the copy's
    # verdict.json must also redirect this kwarg to the copy, or `run()`
    # silently re-reads the untouched original. Defaulted here so every
    # test in this file gets the copy by construction.
    kw.setdefault("verdict_2i_path", Path(root) / "results" / "verdict.json")
    return an.run(root_2i=root, root_2j=root, referents_sha=False,
                  **{**seal, **kw})


def _insufficient(root, seal, needle):
    v = _run(root, seal)
    assert v["verdict"] == "INSUFFICIENT_DATA", v["verdict"]
    assert needle in v["reason"], v["reason"]
    assert v["primary"] is None and v["secondaries"] is None and v["a1"] is None
    return v


# ---------------------------------------------------- 2i-tree shapes,
# ---------------------------------------------------- reached through 2j

def test_predictor_seal_missing(world):
    root, seal = world
    bi.predictor_seal_path(root).unlink()
    _insufficient(root, seal, "predictor seal content")


@pytest.mark.parametrize("payload", ["[]", '"x"', '{"sha256": "a", "tag": "t"'])
def test_predictor_seal_non_dict_or_torn(world, payload):
    root, seal = world
    bi.predictor_seal_path(root).write_text(payload)
    _insufficient(root, seal, "predictor seal content")


def test_predictor_seal_is_a_directory(world):
    root, seal = world
    p = bi.predictor_seal_path(root)
    p.unlink()
    p.mkdir()
    _insufficient(root, seal, "predictor seal content")


def test_truncated_x_b_draws_gz_is_insufficient_data_not_a_raise(world):
    """freeze F-2's lesson (2i), reached through 2j's own collect_total
    (`= an2i.collect_total`, the same widened wrapper): a truncated gzip
    draws stream raises `EOFError`, not `OSError`/`ValueError` — a
    terminal, not a crash."""
    root, seal = world
    p = bi.predictor_draws_path(root, "antonym")
    b = p.read_bytes()
    p.write_bytes(b[:int(len(b) * 0.5)])
    v = _insufficient(root, seal, "x_B counts olmo1b")
    assert any("EOFError" in f for f in v["referents"]["failures"])


def test_sweep_record_torn(world):
    root, seal = world
    bi.record_path(root, bi.GRID_7B[0], "antonym").write_text('{"rung": "a')
    _insufficient(root, seal, "2i sweep olmo7b")


def test_rung_set_missing_r_cap(world):
    root, seal = world
    p = bi.rung_set_path(root)
    rec = json.loads(p.read_text())
    del rec["R_CAP"]
    p.write_text(json.dumps(rec))
    _insufficient(root, seal, "2i rung set file")


# ----------------------------------------------------------- 2j-only shapes

@pytest.mark.parametrize("payload", ['{"primary": {', "[]"])
def test_power_2j_torn_or_not_a_dict(world, payload):
    root, seal = world
    (root / "results" / "power_2j.json").write_text(payload)
    _insufficient(root, seal, "power record")


def test_power_2j_wrong_rungs(world):
    root, seal = world
    p = root / "results" / "power_2j.json"
    rec = json.loads(p.read_text())
    rec["primary"] = dict(rec["primary"])
    rec["primary"]["rungs"] = ["clock24"]
    p.write_text(json.dumps(rec))
    _insufficient(root, seal, "power record")


def test_power_2j_unknown_declared_status(world):
    root, seal = world
    p = root / "results" / "power_2j.json"
    rec = json.loads(p.read_text())
    rec["primary"] = dict(rec["primary"])
    rec["primary"]["declared_status"] = "MAYBE"
    p.write_text(json.dumps(rec))
    _insufficient(root, seal, "power record")


def test_2i_verdict_torn(world):
    root, seal = world
    (root / "results" / "verdict.json").write_text('{"tests": {')
    _insufficient(root, seal, "comparison gate re-derivation")


def test_2i_verdict_missing_secondaries(world):
    root, seal = world
    p = root / "results" / "verdict.json"
    rec = json.loads(p.read_text())
    del rec["secondaries"]
    p.write_text(json.dumps(rec))
    _insufficient(root, seal, "comparison gate re-derivation")


def test_2i_verdict_reverse_direction_missing_vs_6_9b(world):
    root, seal = world
    p = root / "results" / "verdict.json"
    rec = json.loads(p.read_text())
    rec["secondaries"] = dict(rec["secondaries"])
    rec["secondaries"]["reverse_direction"] = {
        k: v for k, v in rec["secondaries"]["reverse_direction"].items() if k != "vs_6.9b"}
    p.write_text(json.dumps(rec))
    _insufficient(root, seal, "comparison gate re-derivation")


def _fake_exp2g_with_torn_verdict(tmp_path) -> Path:
    """A directory that answers exactly like `bg.EXP2G` for every file
    2j's `run()` reads through it (symlinked, not copied — the real
    tree is ~2.3 GB) EXCEPT `results/verdict.json`, which is torn. This
    isolates the ONE read the shape targets; a bare empty stand-in for
    `bg.EXP2G` makes an EARLIER `bg.EXP2G`-rooted load (the strata
    predictor, the 2.8b pythia-outcome sweep) fail first instead,
    proven directly against this tree before writing the assertion
    below (see the Task 3 report)."""
    real = bg.EXP2G
    fake = tmp_path / "fake_exp2g"
    fake.mkdir()
    for entry in real.iterdir():
        if entry.name != "results":
            (fake / entry.name).symlink_to(entry)
    fake_results = fake / "results"
    fake_results.mkdir()
    for entry in (real / "results").iterdir():
        if entry.name != "verdict.json":
            (fake_results / entry.name).symlink_to(entry)
    (fake_results / "verdict.json").write_text('{"tests": {')
    return fake


def test_2g_verdict_torn(world, monkeypatch, tmp_path_factory):
    root, seal = world
    fake_dir = tmp_path_factory.mktemp("fake_exp2g_parent")
    monkeypatch.setattr(bg, "EXP2G", _fake_exp2g_with_torn_verdict(fake_dir))
    _insufficient(root, seal, "comparison gate re-derivation")


def test_x_b_draws_record_attested_tally_disagrees_with_the_draws(world):
    """2i's F-1 check (the predictor stage's own attested vs re-derived
    tally), reached through 2j's `run()`: the per-rung record's
    `per_seed_tallies` is mutated while the draws (and x_B re-derived
    from them) are untouched — caught by `an2i._check_predictor_counts_2i`
    under 2j's own label."""
    root, seal = world
    p = bi.predictor_record_path(root, "antonym")
    rec = json.loads(p.read_text())
    rec["per_seed_tallies"] = dict(rec["per_seed_tallies"])
    rec["per_seed_tallies"]["0"] = dict(rec["per_seed_tallies"]["0"])
    rec["per_seed_tallies"]["0"]["full_string"] += 1
    p.write_text(json.dumps(rec))
    _insufficient(root, seal, "attested full_string")


# ---------------------------- downstream consistency-check refusal paths
# (fix round 1 / Finding 1): every one of these seven collect_total
# sites is only reached once predictor_rec/predictor_records/rung_set/
# stage1_final/sweep have ALL already succeeded — exactly what the
# clean `world` fixture already is (the same technique
# `test_2i_verdict_torn`'s family uses to kill mutant #57, `_cmp`, one
# guard level over): monkeypatch the site's own callee to raise and
# check the run still reaches INSUFFICIENT_DATA under the site's own
# label, or — for the closing secondaries loop, which does NOT flip
# the overall verdict — that the one affected secondary carries a
# `{"failed": …}` shape while the verdict is still delivered.

def _raise_injected(*a, **kw):
    raise ValueError("injected for a Task 4 fix-round-1 totality mutation test")


def test_predictor_seal_sampling_check_failure(world, monkeypatch):
    root, seal = world
    monkeypatch.setattr(an2i, "_check_predictor_seal_sampling", _raise_injected)
    _insufficient(root, seal, "2i predictor seal sampling block")


def test_rung_set_vs_endpoint_check_failure(world, monkeypatch):
    root, seal = world
    monkeypatch.setattr(an2i, "_check_rung_set_vs_endpoint", _raise_injected)
    _insufficient(root, seal, "2i rung set vs endpoint")


def test_rung_set_derivation_check_failure(world, monkeypatch):
    root, seal = world
    monkeypatch.setattr(an2i, "_check_rung_set_derivation", _raise_injected)
    _insufficient(root, seal, "2i rung set re-derivation")


def test_predictor_counts_check_failure(world, monkeypatch):
    root, seal = world
    monkeypatch.setattr(an2i, "_check_predictor_counts_2i", _raise_injected)
    _insufficient(root, seal, "x_B counts vs the sealed attestation")


def test_outcomes_7b_load_failure(world, monkeypatch):
    root, seal = world
    monkeypatch.setattr(an2i, "outcomes_7b", _raise_injected)
    _insufficient(root, seal, "outcome olmo7b")


def test_core_primary_computation_failure(world, monkeypatch):
    root, seal = world
    monkeypatch.setattr(an, "primary_2j", _raise_injected)
    _insufficient(root, seal, "primary A-2")


def test_secondaries_thunk_catches_a_forced_decomposition_failure(world, monkeypatch):
    """Unlike the six refusal tests above, a secondary's own failure
    does NOT flip the overall verdict to INSUFFICIENT_DATA — `_sec`
    catches it locally (`sec[name] = {"failed": f[0]}`) and the
    primary alone still decides RESIDUAL/ABSORBED. This is exactly
    what distinguishes the un-mutated code (a graceful `{"failed":
    …}`) from the totality-strip mutant on `_sec`'s own
    `collect_total(thunk, name)` call, which would let the injected
    exception propagate UNCAUGHT and crash `an.run()` outright — a
    test error, not a clean assertion failure, but still a kill."""
    root, seal = world
    monkeypatch.setattr(an, "decomposition", _raise_injected)
    v = _run(root, seal, n_perm=200, n_boot=20)
    assert v["verdict"] == "RESIDUAL", v["reason"]
    assert v["secondaries"]["decomposition x_B to olmo7b"]["failed"]


# ------------------------------------------------------------- control

def test_untouched_world_still_reaches_residual(world):
    """n_perm=30's permutation p-value floor (1/31 ~ .032) can never
    clear ALPHA (.01, `fires_2i` requires p < ALPHA) regardless of T —
    2i's own control test hits the same floor and raises n_perm for
    exactly this reason. Every refusal test above stays at the file's
    30/10 default (only the routing to INSUFFICIENT_DATA is at stake,
    which n_perm cannot affect); only the control needs resolution
    enough to actually fire."""
    root, seal = world
    v = _run(root, seal, n_perm=200, n_boot=20)
    assert v["verdict"] == "RESIDUAL", v["reason"]
    assert v["primary"]["fires"] is True
