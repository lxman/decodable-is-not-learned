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
                         untrained_fires={}, shuffled_fires=[])


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
                        shuffled_fires=[])
    assert verdict(inp)["verdict"] == "FAIL"


# ------------------- exact-test amendment paths (ruling 2026-08-01,
# implemented pre-freeze 2026-08-06: PASS branch adjudicates with the
# design §5 block-permutation test at fixed alpha .01; the calibrated-
# naive test and its rho_family-dependent cutoff input are gone)


def test_exact_amendment_block_p_replaces_naive():
    out = verdict(_clean())
    assert "naive_p" not in out
    for key in ("block_p", "n_perms", "resolution", "method"):
        assert key in out, key
    # [3]*9 shape: nine same-size blocks -> 9! = 362,880 enumerated perms
    assert out["method"] == "enumerated"
    assert out["n_perms"] == 362_880
    assert out["verdict"] == "PASS"                    # rho=0.9 generator


def test_exact_amendment_no_calibrated_cutoff_field():
    import dataclasses
    names = {f.name for f in dataclasses.fields(AnalyzeInputs)}
    assert "calibrated_cutoff" not in names


def test_exact_amendment_family_noncontiguous_input_grouped():
    # the ledgered interface contract (2026-08-01, "don't pick
    # silently"): rung arrays must reach the block test as contiguous
    # per-family blocks even when the INPUT order interleaves families
    from experiments.exp2c.run.power_table import exact_block_p
    contiguous = _clean()
    interleaved = _clean()
    # round-robin across families: f0r0, f1r0, ..., f8r0, f0r1, ...
    interleaved.rungs = sorted(
        interleaved.rungs, key=lambda r: (r["name"][-1], r["family"]))
    a, b = verdict(contiguous), verdict(interleaved)
    assert a["block_p"] == b["block_p"]                # order-invariant
    # and both equal a hand-grouped direct call
    rungs = contiguous.rungs
    fams = []
    for r in rungs:
        if r["family"] not in fams:
            fams.append(r["family"])
    grouped = [r for f in fams for r in rungs if r["family"] == f]
    x = np.array([r["probe_score"] for r in grouped])
    y = np.array([r["ascent_score"] for r in grouped])
    sizes = [sum(1 for r in rungs if r["family"] == f) for f in fams]
    assert a["block_p"] == exact_block_p(x, y, sizes)["p"]


def test_exact_amendment_sampled_route_on_oversized_shape():
    # [2]*11 -> 11! = 39.9M block perms > the 5e6 enumeration guard:
    # the amendment must route to the sampled path (n_sample=100_000,
    # add-one convention), exactly as the certified power table did
    out = verdict(_clean(n_fam=11, per_fam=2))         # 22 rungs, 11 fams
    assert out["method"] == "sampled"
    assert out["n_perms"] == 100_000
    assert out["verdict"] == "PASS"


def test_exact_amendment_deterministic():
    a, b = verdict(_clean()), verdict(_clean())
    assert a["block_p"] == b["block_p"]
    assert a["rho"] == b["rho"]
