"""Model-facing glue fixtures for the mass module (Open item 1).

Everything here runs on a SYNTHETIC model: a 2-layer random-weight
GPTNeoX built from config over the real Pythia vocabulary. No real
model is loaded and no real cell's quantity is computed — the fixtures
prove path equalities the campaign will rely on:

- the cached depth-2 pass equals a full re-forward of prompt+w, token
  for token, within float tolerance (the KV-cache shortcut changes
  nothing but time);
- the prompt encoding is the harness's batch-of-one encoding: no pad,
  no added BOS;
- the real tokenizer's whitespace classification is a handful of ids,
  as §5 assumes, and every one strips to nothing under first_char.

The MPS variants re-prove the equalities on the campaign device.
"""
import pytest

torch = pytest.importorskip("torch")

from transformers import GPTNeoXConfig, GPTNeoXForCausalLM  # noqa: E402

from experiments.exp3 import analyze_3 as a  # noqa: E402
from experiments.exp3 import masses as m  # noqa: E402

PROMPT = "Q: Spell the string 'pyayd' backwards.\nA:"


@pytest.fixture(scope="module")
def tok():
    import sys
    from pathlib import Path
    exp2b = Path(a.EXPERIMENTS) / "exp2b"
    if str(exp2b) not in sys.path:
        sys.path.insert(0, str(exp2b))
    from models import load_tokenizer
    return load_tokenizer("410m")


@pytest.fixture(scope="module")
def classes(tok):
    return m.classify_tokenizer(tok)


def tiny_model(tok, device="cpu", pad=0):
    """`pad` widens vocab_size past len(tok) — the real GPT-NeoX shape
    (Pythia pads to a multiple of 128: 50304 logits over a 50277-entry
    tokenizer). The build's original fixtures used pad=0, which is why
    the width mismatch reached the campaign (stop #1, ledger
    2026-08-16)."""
    cfg = GPTNeoXConfig(vocab_size=len(tok) + pad, hidden_size=64,
                        num_hidden_layers=2, num_attention_heads=4,
                        intermediate_size=256, max_position_embeddings=256)
    torch.manual_seed(7)
    return GPTNeoXForCausalLM(cfg).to(device).eval()


def test_real_vocab_whitespace_class_shape(tok, classes):
    """340 whitespace-class ids in the real vocabulary (PROGRESS.md,
    2026-08-15 — not §5's 'handful'; every multi-space run token). The
    special ids are carved out as terminal, never whitespace-path."""
    fc, ws, term = classes
    assert 0 < len(ws) < 1000, len(ws)
    assert all(fc[i] is None for i in ws)
    assert set(term) == set(tok.all_special_ids)
    assert not set(term) & set(ws)


def test_classification_matches_first_char_on_sampled_ids(tok, classes):
    fc, _, _ = classes
    for i in range(0, len(tok), 997):
        assert fc[i] == a.first_char(
            tok.batch_decode([[i]], skip_special_tokens=True)[0])


def test_prompt_encoding_is_harness_batch_of_one(tok):
    plain = tok(PROMPT)["input_ids"]
    padded = tok([PROMPT], return_tensors="pt", padding=True)
    assert padded["input_ids"][0].tolist() == plain
    assert padded["attention_mask"].min().item() == 1


def _assert_depth2_equals_full_forward(device, tok, classes):
    fc, ws, term = classes
    model = tiny_model(tok, device)
    rec, probs1, probs2 = m.collect_item_debug(
        model, tok, PROMPT, label="d", first_chars=fc, ws_ids=ws,
        terminal_ids=term)

    s = sum(probs1)
    assert abs(s - 1.0) < 1e-3
    enc = tok(PROMPT, return_tensors="pt").to(device)
    live = [w for w in ws if probs1[w] > 0.0]
    assert set(probs2) == set(live)
    for w in list(live)[:8]:
        full = torch.cat([enc["input_ids"],
                          torch.tensor([[w]], device=device)], dim=1)
        with torch.no_grad():
            ref = torch.softmax(
                model(input_ids=full).logits[0, -1].to("cpu", torch.float32),
                dim=-1).tolist()
        got = probs2[w]
        assert max(abs(x - y) for x, y in zip(got, ref)) < 5e-5
    assert set(rec["letters"]) == set("abcdefghijklmnopqrstuvwxyz")
    assert rec["label_char"] == "d"
    assert 0.0 <= rec["residual"] <= 1.0


def test_depth2_cache_path_equals_full_forward_cpu(tok, classes):
    _assert_depth2_equals_full_forward("cpu", tok, classes)


@pytest.mark.skipif(not torch.backends.mps.is_available(),
                    reason="campaign device not present")
def test_depth2_cache_path_equals_full_forward_mps(tok, classes):
    _assert_depth2_equals_full_forward("mps", tok, classes)


def test_padded_vocab_width_is_covered_and_dead_ids_defer(tok):
    """Campaign stop #1's fix, both directions (ledger 2026-08-16).

    Forward: with n_logits = the model's padded width, the class table
    covers every logit; the dead band [len(tok), n_logits) decodes to
    '' and classes to the whitespace path (the frozen empty-decode
    deferral rule), and the depth-2 cached pass still equals full
    re-forwards on the padded model. Backward: a width-matched table
    against a padded model's distribution is REFUSED by depth2_masses
    — the exact crash, pinned so it can never return silently."""
    pad = 27
    model = tiny_model(tok, pad=pad)
    n_logits = model.config.vocab_size
    fc, ws, term = m.classify_tokenizer(tok, n_logits=n_logits)
    assert len(fc) == n_logits == len(tok) + pad
    dead = range(len(tok), n_logits)
    assert all(fc[i] is None for i in dead)
    assert set(dead) <= set(ws)
    assert not set(dead) & set(term)

    rec, probs1, probs2 = m.collect_item_debug(
        model, tok, PROMPT, label="d", first_chars=fc, ws_ids=ws,
        terminal_ids=term)
    assert len(probs1) == n_logits
    assert set(rec["letters"]) == set("abcdefghijklmnopqrstuvwxyz")
    live_dead = [w for w in dead if probs1[w] > 0.0]
    for w in live_dead[:2]:
        enc = tok(PROMPT, return_tensors="pt")
        full = torch.cat([enc["input_ids"], torch.tensor([[w]])], dim=1)
        with torch.no_grad():
            ref = torch.softmax(
                model(input_ids=full).logits[0, -1].to("cpu", torch.float32),
                dim=-1).tolist()
        assert max(abs(x - y) for x, y in zip(probs2[w], ref)) < 5e-5

    fc0, ws0, term0 = m.classify_tokenizer(tok)   # width-matched table
    with pytest.raises(ValueError, match="token classes"):
        m.depth2_masses(probs1, fc0, ws0, {}, chars=("a",),
                        terminal_ids=term0)


def test_narrower_n_logits_is_refused(tok):
    with pytest.raises(ValueError, match="narrower"):
        m.classify_tokenizer(tok, n_logits=len(tok) - 1)


def test_real_config_width_smoke(tok):
    """The quantity-free integration smoke that belonged on the freeze
    checklist (ledger 2026-08-16): the class table built at the REAL
    model's config.json width covers it, and the real dead band is
    empty-decode deferral ids. Reads the local HF cache's config.json
    only — no model is loaded and no quantity is computed."""
    import glob
    import json
    from pathlib import Path
    hits = glob.glob(str(Path.home() / ".cache/huggingface/hub/"
                         "models--EleutherAI--pythia-410m/snapshots/*/"
                         "config.json"))
    if not hits:
        pytest.skip("pythia-410m config not in the local cache")
    width = json.load(open(hits[0]))["vocab_size"]
    assert width >= len(tok)
    fc, ws, term = m.classify_tokenizer(tok, n_logits=width)
    assert len(fc) == width
    assert all(fc[i] is None for i in range(len(tok), width))
    assert set(range(len(tok), width)) <= set(ws)


# NOTE on dtype (PROGRESS.md 2026-08-15): the campaign computes mass
# and sampling at FLOAT32 — fp16-MPS batched cached steps corrupt every
# row but row 0 on real-model shapes (found at build; an fp16 variant
# of the equality test above failed with a saturated row and was the
# thread that unravelled it). The fp32 MPS test above therefore IS the
# campaign-dtype test. Per-size verification on real models lives in
# run/preflight_paths.py, gating every campaign tier; the gate-4
# determinism fixture byte-compares against the committed reference.
