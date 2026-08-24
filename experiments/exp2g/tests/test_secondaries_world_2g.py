# experiments/exp2g/tests/test_secondaries_world_2g.py
"""The with_2d_secondaries world (final-review parked item): the three
2d-derived secondaries (sampler_competitor, probe_beyond_sampler,
exclude_1b_performable) computed on the real 2d tree against a
synthetic FORECAST predictor/sweep, and non-gating when the 2d tree
is unreachable."""
from __future__ import annotations

from experiments.exp2g import analyze_2g as an
from experiments.exp2g.tests import full_shape as fs

_N_REMOVED = {"antonym": 87, "antonym6": 89, "add_base8": 4, "sub_base8": 8,
              "add3_mid": 1, "sub3_mid": 0, "arith_next": 19}


def test_with_2d_secondaries_on_the_real_tree(tmp_path):
    seal = fs.write_world(tmp_path, assoc=0.8)
    v = an.run(root=tmp_path, n_perm=100, n_boot=20, with_2d_secondaries=True, **seal)
    assert v["verdict"] == "FORECAST"
    sec = v["secondaries"]
    assert sec["failures"] == []
    for name in ("sampler_competitor", "probe_beyond_sampler", "exclude_1b_performable"):
        assert "failed" not in sec[name]
    assert sec["exclude_1b_performable"]["n_removed"] == _N_REMOVED


def test_with_2d_secondaries_non_gating_on_a_broken_d2_root(tmp_path):
    seal = fs.write_world(tmp_path, assoc=0.8)
    v = an.run(root=tmp_path, n_perm=100, n_boot=20, with_2d_secondaries=True,
              d2_root=tmp_path / "nonexistent", **seal)
    assert v["verdict"] == "FORECAST"
    assert v["primary"]["stratified"]["p"] < 0.01
    sec = v["secondaries"]
    for name in ("sampler_competitor", "probe_beyond_sampler", "exclude_1b_performable"):
        assert "failed" in sec[name]
    assert sec["failures"]
