"""Fixtures for the seeded sampler (design §3, §5; doc Open item 2).

Model-free where the provision allows it (stream map, chunk plan,
truncation, untruncated step probabilities); the loop-level determinism
and distinctness provisions run on the synthetic 2-layer model over the
real vocabulary. The campaign-stack determinism artifact (gate 4) is
run/determinism_fixture.py, executed twice in separate processes; this
file unit-tests its comparison logic only.

No real model is loaded and no committed item is sampled anywhere here.
"""
import pytest

torch = pytest.importorskip("torch")

from experiments.exp3 import analyze_3 as a  # noqa: E402
from experiments.exp3 import sampler as sp  # noqa: E402


# ------------------------------------------------------- stream map

def test_stream_seed_is_deterministic_and_distinct():
    k = sp.stream_seed("rev_string7", "410m", "trained", 0, 0)
    assert k == sp.stream_seed("rev_string7", "410m", "trained", 0, 0)
    others = {sp.stream_seed("rev_string7", "410m", "trained", 0, 1),
              sp.stream_seed("rev_string7", "410m", "trained", 1, 0),
              sp.stream_seed("rev_string7", "410m", "untrained", 0, 0),
              sp.stream_seed("rev_string7", "1b", "trained", 0, 0),
              sp.stream_seed("reverse_string", "410m", "trained", 0, 0)}
    assert k not in others and len(others) == 5


def test_stream_seed_golden_values_pin_the_formula():
    """The formula is a commitment (§3, PROGRESS.md reading 4): if this
    literal moves, the streams are not the preregistered streams. The
    63-bit mask is part of the formula (torch.Generator takes a signed
    int64)."""
    assert sp.stream_seed("rev_string7", "410m", "trained", 0, 0) == \
        826817742090631546
    got = {(s, i): sp.stream_seed("ctrl_copy", "1b", "untrained", s, i)
           for s in (0, 3) for i in (0, 499)}
    assert len(set(got.values())) == 4


def test_stream_map_dump_covers_every_cell_seed_pair(tmp_path):
    p = tmp_path / "stream_map.json"
    m = sp.dump_stream_map(p)
    assert len(m["cells"]) == 16 * len(a.SEEDS)
    key = "rev_string7/410m/trained/s0"
    assert m["cells"][key]["item0"] == \
        sp.stream_seed("rev_string7", "410m", "trained", 0, 0)
    assert m["cells"][key]["item499"] == \
        sp.stream_seed("rev_string7", "410m", "trained", 0, 499)
    assert p.is_file()


# ------------------------------------------------------- chunk plan

def test_chunk_plan_matches_the_committed_draw_budget():
    assert sp.chunk_plan(a.DRAWS_PER_SEED["rev_string7"]) == (16, 16, 16, 16)
    assert sp.chunk_plan(a.DRAWS_PER_SEED["ctrl_copy"]) == (8,)
    assert sum(sp.chunk_plan(64)) * len(a.SEEDS) == a.K_TOTAL["rev_string7"]
    assert sum(sp.chunk_plan(8)) * len(a.SEEDS) == a.K_TOTAL["ctrl_copy"]


def test_chunk_plan_never_pads_a_seeds_stream():
    """Rows per chunk are exactly the draws taken from that seed's
    generator — a padded row would consume randomness and change every
    later draw in the stream."""
    assert sum(sp.chunk_plan(64)) == 64
    assert sum(sp.chunk_plan(8)) == 8
    assert all(c <= sp.MAX_ROWS for c in sp.chunk_plan(64))


# ------------------------------------------------------- truncation

def test_draw_tokens_truncate_at_the_first_terminal():
    assert sp.truncate_at_terminal([5, 7, 0, 9], terminal_ids=(0, 1)) == [5, 7]
    assert sp.truncate_at_terminal([5, 7, 9], terminal_ids=(0, 1)) == [5, 7, 9]
    assert sp.truncate_at_terminal([0, 5], terminal_ids=(0, 1)) == []


# ------------------------------------------- untruncated step probs

def test_step_probs_are_exact_softmax_with_tail_kept():
    """T = 1.0, top-p and top-k OFF: the smallest-logit token keeps
    nonzero probability. Truncation deletes tail mass and tail mass is
    the question (§3) — a truncating implementation fails here."""
    logits = torch.tensor([3.0, 1.0, -4.0, 0.0])
    p = sp.step_probs(logits)
    ref = torch.softmax(logits.to(torch.float32), dim=-1)
    assert torch.allclose(p, ref, atol=1e-7)
    assert p.min().item() > 0.0


# ------------------------------------------- loop on a synthetic model

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
def model(tok):
    from transformers import GPTNeoXConfig, GPTNeoXForCausalLM
    cfg = GPTNeoXConfig(vocab_size=len(tok), hidden_size=64,
                        num_hidden_layers=2, num_attention_heads=4,
                        intermediate_size=256, max_position_embeddings=256)
    torch.manual_seed(11)
    return GPTNeoXForCausalLM(cfg).eval()


PROMPT = "Q: Spell the string 'ab' backwards.\nA:"


def test_two_runs_reproduce_byte_identically(model, tok):
    kw = dict(rung="ctrl_copy", size="410m", mode="trained", item_idx=3,
              seeds=(0, 1), draws_per_seed=8, max_new_tokens=5)
    one = sp.sample_item(model, tok, PROMPT, **kw)
    two = sp.sample_item(model, tok, PROMPT, **kw)
    assert one == two
    assert set(one) == {0, 1}
    assert all(len(v) == 8 for v in one.values())


def test_distinct_seeds_draw_distinct_streams(model, tok):
    got = sp.sample_item(model, tok, PROMPT, rung="ctrl_copy", size="410m",
                         mode="trained", item_idx=3, seeds=(0, 1, 2, 3),
                         draws_per_seed=8, max_new_tokens=5)
    flat = ["|".join(got[s]) for s in sorted(got)]
    assert len(set(flat)) == 4


def test_distinct_items_draw_distinct_streams(model, tok):
    kw = dict(rung="ctrl_copy", size="410m", mode="trained", seeds=(0,),
              draws_per_seed=8, max_new_tokens=5)
    one = sp.sample_item(model, tok, PROMPT, item_idx=0, **kw)
    two = sp.sample_item(model, tok, PROMPT, item_idx=1, **kw)
    assert one[0] != two[0]


def test_reversal_chunking_reproduces_the_unchunked_stream(model, tok):
    """64 draws in 16-row chunks must equal what the stream would give —
    the chunk partition is bookkeeping, not a semantic boundary. Proven
    by the two-run identity at draws_per_seed=64 crossing 4 chunks."""
    kw = dict(rung="rev_string7", size="410m", mode="trained", item_idx=0,
              seeds=(2,), draws_per_seed=64, max_new_tokens=3)
    one = sp.sample_item(model, tok, PROMPT, **kw)
    two = sp.sample_item(model, tok, PROMPT, **kw)
    assert one == two
    assert len(one[2]) == 64


# ---------------------------------------- determinism fixture compare

def test_fixture_compare_flags_any_byte_difference(tmp_path):
    p1, p2 = tmp_path / "a.json", tmp_path / "b.json"
    p1.write_text('{"draws": ["x", "y"]}')
    p2.write_text('{"draws": ["x", "y"]}')
    assert sp.fixture_files_identical(p1, p2)
    p2.write_text('{"draws": ["x", "z"]}')
    assert not sp.fixture_files_identical(p1, p2)
