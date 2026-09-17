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

from experiments.exp4 import analyze_4 as an  # noqa: E402
from experiments.exp4 import battery_4  # noqa: E402
from experiments.exp4 import collect_4  # noqa: E402
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
    # Mutation harness finding (Task 6): the two bars are exclusive at
    # the boundary itself (`<`, not `<=`) -- none of the cases above
    # land EXACTLY on `battery_4b.ALPHA_4B`/`MARGINAL_4B`, so weakening
    # either comparison to `<=` was undetectable.
    (0.01, "MARGINAL"),             # == ALPHA_4B exactly: not CALIBRATED
    (0.05, "NOT-DISTINGUISHABLE"),  # == MARGINAL_4B exactly: not MARGINAL
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


def test_stop_before_must_be_none_or_placebo(tmp_path):
    """Finding 1: any value other than `None`/"placebo" used to fall
    through and run the full placebo pipeline -- fatal under the
    pre-tag stand-ins, since that would compute the null on whatever
    `root4` was given, including the real tree."""
    with pytest.raises(ValueError, match="stop_before"):
        an4b.run(root4b=tmp_path / "4b", root4=tmp_path / "4", stop_before="bogus",
                **_run4b_kwargs())


def test_stop_before_placebo_never_calls_the_placebo_functions(tmp_path, monkeypatch):
    """Finding 2: `stop_before="placebo"` must return BEFORE any
    placebo function is called, not merely before the null happens to
    be USED -- the previous test only observed `v["primary"] is None`,
    which a bug two lines later (calling `placebo_pool_4b` and
    discarding the result) would not have caught. Monkeypatches the
    two functions the placebo pipeline calls first (`placebo_pool_4b`,
    per trajectory, then `draw_batteries_4b`) to raise; `root4` is
    empty (no world needed -- `stop_before` must win regardless of
    what else has already failed)."""
    from experiments.exp4b import placebo_4b

    def _boom(*a, **k):
        raise AssertionError("placebo_4b function called despite stop_before='placebo'")

    monkeypatch.setattr(placebo_4b, "placebo_pool_4b", _boom)
    monkeypatch.setattr(placebo_4b, "draw_batteries_4b", _boom)

    v = an4b.run(root4b=tmp_path / "4b", root4=tmp_path / "4", stop_before="placebo",
                **_run4b_kwargs())
    assert v["verdict"] == "INSUFFICIENT_DATA"
    assert v["reason"] == "4b: stopped before the placebo null (pre-tag tool run)"


@pytest.mark.slow
def test_stop_before_placebo_never_calls_the_placebo_functions_on_a_real_world(_leads_world_4b,
                                                                               tmp_path, monkeypatch):
    """Task 5 review, carried item (c): the fast version above proves
    the guard fires on an EMPTY `root4`, where the placebo pipeline was
    never going to be reached anyway (every upstream loader already
    failed) -- it cannot distinguish "stop_before wins" from "nothing
    got far enough to call these functions regardless". On the shared
    "leads" world every gate passes and the per-trajectory placebo-pool
    loop IS reached (`test_full_shape_4b.py::test_leads_world_
    feasibility_floor` -- the floor fires only AFTER the pool loop),
    so this is the genuine test: `stop_before="placebo"` must win even
    when the pipeline is otherwise healthy enough to have called these
    functions for real."""
    from experiments.exp4b import placebo_4b

    def _boom(*a, **k):
        raise AssertionError("placebo_4b function called despite stop_before='placebo'")

    monkeypatch.setattr(placebo_4b, "placebo_pool_4b", _boom)
    monkeypatch.setattr(placebo_4b, "draw_batteries_4b", _boom)

    root4, v4 = _leads_world_4b
    v = an4b.run(root4b=tmp_path / "4b", root4=root4, stop_before="placebo", power_gate="full",
                **_run4b_kwargs())
    assert v["verdict"] == "INSUFFICIENT_DATA"
    assert v["reason"] == "4b: stopped before the placebo null (pre-tag tool run)"
    for n in ("1", "2", "3", "4", "5"):
        assert v["gates"][n]["pass"] is True, (n, v["gates"][n])


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


# --------------------------------- gate rederivation, unit-level (fast, hand data)
#
# Mutation harness finding (Task 6, controller ruling): gate1/2/3/5_
# rederive_4b are pure comparison functions over already-validated
# inputs -- the slow gate-perturbation tests above cover the SAME
# sites reached through a full `run()` on a real/synthetic world
# (needed for the FULL re-derivation's own correctness), but the
# mutation harness's FAST suite never reaches them that way. These
# unit-test the comparison logic directly: gate1 with hand-built
# series/rung_sets/eligibility/cells (no file I/O at all -- `cells_4`/
# `primary_4` are pure functions of in-memory data); gate2/3/5 with the
# one real-file-reading call monkeypatched to a fixed stub (`an.
# eligibility_table_4`, `an.lambda_hat_4`, `an.gate0_4`/`collect_4.
# load_ref_tables_4` respectively), so what is under test is each
# gate's OWN `got != want` comparison, never a fresh re-derivation.


def test_gate1_rederive_4b_fails_on_mismatched_t4():
    # One trajectory "T", one flat rung "F" (identically zero, so the
    # trend is flat and excess("X") == a("X") exactly), one real rung
    # "X" clearing at index 3: phi = x[2]/x[3] = 2.0/4.0 = 0.5.
    series_by_traj = {"T": {"a": {"F": [0.0, 0.0, 0.0, 0.0], "X": [0.0, 1.0, 2.0, 4.0]},
                            "steps": [0, 1, 2, 3]}}
    rung_sets = {"T": {"flat": ["F"], "R": {"X": {}}}}
    elig4 = {"T": {"R": {"X": {"eligible": True, "t_clear_index": 3, "t_clear": 3}}}}
    cells4 = [{"traj": "T", "rung": "X", "phi": 0.5, "t_clear": 3}]

    g_ok = an4b.gate1_rederive_4b(series_by_traj, rung_sets, elig4, cells4, T4=0.5)
    assert g_ok["pass"] is True, g_ok
    assert g_ok["t_match"] is True and g_ok["cells_match"] is True

    g_bad = an4b.gate1_rederive_4b(series_by_traj, rung_sets, elig4, cells4, T4=0.999)
    assert g_bad["pass"] is False
    assert g_bad["t_match"] is False


def test_gate2_rederive_4b_fails_on_mismatched_eligibility(monkeypatch):
    recomputed = {"T": {"R": {"X": {"eligible": True, "se": 0.1}}}}
    monkeypatch.setattr(an, "eligibility_table_4", lambda root4: recomputed)

    g_ok = an4b.gate2_rederive_4b(root4="unused", elig4=recomputed)
    assert g_ok["pass"] is True, g_ok
    assert g_ok["diffs"] == []

    committed_wrong = {"T": {"R": {"X": {"eligible": True, "se": 0.2}}}}
    g_bad = an4b.gate2_rederive_4b(root4="unused", elig4=committed_wrong)
    assert g_bad["pass"] is False
    assert g_bad["diffs"]


def test_gate3_rederive_4b_fails_on_mismatched_lambda_hat(monkeypatch):
    monkeypatch.setattr(
        an, "lambda_hat_4",
        lambda series_by_traj, rung_sets, elig4: {"per_traj": {"T": {"lambda_hat": 2.0}}})

    v4_ok = {"calibration": {"per_traj": {"T": {"lambda_hat": 2.0}}}}
    g_ok = an4b.gate3_rederive_4b({}, {}, {}, v4_ok)
    assert g_ok["pass"] is True, g_ok
    assert g_ok["diffs"] == []

    v4_bad = {"calibration": {"per_traj": {"T": {"lambda_hat": 3.0}}}}
    g_bad = an4b.gate3_rederive_4b({}, {}, {}, v4_bad)
    assert g_bad["pass"] is False
    assert g_bad["diffs"]


def test_gate5_rederive_4b_fails_on_mismatched_fraction_below(monkeypatch):
    monkeypatch.setattr(collect_4, "load_ref_tables_4",
                        lambda root4, refs: {ref: {"sets": {}} for ref in refs})
    monkeypatch.setattr(an, "gate0_4",
                        lambda root4, traj, ref_tables, stage_tables: {"fraction_below": 0.9})

    v4_ok = {"gate0": {traj: {"fraction_below": 0.9} for traj in battery_4.TRAJECTORIES_4}}
    g_ok = an4b.gate5_rederive_4b(root4="unused", stage_tables_4={}, v4=v4_ok)
    assert g_ok["pass"] is True, g_ok

    v4_bad = {"gate0": {traj: {"fraction_below": 0.1} for traj in battery_4.TRAJECTORIES_4}}
    g_bad = an4b.gate5_rederive_4b(root4="unused", stage_tables_4={}, v4=v4_bad)
    assert g_bad["pass"] is False


def test_imported_sha256_4b_pin_matches_disk_and_covers_every_residual_module():
    """Mutation harness review finding 2: nothing in the suite asserts
    the FILLED pin itself -- every other test passes `imports_pinned=
    False`, and the one `imports_pinned=True` test (`test_totality_4b.
    py`'s import-surface-entry test) monkeypatches `check_imports_4b`
    away rather than exercising the pin's own content.

    (a) `IMPORTED_SHA256_4B` is not `None` and every pinned path's
    CURRENT `sha256_file` matches its literal -- catches silent drift a
    one-shot manual `import_scan_4b.py` run would not.
    (b) its key set equals the directory listing of every `*.py` file
    directly under `experiments/exp4b/` (not `tests/`) MINUS
    `INSTRUMENT_BLOBS_4B`'s five tag-bound files -- a module added
    later without re-running `import_scan_4b.py` fails THIS test
    instead of silently slipping past `check_imports_4b`, which only
    complains about modules the CURRENT process actually imported, not
    modules that exist on disk but were never reached this run."""
    assert an4b.IMPORTED_SHA256_4B is not None
    for p, want in an4b.IMPORTED_SHA256_4B.items():
        got = an4b.bg.sha256_file(Path(p))
        assert got == want, f"{p}: sha256_file drifted from the pin ({got!r} != {want!r})"

    instrument = {(an4b.battery_4b.REPO / rel).resolve()
                 for rel in an4b.battery_4b.INSTRUMENT_BLOBS_4B}
    on_disk = {p.resolve() for p in an4b.EXP4B.glob("*.py")} - instrument
    pinned = {Path(p).resolve() for p in an4b.IMPORTED_SHA256_4B}
    assert pinned == on_disk, f"only pinned: {pinned - on_disk}; only on disk: {on_disk - pinned}"


def test_check_imports_4b_drift_checks_exp4s_own_residual_pins(monkeypatch):
    """Final review Important 1: `an.IMPORTED_SHA256_4`'s five entries
    (exp4's own residual, e.g. `_threads_4.py`, the BLAS thread pin)
    used to sit only in `covered` (set membership) inside `check_
    imports_4b` -- a drifted file there passed silently, since
    membership never compares a file's CURRENT hash against its pin.
    They are now folded into `pinned` too (see the fix), so a drifted
    entry there must raise "drifted from its pin" exactly like exp4b's
    own residual pins already did. Calls `check_imports_4b()` directly
    (a real scan of `sys.modules`, not a monkeypatched stand-in) --
    every module this test file's own imports pull in is already
    covered/pinned (`test_imported_sha256_4b_pin_matches_disk_and_
    covers_every_residual_module`, above, exercises that half), so the
    only thing perturbed here is one entry's hash."""
    real = dict(an4b.an.IMPORTED_SHA256_4)
    assert real, "an.IMPORTED_SHA256_4 must carry at least one entry to perturb"
    bad_path = next(iter(real))
    bad = dict(real)
    bad[bad_path] = "0" * 64
    monkeypatch.setattr(an4b.an, "IMPORTED_SHA256_4", bad)
    with pytest.raises(RuntimeError, match="drifted from its pin"):
        an4b.check_imports_4b()
