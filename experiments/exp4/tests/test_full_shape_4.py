# experiments/exp4/tests/test_full_shape_4.py
"""World-terminal tests for `analyze_4.run()` (Task 4 brief, Step 3):
every terminal reached; the LEADS world's per-cell phi in (.4, .8);
the FOLLOWS world's T within +/-.1 of 0; S1-S11 present in every non-
INSUFFICIENT world; verdict.json strict JSON; the two-process
determinism fixture.

Every world is built through `full_shape.build_world`, which writes
through the production persistence functions from synthetic
activations (no torch, no network, no model contact) -- see that
module's docstring for the construction and its test-performance
simplifications (disclosed in PROGRESS.md).

Grid shrinking is NOT used here: `analyze_4.run()`'s "4 checkpoint
manifests" gate (`battery_4.manifests_4`) compares the LIVE
`battery_4.GRID_4` against the REAL committed manifest's grid field,
with no test-injection point -- shrinking `GRID_4` makes that gate
fail before any later gate (gate 1, eligibility, the missing= route
under test) is ever reached. Every `stage='full'` world here therefore
uses the real, full per-trajectory grid (92 sweep points + 19
reference-stage keys); one LEADS-mode build is shared, via
`shutil.copytree`, across the missing-route and determinism tests to
avoid rebuilding it nine-plus times."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from experiments.exp2g import battery_2g as bg
from experiments.exp4 import analyze_4 as an
from experiments.exp4 import battery_4
from experiments.exp4.tests import full_shape as fs


def _blob_sha(tag, rel):
    """The 2k/2n-pattern fake: the 'tag-bound' sha IS the file's own
    sha, so `require_prereg_4`'s equality check passes without a real
    git tag."""
    p = battery_4.REPO / rel
    return bg.sha256_file(p) if p.is_file() else None


def _run_kwargs():
    # Review round 1, IMPORTANT 3: build_world's power record is now a
    # REAL power_4.compute(n_sim=fs.WORLD_POWER_N_SIM_4, ...) call, not
    # a stub -- expected_n_sim must match for the analyzer's shape
    # check to accept it.
    return dict(tag_exists=lambda t: True, blob_sha=_blob_sha,
               blobs_bound=lambda tag, paths, repo_root=None: [],
               referents_sha=False, imports_pinned=False,
               expected_n_sim=fs.WORLD_POWER_N_SIM_4)


def _needle_in_failures(v, needle):
    ref = (v.get("referents") or {}).get("failures") or []
    text = " ".join(ref) + " " + (v.get("reason") or "")
    return needle.lower() in text.lower()


# ---------------------------------------------------------------- terminals

def _assert_every_secondary_and_sensitivity_present(v):
    # I-5(c): every S1-S11 entry and every sensitivity entry must be a
    # REAL value, never the `{"failed": ...}` shape `_sec` writes when
    # `collect_total_4` catches an exception -- a passing LEADS world
    # is exactly the case where nothing should be silently degraded.
    for name, entry in (v["secondaries"] or {}).items():
        assert not (isinstance(entry, dict) and "failed" in entry), (name, entry)
    for name, entry in (v["sensitivities"] or {}).items():
        assert not (isinstance(entry, dict) and "failed" in entry), (name, entry)


@pytest.mark.slow
def test_leads_world_reaches_leads(_leads_world):
    # I-4: the non-xfail half -- verdict, cell count, gate 0/1 PASS on
    # every trajectory, every secondary/sensitivity a real value. The
    # strict per-cell phi band (the one known, disclosed gap) is its
    # own xfail test below so a real assertion failure here can never
    # be masked by `xfail(strict=True)`.
    v = an.run(root=_leads_world, **_run_kwargs())
    assert v["verdict"] == "LEADS", v["reason"]
    cells = v["cells"]
    assert len(cells) >= 3
    for name in ("S1", "S8", "S10", "S11", "S11 per-reference"):
        assert name in v["secondaries"]
    assert v["sensitivities"]
    # Final review IMPORTANT 3: the two preregistered descriptives the
    # build never implemented must be real values on a passing world.
    fam = v["sensitivities"]["family-matched trend"]
    assert fam["per_cell"] and fam["no_alpha_claim"] is True
    per_ref = v["secondaries"]["S11 per-reference"]["per_traj"]
    assert any((b or {}).get("available") for b in per_ref.values()), per_ref
    # R-7 (IMPORTANT 2) + Minor 9: the calibration block, the realized
    # alpha, the scatter grid and the computed licence condition.
    assert v["calibration"] and v["calibration"]["per_traj"]
    assert "failed" not in v["calibration"]
    assert (v["power"] or {}).get("realized_alpha_leads") is not None
    assert set((v["power"] or {}).get("zero_excess_scatter") or {}) == \
        {"1.0", "1.5", "2.0", "3.0"}
    assert isinstance(v["licence_condition_met"], bool)
    assert v["licence_condition"]["rule"]
    # Minor 7: the verdict carries the thread pin.
    assert v["pins_active"]["threads_pinned"] is True
    for traj in battery_4.TRAJECTORIES_4:
        g0 = v["gate0"][traj]
        assert g0 is not None and g0["pass"] is True, (traj, g0)
        g1 = v["gate1"][traj]
        assert g1 is not None and all(g1["sets_equal"].values()) \
            and all(g1["activation_sha_equal"].values()) \
            and all(g1["attested_sha_equal"].values()) and g1["digest_equal"], (traj, g1)
    _assert_every_secondary_and_sensitivity_present(v)


@pytest.mark.slow
@pytest.mark.xfail(
    reason="KNOWN GAP (see PROGRESS.md 'World verification'): five "
    "(seed, K_TASK_EXPONENT) combinations were tried for the LEADS "
    "construction; the closest, seed=11 at K_TASK_EXPONENT=2.0 (what "
    "_leads_world builds), gives phi in [0.3933, 0.7104] over 42 "
    "cells -- ONE cell (comma_7b/add3_mid) 0.0067 below the brief's "
    "0.4 floor, the rest comfortably inside (.4, .8). The assertion "
    "is left matching the brief's literal requirement rather than "
    "widened to fit what was actually achieved; strict=True so this "
    "flips to an error (XPASS) the day a better seed/construction "
    "closes the gap, exactly as happened for the UNDETERMINED world.",
    strict=True,
)
def test_leads_world_every_cell_phi_in_band(_leads_world):
    v = an.run(root=_leads_world, **_run_kwargs())
    assert v["verdict"] == "LEADS", v["reason"]
    for c in v["cells"]:
        assert 0.4 < c["phi"] < 0.8, c


@pytest.mark.slow
def test_follows_world_t_near_zero(tmp_path):
    fs.build_world(tmp_path, "follows", seed=3)
    v = an.run(root=tmp_path, **_run_kwargs())
    assert v["verdict"] == "FOLLOWS", v["reason"]
    assert abs(v["primary"]["T"]) < 0.1, v["primary"]["T"]


@pytest.mark.slow
def test_no_convergence_world(tmp_path):
    # seed=29: task signal is off entirely in this mode (p_task == 0
    # for every rung, regardless of K_TASK_EXPONENT), so the only
    # thing that varies by seed is which of the ~50 candidate
    # (trajectory, R_M-rung) cells' pure sampling noise happens to
    # cross eligibility's 2-SE bar; most seeds give 0-2 such false
    # positives (comfortably under MIN_CELLS_4), this one is confirmed
    # clean (1 eligible cell).
    fs.build_world(tmp_path, "no_convergence", seed=29)
    v = an.run(root=tmp_path, **_run_kwargs())
    assert v["verdict"] == "NO-CONVERGENCE", v["reason"]


@pytest.mark.slow
def test_partial_world_reaches_partial(tmp_path):
    fs.build_world(tmp_path, "partial", seed=3)
    v = an.run(root=tmp_path, **_run_kwargs())
    assert v["verdict"] == "PARTIAL", v["reason"]
    # PARTIAL is a statement about the AGGREGATE T (0 < T < .25,
    # p+ < .01), not a per-cell guarantee -- individual cells may be
    # small or even slightly negative under sampling noise, same as a
    # real battery's texture.
    assert 0.0 < v["primary"]["T"] < 0.25


@pytest.mark.slow
def test_undetermined_world(tmp_path):
    # The dedicated "undetermined" mode (signal diluted 3x, injected
    # into only the two smallest-|R_M| trajectories) was tried at
    # three seeds (3, 5, 23) and all three landed PARTIAL (a real,
    # small, highly significant effect -- p+ 7e-4-1.5e-3), never
    # UNDETERMINED -- diluting the signal shrinks T but does not widen
    # the bootstrap CI enough to cross into genuine ambiguity.
    # UNDETERMINED turned out to come from the OTHER direction: mode=
    # "no_convergence" (task signal off entirely, p_task == 0 for
    # every rung) with a seed whose pure sampling noise crosses
    # eligibility's 2-SE bar on enough (trajectory, rung) cells --
    # here 6, versus the 1 that no_convergence_retry2/seed=29 gives
    # (see test_no_convergence_world) -- for cells_4() to clear
    # MIN_CELLS_4/MIN_RUNGS_4 and reach primary_4, but too few for the
    # bootstrap to resolve a real-looking point estimate (T .3795) as
    # significant: p+ .0625 >= ALPHA_4 (not PARTIAL/LEADS) and the
    # CI95 upper bound .5008 >= T_BAR_4 (not FOLLOWS) -- the tree's own
    # UNDETERMINED branch, reached by a genuinely ambiguous noise
    # draw, not by construction. The UNDETERMINED branch of
    # `verdict_tree_4` is also covered directly, hand-built, by
    # `test_tree_cells` in test_analyze_4.py.
    fs.build_world(tmp_path, "no_convergence", seed=1)
    v = an.run(root=tmp_path, **_run_kwargs())
    assert v["verdict"] == "UNDETERMINED", v["reason"]


# --------------------------------------------------------------- INSUFFICIENT

@pytest.fixture(scope="module")
def _leads_world(tmp_path_factory):
    """ONE full-grid LEADS-mode world, built once and shared (fresh
    copies via `shutil.copytree`) by the missing-route tests, the
    determinism fixture and the strict per-cell-phi test. seed=11 is
    the best of four (seed, K_TASK_EXPONENT) combinations tried --
    see PROGRESS.md."""
    root = tmp_path_factory.mktemp("leads_world")
    fs.build_world(root, "leads", seed=11)
    return root


def _fresh_copy(template_root, tmp_path):
    dst = tmp_path / "world"
    shutil.copytree(template_root, dst)
    return dst


@pytest.mark.slow
@pytest.mark.parametrize("missing", fs.MISSING_ROUTES)
def test_missing_route_gives_insufficient_data(missing, _leads_world, tmp_path):
    root = _fresh_copy(_leads_world, tmp_path)
    needle = fs.apply_missing(root, missing)
    v = an.run(root=root, **_run_kwargs())
    assert v["verdict"] == "INSUFFICIENT_DATA", (missing, v["reason"])
    assert _needle_in_failures(v, needle), (missing, v["reason"], v["referents"]["failures"])


# ------------------------------------------------------------- I-1 totality

@pytest.mark.slow
def test_gate1_json_as_a_list_gives_insufficient_data(_leads_world, tmp_path):
    # I-1: `battery_4.gate1_failures_4(g1_att, ...)` must not RAISE on
    # a malformed gate1.json (a list, not a dict) -- `collect_total_4`
    # catches it and the tree lands INSUFFICIENT_DATA, not a crash.
    root = _fresh_copy(_leads_world, tmp_path)
    battery_4.gate1_path(root, "pythia_2.8b").write_text(json.dumps([1, 2, 3]))
    v = an.run(root=root, **_run_kwargs())
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert _needle_in_failures(v, "gate 1 pythia_2.8b")


@pytest.mark.slow
def test_power_record_as_a_scalar_gives_insufficient_data(_leads_world, tmp_path):
    # I-1: `_check_power_matches_eligibility_4(power, ...)` must not
    # RAISE on a scalar power record.
    root = _fresh_copy(_leads_world, tmp_path)
    battery_4.power_path(root).write_text(json.dumps(42))
    v = an.run(root=root, **_run_kwargs())
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert _needle_in_failures(v, "power")


@pytest.mark.slow
def test_eligibility_record_as_a_list_gives_insufficient_data(_leads_world, tmp_path):
    # I-1: `_eligibility_summary_4(eligibility)` inside `verdict_4`
    # must not RAISE on a malformed (list) eligibility file -- it
    # fires AFTER the comparison step already recorded its own
    # disagreement failure, and previously threw that INSUFFICIENT_
    # DATA away with an unhandled AttributeError.
    root = _fresh_copy(_leads_world, tmp_path)
    battery_4.eligibility_path(root).write_text(json.dumps([1, 2, 3]))
    v = an.run(root=root, **_run_kwargs())
    assert v["verdict"] == "INSUFFICIENT_DATA", v["reason"]
    assert _needle_in_failures(v, "eligibility")


# ------------------------------------------------------------------- I-8

@pytest.mark.slow
def test_referent_manifest_pin_hook_runs_the_real_check(_leads_world, tmp_path, monkeypatch):
    # I-8: when referents_sha is a string, run() must actually CALL a
    # referent-manifest checker (lazily imported as `experiments.exp4.
    # make_referents_4`), not merely assume "pinned" from the sha's
    # mere presence -- `pins_active["referent_manifest"]` reflects
    # whether that check ran AND passed.
    import sys
    import types
    root = _fresh_copy(_leads_world, tmp_path)
    kwargs = dict(_run_kwargs())
    kwargs["referents_sha"] = "a" * 64

    calls = []
    stub_pass = types.ModuleType("experiments.exp4.make_referents_4")

    def check_referents_pass(path, *, sha_pin):
        calls.append((path, sha_pin))
        return []          # the real contract: a list of drift failures, empty = clean
    stub_pass.check_referents = check_referents_pass
    monkeypatch.setitem(sys.modules, "experiments.exp4.make_referents_4", stub_pass)

    v = an.run(root=root, **kwargs)
    assert calls == [(an.REFERENTS_PATH_4, "a" * 64)]
    assert v["pins_active"]["referent_manifest"] is True

    stub_fail = types.ModuleType("experiments.exp4.make_referents_4")

    def check_referents_fail(path, *, sha_pin):
        raise ValueError("referent manifest sha mismatch")
    stub_fail.check_referents = check_referents_fail
    monkeypatch.setitem(sys.modules, "experiments.exp4.make_referents_4", stub_fail)

    v2 = an.run(root=root, **kwargs)
    assert v2["pins_active"]["referent_manifest"] is False
    assert _needle_in_failures(v2, "referent manifest")

    # Task 5 finding 2: a check that returns a NON-EMPTY list of drift
    # failures WITHOUT raising must also be consumed, not discarded —
    # the bug the finding fixes was exactly `_, f =
    # collect_total_4(...)` throwing the returned list away.
    stub_drift = types.ModuleType("experiments.exp4.make_referents_4")

    def check_referents_drift(path, *, sha_pin):
        return ["experiments/exp2g/results/predictor/predictor.json: sha drift"]
    stub_drift.check_referents = check_referents_drift
    monkeypatch.setitem(sys.modules, "experiments.exp4.make_referents_4", stub_drift)

    v3 = an.run(root=root, **kwargs)
    assert v3["pins_active"]["referent_manifest"] is False
    assert _needle_in_failures(v3, "predictor.json: sha drift")


# --------------------------------------------------------- secondaries/JSON

@pytest.mark.slow
def test_secondaries_and_strict_json_leads(_leads_world, tmp_path):
    root = _fresh_copy(_leads_world, tmp_path)
    v = an.run(root=root, write=True, **_run_kwargs())
    assert v["verdict"] != "INSUFFICIENT_DATA"
    for name in ("S1", "S2 from-below (1b)", "S2 per-trajectory", "S2 known-answer gates",
                "S3", "S4", "S8", "S10", "S11", "S11 per-reference"):
        assert name in v["secondaries"], (name, sorted(v["secondaries"]))
    assert v["sensitivities"] is not None
    sens_keys = sorted(v["sensitivities"])
    for prefix in ("S5 ", "S6 ", "S7 "):
        assert any(k.startswith(prefix) for k in sens_keys), (prefix, sens_keys)
    assert "S9" in v["sensitivities"]
    assert "S1 quarter/three-quarter" in v["sensitivities"]
    assert "primary_clears_and_stays" in v["sensitivities"]
    assert "family-matched trend" in v["sensitivities"]
    assert "k=5" in v["sensitivities"] and "k=20" in v["sensitivities"]
    assert v["known_outcome_caveat"]
    assert v["licensed_sentence"]
    raw = json.dumps(v, allow_nan=False)          # raises on NaN/Inf if any slipped through
    reparsed = json.loads(raw)
    assert reparsed["verdict"] == v["verdict"]
    verdict_path = battery_4.verdict_path(root)
    assert verdict_path.is_file()
    on_disk = json.loads(verdict_path.read_text())
    json.dumps(on_disk, allow_nan=False)


# ------------------- RATIFICATION: the lambda_hat site, where it is REACHED

@pytest.mark.slow
def test_lambda_hat_4_call_is_collected_not_raised(_leads_world, tmp_path, monkeypatch):
    """Ratification open item 3. R-7(b)'s `collect_total_4(lambda:
    lambda_hat_4(...), "4 lambda_hat")` site is guarded by `not
    failures`, so NO tree the totality base can produce reaches it —
    that base is reference-only and its failures are non-empty by
    construction, which is why its auto-generated mutant survives a
    `--totality` pass. It is reached on a complete world, and its
    contract there is not the tree's: a raise DEGRADES the calibration
    block and leaves the verdict alone (`calibration = {"failed": ...}`),
    it does not refuse. Tested here, on the world where the site runs.
    The wrapper itself is also pinned structurally by
    `test_every_collect_total_4_refusal_label_is_present`, which the
    fast suite runs and which the mutant fails in milliseconds."""
    root = _fresh_copy(_leads_world, tmp_path)
    clean = an.run(root=root, **_run_kwargs())
    assert clean["verdict"] != "INSUFFICIENT_DATA", clean["reason"]
    assert isinstance(clean["calibration"], dict) and "failed" not in clean["calibration"]

    def _boom(series_by_traj, rung_sets_by_traj, eligibility):
        raise RuntimeError("synthetic lambda_hat_4 failure (test-injected)")

    monkeypatch.setattr(an, "lambda_hat_4", _boom)
    v = an.run(root=root, **_run_kwargs())
    assert v["verdict"] == clean["verdict"], v["reason"]     # the verdict is untouched
    assert list(v["calibration"]) == ["failed"]
    assert "4 lambda_hat" in v["calibration"]["failed"]


# ----------------------------------------------------------------- determ.

_DET_SCRIPT = """
import json, sys
from pathlib import Path

sys.path.insert(0, {repo!r})
from experiments.exp2g import battery_2g as bg
from experiments.exp4 import analyze_4 as an
from experiments.exp4 import battery_4

def blob_sha(tag, rel):
    p = battery_4.REPO / rel
    return bg.sha256_file(p) if p.is_file() else None

root = Path(sys.argv[1])
v = an.run(root=root, tag_exists=lambda t: True, blob_sha=blob_sha,
          blobs_bound=lambda tag, paths, repo_root=None: [],
          referents_sha=False, imports_pinned=False)
print(json.dumps(v, sort_keys=True, allow_nan=False))
"""


@pytest.mark.slow
def test_determinism_fixture_two_processes(_leads_world, tmp_path):
    root = _fresh_copy(_leads_world, tmp_path)
    script = tmp_path / "_det.py"
    script.write_text(_DET_SCRIPT.format(repo=str(battery_4.REPO)))
    outs = []
    for _ in range(2):
        r = subprocess.run([sys.executable, str(script), str(root)],
                           cwd=str(battery_4.REPO), capture_output=True, text=True, check=True)
        outs.append(json.loads(r.stdout))

    def strip(v):
        v = dict(v)
        v.pop("git_sha", None)
        return v
    a, b = strip(outs[0]), strip(outs[1])
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)
