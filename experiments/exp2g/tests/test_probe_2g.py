import numpy as np
import pytest

from experiments.exp2g import probe_2g as pg

K, N_TRAIN, N_EVAL, D, N_LAYERS = 5, 400, 200, 10, 7   # family {0,3,6} × 2


def _labels(rng, n):
    return [str(rng.integers(0, K)) for _ in range(n)]


def _acts(rng, y, *, site=None, strength=3.0):
    act = {}
    for layer in range(N_LAYERS):
        for slot in range(2):
            X = rng.normal(size=(len(y), D)).astype(np.float32)
            if (layer, slot) == site:
                for i, lab in enumerate(y):
                    X[i, int(lab)] += strength
            act[(layer, slot)] = X
    return act


@pytest.fixture(scope="module")
def synth():
    rng = np.random.default_rng(0)
    y_tr, y_ev = _labels(rng, N_TRAIN), _labels(rng, N_EVAL)
    from experiments.exp2f import probe_2f as pb
    return {"y_tr": y_tr, "y_ev": y_ev,
            "tr": pb.thin(_acts(rng, y_tr, site=(3, 1))),
            "ev": pb.thin(_acts(rng, y_ev, site=(3, 1))),
            "tw_tr": pb.thin(_acts(rng, y_tr)), "tw_ev": pb.thin(_acts(rng, y_ev))}


def test_cv_site_finds_the_encoding_site(synth):
    site, per_site, split = pg.cv_site(synth["tr"], synth["y_tr"])
    assert site == (3, 1) and per_site[pg.site_key((3, 1))] > 0.8
    assert split["seed"] == pg.CV_SEED and split["holdout_frac"] == pg.CV_HOLDOUT
    assert len(per_site) == 6


def test_scores_are_log_probs_of_the_true_label(synth):
    cell = pg.score_cell(synth["tr"], synth["y_tr"], synth["ev"], synth["y_ev"])
    assert cell["site"] == [3, 1] and cell["n"] == N_EVAL and cell["n_sites"] == 6
    s = np.asarray(cell["scores"])
    assert s.shape == (N_EVAL,) and np.all(s <= 0) and s.mean() > np.log(1 / K)
    assert cell["eval_acc"] > 0.8 and cell["eval_correct"] == round(cell["eval_acc"] * N_EVAL)
    assert cell["eval_rule"]["site"] == [3, 1]
    assert len(cell["pred"]) == N_EVAL


def test_twin_scores_are_uninformative(synth):
    cell = pg.score_cell(synth["tw_tr"], synth["y_tr"], synth["tw_ev"], synth["y_ev"])
    assert cell["eval_acc"] < 0.4
    assert abs(np.mean(cell["scores"]) - np.log(1 / K)) < 0.5


def test_missing_class_is_a_hard_error(synth):
    from experiments.exp2f import probe_2f as pb
    clf = pb.fit_probe(synth["tr"][(3, 1)], synth["y_tr"])
    with pytest.raises(ValueError):
        pg.item_log_probs(clf, synth["ev"][(3, 1)], ["99"] * N_EVAL)


def test_cv_tie_break_is_lowest_site():
    rng = np.random.default_rng(1)
    y = _labels(rng, 120)
    from experiments.exp2f import probe_2f as pb
    act = pb.thin(_acts(rng, y))          # nothing encoded: ties likely
    site, per_site, _ = pg.cv_site(act, y)
    best = max(per_site.values())
    cands = [k for k, v in per_site.items() if v == best]
    assert pg.site_key(site) == min(cands, key=lambda k: tuple(int(t) for t in k.strip("()").split(",")))
