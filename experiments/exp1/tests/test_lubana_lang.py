"""M5 unit tests for the Lubana formal-language task.

Pin the structural guarantees the percolation ground truth rests on: the graph is
within-class only, fragmented below p_c and connected above; sentences respect type
constraints; queries are answerable only via class structure.
"""

import numpy as np
import pytest
import torch

from tasks.lubana_lang import LubanaConfig, LubanaLanguage


def _lang(mult, seed=0, **kw):
    kw.setdefault("n_classes", 5)
    kw.setdefault("n_entities", 100)
    kw.setdefault("n_properties", 1000)
    return LubanaLanguage(LubanaConfig(edge_prob_mult=mult, seed=seed, **kw))


# ---- graph structure ---------------------------------------------------------

def test_edges_are_within_class_only():
    lang = _lang(10.0)
    e_idx, k_idx = np.nonzero(lang.adj)
    assert (lang.entity_class[e_idx] == lang.prop_class[k_idx]).all()


def test_threshold_formula():
    cfg = LubanaConfig(n_classes=5, n_entities=100, n_properties=1000, edge_prob_mult=1.0)
    assert cfg.p_c == pytest.approx(1.0 / np.sqrt(20 * 200))
    assert cfg.edge_prob == pytest.approx(cfg.p_c)


def test_above_threshold_has_giant_component():
    stats = _lang(10.0).giant_component_stats()
    assert stats["giant_frac_min"] > 0.3   # a macroscopic component in every class


def test_below_threshold_is_fragmented():
    stats = _lang(0.5).giant_component_stats()
    assert stats["giant_frac_mean"] < 0.1  # only microscopic islands


def test_gt_certification_separates_settings():
    """The independent gt-check (graph connectivity) must separate below from above
    by a wide margin — this is what 'known by construction' means operationally."""
    above = _lang(10.0).giant_component_stats()["giant_frac_mean"]
    below = _lang(0.5).giant_component_stats()["giant_frac_mean"]
    assert above > 3 * below


# ---- sentences ---------------------------------------------------------------

def test_sentences_respect_type_constraints():
    lang = _lang(10.0)
    cfg = lang.cfg
    rng = np.random.default_rng(1)
    checked = 0
    for _ in range(100):
        s = lang.sample_sentence(rng)
        if s is None:
            continue
        ents = [t for t in s if t < cfg.n_entities]
        subj = ents[0]
        # every property token in the sentence is owned by SOME entity in it
        # (descriptors/verbs bind to subject or the adjacent entity)
        for t in s:
            if cfg.n_entities <= t < cfg.n_entities + cfg.n_properties:
                k = t - cfg.n_entities
                assert any(lang.adj[e, k] for e in ents), "unowned property in sentence"
                checked += 1
    assert checked > 50  # the check actually exercised properties


def test_sentences_fit_max_len_and_use_valid_tokens():
    lang = _lang(10.0)
    cfg = lang.cfg
    rng = np.random.default_rng(2)
    for _ in range(50):
        s = lang.sample_sentence(rng)
        if s is None:
            continue
        assert len(s) + 1 <= cfg.max_len
        assert all(0 <= t < cfg.bos for t in s)  # no BOS/PAD inside a sentence


def test_corpus_shapes():
    lang = _lang(10.0)
    cfg = lang.cfg
    ids = lang.make_corpus(50, seed=3)
    assert ids.shape == (50, cfg.max_len)
    assert (ids[:, 0] == cfg.bos).all()


def test_below_threshold_corpus_still_generates():
    """Sparse graphs make many symbolic drafts unsatisfiable; generation must still
    terminate and produce type-valid sentences from the islands that exist."""
    lang = _lang(0.5)
    ids = lang.make_corpus(20, seed=4)
    assert ids.shape[0] == 20


def test_online_batches_are_fresh_and_valid():
    lang = _lang(10.0)
    cfg = lang.cfg
    rng = np.random.default_rng(11)
    b1 = lang.sample_batch(8, rng)
    b2 = lang.sample_batch(8, rng)
    assert b1.shape == (8, cfg.max_len) and (b1[:, 0] == cfg.bos).all()
    assert not torch.equal(b1, b2)  # fresh data every call


# ---- holdout (construction-level; makes queries stable under online data) -----

def test_reserved_edges_never_bound_in_generation():
    """The holdout invariant: a reserved (e,k) pair is never SYNTACTICALLY BOUND in
    training (Desc/Verb bind to the subject; eAdj binds to the following entity).
    Incidental co-occurrence with another entity's property is allowed — that shared
    context is precisely the class signal the capability learns from (as in the
    paper's multi-entity strings); the verifier tests binding, not co-occurrence."""
    lang = _lang(10.0, n_entities=50, n_properties=500)
    cfg = lang.cfg
    assert lang.reserved.sum() > 0            # holdout is non-empty
    assert not (lang.reserved & lang.trainable).any()
    rng = np.random.default_rng(12)
    checked = 0
    for _ in range(300):
        s = lang.sample_sentence(rng)
        if s is None:
            continue
        subj = next(t for t in s if t < cfg.n_entities)
        for i, t in enumerate(s):
            if cfg.n_entities <= t < cfg.n_entities + cfg.n_properties:
                k = t - cfg.n_entities
                # bound entity: the entity that immediately follows (eAdj slot), else
                # the subject (Desc/Verb slots)
                nxt = s[i + 1] if i + 1 < len(s) else None
                bound = nxt if (nxt is not None and nxt < cfg.n_entities) else subj
                assert lang.trainable[bound, k], "reserved/non-edge pair was bound"
                assert not lang.reserved[bound, k]
                checked += 1
    assert checked > 100


# ---- queries (the scored capability) ------------------------------------------

def test_queries_mask_is_never_trainable_by_construction():
    lang = _lang(10.0)
    cfg = lang.cfg
    q = lang.make_queries(20, seed=6)
    assert q["prompts"].shape == (20, 3)
    for i in range(20):
        e = int(q["subjects"][i])
        cand = torch.nonzero(q["masks"][i]).flatten().tolist()
        assert cand, "empty candidate set"
        for t in cand[:100]:
            k = t - cfg.n_entities
            assert lang.prop_is_desc[k]
            assert not lang.trainable[e, k]   # can NEVER appear with e in training


def test_verifier_accepts_same_class_rejects_cross_class():
    lang = _lang(10.0)
    cfg = lang.cfg
    q = lang.make_queries(10, seed=8)
    for i in range(10):
        c = int(q["classes"][i])
        cand = torch.nonzero(q["masks"][i]).flatten().numpy()
        same = [t for t in cand if lang.prop_class[t - cfg.n_entities] == c]
        cross = [t for t in cand if lang.prop_class[t - cfg.n_entities] != c]
        if same:
            assert lang.verify_choice(i, q, int(same[0])) is True
        if cross:
            assert lang.verify_choice(i, q, int(cross[0])) is False
    assert lang.chance == pytest.approx(1 / 5)


def test_chance_matches_candidate_composition():
    """Empirical same-class fraction among candidates ~ 1/|C| (the chance floor)."""
    lang = _lang(10.0)
    cfg = lang.cfg
    q = lang.make_queries(30, seed=10)
    fracs = []
    for i in range(30):
        c = int(q["classes"][i])
        cand = torch.nonzero(q["masks"][i]).flatten().numpy()
        same = sum(1 for t in cand if lang.prop_class[t - cfg.n_entities] == c)
        fracs.append(same / len(cand))
    assert np.mean(fracs) == pytest.approx(1 / 5, abs=0.03)
