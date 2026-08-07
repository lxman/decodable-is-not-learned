"""M2 campaign runner: battery-set arithmetic, the shuffled-labels
ordering contract, and the cross-tree entity_track import hygiene.
Model/collection paths are exercised by the campaign itself (2b
pattern: correctness gate on those is code review + the resumable
log), never by unit tests."""

import numpy as np

from experiments.exp2c.run import campaign_m2 as m2
from experiments.exp2c.run import screen


def test_new_pool_is_22_and_excludes_carried_and_dead():
    rungs = m2.new_pool_rungs()
    assert len(rungs) == 22
    # the 12 reused survivors carry from 2b — never refit here
    assert not (set(rungs) & m2.survivors())
    # screen/M1 rejections and the gate control are not scored rungs
    for dead in ("base12", "letter_sum", "letter_prod", "hamming8",
                 "ctrl_copy"):
        assert dead not in rungs
    # spot checks across the pool
    for alive in ("base12_digitsum", "mod17", "hamming12", "roman_sum7",
                  "antonym6", "odd6"):
        assert alive in rungs


def test_stage_caps():
    assert m2.stage_caps("known_present") == ["entity_track", "ctrl_copy"]
    assert m2.stage_caps("m3") == m2.new_pool_rungs()
    assert m2.stage_caps("shuffled") == m2.new_pool_rungs()


def test_shuffled_labels_ordering_contract():
    """Split from TRUE labels; only the fit labels permuted; rng(1000+seed)."""
    y = np.array([f"c{i % 6}" for i in range(300)], dtype=object)
    split_labels, y_perm = m2.shuffled_labels(y, seed=3)
    assert split_labels is y                       # the true labels, unpermuted
    assert sorted(y_perm) == sorted(y)             # a permutation
    assert not np.array_equal(y_perm, y)           # actually shuffled
    ref = np.random.default_rng(1003).permutation(y)
    assert np.array_equal(y_perm, ref)             # the canonical stream
    again = m2.shuffled_labels(y, seed=3)[1]
    assert np.array_equal(y_perm, again)           # deterministic


def test_probe_result_path_matches_campaign_format():
    p = m2.probe_result_path("m3", "410m", "mod17", 2)
    assert p.name == "410m_mod17_seed2.json"
    assert p.parent.name == "m3"
    assert p.parent.parent.name == "probes"


def test_entity_track_split_params_and_battery_cache_hygiene():
    sp = m2._entity_track_split_params()
    assert type(sp).__name__ == "SplitParams"
    # the cross-tree import must not poison exp2c's own battery modules:
    # screen's split-plan lookup for a 2c rung still resolves afterward
    sp2c = screen._split_plan("mod17")
    assert type(sp2c).__name__ == "SplitParams"
