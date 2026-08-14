"""Fixture suite for 1c's runner logic (design §4, §8).

The torch-dependent orchestration lives in run_profile.py; everything with a
decision in it lives here, in plain numpy, so it can be tested without a
checkpoint or a GPU. Three things are worth testing and are tested:

  - the stratified subsample, which is what makes n and class balance constant
    along the swept axis rather than adjusted for afterwards;
  - the checkpoint path, because reading the wrong step would silently answer
    a different question than the one preregistered;
  - the per-site probe, because the twin comparison is only valid if the cell
    and its twin are scored on the identical train/val split.
"""
import numpy as np
import pytest

from experiments.exp1c.run import profile_lib as pl


# ------------------------------------------------------ stratified subsample

def entity_class(n_per_class=90, n_classes=10):
    return np.repeat(np.arange(n_classes), n_per_class)


def test_subsample_takes_exactly_per_class_from_every_class():
    ec = entity_class()
    got = pl.stratified_subsample(np.arange(ec.size), ec, per_class=40, seed=1)
    assert got.size == 400
    _, counts = np.unique(ec[got], return_counts=True)
    assert set(counts) == {40}


def test_subsample_is_deterministic_so_a_cell_and_its_twin_share_rows():
    """The margin is a paired difference at the same site on the same data. A
    twin scored on different entities is not a floor, it is a second sample."""
    ec = entity_class()
    kw = dict(entity_class=ec, per_class=40, seed=7)
    a = pl.stratified_subsample(np.arange(ec.size), **kw)
    b = pl.stratified_subsample(np.arange(ec.size), **kw)
    assert np.array_equal(a, b)


def test_subsample_varies_with_seed():
    ec = entity_class()
    a = pl.stratified_subsample(np.arange(ec.size), ec, per_class=40, seed=1)
    b = pl.stratified_subsample(np.arange(ec.size), ec, per_class=40, seed=2)
    assert not np.array_equal(a, b)


def test_subsample_returns_entity_ids_not_positions():
    """The pool is a set of entity ids (singletons), not a dense range."""
    ents = np.array([5, 11, 12, 30, 31, 40, 41, 55])
    ec = np.array([0, 0, 0, 0, 1, 1, 1, 1])
    got = pl.stratified_subsample(ents, ec, per_class=2, seed=1)
    assert set(got.tolist()) <= set(ents.tolist())
    assert got.size == 4


def test_subsample_refuses_a_class_that_cannot_fill_the_quota():
    """40/class has ZERO margin at 0.85 p_c (design open item 3). The runner
    asserts the count rather than silently returning a smaller, unbalanced
    sample that would make n vary along the swept axis after all."""
    ec = np.repeat(np.arange(10), 39)
    with pytest.raises(ValueError, match="39"):
        pl.stratified_subsample(np.arange(ec.size), ec, per_class=40, seed=1)


# ---------------------------------------------------------- checkpoint paths

def test_sweep_checkpoint_path_matches_the_tree_run_lubana_wrote(tmp_path):
    got = pl.checkpoint_path("sweep", "10M", 100, step=10_000,
                             density=0.25, root=tmp_path)
    assert got == (tmp_path / "checkpoints" / "lubana_s3graph_0.25"
                   / "seed100" / "step_0010000.pt")


def test_the_1M_tier_carries_the_model_size_suffix(tmp_path):
    got = pl.checkpoint_path("sweep", "1M", 104, step=10_000,
                             density=0.85, root=tmp_path)
    assert got.parent.parent.name == "lubana_s3graph_0.85_m1M"


def test_stage_a_rows_read_their_own_checkpoint_trees(tmp_path):
    above = pl.checkpoint_path("lubana_above", "10M", 100, step=4516,
                               root=tmp_path)
    below = pl.checkpoint_path("lubana_below", "1M", 102, step=1234,
                               root=tmp_path)
    assert above.parent.parent.name == "lubana_above"
    assert above.name == "step_0004516.pt"
    assert below.parent.parent.name == "lubana_below_m1M"


def test_the_sweep_requires_a_density():
    with pytest.raises(ValueError, match="density"):
        pl.checkpoint_path("sweep", "10M", 100, step=10_000)


# ------------------------------------------------------------ the per-site probe

def acts_with_signal(n=400, d=32, n_classes=10, signal_layers=(2, 3), seed=0,
                     centre_scale=4.0):
    """Sites at `signal_layers` carry a linearly decodable class signal; the
    rest are noise of the same shape.

    `centre_scale` sets how separable the signal is. At 4.0 the probe scores
    exactly 1.000 on every split, which is what a saturated site looks like; a
    test that needs accuracy to RESPOND to the split must use a weaker
    separation (0.5 gives ~0.66-0.74 across splits).
    """
    rng = np.random.default_rng(seed)
    labels = np.repeat(np.arange(n_classes), n // n_classes)
    centres = rng.normal(0, centre_scale, size=(n_classes, d))
    out = {}
    for layer in (0, 1, 2, 3):
        for token in (1, -1):
            if layer in signal_layers:
                X = centres[labels] + rng.normal(0, 1.0, size=(n, d))
            else:
                X = rng.normal(0, 1.0, size=(n, d))
            out[(layer, token)] = X
    return out, labels


def test_probe_returns_one_result_per_site():
    acts, labels = acts_with_signal()
    got = pl.probe_sites(acts, labels, seed=1)
    assert len(got) == 8
    assert {(s.layer, s.token) for s in got} == {
        (l, t) for l in (0, 1, 2, 3) for t in (1, -1)}


def test_probe_reads_signal_where_it_was_planted_and_not_elsewhere():
    acts, labels = acts_with_signal(signal_layers=(2, 3))
    by = {(s.layer, s.token): s for s in pl.probe_sites(acts, labels, seed=1)}
    assert by[(2, 1)].accuracy > 0.90
    assert by[(3, -1)].accuracy > 0.90
    assert by[(0, 1)].accuracy < 0.25          # chance is 0.10
    assert by[(1, -1)].accuracy < 0.25


def test_the_natural_arm_carries_no_permutation_null():
    acts, labels = acts_with_signal()
    got = pl.probe_sites(acts, labels, seed=1, n_perm=None)
    assert all(s.null_p_raw is None for s in got)
    assert all(s.null_mean is None for s in got)


def test_the_fixed_arm_carries_an_uncorrected_null_per_site():
    """Records store RAW p; the Bonferroni family lives in analyze_1c so a
    fixture can test it. A pre-corrected p here would be corrected twice."""
    acts, labels = acts_with_signal()
    got = pl.probe_sites(acts, labels, seed=1, n_perm=50)
    assert all(0.0 < s.null_p_raw <= 1.0 for s in got)
    signal = next(s for s in got if (s.layer, s.token) == (2, 1))
    assert signal.null_p_raw == pytest.approx(1 / 51)


def test_every_site_is_scored_on_the_same_split():
    """A per-site split would make the eight accuracies incomparable and the
    mean-over-sites margin meaningless."""
    acts, labels = acts_with_signal()
    tr, va = pl.split_indices(len(labels), 0.25, seed=1)
    assert len(va) == 100 and len(tr) == 300
    assert set(tr).isdisjoint(va)
    # the probe reports the split it used, once, not once per site
    assert pl.probe_sites(acts, labels, seed=1, return_n_val=True)[1] == 100


def test_identical_features_at_different_sites_score_identically():
    """The teeth of the shared-split rule. Give three sites byte-identical
    features: under one shared partition they must return the same number. If
    each site drew its own split the accuracies would differ, the eight values
    would be incomparable, and the mean-over-sites margin would be an average
    over eight different experiments rather than one profile.

    Checking only n_val does NOT catch this — a per-site split has the right
    size every time. Neither does a SATURATED site: at the default separation
    the probe scores exactly 1.000 under every split, so identical accuracies
    are consistent with eight different partitions. The separation is weakened
    deliberately so that accuracy responds to the split. Both of those false
    negatives were found by mutation testing, which is why this test looks the
    way it does."""
    acts, labels = acts_with_signal(signal_layers=(2, 3), centre_scale=0.5)
    acts[(0, 1)] = acts[(2, 1)].copy()
    acts[(0, -1)] = acts[(2, 1)].copy()
    by = {(s.layer, s.token): s for s in pl.probe_sites(acts, labels, seed=1)}
    assert by[(0, 1)].accuracy == by[(2, 1)].accuracy
    assert by[(0, -1)].accuracy == by[(2, 1)].accuracy
    # in the responsive band: not at chance (0.10) and not saturated at 1.0
    assert 0.35 < by[(2, 1)].accuracy < 0.95


def test_probe_is_deterministic_under_a_fixed_seed():
    acts, labels = acts_with_signal()
    a = [s.accuracy for s in pl.probe_sites(acts, labels, seed=3, n_perm=20)]
    b = [s.accuracy for s in pl.probe_sites(acts, labels, seed=3, n_perm=20)]
    assert a == b
