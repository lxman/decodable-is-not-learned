import pytest

from experiments.exp5b import analyze_5b as an
from experiments.exp5b import battery_5b as b5b
from experiments.exp5b import power_5b as pw5b


def test_collect_total_5b_prefix_named_types_and_crash_on_logic_defect():
    v, f = an.collect_total_5b(lambda: (_ for _ in ()).throw(OSError("x")), "5b x")
    assert v is None and f == ["5b x: OSError: x"]
    assert an.collect_total_5b(lambda: 3, "5b y") == (3, [])
    with pytest.raises(ZeroDivisionError):
        an.collect_total_5b(lambda: 1 / 0, "5b z")
    with pytest.raises(ValueError, match="prefix"):
        an.collect_total_5b(lambda: 3, "5 no")


def test_licence_block_names_every_cell():
    s1 = {"outside_2p8b": {"T": 0.004, "p": 0.3, "n_cells": 40}}
    for verdict, cell in (("SURVIVES", "CALIBRATED"), ("SURVIVES", "INFLATED"), ("SURVIVES", "OFF-GRID"),
                          ("NOT-SURVIVED", "INSIDE"), ("NOT-SURVIVED", "SIGN-ONLY"),
                          ("NOT-SURVIVED", "SIZE-ONLY"), ("UNDETERMINED", None), ("INSUFFICIENT_DATA", None)):
        tree = {"verdict": verdict, "cell": cell, "reason": "r"}
        lb = an.licence_block_5b(tree, primary={"T": 0.03, "rung_block": {"p": 0.002}},
                                 calibration={"alpha_realized": 0.012, "sigma_hat": 14.2, "null_mean_T": -0.001,
                                              "T_star": 0.031, "cell": cell, "in_grid": cell != "OFF-GRID"},
                                 s1=s1, sigma_hat={"pooled": 14.2, "per_side": {"1b": 12.0}})
        assert lb["key"] == (f"{verdict}-{cell}" if cell else verdict)
        assert lb["sentence"] and lb["caveat"]
        if cell == "OFF-GRID":
            # finding (Task 5): the brief's licence body (== design §6's verbatim sentence,
            # `experiment-5b-design.md` line 116, "the licence is NOT claimed") capitalizes
            # NOT for emphasis, matching its "DEMOTED" sibling; the brief's own assertion here
            # checked the lowercase spelling, which is never a substring of the capitalized
            # source phrase — corrected to the phrase design §6 actually specifies, unruled
            # (flagged in PROGRESS.md / the task report; not weakened otherwise)
            assert "NOT claimed" in lb["sentence"]
        if verdict == "SURVIVES":
            assert "15 items" in lb["sentence"] and "2 items" in lb["sentence"]     # .03×500, .004×500


def test_power_failures_5b_catches_a_non_reproducing_record(monkeypatch):
    def fake_compute(cells, floors, *, n_sim, seed):
        return {"n_sim": n_sim, "seed": seed, "declaration": "POWERED", "prereg_tag": b5b.PREREG_TAG_5B,
               "exp5_closed_tag": b5b.EXP5_CLOSED_TAG_5B, "sigma_hat_axis": [1] * 6, "alpha_5b_axis": [1] * 6,
               "null_mean_5b_axis": [1] * 6, "alpha_exp5_axis": [1] * 6, "alpha_naive_axis": [1] * 6,
               "null_mean_exp5_axis": [1] * 6, "null_mean_naive_axis": [1] * 6}
    monkeypatch.setattr(an.pw5b, "compute_5b", fake_compute)
    monkeypatch.setattr(an.pw5b, "N_SIM_5B", 5)
    monkeypatch.setattr(an.pw5b, "SEED_5B", 0)
    struct_sha = pw5b.structure_sha256_5b(pw5b.structure_5b([]))
    rec = {"prereg_tag": b5b.PREREG_TAG_5B, "exp5_closed_tag": b5b.EXP5_CLOSED_TAG_5B, "n_sim": 5, "seed": 0,
          "declaration": "DECLARED UNDERPOWERED IN ADVANCE", "sigma_hat_axis": [1, 2, 3, 4, 5, 6],
          "alpha_5b_axis": [1] * 6,
          "null_mean_5b_axis": [1] * 6, "alpha_exp5_axis": [1] * 6, "alpha_naive_axis": [1] * 6,
          "null_mean_exp5_axis": [1] * 6, "null_mean_naive_axis": [1] * 6, "structure_sha256": struct_sha}
    bad = an.power_failures_5b(rec, cells5_live=[], floors={}, closed=None, power_gate="full")
    assert any("byte-for-byte" in b for b in bad)


def test_power_failures_5b_refuses_a_non_increasing_sigma_hat_axis():
    """Freeze F-3: `numpy.interp` reads a number off ANY axis; the calibration
    read is defined only on a strictly increasing simulated sigma-hat axis —
    a flat or out-of-order axis refuses (checked before the recompute, so
    also under power_gate='skip')."""
    struct_sha = pw5b.structure_sha256_5b(pw5b.structure_5b([]))
    base = {"prereg_tag": b5b.PREREG_TAG_5B, "exp5_closed_tag": b5b.EXP5_CLOSED_TAG_5B, "n_sim": pw5b.N_SIM_5B,
            "seed": pw5b.SEED_5B, "declaration": "POWERED", "alpha_5b_axis": [0] * 6, "null_mean_5b_axis": [0] * 6,
            "alpha_exp5_axis": [0] * 6, "alpha_naive_axis": [0] * 6, "null_mean_exp5_axis": [0] * 6,
            "null_mean_naive_axis": [0] * 6, "structure_sha256": struct_sha}
    ok = an.power_failures_5b(dict(base, sigma_hat_axis=[5, 10, 15, 20, 30, 45]), cells5_live=[], floors={},
                              closed=None, power_gate="skip")
    assert ok == []
    for ax in ([5, 10, 10, 20, 30, 45], [5, 15, 10, 20, 30, 45], [45, 30, 20, 15, 10, 5]):
        bad = an.power_failures_5b(dict(base, sigma_hat_axis=ax), cells5_live=[], floors={}, closed=None,
                                   power_gate="skip")
        assert any("not strictly increasing" in b for b in bad), (ax, bad)


def _isolated_kwargs(tmp_path, **over):
    """Fix round 1 (Important 1): a minimal, isolated `an.run()` call that
    reaches every UNCONDITIONAL gate in `run()`'s own body without ever
    touching the real campaign tree — `root`/`exp5_root` are empty tmp
    directories, `tag_exists` refuses the prereg/exp5-closed gates
    harmlessly, `frozen_check` is a no-op unless the caller overrides it,
    `manifest`/`sl` are injected fakes unless the caller passes `None` to
    exercise the real loader at that ONE site, `referents_sha=False`/
    `imports_pinned=False` skip those two sites unless overridden. Every
    other unconditional site (battery/floors/verify/exp5/host/units/gate
    1/power/projection) is left to fail on its own in this isolated tree
    — harmless, since none of these tests care about the FINAL verdict,
    only that ONE named site's failure is present and nothing raises."""
    kw = dict(root=tmp_path, exp5_root=tmp_path / "exp5", write=False,
              tag_exists=lambda t: False, frozen_check=lambda: None,
              manifest={"fake": True}, sl={"sha256": "x" * 64, "meta": {"n_scored": 1}},
              referents_sha=False, imports_pinned=False, power_gate="skip",
              exp5_kwargs=dict(tag_exists=lambda t: False, frozen_check=lambda: None,
                               referents_sha=False, imports_pinned=False))
    kw.update(over)
    return kw


def _assert_insufficient_with_label(v, label_prefix):
    assert v["verdict"] == "INSUFFICIENT_DATA", v
    assert any(f.startswith(label_prefix) for f in v["failures"]), v["failures"]


def test_frozen_modules_site_raises_without_the_wrapper(tmp_path):
    """Fix round 1 (Important 1): a behavioural kill for the '5b frozen
    modules' totality mutant — under the stripped wrapper this OSError
    propagates out of `run()` instead of becoming a failure."""
    v = an.run(**_isolated_kwargs(tmp_path, frozen_check=lambda: (_ for _ in ()).throw(OSError("x"))))
    _assert_insufficient_with_label(v, "5b frozen modules")


def test_import_surface_sites_raise_without_the_wrapper(tmp_path, monkeypatch):
    """Fix round 1: both '5b import surface (entry)' and '(exit)' call the
    SAME `b5b.check_imports_5b` — this one patch, run once, distinguishes
    EITHER site's own mutant (whichever one is stripped raises at that
    exact point; the other, still wrapped, is caught normally)."""
    monkeypatch.setattr(an.b5b, "check_imports_5b", lambda: (_ for _ in ()).throw(RuntimeError("boom")))
    v = an.run(**_isolated_kwargs(tmp_path, imports_pinned=True))
    assert v["verdict"] == "INSUFFICIENT_DATA", v
    assert any(f.startswith("5b import surface (entry)") for f in v["failures"]), v["failures"]
    assert any(f.startswith("5b import surface (exit)") for f in v["failures"]), v["failures"]


def test_manifest_site_raises_without_the_wrapper(tmp_path, monkeypatch):
    monkeypatch.setattr(an.b5, "load_manifest_5", lambda **kw: (_ for _ in ()).throw(ValueError("boom")))
    v = an.run(**_isolated_kwargs(tmp_path, manifest=None))
    _assert_insufficient_with_label(v, "5b manifest")


def test_slice_site_raises_without_the_wrapper(tmp_path, monkeypatch):
    monkeypatch.setattr(an.sl5, "load_slice_5", lambda **kw: (_ for _ in ()).throw(ValueError("boom")))
    v = an.run(**_isolated_kwargs(tmp_path, sl=None))
    _assert_insufficient_with_label(v, "5b slice")


def test_referents_site_raises_without_the_wrapper(tmp_path):
    """A wrong sha (never a monkeypatch) trips `check_referents_5b`'s own
    ValueError — the site's real failure mode."""
    v = an.run(**_isolated_kwargs(tmp_path, referents_sha="0" * 64))
    _assert_insufficient_with_label(v, "5b referents")


def test_battery_site_raises_without_the_wrapper(tmp_path, monkeypatch):
    monkeypatch.setattr(an.bt, "load_battery", lambda: (_ for _ in ()).throw(ValueError("boom")))
    v = an.run(**_isolated_kwargs(tmp_path))
    _assert_insufficient_with_label(v, "5b battery")


def test_floors_site_raises_without_the_wrapper(tmp_path, monkeypatch):
    monkeypatch.setattr(an.b5, "load_floors_5", lambda: (_ for _ in ()).throw(ValueError("boom")))
    v = an.run(**_isolated_kwargs(tmp_path))
    _assert_insufficient_with_label(v, "5b floors")


def test_verify_site_raises_without_the_wrapper(tmp_path, monkeypatch):
    monkeypatch.setattr(an.a2d, "load_verify", lambda: (_ for _ in ()).throw(ValueError("boom")))
    v = an.run(**_isolated_kwargs(tmp_path))
    _assert_insufficient_with_label(v, "5b verify")


def test_projection_failures_5b_checks_both_ancestries():
    sides = {"1b": {"git_shas": {143000: "u1", 30000: "u2"}, "whys": {143000: "final", 30000: "member"}}}
    ok = an.projection_failures_5b(sides, projection_commit="p", prereg_commit="t",
                                   is_ancestor=lambda a, b: True, edits=[])
    assert ok == []
    assert an.projection_failures_5b(sides, projection_commit=None, prereg_commit="t",
                                     is_ancestor=lambda a, b: True, edits=[])
    assert an.projection_failures_5b(sides, projection_commit="p", prereg_commit="t",
                                     is_ancestor=lambda a, b: not (a == "t" and b == "p"), edits=[])
    assert an.projection_failures_5b(sides, projection_commit="p", prereg_commit="t",
                                     is_ancestor=lambda a, b: not (a == "p" and b == "u2"), edits=[])
    assert an.projection_failures_5b(sides, projection_commit="p", prereg_commit="t",
                                     is_ancestor=lambda a, b: True, edits=["edited"])


def test_window_completeness_site_raises_without_the_wrapper(tmp_path):
    """Freeze F-1: the '5b window completeness' site — on an empty tree every
    side's four units are missing, so the site fails for real; under the
    stripped wrapper its ValueError propagates out of `run()`."""
    v = an.run(**_isolated_kwargs(tmp_path))
    _assert_insufficient_with_label(v, "5b window completeness")


def test_window_completeness_failures_5b_measures_the_tree(tmp_path):
    """Freeze F-1: every small side owes all four units; a missing side, a
    missing unit and a non-side directory under results/units/ each fail;
    a unit present but not 5b-complete (no `_unit_5b.json`) counts as missing."""
    from experiments.exp5 import battery_5 as b5
    bad = an.window_completeness_failures_5b(tmp_path)
    assert len(bad) == len(b5b.small_sides_5b())
    assert all("not on disk as complete 5b units" in b for b in bad)
    (b5b.units_root_5b(tmp_path) / "12b").mkdir(parents=True)
    bad = an.window_completeness_failures_5b(tmp_path)
    assert any("['12b']" in b and "not a small side" in b for b in bad)
    # a unit that Experiment 5's completeness accepts but lacks 5b's attestation is still owed
    import json as _j
    d = b5b.unit_dir_5b(tmp_path, "1b", b5.FINAL_STEP_5)
    d.mkdir(parents=True)
    import hashlib as _h
    files = {}
    for name in b5.unit_files_5():
        (d / name).write_text(name)
        files[name] = _h.sha256(name.encode()).hexdigest()
    (d / "_unit.json").write_text(_j.dumps({"files": files}))
    assert b5.unit_complete_5(tmp_path, "1b", b5.FINAL_STEP_5) and \
        not b5b.unit_complete_5b(tmp_path, "1b", b5.FINAL_STEP_5)
    bad = an.window_completeness_failures_5b(tmp_path)
    assert any(b.startswith("gate 4 1b:") and str(b5.FINAL_STEP_5) in b for b in bad)
