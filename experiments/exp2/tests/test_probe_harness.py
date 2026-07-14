"""Probe-harness tests: position indexing against the real tokenizer, activation
storage round-trips, and the frozen probe module driven end-to-end on synthetic
activations — separable structure must fire, noise must not, shuffles must kill."""

import json

import numpy as np
import pytest

import run.run_probes as rp
from activations import (activations_path, load_activation_map, position_indices,
                         question_end_char, save_activations)
from battery.base import load_items, render_prompt
from probe_frozen import probe_below_threshold


def test_question_end_char_finds_final_cue():
    cap = load_items("add2")
    prompt = render_prompt(cap["eval_items"][0]["question"],
                           [tuple(s) for s in cap["shots"]])
    cut = question_end_char(prompt)
    assert prompt[cut:cut + 3] == "\nA:"
    assert prompt.rfind("Q: ") < cut  # cut is after the FINAL question


def test_position_indices_against_real_tokenizer():
    from models import load_tokenizer
    tok = load_tokenizer("410m")
    cap = load_items("mod7")
    for it in cap["probe_items"][:3]:
        prompt = render_prompt(it["question"], [tuple(s) for s in cap["shots"]])
        q_idx, p_idx = position_indices(tok, prompt)
        ids = tok(prompt, add_special_tokens=False)["input_ids"]
        assert p_idx == len(ids) - 1
        assert 0 < q_idx < p_idx
        # decoding from q_idx+1 onward must be exactly the answer cue
        assert tok.decode(ids[q_idx + 1:]) == "\nA:"


def _synthetic(n=240, d=24, separable=True, seed=0):
    """3 (layer, slot) candidates; candidate (1, 1) carries signal if separable."""
    rng = np.random.default_rng(seed)
    y = np.array([str(i % 3) for i in range(n)], dtype=object)
    X = rng.normal(size=(n, 2, 2, d)).astype(np.float16)
    if separable:
        for i in range(n):
            X[i, 1, 1, int(y[i])] += 4.0
    return {"X": X, "y": y}


def test_activation_npz_round_trip(tmp_path):
    arrays = _synthetic()
    path = tmp_path / "410m_trained" / "fake.npz"
    save_activations(path, arrays, {"size": "410m", "mode": "trained", "sha": "x" * 40})
    act, y, meta = load_activation_map(path)
    assert set(act.keys()) == {(0, 0), (0, 1), (1, 0), (1, 1)}
    assert act[(1, 1)].dtype == np.float32 and len(y) == 240
    assert meta["mode"] == "trained"


def test_frozen_probe_fires_on_separable_not_on_noise():
    # n_perm must give an achievable bar: add-one floor 1/(n_perm+1) x 4 Bonferroni
    # candidates must sit below alpha=.01 -> n_perm=500 gives floor ~.008.
    sep = _synthetic(separable=True)
    act = {(l, s): sep["X"][:, l, s, :].astype(np.float32) for l in range(2) for s in range(2)}
    r = probe_below_threshold(act, sep["y"], chance=1 / 3, checkpoint_id="t",
                              below_threshold=True, seed=0, n_perm=500)
    assert r.present and r.best_layer == 1 and r.best_token == 1

    noise = _synthetic(separable=False)
    act_n = {(l, s): noise["X"][:, l, s, :].astype(np.float32) for l in range(2) for s in range(2)}
    rn = probe_below_threshold(act_n, noise["y"], chance=1 / 3, checkpoint_id="t",
                               below_threshold=True, seed=0, n_perm=500)
    assert not rn.present


def test_normalized_margin_is_zero_below_the_bar():
    assert rp.normalized_margin({"null_p": 0.5, "accuracy": 0.9, "null_mean": 0.3}) == 0.0
    m = rp.normalized_margin({"null_p": 0.001, "accuracy": 0.65, "null_mean": 0.33})
    assert m == pytest.approx((0.65 - 0.33) / (1 - 0.33))


def test_fit_one_end_to_end_and_shuffle_kills_signal(tmp_path, monkeypatch):
    arrays = _synthetic(separable=True, seed=3)
    apath = tmp_path / "acts" / "410m_trained" / "fake.npz"
    save_activations(apath, arrays, {"size": "410m", "mode": "trained", "sha": "y" * 40})
    monkeypatch.setattr(rp, "activations_path", lambda size, mode, cap: apath)
    monkeypatch.setattr(rp, "probe_result_path",
                        lambda st, sz, c, s: tmp_path / "probes" / f"{st}_{sz}_{c}_{s}.json")
    monkeypatch.setattr(rp, "N_PERM", 500)  # floor 4/501=.008 < .01, fast in tests

    d = rp.fit_one("m3", "410m", "fake", seed=0)
    assert d["present"] and d["margin"] > 0.3

    ds = rp.fit_one("m2_shuffled", "410m", "fake", seed=0)
    assert not ds["present"] and ds["margin"] == 0.0

    # resumability: cached result returned verbatim
    again = rp.fit_one("m3", "410m", "fake", seed=0)
    assert again == d


def test_permutation_floor_clears_alpha_for_real_families():
    """Guard the arithmetic that bit the synthetic test: the add-one permutation
    floor times the Bonferroni family must clear alpha=.01 for BOTH real model
    depths under the ledgered family (stride-3 layers + final, x2 positions)."""
    for n_hidden in (25, 17):  # 410m: 24 layers + emb; 1b: 16 + emb
        keep = set(range(0, n_hidden, rp.LAYER_STRIDE)) | {n_hidden - 1}
        family = len(keep) * 2
        floor = family / (rp.N_PERM + 1)
        assert floor < 0.01, (n_hidden, family, floor)


def test_thin_layers_keeps_stride_and_final():
    act = {(l, s): np.zeros((4, 2)) for l in range(25) for s in range(2)}
    thinned = rp.thin_layers(act)
    layers = {l for l, _ in thinned.keys()}
    assert 24 in layers and 0 in layers and 1 not in layers
    assert len(thinned) == len(layers) * 2


def test_stage1_schema_matches_frozen_analyze():
    """analyze.py binds to {capability: {'probe_margin': float}} — pin the shape."""
    from analyze import analyze
    probe = {f"c{i}": {"probe_margin": i / 12} for i in range(12)}
    evals = {f"c{i}": {m: i / 24 for m in ("2.8b", "6.9b", "12b")} for i in range(12)}
    r = analyze(probe, evals, list(probe.keys()))
    assert r.verdict == "PASS" and r.n == 12
