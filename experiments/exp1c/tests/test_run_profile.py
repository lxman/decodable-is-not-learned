"""Integration tests for 1c's profile runner.

These build a real language and a real model and run a real probe. Only the
TWIN path is exercised, because a twin needs no checkpoint — which is also why
design §8 runs the twins first. The trained path differs from it by one
`load_state_dict`, and its checkpoint mapping is unit-tested in
test_profile_lib.py.
"""
import pytest

from experiments.exp1c import records as r
from experiments.exp1c.run import run_profile as rp


def test_a_natural_arm_twin_runs_end_to_end(tmp_path):
    rec = rp.run_profile("sweep", "natural", 0.25, "1M", 100, trained=False,
                         out_root=tmp_path)
    assert isinstance(rec, r.ProfileRecord)
    assert len(rec.sites) == 8
    assert all(s.null_p_raw is None for s in rec.sites)
    assert rec.capability_metric is None
    assert rec.per_class is None
    # 0.25 p_c has ~866 singletons; the natural arm takes the pool as it is
    assert 800 < rec.n_rows < 900


def test_a_fixed_arm_twin_probes_the_stratified_four_hundred(tmp_path):
    rec = rp.run_profile("sweep", "fixed", 0.85, "1M", 100, trained=False,
                         out_root=tmp_path, n_perm=8)
    assert rec.n_rows == 400
    assert rec.per_class == 40
    assert rec.n_val == 100
    assert all(0.0 < s.null_p_raw <= 1.0 for s in rec.sites)


def test_the_record_lands_where_the_loader_looks(tmp_path):
    from experiments.exp1c import analyze_1c as a
    rp.run_profile("sweep", "natural", 0.45, "1M", 101, trained=False,
                   out_root=tmp_path)
    got = a.load_profiles(tmp_path, arm="natural")
    assert len(got) == 1 and got[0].seed == 101


def test_the_runner_is_resumable_and_skips_an_existing_record(tmp_path):
    """Design §9: durable, resumable, one JSON per cell. A campaign that
    recomputes finished cells cannot be restarted safely."""
    first = rp.run_profile("sweep", "natural", 0.45, "1M", 102, trained=False,
                           out_root=tmp_path)
    path = r.record_path(tmp_path, "sweep", "natural", 0.45, "1M", 102, False)
    mtime = path.stat().st_mtime_ns
    again = rp.run_profile("sweep", "natural", 0.45, "1M", 102, trained=False,
                           out_root=tmp_path)
    assert path.stat().st_mtime_ns == mtime
    assert again.to_dict() == r.ProfileRecord.load(path).to_dict()
    assert ([s.accuracy for s in again.sites]
            == [s.accuracy for s in first.sites])


def test_a_reloaded_record_is_not_dict_equal_to_the_fresh_one():
    """Pinned deliberately. exp1's config carries tuples (s3_graph_points),
    and JSON has no tuple, so a fresh record and its reload never compare
    equal even though every measured quantity matches. Anything that compares
    whole records for provenance must compare the SAVED json, not the object —
    a resume check written the naive way would recompute every finished cell."""
    import json

    a = r.ProfileRecord(
        system="sweep", arm="natural", density=0.25, size_bucket="1M",
        seed=100, trained=False,
        sites=[r.SiteResult(layer=l, token=t, accuracy=0.1)
               for l in (0, 1, 2, 3) for t in (1, -1)],
        n_rows=800, n_val=200, per_class=None, capability_metric=None,
        git_sha="abc1234", config={"points": (0.25, 0.45)})
    b = r.ProfileRecord.from_json(a.to_json())
    assert b.to_dict() != a.to_dict()
    assert json.loads(b.to_json()) == json.loads(a.to_json())


def test_a_cell_and_its_twin_are_scored_on_identical_rows(tmp_path):
    """The margin is a paired difference. Two runs at the same (density, size,
    seed) must select the same entities regardless of trained/twin."""
    a1 = rp.probe_pool("sweep", "fixed", 0.65, 100)
    a2 = rp.probe_pool("sweep", "fixed", 0.65, 100)
    assert list(a1) == list(a2)
    assert len(a1) == 400


def test_the_sweep_refuses_a_density_it_never_trained(tmp_path):
    with pytest.raises(ValueError, match="density"):
        rp.run_profile("sweep", "natural", 0.33, "1M", 100, trained=False,
                       out_root=tmp_path)
