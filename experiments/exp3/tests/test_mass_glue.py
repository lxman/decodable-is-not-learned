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


def tiny_model(tok, device="cpu"):
    cfg = GPTNeoXConfig(vocab_size=len(tok), hidden_size=64,
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
