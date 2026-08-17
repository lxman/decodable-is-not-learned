"""The standing tokenizer/config glue smoke (exp3 stop #1's rule; doc
Open item 8, freeze-checklist line).

Exp 3's stop #1 was a padded-vocab width mismatch: config.vocab_size
(50304) exceeds len(tok) (50277), and an instrument built over the
tokenizer's width crashed on first real-model contact. The ledgered
fix note records that THE SAMPLER NEEDED NO CHANGE — its draws already
ranged over the padded width and decode disposes of dead ids — but the
rule stands: the glue is proven executable BEFORE the tag, not
discovered at campaign time.

3c has no mass arm, so its glue surface is the sampling path only:

- synthetic padded model (vocab_size > len(tok)): the frozen
  sample_item draws over the FULL padded width, decodes every draw
  without error, and stays byte-reproducible — dead ids are handled
  by decode exactly as the committed campaign relied on;
- real-config smoke (quantity-free: tokenizer + config.json only, no
  weights, no forward): for both campaign sizes, the padded width
  covers the tokenizer and every terminal id lives inside it.
"""
import pytest

torch = pytest.importorskip("torch")

from experiments.exp3 import analyze_3 as a3  # noqa: E402


@pytest.fixture(scope="module")
def tok():
    import sys
    from pathlib import Path
    exp2b = Path(a3.EXPERIMENTS) / "exp2b"
    if str(exp2b) not in sys.path:
        sys.path.insert(0, str(exp2b))
    from models import load_tokenizer
    return load_tokenizer("410m")


def test_sampler_over_padded_vocab_is_clean_and_reproducible(tok):
    """vocab_size strictly greater than len(tok): draws range over the
    padded width, every draw decodes, two runs are byte-identical."""
    from transformers import GPTNeoXConfig, GPTNeoXForCausalLM

    from experiments.exp3.sampler import sample_item

    cfg = GPTNeoXConfig(vocab_size=len(tok) + 137, hidden_size=64,
                        num_hidden_layers=2, num_attention_heads=4,
                        intermediate_size=256,
                        max_position_embeddings=256)
    torch.manual_seed(23)
    model = GPTNeoXForCausalLM(cfg).eval()
    kw = dict(rung="glue_smoke", size="410m", mode="trained",
              item_idx=0, seeds=(0, 1), draws_per_seed=8,
              max_new_tokens=6)
    prompt = "Q: Spell the string 'zq' backwards.\nA:"
    one = sample_item(model, tok, prompt, **kw)
    two = sample_item(model, tok, prompt, **kw)
    assert one == two
    assert all(isinstance(d, str) for s in one for d in one[s])
    assert sum(len(one[s]) for s in one) == 16


def test_real_config_width_glue_both_campaign_sizes(tok):
    """Quantity-free: the local config.json's padded width covers the
    tokenizer, and the terminal ids the sampler truncates at all live
    inside it. No weights load, no forward, no sampled quantity."""
    import sys
    from pathlib import Path

    from transformers import AutoConfig

    exp2b = Path(a3.EXPERIMENTS) / "exp2b"
    if str(exp2b) not in sys.path:
        sys.path.insert(0, str(exp2b))
    from models import PYTHIA_SHAS, load_tokenizer

    for size in a3.PROBE_SIZES:
        t = tok if size == "410m" else load_tokenizer(size)
        cfg = AutoConfig.from_pretrained(f"EleutherAI/pythia-{size}",
                                         revision=PYTHIA_SHAS[size])
        assert cfg.vocab_size >= len(t), (
            f"{size}: config width {cfg.vocab_size} does not cover the "
            f"tokenizer's {len(t)} — the stop-#1 class, live")
        terminal = tuple(sorted(set(t.all_special_ids)))
        assert terminal, f"{size}: no terminal ids to truncate at"
        assert all(0 <= i < cfg.vocab_size for i in terminal)
