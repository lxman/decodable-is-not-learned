"""Gate-1 fixtures (doc Open item 3): the byte gate must fire on a
planted one-byte drift in EITHER direction and stay silent on
identical streams; incomplete comparisons are refused, never silently
shortened. The synthetic-model provision runs the real sampler loop
(exp3's frozen sample_item) against a stored stream and back through
the comparator — the full regenerate-and-compare path minus the real
model, which only the freeze session's single-cell rehearsal touches.
"""
import pytest

torch = pytest.importorskip("torch")

from experiments.exp3c import rederive  # noqa: E402

ROWS = [{"item": 0, "draws": {"0": [" ab", " cd"]}},
        {"item": 1, "draws": {"0": [" ef", " gh"]}}]


def test_identical_streams_produce_no_diffs():
    assert rederive.diff_seed0(
        ROWS, {0: [" ab", " cd"], 1: [" ef", " gh"]}, dps=2) == []


def test_planted_drift_in_the_regenerated_stream_fires():
    diffs = rederive.diff_seed0(
        ROWS, {0: [" ab", " cX"], 1: [" ef", " gh"]}, dps=2)
    assert diffs == [{"item": 0, "seed": 0, "draw": 1,
                      "got": " cX", "committed": " cd"}]


def test_planted_drift_in_the_committed_stream_fires():
    rows = [{"item": 0, "draws": {"0": [" ab", " cd"]}},
            {"item": 1, "draws": {"0": [" eX", " gh"]}}]
    diffs = rederive.diff_seed0(
        rows, {0: [" ab", " cd"], 1: [" ef", " gh"]}, dps=2)
    assert diffs == [{"item": 1, "seed": 0, "draw": 0,
                      "got": " ef", "committed": " eX"}]


def test_every_differing_draw_is_reported_not_just_the_first():
    diffs = rederive.diff_seed0(
        ROWS, {0: [" X", " Y"], 1: [" ef", " Z"]}, dps=2)
    assert len(diffs) == 3
    assert [d["item"] for d in diffs] == [0, 0, 1]


def test_incomplete_regeneration_is_refused():
    with pytest.raises(ValueError, match="incomplete"):
        rederive.diff_seed0(ROWS, {0: [" ab", " cd"]}, dps=2)


def test_short_regenerated_stream_is_refused():
    with pytest.raises(ValueError, match="incomplete"):
        rederive.diff_seed0(ROWS, {0: [" ab"], 1: [" ef", " gh"]}, dps=2)


def test_extra_regenerated_items_are_refused():
    with pytest.raises(ValueError, match="does not carry"):
        rederive.diff_seed0(
            ROWS, {0: [" ab", " cd"], 1: [" ef", " gh"],
                   2: [" zz", " zz"]}, dps=2)


def test_committed_stream_of_the_wrong_depth_is_refused():
    with pytest.raises(ValueError, match="against draws_per_seed"):
        rederive.diff_seed0(ROWS, {0: [" ab", " cd", " x"],
                                   1: [" ef", " gh", " y"]}, dps=3)


def test_gate1_record_shape():
    rec = rederive.gate1_record(
        "reverse_string", "1b", n_items=500, dps=64, diffs=[],
        committed_gz_sha="abc", items_sha="def", model_sha="sha",
        stack={"torch": "x", "transformers": "y"})
    assert rec["draws_compared"] == 32_000
    assert rec["n_diffs"] == 0
    assert rec["seeds_rederived"] == [0]
    assert rec["dtype"] == "float32"
    assert rec["mode"] == "trained"


# ------------------------------------------- synthetic-model provision

@pytest.fixture(scope="module")
def tok():
    import sys
    from pathlib import Path

    from experiments.exp3 import analyze_3 as a3
    exp2b = Path(a3.EXPERIMENTS) / "exp2b"
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


def _sample_rows(model, tok, n_items, dps):
    from experiments.exp3.sampler import sample_item
    rows = []
    for i in range(n_items):
        got = sample_item(model, tok,
                          f"Q: Spell the string 'ab{i}' backwards.\nA:",
                          rung="reverse_string", size="410m",
                          mode="trained", item_idx=i, seeds=(0,),
                          draws_per_seed=dps, max_new_tokens=4)
        rows.append({"item": i, "draws": {"0": got[0]}})
    return rows


def test_regenerate_and_compare_is_clean_end_to_end(model, tok):
    """The full gate-1 path on a synthetic model: a stored seed-0
    stream re-derived through the frozen sampler compares clean."""
    committed = _sample_rows(model, tok, 2, 8)
    regen = {r["item"]: list(r["draws"]["0"])
             for r in _sample_rows(model, tok, 2, 8)}
    assert rederive.diff_seed0(committed, regen, dps=8) == []


def test_one_byte_drift_through_the_full_path_fires(model, tok):
    committed = _sample_rows(model, tok, 2, 8)
    regen = {r["item"]: list(r["draws"]["0"])
             for r in _sample_rows(model, tok, 2, 8)}
    committed[1]["draws"]["0"][3] = committed[1]["draws"]["0"][3] + "X"
    diffs = rederive.diff_seed0(committed, regen, dps=8)
    assert len(diffs) == 1
    assert (diffs[0]["item"], diffs[0]["seed"], diffs[0]["draw"]) \
        == (1, 0, 3)
    assert diffs[0]["committed"].endswith("X")
