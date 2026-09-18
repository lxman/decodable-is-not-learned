# experiments/exp4c/tests/test_collect_4c.py
"""Task 3's per-load wrapper, cold: FakeModel/FakeTokenizer (no torch
model contact, no network). `tmp_root4` carries three reference-stage
units (`ref_olmo2_7b`, `ref_smollm3_3b`, `ref_comma_7b`) written
through Exp 4's own frozen synthetic-unit writer (`full_shape.
_write_synthetic_unit`, `refs=()`) — the candidate under test aligns
against them; `tmp_root4c` is exp4c's own results root."""
from __future__ import annotations

import json
import random

import numpy as np
import pytest

from experiments.exp4 import battery_4
from experiments.exp4 import collect_4
from experiments.exp4 import metric_4
from experiments.exp4.tests import fakes_4
from experiments.exp4.tests import full_shape
from experiments.exp4c import battery_4c as b
from experiments.exp4c import collect_4c as c4c

_REF_N_HIDDEN = {"ref_olmo2_7b": 33, "ref_smollm3_3b": 37, "ref_comma_7b": 33}
_REF_FAMILY = {"ref_olmo2_7b": "olmo2", "ref_smollm3_3b": "smollm3", "ref_comma_7b": "comma"}

_WORDS = ["cat", "dog", "blue", "fast", "moon", "tree", "gold", "iron", "leaf", "wave",
         "frost", "spark", "amber", "cliff", "delta", "ember"]


def _tiny_battery_34(n=12):
    """All 34 rungs (`process_model_4c` loops over them unconditionally)
    with 12 varied items each — k=10 needs n > k."""
    battery = {}
    for r in battery_4.RUNGS:
        rng = random.Random(r)
        battery[r] = {
            "shots": [["amber cliff quartz willow", "2"], ["delta ember frost spark", "4"]],
            "eval_items": [{"question": " ".join(rng.choice(_WORDS) for _ in range(4)) + f" {i}",
                           "answer": str(i)} for i in range(n)]}
    return battery


# ------------------------------------------------------------- fixtures

@pytest.fixture
def tmp_root4c(tmp_path):
    return tmp_path / "root4c"


@pytest.fixture
def tmp_root4(tmp_path):
    root = tmp_path / "root4"
    for ref, n_hidden in _REF_N_HIDDEN.items():
        sites = metric_4.sites_4(n_hidden)
        rng = np.random.default_rng(abs(hash(ref)) % (2 ** 31))

        def provider(rung, _rng=rng, _n_sites=len(sites)):
            return _rng.standard_normal((12, _n_sites, 1, 8)).astype(np.float32)

        full_shape._write_synthetic_unit(
            root, ref, family=_REF_FAMILY[ref], n_hidden=n_hidden, sites=sites,
            batch_size=battery_4.BATCH_4[ref], refs=(), ref_tables={},
            committed_digest=f"synthetic:{ref}", X_provider=provider, keep_activations=True)
    return root


@pytest.fixture
def fake_model_tok():
    def _make(n_hidden, seed, d=8, vocab_size=1024):
        return (fakes_4.FakeModel(seed=seed, n_hidden=n_hidden, d=d, vocab_size=vocab_size),
                fakes_4.FakeTokenizer())
    return _make


@pytest.fixture
def small_battery():
    return _tiny_battery_34()


def _info(n_hidden=33, digest="d"):
    return {"tensor_digest": digest, "commit": "c", "revision": "r", "repo": "p",
           "kind": "candidate", "config_source": "s", "n_hidden": n_hidden, "loading_info": {}}


# ---------------------------------------------------------------- happy path

def test_process_model_4c_writes_a_4c_record_and_no_activations(
        tmp_root4c, tmp_root4, fake_model_tok, small_battery):
    refs = ("ref_olmo2_7b", "ref_smollm3_3b", "ref_comma_7b")
    ref_tables = collect_4.load_ref_tables_4(tmp_root4, refs)
    model, tok = fake_model_tok(n_hidden=33, seed=1)
    info = _info()

    rec = c4c.process_model_4c(
        [model], tok, key_or_unit=("pythia_6.9b", 1000), family="pythia", info=info,
        root=tmp_root4c, battery=small_battery, ref_tables=ref_tables, batch_size=16,
        device="cpu", sites=metric_4.sites_4(33), refs=refs, committed_digest="d",
        stack={"torch": "x"}, git_sha="0" * 40)

    assert rec["prereg_tag"] == b.PREREG_TAG_4C
    assert rec["batch_size"] == 16
    assert rec["global_sha256"] is None
    assert rec["render"] == b.RENDER_4C["pythia"]
    assert not (battery_4.unit_dir(tmp_root4c, "pythia_6.9b", 1000) / "activations").exists()
    assert all(v is not None for v in rec["activation_sha256"].values())   # computed before deletion
    assert battery_4.unit_complete_4(tmp_root4c, ("pythia_6.9b", 1000))
    # every reference actually got aligned against (real overlap numbers, not a stub)
    align = json.loads((battery_4.unit_dir(tmp_root4c, "pythia_6.9b", 1000) / "align.json").read_text())
    one_rung = next(iter(align.values()))
    assert set(one_rung) == set(refs)
    for ref in refs:
        assert one_rung[ref]["cka_prompt_end"] is None                # (ii): no CKA, ever
        assert one_rung[ref]["knn_prompt_end"] is not None


def test_process_model_4c_writes_the_13b_thin_endpoint_key_with_no_global_bank(
        tmp_root4c, fake_model_tok, small_battery):
    """A str key (`THIN_ENDPOINT_KEY_4C`) would read as a "reference
    stage" key under exp4's own `is_reference_stage_key` test — 4c
    drops that branch entirely (dial iii), so even this key gets no
    `global.npz`."""
    model, tok = fake_model_tok(n_hidden=41, seed=7)
    info = _info(n_hidden=41, digest="e")

    rec = c4c.process_model_4c(
        [model], tok, key_or_unit=b.THIN_ENDPOINT_KEY_4C, family="olmo2", info=info,
        root=tmp_root4c, battery=small_battery, ref_tables={}, batch_size=16, device="cpu",
        sites=metric_4.sites_4(41), refs=(), committed_digest="e", stack={"torch": "x"},
        git_sha="0" * 40)

    assert rec["global_sha256"] is None
    assert not (battery_4.reference_dir(tmp_root4c, b.THIN_ENDPOINT_KEY_4C) / "global.npz").exists()
    assert battery_4.unit_complete_4(tmp_root4c, b.THIN_ENDPOINT_KEY_4C)


def test_process_model_4c_refuses_the_wrong_batch(tmp_root4c, fake_model_tok, small_battery):
    model, tok = fake_model_tok(n_hidden=33, seed=2)
    info = _info()
    with pytest.raises(ValueError, match="batch_size 32 != the pinned 16"):
        c4c.process_model_4c(
            [model], tok, key_or_unit=("pythia_6.9b", 2000), family="pythia", info=info,
            root=tmp_root4c, battery=small_battery, ref_tables={}, batch_size=32, device="cpu",
            sites=metric_4.sites_4(33), refs=(), committed_digest="d", stack={"torch": "x"},
            git_sha="0" * 40)


def test_the_box_is_emptied_before_the_first_forward_pass(
        tmp_root4c, fake_model_tok, small_battery, monkeypatch):
    """The `model_box` contract (ratification open item 1, carried over
    from exp4's `process_model_4`): the box must already be empty by
    the time the first rung's forward pass happens, so nothing but this
    frame names the weights from then on."""
    model, tok = fake_model_tok(n_hidden=33, seed=3)
    box = [model]
    info = _info()
    seen = {}
    real_collect_rung = c4c.collect_4.collect_rung_4

    def spy(*a, **kw):
        seen.setdefault("len_at_first_call", len(box))
        return real_collect_rung(*a, **kw)

    monkeypatch.setattr(c4c.collect_4, "collect_rung_4", spy)

    c4c.process_model_4c(
        box, tok, key_or_unit=("pythia_6.9b", 1000), family="pythia", info=info,
        root=tmp_root4c, battery=small_battery, ref_tables={}, batch_size=16, device="cpu",
        sites=metric_4.sites_4(33), refs=(), committed_digest="d", stack={"torch": "x"},
        git_sha="0" * 40)

    assert seen["len_at_first_call"] == 0
    assert box == []


def test_process_model_4c_rejects_a_non_boxed_model(tmp_root4c, fake_model_tok, small_battery):
    model, tok = fake_model_tok(n_hidden=33, seed=4)
    with pytest.raises(TypeError, match="model_box must be a one-element list"):
        c4c.process_model_4c(
            model, tok, key_or_unit=("pythia_6.9b", 1000), family="pythia", info=_info(),
            root=tmp_root4c, battery=small_battery, ref_tables={}, batch_size=16, device="cpu",
            sites=metric_4.sites_4(33), refs=(), committed_digest="d", stack={"torch": "x"},
            git_sha="0" * 40)


def test_release_model_called_once_after_the_last_forward_pass(
        tmp_root4c, fake_model_tok, small_battery):
    model, tok = fake_model_tok(n_hidden=33, seed=5)
    calls = []
    c4c.process_model_4c(
        [model], tok, key_or_unit=("pythia_6.9b", 1000), family="pythia", info=_info(),
        root=tmp_root4c, battery=small_battery, ref_tables={}, batch_size=16, device="cpu",
        sites=metric_4.sites_4(33), refs=(), committed_digest="d", stack={"torch": "x"},
        git_sha="0" * 40, release_model=lambda: calls.append("release"))
    assert calls == ["release"]


def test_real_loaders_4c_shape():
    loaders = c4c.real_loaders_4c()
    assert set(loaders) == {"step", "thin", "free_step", "release"}
    assert loaders["step"] is b.load_step_4c
    assert loaders["thin"] is b.load_thin_endpoint_4c
    assert loaders["free_step"] is b.free_step_4c
