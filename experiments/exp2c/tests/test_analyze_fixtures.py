# experiments/exp2c/tests/test_analyze_fixtures.py
"""The §4.5 fixture suite. The freeze does not happen until this file
passes against the frozen analyze.py. One synthetic case per
preregistered provision."""

import numpy as np

from experiments.exp2c.analyze import AnalyzeInputs, verdict


def _rungs(n_fam, per_fam, rho=0.9, seed=0):
    rng = np.random.default_rng(seed)
    rungs = []
    for f in range(n_fam):
        for r in range(per_fam):
            x = rng.normal()
            rungs.append({"name": f"f{f}r{r}", "family": f"fam{f}",
                          "probe_score": x,
                          "ascent_score": rho * x + (1 - rho) * rng.normal(),
                          "scored": True})
    return rungs


def _clean(n_fam=9, per_fam=3):
    return AnalyzeInputs(rungs=_rungs(n_fam, per_fam),
                         untrained_fires={}, shuffled_fires=[],
                         calibrated_cutoff=0.01)


def test_provision_one_leaking_rung_attrition_without_abort():
    inp = _clean()
    inp.untrained_fires = {"f0r0": ["structural_abort"] * 10}
    out = verdict(inp)
    assert out["verdict"] != "PIPELINE_ABORT"          # ruling (a)'s boundary
    assert "attrition:f0r0" in out["audit"]
    assert out["n_rungs"] == 26                        # 27 - 1


def test_provision_clean_null_floor_fire_tolerated():
    inp = _clean()
    inp.shuffled_fires = [{"rung": "f1r0", "classification": "tolerated"}]
    out = verdict(inp)
    assert out["verdict"] != "PIPELINE_ABORT"
    assert "shuffled:count_test" in " ".join(out["audit"])


def test_provision_elevated_fire_counts_but_never_aborts():
    inp = _clean()
    inp.shuffled_fires = [{"rung": "f1r0", "classification": "elevated"}]
    assert verdict(inp)["verdict"] != "PIPELINE_ABORT"


def test_provision_structural_shuffled_fire_aborts():
    inp = _clean()
    inp.shuffled_fires = [{"rung": "f1r0",
                           "classification": "structural_abort"}]
    assert verdict(inp)["verdict"] == "PIPELINE_ABORT"


def test_provision_flat_family_zero_ties_path():
    inp = _clean()
    for r in inp.rungs:
        if r["family"] == "fam2":
            r["ascent_score"] = 0.0                    # flat family: ties
    out = verdict(inp)
    assert out["verdict"] in ("PASS", "FAIL", "INDETERMINATE")
    assert "ties:fam2" in " ".join(out["audit"])


def test_provision_dual_floor_families():
    out = verdict(_clean(n_fam=7, per_fam=3))          # 7 < 8 families
    assert out["verdict"] == "INSUFFICIENT_DATA"


def test_provision_dual_floor_rungs():
    out = verdict(_clean(n_fam=9, per_fam=2))          # 18 < 20 rungs
    assert out["verdict"] == "INSUFFICIENT_DATA"


def test_verdict_precedence_insufficient_beats_pass():
    inp = _clean(n_fam=7, per_fam=3)                   # would PASS on rho
    assert verdict(inp)["verdict"] == "INSUFFICIENT_DATA"


def test_provision_unscored_rung_audited():
    # authorized amendment 2 (2026-07-29): a scored=False rung with no
    # fires must leave an audit trail, not vanish silently
    inp = _clean()
    inp.rungs[0]["scored"] = False
    out = verdict(inp)
    assert out["verdict"] != "PIPELINE_ABORT"
    assert "unscored:f0r0" in out["audit"]
    assert out["n_rungs"] == 26                        # 27 - 1


def test_provision_independent_battery_fail_branch():
    # authorized amendment 3 (2026-07-29): the §5 falsifier — probe and
    # ascent scores drawn independently, family-cluster CI spans 0
    rng = np.random.default_rng(2)
    rungs = []
    for f in range(9):
        for r in range(3):
            rungs.append({"name": f"f{f}r{r}", "family": f"fam{f}",
                          "probe_score": rng.normal(),
                          "ascent_score": rng.normal(),
                          "scored": True})
    inp = AnalyzeInputs(rungs=rungs, untrained_fires={},
                        shuffled_fires=[], calibrated_cutoff=0.01)
    assert verdict(inp)["verdict"] == "FAIL"
