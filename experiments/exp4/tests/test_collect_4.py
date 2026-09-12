# experiments/exp4/tests/test_collect_4.py
"""Task 3's per-load pipeline, cold: FakeModel/FakeTokenizer (no torch
model contact, no network) exercise render/positions/collect/set-table/
overlap/align/write+re-read/ref-table-load. Real item files (2d's
committed battery) back the render test only — everything touching a
model uses `fakes_4`."""
from __future__ import annotations

import json

import numpy as np
import pytest

from experiments.exp2d import battery_2d as bt
from experiments.exp4 import battery_4
from experiments.exp4 import collect_4 as c4
from experiments.exp4 import metric_4
from experiments.exp4.tests import fakes_4


def _tiny_cap(n=6, prefix="q"):
    return {"shots": [["1+1?", "2"], ["2+2?", "4"]],
           "eval_items": [{"question": f"{prefix}{i}", "answer": str(i)} for i in range(n)]}


# --------------------------------------------------------------- render

def test_render_prompts_4_plain_on_real_item_file():
    cap = bt.load_item_file("antonym")
    prompts = c4.render_prompts_4("pythia", cap)
    assert len(prompts) == 500
    assert all(p.endswith("\nA:") for p in prompts)
    assert not prompts[0].startswith(battery_4.bn.BOS_TOKEN_2N)


def test_render_prompts_4_comma_prefixes_bos():
    cap = bt.load_item_file("antonym")
    prompts = c4.render_prompts_4("comma", cap)
    assert len(prompts) == 500
    assert all(p.endswith("\nA:") for p in prompts)
    assert all(p.startswith(battery_4.bn.BOS_TOKEN_2N) for p in prompts)


def test_positions_4_matches_screen():
    from experiments.exp2c.run import screen
    cap = _tiny_cap(3)
    tok = fakes_4.FakeTokenizer()
    prompts = c4.render_prompts_4("pythia", cap)
    got = c4.positions_4(tok, prompts)
    want = [screen._position_indices(tok, p) for p in prompts]
    assert got == want


# ------------------------------------------------------------- collect

def test_collect_rung_4_shapes_and_determinism_and_device_independence():
    cap = _tiny_cap(5)
    n_hidden, d = 7, 8
    sites = metric_4.sites_4(n_hidden)
    model = fakes_4.FakeModel(seed=1, n_hidden=n_hidden, d=d)
    tok = fakes_4.FakeTokenizer()

    out1 = c4.collect_rung_4(model, tok, "pythia", cap, sites=sites, batch_size=2, device="mps")
    out2 = c4.collect_rung_4(model, tok, "pythia", cap, sites=sites, batch_size=2, device="cpu")

    assert out1["X"].shape == (5, len(sites), 2, d)
    assert out1["P"].shape == (5, len(sites), d)
    assert out1["X"].dtype == np.float16
    assert out1["P"].dtype == np.float16
    assert np.array_equal(out1["X"], out2["X"])
    assert np.array_equal(out1["P"], out2["P"])


def test_collect_rung_4_pooled_mean_excludes_padded_tokens():
    # Task 5 mutation harness: `_tiny_cap`'s items are same-length
    # after rendering, so padding never fires and a dropped attention
    # mask goes unnoticed. Two items of very different QUESTION length
    # (single char vs. ten) render to very different token counts, so
    # the shorter one is genuinely right-padded; FakeModel's layer-0
    # state for the pad token id (0) is a real, nonzero, distinct
    # embedding row, so an unmasked mean would differ measurably from
    # the masked one -- cross-checked here against a by-hand
    # recomputation using ONLY the true (non-padded) token positions.
    cap = {"shots": [], "eval_items": [{"question": "a", "answer": "x"},
                                       {"question": "b" * 10, "answer": "y"}]}
    n_hidden, d = 7, 8
    sites = metric_4.sites_4(n_hidden)
    model = fakes_4.FakeModel(seed=3, n_hidden=n_hidden, d=d)
    tok = fakes_4.FakeTokenizer()

    prompts = c4.render_prompts_4("pythia", cap)
    lengths = [len(tok._ids(p)) for p in prompts]
    assert lengths[0] != lengths[1], "the two prompts must render to different lengths"

    out = c4.collect_rung_4(model, tok, "pythia", cap, sites=sites, batch_size=2, device="mps")

    for item_idx, prompt in enumerate(prompts):
        ids = np.array(tok._ids(prompt), dtype=np.int64) % model.vocab_size
        for site_pos, layer in enumerate(sites):
            hs = model._embed[ids] * (layer + 1) + model._offsets[layer]   # [T, d], every token
            want = hs.mean(axis=0).astype(np.float16)          # the MASKED mean == every real token
            got = out["P"][item_idx, site_pos, :]
            assert np.allclose(got.astype(np.float32), want.astype(np.float32), atol=1e-3), \
                (item_idx, layer)


def test_collect_rung_4_wrong_batch_size_raises(monkeypatch):
    cap = _tiny_cap(4)
    sites = metric_4.sites_4(7)
    model = fakes_4.FakeModel(seed=2, n_hidden=7, d=8)
    tok = fakes_4.FakeTokenizer()
    monkeypatch.setitem(battery_4.BATCH_4, "unit-test-key", 32)
    with pytest.raises(ValueError, match="batch_size"):
        c4.collect_rung_4(model, tok, "pythia", cap, sites=sites, batch_size=16, device="mps",
                          key="unit-test-key")
    # the pinned value is accepted
    out = c4.collect_rung_4(model, tok, "pythia", cap, sites=sites, batch_size=32, device="mps",
                            key="unit-test-key")
    assert out["X"].shape[0] == 4


# ---------------------------------------------------------- set tables

def test_non_pythia_refs_4_excludes_pythia():
    refs = c4.non_pythia_refs_4()
    assert "ref_pythia_12b" not in refs
    assert set(refs) == set(battery_4.REFERENCES_4) - {"ref_pythia_12b"}
    assert len(refs) == 3


def test_family_of_traj_4_matches_family_of_key():
    for traj, want in (("pythia_2.8b", "pythia"), ("olmo2_7b", "olmo2"),
                       ("smollm3_3b", "smollm3"), ("comma_7b", "comma")):
        assert c4.family_of_traj_4(traj) == want


def test_set_tables_4_shape_dtype():
    n, n_sites, d = 6, 3, 5
    rng = np.random.default_rng(0)
    X = rng.standard_normal((n, n_sites, 2, d)).astype(np.float16)
    sets = c4.set_tables_4(X, k=2)
    assert sets.shape == (n_sites, 2, n, 2)
    assert sets.dtype == np.uint16


def test_pooled_sets_4_shape_dtype():
    n, n_sites, d = 6, 3, 5
    rng = np.random.default_rng(0)
    P = rng.standard_normal((n, n_sites, d)).astype(np.float16)
    pooled = c4.pooled_sets_4(P, k=2)
    assert pooled.shape == (n_sites, n, 2)
    assert pooled.dtype == np.uint16


def test_global_sets_4_order_is_rungs_by_item():
    rng = np.random.default_rng(0)
    r0, r1 = battery_4.RUNGS[3], battery_4.RUNGS[1]   # deliberately out of RUNGS order
    n_sites, d = 2, 4
    X_by_rung = {
        r0: rng.standard_normal((3, n_sites, 2, d)).astype(np.float16),
        r1: rng.standard_normal((4, n_sites, 2, d)).astype(np.float16),
    }
    sets, order = c4.global_sets_4(X_by_rung, k=2)
    assert sets.shape == (n_sites, 7, 2)
    want_order = [(r1, i) for i in range(4)] + [(r0, i) for i in range(3)]
    assert order == want_order


# -------------------------------------------------------------- overlap

def test_overlap_table_4_matches_metric_4_overlap_counts_per_site():
    rng = np.random.default_rng(0)
    sets_m = rng.integers(0, 20, size=(2, 6, 3)).astype(np.uint16)
    sets_q = rng.integers(0, 20, size=(2, 6, 3)).astype(np.uint16)
    pairing = [1, 0]
    got = c4.overlap_table_4(sets_m, sets_q, pairing)
    assert got.shape == (2, 6)
    assert got.dtype == np.uint8
    assert np.array_equal(got[0], metric_4.overlap_counts(sets_m[0], sets_q[1]))
    assert np.array_equal(got[1], metric_4.overlap_counts(sets_m[1], sets_q[0]))


def test_overlap_table_4_pairing_length_mismatch_raises():
    sets_m = np.zeros((2, 4, 3), dtype=np.uint16)
    sets_q = np.zeros((2, 4, 3), dtype=np.uint16)
    with pytest.raises(ValueError, match="pairing"):
        c4.overlap_table_4(sets_m, sets_q, [0])


# ------------------------------------------------------------ alignment

def test_align_scalars_4_keys():
    n_sites, n, k, d = 2, 6, 3, 4
    rng = np.random.default_rng(0)
    sets_m_pos = {"question_end": rng.integers(0, n, size=(n_sites, n, k)).astype(np.uint16),
                 "prompt_end": rng.integers(0, n, size=(n_sites, n, k)).astype(np.uint16)}
    sets_m_pooled = rng.integers(0, n, size=(n_sites, n, k)).astype(np.uint16)
    X_m = rng.standard_normal((n, n_sites, d)).astype(np.float32)
    ref_sets_pe = rng.integers(0, n, size=(n_sites, n, k)).astype(np.uint16)
    ref_sets_qe = rng.integers(0, n, size=(n_sites, n, k)).astype(np.uint16)
    ref_sets_pool = rng.integers(0, n, size=(n_sites, n, k)).astype(np.uint16)
    ref_act = rng.standard_normal((n, n_sites, d)).astype(np.float32)
    refs = {"ref_x": {"sets_prompt_end": ref_sets_pe, "sets_question_end": ref_sets_qe,
                      "sets_pooled": ref_sets_pool, "activations_prompt_end": ref_act,
                      "sites_q": [5, 15]},
           "ref_y": {"sets_prompt_end": ref_sets_pe, "sets_question_end": None,
                      "sets_pooled": None, "activations_prompt_end": None, "sites_q": [5, 15]}}
    pairing_by_ref = {"ref_x": [0, 1], "ref_y": [1, 0]}

    got = c4.align_scalars_4(sets_m_pos, sets_m_pooled, X_m, refs, pairing_by_ref, k=k,
                             sites_m=[10, 20])

    assert set(got) == {"ref_x", "ref_y"}
    want_keys = {"knn_prompt_end", "knn_question_end", "knn_pooled",
                "knn_max_over_pairs_prompt_end", "knn_max_over_pairs_pooled",
                "knn_argmax_pair_prompt_end", "knn_argmax_pair_pooled", "cka_prompt_end"}
    assert set(got["ref_x"]) == want_keys
    assert len(got["ref_x"]["knn_prompt_end"]) == n_sites
    assert got["ref_x"]["cka_prompt_end"] is not None and len(got["ref_x"]["cka_prompt_end"]) == n_sites
    assert got["ref_x"]["knn_argmax_pair_prompt_end"][0] in (10, 20)
    assert got["ref_x"]["knn_argmax_pair_prompt_end"][1] in (5, 15)
    assert got["ref_x"]["knn_argmax_pair_pooled"][0] in (10, 20)
    assert got["ref_x"]["knn_argmax_pair_pooled"][1] in (5, 15)
    assert got["ref_y"]["knn_question_end"] is None
    assert got["ref_y"]["knn_pooled"] is None
    assert got["ref_y"]["knn_max_over_pairs_pooled"] is None
    assert got["ref_y"]["knn_argmax_pair_pooled"] is None
    assert got["ref_y"]["cka_prompt_end"] is None
    assert got["ref_y"]["knn_prompt_end"] is not None
    assert got["ref_y"]["knn_max_over_pairs_prompt_end"] is not None
    assert got["ref_y"]["knn_argmax_pair_prompt_end"] is not None


def test_align_scalars_4_max_over_pairs_is_the_full_cross_product_not_the_depth_matched_pair():
    """Fix round 1, finding 2: hand-built so the depth-matched pairing
    (m-site0<->q-site0, m-site1<->q-site1, both by construction the
    WORST pair — overlap 0) disagrees with the true best pair (the
    off-diagonal one, overlap = k on every item). The old formula
    (max over ITEMS of the depth-matched per-item overlap, then mean)
    would read 0.0 here; the fixed formula (Huh's full cross-product
    max of the per-pair MEAN) reads 1.0 and names the winning pair by
    hidden-state LAYER INDEX, not array position."""
    k, n = 2, 4
    m0 = np.tile(np.array([2, 3], dtype=np.uint16), (n, 1))
    m1 = np.tile(np.array([0, 1], dtype=np.uint16), (n, 1))
    q0 = np.tile(np.array([0, 1], dtype=np.uint16), (n, 1))
    q1 = np.tile(np.array([2, 3], dtype=np.uint16), (n, 1))
    sets_m_prompt_end = np.stack([m0, m1])   # [2, n, k]
    sets_q_prompt_end = np.stack([q0, q1])   # [2, n, k]
    sets_m_pos = {"question_end": sets_m_prompt_end, "prompt_end": sets_m_prompt_end}
    pairing_by_ref = {"ref_x": [0, 1]}       # depth-matched: m0<->q0, m1<->q1 (both overlap 0)
    refs = {"ref_x": {"sets_prompt_end": sets_q_prompt_end, "sets_question_end": None,
                      "sets_pooled": None, "activations_prompt_end": None, "sites_q": [0, 10]}}

    got = c4.align_scalars_4(sets_m_pos, None, None, refs, pairing_by_ref, k=k, sites_m=[0, 10])

    # the depth-matched (primary) reading really is 0.0 on both sites —
    # confirms the scenario is genuinely adversarial to the old formula
    assert got["ref_x"]["knn_prompt_end"] == [0.0, 0.0]
    # the fixed full-cross-product maximum finds the off-diagonal pair
    assert got["ref_x"]["knn_max_over_pairs_prompt_end"] == pytest.approx(1.0)
    assert got["ref_x"]["knn_argmax_pair_prompt_end"] == [0, 10]


# ------------------------------------------------- IMPORTANT 4 (peak load)

def _tiny_battery_34(n=12):
    """All 34 rungs (`process_model_4` loops over them unconditionally)
    with 12 varied items each — k=10 needs n > k."""
    import random
    words = ["cat", "dog", "blue", "fast", "moon", "tree", "gold", "iron", "leaf", "wave",
             "frost", "spark", "amber", "cliff", "delta", "ember"]
    battery = {}
    for r in battery_4.RUNGS:
        rng = random.Random(r)
        battery[r] = {
            "shots": [["amber cliff quartz willow", "2"], ["delta ember frost spark", "4"]],
            "eval_items": [{"question": " ".join(rng.choice(words) for _ in range(4)) + f" {i}",
                           "answer": str(i)} for i in range(n)]}
    return battery


def test_process_model_4_releases_the_model_before_the_bank_and_records_numpy(tmp_path,
                                                                             monkeypatch):
    """Final review IMPORTANT 4: stage 1's first load is the memory and
    time peak — the weights must go after the LAST FORWARD PASS and
    before the 17,000-row global bank and the write, not when the
    caller's `finally` runs. And the record must name numpy, since
    gate 1's npz byte-identity requirement rests on numpy's zip
    writer."""
    events = []
    real_bank, real_write = c4.global_sets_4, c4.write_load_4

    def spy_bank(X_by_rung, k=metric_4.K_4):
        events.append("bank")
        return real_bank(X_by_rung, k=k)

    def spy_write(*a, **kw):
        events.append("write")
        return real_write(*a, **kw)

    monkeypatch.setattr(c4, "global_sets_4", spy_bank)
    monkeypatch.setattr(c4, "write_load_4", spy_write)

    key = "ref_pythia_12b"
    model = fakes_4.FakeModel(seed=3, n_hidden=7, d=8)
    tok = fakes_4.FakeTokenizer()
    info = {"n_hidden": 7, "tensor_digest": "digest", "commit": "c", "revision": "main",
           "repo": "fake/x", "kind": "2b", "config_source": "fake/x@main",
           "loading_info": {"missing_keys": 0, "unexpected_keys": 0, "mismatched_keys": 0}}
    rec = c4.process_model_4(
        model, tok, key_or_unit=key, family="pythia", info=info, root=tmp_path,
        battery=_tiny_battery_34(), ref_tables={}, ref_activation_paths={},
        batch_size=battery_4.BATCH_4[key], device="cpu", keep_activations=False,
        sites=[0, 3, 6], refs=(), committed_digest=None,
        stack={"torch": "x", "transformers": "y"}, git_sha="0" * 40,
        release_model=lambda: events.append("release"))

    assert events == ["release", "bank", "write"], events
    assert rec["stack"]["numpy"] == np.__version__
    assert rec["stack"]["torch"] == "x" and rec["stack"]["transformers"] == "y"
    assert rec["global_sha256"] is not None      # the bank really was built


def test_release_once_4_is_idempotent():
    calls = []
    release = c4.release_once_4({"release": calls.append}, "the-model")
    release()
    release()
    release()
    assert calls == ["the-model"]


def test_stack_record_4_keeps_a_callers_own_numpy_entry():
    assert c4.stack_record_4({"torch": "2.12.1"})["numpy"] == np.__version__
    assert c4.stack_record_4({"numpy": "pinned"})["numpy"] == "pinned"


# --------------------------------------------------------------- storage

def _record_fields(**over):
    base = dict(family="pythia", info={"n_hidden": 7}, sites=[0, 3, 6], d=8, render="plain",
               batch_size=32, refs=[], pairing={}, committed_digest=None, seconds=0.5,
               stack={"torch": "x", "transformers": "y"}, git_sha="deadbeef",
               prereg_tag=battery_4.PREREG_TAG_4)
    base.update(over)
    return base


def _small_sets(n_sites=2, n=4, k=2):
    rng = np.random.default_rng(0)
    return rng.integers(0, n, size=(n_sites, n, k)).astype(np.uint16)


def test_write_load_4_round_trip(tmp_path):
    sets_by_rung = {r: _small_sets() for r in battery_4.RUNGS}
    attested_by_rung = {r: {"question_end": _small_sets(), "pooled": _small_sets()}
                        for r in battery_4.RUNGS}
    overlaps_by_rung = {r: {"ref_x": np.ones((2, 4), dtype=np.uint8)} for r in battery_4.RUNGS}
    X = np.zeros((4, 2, 2, 8), dtype=np.float16)
    P = np.zeros((4, 2, 8), dtype=np.float16)
    activations_by_rung = {r: {"X": X, "P": P} for r in battery_4.RUNGS}
    align = {r: {} for r in battery_4.RUNGS}

    rec = c4.write_load_4(tmp_path, "test_key", record_fields=_record_fields(),
                          sets_by_rung=sets_by_rung, overlaps_by_rung=overlaps_by_rung,
                          attested_by_rung=attested_by_rung, activations_by_rung=activations_by_rung,
                          global_sets=None, align=align, keep_activations=True)

    d = battery_4.reference_dir(tmp_path, "test_key")
    assert (d / "_load.json").is_file()
    assert (d / "align.json").is_file()
    assert set(rec["sets_sha256"]) == set(battery_4.RUNGS)
    for r in battery_4.RUNGS:
        assert rec["sets_sha256"][r] == battery_4.bg.sha256_file(d / "sets" / f"{r}.npz")
        assert rec["attested_sha256"][r] == battery_4.bg.sha256_file(d / "attested" / f"{r}.npz")
        assert rec["activation_sha256"][r] == battery_4.bg.sha256_file(d / "activations" / f"{r}.npz")
    with np.load(d / "sets" / f"{battery_4.RUNGS[0]}.npz") as z:
        assert np.array_equal(z["sets"], sets_by_rung[battery_4.RUNGS[0]])
        assert np.array_equal(z["overlap_ref_x"], overlaps_by_rung[battery_4.RUNGS[0]]["ref_x"])
    assert battery_4.unit_complete_4(tmp_path, "test_key")


def test_write_load_4_raises_on_sets_reread_mismatch(tmp_path, monkeypatch):
    # Task 5 mutation harness: a real write always round-trips
    # correctly, so this defensive check needs an INJECTED corruption
    # to observe at all -- wrap np.load so the "sets" array it returns
    # never matches what was written.
    sets_by_rung = {r: _small_sets() for r in battery_4.RUNGS}
    align = {r: {} for r in battery_4.RUNGS}
    real_load = c4.np.load

    class _BadSets:
        def __init__(self, real_ctx):
            self._ctx = real_ctx
        def __enter__(self):
            self._z = self._ctx.__enter__()
            return self
        def __exit__(self, *a):
            return self._ctx.__exit__(*a)
        def __getitem__(self, key):
            if key == "sets":
                return np.zeros((1, 1, 1), dtype=np.uint16)
            return self._z[key]
        @property
        def files(self):
            return self._z.files

    def fake_load(path, *a, **kw):
        return _BadSets(real_load(path, *a, **kw))

    monkeypatch.setattr(c4.np, "load", fake_load)
    with pytest.raises(ValueError, match="sets re-read mismatch"):
        c4.write_load_4(tmp_path, "test_key_bad_reread", record_fields=_record_fields(),
                        sets_by_rung=sets_by_rung, overlaps_by_rung={},
                        attested_by_rung={r: {} for r in battery_4.RUNGS},
                        activations_by_rung={}, global_sets=None, align=align,
                        keep_activations=True)


def test_write_load_4_keep_activations_false_leaves_no_activations_dir(tmp_path):
    sets_by_rung = {r: _small_sets() for r in battery_4.RUNGS}
    attested_by_rung = {r: {} for r in battery_4.RUNGS}
    X = np.zeros((4, 2, 2, 8), dtype=np.float16)
    P = np.zeros((4, 2, 8), dtype=np.float16)
    activations_by_rung = {r: {"X": X, "P": P} for r in battery_4.RUNGS}
    align = {r: {} for r in battery_4.RUNGS}

    rec = c4.write_load_4(tmp_path, "test_key2", record_fields=_record_fields(),
                          sets_by_rung=sets_by_rung, overlaps_by_rung={},
                          attested_by_rung=attested_by_rung, activations_by_rung=activations_by_rung,
                          global_sets=None, align=align, keep_activations=False)

    d = battery_4.reference_dir(tmp_path, "test_key2")
    assert not (d / "activations").exists()
    assert rec["activation_sha256"][battery_4.RUNGS[0]] is not None


def test_write_load_4_global_sets_round_trip(tmp_path):
    sets_by_rung = {r: _small_sets() for r in battery_4.RUNGS}
    attested_by_rung = {r: {} for r in battery_4.RUNGS}
    align = {r: {} for r in battery_4.RUNGS}
    global_arr = np.ones((2, 5, 2), dtype=np.uint16)
    order = [("antonym", i) for i in range(5)]

    rec = c4.write_load_4(tmp_path, "test_key3", record_fields=_record_fields(),
                          sets_by_rung=sets_by_rung, overlaps_by_rung={},
                          attested_by_rung=attested_by_rung, activations_by_rung={},
                          global_sets=(global_arr, order), align=align, keep_activations=True)
    d = battery_4.reference_dir(tmp_path, "test_key3")
    assert (d / "global.npz").is_file()
    assert rec["global_sha256"] == battery_4.bg.sha256_file(d / "global.npz")
    with np.load(d / "global.npz") as z:
        assert np.array_equal(z["sets"], global_arr)


def test_load_ref_tables_4_refuses_sha_drift(tmp_path):
    sets_by_rung = {r: _small_sets() for r in battery_4.RUNGS}
    attested_by_rung = {r: {"question_end": _small_sets(), "pooled": _small_sets()}
                        for r in battery_4.RUNGS}
    align = {r: {} for r in battery_4.RUNGS}
    c4.write_load_4(tmp_path, "ref_pythia_12b", record_fields=_record_fields(),
                    sets_by_rung=sets_by_rung, overlaps_by_rung={},
                    attested_by_rung=attested_by_rung, activations_by_rung={},
                    global_sets=None, align=align, keep_activations=True)

    ok = c4.load_ref_tables_4(tmp_path, ["ref_pythia_12b"])
    assert set(ok["ref_pythia_12b"]["sets"]) == set(battery_4.RUNGS)
    assert ok["ref_pythia_12b"]["n_hidden"] == 7

    d = battery_4.reference_dir(tmp_path, "ref_pythia_12b")
    p = d / "sets" / f"{battery_4.RUNGS[0]}.npz"
    corrupt = np.load(p)
    arrs = {k: corrupt[k] for k in corrupt.files}
    corrupt.close()
    arrs["sets"] = arrs["sets"] + 1
    np.savez_compressed(p, **arrs)

    with pytest.raises(ValueError, match="sha256"):
        c4.load_ref_tables_4(tmp_path, ["ref_pythia_12b"])


# ---------------------------------------------------------- fake loaders

def test_fake_loaders_shape():
    seed_by_key = {"ref_pythia_12b": 1, ("pythia_2.8b", 1000): 2}
    n_hidden_by = {"ref_pythia_12b": 37, "pythia_2.8b": 33}
    loaders = fakes_4.fake_loaders(seed_by_key, n_hidden_by=n_hidden_by)
    model, tok, info = loaders["key"]("ref_pythia_12b")
    assert info["n_hidden"] == 37
    model2, tok2, info2 = loaders["step"]("pythia_2.8b", 1000)
    assert info2["n_hidden"] == 33
    loaders["free_step"]("pythia_2.8b", 1000)
    loaders["release"](model)


def test_load_ref_tables_4_refuses_a_rung_with_no_recorded_sha(tmp_path):
    """FREEZE F-6: `want is None` used to SKIP the sha check, so a rung
    dropped from a reference record's `sets_sha256` had its bytes read
    unchecked. `_load_one_unit_4` requires full 34-rung coverage, but
    `eligibility_table_4` — what the reference stage calls to WRITE the
    committed eligibility table, before any analyzer runs — reaches
    this loader directly."""
    sets_by_rung = {r: _small_sets() for r in battery_4.RUNGS}
    attested_by_rung = {r: {"question_end": _small_sets(), "pooled": _small_sets()}
                        for r in battery_4.RUNGS}
    c4.write_load_4(tmp_path, "ref_pythia_12b", record_fields=_record_fields(),
                    sets_by_rung=sets_by_rung, overlaps_by_rung={},
                    attested_by_rung=attested_by_rung, activations_by_rung={},
                    global_sets=None, align={r: {} for r in battery_4.RUNGS},
                    keep_activations=True)
    assert set(c4.load_ref_tables_4(tmp_path, ["ref_pythia_12b"])["ref_pythia_12b"]["sets"]) \
        == set(battery_4.RUNGS)
    p = battery_4.load_record_path(tmp_path, "ref_pythia_12b")
    rec = json.loads(p.read_text())
    del rec["sets_sha256"][battery_4.RUNGS[0]]
    p.write_text(json.dumps(rec, indent=1))
    with pytest.raises(ValueError, match="no sets_sha256"):
        c4.load_ref_tables_4(tmp_path, ["ref_pythia_12b"])
