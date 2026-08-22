"""probe_2f on synthetic activations: the site family (2c's thinning),
the eval-item probe against the floor with Bonferroni over the family,
the twin void rule, the CV secondary and the m3-reproduction gate's
arithmetic."""
import numpy as np
import pytest

from experiments.exp2f import probe_2f as pb

K = 10
N_TRAIN, N_EVAL, D, N_LAYERS = 600, 500, 12, 7   # 7 layers → family {0,3,6} × 2


def _labels(rng, n):
    return np.array([str(rng.integers(0, K)) for _ in range(n)])


def _acts(rng, y, *, encode_site=None, strength=3.0, d=D, n_layers=N_LAYERS):
    """{(layer, slot): [n, d]} noise everywhere; at `encode_site` the
    label's one-hot is added to the first K dims."""
    n = len(y)
    act = {}
    for layer in range(n_layers):
        for slot in range(2):
            X = rng.normal(size=(n, d)).astype(np.float32)
            if (layer, slot) == encode_site:
                for i, lab in enumerate(y):
                    X[i, int(lab)] += strength
            act[(layer, slot)] = X
    return act


@pytest.fixture(scope="module")
def synth():
    rng = np.random.default_rng(0)
    y_tr, y_ev = _labels(rng, N_TRAIN), _labels(rng, N_EVAL)
    site = (3, 1)
    return {
        "y_tr": y_tr, "y_ev": y_ev, "site": site,
        "tr_train": _acts(rng, y_tr, encode_site=site),
        "tr_eval": _acts(rng, y_ev, encode_site=site),
        "tw_train": _acts(rng, y_tr), "tw_eval": _acts(rng, y_ev),
        "res_train": _acts(rng, y_tr, encode_site=site),   # reservoir twin
        "res_eval": _acts(rng, y_ev, encode_site=site),
    }


def test_site_family_is_2cs_thinning():
    assert pb.site_family(7) == [(0, 0), (0, 1), (3, 0), (3, 1), (6, 0), (6, 1)]
    assert len(pb.site_family(25)) == 18 and len(pb.site_family(17)) == 14
    # equal to screen._thin_layers on a synthetic full map
    from experiments.exp2c.run import screen
    full = {(l, s): np.zeros((2, 2)) for l in range(17) for s in range(2)}
    assert sorted(screen._thin_layers(full)) == pb.site_family(17)
    assert pb.thin(full).keys() == set(pb.site_family(17))
    with pytest.raises(ValueError):
        pb.site_family(0)


def test_probe_constants_are_2bs():
    from experiments.exp2b import probe_starved as ps
    assert pb.C is ps.C and pb.MAX_ITER is ps.MAX_ITER and pb.ALPHA is ps.ALPHA


def test_eval_probe_detects_at_the_encoding_site(synth):
    s = synth
    sites = pb.site_family(N_LAYERS)
    per = pb.eval_probe_sites(s["tr_train"], s["y_tr"], s["tr_eval"], s["y_ev"],
                              sites)
    assert set(per) == set(sites)
    assert per[s["site"]]["acc"] > 0.8 and per[s["site"]]["n"] == N_EVAL
    assert all(per[k]["acc"] < 0.25 for k in sites if k != s["site"])
    det = pb.detect(per, floor=1 / K, alpha=pb.ALPHA)
    assert det["detected"] and det["best_site"] == list(s["site"])
    assert det["n_sites"] == len(sites)
    assert det["per_site"][str(s["site"])]["p_corrected"] == pytest.approx(
        min(1.0, det["per_site"][str(s["site"])]["p"] * len(sites)))
    assert det["best_acc"] == per[s["site"]]["acc"]


def test_detect_requires_bar_and_rate_above_floor():
    per = {(0, 0): {"acc": .09, "correct": 45, "n": 500},
           (0, 1): {"acc": .11, "correct": 55, "n": 500}}
    det = pb.detect(per, floor=.10, alpha=.01)
    assert not det["detected"]
    per2 = {(0, 0): {"acc": .20, "correct": 100, "n": 500},
            (0, 1): {"acc": .11, "correct": 55, "n": 500}}
    det2 = pb.detect(per2, floor=.10, alpha=.01)
    assert det2["detected"] and det2["best_site"] == [0, 0]
    # Bonferroni: a site that clears alpha raw but not ×n_sites is not detected
    per3 = {(l, s): {"acc": .10, "correct": 50, "n": 500}
            for l in range(9) for s in range(2)}
    per3[(3, 0)] = {"acc": .14, "correct": 70, "n": 500}   # raw p ≈ .002, ×18 ≈ .04
    det3 = pb.detect(per3, floor=.10, alpha=.01)
    assert not det3["detected"] and det3["per_site"]["(3, 0)"]["p"] < .01 \
        and det3["per_site"]["(3, 0)"]["p_corrected"] > .01


def test_probe_rung_clean_twin_is_not_void(synth):
    s = synth
    r = pb.probe_rung(s["tr_train"], s["y_tr"], s["tr_eval"], s["y_ev"],
                      s["tw_train"], s["tw_eval"], floor=1 / K)
    assert r["trained"]["detected"] and not r["twin_detects_at_best"]
    assert not r["void"] and r["trained_exceeds_twin_at_best"]
    assert r["D_probe"] is True
    assert r["twin"]["acc_at_trained_best"] < 0.25


def test_probe_rung_reservoir_twin_voids_the_cell(synth):
    s = synth
    r = pb.probe_rung(s["tr_train"], s["y_tr"], s["tr_eval"], s["y_ev"],
                      s["res_train"], s["res_eval"], floor=1 / K)
    assert r["trained"]["detected"] and r["twin_detects_at_best"]
    assert r["void"] and r["D_probe"] is None


def test_probe_rung_silent_is_not_detected(synth):
    s = synth
    r = pb.probe_rung(s["tw_train"], s["y_tr"], s["tw_eval"], s["y_ev"],
                      s["tw_train"], s["tw_eval"], floor=1 / K)
    assert not r["trained"]["detected"] and r["D_probe"] is False \
        and not r["void"]


def test_cv_secondary_reads_the_population(synth):
    s = synth
    cv = pb.cv_probe_sites(s["tr_train"], s["y_tr"], pb.site_family(N_LAYERS),
                           seed=0, holdout_frac=0.2)
    assert cv[s["site"]]["acc"] > 0.8 and cv[s["site"]]["n"] == 120
    assert cv["split"]["n_train"] == 480 and cv["split"]["seed"] == 0


def test_fit_is_deterministic(synth):
    s = synth
    a = pb.eval_probe_sites(s["tr_train"], s["y_tr"], s["tr_eval"], s["y_ev"],
                            [(3, 1)])
    b = pb.eval_probe_sites(s["tr_train"], s["y_tr"], s["tr_eval"], s["y_ev"],
                            [(3, 1)])
    assert a == b


def test_starved_accuracies_use_2bs_split():
    """The m3-reproduction gate's arithmetic: starved accuracies over
    the family under 2b's `starving_split`, best = 2c's tie rule
    (min corrected p, then max accuracy) — here with no null, the
    max-accuracy site."""
    from experiments.exp2b.splits import SplitParams
    rng = np.random.default_rng(1)
    n = 600
    bases = [(str(rng.integers(0, 30)),) for _ in range(n)]
    y = np.array([str(int(b[0]) % K) for b in bases])   # label from basis
    act = _acts(rng, y, encode_site=(3, 0), n_layers=4)
    out = pb.starved_accuracies(act, y, bases,
                                SplitParams(n_holdout=12, min_holdout_values=12, min_val_items=150),
                                seed=0)
    assert out["split"]["held_per_component"] == [12]
    assert out["n_val"] >= 150
    assert out["best_site"] == [3, 0] and out["accuracy"] > 0.8
    assert set(out["per_site"]) == {str(k) for k in pb.site_family(4)}


def test_void_reads_the_twin_at_the_trained_best_site_only(synth):
    """A twin that encodes the label at a DIFFERENT site than the
    trained model does not void the cell: the rule reads the twin at
    the trained model's best site, not at the twin's own best."""
    rng = np.random.default_rng(5)
    s = synth
    tw_train = _acts(rng, s["y_tr"], encode_site=(6, 0))
    tw_eval = _acts(rng, s["y_ev"], encode_site=(6, 0))
    r = pb.probe_rung(s["tr_train"], s["y_tr"], s["tr_eval"], s["y_ev"],
                      tw_train, tw_eval, floor=1 / K)
    assert r["trained"]["best_site"] == [3, 1] and r["twin"]["best_site"] == [6, 0]
    assert r["twin"]["detected"] and not r["twin_detects_at_best"]
    assert not r["void"] and r["D_probe"] is True


def test_min_detectable_acc_is_printed_and_brute_force_equal():
    from experiments.exp2d import stats_2d as st
    m = pb.min_detectable_acc(500, .12, .01, 18)
    ks = [k for k in range(501) if st.binomial_bar(k, 500, .12, .01)["p"] * 18 < .01]
    assert m == min(ks) / 500 and m == pytest.approx(.172)
    assert pb.min_detectable_acc(500, .132, .01, 14) == pytest.approx(.184)
    per = {(0, 0): {"acc": .10, "correct": 50, "n": 500}}
    det = pb.detect(per, floor=.10, alpha=.01)
    assert det["min_detectable_acc"] == pb.min_detectable_acc(500, .10, .01, 1)
