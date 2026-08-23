"""Fixture suite for 1c's record container.

A profile is 8 sites or it is not a profile. Exp 1's units failure and 2c's
chance-floor defect were both cases of a record that looked well-formed while
carrying a quantity that meant something other than what the analysis assumed.
These tests refuse the malformed shapes at write time rather than at analysis
time.
"""
import json

import pytest

from experiments.exp1c import records as r


def sites(null_p=0.001):
    return [r.SiteResult(layer=l, token=t, accuracy=0.2, null_p_raw=null_p,
                         null_mean=0.1)
            for l in (0, 1, 2, 3) for t in (1, -1)]


def rec(**kw):
    base = dict(system="sweep", arm="fixed", density=0.45, size_bucket="1M",
                seed=100, trained=True, sites=sites(), n_rows=400, n_val=100,
                per_class=40, capability_metric=0.09, git_sha="abc1234",
                config={})
    return r.ProfileRecord(**{**base, **kw})


def test_a_wellformed_profile_round_trips_through_json():
    a = rec()
    b = r.ProfileRecord.from_json(a.to_json())
    assert b.to_dict() == a.to_dict()
    assert [(s.layer, s.token) for s in b.sites] == [(s.layer, s.token)
                                                     for s in a.sites]


def test_a_profile_must_carry_all_eight_sites():
    with pytest.raises(ValueError, match="8 sites"):
        rec(sites=sites()[:7])


def test_a_profile_refuses_duplicate_sites():
    dup = sites()
    dup[1] = dup[0]
    with pytest.raises(ValueError, match="duplicate"):
        rec(sites=dup)


def test_a_site_outside_the_grid_is_refused_at_construction():
    """Earlier than the profile — a bad site never reaches a record at all."""
    with pytest.raises(ValueError, match="layer"):
        r.SiteResult(layer=7, token=1, accuracy=0.2, null_p_raw=0.001,
                     null_mean=0.1)
    with pytest.raises(ValueError, match="token"):
        r.SiteResult(layer=0, token=99, accuracy=0.2, null_p_raw=0.001,
                     null_mean=0.1)


def test_the_fixed_arm_requires_a_permutation_null():
    """The fixed-n arm is the verdict-touching one; a site with no null cannot
    be adjudicated by the two-gate rule."""
    with pytest.raises(ValueError, match="null"):
        rec(arm="fixed", sites=sites(null_p=None))


def test_the_natural_arm_must_not_carry_a_null():
    """Design §4: the diagnostic arm computes margins only. A null here would
    mean it had silently cost 10,000x what the design budgeted."""
    with pytest.raises(ValueError, match="null"):
        rec(arm="natural", sites=sites(null_p=0.001))


def test_a_natural_arm_profile_is_valid_without_nulls():
    got = rec(arm="natural", sites=sites(null_p=None), n_rows=773, n_val=193,
              per_class=None)
    assert got.arm == "natural"


def test_density_must_be_one_the_experiment_actually_ran():
    with pytest.raises(ValueError, match="density"):
        rec(density=0.33)


def test_the_scored_1b_rows_are_admissible_densities():
    """0.50 is lubana_below (the consistency check) and 10.0 is lubana_above
    (the Stage A present row). Both are read by this experiment."""
    assert rec(system="lubana_below", density=0.50).density == 0.50
    assert rec(system="lubana_above", density=10.0).density == 10.0


def test_a_twin_may_not_claim_a_capability_metric():
    """An untrained network was never trained, so it has no eval_metric. A
    number here would silently enter the 'capability stays flat' half."""
    with pytest.raises(ValueError, match="capability"):
        rec(trained=False, capability_metric=0.09)


def test_save_and_load_uses_the_durable_unit(tmp_path):
    p = rec().save(tmp_path / "x.json")
    assert json.loads(p.read_text())["arm"] == "fixed"
    assert r.ProfileRecord.load(p).seed == 100
